"""
Quality scoring service for candidate ranking.

Implements 7-factor composite scoring:
- Upvote ratio (0.15)
- Author karma (0.10)
- Thread freshness (0.20)
- Engagement velocity (0.15)
- Question signal (0.15)
- Thread depth (0.10)
- Historical performance (0.15)
"""
import time
import re
from typing import Optional
from dataclasses import replace

from services.reddit_client import Candidate, CandidateComment, CandidatePost
from config import Settings
from utils.logging import get_logger

logger = get_logger(__name__)


class QualityScorer:
    """Calculate quality scores for engagement candidates."""

    def __init__(
        self,
        settings: Settings,
        performance_tracker: Optional['PerformanceTracker'] = None
    ):
        """
        Initialize scorer with configuration.

        Args:
            settings: Application settings
            performance_tracker: Optional performance tracker for historical scoring
        """
        self.settings = settings
        self.performance_tracker = performance_tracker

        # Parse keyword lists
        help_keywords = [k.strip() for k in settings.score_help_keywords.split(',') if k.strip()]
        problem_keywords = [k.strip() for k in settings.score_problem_keywords.split(',') if k.strip()]

        # Compile regex patterns once for efficiency
        self._help_pattern = re.compile(
            '|'.join(re.escape(kw) for kw in help_keywords),
            re.IGNORECASE
        ) if help_keywords else None

        self._problem_pattern = re.compile(
            '|'.join(re.escape(kw) for kw in problem_keywords),
            re.IGNORECASE
        ) if problem_keywords else None

        # Normalize weights (must sum to 1.0)
        total_weight = (
            settings.score_weight_upvote +
            settings.score_weight_karma +
            settings.score_weight_freshness +
            settings.score_weight_velocity +
            settings.score_weight_question +
            settings.score_weight_depth +
            settings.score_weight_historical
        )

        if total_weight == 0:
            total_weight = 1.0  # Avoid division by zero

        self._weight_upvote = settings.score_weight_upvote / total_weight
        self._weight_karma = settings.score_weight_karma / total_weight
        self._weight_freshness = settings.score_weight_freshness / total_weight
        self._weight_velocity = settings.score_weight_velocity / total_weight
        self._weight_question = settings.score_weight_question / total_weight
        self._weight_depth = settings.score_weight_depth / total_weight
        self._weight_historical = settings.score_weight_historical / total_weight

        logger.info(
            "quality_scorer_initialized",
            weights={
                "upvote": round(self._weight_upvote, 3),
                "karma": round(self._weight_karma, 3),
                "freshness": round(self._weight_freshness, 3),
                "velocity": round(self._weight_velocity, 3),
                "question": round(self._weight_question, 3),
                "depth": round(self._weight_depth, 3),
                "historical": round(self._weight_historical, 3)
            }
        )

    def score_candidate(self, candidate: Candidate) -> Candidate:
        """
        Calculate composite quality score for a candidate.

        Args:
            candidate: Candidate to score

        Returns:
            Candidate with quality_score field populated
        """
        try:
            scores = {
                "upvote": self._score_upvote_ratio(candidate),
                "karma": self._score_author_karma(candidate),
                "freshness": self._score_freshness(candidate),
                "velocity": self._score_velocity(candidate),
                "question": self._score_question_signal(candidate),
                "depth": self._score_thread_depth(candidate),
                "historical": self._score_historical(candidate.subreddit)
            }

            final_score = (
                scores["upvote"] * self._weight_upvote +
                scores["karma"] * self._weight_karma +
                scores["freshness"] * self._weight_freshness +
                scores["velocity"] * self._weight_velocity +
                scores["question"] * self._weight_question +
                scores["depth"] * self._weight_depth +
                scores["historical"] * self._weight_historical
            )

            logger.info(
                "candidate_scored",
                reddit_id=candidate.reddit_id,
                subreddit=candidate.subreddit,
                candidate_type=candidate.candidate_type,
                scores={k: round(v, 3) for k, v in scores.items()},
                final_score=round(final_score, 3)
            )

            # Attach score to candidate (dataclass immutability workaround)
            return replace(candidate, quality_score=final_score)

        except Exception as e:
            logger.error(
                "scoring_failed",
                reddit_id=candidate.reddit_id,
                error=str(e)
            )
            # Return candidate with default score on error
            return replace(candidate, quality_score=0.5)

    def _score_upvote_ratio(self, candidate: Candidate) -> float:
        """Score based on upvote ratio (posts) or estimated ratio (comments)."""
        try:
            if isinstance(candidate, CandidatePost):
                ratio = candidate.submission.upvote_ratio
            else:
                # Estimate ratio from comment score (heuristic)
                score = candidate.comment.score
                if score >= 10:
                    ratio = 0.85
                elif score >= 5:
                    ratio = 0.75
                elif score >= 2:
                    ratio = 0.65
                elif score >= 0:
                    ratio = 0.55
                else:
                    ratio = 0.40

            if ratio >= self.settings.score_upvote_excellent:
                return 1.0
            elif ratio >= self.settings.score_upvote_good:
                return 0.8
            elif ratio >= self.settings.score_upvote_mixed:
                return 0.5
            else:
                return 0.2

        except Exception as e:
            logger.warning("upvote_ratio_scoring_failed", error=str(e))
            return 0.5

    def _score_author_karma(self, candidate: Candidate) -> float:
        """Score based on author's combined karma."""
        try:
            if isinstance(candidate, CandidatePost):
                author = candidate.submission.author
            else:
                author = candidate.comment.author

            if author is None:
                return 0.0

            # Get karma safely
            try:
                link_karma = getattr(author, 'link_karma', 0)
                comment_karma = getattr(author, 'comment_karma', 0)
                total_karma = link_karma + comment_karma
            except Exception:
                return 0.5

            if total_karma >= self.settings.score_karma_established:
                return 1.0
            elif total_karma >= self.settings.score_karma_active:
                return 0.8
            elif total_karma >= self.settings.score_karma_regular:
                return 0.5
            else:
                return 0.3

        except Exception as e:
            logger.warning("karma_scoring_failed", error=str(e))
            return 0.5

    def _score_freshness(self, candidate: Candidate) -> float:
        """Score based on how recently the thread was created."""
        try:
            if isinstance(candidate, CandidatePost):
                created_utc = candidate.submission.created_utc
            else:
                created_utc = candidate.comment.created_utc

            age_seconds = time.time() - created_utc

            if age_seconds < self.settings.score_freshness_hot:
                return 1.0
            elif age_seconds < self.settings.score_freshness_active:
                return 0.8
            elif age_seconds < self.settings.score_freshness_warm:
                return 0.6
            elif age_seconds < self.settings.score_freshness_cooling:
                return 0.4
            else:
                return 0.2

        except Exception as e:
            logger.warning("freshness_scoring_failed", error=str(e))
            return 0.5

    def _score_velocity(self, candidate: Candidate) -> float:
        """Score based on engagement velocity (comments/minute)."""
        try:
            if isinstance(candidate, CandidatePost):
                submission = candidate.submission
            else:
                # Get parent submission from comment
                submission = candidate.comment.submission

            age_minutes = (time.time() - submission.created_utc) / 60.0
            if age_minutes < 1:
                age_minutes = 1  # Avoid division by zero

            num_comments = submission.num_comments
            velocity = num_comments / age_minutes

            if velocity >= self.settings.score_velocity_viral:
                return 1.0
            elif velocity >= self.settings.score_velocity_high:
                return 0.8
            elif velocity >= self.settings.score_velocity_moderate:
                return 0.6
            elif velocity >= self.settings.score_velocity_low:
                return 0.4
            else:
                return 0.2

        except Exception as e:
            logger.warning("velocity_scoring_failed", error=str(e))
            return 0.5

    def _score_question_signal(self, candidate: Candidate) -> float:
        """Score based on question/help-seeking signals."""
        try:
            if isinstance(candidate, CandidatePost):
                title = candidate.title
                body = candidate.body or ""
            else:
                title = candidate.post_title
                body = candidate.body

            score = 0.0
            text = f"{title} {body}".lower()

            # Question mark in title
            if '?' in title:
                score += 0.4

            # Help keywords
            if self._help_pattern and self._help_pattern.search(text):
                score += 0.3

            # Problem keywords
            if self._problem_pattern and self._problem_pattern.search(text):
                score += 0.3

            # No signals - default baseline
            if score == 0:
                score = 0.2

            return min(score, 1.0)

        except Exception as e:
            logger.warning("question_signal_scoring_failed", error=str(e))
            return 0.5

    def _score_thread_depth(self, candidate: Candidate) -> float:
        """Score based on thread comment count (optimal engagement window)."""
        try:
            if isinstance(candidate, CandidatePost):
                num_comments = candidate.submission.num_comments
            else:
                num_comments = candidate.comment.submission.num_comments

            ideal_min = self.settings.score_depth_ideal_min
            ideal_max = self.settings.score_depth_ideal_max
            early_min = self.settings.score_depth_early_min
            crowded_max = self.settings.score_depth_crowded_max

            if ideal_min <= num_comments <= ideal_max:
                return 1.0
            elif early_min <= num_comments < ideal_min:
                return 0.8
            elif ideal_max < num_comments <= crowded_max:
                return 0.7
            elif num_comments < early_min:
                return 0.4
            else:  # > crowded_max
                return 0.3

        except Exception as e:
            logger.warning("depth_scoring_failed", error=str(e))
            return 0.5

    def _score_historical(self, subreddit: str) -> float:
        """Score based on historical performance in subreddit."""
        # Phase 1: Return neutral score (Phase 3 will integrate PerformanceTracker)
        if not self.settings.learning_enabled:
            return 0.5

        if self.performance_tracker is None:
            return 0.5

        try:
            return self.performance_tracker.get_subreddit_score(subreddit)
        except Exception as e:
            logger.warning("historical_scoring_failed", subreddit=subreddit, error=str(e))
            return 0.5
