"""
State management with idempotency and cooldowns.

Implements Story 7: State Manager
- Draft queue management
- Duplicate prevention
- Cooldown logic for failed items
- Daily volume tracking
- Secure approval token generation and validation
"""
import hashlib
import secrets
from datetime import datetime, date, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from models.database import DraftQueue, RepliedItem, DailyStats
from utils.logging import get_logger
from config import Settings

logger = get_logger(__name__)
settings = Settings()

# Token configuration
TOKEN_TTL_HOURS = 48  # Tokens expire after 48 hours

# Allowed status transitions (state machine)
ALLOWED_TRANSITIONS = {
    "PENDING": {"APPROVED", "REJECTED"},
    "APPROVED": {"PUBLISHED"},
    "REJECTED": set(),  # Terminal state
    "PUBLISHED": set(),  # Terminal state
}


def _hash_token(token: str) -> str:
    """Hash a token using SHA-256 for secure storage."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


class StateManager:
    """
    Manage agent state with idempotency guarantees.
    
    Features:
    - Draft queue CRUD operations
    - Idempotent draft insertion (skip duplicates)
    - Cooldown logic for failed items
    - Daily volume limit tracking
    - Secure token-based approval with hashing and expiration
    """
    
    def __init__(
        self,
        session: Session,
        cooldown_hours: int = 24,
        max_daily: int = 8,
        inbox_cooldown_hours: int = 6
    ):
        """
        Initialize state manager.

        Args:
            session: SQLAlchemy session
            cooldown_hours: Hours to wait before retrying failed rising items
            max_daily: Maximum comments per day
            inbox_cooldown_hours: Hours to wait before retrying failed inbox items (Phase A)
        """
        self._session = session
        self._cooldown_hours = cooldown_hours
        self._inbox_cooldown_hours = inbox_cooldown_hours
        self._max_daily = max_daily

        logger.debug(
            "state_manager_initialized",
            cooldown_hours=cooldown_hours,
            inbox_cooldown_hours=inbox_cooldown_hours,
            max_daily=max_daily
        )
    
    # ========================================
    # Draft Queue Operations
    # ========================================
    
    def save_draft(
        self,
        draft_id: str,
        reddit_id: str,
        subreddit: str,
        content: str,
        context_url: str,
        status: str = "PENDING",
        candidate_type: str = "comment",
        quality_score: float = 0.0
    ) -> Optional[str]:
        """
        Save a draft to the queue.

        Idempotent: if reddit_id already exists, skip gracefully.

        Args:
            draft_id: Unique draft identifier
            reddit_id: Reddit item ID being replied to
            subreddit: Subreddit name
            content: Draft content
            context_url: URL to the thread
            status: Initial status (default PENDING)
            candidate_type: "post" or "comment" (Phase 2)
            quality_score: Quality score at selection time (Phase 2)

        Returns:
            Approval token (plaintext) if saved, None if duplicate
        """
        try:
            # Generate secure token and store its hash
            approval_token = secrets.token_urlsafe(32)
            token_hash = _hash_token(approval_token)

            # Build approval URLs for dashboard display
            base_url = settings.public_url.rstrip('/')
            approve_url = f"{base_url}/approve?token={approval_token}&action=approve"
            reject_url = f"{base_url}/approve?token={approval_token}&action=reject"

            draft = DraftQueue(
                draft_id=draft_id,
                reddit_id=reddit_id,
                subreddit=subreddit,
                content=content,
                context_url=context_url,
                status=status,
                created_at=datetime.utcnow(),
                approval_token_hash=token_hash,
                approve_url=approve_url,
                reject_url=reject_url,
                candidate_type=candidate_type,
                quality_score=quality_score
            )
            self._session.add(draft)
            self._session.commit()

            logger.info(
                "draft_saved",
                draft_id=draft_id,
                reddit_id=reddit_id,
                subreddit=subreddit,
                candidate_type=candidate_type,
                quality_score=round(quality_score, 3)
            )
            return approval_token

        except IntegrityError:
            # Duplicate reddit_id - skip gracefully
            self._session.rollback()
            logger.debug(
                "draft_duplicate_skipped",
                reddit_id=reddit_id
            )
            return None
    
    def update_draft_status(self, draft_id: str, status: str) -> bool:
        """
        Update draft status with state machine validation.
        
        Args:
            draft_id: Draft to update
            status: New status (PENDING, APPROVED, REJECTED, PUBLISHED)
            
        Returns:
            True if updated, False if not found or invalid transition
        """
        draft = self._session.query(DraftQueue).filter_by(
            draft_id=draft_id
        ).first()
        
        if not draft:
            logger.warning("draft_not_found", draft_id=draft_id)
            return False
        
        old_status = draft.status
        
        # Validate state transition
        allowed = ALLOWED_TRANSITIONS.get(old_status, set())
        if status not in allowed:
            logger.warning(
                "invalid_status_transition",
                draft_id=draft_id,
                from_status=old_status,
                to_status=status
            )
            return False
        
        draft.status = status
        
        if status == "APPROVED":
            draft.approved_at = datetime.utcnow()
        
        # Invalidate token after approval/rejection (one-time use)
        if status in ("APPROVED", "REJECTED"):
            draft.approval_token_hash = None
        
        self._session.commit()
        
        logger.info(
            "draft_status_updated",
            draft_id=draft_id,
            old_status=old_status,
            new_status=status
        )
        return True
    
    def get_pending_drafts(self, limit: int = 10):
        """Get drafts pending approval."""
        return self._session.query(DraftQueue).filter_by(
            status="PENDING"
        ).order_by(DraftQueue.created_at).limit(limit).all()
    
    def get_approved_drafts(self, limit: int = 10):
        """Get approved drafts ready for publishing."""
        return self._session.query(DraftQueue).filter_by(
            status="APPROVED"
        ).order_by(DraftQueue.approved_at).limit(limit).all()
    
    def get_draft_by_id(self, draft_id: str) -> Optional[DraftQueue]:
        """Get a specific draft by ID."""
        return self._session.query(DraftQueue).filter_by(
            draft_id=draft_id
        ).first()
    
    def get_draft_by_token(self, token: str) -> Optional[DraftQueue]:
        """
        Get a draft by approval token with expiration check.
        
        Token must be valid, not expired, and draft must be PENDING.
        
        Args:
            token: Plaintext approval token
            
        Returns:
            Draft if valid and not expired, None otherwise
        """
        if not token or len(token) < 20:
            return None
        
        token_hash = _hash_token(token)
        cutoff = datetime.utcnow() - timedelta(hours=TOKEN_TTL_HOURS)
        
        return self._session.query(DraftQueue).filter(
            DraftQueue.approval_token_hash == token_hash,
            DraftQueue.created_at >= cutoff,
            DraftQueue.status == "PENDING"
        ).first()
    
    # ========================================
    # Replied Items Tracking
    # ========================================
    
    def mark_replied(
        self,
        reddit_id: str,
        subreddit: str,
        status: str = "SUCCESS",
        candidate_type: str = "comment"
    ) -> None:
        """
        Mark an item as replied to.

        Args:
            reddit_id: Reddit item ID
            subreddit: Subreddit name
            status: Result status (SUCCESS, FAILED, SKIPPED)
            candidate_type: "post" or "comment" (Phase A)
        """
        existing = self._session.query(RepliedItem).filter_by(
            reddit_id=reddit_id
        ).first()

        if existing:
            existing.status = status
            existing.last_attempt = datetime.utcnow()
            existing.candidate_type = candidate_type
        else:
            item = RepliedItem(
                reddit_id=reddit_id,
                subreddit=subreddit,
                status=status,
                last_attempt=datetime.utcnow(),
                candidate_type=candidate_type
            )
            self._session.add(item)

        self._session.commit()

        logger.info(
            "item_marked_replied",
            reddit_id=reddit_id,
            status=status,
            candidate_type=candidate_type
        )
    
    def has_replied(self, reddit_id: str) -> bool:
        """Check if we've already replied to an item."""
        item = self._session.query(RepliedItem).filter_by(
            reddit_id=reddit_id
        ).first()
        
        return item is not None and item.status == "SUCCESS"
    
    def is_retryable(self, reddit_id: str) -> bool:
        """
        Check if a failed item can be retried.

        Rules:
        - SUCCESS items are never retried
        - FAILED items can be retried after cooldown (inbox: 6h, rising: 24h)
        - Unknown items are retryable (first attempt)

        Args:
            reddit_id: Reddit item ID

        Returns:
            True if item can be processed
        """
        item = self._session.query(RepliedItem).filter_by(
            reddit_id=reddit_id
        ).first()

        if not item:
            # First attempt
            return True

        if item.status == "SUCCESS":
            # Never retry success
            return False

        if item.status == "SKIPPED":
            # Skipped items are not retried
            return False

        # FAILED - check cooldown (Phase A: separate cooldown for inbox)
        # Determine cooldown period based on candidate_type
        if item.candidate_type == "comment" and hasattr(item, 'priority'):
            # Check if it's an inbox item (HIGH priority)
            # For now, we use inbox_cooldown for all comments
            # TODO: Store priority in RepliedItem for more accurate detection
            cooldown_hours = self._inbox_cooldown_hours
        else:
            cooldown_hours = self._cooldown_hours

        cooldown_end = item.last_attempt + timedelta(hours=cooldown_hours)
        if datetime.utcnow() < cooldown_end:
            # Still in cooldown
            return False

        return True
    
    # ========================================
    # Daily Volume Limits
    # ========================================
    
    def get_daily_count(self) -> int:
        """Get today's comment count."""
        today = date.today()
        stats = self._session.query(DailyStats).filter_by(
            date=today
        ).first()
        
        return stats.comment_count if stats else 0
    
    def increment_daily_count(self) -> int:
        """
        Increment today's comment count.
        
        Returns:
            New count
        """
        today = date.today()
        stats = self._session.query(DailyStats).filter_by(
            date=today
        ).first()
        
        if stats:
            stats.comment_count += 1
        else:
            stats = DailyStats(date=today, comment_count=1)
            self._session.add(stats)
        
        self._session.commit()
        
        logger.info("daily_count_incremented", count=stats.comment_count)
        return stats.comment_count
    
    def can_post_today(self) -> bool:
        """Check if we're under the daily limit."""
        count = self.get_daily_count()
        can_post = count < self._max_daily

        if not can_post:
            logger.warning(
                "daily_limit_reached",
                count=count,
                max=self._max_daily
            )

        return can_post

    # ========================================
    # Performance Tracking (Phase 2)
    # ========================================

    def record_performance_outcome(
        self,
        draft_id: str,
        subreddit: str,
        candidate_type: str,
        quality_score: float,
        outcome: str
    ) -> None:
        """
        Record performance outcome for a draft.

        Creates or updates performance_history record.

        Args:
            draft_id: Draft identifier
            subreddit: Subreddit name
            candidate_type: "post" or "comment"
            quality_score: Quality score at selection time
            outcome: PENDING, APPROVED, REJECTED, PUBLISHED
        """
        from models.database import PerformanceHistory

        # Check if record exists
        existing = self._session.query(PerformanceHistory).filter_by(
            draft_id=draft_id
        ).first()

        if existing:
            # Update existing record
            existing.outcome = outcome
            existing.outcome_at = datetime.utcnow()
        else:
            # Create new record
            record = PerformanceHistory(
                draft_id=draft_id,
                subreddit=subreddit,
                candidate_type=candidate_type,
                quality_score=quality_score,
                outcome=outcome,
                created_at=datetime.utcnow(),
                outcome_at=datetime.utcnow() if outcome != "PENDING" else None
            )
            self._session.add(record)

        self._session.commit()

        logger.info(
            "performance_outcome_recorded",
            draft_id=draft_id,
            outcome=outcome
        )

    def update_engagement_metrics(
        self,
        draft_id: str,
        upvotes: int,
        replies: int
    ) -> None:
        """
        Update engagement metrics for a published draft.

        Args:
            draft_id: Draft identifier
            upvotes: Upvote count after 24h
            replies: Reply count after 24h
        """
        from models.database import PerformanceHistory
        import math

        record = self._session.query(PerformanceHistory).filter_by(
            draft_id=draft_id
        ).first()

        if not record:
            logger.warning("performance_record_not_found", draft_id=draft_id)
            return

        # Calculate engagement score: log(upvotes + 1) + (replies * 2)
        engagement_score = math.log(upvotes + 1) + (replies * 2)

        record.upvotes_24h = upvotes
        record.replies_24h = replies
        record.engagement_score = engagement_score

        self._session.commit()

        logger.info(
            "engagement_metrics_updated",
            draft_id=draft_id,
            upvotes=upvotes,
            replies=replies,
            engagement_score=round(engagement_score, 2)
        )

    def mark_engagement_checked(self, comment_id: str) -> None:
        """Mark a draft as engagement-checked."""
        draft = self._session.query(DraftQueue).filter_by(
            comment_id=comment_id
        ).first()

        if draft:
            draft.engagement_checked = True
            self._session.commit()
            logger.info("engagement_marked_checked", comment_id=comment_id)
