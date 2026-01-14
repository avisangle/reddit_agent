"""
Pydantic schemas for data validation.
"""
from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field


class ItemStatus(str, Enum):
    """Status for replied items."""
    SUCCESS = "SUCCESS"
    SKIPPED = "SKIPPED"
    BANNED = "BANNED"
    FAILED = "FAILED"


class DraftStatus(str, Enum):
    """Status for draft queue."""
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    PUBLISHED = "PUBLISHED"


class ErrorType(str, Enum):
    """Types of errors."""
    HTTP_403 = "403"
    HTTP_429 = "429"
    SHADOWBAN_SUSPECTED = "SHADOWBAN_SUSPECTED"
    RULE_VIOLATION = "RULE_VIOLATION"
    CONTENT_FILTER = "CONTENT_FILTER"
    API_ERROR = "API_ERROR"


class SubredditStatus(str, Enum):
    """Status for subreddit rules cache."""
    ALLOWED = "ALLOWED"
    RESTRICTED = "RESTRICTED"


# Request/Response schemas

class DraftCreate(BaseModel):
    """Schema for creating a draft."""
    reddit_id: str
    subreddit: str
    content: str
    context_url: str


class DraftResponse(BaseModel):
    """Schema for draft response."""
    draft_id: str
    reddit_id: str
    subreddit: str
    content: str
    context_url: str
    status: DraftStatus
    created_at: datetime
    approved_at: datetime | None = None
    
    class Config:
        from_attributes = True


class WebhookPayload(BaseModel):
    """Schema for webhook notification payload."""
    draft_id: str
    subreddit: str
    content: str
    thread_url: str
    timestamp: datetime


class CallbackRequest(BaseModel):
    """Schema for approval callback."""
    action: str = Field(..., pattern="^(approve|reject)$")
    draft_id: str
    signature: str | None = None


class ErrorLogCreate(BaseModel):
    """Schema for creating error log."""
    reddit_id: str
    error_type: ErrorType
    message: str
