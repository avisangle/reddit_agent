"""
Setup wizard routes for first-time configuration.

Provides a guided 4-step setup process:
1. Reddit API credentials
2. LLM API keys
3. Notification settings
4. Safety limits

Generates .env file on completion.
"""
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
import praw
import requests
import os
import secrets
import subprocess

from utils.logging import get_logger

logger = get_logger(__name__)

# Initialize router
router = APIRouter()

# Initialize Jinja2 templates
templates = Jinja2Templates(directory="frontend/templates")


@router.get("/setup", response_class=HTMLResponse)
async def get_setup_wizard(request: Request):
    """
    Render setup wizard page.

    Only accessible if .env file doesn't exist.
    """
    env_path = Path(".env")

    # If .env exists, redirect to admin login
    if env_path.exists():
        return HTMLResponse(
            content="""
            <html>
            <body>
                <h1>Setup Already Complete</h1>
                <p>The .env file already exists. Please use the admin dashboard to modify settings.</p>
                <a href="/admin/login">Go to Admin Login</a>
            </body>
            </html>
            """,
            status_code=200
        )

    return templates.TemplateResponse(
        "setup.html",
        {"request": request}
    )


@router.get("/api/setup/status", response_class=JSONResponse)
async def get_setup_status():
    """
    Check if setup is already completed.
    
    Returns:
        JSON with is_configured boolean
    """
    env_path = Path(".env")
    return JSONResponse({
        "is_configured": env_path.exists()
    })


@router.post("/api/setup/test-reddit", response_class=JSONResponse)
async def test_reddit_connection(request: Request):
    """
    Test Reddit API credentials.

    Args:
        request: FastAPI request with JSON body containing:
            - client_id: Reddit app client ID
            - client_secret: Reddit app client secret
            - username: Reddit username
            - password: Reddit password
            - user_agent: Reddit user agent

    Returns:
        JSON with success status and user info or error message
    """
    try:
        body = await request.json()
        client_id = body.get("client_id", "").strip()
        client_secret = body.get("client_secret", "").strip()
        username = body.get("username", "").strip()
        password = body.get("password", "").strip()
        user_agent = body.get("user_agent", "").strip()

        # Validate all fields present
        if not all([client_id, client_secret, username, password, user_agent]):
            return JSONResponse({
                "success": False,
                "error": "All fields are required"
            }, status_code=400)

        # Test connection
        reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            username=username,
            password=password,
            user_agent=user_agent
        )

        # Try to get authenticated user
        user = reddit.user.me()

        logger.info("reddit_test_successful", username=user.name)

        return JSONResponse({
            "success": True,
            "username": user.name,
            "karma": user.link_karma + user.comment_karma,
            "created_utc": user.created_utc
        })

    except Exception as e:
        logger.error("reddit_test_failed", error=str(e))
        return JSONResponse({
            "success": False,
            "error": str(e)
        }, status_code=400)


@router.post("/api/setup/test-gemini", response_class=JSONResponse)
async def test_gemini_key(request: Request):
    """
    Test Gemini API key.

    Args:
        request: FastAPI request with JSON body containing:
            - api_key: Gemini API key

    Returns:
        JSON with success status or error message
    """
    try:
        body = await request.json()
        api_key = body.get("api_key", "").strip()

        if not api_key:
            return JSONResponse({
                "success": False,
                "error": "API key is required"
            }, status_code=400)

        # Test Gemini API
        url = "https://generativelanguage.googleapis.com/v1beta/models?key=" + api_key
        response = requests.get(url, timeout=5)

        if response.status_code == 200:
            logger.info("gemini_test_successful")
            return JSONResponse({"success": True})
        else:
            logger.error("gemini_test_failed", status_code=response.status_code)
            return JSONResponse({
                "success": False,
                "error": f"Invalid API key (status {response.status_code})"
            }, status_code=400)

    except Exception as e:
        logger.error("gemini_test_failed", error=str(e))
        return JSONResponse({
            "success": False,
            "error": str(e)
        }, status_code=400)


@router.post("/api/setup/test-slack", response_class=JSONResponse)
async def test_slack_webhook(request: Request):
    """
    Test Slack webhook URL.

    Args:
        request: FastAPI request with JSON body containing:
            - webhook_url: Slack webhook URL

    Returns:
        JSON with success status or error message
    """
    try:
        body = await request.json()
        webhook_url = body.get("webhook_url", "").strip()

        if not webhook_url:
            return JSONResponse({
                "success": False,
                "error": "Webhook URL is required"
            }, status_code=400)

        # Test webhook
        response = requests.post(
            webhook_url,
            json={"text": "✓ Slack webhook test from Reddit Agent Setup"},
            timeout=5
        )

        if response.status_code == 200:
            logger.info("slack_test_successful")
            return JSONResponse({"success": True})
        else:
            logger.error("slack_test_failed", status_code=response.status_code)
            return JSONResponse({
                "success": False,
                "error": f"Invalid webhook URL (status {response.status_code})"
            }, status_code=400)

    except Exception as e:
        logger.error("slack_test_failed", error=str(e))
        return JSONResponse({
            "success": False,
            "error": str(e)
        }, status_code=400)


@router.post("/api/setup/test-telegram", response_class=JSONResponse)
async def test_telegram_bot(request: Request):
    """
    Test Telegram bot credentials.

    Args:
        request: FastAPI request with JSON body containing:
            - bot_token: Telegram bot token
            - chat_id: Telegram chat ID

    Returns:
        JSON with success status or error message
    """
    try:
        body = await request.json()
        bot_token = body.get("bot_token", "").strip()
        chat_id = body.get("chat_id", "").strip()

        if not all([bot_token, chat_id]):
            return JSONResponse({
                "success": False,
                "error": "Bot token and chat ID are required"
            }, status_code=400)

        # Test sendMessage API
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        response = requests.post(
            url,
            json={
                "chat_id": chat_id,
                "text": "✓ Telegram bot test from Reddit Agent Setup"
            },
            timeout=5
        )

        if response.status_code == 200:
            logger.info("telegram_test_successful")
            return JSONResponse({"success": True})
        else:
            logger.error("telegram_test_failed", status_code=response.status_code)
            return JSONResponse({
                "success": False,
                "error": f"Invalid credentials (status {response.status_code})"
            }, status_code=400)

    except Exception as e:
        logger.error("telegram_test_failed", error=str(e))
        return JSONResponse({
            "success": False,
            "error": str(e)
        }, status_code=400)


@router.post("/api/setup/complete", response_class=JSONResponse)
async def complete_setup(request: Request):
    """
    Complete setup wizard - generate .env file.

    Args:
        request: FastAPI request with JSON body containing all config values

    Returns:
        JSON with success status or error message
    """
    try:
        body = await request.json()

        # Validate required fields
        required_fields = [
            "REDDIT_CLIENT_ID",
            "REDDIT_CLIENT_SECRET",
            "REDDIT_USERNAME",
            "REDDIT_PASSWORD",
            "REDDIT_USER_AGENT",
            "ALLOWED_SUBREDDITS",
            "NOTIFICATION_TYPE",
            "PUBLIC_URL"
        ]

        missing_fields = [f for f in required_fields if not body.get(f)]
        if missing_fields:
            return JSONResponse({
                "success": False,
                "error": f"Missing required fields: {', '.join(missing_fields)}"
            }, status_code=400)

        # Validate at least one LLM key
        llm_keys = ["GEMINI_API_KEY", "OPENAI_API_KEY", "ANTHROPIC_API_KEY"]
        if not any(body.get(key) for key in llm_keys):
            return JSONResponse({
                "success": False,
                "error": "At least one LLM API key is required"
            }, status_code=400)

        # Generate .env file
        env_content = []

        # Reddit API
        env_content.append("# Reddit API")
        env_content.append(f"REDDIT_CLIENT_ID={body.get('REDDIT_CLIENT_ID')}")
        env_content.append(f"REDDIT_CLIENT_SECRET={body.get('REDDIT_CLIENT_SECRET')}")
        env_content.append(f"REDDIT_USERNAME={body.get('REDDIT_USERNAME')}")
        env_content.append(f"REDDIT_PASSWORD={body.get('REDDIT_PASSWORD')}")
        env_content.append(f"REDDIT_USER_AGENT={body.get('REDDIT_USER_AGENT')}")
        env_content.append("")

        # Subreddits
        env_content.append("# Subreddits")
        env_content.append(f"ALLOWED_SUBREDDITS={body.get('ALLOWED_SUBREDDITS')}")
        env_content.append("")

        # LLM Keys
        env_content.append("# LLM API Keys")
        if body.get('GEMINI_API_KEY'):
            env_content.append(f"GEMINI_API_KEY={body.get('GEMINI_API_KEY')}")
        if body.get('OPENAI_API_KEY'):
            env_content.append(f"OPENAI_API_KEY={body.get('OPENAI_API_KEY')}")
        if body.get('ANTHROPIC_API_KEY'):
            env_content.append(f"ANTHROPIC_API_KEY={body.get('ANTHROPIC_API_KEY')}")
        env_content.append("")

        # Notifications
        env_content.append("# Notifications")
        env_content.append(f"NOTIFICATION_TYPE={body.get('NOTIFICATION_TYPE')}")
        if body.get('SLACK_WEBHOOK_URL'):
            env_content.append(f"SLACK_WEBHOOK_URL={body.get('SLACK_WEBHOOK_URL')}")
        if body.get('SLACK_CHANNEL'):
            env_content.append(f"SLACK_CHANNEL={body.get('SLACK_CHANNEL')}")
        if body.get('TELEGRAM_BOT_TOKEN'):
            env_content.append(f"TELEGRAM_BOT_TOKEN={body.get('TELEGRAM_BOT_TOKEN')}")
        if body.get('TELEGRAM_CHAT_ID'):
            env_content.append(f"TELEGRAM_CHAT_ID={body.get('TELEGRAM_CHAT_ID')}")
        if body.get('WEBHOOK_URL'):
            env_content.append(f"WEBHOOK_URL={body.get('WEBHOOK_URL')}")
        if body.get('WEBHOOK_SECRET'):
            env_content.append(f"WEBHOOK_SECRET={body.get('WEBHOOK_SECRET')}")
        env_content.append(f"PUBLIC_URL={body.get('PUBLIC_URL')}")
        env_content.append("")

        # Safety Limits
        env_content.append("# Safety Limits")
        env_content.append(f"MAX_COMMENTS_PER_DAY={body.get('MAX_COMMENTS_PER_DAY', '8')}")
        env_content.append(f"MAX_COMMENTS_PER_RUN={body.get('MAX_COMMENTS_PER_RUN', '3')}")
        env_content.append(f"SHADOWBAN_RISK_THRESHOLD={body.get('SHADOWBAN_RISK_THRESHOLD', '0.7')}")
        env_content.append(f"COOLDOWN_PERIOD_HOURS={body.get('COOLDOWN_PERIOD_HOURS', '24')}")
        env_content.append(f"POST_REPLY_RATIO={body.get('POST_REPLY_RATIO', '0.3')}")
        env_content.append(f"MAX_POST_REPLIES_PER_RUN={body.get('MAX_POST_REPLIES_PER_RUN', '1')}")
        env_content.append(f"MAX_COMMENT_REPLIES_PER_RUN={body.get('MAX_COMMENT_REPLIES_PER_RUN', '2')}")
        env_content.append("")

        # Admin (generate secure defaults)
        env_content.append("# Admin")
        env_content.append("ADMIN_PASSWORD_HASH=  # Set with: python -c \"import bcrypt; print(bcrypt.hashpw(b'your-password', bcrypt.gensalt(12)).decode())\"")
        env_content.append(f"ADMIN_JWT_SECRET={secrets.token_urlsafe(32)}")
        env_content.append("ADMIN_SESSION_HOURS=24")
        env_content.append("")

        # Write to .env file
        with open(".env", "w") as f:
            f.write("\n".join(env_content))

        logger.info("setup_completed", notification_type=body.get('NOTIFICATION_TYPE'))

        # Try to run migrations
        try:
            result = subprocess.run(
                ["alembic", "upgrade", "head"],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                migrations_success = True
                migrations_message = "Database migrations completed successfully"
            else:
                migrations_success = False
                migrations_message = f"Migration warning: {result.stderr}"
        except Exception as e:
            migrations_success = False
            migrations_message = f"Could not run migrations: {str(e)}"

        return JSONResponse({
            "success": True,
            "message": "Setup completed successfully!",
            "migrations_success": migrations_success,
            "migrations_message": migrations_message
        })

    except Exception as e:
        logger.error("setup_failed", error=str(e))
        return JSONResponse({
            "success": False,
            "error": str(e)
        }, status_code=500)
