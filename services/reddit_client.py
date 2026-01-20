"""
Reddit API client with safety features.

Implements Story 2: Reddit Client with Shadowban Kill-Switch
- AutoMod/Bot filtering
- Shadowban detection and circuit breaker
- Rate limit handling
- Subreddit allow-listing
"""
import re
import time
from typing import List, Optional, Any, Union
from dataclasses import dataclass, field
import praw
from praw.models import Comment, Submission

from utils.logging import get_logger
from config import get_settings

logger = get_logger(__name__)


class SafetyLockoutException(Exception):
    """Raised when shadowban risk exceeds threshold. System must halt."""
    pass


class RateLimitExceeded(Exception):
    """Raised when Reddit API rate limit is exceeded."""
    pass


@dataclass
class CandidateComment:
    """A comment candidate for potential response."""
    comment: Any  # PRAW Comment object
    subreddit: str
    reddit_id: str
    author: str
    body: str
    context_url: str
    post_title: str
    parent_id: str
    post_id: str = ""  # Submission ID (Phase B: for diversity filtering)
    candidate_type: str = "comment"  # Type discriminator
    quality_score: float = 0.0  # Quality score (populated by QualityScorer)
    priority: str = "NORMAL"  # Priority level: HIGH (inbox) or NORMAL (rising)


@dataclass
class CandidatePost:
    """A post candidate for direct reply."""
    submission: Any  # PRAW Submission object
    subreddit: str
    reddit_id: str
    author: str
    title: str
    body: str  # selftext
    context_url: str
    candidate_type: str = "post"  # Type discriminator
    quality_score: float = 0.0  # Quality score (populated by QualityScorer)
    priority: str = "NORMAL"  # Priority level: HIGH (inbox) or NORMAL (rising)


# Type alias for any candidate
Candidate = Union[CandidateComment, CandidatePost]


class RedditClient:
    """
    Reddit API client with safety features.
    
    Features:
    - AutoModerator and bot filtering
    - Shadowban detection with circuit breaker
    - Rate limit tracking
    - Subreddit allow-listing
    - Post discovery (rising posts < 45 min)
    """
    
    # Bot detection pattern (case insensitive)
    BOT_PATTERN = re.compile(r'(?i)(bot|assistant|auto)', re.IGNORECASE)
    
    # Controversial/political keywords to avoid (PRD §6.2)
    CONTROVERSIAL_KEYWORDS = [
        "trump", "biden", "obama", "maga",
        "democrat", "republican", "liberal", "conservative",
        "politics", "political", "election", "vote",
        "abortion", "pro-life", "pro-choice",
        "gun control", "second amendment", "2nd amendment",
        "immigration", "immigrant", "border wall", "deportation",
        "racist", "racism", "nazi", "fascist", "antifa",
        "blm", "black lives matter", "all lives matter",
        "lgbtq", "transgender", "trans rights",
        "climate change", "global warming",
        "vaccine", "anti-vax", "covid hoax",
        "conspiracy", "qanon", "deep state",
    ]
    
    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        user_agent: Optional[str] = None,
        allowed_subreddits: Optional[List[str]] = None,
        risk_threshold: float = 0.7,
    ):
        """
        Initialize Reddit client.
        
        Args:
            client_id: Reddit OAuth client ID
            client_secret: Reddit OAuth client secret
            username: Reddit username
            password: Reddit password
            user_agent: User agent string (must match format)
            allowed_subreddits: List of allowed subreddit names
            risk_threshold: Shadowban risk threshold (0-1)
        """
        settings = get_settings()
        
        self._client_id = client_id or settings.reddit_client_id
        self._client_secret = client_secret or settings.reddit_client_secret
        self._username = username or settings.reddit_username
        self._password = password or settings.reddit_password
        self._user_agent = user_agent or settings.reddit_user_agent
        self._allowed_subreddits = allowed_subreddits or settings.subreddits_list
        self._risk_threshold = risk_threshold or settings.shadowban_risk_threshold
        
        # Normalize subreddit names (lowercase, no r/ prefix)
        self._allowed_subreddits = [
            s.lower().replace('r/', '') for s in self._allowed_subreddits
        ]
        
        # Safety tracking
        self._error_counts = {"403": 0, "empty_listing": 0}
        self._total_requests = 0
        self._rate_limit_remaining = 100
        self._rate_limit_reset = 0

        # Post discovery settings
        self._max_post_age_seconds = 45 * 60 * 15 # 45 minutes
        self._min_comments = 3
        self._max_comments = 20

        # Cache for rising posts (per workflow run) to avoid duplicate fetches
        self._rising_posts_cache = {}  # {subreddit: List[Submission]}

        # Initialize PRAW client (lazy)
        self._reddit: Optional[praw.Reddit] = None
        
        logger.info(
            "reddit_client_initialized",
            allowed_subreddits=self._allowed_subreddits,
            risk_threshold=self._risk_threshold
        )
    
    @property
    def reddit(self) -> praw.Reddit:
        """Lazy initialization of PRAW client."""
        if self._reddit is None:
            self._reddit = praw.Reddit(
                client_id=self._client_id,
                client_secret=self._client_secret,
                username=self._username,
                password=self._password,
                user_agent=self._user_agent
            )
            logger.info("praw_client_created")
        return self._reddit
    
    # ========================================
    # Author Filtering (Story 2 requirement)
    # ========================================
    
    def _should_skip_author(self, comment: Any) -> bool:
        """
        Check if comment author should be skipped.
        
        Skip if:
        - author is None (deleted account)
        - author is AutoModerator
        - author matches bot pattern
        - author_is_bot flag is True
        
        Args:
            comment: PRAW comment or mock
            
        Returns:
            True if author should be skipped
        """
        # Deleted author
        if comment.author is None:
            logger.debug("skipping_deleted_author", reddit_id=getattr(comment, 'id', 'unknown'))
            return True
        
        author_name = comment.author.name
        
        # AutoModerator
        if author_name == "AutoModerator":
            logger.debug("skipping_automoderator")
            return True
        
        # Bot flag
        if getattr(comment, 'author_is_bot', False):
            logger.debug("skipping_bot_flag", author=author_name)
            return True
        
        # Bot pattern match
        if self.BOT_PATTERN.search(author_name):
            logger.debug("skipping_bot_pattern", author=author_name)
            return True
        
        return False
    
    def _should_skip_author_submission(self, submission: Submission) -> bool:
        """
        Check if submission author should be skipped.
        
        Skip if:
        - author is None (deleted account)
        - author matches bot pattern
        
        Args:
            submission: PRAW Submission object
            
        Returns:
            True if author should be skipped
        """
        if submission.author is None:
            logger.debug("skipping_deleted_author_submission", reddit_id=getattr(submission, 'id', 'unknown'))
            return True
        
        author_name = submission.author.name
        
        if self.BOT_PATTERN.search(author_name):
            logger.debug("skipping_bot_pattern_submission", author=author_name)
            return True
        
        return False
    
    # ========================================
    # Shadowban Detection (Story 2 requirement)
    # ========================================
    
    def _record_error(self, error_type: str) -> None:
        """Record an error for risk calculation."""
        if error_type in self._error_counts:
            self._error_counts[error_type] += 1
        self._total_requests += 1
        
        logger.warning(
            "error_recorded",
            error_type=error_type,
            counts=self._error_counts,
            total=self._total_requests
        )
    
    def _calculate_shadowban_risk(self) -> float:
        """
        Calculate shadowban risk score based on error patterns.
        
        Risk factors:
        - High rate of 403 errors on accessible content
        - Empty listing responses
        
        Returns:
            Risk score between 0 and 1
        """
        if self._total_requests == 0:
            return 0.0
        
        # Weight factors
        error_403_weight = 0.6
        empty_listing_weight = 0.4
        
        # Calculate weighted risk
        error_403_rate = self._error_counts["403"] / max(self._total_requests, 1)
        empty_listing_rate = self._error_counts["empty_listing"] / max(self._total_requests, 1)
        
        risk = (error_403_rate * error_403_weight) + (empty_listing_rate * empty_listing_weight)
        
        return min(risk, 1.0)
    
    def _check_shadowban_risk(self) -> None:
        """
        Check shadowban risk and raise exception if too high.
        
        Raises:
            SafetyLockoutException: If risk exceeds threshold
        """
        risk = self._calculate_shadowban_risk()
        
        if risk > self._risk_threshold:
            logger.error(
                "shadowban_risk_exceeded",
                risk=risk,
                threshold=self._risk_threshold,
                error_counts=self._error_counts
            )
            raise SafetyLockoutException(
                f"Shadowban risk ({risk:.2f}) exceeds threshold ({self._risk_threshold}). "
                "Halting to protect account."
            )
    
    # ========================================
    # Rate Limiting (Story 2 requirement)
    # ========================================
    
    def _check_rate_limit(self) -> None:
        """
        Check rate limit and raise exception if depleted.
        
        Raises:
            RateLimitExceeded: If no remaining requests
        """
        if self._rate_limit_remaining <= 0:
            logger.warning(
                "rate_limit_exceeded",
                reset_in=self._rate_limit_reset
            )
            raise RateLimitExceeded(
                f"Rate limit exceeded. Reset in {self._rate_limit_reset} seconds."
            )
    
    def _update_rate_limit(self, remaining: int, reset: int) -> None:
        """Update rate limit tracking from API response."""
        self._rate_limit_remaining = remaining
        self._rate_limit_reset = reset
    
    # ========================================
    # Subreddit Filtering
    # ========================================
    
    def _is_allowed_subreddit(self, comment: Any) -> bool:
        """
        Check if comment is from an allowed subreddit.
        
        Args:
            comment: PRAW comment or mock
            
        Returns:
            True if subreddit is in allow-list
        """
        subreddit_name = comment.subreddit.display_name.lower()
        is_allowed = subreddit_name in self._allowed_subreddits
        
        if not is_allowed:
            logger.debug(
                "subreddit_not_allowed",
                subreddit=subreddit_name,
                allowed=self._allowed_subreddits
            )
        
        return is_allowed
    
    # ========================================
    # Post Discovery (Rising posts < 45 min)
    # ========================================
    
    def _is_valid_post_age(self, post: Any) -> bool:
        """Check if post is within age limit."""
        post_age = time.time() - post.created_utc
        return post_age <= self._max_post_age_seconds
    
    def _is_valid_comment_count(self, post: Any) -> bool:
        """Check if post has appropriate comment count (3-20)."""
        count = post.num_comments
        return self._min_comments <= count <= self._max_comments
    
    def _is_thread_available(self, post: Any) -> bool:
        """Check if thread is available (not locked/removed)."""
        if post.locked:
            return False
        if getattr(post, 'removed_by_category', None) is not None:
            return False
        return True
    
    def _has_controversial_keywords(self, post: Any) -> bool:
        """
        Check if post contains controversial/political keywords.
        
        Checks title and body (selftext) for blocklisted terms.
        """
        text_to_check = f"{post.title} {getattr(post, 'selftext', '')}".lower()
        
        for keyword in self.CONTROVERSIAL_KEYWORDS:
            if keyword in text_to_check:
                logger.debug(
                    "controversial_keyword_found",
                    post_id=post.id,
                    keyword=keyword
                )
                return True
        return False
    
    # ========================================
    # Public API
    # ========================================
    
    def fetch_inbox_replies(self, limit: int = 25) -> List[CandidateComment]:
        """
        Fetch unread inbox replies.
        
        Filters:
        - Allowed subreddits only
        - Excludes AutoModerator and bots
        - Excludes deleted authors
        
        Args:
            limit: Maximum replies to fetch
            
        Returns:
            List of candidate comments
            
        Raises:
            SafetyLockoutException: If shadowban risk is high
            RateLimitExceeded: If rate limit is exceeded
        """
        self._check_rate_limit()
        self._check_shadowban_risk()
        
        candidates = []
        
        try:
            inbox = self.reddit.inbox.unread(limit=limit)
            self._total_requests += 1
            
            for item in inbox:
                # Only process comments (not messages)
                if not isinstance(item, Comment):
                    continue
                
                # Apply filters
                if not self._is_allowed_subreddit(item):
                    continue
                    
                if self._should_skip_author(item):
                    continue
                
                # Create candidate
                candidate = CandidateComment(
                    comment=item,
                    subreddit=item.subreddit.display_name,
                    reddit_id=item.id,
                    author=item.author.name,
                    body=item.body,
                    context_url=f"https://reddit.com{item.permalink}",
                    post_title=item.submission.title,
                    parent_id=item.parent_id,
                    post_id=item.submission.id  # Phase B: Extract post ID for diversity
                )
                candidates.append(candidate)
                
                logger.info(
                    "candidate_found",
                    reddit_id=item.id,
                    subreddit=candidate.subreddit,
                    author=candidate.author
                )
            
        except Exception as e:
            error_str = str(e)
            if "403" in error_str:
                self._record_error("403")
            logger.error("inbox_fetch_error", error=error_str)
            raise
        
        logger.info("inbox_fetch_complete", count=len(candidates))
        return candidates
    
    def clear_cache(self) -> None:
        """
        Clear the rising posts cache.

        Should be called at the start of each workflow run to ensure fresh data.
        """
        self._rising_posts_cache = {}
        logger.debug("rising_posts_cache_cleared")

    def fetch_rising_posts(self, subreddit: str, limit: int = 10) -> List[Submission]:
        """
        Fetch rising posts from a subreddit with caching.

        Filters (PRD §6.2):
        - Age < 45 minutes
        - Comment count 3-20
        - Not locked or removed
        - No controversial keywords

        Caching: Results are cached per subreddit for the duration of a single
        workflow run to avoid duplicate API calls. Call clear_cache() at the
        start of each run.

        Args:
            subreddit: Subreddit name
            limit: Maximum posts to fetch

        Returns:
            List of valid submissions
        """
        # Check cache first
        if subreddit in self._rising_posts_cache:
            logger.debug(
                "rising_posts_cache_hit",
                subreddit=subreddit,
                cached_count=len(self._rising_posts_cache[subreddit])
            )
            return self._rising_posts_cache[subreddit]

        self._check_rate_limit()
        self._check_shadowban_risk()

        valid_posts = []

        try:
            sub = self.reddit.subreddit(subreddit)
            rising = sub.rising(limit=limit)
            self._total_requests += 1

            for post in rising:
                if not self._is_valid_post_age(post):
                    continue
                if not self._is_valid_comment_count(post):
                    continue
                if not self._is_thread_available(post):
                    continue
                if self._has_controversial_keywords(post):
                    continue

                valid_posts.append(post)
                logger.info(
                    "rising_post_found",
                    post_id=post.id,
                    title=post.title[:50],
                    comments=post.num_comments
                )

            if len(valid_posts) == 0:
                self._record_error("empty_listing")

            # Store in cache
            self._rising_posts_cache[subreddit] = valid_posts
            logger.debug(
                "rising_posts_cached",
                subreddit=subreddit,
                count=len(valid_posts)
            )

        except Exception as e:
            error_str = str(e)
            if "403" in error_str:
                self._record_error("403")
            logger.error("rising_fetch_error", subreddit=subreddit, error=error_str)
            raise

        return valid_posts
    
    def fetch_rising_candidates(self, limit_per_subreddit: int = 5, one_per_post: bool = True) -> List[CandidateComment]:
        """
        Fetch candidate comments from rising posts in all allowed subreddits.
        
        For each valid rising post, selects top-level comments as candidates.
        
        Args:
            limit_per_subreddit: Max posts to check per subreddit
            one_per_post: If True, select only one comment per post for diversity
            
        Returns:
            List of candidate comments from rising posts
        """
        candidates = []
        comments_per_post = 1 if one_per_post else 3
        
        for subreddit in self._allowed_subreddits:
            try:
                posts = self.fetch_rising_posts(subreddit, limit=limit_per_subreddit)
                
                for post in posts:
                    # Get top-level comments from the post
                    post.comments.replace_more(limit=0)
                    self._total_requests += 1
                    
                    for comment in post.comments[:comments_per_post]:
                        # Apply author filters
                        if self._should_skip_author(comment):
                            continue
                        
                        candidate = CandidateComment(
                            comment=comment,
                            subreddit=subreddit,
                            reddit_id=comment.id,
                            author=comment.author.name if comment.author else "[deleted]",
                            body=comment.body,
                            context_url=f"https://reddit.com{comment.permalink}",
                            post_title=post.title,
                            parent_id=comment.parent_id,
                            post_id=post.id  # Phase B: Extract post ID for diversity
                        )
                        candidates.append(candidate)
                        
                        logger.info(
                            "rising_candidate_found",
                            reddit_id=comment.id,
                            subreddit=subreddit,
                            post_title=post.title[:30]
                        )
                        
            except Exception as e:
                logger.warning(
                    "rising_fetch_subreddit_error",
                    subreddit=subreddit,
                    error=str(e)
                )
                continue
        
        logger.info("rising_candidates_complete", count=len(candidates))
        return candidates
    
    def fetch_rising_posts_as_candidates(self, limit_per_subreddit: int = 5) -> List[CandidatePost]:
        """
        Fetch rising posts as candidates for direct reply.
        
        Uses same filters as fetch_rising_posts but returns CandidatePost objects.
        
        Args:
            limit_per_subreddit: Max posts to fetch per subreddit
            
        Returns:
            List of CandidatePost objects
        """
        candidates = []
        
        for subreddit in self._allowed_subreddits:
            try:
                posts = self.fetch_rising_posts(subreddit, limit=limit_per_subreddit)
                
                for post in posts:
                    # Apply author filter
                    if self._should_skip_author_submission(post):
                        continue
                    
                    candidate = CandidatePost(
                        submission=post,
                        subreddit=subreddit,
                        reddit_id=post.id,
                        author=post.author.name if post.author else "[deleted]",
                        title=post.title,
                        body=post.selftext or "",
                        context_url=f"https://reddit.com{post.permalink}"
                    )
                    candidates.append(candidate)
                    
                    logger.info(
                        "post_candidate_found",
                        reddit_id=post.id,
                        subreddit=subreddit,
                        title=post.title[:30]
                    )
                    
            except Exception as e:
                logger.warning(
                    "rising_posts_fetch_error",
                    subreddit=subreddit,
                    error=str(e)
                )
                continue
        
        logger.info("post_candidates_complete", count=len(candidates))
        return candidates
    
    def post_comment(self, parent: Any, body: str, dry_run: bool = False) -> Optional[str]:
        """
        Post a comment reply.
        
        Args:
            parent: Parent comment or submission
            body: Comment text
            dry_run: If True, don't actually post
            
        Returns:
            Comment ID if posted, None if dry run
        """
        self._check_rate_limit()
        self._check_shadowban_risk()
        
        if dry_run:
            logger.info(
                "dry_run_post",
                parent_id=parent.id,
                body_length=len(body)
            )
            return None
        
        try:
            comment = parent.reply(body)
            self._total_requests += 1
            
            logger.info(
                "comment_posted",
                comment_id=comment.id,
                parent_id=parent.id
            )
            
            return comment.id
            
        except Exception as e:
            error_str = str(e)
            if "403" in error_str:
                self._record_error("403")
            logger.error("post_comment_error", error=error_str)
            raise
    
    def get_comment_context(self, comment: Comment) -> dict:
        """
        Get context for a comment (post + parent chain).
        
        Args:
            comment: PRAW Comment object
            
        Returns:
            Dict with post and parent chain
        """
        self._check_rate_limit()
        
        try:
            # Get the submission (post)
            submission = comment.submission
            self._total_requests += 1
            
            # Build parent chain (grandparent -> parent -> target)
            parent_chain = []
            current = comment
            
            # Walk up the chain (max 3 levels: grandparent, parent, target)
            for _ in range(3):
                parent_chain.insert(0, current)
                
                if current.parent_id.startswith("t3_"):
                    # Parent is the post, stop here
                    break
                    
                # Get parent comment
                parent = self.reddit.comment(current.parent_id.replace("t1_", ""))
                current = parent
                self._total_requests += 1
            
            return {
                "post": submission,
                "parent_chain": parent_chain,
                "target": comment
            }
            
        except Exception as e:
            logger.error("get_context_error", comment_id=comment.id, error=str(e))
            raise
    
    def get_post_context(self, submission: Submission) -> dict:
        """
        Get context for a post (for direct reply).
        
        Args:
            submission: PRAW Submission object
            
        Returns:
            Dict with post details for context building
        """
        self._check_rate_limit()
        self._total_requests += 1
        
        return {
            "post": submission,
            "parent_chain": [],
            "target": submission,
            "is_post_reply": True
        }
