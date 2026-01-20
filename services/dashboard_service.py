"""
Dashboard service for aggregating admin dashboard data.

Provides performance metrics, status counts, and recent activity data
with caching for expensive queries.
"""
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from functools import lru_cache
import time

from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from models.database import (
    DraftQueue,
    DailyStats,
    PerformanceHistory,
    AdminAuditLog,
    get_session_local
)
from utils.logging import get_logger

logger = get_logger(__name__)

# Cache TTL in seconds
CACHE_TTL = 30


class DashboardService:
    """Service for dashboard data aggregation with caching."""

    def __init__(self):
        """Initialize dashboard service."""
        self._cache_timestamp = 0
        self._cached_stats = None

    def _is_cache_valid(self) -> bool:
        """Check if cache is still valid."""
        return (time.time() - self._cache_timestamp) < CACHE_TTL

    def get_status_counts(self, session: Optional[Session] = None) -> Dict[str, int]:
        """
        Get draft counts by status.

        Args:
            session: Database session (creates new one if not provided)

        Returns:
            Dictionary with status counts (PENDING, APPROVED, PUBLISHED, REJECTED)
        """
        should_close = False
        if session is None:
            SessionLocal = get_session_local()
            session = SessionLocal()
            should_close = True

        try:
            # Query counts grouped by status
            counts = session.query(
                DraftQueue.status,
                func.count(DraftQueue.draft_id)
            ).group_by(DraftQueue.status).all()

            # Convert to dictionary
            status_dict = {status: count for status, count in counts}

            # Ensure all statuses are present
            return {
                "PENDING": status_dict.get("PENDING", 0),
                "APPROVED": status_dict.get("APPROVED", 0),
                "PUBLISHED": status_dict.get("PUBLISHED", 0),
                "REJECTED": status_dict.get("REJECTED", 0)
            }
        finally:
            if should_close:
                session.close()

    def get_daily_count(self, session: Optional[Session] = None) -> Dict[str, Any]:
        """
        Get today's comment count and daily limit.

        Args:
            session: Database session (creates new one if not provided)

        Returns:
            Dictionary with count and limit
        """
        should_close = False
        if session is None:
            SessionLocal = get_session_local()
            session = SessionLocal()
            should_close = True

        try:
            today = datetime.utcnow().date()

            # Get today's count
            today_stat = session.query(DailyStats).filter(
                DailyStats.date == today
            ).first()

            count = today_stat.comment_count if today_stat else 0

            # Get limit from config
            from config import get_settings
            limit = get_settings().max_comments_per_day

            return {
                "count": count,
                "limit": limit,
                "percentage": round((count / limit) * 100) if limit > 0 else 0
            }
        finally:
            if should_close:
                session.close()

    def get_performance_metrics(self, days: int = 7, session: Optional[Session] = None) -> Dict[str, float]:
        """
        Get performance metrics over the last N days.

        Args:
            days: Number of days to look back
            session: Database session (creates new one if not provided)

        Returns:
            Dictionary with approval_rate, publish_rate, avg_engagement
        """
        should_close = False
        if session is None:
            SessionLocal = get_session_local()
            session = SessionLocal()
            should_close = True

        try:
            cutoff = datetime.utcnow() - timedelta(days=days)

            # Get performance history
            histories = session.query(PerformanceHistory).filter(
                PerformanceHistory.created_at >= cutoff
            ).all()

            if not histories:
                return {
                    "approval_rate": 0.0,
                    "publish_rate": 0.0,
                    "avg_engagement": 0.0
                }

            # Calculate rates
            total = len(histories)
            approved = sum(1 for h in histories if h.outcome in ["APPROVED", "PUBLISHED"])
            published = sum(1 for h in histories if h.outcome == "PUBLISHED")

            # Calculate average engagement (for published items)
            engagement_scores = [h.engagement_score for h in histories if h.engagement_score is not None]
            avg_engagement = sum(engagement_scores) / len(engagement_scores) if engagement_scores else 0.0

            return {
                "approval_rate": round((approved / total) * 100, 1) if total > 0 else 0.0,
                "publish_rate": round((published / total) * 100, 1) if total > 0 else 0.0,
                "avg_engagement": round(avg_engagement, 2)
            }
        finally:
            if should_close:
                session.close()

    def get_weekly_trend(self, session: Optional[Session] = None) -> List[Dict[str, Any]]:
        """
        Get 7-day comment count trend.

        Args:
            session: Database session (creates new one if not provided)

        Returns:
            List of dictionaries with date and count
        """
        should_close = False
        if session is None:
            SessionLocal = get_session_local()
            session = SessionLocal()
            should_close = True

        try:
            # Get last 7 days of stats
            cutoff_date = datetime.utcnow().date() - timedelta(days=6)

            stats = session.query(DailyStats).filter(
                DailyStats.date >= cutoff_date
            ).order_by(DailyStats.date).all()

            # Create result list with all 7 days (fill missing with 0)
            result = []
            for i in range(7):
                date = datetime.utcnow().date() - timedelta(days=6 - i)
                count = next((s.comment_count for s in stats if s.date == date), 0)
                result.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "count": count
                })

            return result
        finally:
            if should_close:
                session.close()

    def get_subreddit_distribution(self, limit: int = 10, session: Optional[Session] = None) -> List[Dict[str, Any]]:
        """
        Get draft distribution by subreddit (last 7 days).

        Args:
            limit: Maximum number of subreddits to return
            session: Database session (creates new one if not provided)

        Returns:
            List of dictionaries with subreddit and count
        """
        should_close = False
        if session is None:
            SessionLocal = get_session_local()
            session = SessionLocal()
            should_close = True

        try:
            cutoff = datetime.utcnow() - timedelta(days=7)

            # Query subreddit counts
            counts = session.query(
                DraftQueue.subreddit,
                func.count(DraftQueue.draft_id).label('count')
            ).filter(
                DraftQueue.created_at >= cutoff
            ).group_by(
                DraftQueue.subreddit
            ).order_by(
                desc('count')
            ).limit(limit).all()

            return [
                {"subreddit": subreddit, "count": count}
                for subreddit, count in counts
            ]
        finally:
            if should_close:
                session.close()

    def get_recent_drafts(self, limit: int = 10, session: Optional[Session] = None) -> List[DraftQueue]:
        """
        Get recent drafts.

        Args:
            limit: Maximum number of drafts to return
            session: Database session (creates new one if not provided)

        Returns:
            List of DraftQueue objects
        """
        should_close = False
        if session is None:
            SessionLocal = get_session_local()
            session = SessionLocal()
            should_close = True

        try:
            drafts = session.query(DraftQueue).order_by(
                desc(DraftQueue.created_at)
            ).limit(limit).all()

            return drafts
        finally:
            if should_close:
                session.close()

    def get_realtime_stats(self, session: Optional[Session] = None) -> Dict[str, Any]:
        """
        Get real-time stats for HTMX polling.

        Args:
            session: Database session (creates new one if not provided)

        Returns:
            Dictionary with pending count and last update time
        """
        should_close = False
        if session is None:
            SessionLocal = get_session_local()
            session = SessionLocal()
            should_close = True

        try:
            pending_count = session.query(DraftQueue).filter(
                DraftQueue.status == "PENDING"
            ).count()

            return {
                "pending": pending_count,
                "last_update": datetime.utcnow().strftime("%H:%M:%S")
            }
        finally:
            if should_close:
                session.close()

    def get_dashboard_data(self, session: Optional[Session] = None) -> Dict[str, Any]:
        """
        Get all dashboard data in a single call (cached for 30 seconds).

        Args:
            session: Database session (creates new one if not provided)

        Returns:
            Dictionary with all dashboard metrics
        """
        # Return cached data if valid
        if self._is_cache_valid() and self._cached_stats:
            logger.debug("dashboard_cache_hit")
            return self._cached_stats

        should_close = False
        if session is None:
            SessionLocal = get_session_local()
            session = SessionLocal()
            should_close = True

        try:
            data = {
                "status_counts": self.get_status_counts(session),
                "daily_count": self.get_daily_count(session),
                "performance": self.get_performance_metrics(session=session),
                "weekly_trend": self.get_weekly_trend(session),
                "subreddit_distribution": self.get_subreddit_distribution(session=session),
                "recent_drafts": [
                    {
                        "draft_id": d.draft_id,
                        "subreddit": d.subreddit,
                        "status": d.status,
                        "quality_score": round(d.quality_score, 2) if d.quality_score else None,
                        "created_at": d.created_at.strftime("%Y-%m-%d %H:%M"),
                        "context_url": d.context_url,
                        "approve_url": d.approve_url if d.status == "PENDING" else None,
                        "reject_url": d.reject_url if d.status == "PENDING" else None
                    }
                    for d in self.get_recent_drafts(session=session)
                ]
            }

            # Update cache
            self._cached_stats = data
            self._cache_timestamp = time.time()

            logger.debug("dashboard_cache_updated")
            return data
        finally:
            if should_close:
                session.close()
