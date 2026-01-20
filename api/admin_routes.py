"""
Admin routes for dashboard, .env editor, and audit log.

Provides password-protected admin interface with Jinja2 templates.
"""
from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from api.auth import (
    verify_password,
    create_session_token,
    check_rate_limit,
    record_login_attempt,
    get_client_ip,
    require_admin,
    SESSION_COOKIE_NAME
)
from models.database import get_db, get_db_optional
from services.dashboard_service import DashboardService
from services.audit_logger import AuditLogger
from services.workflow_visualizer import WorkflowVisualizer, get_workflow_metadata
from services.env_manager import EnvManager
from config import get_settings
from utils.logging import get_logger

logger = get_logger(__name__)

# Initialize router
router = APIRouter()

# Initialize Jinja2 templates
templates = Jinja2Templates(directory="frontend/templates")

# Initialize services
dashboard_service = DashboardService()
audit_logger = AuditLogger()
workflow_visualizer = WorkflowVisualizer()
env_manager = EnvManager()


@router.get("/admin/")
@router.get("/admin")
async def admin_root():
    """Redirect /admin/ to /admin/login."""
    return RedirectResponse(url="/admin/login", status_code=302)


@router.get("/admin/login", response_class=HTMLResponse)
async def get_login_page(request: Request):
    """Render admin login page."""
    return templates.TemplateResponse(
        "admin/login.html",
        {"request": request}
    )


@router.post("/admin/login")
async def handle_login(
    request: Request,
    password: str = Form(...),
    session: Session = Depends(get_db_optional)
):
    """
    Handle admin login with rate limiting and audit logging.

    Args:
        request: FastAPI request object
        password: Form password field
        session: Optional database session (None during setup mode)

    Returns:
        Redirect to dashboard on success, login page with error on failure
    """
    try:
        settings = get_settings()
    except Exception as e:
        # Settings can't be loaded (incomplete .env)
        logger.warning("login_failed_no_settings", error=str(e))
        return templates.TemplateResponse(
            "admin/login.html",
            {
                "request": request,
                "error": "Configuration incomplete. Please complete setup wizard first at /setup"
            }
        )

    client_ip = get_client_ip(request)
    user_agent = request.headers.get("User-Agent")

    # Check rate limit (skip if no database available)
    if session is not None and not check_rate_limit(client_ip):
        logger.warning("login_rate_limited", ip=client_ip)
        audit_logger.log_login(
            ip_address=client_ip,
            success=False,
            user_agent=user_agent,
            reason="rate_limited"
        )
        return templates.TemplateResponse(
            "admin/login.html",
            {
                "request": request,
                "error": "Too many failed attempts. Please try again in 15 minutes."
            }
        )

    # Verify password
    if not verify_password(password, settings.admin_password_hash):
        logger.info("login_failed_invalid_password", ip=client_ip)

        # Record failed attempt (skip if no database)
        if session is not None:
            record_login_attempt(client_ip, success=False, user_agent=user_agent)
            audit_logger.log_login(
                ip_address=client_ip,
                success=False,
                user_agent=user_agent,
                reason="invalid_password"
            )

        return templates.TemplateResponse(
            "admin/login.html",
            {
                "request": request,
                "error": "Invalid password."
            }
        )

    # Password correct - create session
    token = create_session_token(client_ip, settings.admin_jwt_secret)

    # Record successful attempt (skip if no database)
    if session is not None:
        record_login_attempt(client_ip, success=True, user_agent=user_agent)
        audit_logger.log_login(
            ip_address=client_ip,
            success=True,
            user_agent=user_agent
        )

    logger.info("login_successful", ip=client_ip)

    # Set session cookie and redirect to dashboard
    response = RedirectResponse(url="/admin/dashboard", status_code=302)
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=token,
        httponly=True,  # Prevent XSS
        max_age=settings.admin_session_hours * 3600,
        samesite="lax"
    )

    return response


@router.post("/admin/api/login", response_class=JSONResponse)
async def handle_api_login(
    request: Request,
    session: Session = Depends(get_db_optional)
):
    """
    Handle admin login via JSON API (for React frontend).

    Returns JSON response with session cookie.
    """
    try:
        body = await request.json()
        password = body.get("password", "")
    except Exception:
        return JSONResponse({"success": False, "error": "Invalid JSON body"}, status_code=400)

    try:
        settings = get_settings()
    except Exception as e:
        return JSONResponse(
            {"success": False, "error": "Configuration incomplete. Please complete setup wizard first at /setup"},
            status_code=500
        )

    client_ip = get_client_ip(request)
    user_agent = request.headers.get("User-Agent")

    # Check rate limit
    if session is not None and not check_rate_limit(client_ip):
        return JSONResponse(
            {"success": False, "error": "Too many failed attempts. Please try again in 15 minutes."},
            status_code=429
        )

    # Verify password
    if not verify_password(password, settings.admin_password_hash):
        if session is not None:
            record_login_attempt(client_ip, success=False, user_agent=user_agent)
        return JSONResponse(
            {"success": False, "error": "Invalid password"},
            status_code=401
        )

    # Password correct - create session
    token = create_session_token(client_ip, settings.admin_jwt_secret)

    if session is not None:
        record_login_attempt(client_ip, success=True, user_agent=user_agent)

    logger.info("api_login_successful", ip=client_ip)

    # Set session cookie in JSON response
    response = JSONResponse({"success": True, "message": "Login successful"})
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=token,
        httponly=True,
        max_age=settings.admin_session_hours * 3600,
        samesite="lax"
    )

    return response


@router.get("/admin/api/check-auth")
@require_admin
async def check_auth(request: Request):
    """
    Lightweight endpoint to check if session is valid.

    Used by Next.js middleware to validate authentication.
    Protected by @require_admin - returns 302 redirect if invalid.
    """
    return JSONResponse({"authenticated": True}, status_code=200)


@router.get("/admin/dashboard", response_class=HTMLResponse)
@require_admin
async def get_dashboard(request: Request, session: Session = Depends(get_db_optional)):
    """
    Render admin dashboard with metrics and charts.

    Protected by @require_admin decorator.
    """
    # Check if database is available
    if session is None:
        return templates.TemplateResponse(
            "admin/dashboard.html",
            {
                "request": request,
                "stats": None,
                "error": "Configuration incomplete. Please complete setup wizard first at <a href='/setup'>/setup</a>"
            }
        )

    # Get dashboard data
    data = dashboard_service.get_dashboard_data(session)

    return templates.TemplateResponse(
        "admin/dashboard.html",
        {
            "request": request,
            "stats": data
        }
    )


@router.get("/admin/api/dashboard", response_class=JSONResponse)
@require_admin
async def get_dashboard_stats(request: Request, session: Session = Depends(get_db_optional)):
    """
    API endpoint for React dashboard - returns full dashboard data.

    Used by Next.js frontend to populate dashboard with real-time stats.
    Protected by @require_admin decorator.

    Returns:
        JSONResponse with:
        - status_counts: Draft counts by status (PENDING, APPROVED, PUBLISHED, REJECTED)
        - daily_count: Today's comment count vs limit
        - performance: Approval/publish rates
        - weekly_trend: Last 7 days comment counts
        - subreddit_distribution: Activity by subreddit
        - recent_drafts: Latest draft submissions
    """
    if session is None:
        return JSONResponse({"error": "Database not available"}, status_code=503)

    try:
        data = dashboard_service.get_dashboard_data(session)
        return JSONResponse({"success": True, "data": data})
    except Exception as e:
        logger.error("dashboard_api_error", error=str(e))
        return JSONResponse(
            {"success": False, "error": "Failed to load dashboard data"},
            status_code=500
        )


@router.get("/admin/api/live", response_class=JSONResponse)
@require_admin
async def get_live_stats(request: Request, session: Session = Depends(get_db_optional)):
    """
    API endpoint for HTMX polling - returns real-time stats.

    Protected by @require_admin decorator.
    """
    if session is None:
        return JSONResponse({"error": "Database not available"}, status_code=503)

    stats = dashboard_service.get_realtime_stats(session)
    return JSONResponse(stats)


@router.get("/admin/api/live-stats", response_class=HTMLResponse)
@require_admin
async def get_live_stats_html(request: Request, session: Session = Depends(get_db_optional)):
    """
    HTMX endpoint - returns HTML fragment with updated stats grid.

    Protected by @require_admin decorator.
    Polled every 30 seconds by dashboard.
    """
    data = dashboard_service.get_dashboard_data(session)

    html = f"""
    <div class="stats-grid" hx-get="/admin/api/live-stats" hx-trigger="every 30s" hx-swap="outerHTML">
        <div class="stat-card">
            <h3>Pending Drafts</h3>
            <p class="stat-value">{data['status_counts']['PENDING']}</p>
        </div>

        <div class="stat-card">
            <h3>Today's Comments</h3>
            <p class="stat-value">{data['daily_count']['count']} / {data['daily_count']['limit']}</p>
            <p class="stat-label">{data['daily_count']['percentage']}% of daily limit</p>
        </div>

        <div class="stat-card">
            <h3>Approval Rate</h3>
            <p class="stat-value">{data['performance']['approval_rate']}%</p>
            <p class="stat-label">Last 7 days</p>
        </div>

        <div class="stat-card">
            <h3>Publish Rate</h3>
            <p class="stat-value">{data['performance']['publish_rate']}%</p>
            <p class="stat-label">Last 7 days</p>
        </div>
    </div>
    """

    return HTMLResponse(html)


@router.get("/admin/logout")
async def logout(request: Request):
    """Clear session cookie and redirect to login."""
    client_ip = get_client_ip(request)
    logger.info("logout", ip=client_ip)

    response = RedirectResponse(url="/admin/login", status_code=302)
    response.delete_cookie(SESSION_COOKIE_NAME)
    return response


@router.get("/admin/workflow", response_class=HTMLResponse)
@require_admin
async def get_workflow_visualizer(request: Request):
    """
    Render workflow visualizer with interactive SVG diagram.

    Protected by @require_admin decorator.
    """
    # Generate SVG diagram
    svg_content = workflow_visualizer.generate_svg()

    # Get metadata for modal and stats
    metadata = get_workflow_metadata()

    return templates.TemplateResponse(
        "workflow.html",
        {
            "request": request,
            "svg_content": svg_content,
            "metadata": metadata
        }
    )


# ===== .env Editor Routes =====

@router.get("/admin/env", response_class=HTMLResponse)
@require_admin
async def get_env_editor(request: Request):
    """
    Render .env editor page.

    Protected by @require_admin decorator.
    """
    try:
        # Load current .env
        env_vars = env_manager.load_env()

        # Get field metadata for rendering
        field_metadata = env_manager.get_field_metadata()

        # Get backup list
        backups = env_manager.list_backups()

        return templates.TemplateResponse(
            "admin/env_editor.html",
            {
                "request": request,
                "env_vars": env_vars,
                "field_metadata": field_metadata,
                "backups": backups
            }
        )
    except Exception as e:
        logger.error("env_editor_load_failed", error=str(e))
        return templates.TemplateResponse(
            "admin/env_editor.html",
            {
                "request": request,
                "error": f"Failed to load .env file: {str(e)}",
                "env_vars": {},
                "field_metadata": {},
                "backups": []
            }
        )


@router.get("/admin/api/env", response_class=JSONResponse)
@require_admin
async def get_env_json(request: Request):
    """
    API endpoint to get current .env values as JSON.

    Protected by @require_admin decorator.
    Used by the React frontend settings page.
    """
    try:
        env_vars = env_manager.load_env()
        field_metadata = env_manager.get_field_metadata()
        return JSONResponse({
            "success": True,
            "env_vars": env_vars,
            "field_metadata": field_metadata
        })
    except Exception as e:
        logger.error("env_api_load_failed", error=str(e))
        return JSONResponse({
            "success": False,
            "error": str(e)
        }, status_code=500)


@router.post("/admin/api/env/preview", response_class=JSONResponse)
@require_admin
async def preview_env_changes(request: Request):
    """
    Preview changes to .env file (show diff).

    Protected by @require_admin decorator.
    """
    try:
        # Get new values from request body
        body = await request.json()
        new_env = body.get("env_vars", {})

        # Load current .env
        current_env = env_manager.load_env()

        # Merge new values with current (so missing fields use current values)
        merged_env = {**current_env, **new_env}

        # Generate diff
        diff = env_manager.preview_changes(current_env, new_env)

        # Validate merged environment (not just new values)
        validation_errors = env_manager.validate_env(merged_env)

        return JSONResponse({
            "success": validation_errors is None,
            "diff": diff,
            "errors": validation_errors
        })

    except Exception as e:
        logger.error("env_preview_failed", error=str(e))
        return JSONResponse({
            "success": False,
            "error": str(e)
        }, status_code=400)


@router.post("/admin/api/env/save", response_class=JSONResponse)
@require_admin
async def save_env_changes(request: Request, session: Session = Depends(get_db_optional)):
    """
    Save changes to .env file.

    Protected by @require_admin decorator.
    """
    client_ip = get_client_ip(request)

    try:
        # Get new values from request body
        body = await request.json()
        new_env = body.get("env_vars", {})

        # Load current .env for audit logging
        current_env = env_manager.load_env()

        # Merge new values with current (so unchanged fields keep their values)
        merged_env = {**current_env, **new_env}

        # Save merged environment with validation and backup
        env_manager.save_env(merged_env, create_backup=True)

        # Log to audit log (with redacted values) - skip if no database
        diff = env_manager.preview_changes(current_env, new_env)
        changed_fields = [k for k, v in diff.items() if v["changed"]]

        if session is not None:
            audit_logger.log_env_update(
                ip_address=client_ip,
                changed_fields=changed_fields,
                success=True
            )

        logger.info("env_saved_by_admin", ip=client_ip, fields_changed=len(changed_fields))

        return JSONResponse({
            "success": True,
            "message": f"Saved {len(changed_fields)} changes. Backup created.",
            "fields_changed": len(changed_fields)
        })

    except Exception as e:
        logger.error("env_save_failed", error=str(e), ip=client_ip)
        return JSONResponse({
            "success": False,
            "error": str(e)
        }, status_code=400)


@router.post("/admin/api/env/restore", response_class=JSONResponse)
@require_admin
async def restore_env_backup(request: Request, session: Session = Depends(get_db_optional)):
    """
    Restore .env from a backup.

    Protected by @require_admin decorator.
    """
    client_ip = get_client_ip(request)

    try:
        # Get backup path from request body
        body = await request.json()
        backup_path = body.get("backup_path")

        if not backup_path:
            return JSONResponse({
                "success": False,
                "error": "backup_path is required"
            }, status_code=400)

        # Restore from backup
        env_manager.restore_backup(backup_path)

        # Log to audit log - skip if no database
        if session is not None:
            audit_logger.log_backup_restore(
                ip_address=client_ip,
                backup_file=backup_path,
                success=True
            )

        logger.info("env_restored_by_admin", ip=client_ip, backup_path=backup_path)

        return JSONResponse({
            "success": True,
            "message": f"Restored from backup: {backup_path}"
        })

    except FileNotFoundError as e:
        return JSONResponse({
            "success": False,
            "error": str(e)
        }, status_code=404)
    except Exception as e:
        logger.error("env_restore_failed", error=str(e), ip=client_ip)
        return JSONResponse({
            "success": False,
            "error": str(e)
        }, status_code=400)
