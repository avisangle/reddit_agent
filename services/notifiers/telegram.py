"""
Telegram notification adapter.

Sends draft notifications to Telegram with URL-based approve/reject buttons.
Uses the same token-based approval flow as Slack for consistency.
"""
import json
from datetime import datetime
from typing import Optional, Dict, Any

import requests

from utils.logging import get_logger

logger = get_logger(__name__)


class TelegramNotifier:
    """
    Send notifications via Telegram Bot API.
    
    Features:
    - Formatted draft messages
    - URL buttons for approve/reject (opens browser)
    - Status updates
    """
    
    BASE_URL = "https://api.telegram.org/bot{token}"
    
    def __init__(
        self,
        bot_token: str,
        chat_id: str,
        public_url: str = "http://localhost:8000",
        timeout: int = 10
    ):
        """
        Initialize Telegram notifier.
        
        Args:
            bot_token: Telegram bot token from @BotFather
            chat_id: Chat ID to send messages to
            public_url: Base URL for approval links
            timeout: Request timeout in seconds
        """
        self._bot_token = bot_token
        self._chat_id = chat_id
        self._public_url = public_url.rstrip('/')
        self._timeout = timeout
        self._base_url = self.BASE_URL.format(token=bot_token)
        
        if not bot_token or not chat_id:
            logger.warning("telegram_config_incomplete")
    
    def _build_message(
        self,
        draft_id: str,
        subreddit: str,
        content: str,
        thread_url: str
    ) -> str:
        """Build formatted message text."""
        return f"""📝 *New Draft for Approval*

*Subreddit:* r/{subreddit}
*Thread:* [View on Reddit]({thread_url})
*Draft ID:* `{draft_id}`

───────────────

{content}

───────────────

Click the buttons below to approve or reject."""
    
    def _build_inline_keyboard(self, approval_token: str) -> Dict[str, Any]:
        """Build inline keyboard with URL buttons for approve/reject."""
        approve_url = f"{self._public_url}/approve?token={approval_token}&action=approve"
        reject_url = f"{self._public_url}/approve?token={approval_token}&action=reject"
        
        return {
            "inline_keyboard": [
                [
                    {
                        "text": "✅ Approve",
                        "url": approve_url
                    },
                    {
                        "text": "❌ Reject",
                        "url": reject_url
                    }
                ]
            ]
        }
    
    def _send_message(
        self,
        text: str,
        reply_markup: Optional[Dict] = None,
        parse_mode: str = "Markdown"
    ) -> bool:
        """
        Send a message via Telegram API.
        
        Args:
            text: Message text
            reply_markup: Optional keyboard markup
            parse_mode: Parse mode (Markdown or HTML)
            
        Returns:
            True if sent successfully
        """
        if not self._bot_token or not self._chat_id:
            logger.error("telegram_not_configured")
            return False
        
        url = f"{self._base_url}/sendMessage"
        
        payload = {
            "chat_id": self._chat_id,
            "text": text,
            "parse_mode": parse_mode,
            "disable_web_page_preview": False
        }
        
        if reply_markup:
            payload["reply_markup"] = json.dumps(reply_markup)
        
        try:
            response = requests.post(
                url,
                json=payload,
                timeout=self._timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("ok"):
                    logger.info(
                        "telegram_message_sent",
                        chat_id=self._chat_id,
                        message_id=result.get("result", {}).get("message_id")
                    )
                    return True
            
            logger.error(
                "telegram_send_failed",
                status_code=response.status_code,
                response=response.text[:200]
            )
            return False
            
        except requests.RequestException as e:
            logger.error("telegram_request_error", error=str(e))
            return False
    
    def send_draft_notification(
        self,
        draft_id: str,
        subreddit: str,
        content: str,
        thread_url: str,
        approval_token: str = ""
    ) -> bool:
        """
        Send a draft notification with approve/reject URL buttons.
        
        Args:
            draft_id: Draft identifier
            subreddit: Subreddit name
            content: Draft content
            thread_url: URL to the thread
            approval_token: Secure token for approval URLs
            
        Returns:
            True if sent successfully
        """
        if not approval_token:
            logger.error("telegram_missing_approval_token", draft_id=draft_id)
            return False
        
        message = self._build_message(
            draft_id=draft_id,
            subreddit=subreddit,
            content=content,
            thread_url=thread_url
        )
        
        keyboard = self._build_inline_keyboard(approval_token)
        
        return self._send_message(text=message, reply_markup=keyboard)
    
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
        
        message = f"{emoji} *Status Update*\n\nDraft `{draft_id}` is now *{status}*"
        
        if comment_id:
            message += f"\n\nComment ID: `{comment_id}`"
        
        return self._send_message(text=message)
