"""
SQLAlchemy database models and session management.
"""
from datetime import datetime
from typing import Optional, Generator
from sqlalchemy import (
    create_engine, 
    Column, 
    String, 
    Integer, 
    DateTime, 
    Date,
    Text,
    Engine
)
from sqlalchemy.orm import declarative_base, sessionmaker, Session

# Base class for models
Base = declarative_base()


class RepliedItem(Base):
    """Track items that have been replied to."""
    __tablename__ = "replied_items"
    
    reddit_id = Column(String, primary_key=True, index=True)
    subreddit = Column(String, nullable=False, index=True)
    status = Column(String, nullable=False)  # SUCCESS, SKIPPED, BANNED, FAILED
    last_attempt = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<RepliedItem(reddit_id='{self.reddit_id}', status='{self.status}')>"


class DraftQueue(Base):
    """Queue of drafts awaiting approval."""
    __tablename__ = "draft_queue"
    
    draft_id = Column(String, primary_key=True, index=True)
    reddit_id = Column(String, nullable=False, unique=True, index=True)  # Prevent duplicates
    subreddit = Column(String, nullable=False, index=True)
    content = Column(Text, nullable=False)
    context_url = Column(String, nullable=False)
    status = Column(String, nullable=False, default="PENDING")  # PENDING, APPROVED, REJECTED, PUBLISHED
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    approved_at = Column(DateTime, nullable=True)
    approval_token_hash = Column(String, nullable=True, index=True)  # SHA-256 hash of approval token
    
    def __repr__(self):
        return f"<DraftQueue(draft_id='{self.draft_id}', status='{self.status}')>"


class ErrorLog(Base):
    """Log of errors encountered."""
    __tablename__ = "error_log"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    reddit_id = Column(String, nullable=False, index=True)
    error_type = Column(String, nullable=False)  # 403, 429, SHADOWBAN_SUSPECTED, etc.
    message = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    def __repr__(self):
        return f"<ErrorLog(id={self.id}, error_type='{self.error_type}')>"


class SubredditRulesCache(Base):
    """Cache of subreddit rules and compliance status."""
    __tablename__ = "subreddit_rules_cache"
    
    subreddit = Column(String, primary_key=True, index=True)
    rules = Column(Text, nullable=True)  # JSON or plain text
    status = Column(String, nullable=False, default="ALLOWED")  # ALLOWED, RESTRICTED
    last_updated = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<SubredditRulesCache(subreddit='{self.subreddit}', status='{self.status}')>"


class DailyStats(Base):
    """Track daily comment counts for volume limits."""
    __tablename__ = "daily_stats"
    
    date = Column(Date, primary_key=True, index=True)
    comment_count = Column(Integer, nullable=False, default=0)
    
    def __repr__(self):
        return f"<DailyStats(date={self.date}, count={self.comment_count})>"


# Lazy database initialization
_engine: Optional[Engine] = None
_SessionLocal: Optional[sessionmaker] = None


def get_engine(database_url: Optional[str] = None) -> Engine:
    """Get or create database engine (lazy initialization)."""
    global _engine
    
    if _engine is None:
        if database_url is None:
            from config import get_settings
            database_url = get_settings().database_url
        
        connect_args = {}
        if "sqlite" in database_url:
            connect_args["check_same_thread"] = False
        
        _engine = create_engine(
            database_url,
            connect_args=connect_args,
            echo=False
        )
    
    return _engine


def get_session_local(database_url: Optional[str] = None) -> sessionmaker:
    """Get or create session factory (lazy initialization)."""
    global _SessionLocal
    
    if _SessionLocal is None:
        engine = get_engine(database_url)
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    return _SessionLocal


# Legacy compatibility
@property
def engine() -> Engine:
    """Legacy engine property for backwards compatibility."""
    return get_engine()


@property  
def SessionLocal() -> sessionmaker:
    """Legacy SessionLocal property for backwards compatibility."""
    return get_session_local()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency for database sessions.
    
    Yields:
        SQLAlchemy session
    """
    SessionLocal = get_session_local()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db(database_url: Optional[str] = None) -> None:
    """Initialize database tables."""
    engine = get_engine(database_url)
    Base.metadata.create_all(bind=engine)

