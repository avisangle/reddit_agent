"""
Test state manager with idempotency and cooldowns (Story 7).
"""
import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class TestIdempotency:
    """Test duplicate prevention."""
    
    def test_duplicate_draft_skipped(self):
        """Try to insert draft with existing reddit_id. Assert graceful skip."""
        from services.state_manager import StateManager
        from models.database import Base, DraftQueue
        
        # Create in-memory database
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        manager = StateManager(session=session)
        
        # Insert first draft - returns approval token on success
        result1 = manager.save_draft(
            draft_id="draft1",
            reddit_id="comment123",
            subreddit="test",
            content="First content",
            context_url="https://reddit.com/test"
        )
        assert result1 is not None  # Returns token string on success
        assert isinstance(result1, str)
        
        # Try to insert duplicate
        result2 = manager.save_draft(
            draft_id="draft2",
            reddit_id="comment123",  # Same reddit_id
            subreddit="test",
            content="Different content",
            context_url="https://reddit.com/test"
        )
        
        # Should be skipped gracefully - returns None for duplicate
        assert result2 is None
        
        # Only one draft in database
        count = session.query(DraftQueue).count()
        assert count == 1
        
        session.close()


class TestCooldowns:
    """Test cooldown logic for failed items."""
    
    def test_failed_item_not_retryable_during_cooldown(self):
        """
        Mark an item as FAILED with timestamp T.
        Try to process at T + 10 mins. Assert is_retryable returns False.
        """
        from services.state_manager import StateManager
        from models.database import Base, RepliedItem
        
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        manager = StateManager(session=session, cooldown_hours=24)
        
        # Create failed item 10 minutes ago
        failed_time = datetime.utcnow() - timedelta(minutes=10)
        item = RepliedItem(
            reddit_id="failed123",
            subreddit="test",
            status="FAILED",
            last_attempt=failed_time
        )
        session.add(item)
        session.commit()
        
        # Should not be retryable (within cooldown)
        assert manager.is_retryable("failed123") is False
        
        session.close()
    
    def test_failed_item_retryable_after_cooldown(self):
        """
        Mark an item as FAILED with timestamp T.
        Try to process at T + 24 hours. Assert is_retryable returns True.
        """
        from services.state_manager import StateManager
        from models.database import Base, RepliedItem
        
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        manager = StateManager(session=session, cooldown_hours=24)
        
        # Create failed item 25 hours ago
        failed_time = datetime.utcnow() - timedelta(hours=25)
        item = RepliedItem(
            reddit_id="oldfail123",
            subreddit="test",
            status="FAILED",
            last_attempt=failed_time
        )
        session.add(item)
        session.commit()
        
        # Should be retryable (after cooldown)
        assert manager.is_retryable("oldfail123") is True
        
        session.close()
    
    def test_success_item_not_retryable(self):
        """Successfully processed items should never be retried."""
        from services.state_manager import StateManager
        from models.database import Base, RepliedItem
        
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        manager = StateManager(session=session)
        
        item = RepliedItem(
            reddit_id="success123",
            subreddit="test",
            status="SUCCESS",
            last_attempt=datetime.utcnow()
        )
        session.add(item)
        session.commit()
        
        # Should not be retryable
        assert manager.is_retryable("success123") is False
        
        session.close()


class TestStatusFlow:
    """Test state transitions."""
    
    def test_pending_to_approved(self):
        """Verify transition: PENDING -> APPROVED."""
        from services.state_manager import StateManager
        from models.database import Base, DraftQueue
        
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        manager = StateManager(session=session)
        
        # Create pending draft
        manager.save_draft(
            draft_id="draft1",
            reddit_id="test123",
            subreddit="test",
            content="Test",
            context_url="https://test.com"
        )
        
        # Approve it
        result = manager.update_draft_status("draft1", "APPROVED")
        assert result is True
        
        # Verify status
        draft = session.query(DraftQueue).filter_by(draft_id="draft1").first()
        assert draft.status == "APPROVED"
        assert draft.approved_at is not None
        
        session.close()
    
    def test_approved_to_published(self):
        """Verify transition: APPROVED -> PUBLISHED."""
        from services.state_manager import StateManager
        from models.database import Base, DraftQueue
        
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        manager = StateManager(session=session)
        
        manager.save_draft(
            draft_id="draft1",
            reddit_id="test123",
            subreddit="test",
            content="Test",
            context_url="https://test.com"
        )
        manager.update_draft_status("draft1", "APPROVED")
        
        # Publish
        result = manager.update_draft_status("draft1", "PUBLISHED")
        assert result is True
        
        draft = session.query(DraftQueue).filter_by(draft_id="draft1").first()
        assert draft.status == "PUBLISHED"
        
        session.close()
    
    def test_pending_to_rejected(self):
        """Verify transition: PENDING -> REJECTED."""
        from services.state_manager import StateManager
        from models.database import Base, DraftQueue
        
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        manager = StateManager(session=session)
        
        manager.save_draft(
            draft_id="draft1",
            reddit_id="test123",
            subreddit="test",
            content="Test",
            context_url="https://test.com"
        )
        
        # Reject
        result = manager.update_draft_status("draft1", "REJECTED")
        assert result is True
        
        draft = session.query(DraftQueue).filter_by(draft_id="draft1").first()
        assert draft.status == "REJECTED"
        
        session.close()


class TestDailyLimits:
    """Test daily volume limit tracking."""
    
    def test_increments_daily_count(self):
        """Posting should increment daily count."""
        from services.state_manager import StateManager
        from models.database import Base
        
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        manager = StateManager(session=session, max_daily=8)
        
        initial = manager.get_daily_count()
        manager.increment_daily_count()
        
        assert manager.get_daily_count() == initial + 1
        
        session.close()
    
    def test_daily_limit_check(self):
        """Should detect when daily limit reached."""
        from services.state_manager import StateManager
        from models.database import Base, DailyStats
        from datetime import date
        
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        manager = StateManager(session=session, max_daily=8)
        
        # Set count to limit
        stats = DailyStats(date=date.today(), comment_count=8)
        session.add(stats)
        session.commit()
        
        assert manager.can_post_today() is False
        
        session.close()
    
    def test_under_limit_can_post(self):
        """Under limit should allow posting."""
        from services.state_manager import StateManager
        from models.database import Base, DailyStats
        from datetime import date
        
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        manager = StateManager(session=session, max_daily=8)
        
        # Set count below limit
        stats = DailyStats(date=date.today(), comment_count=5)
        session.add(stats)
        session.commit()
        
        assert manager.can_post_today() is True
        
        session.close()
