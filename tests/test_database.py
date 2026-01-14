"""
Test database schema and migrations (Story 0).
"""
import pytest
from datetime import datetime, date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Import models directly without triggering config loading
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from models.database import Base, RepliedItem, DraftQueue, ErrorLog, SubredditRulesCache, DailyStats


@pytest.fixture
def db_session():
    """Create a test database session."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_tables_created(db_session):
    """Test that all tables are created."""
    # Check that we can query each table
    assert db_session.query(RepliedItem).count() == 0
    assert db_session.query(DraftQueue).count() == 0
    assert db_session.query(ErrorLog).count() == 0
    assert db_session.query(SubredditRulesCache).count() == 0
    assert db_session.query(DailyStats).count() == 0


def test_replied_item_creation(db_session):
    """Test creating a replied item."""
    item = RepliedItem(
        reddit_id="abc123",
        subreddit="sysadmin",
        status="SUCCESS",
        last_attempt=datetime.utcnow()
    )
    db_session.add(item)
    db_session.commit()
    
    result = db_session.query(RepliedItem).filter_by(reddit_id="abc123").first()
    assert result is not None
    assert result.subreddit == "sysadmin"
    assert result.status == "SUCCESS"


def test_draft_queue_unique_reddit_id(db_session):
    """Test that draft queue enforces unique reddit_id."""
    from sqlalchemy.exc import IntegrityError
    
    draft1 = DraftQueue(
        draft_id="draft1",
        reddit_id="comment123",
        subreddit="test",
        content="Test content",
        context_url="https://reddit.com/test"
    )
    db_session.add(draft1)
    db_session.commit()
    
    # Try to add another draft with same reddit_id
    draft2 = DraftQueue(
        draft_id="draft2",
        reddit_id="comment123",  # Same reddit_id
        subreddit="test",
        content="Different content",
        context_url="https://reddit.com/test2"
    )
    db_session.add(draft2)
    
    with pytest.raises(IntegrityError):
        db_session.commit()


def test_error_log_creation(db_session):
    """Test creating an error log entry."""
    error = ErrorLog(
        reddit_id="abc123",
        error_type="403",
        message="Forbidden error",
        timestamp=datetime.utcnow()
    )
    db_session.add(error)
    db_session.commit()
    
    result = db_session.query(ErrorLog).filter_by(reddit_id="abc123").first()
    assert result is not None
    assert result.error_type == "403"


def test_subreddit_rules_cache(db_session):
    """Test subreddit rules cache."""
    cache = SubredditRulesCache(
        subreddit="test",
        rules='{"no_bots": true}',
        status="RESTRICTED",
        last_updated=datetime.utcnow()
    )
    db_session.add(cache)
    db_session.commit()
    
    result = db_session.query(SubredditRulesCache).filter_by(subreddit="test").first()
    assert result is not None
    assert result.status == "RESTRICTED"


def test_daily_stats(db_session):
    """Test daily stats tracking."""
    stats = DailyStats(
        date=date.today(),
        comment_count=5
    )
    db_session.add(stats)
    db_session.commit()
    
    result = db_session.query(DailyStats).filter_by(date=date.today()).first()
    assert result is not None
    assert result.comment_count == 5
