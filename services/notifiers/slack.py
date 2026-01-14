"""
Slack notification adapter.

Sends draft notifications to Slack using Block Kit for rich formatting.
Uses URL buttons that open approval page in browser (no Slack App interactivity required).
"""
import json
from datetime import datetime
from typing import Optional, Dict, Any, List

import requests

from utils.logging import get_logger

logger = get_logger(__name__)


class SlackNotifier:
    """
    Send notifications via Slack Incoming Webhooks.
    
    Features:
    - Block Kit formatted messages
    - URL buttons for approve/reject (opens in browser)
    - Status updates
    """
    
    def __init__(
        self,
        webhook_url: str,
        channel: Optional[str] = None,
        public_url: str = "http://localhost:8000",
        timeout: int = 10
    ):
        """
        Initialize Slack notifier.
        
        Args:
            webhook_url: Slack incoming webhook URL
            channel: Optional channel override
            public_url: Base URL for approval links
            timeout: Request timeout in seconds
        """
        self._webhook_url = webhook_url
        self._channel = channel
        self._public_url = public_url.rstrip('/')
        self._timeout = timeout
        
        if not webhook_url:
            logger.warning("slack_webhook_not_configured")
    
    def _build_blocks(
        self,
        draft_id: str,
        subreddit: str,
        content: str,
        thread_url: str,
        approval_token: str
    ) -> List[Dict[str, Any]]:
        """Build Slack Block Kit blocks for the message."""
        approve_url = f"{self._public_url}/approve?token={approval_token}&action=approve"
        reject_url = f"{self._public_url}/approve?token={approval_token}&action=reject"
        
        return [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "📝 New Draft for Approval",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Subreddit:*\nr/{subreddit}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Draft ID:*\n`{draft_id}`"
                    }
                ]
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"<{thread_url}|View Thread on Reddit>"
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Draft Content:*\n\n{content}"
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "actions",
                "block_id": f"draft_actions_{draft_id}",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "✅ Approve",
                            "emoji": True
                        },
                        "style": "primary",
                        "url": approve_url
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "❌ Reject",
                            "emoji": True
                        },
                        "style": "danger",
                        "url": reject_url
                    }
                ]
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"Sent at {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}"
                    }
                ]
            }
        ]
    
    def _send_message(
        self,
        blocks: Optional[List[Dict]] = None,
        text: str = "",
        attachments: Optional[List[Dict]] = None
    ) -> bool:
        """
        Send a message via Slack webhook.
        
        Args:
            blocks: Block Kit blocks
            text: Fallback text
            attachments: Legacy attachments
            
        Returns:
            True if sent successfully
        """
        if not self._webhook_url:
            logger.error("slack_webhook_not_configured")
            return False
        
        payload: Dict[str, Any] = {"text": text}
        
        if blocks:
            payload["blocks"] = blocks
        
        if attachments:
            payload["attachments"] = attachments
        
        if self._channel:
            payload["channel"] = self._channel
        
        try:
            response = requests.post(
                self._webhook_url,
                json=payload,
                timeout=self._timeout
            )
            
            if response.status_code == 200 and response.text == "ok":
                logger.info("slack_message_sent")
                return True
            
            logger.error(
                "slack_send_failed",
                status_code=response.status_code,
                response=response.text[:200]
            )
            return False
            
        except requests.RequestException as e:
            logger.error("slack_request_error", error=str(e))
            return False
    
    def send_draft_notification(
        self,
        draft_id: str,
        subreddit: str,
        content: str,
        thread_url: str,
        approval_token: str
    ) -> bool:
        """
        Send a draft notification with approve/reject URL buttons.
        
        Args:
            draft_id: Draft identifier
            subreddit: Subreddit name
            content: Draft content
            thread_url: URL to the thread
            approval_token: Secure token for approval URL
            
        Returns:
            True if sent successfully
        """
        blocks = self._build_blocks(
            draft_id=draft_id,
            subreddit=subreddit,
            content=content,
            thread_url=thread_url,
            approval_token=approval_token
        )
        
        fallback_text = f"New draft for r/{subreddit}: {content[:100]}..."
        
        return self._send_message(blocks=blocks, text=fallback_text)
    
    def send_status_update(
        self,
        draft_id: str,
        status: str,
        comment_id: Optional[str] = None
    ) -> bool:
        """
        Send a status update notification.
        
        Args:
            draft_id: Draft identifier
            status: New status (APPROVED, REJECTED, PUBLISHED)
            comment_id: Posted comment ID (if published)
            
        Returns:
            True if sent successfully
        """
        emoji = {
            "APPROVED": "✅",
            "REJECTED": "❌",
            "PUBLISHED": "🚀",
            "FAILED": "⚠️"
        }.get(status, "ℹ️")
        
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"{emoji} *Status Update*\n\nDraft `{draft_id}` is now *{status}*"
                }
            }
        ]
        
        if comment_id:
            blocks.append({
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"Comment ID: `{comment_id}`"
                    }
                ]
            })
        
        return self._send_message(
            blocks=blocks,
            text=f"Draft {draft_id} is now {status}"
        )
