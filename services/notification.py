"""
Webhook notification system.

Implements Story 8: Webhook Notifications
- HMAC signed payloads
- Draft notification sending
- Retry logic
"""
import hmac
import hashlib
import json
from datetime import datetime
from typing import Dict, Any, Optional

import requests

from utils.logging import get_logger

logger = get_logger(__name__)


class WebhookError(Exception):
    """Raised when webhook notification fails."""
    pass


class WebhookNotifier:
    """
    Send webhook notifications for draft approval.
    
    Features:
    - HMAC signature for security
    - Structured payload format
    - Retry on failure
    """
    
    def __init__(
        self,
        webhook_url: str,
        secret: str,
        public_url: str = "http://localhost:8000",
        timeout: int = 10,
        max_retries: int = 3
    ):
        """
        Initialize webhook notifier.
        
        Args:
            webhook_url: URL to send notifications to
            secret: HMAC secret for signing
            public_url: Base URL for callback links
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts
        """
        self._url = webhook_url
        self._secret = secret
        self._public_url = public_url.rstrip('/')
        self._timeout = timeout
        self._max_retries = max_retries
        
        logger.debug(
            "webhook_notifier_initialized",
            url=webhook_url,
            public_url=self._public_url,
            timeout=timeout
        )
    
    def _compute_signature(self, payload: Dict[str, Any]) -> str:
        """
        Compute HMAC-SHA256 signature for payload.
        
        Args:
            payload: Payload dict
            
        Returns:
            Signature string prefixed with "sha256="
        """
        payload_str = json.dumps(payload, sort_keys=True)
        signature = hmac.new(
            self._secret.encode(),
            payload_str.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return f"sha256={signature}"
    
    def _build_headers(self, payload: Dict[str, Any]) -> Dict[str, str]:
        """Build request headers with signature."""
        return {
            "Content-Type": "application/json",
            "X-Signature": self._compute_signature(payload),
            "User-Agent": "RedditAgent/1.0"
        }
    
    def _build_payload(
        self,
        draft_id: str,
        subreddit: str,
        content: str,
        thread_url: str,
        approval_token: str = ""
    ) -> Dict[str, Any]:
        """Build notification payload with approval URLs."""
        payload = {
            "draft_id": draft_id,
            "subreddit": subreddit,
            "content": content,
            "thread_url": thread_url,
            "timestamp": datetime.utcnow().isoformat(),
            "callback_url": f"{self._public_url}/api/callback/{draft_id}"
        }
        
        # Include approval URLs if token provided
        if approval_token:
            payload["approve_url"] = f"{self._public_url}/approve?token={approval_token}&action=approve"
            payload["reject_url"] = f"{self._public_url}/approve?token={approval_token}&action=reject"
        
        return payload
    
    def send_draft_notification(
        self,
        draft_id: str,
        subreddit: str,
        content: str,
        thread_url: str,
        approval_token: str = ""
    ) -> bool:
        """
        Send notification for a new draft.
        
        Args:
            draft_id: Draft identifier
            subreddit: Subreddit name
            content: Draft content
            thread_url: Thread URL
            approval_token: Secure token for approval (not used by webhook)
            
        Returns:
            True if sent successfully
        """
        payload = self._build_payload(
            draft_id=draft_id,
            subreddit=subreddit,
            content=content,
            thread_url=thread_url,
            approval_token=approval_token
        )
        headers = self._build_headers(payload)
        
        for attempt in range(self._max_retries):
            try:
                response = requests.post(
                    url=self._url,
                    json=payload,
                    headers=headers,
                    timeout=self._timeout
                )
                
                if response.status_code == 200:
                    logger.info(
                        "notification_sent",
                        draft_id=draft_id,
                        status_code=response.status_code
                    )
                    return True
                
                logger.warning(
                    "notification_failed",
                    draft_id=draft_id,
                    status_code=response.status_code,
                    attempt=attempt + 1
                )
                
            except requests.RequestException as e:
                logger.error(
                    "notification_error",
                    draft_id=draft_id,
                    error=str(e),
                    attempt=attempt + 1
                )
        
        raise WebhookError(f"Failed to send notification after {self._max_retries} attempts")
    
    def send_status_update(
        self,
        draft_id: str,
        status: str,
        comment_id: Optional[str] = None
    ) -> bool:
        """
        Send status update notification.
        
        Args:
            draft_id: Draft identifier
            status: New status
            comment_id: Posted comment ID (if published)
            
        Returns:
            True if sent successfully
        """
        payload = {
            "type": "status_update",
            "draft_id": draft_id,
            "status": status,
            "comment_id": comment_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        headers = self._build_headers(payload)
        
        try:
            response = requests.post(
                url=self._url,
                json=payload,
                headers=headers,
                timeout=self._timeout
            )
            return response.status_code == 200
            
        except requests.RequestException as e:
            logger.error("status_update_failed", draft_id=draft_id, error=str(e))
            return False
