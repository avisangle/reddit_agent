"""
Engagement tracking service for published comments.

Fetches upvotes and replies from Reddit 24 hours after publishing
to measure comment performance and feed into historical learning.
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from sqlalchemy.orm import Session

from utils.logging import get_logger

logger = get_logger(__name__)


class EngagementChecker:
    """
    Background job to check engagement metrics for published comments.

    Features:
    - Queries published drafts after 24h delay
    - Fetches upvotes and replies from Reddit
    - Updates engagement metrics in performance_history
    - Marks drafts as engagement_checked
    - Handles deleted/removed comments gracefully
    """

    def __init__(
        self,
        session: Session,
        reddit_client: any,
        state_manager: any,
        settings: any
    ):
        """
        Initialize engagement checker.

        Args:
            session: SQLAlchemy session
            reddit_client: RedditClient instance
            state_manager: StateManager instance
            settings: Application settings
        """
        self._session = session
        self._reddit_client = reddit_client
        self._state_manager = state_manager
        self._settings = settings

        logger.info("engagement_checker_initialized")

    def check_pending_engagements(self, limit: int = 20) -> Dict[str, int]:
        """
        Check engagement metrics for published drafts after 24h.

        Queries drafts that are:
        - Published
        - Not yet engagement-checked
        - Published > 24h ago
        - Have a comment_id

        Args:
            limit: Maximum drafts to check in this run

        Returns:
            Dict with counts: {checked, success, failed, skipped}
        """
        if not self._settings.engagement_check_enabled:
            logger.info("engagement_check_disabled")
            return {"checked": 0, "success": 0, "failed": 0, "skipped": 0}

        from models.database import DraftQueue

        # Calculate cutoff time (24h ago)
        delay_hours = getattr(self._settings, 'engagement_check_delay_hours', 24)
        cutoff_time = datetime.utcnow() - timedelta(hours=delay_hours)

        # Query drafts ready for engagement check
        drafts = self._session.query(DraftQueue).filter(
            DraftQueue.status == "PUBLISHED",
            DraftQueue.engagement_checked == False,
            DraftQueue.published_at < cutoff_time,
            DraftQueue.comment_id.isnot(None)
        ).limit(limit).all()

        if not drafts:
            logger.info("no_drafts_to_check")
            return {"checked": 0, "success": 0, "failed": 0, "skipped": 0}

        logger.info("checking_engagements", count=len(drafts))

        results = {
            "checked": len(drafts),
            "success": 0,
            "failed": 0,
            "skipped": 0
        }

        for draft in drafts:
            try:
                success = self._check_single_draft(draft)
                if success:
                    results["success"] += 1
                else:
                    results["failed"] += 1
            except Exception as e:
                logger.error(
                    "engagement_check_error",
                    draft_id=draft.draft_id,
                    comment_id=draft.comment_id,
                    error=str(e)
                )
                results["failed"] += 1

        logger.info(
            "engagement_check_complete",
            checked=results["checked"],
            success=results["success"],
            failed=results["failed"]
        )

        return results

    def _check_single_draft(self, draft) -> bool:
        """
        Check engagement metrics for a single draft.

        Fetches comment from Reddit, extracts upvotes and replies,
        updates performance_history, and marks as checked.

        Args:
            draft: DraftQueue object

        Returns:
            True if successful, False otherwise
        """
        comment_id = draft.comment_id

        try:
            # Fetch comment from Reddit
            comment = self._reddit_client.reddit.comment(id=comment_id)
            comment.refresh()

            # Extract metrics
            upvotes = comment.score
            replies = len(comment.replies)

            logger.info(
                "engagement_fetched",
                draft_id=draft.draft_id,
                comment_id=comment_id,
                upvotes=upvotes,
                replies=replies
            )

            # Update engagement metrics in performance_history
            self._state_manager.update_engagement_metrics(
                draft_id=draft.draft_id,
                upvotes=upvotes,
                replies=replies
            )

            # Mark as checked
            self._state_manager.mark_engagement_checked(comment_id)

            return True

        except AttributeError as e:
            # Comment may be deleted/removed
            logger.warning(
                "comment_deleted_or_removed",
                draft_id=draft.draft_id,
                comment_id=comment_id,
                error=str(e)
            )

            # Mark as checked anyway (can't get metrics for deleted comment)
            self._state_manager.mark_engagement_checked(comment_id)

            return False

        except Exception as e:
            logger.error(
                "engagement_fetch_failed",
                draft_id=draft.draft_id,
                comment_id=comment_id,
                error=str(e)
            )
            return False
