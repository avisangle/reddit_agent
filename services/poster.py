"""
Comment poster service for publishing approved drafts.

Implements the poster job that:
- Fetches approved drafts from the queue
- Posts them to Reddit
- Updates status to PUBLISHED
- Respects daily limits and applies jitter
"""
import time
import random
from datetime import datetime
from typing import List, Optional
from dataclasses import dataclass

from utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class PublishResult:
    """Result of a publish operation."""
    draft_id: str
    reddit_id: str
    comment_id: Optional[str]
    success: bool
    error: Optional[str] = None


class CommentPoster:
    """
    Publish approved drafts to Reddit.
    
    Features:
    - Fetch approved drafts from queue
    - Post to Reddit with safety checks
    - Apply jitter between posts
    - Respect daily volume limits
    - Update status to PUBLISHED
    """
    
    def __init__(
        self,
        reddit_client,
        state_manager,
        min_jitter: int = 30,
        max_jitter: int = 120,
        dry_run: bool = False
    ):
        """
        Initialize comment poster.
        
        Args:
            reddit_client: RedditClient instance
            state_manager: StateManager instance
            min_jitter: Minimum seconds between posts
            max_jitter: Maximum seconds between posts
            dry_run: If True, don't actually post
        """
        self._reddit_client = reddit_client
        self._state_manager = state_manager
        self._min_jitter = min_jitter
        self._max_jitter = max_jitter
        self._dry_run = dry_run
        
        logger.info(
            "poster_initialized",
            min_jitter=min_jitter,
            max_jitter=max_jitter,
            dry_run=dry_run
        )
    
    def _get_jitter(self) -> float:
        """Calculate random jitter delay."""
        return random.uniform(self._min_jitter, self._max_jitter)
    
    def _fetch_parent_comment(self, reddit_id: str):
        """
        Fetch the parent comment/submission to reply to.
        
        Args:
            reddit_id: Reddit ID (comment or submission ID)
            
        Returns:
            PRAW Comment or Submission object
        """
        try:
            # Try as comment first (t1_ prefix)
            if reddit_id.startswith("t1_"):
                return self._reddit_client.reddit.comment(reddit_id.replace("t1_", ""))
            elif reddit_id.startswith("t3_"):
                return self._reddit_client.reddit.submission(reddit_id.replace("t3_", ""))
            else:
                # Assume it's a comment ID without prefix
                return self._reddit_client.reddit.comment(reddit_id)
        except Exception as e:
            logger.error("fetch_parent_failed", reddit_id=reddit_id, error=str(e))
            raise
    
    def publish_single(self, draft) -> PublishResult:
        """
        Publish a single draft.
        
        Args:
            draft: DraftQueue object
            
        Returns:
            PublishResult with outcome
        """
        try:
            # Check daily limit first
            if not self._state_manager.can_post_today():
                logger.warning(
                    "publish_blocked_daily_limit",
                    draft_id=draft.draft_id
                )
                return PublishResult(
                    draft_id=draft.draft_id,
                    reddit_id=draft.reddit_id,
                    comment_id=None,
                    success=False,
                    error="Daily limit reached"
                )
            
            # Fetch parent to reply to
            parent = self._fetch_parent_comment(draft.reddit_id)
            
            # Post the comment
            comment_id = self._reddit_client.post_comment(
                parent=parent,
                body=draft.content,
                dry_run=self._dry_run
            )

            # Update status
            self._state_manager.update_draft_status(draft.draft_id, "PUBLISHED")

            # Phase 2: Update draft with comment_id and published_at
            if not self._dry_run:
                try:
                    # Access the draft object from the database and update it
                    session = self._state_manager._session
                    from models.database import DraftQueue
                    db_draft = session.query(DraftQueue).filter_by(
                        draft_id=draft.draft_id
                    ).first()

                    if db_draft:
                        db_draft.comment_id = comment_id
                        db_draft.published_at = datetime.utcnow()
                        session.commit()

                        # Record PUBLISHED outcome in performance_history
                        self._state_manager.record_performance_outcome(
                            draft_id=draft.draft_id,
                            subreddit=db_draft.subreddit,
                            candidate_type=db_draft.candidate_type or "comment",
                            quality_score=db_draft.quality_score or 0.0,
                            outcome="PUBLISHED"
                        )
                except Exception as e:
                    # Don't fail publish if performance tracking fails
                    logger.warning(
                        "performance_tracking_failed",
                        draft_id=draft.draft_id,
                        error=str(e)
                    )

            self._state_manager.mark_replied(draft.reddit_id, draft.subreddit, "SUCCESS")

            if not self._dry_run:
                self._state_manager.increment_daily_count()
            
            logger.info(
                "draft_published",
                draft_id=draft.draft_id,
                reddit_id=draft.reddit_id,
                comment_id=comment_id,
                dry_run=self._dry_run
            )
            
            return PublishResult(
                draft_id=draft.draft_id,
                reddit_id=draft.reddit_id,
                comment_id=comment_id,
                success=True
            )
            
        except Exception as e:
            error_str = str(e)
            logger.error(
                "publish_failed",
                draft_id=draft.draft_id,
                error=error_str
            )
            
            # Mark as failed for cooldown
            self._state_manager.mark_replied(
                draft.reddit_id,
                draft.subreddit,
                "FAILED"
            )
            
            return PublishResult(
                draft_id=draft.draft_id,
                reddit_id=draft.reddit_id,
                comment_id=None,
                success=False,
                error=error_str
            )
    
    def publish_approved(self, limit: int = 3) -> List[PublishResult]:
        """
        Publish all approved drafts up to limit.
        
        Args:
            limit: Maximum drafts to publish in this run
            
        Returns:
            List of PublishResult objects
        """
        results = []
        
        # Get approved drafts
        drafts = self._state_manager.get_approved_drafts(limit=limit)
        
        if not drafts:
            logger.info("no_approved_drafts")
            return results
        
        logger.info("publishing_drafts", count=len(drafts))
        
        for i, draft in enumerate(drafts):
            # Check daily limit
            if not self._state_manager.can_post_today():
                logger.warning("daily_limit_reached_during_publish")
                break
            
            # Publish
            result = self.publish_single(draft)
            results.append(result)
            
            # Apply jitter between posts (not after last one)
            if i < len(drafts) - 1 and result.success and not self._dry_run:
                jitter = self._get_jitter()
                logger.info("applying_jitter", seconds=jitter)
                time.sleep(jitter)
        
        # Summary
        success_count = sum(1 for r in results if r.success)
        logger.info(
            "publish_complete",
            total=len(results),
            success=success_count,
            failed=len(results) - success_count
        )
        
        return results
