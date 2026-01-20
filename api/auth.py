"""
Authentication and authorization for admin routes.

Provides JWT-based session management with bcrypt password hashing,
rate limiting, and IP validation for security.
"""
import secrets
from datetime import datetime, timedelta
from typing import Optional
from functools import wraps

import bcrypt
import jwt
from fastapi import Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from models.database import LoginAttempt, get_session_local
from utils.logging import get_logger

logger = get_logger(__name__)

# Session configuration
SESSION_COOKIE_NAME = "admin_session"
SESSION_HOURS = 24


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt with 12 rounds.

    Args:
        password: Plain text password

    Returns:
        Bcrypt hashed password string
    """
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(password: str, hashed: str) -> bool:
    """
    Verify a password against a bcrypt hash.

    Args:
        password: Plain text password to verify
        hashed: Bcrypt hashed password

    Returns:
        True if password matches, False otherwise
    """
    try:
        return bcrypt.checkpw(
            password.encode('utf-8'),
            hashed.encode('utf-8')
        )
    except Exception as e:
        logger.error("password_verification_failed", error=str(e))
        return False


def create_session_token(ip_address: str, jwt_secret: str) -> str:
    """
    Create a JWT session token.

    Args:
        ip_address: Client IP address (included in JWT payload for validation)
        jwt_secret: Secret key for JWT signing

    Returns:
        JWT token string
    """
    expiry = datetime.utcnow() + timedelta(hours=SESSION_HOURS)

    payload = {
        "ip": ip_address,
        "exp": expiry,
        "iat": datetime.utcnow(),
        "jti": secrets.token_urlsafe(16)  # JWT ID for uniqueness
    }

    token = jwt.encode(payload, jwt_secret, algorithm="HS256")
    return token


def verify_session_token(token: str, ip_address: str, jwt_secret: str) -> bool:
    """
    Verify a JWT session token.

    Args:
        token: JWT token to verify
        ip_address: Client IP address (must match token payload)
        jwt_secret: Secret key for JWT verification

    Returns:
        True if token is valid and IP matches, False otherwise
    """
    try:
        payload = jwt.decode(token, jwt_secret, algorithms=["HS256"])

        # Verify IP address matches
        if payload.get("ip") != ip_address:
            logger.warning(
                "session_ip_mismatch",
                token_ip=payload.get("ip"),
                request_ip=ip_address
            )
            return False

        return True
    except jwt.ExpiredSignatureError:
        logger.info("session_expired")
        return False
    except jwt.InvalidTokenError as e:
        logger.warning("invalid_session_token", error=str(e))
        return False
    except Exception as e:
        logger.error("session_verification_failed", error=str(e))
        return False


def check_rate_limit(ip_address: str, minutes: int = 15, max_attempts: int = 5) -> bool:
    """
    Check if an IP address has exceeded the login rate limit.

    Args:
        ip_address: Client IP address
        minutes: Time window in minutes (default: 15)
        max_attempts: Maximum failed attempts allowed (default: 5)

    Returns:
        True if under rate limit, False if rate limit exceeded
    """
    SessionLocal = get_session_local()
    session = SessionLocal()

    try:
        cutoff = datetime.utcnow() - timedelta(minutes=minutes)

        # Count failed login attempts in the time window
        failed_attempts = session.query(LoginAttempt).filter(
            LoginAttempt.ip_address == ip_address,
            LoginAttempt.timestamp >= cutoff,
            LoginAttempt.success == False
        ).count()

        if failed_attempts >= max_attempts:
            logger.warning(
                "rate_limit_exceeded",
                ip_address=ip_address,
                attempts=failed_attempts,
                window_minutes=minutes
            )
            return False

        return True
    finally:
        session.close()


def record_login_attempt(
    ip_address: str,
    success: bool,
    user_agent: Optional[str] = None
) -> None:
    """
    Record a login attempt in the database.

    Args:
        ip_address: Client IP address
        success: Whether the login was successful
        user_agent: Client user agent string
    """
    SessionLocal = get_session_local()
    session = SessionLocal()

    try:
        attempt = LoginAttempt(
            ip_address=ip_address,
            success=success,
            user_agent=user_agent,
            timestamp=datetime.utcnow()
        )
        session.add(attempt)
        session.commit()

        logger.info(
            "login_attempt_recorded",
            ip_address=ip_address,
            success=success
        )
    except Exception as e:
        session.rollback()
        logger.error("failed_to_record_login_attempt", error=str(e))
    finally:
        session.close()


def get_client_ip(request: Request) -> str:
    """
    Extract client IP address from request.

    Handles X-Forwarded-For header for proxied requests.

    Args:
        request: FastAPI request object

    Returns:
        Client IP address string
    """
    # Check X-Forwarded-For header (for proxied requests)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # Use first IP in the list (client's original IP)
        return forwarded_for.split(",")[0].strip()

    # Fallback to direct client IP
    return request.client.host if request.client else "unknown"


def require_admin(func):
    """
    Decorator to protect admin routes with session authentication.

    Checks for valid session cookie and redirects to login if not authenticated.

    Usage:
        @router.get("/admin/dashboard")
        @require_admin
        async def get_dashboard(request: Request):
            ...
    """
    @wraps(func)
    async def wrapper(request: Request, *args, **kwargs):
        # Get session token from cookie
        token = request.cookies.get(SESSION_COOKIE_NAME)

        if not token:
            logger.info("no_session_cookie", path=request.url.path)
            return RedirectResponse(url="/admin/login", status_code=302)

        # Get JWT secret from config
        from config import get_settings
        settings = get_settings()
        jwt_secret = settings.admin_jwt_secret

        # Verify token
        client_ip = get_client_ip(request)
        if not verify_session_token(token, client_ip, jwt_secret):
            logger.info("invalid_session", path=request.url.path, ip=client_ip)
            return RedirectResponse(url="/admin/login", status_code=302)

        # Token valid, proceed to route handler
        return await func(request, *args, **kwargs)

    return wrapper
