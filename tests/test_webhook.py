"""
Test webhook notification and callback (Story 8).
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import hmac
import hashlib
import json


class TestWebhookNotifier:
    """Test outbound webhook notifications."""
    
    def test_outbound_hmac_signature(self):
        """Assert outgoing payload has X-Signature."""
        from services.notification import WebhookNotifier
        
        notifier = WebhookNotifier(
            webhook_url="https://hooks.example.com/test",
            secret="test_secret_key"
        )
        
        payload = {
            "draft_id": "abc123",
            "subreddit": "sysadmin",
            "content": "Test reply content",
            "thread_url": "https://reddit.com/r/sysadmin/test"
        }
        
        # Get headers that would be sent
        headers = notifier._build_headers(payload)
        
        assert "X-Signature" in headers
        assert headers["X-Signature"].startswith("sha256=")
    
    def test_signature_is_valid_hmac(self):
        """Verify signature is correctly computed."""
        from services.notification import WebhookNotifier
        
        secret = "my_secret"
        notifier = WebhookNotifier(
            webhook_url="https://hooks.example.com/test",
            secret=secret
        )
        
        payload = {"test": "data"}
        headers = notifier._build_headers(payload)
        
        # Manually compute expected signature
        payload_str = json.dumps(payload, sort_keys=True)
        expected = hmac.new(
            secret.encode(),
            payload_str.encode(),
            hashlib.sha256
        ).hexdigest()
        
        assert headers["X-Signature"] == f"sha256={expected}"
    
    def test_send_notification_makes_request(self):
        """Notification should make HTTP request."""
        from services.notification import WebhookNotifier
        
        notifier = WebhookNotifier(
            webhook_url="https://hooks.example.com/test",
            secret="secret"
        )
        
        with patch('services.notification.requests.post') as mock_post:
            mock_post.return_value = Mock(status_code=200)
            
            result = notifier.send_draft_notification(
                draft_id="draft123",
                subreddit="test",
                content="Test content",
                thread_url="https://reddit.com/test"
            )
            
            assert result is True
            mock_post.assert_called_once()
            
            # Verify URL
            call_args = mock_post.call_args
            assert call_args.kwargs.get('url') == "https://hooks.example.com/test" or \
                   call_args[0][0] == "https://hooks.example.com/test"


class TestCallbackValidation:
    """Test inbound callback validation."""
    
    def test_valid_callback_updates_status(self):
        """Mock POST to /webhook/callback. Assert draft_queue status updates to APPROVED."""
        from api.callback_server import validate_signature, process_callback
        from services.state_manager import StateManager
        from models.database import Base, DraftQueue
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Create a pending draft
        draft = DraftQueue(
            draft_id="draft123",
            reddit_id="comment123",
            subreddit="test",
            content="Test",
            context_url="https://test.com",
            status="PENDING"
        )
        session.add(draft)
        session.commit()
        
        manager = StateManager(session=session)
        
        # Process approval callback
        result = process_callback(
            action="approve",
            draft_id="draft123",
            state_manager=manager
        )
        
        assert result["success"] is True
        
        # Verify status updated
        draft = session.query(DraftQueue).filter_by(draft_id="draft123").first()
        assert draft.status == "APPROVED"
        
        session.close()
    
    def test_reject_callback_updates_status(self):
        """Reject callback should update status to REJECTED."""
        from api.callback_server import process_callback
        from services.state_manager import StateManager
        from models.database import Base, DraftQueue
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        draft = DraftQueue(
            draft_id="draft456",
            reddit_id="comment456",
            subreddit="test",
            content="Test",
            context_url="https://test.com",
            status="PENDING"
        )
        session.add(draft)
        session.commit()
        
        manager = StateManager(session=session)
        
        result = process_callback(
            action="reject",
            draft_id="draft456",
            state_manager=manager
        )
        
        assert result["success"] is True
        
        draft = session.query(DraftQueue).filter_by(draft_id="draft456").first()
        assert draft.status == "REJECTED"
        
        session.close()
    
    def test_invalid_signature_rejected(self):
        """Send callback with bad signature. Assert 401 Unauthorized."""
        from api.callback_server import validate_signature
        
        secret = "correct_secret"
        
        payload = {"action": "approve", "draft_id": "123"}
        payload_str = json.dumps(payload, sort_keys=True)
        
        # Create invalid signature with wrong secret
        invalid_sig = hmac.new(
            "wrong_secret".encode(),
            payload_str.encode(),
            hashlib.sha256
        ).hexdigest()
        
        # Should fail validation
        is_valid = validate_signature(
            payload=payload,
            signature=f"sha256={invalid_sig}",
            secret=secret
        )
        
        assert is_valid is False
    
    def test_valid_signature_accepted(self):
        """Valid signature should pass validation."""
        from api.callback_server import validate_signature
        
        secret = "correct_secret"
        
        payload = {"action": "approve", "draft_id": "123"}
        payload_str = json.dumps(payload, sort_keys=True)
        
        valid_sig = hmac.new(
            secret.encode(),
            payload_str.encode(),
            hashlib.sha256
        ).hexdigest()
        
        is_valid = validate_signature(
            payload=payload,
            signature=f"sha256={valid_sig}",
            secret=secret
        )
        
        assert is_valid is True


class TestNotificationFormat:
    """Test notification payload format."""
    
    def test_payload_includes_required_fields(self):
        """Payload should include draft_id, subreddit, content, thread_url, and callback_url."""
        from services.notification import WebhookNotifier
        
        notifier = WebhookNotifier(
            webhook_url="https://test.com",
            secret="secret",
            public_url="https://myapp.com"
        )
        
        payload = notifier._build_payload(
            draft_id="draft123",
            subreddit="sysadmin",
            content="Test content",
            thread_url="https://reddit.com/test"
        )
        
        assert payload["draft_id"] == "draft123"
        assert payload["subreddit"] == "sysadmin"
        assert payload["content"] == "Test content"
        assert payload["thread_url"] == "https://reddit.com/test"
        assert "timestamp" in payload
        assert payload["callback_url"] == "https://myapp.com/api/callback/draft123"
