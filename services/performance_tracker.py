"""
Performance tracking and historical learning service.

Analyzes historical draft outcomes per subreddit to predict future success.
Implements decay-weighted scoring with minimum sample requirements.
"""
import math
from datetime import datetime, timedelta
from typing import Dict, Optional
from sqlalchemy.orm import Session

from utils.logging import get_logger

logger = get_logger(__name__)


class PerformanceTracker:
    """
    Track and analyze historical performance to improve candidate selection.

    Features:
    - Subreddit-specific performance scoring
    - Time-based decay weighting (recent > old)
    - Minimum sample size requirements
    - In-memory caching with TTL
    - Composite scoring from multiple signals
    """

    def __init__(
        self,
        session: Session,
        settings: any,
        cache_ttl_seconds: int = 300  # 5 minutes
    ):
        """
        Initialize performance tracker.

        Args:
            session: SQLAlchemy session
            settings: Application settings
            cache_ttl_seconds: Cache TTL in seconds
        """
        self._session = session
        self._settings = settings
        self._cache_ttl = timedelta(seconds=cache_ttl_seconds)

        # Cache: {subreddit: (score, timestamp)}
        self._score_cache: Dict[str, tuple[float, datetime]] = {}

        logger.info(
            "performance_tracker_initialized",
            cache_ttl_seconds=cache_ttl_seconds
        )

    def get_subreddit_score(self, subreddit: str) -> float:
        """
        Get historical performance score for a subreddit.

        Returns cached score if available and not expired.
        Otherwise calculates fresh score.

        Args:
            subreddit: Subreddit name

        Returns:
            Score between 0.0 and 1.0 (0.5 = neutral)
        """
        # Check cache
        if subreddit in self._score_cache:
            score, timestamp = self._score_cache[subreddit]
            age = datetime.utcnow() - timestamp

            if age < self._cache_ttl:
                logger.debug(
                    "subreddit_score_cached",
                    subreddit=subreddit,
                    score=round(score, 3),
                    cache_age_seconds=int(age.total_seconds())
                )
                return score

        # Calculate fresh score
        score = self._calculate_subreddit_score(subreddit)

        # Update cache
        self._score_cache[subreddit] = (score, datetime.utcnow())

        logger.info(
            "subreddit_score_calculated",
            subreddit=subreddit,
            score=round(score, 3)
        )

        return score

    def _calculate_subreddit_score(self, subreddit: str) -> float:
        """
        Calculate composite historical score for a subreddit.

        Combines 4 signals:
        - Approval rate (30%)
        - Publish rate (20%)
        - Engagement score (30%)
        - Success rate (20%)

        Requires minimum sample size, else returns neutral (0.5).

        Args:
            subreddit: Subreddit name

        Returns:
            Composite score 0.0-1.0
        """
        from models.database import PerformanceHistory

        min_samples = getattr(self._settings, 'learning_min_samples', 5)

        # Fetch all historical records for this subreddit
        records = self._session.query(PerformanceHistory).filter(
            PerformanceHistory.subreddit == subreddit
        ).all()

        if len(records) < min_samples:
            logger.debug(
                "insufficient_samples",
                subreddit=subreddit,
                count=len(records),
                required=min_samples
            )
            return 0.5  # Neutral score

        # Calculate component scores with decay weighting
        approval_rate = self._calculate_approval_rate(records)
        publish_rate = self._calculate_publish_rate(records)
        engagement_score = self._calculate_engagement_score(records)
        success_rate = self._calculate_success_rate(records)

        # Get weights from settings
        weight_approval = getattr(self._settings, 'learning_weight_approval', 0.30)
        weight_publish = getattr(self._settings, 'learning_weight_publish', 0.20)
        weight_engagement = getattr(self._settings, 'learning_weight_engagement', 0.30)
        weight_success = getattr(self._settings, 'learning_weight_success', 0.20)

        # Calculate composite score
        composite_score = (
            approval_rate * weight_approval +
            publish_rate * weight_publish +
            engagement_score * weight_engagement +
            success_rate * weight_success
        )

        logger.debug(
            "score_components",
            subreddit=subreddit,
            approval=round(approval_rate, 3),
            publish=round(publish_rate, 3),
            engagement=round(engagement_score, 3),
            success=round(success_rate, 3),
            composite=round(composite_score, 3)
        )

        return composite_score

    def _get_decay_weight(self, created_at: datetime) -> float:
        """
        Calculate time-based decay weight.

        Recent data gets higher weight than old data:
        - Last 7 days: 1.0
        - 7-30 days: 0.7
        - 30-90 days: 0.4
        - Older: 0.2

        Args:
            created_at: Record creation timestamp

        Returns:
            Decay weight between 0.2 and 1.0
        """
        age = datetime.utcnow() - created_at
        days_old = age.days

        recent_days = getattr(self._settings, 'learning_decay_recent_days', 7)
        medium_days = getattr(self._settings, 'learning_decay_medium_days', 30)
        old_days = getattr(self._settings, 'learning_decay_old_days', 90)

        if days_old <= recent_days:
            return 1.0
        elif days_old <= medium_days:
            return 0.7
        elif days_old <= old_days:
            return 0.4
        else:
            return 0.2

    def _calculate_approval_rate(self, records: list) -> float:
        """
        Calculate decay-weighted approval rate.

        Args:
            records: List of PerformanceHistory records

        Returns:
            Weighted approval rate 0.0-1.0
        """
        total_weight = 0.0
        approved_weight = 0.0

        for record in records:
            weight = self._get_decay_weight(record.created_at)
            total_weight += weight

            if record.outcome in ("APPROVED", "PUBLISHED"):
                approved_weight += weight

        if total_weight == 0:
            return 0.5  # Neutral

        return approved_weight / total_weight

    def _calculate_publish_rate(self, records: list) -> float:
        """
        Calculate decay-weighted publish rate among approved drafts.

        Args:
            records: List of PerformanceHistory records

        Returns:
            Weighted publish rate 0.0-1.0
        """
        total_weight = 0.0
        published_weight = 0.0

        for record in records:
            # Only consider approved drafts
            if record.outcome not in ("APPROVED", "PUBLISHED"):
                continue

            weight = self._get_decay_weight(record.created_at)
            total_weight += weight

            if record.outcome == "PUBLISHED":
                published_weight += weight

        if total_weight == 0:
            return 0.5  # Neutral

        return published_weight / total_weight

    def _calculate_engagement_score(self, records: list) -> float:
        """
        Calculate normalized engagement score.

        Uses engagement_score field (log(upvotes+1) + replies*2).
        Normalizes to 0.0-1.0 range based on observed values.

        Args:
            records: List of PerformanceHistory records

        Returns:
            Normalized engagement score 0.0-1.0
        """
        total_weight = 0.0
        weighted_engagement = 0.0

        for record in records:
            # Only consider published drafts with engagement data
            if record.outcome != "PUBLISHED" or record.engagement_score is None:
                continue

            weight = self._get_decay_weight(record.created_at)
            total_weight += weight
            weighted_engagement += record.engagement_score * weight

        if total_weight == 0:
            return 0.5  # Neutral

        avg_engagement = weighted_engagement / total_weight

        # Normalize to 0-1 range
        # Assume engagement_score ranges from 0 to ~10 (based on formula)
        # 0 upvotes, 0 replies = 0
        # 100 upvotes, 5 replies = log(101) + 10 ≈ 14.6
        # Use a softer normalization curve
        max_expected = 10.0
        normalized = min(avg_engagement / max_expected, 1.0)

        return normalized

    def _calculate_success_rate(self, records: list) -> float:
        """
        Calculate decay-weighted success rate.

        Success = published with 5+ upvotes after 24h.

        Args:
            records: List of PerformanceHistory records

        Returns:
            Weighted success rate 0.0-1.0
        """
        total_weight = 0.0
        success_weight = 0.0

        for record in records:
            # Only consider published drafts with engagement data
            if record.outcome != "PUBLISHED" or record.upvotes_24h is None:
                continue

            weight = self._get_decay_weight(record.created_at)
            total_weight += weight

            if record.upvotes_24h >= 5:
                success_weight += weight

        if total_weight == 0:
            return 0.5  # Neutral

        return success_weight / total_weight
