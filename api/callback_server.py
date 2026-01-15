"""
Callback server for HITL approval flow.

Implements Story 8: Callback Server
- HMAC signature validation
- Approve/reject endpoints
- Slack interactivity endpoint
- Status updates
"""
import hmac
import hashlib
import json
import urllib.parse
from typing import Dict, Any, Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException, Header, Request, Form, Query, BackgroundTasks
from fastapi.responses import JSONResponse, HTMLResponse
from pydantic import BaseModel

from utils.logging import get_logger
from services.poster import CommentPoster, PublishResult

logger = get_logger(__name__)


# ========================================
# Request/Response Models
# ========================================

class CallbackRequest(BaseModel):
    """Callback request payload."""
    action: str  # "approve" or "reject"
    draft_id: str
    reason: Optional[str] = None


class CallbackResponse(BaseModel):
    """Callback response."""
    success: bool
    message: str
    draft_id: str
    new_status: Optional[str] = None


# ========================================
# Signature Validation
# ========================================

def validate_signature(
    payload: Dict[str, Any],
    signature: str,
    secret: str
) -> bool:
    """
    Validate HMAC signature.
    
    Args:
        payload: Request payload
        signature: Signature header value (sha256=...)
        secret: Expected secret
        
    Returns:
        True if signature is valid
    """
    if not signature or not signature.startswith("sha256="):
        return False
    
    expected_signature = signature[7:]  # Remove "sha256=" prefix
    
    payload_str = json.dumps(payload, sort_keys=True)
    computed = hmac.new(
        secret.encode(),
        payload_str.encode(),
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(expected_signature, computed)


# ========================================
# Callback Processing
# ========================================

def process_callback(
    action: str,
    draft_id: str,
    state_manager: Any,
    reason: Optional[str] = None
) -> Dict[str, Any]:
    """
    Process an approval/rejection callback.
    
    Args:
        action: "approve" or "reject"
        draft_id: Draft to process
        state_manager: StateManager instance
        reason: Optional rejection reason
        
    Returns:
        Result dict with success, message, new_status
    """
    if action not in ["approve", "reject"]:
        return {
            "success": False,
            "message": f"Invalid action: {action}",
            "draft_id": draft_id,
            "new_status": None
        }
    
    # Map action to status
    new_status = "APPROVED" if action == "approve" else "REJECTED"
    
    # Update status
    success = state_manager.update_draft_status(draft_id, new_status)
    
    if success:
        logger.info(
            "callback_processed",
            draft_id=draft_id,
            action=action,
            new_status=new_status
        )

        # Phase 2: Record approval/rejection outcome in performance_history
        try:
            draft = state_manager.get_draft_by_id(draft_id)
            if draft:
                state_manager.record_performance_outcome(
                    draft_id=draft_id,
                    subreddit=draft.subreddit,
                    candidate_type=draft.candidate_type or "comment",
                    quality_score=draft.quality_score or 0.0,
                    outcome=new_status
                )
        except Exception as e:
            # Don't fail callback if performance tracking fails
            logger.warning(
                "performance_tracking_failed",
                draft_id=draft_id,
                action=action,
                error=str(e)
            )

        return {
            "success": True,
            "message": f"Draft {action}d successfully",
            "draft_id": draft_id,
            "new_status": new_status
        }
    else:
        logger.warning(
            "callback_failed",
            draft_id=draft_id,
            action=action
        )
        return {
            "success": False,
            "message": f"Draft not found: {draft_id}",
            "draft_id": draft_id,
            "new_status": None
        }


# ========================================
# Auto-Publish Helper
# ========================================

def _publish_draft_async(draft: Any, poster: CommentPoster) -> None:
    """
    Publish a draft to Reddit (runs as background task).
    
    Args:
        draft: DraftQueue object to publish
        poster: CommentPoster instance
    """
    try:
        logger.info(
            "auto_publish_starting",
            draft_id=draft.draft_id,
            reddit_id=draft.reddit_id,
            subreddit=draft.subreddit
        )
        
        result = poster.publish_single(draft)
        
        if result.success:
            logger.info(
                "auto_publish_success",
                draft_id=draft.draft_id,
                comment_id=result.comment_id
            )
        else:
            logger.error(
                "auto_publish_failed",
                draft_id=draft.draft_id,
                error=result.error
            )
    except Exception as e:
        logger.error(
            "auto_publish_error",
            draft_id=draft.draft_id,
            error=str(e)
        )


# ========================================
# FastAPI Application
# ========================================

def create_callback_app(
    state_manager: Any,
    secret: str,
    poster: Optional[CommentPoster] = None,
    auto_publish: bool = True
) -> FastAPI:
    """
    Create FastAPI app for callback handling.
    
    Args:
        state_manager: StateManager instance
        secret: HMAC secret for validation
        poster: Optional CommentPoster for auto-publishing approved drafts
        auto_publish: If True and poster provided, auto-publish on approval
        
    Returns:
        Configured FastAPI app
    """
    app = FastAPI(
        title="Reddit Agent Callback Server",
        description="HITL approval callback endpoints"
    )
    
    # Store poster for auto-publish
    _poster = poster
    _auto_publish = auto_publish and poster is not None
    
    @app.middleware("http")
    async def add_security_headers(request: Request, call_next):
        """Add security headers to all responses."""
        response = await call_next(request)
        # Prevent token leakage via Referer header
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        return response
    
    @app.post("/api/callback/{draft_id}")
    async def handle_callback(
        draft_id: str,
        request: Request,
        x_signature: str = Header(None, alias="X-Signature")
    ):
        """Handle approval/rejection callback."""
        # Parse body
        body = await request.json()
        
        # Validate signature
        if not validate_signature(body, x_signature, secret):
            raise HTTPException(status_code=401, detail="Invalid signature")
        
        action = body.get("action")
        reason = body.get("reason")
        
        result = process_callback(
            action=action,
            draft_id=draft_id,
            state_manager=state_manager,
            reason=reason
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])
        
        return CallbackResponse(**result)
    
    @app.get("/api/drafts/pending")
    async def get_pending_drafts():
        """Get all pending drafts."""
        drafts = state_manager.get_pending_drafts()
        return {
            "drafts": [
                {
                    "draft_id": d.draft_id,
                    "reddit_id": d.reddit_id,
                    "subreddit": d.subreddit,
                    "content": d.content,
                    "context_url": d.context_url,
                    "created_at": d.created_at.isoformat()
                }
                for d in drafts
            ]
        }
    
    @app.get("/api/drafts/{draft_id}")
    async def get_draft(draft_id: str):
        """Get a specific draft."""
        draft = state_manager.get_draft_by_id(draft_id)
        
        if not draft:
            raise HTTPException(status_code=404, detail="Draft not found")
        
        return {
            "draft_id": draft.draft_id,
            "reddit_id": draft.reddit_id,
            "subreddit": draft.subreddit,
            "content": draft.content,
            "context_url": draft.context_url,
            "status": draft.status,
            "created_at": draft.created_at.isoformat(),
            "approved_at": draft.approved_at.isoformat() if draft.approved_at else None
        }
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}
    
    @app.get("/approve", response_class=HTMLResponse)
    async def handle_approval_link(
        background_tasks: BackgroundTasks,
        token: str = Query(..., description="Approval token"),
        action: str = Query(..., description="Action: approve or reject")
    ):
        """
        Handle approval/rejection via URL link (from Slack buttons).
        
        This is the simpler approach that doesn't require Slack App interactivity.
        Buttons in Slack open this URL in a browser.
        
        If auto_publish is enabled and a poster is configured, approved drafts
        will be automatically posted to Reddit in the background.
        """
        if action not in ["approve", "reject"]:
            return HTMLResponse(
                content=_error_html("Invalid Action", "Action must be 'approve' or 'reject'."),
                status_code=400
            )
        
        # Basic token format validation (fail fast before DB lookup)
        if not token or len(token) < 20:
            logger.warning("approval_invalid_token_format")
            return HTMLResponse(
                content=_error_html("Invalid Link", "This approval link is malformed."),
                status_code=400
            )
        
        # Find draft by token (includes expiration and status check)
        draft = state_manager.get_draft_by_token(token)
        
        if not draft:
            # Token is invalid, expired, or draft already processed
            return HTMLResponse(
                content=_error_html(
                    "Link Expired or Invalid", 
                    "This approval link has expired or has already been used. "
                    "Approval links are valid for 48 hours and can only be used once."
                ),
                status_code=410  # 410 Gone - resource no longer available
            )
        
        # Process the action
        result = process_callback(
            action=action,
            draft_id=draft.draft_id,
            state_manager=state_manager,
            reason=None
        )
        
        if result["success"]:
            status_text = "APPROVED" if action == "approve" else "REJECTED"
            emoji = "✅" if action == "approve" else "❌"
            
            # Auto-publish if approved and poster is configured
            publish_message = ""
            if action == "approve" and _auto_publish and _poster:
                # Re-fetch draft to get updated status
                updated_draft = state_manager.get_draft_by_id(draft.draft_id)
                if updated_draft and updated_draft.status == "APPROVED":
                    # Publish in background to not block the response
                    background_tasks.add_task(_publish_draft_async, updated_draft, _poster)
                    publish_message = " Publishing to Reddit..."
            
            return HTMLResponse(
                content=_success_html(
                    f"{emoji} Draft {status_text}",
                    f"Draft for r/{draft.subreddit} has been {status_text.lower()}.{publish_message}",
                    draft.content[:200] + "..." if len(draft.content) > 200 else draft.content
                ),
                status_code=200
            )
        else:
            return HTMLResponse(
                content=_error_html("Error", result["message"]),
                status_code=400
            )
    
    @app.post("/api/slack/interactions")
    async def handle_slack_interaction(
        request: Request,
        x_slack_signature: str = Header(None, alias="X-Slack-Signature"),
        x_slack_request_timestamp: str = Header(None, alias="X-Slack-Request-Timestamp")
    ):
        """
        Handle Slack interactive component callbacks.
        
        Slack sends button clicks here when users click Approve/Reject.
        The payload is URL-encoded form data with a 'payload' field containing JSON.
        
        Configure this URL in Slack App settings:
        Interactivity & Shortcuts -> Request URL -> {PUBLIC_URL}/api/slack/interactions
        """
        body = await request.body()
        body_str = body.decode("utf-8")
        
        # Validate Slack signature if bot token is configured
        if hasattr(state_manager, 'slack_signing_secret') and state_manager.slack_signing_secret:
            if not _validate_slack_signature(
                body_str, 
                x_slack_signature, 
                x_slack_request_timestamp,
                state_manager.slack_signing_secret
            ):
                logger.warning("slack_signature_validation_failed")
                raise HTTPException(status_code=401, detail="Invalid Slack signature")
        
        # Parse URL-encoded payload
        try:
            parsed = urllib.parse.parse_qs(body_str)
            payload_json = parsed.get("payload", [""])[0]
            payload = json.loads(payload_json)
        except (json.JSONDecodeError, KeyError, IndexError) as e:
            logger.error("slack_payload_parse_error", error=str(e))
            raise HTTPException(status_code=400, detail="Invalid payload")
        
        # Extract action details
        actions = payload.get("actions", [])
        if not actions:
            logger.warning("slack_no_actions_in_payload")
            return JSONResponse({"text": "No action found"})
        
        action = actions[0]
        action_id = action.get("action_id")  # "approve_draft" or "reject_draft"
        draft_id = action.get("value")  # The draft_id we stored in value
        
        if not draft_id:
            logger.warning("slack_no_draft_id", action=action)
            return JSONResponse({"text": "No draft ID found"})
        
        # Map action_id to action
        if action_id == "approve_draft":
            action_type = "approve"
        elif action_id == "reject_draft":
            action_type = "reject"
        else:
            logger.warning("slack_unknown_action", action_id=action_id)
            return JSONResponse({"text": f"Unknown action: {action_id}"})
        
        # Process the callback
        result = process_callback(
            action=action_type,
            draft_id=draft_id,
            state_manager=state_manager,
            reason=None
        )
        
        # Get original message for update
        original_message = payload.get("message", {})
        user_info = payload.get("user", {})
        user_name = user_info.get("username", "Unknown user")
        
        if result["success"]:
            status_emoji = "✅" if action_type == "approve" else "❌"
            status_text = "APPROVED" if action_type == "approve" else "REJECTED"
            
            # Return updated message to replace the original
            return JSONResponse({
                "replace_original": True,
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"{status_emoji} *Draft {status_text}*\n\nDraft `{draft_id}` was {status_text.lower()} by @{user_name}"
                        }
                    },
                    {
                        "type": "context",
                        "elements": [
                            {
                                "type": "mrkdwn",
                                "text": f"Processed at {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}"
                            }
                        ]
                    }
                ]
            })
        else:
            return JSONResponse({
                "replace_original": False,
                "text": f"⚠️ Failed to process: {result['message']}"
            })
    
    return app


def _validate_slack_signature(
    body: str,
    signature: str,
    timestamp: str,
    signing_secret: str
) -> bool:
    """
    Validate Slack request signature.
    
    Args:
        body: Raw request body
        signature: X-Slack-Signature header
        timestamp: X-Slack-Request-Timestamp header
        signing_secret: Slack app signing secret
        
    Returns:
        True if signature is valid
    """
    if not signature or not timestamp:
        return False
    
    # Check timestamp to prevent replay attacks (allow 5 min window)
    try:
        ts = int(timestamp)
        now = int(datetime.utcnow().timestamp())
        if abs(now - ts) > 300:
            return False
    except ValueError:
        return False
    
    # Compute expected signature
    sig_basestring = f"v0:{timestamp}:{body}"
    computed = "v0=" + hmac.new(
        signing_secret.encode(),
        sig_basestring.encode(),
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, computed)


# ========================================
# HTML Response Templates
# ========================================

def _base_html(title: str, content: str, color: str = "#4CAF50") -> str:
    """Generate base HTML template."""
    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - Reddit Agent</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f5f5f5;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }}
        .card {{
            background: white;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            max-width: 500px;
            width: 100%;
            overflow: hidden;
        }}
        .header {{
            background: {color};
            color: white;
            padding: 24px;
            text-align: center;
        }}
        .header h1 {{
            font-size: 24px;
            font-weight: 600;
        }}
        .body {{
            padding: 24px;
        }}
        .message {{
            color: #333;
            font-size: 16px;
            line-height: 1.5;
            margin-bottom: 16px;
        }}
        .draft-content {{
            background: #f9f9f9;
            border-left: 3px solid {color};
            padding: 12px;
            font-size: 14px;
            color: #666;
            border-radius: 4px;
        }}
        .close-hint {{
            text-align: center;
            color: #999;
            font-size: 12px;
            margin-top: 16px;
        }}
    </style>
</head>
<body>
    <div class="card">
        {content}
    </div>
</body>
</html>
"""


def _success_html(title: str, message: str, draft_preview: str = "") -> str:
    """Generate success HTML page."""
    draft_section = f'<div class="draft-content">{draft_preview}</div>' if draft_preview else ""
    content = f"""
        <div class="header">
            <h1>{title}</h1>
        </div>
        <div class="body">
            <p class="message">{message}</p>
            {draft_section}
            <p class="close-hint">You can close this tab.</p>
        </div>
    """
    return _base_html(title, content, "#4CAF50")


def _error_html(title: str, message: str) -> str:
    """Generate error HTML page."""
    content = f"""
        <div class="header">
            <h1>{title}</h1>
        </div>
        <div class="body">
            <p class="message">{message}</p>
        </div>
    """
    return _base_html(title, content, "#f44336")


def _info_html(title: str, message: str) -> str:
    """Generate info HTML page."""
    content = f"""
        <div class="header">
            <h1>{title}</h1>
        </div>
        <div class="body">
            <p class="message">{message}</p>
            <p class="close-hint">You can close this tab.</p>
        </div>
    """
    return _base_html(title, content, "#2196F3")
