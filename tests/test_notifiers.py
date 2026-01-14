"""
Tests for notification adapters (Telegram, Slack).
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import json


class TestTelegramNotifier:
    """Test Telegram notification adapter."""
    
    def test_build_message_format(self):
        """Message should be properly formatted."""
        from services.notifiers.telegram import TelegramNotifier
        
        notifier = TelegramNotifier(
            bot_token="test_token",
            chat_id="123456"
        )
        
        message = notifier._build_message(
            draft_id="draft123",
            subreddit="sysadmin",
            content="This is a test reply.",
            thread_url="https://reddit.com/r/sysadmin/123"
        )
        
        assert "draft123" in message
        assert "r/sysadmin" in message
        assert "This is a test reply." in message
        assert "reddit.com" in message
    
    def test_inline_keyboard_structure(self):
        """Inline keyboard should have approve/reject URL buttons."""
        from services.notifiers.telegram import TelegramNotifier
        
        notifier = TelegramNotifier(
            bot_token="test_token",
            chat_id="123456",
            public_url="https://myapp.com"
        )
        
        keyboard = notifier._build_inline_keyboard("test_token_abc")
        
        assert "inline_keyboard" in keyboard
        buttons = keyboard["inline_keyboard"][0]
        assert len(buttons) == 2
        assert "Approve" in buttons[0]["text"]
        assert "Reject" in buttons[1]["text"]
        # URL buttons have 'url' instead of 'callback_data'
        assert "url" in buttons[0]
        assert "url" in buttons[1]
        assert "test_token_abc" in buttons[0]["url"]
        assert "action=approve" in buttons[0]["url"]
        assert "action=reject" in buttons[1]["url"]
    
    def test_send_message_success(self):
        """Successful send should return True."""
        from services.notifiers.telegram import TelegramNotifier
        
        notifier = TelegramNotifier(
            bot_token="test_token",
            chat_id="123456"
        )
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "ok": True,
            "result": {"message_id": 789}
        }
        
        with patch("requests.post", return_value=mock_response):
            result = notifier._send_message("Test message")
        
        assert result is True
    
    def test_send_message_failure(self):
        """Failed send should return False."""
        from services.notifiers.telegram import TelegramNotifier
        
        notifier = TelegramNotifier(
            bot_token="test_token",
            chat_id="123456"
        )
        
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        
        with patch("requests.post", return_value=mock_response):
            result = notifier._send_message("Test message")
        
        assert result is False
    
    def test_not_configured_returns_false(self):
        """Missing config should return False."""
        from services.notifiers.telegram import TelegramNotifier
        
        notifier = TelegramNotifier(bot_token="", chat_id="")
        
        result = notifier.send_draft_notification(
            draft_id="draft123",
            subreddit="test",
            content="Test",
            thread_url="http://test.com"
        )
        
        assert result is False


class TestSlackNotifier:
    """Test Slack notification adapter."""
    
    def test_build_blocks_structure(self):
        """Blocks should have proper structure."""
        from services.notifiers.slack import SlackNotifier
        
        notifier = SlackNotifier(webhook_url="https://hooks.slack.com/test")
        
        blocks = notifier._build_blocks(
            draft_id="draft123",
            subreddit="sysadmin",
            content="Test content",
            thread_url="https://reddit.com/r/sysadmin/123",
            approval_token="test_token_123"
        )
        
        # Should have header, fields, content, and actions
        block_types = [b["type"] for b in blocks]
        assert "header" in block_types
        assert "section" in block_types
        assert "actions" in block_types
        assert "divider" in block_types
    
    def test_action_buttons_present(self):
        """Actions should have approve/reject URL buttons."""
        from services.notifiers.slack import SlackNotifier
        
        notifier = SlackNotifier(
            webhook_url="https://hooks.slack.com/test",
            public_url="https://myapp.com"
        )
        
        blocks = notifier._build_blocks(
            draft_id="draft123",
            subreddit="test",
            content="Test",
            thread_url="http://test.com",
            approval_token="test_token_abc"
        )
        
        # Find actions block
        actions_block = next(b for b in blocks if b["type"] == "actions")
        elements = actions_block["elements"]
        
        assert len(elements) == 2
        # URL buttons have 'url' instead of 'action_id'
        assert "url" in elements[0]
        assert "url" in elements[1]
        assert "test_token_abc" in elements[0]["url"]
        assert "action=approve" in elements[0]["url"]
        assert "action=reject" in elements[1]["url"]
    
    def test_send_message_success(self):
        """Successful send should return True."""
        from services.notifiers.slack import SlackNotifier
        
        notifier = SlackNotifier(webhook_url="https://hooks.slack.com/test")
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "ok"
        
        with patch("requests.post", return_value=mock_response):
            result = notifier._send_message(text="Test")
        
        assert result is True
    
    def test_send_message_failure(self):
        """Failed send should return False."""
        from services.notifiers.slack import SlackNotifier
        
        notifier = SlackNotifier(webhook_url="https://hooks.slack.com/test")
        
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Server Error"
        
        with patch("requests.post", return_value=mock_response):
            result = notifier._send_message(text="Test")
        
        assert result is False
    
    def test_not_configured_returns_false(self):
        """Missing config should return False."""
        from services.notifiers.slack import SlackNotifier
        
        notifier = SlackNotifier(webhook_url="")
        
        result = notifier.send_draft_notification(
            draft_id="draft123",
            subreddit="test",
            content="Test",
            thread_url="http://test.com",
            approval_token="test_token"
        )
        
        assert result is False


class TestNotifierFactory:
    """Test notifier factory function."""
    
    def test_creates_webhook_notifier(self):
        """Should create webhook notifier."""
        from services.notifiers import get_notifier
        from services.notification import WebhookNotifier
        
        notifier = get_notifier(
            "webhook",
            webhook_url="http://test.com",
            webhook_secret="secret"
        )
        
        assert isinstance(notifier, WebhookNotifier)
    
    def test_creates_telegram_notifier(self):
        """Should create telegram notifier."""
        from services.notifiers import get_notifier
        from services.notifiers.telegram import TelegramNotifier
        
        notifier = get_notifier(
            "telegram",
            telegram_bot_token="token123",
            telegram_chat_id="chat456"
        )
        
        assert isinstance(notifier, TelegramNotifier)
    
    def test_creates_slack_notifier(self):
        """Should create slack notifier."""
        from services.notifiers import get_notifier
        from services.notifiers.slack import SlackNotifier
        
        notifier = get_notifier(
            "slack",
            slack_webhook_url="https://hooks.slack.com/test"
        )
        
        assert isinstance(notifier, SlackNotifier)
    
    def test_unknown_type_raises(self):
        """Unknown type should raise ValueError."""
        from services.notifiers import get_notifier
        
        with pytest.raises(ValueError) as exc_info:
            get_notifier("unknown")
        
        assert "Unknown notification type" in str(exc_info.value)
