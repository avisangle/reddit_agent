"""
Notification adapters for different platforms.

Supports:
- Generic webhook
- Telegram
- Slack
"""
from typing import Protocol, Optional
from abc import abstractmethod

from utils.logging import get_logger

logger = get_logger(__name__)


class NotifierProtocol(Protocol):
    """Protocol for notification adapters."""
    
    @abstractmethod
    def send_draft_notification(
        self,
        draft_id: str,
        subreddit: str,
        content: str,
        thread_url: str,
        approval_token: str = ""
    ) -> bool:
        """Send a draft notification."""
        ...
    
    @abstractmethod
    def send_status_update(
        self,
        draft_id: str,
        status: str,
        comment_id: Optional[str] = None
    ) -> bool:
        """Send a status update."""
        ...


def get_notifier(notification_type: str, **kwargs):
    """
    Factory function to create the appropriate notifier.
    
    Args:
        notification_type: One of 'webhook', 'telegram', 'slack'
        **kwargs: Configuration for the notifier
        
    Returns:
        Notifier instance
    """
    from services.notification import WebhookNotifier
    from services.notifiers.telegram import TelegramNotifier
    from services.notifiers.slack import SlackNotifier
    
    notifiers = {
        "webhook": lambda: WebhookNotifier(
            webhook_url=kwargs.get("webhook_url", ""),
            secret=kwargs.get("webhook_secret", ""),
            public_url=kwargs.get("public_url", "http://localhost:8000")
        ),
        "telegram": lambda: TelegramNotifier(
            bot_token=kwargs.get("telegram_bot_token", ""),
            chat_id=kwargs.get("telegram_chat_id", ""),
            public_url=kwargs.get("public_url", "http://localhost:8000")
        ),
        "slack": lambda: SlackNotifier(
            webhook_url=kwargs.get("slack_webhook_url", ""),
            channel=kwargs.get("slack_channel"),
            public_url=kwargs.get("public_url", "http://localhost:8000")
        ),
    }
    
    if notification_type not in notifiers:
        raise ValueError(f"Unknown notification type: {notification_type}")
    
    logger.info("notifier_created", type=notification_type)
    return notifiers[notification_type]()
