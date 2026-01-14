"""
Subreddit rule interpreter and cache.

Implements Story 4: Subreddit Rule Interpreter & Cache Enforcement
- Keyword-based blocking
- Cache-first compliance checking
- Bot ban detection
- Political/controversial content filtering
"""
import re
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field

from utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class CachedRule:
    """Cached subreddit rules and status."""
    subreddit: str
    rules: str
    status: str  # ALLOWED or RESTRICTED
    timestamp: datetime = field(default_factory=datetime.utcnow)


class RuleCache:
    """
    In-memory cache for subreddit rules.
    
    Provides cache-first lookups to minimize API calls.
    """
    
    def __init__(self, max_age_hours: int = 24):
        """
        Initialize rule cache.
        
        Args:
            max_age_hours: Maximum age before cache entry is stale
        """
        self._cache: Dict[str, CachedRule] = {}
        self._max_age = timedelta(hours=max_age_hours)
        logger.debug("rule_cache_initialized", max_age_hours=max_age_hours)
    
    def get(self, subreddit: str) -> Optional[Dict[str, Any]]:
        """
        Get cached rules for a subreddit.
        
        Args:
            subreddit: Subreddit name
            
        Returns:
            Dict with rules and status, or None if not cached/stale
        """
        subreddit = subreddit.lower().replace('r/', '')
        
        if subreddit not in self._cache:
            return None
        
        cached = self._cache[subreddit]
        
        # Check if stale
        age = datetime.utcnow() - cached.timestamp
        if age > self._max_age:
            logger.debug("cache_stale", subreddit=subreddit, age_hours=age.total_seconds() / 3600)
            return None
        
        return {
            "rules": cached.rules,
            "status": cached.status,
            "timestamp": cached.timestamp
        }
    
    def set(
        self,
        subreddit: str,
        rules: str,
        status: str,
        timestamp: Optional[datetime] = None
    ) -> None:
        """
        Cache rules for a subreddit.
        
        Args:
            subreddit: Subreddit name
            rules: Rule text
            status: ALLOWED or RESTRICTED
            timestamp: Cache timestamp (defaults to now)
        """
        subreddit = subreddit.lower().replace('r/', '')
        
        self._cache[subreddit] = CachedRule(
            subreddit=subreddit,
            rules=rules,
            status=status,
            timestamp=timestamp or datetime.utcnow()
        )
        
        logger.info(
            "rules_cached",
            subreddit=subreddit,
            status=status,
            rules_length=len(rules)
        )
    
    def is_stale(self, subreddit: str) -> bool:
        """Check if cache entry is stale or missing."""
        cached = self.get(subreddit)
        return cached is None


class RuleEngine:
    """
    Subreddit rule interpreter and compliance checker.
    
    Features:
    - Keyword-based blocking (support threads, etc.)
    - Bot restriction detection
    - Political/controversial content filtering
    - Cache-first compliance checking
    """
    
    # Patterns for detecting support/help requests
    SUPPORT_PATTERNS = [
        re.compile(r'\bhelp\s*(me|us)?\b', re.IGNORECASE),
        re.compile(r'\bhow\s+do\s+i\b', re.IGNORECASE),
        re.compile(r'\bplease\s+help\b', re.IGNORECASE),
        re.compile(r'\bsupport\s+question\b', re.IGNORECASE),
    ]
    
    # Patterns for bot restriction in rules
    BOT_RESTRICTION_PATTERNS = [
        re.compile(r'\bno\s+bots?\b', re.IGNORECASE),
        re.compile(r'\bbots?\s+not\s+allowed\b', re.IGNORECASE),
        re.compile(r'\bno\s+automation\b', re.IGNORECASE),
        re.compile(r'\bhuman\s+(posts?|only)\b', re.IGNORECASE),
    ]
    
    # Political/controversial keywords
    POLITICAL_KEYWORDS = [
        'biden', 'trump', 'republican', 'democrat', 'liberal', 'conservative',
        'abortion', 'gun control', 'immigration', 'election', 'vote for',
        'political', 'left wing', 'right wing', 'socialist', 'fascist',
    ]
    
    # Rule keywords that indicate restrictions
    BLOCKING_KEYWORDS = {
        'no support': SUPPORT_PATTERNS,
    }
    
    def __init__(
        self,
        cache: Optional[RuleCache] = None,
        fetch_rules_fn: Optional[Callable[[str], str]] = None
    ):
        """
        Initialize rule engine.
        
        Args:
            cache: Rule cache instance
            fetch_rules_fn: Function to fetch rules from Reddit API
        """
        self._cache = cache or RuleCache()
        self._fetch_rules_fn = fetch_rules_fn
        logger.debug("rule_engine_initialized")
    
    def check_compliance(self, subreddit: str) -> bool:
        """
        Check if subreddit allows our engagement.
        
        Uses cache-first approach:
        1. Check cache for status
        2. If cached and RESTRICTED, return False immediately
        3. If cached and ALLOWED, return True
        4. If not cached or stale, fetch and analyze rules
        
        Args:
            subreddit: Subreddit name
            
        Returns:
            True if compliant (can engage), False if restricted
        """
        subreddit = subreddit.lower().replace('r/', '')
        
        # Check cache first
        cached = self._cache.get(subreddit)
        
        if cached is not None:
            if cached["status"] == "RESTRICTED":
                logger.info(
                    "subreddit_restricted_cached",
                    subreddit=subreddit
                )
                return False
            else:
                logger.debug("subreddit_allowed_cached", subreddit=subreddit)
                return True
        
        # Cache miss - fetch rules
        if self._fetch_rules_fn is None:
            logger.warning("no_fetch_function", subreddit=subreddit)
            return True  # Default to allow if no fetch function
        
        try:
            rules = self._fetch_rules_fn(subreddit)
        except Exception as e:
            logger.error("rules_fetch_error", subreddit=subreddit, error=str(e))
            return True  # Default to allow on error
        
        # Analyze rules for bot restrictions
        if self.has_bot_restriction(rules):
            self._cache.set(subreddit, rules=rules, status="RESTRICTED")
            logger.warning(
                "subreddit_restricted_bot_ban",
                subreddit=subreddit
            )
            return False
        
        # No restrictions found
        self._cache.set(subreddit, rules=rules, status="ALLOWED")
        logger.info("subreddit_allowed", subreddit=subreddit)
        return True
    
    def is_compliant(
        self,
        subreddit: str,
        rules: str,
        post_title: str
    ) -> bool:
        """
        Check if a specific post is compliant with subreddit rules.
        
        Args:
            subreddit: Subreddit name
            rules: Rule text
            post_title: Title of the post
            
        Returns:
            True if post is compliant
        """
        # Check for "no support" rules
        if self._rules_block_support(rules):
            if self._is_support_request(post_title):
                logger.info(
                    "post_blocked_support",
                    subreddit=subreddit,
                    title=post_title[:50]
                )
                return False
        
        return True
    
    def has_bot_restriction(self, rules: str) -> bool:
        """
        Check if rules contain bot restrictions.
        
        Args:
            rules: Rule text
            
        Returns:
            True if rules mention bot restrictions
        """
        for pattern in self.BOT_RESTRICTION_PATTERNS:
            if pattern.search(rules):
                return True
        return False
    
    def has_controversial_content(self, text: str) -> bool:
        """
        Check if text contains political/controversial content.
        
        Args:
            text: Text to check (title, body)
            
        Returns:
            True if controversial content detected
        """
        text_lower = text.lower()
        
        for keyword in self.POLITICAL_KEYWORDS:
            if keyword in text_lower:
                logger.debug(
                    "controversial_content_detected",
                    keyword=keyword
                )
                return True
        
        return False
    
    def parse_rules(self, rules_text: str) -> List[str]:
        """
        Parse rule text into individual rules.
        
        Handles:
        - Numbered lists (1. Rule, 2. Rule)
        - Bullet points (• Rule, - Rule)
        
        Args:
            rules_text: Raw rules text
            
        Returns:
            List of individual rule strings
        """
        rules = []
        
        # Split by common delimiters
        lines = rules_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Remove numbering
            line = re.sub(r'^\d+[\.\)]\s*', '', line)
            
            # Remove bullet points
            line = re.sub(r'^[•\-\*]\s*', '', line)
            
            if line:
                rules.append(line)
        
        return rules
    
    def _rules_block_support(self, rules: str) -> bool:
        """Check if rules mention blocking support threads."""
        rules_lower = rules.lower()
        return 'no support' in rules_lower or 'support threads' in rules_lower
    
    def _is_support_request(self, title: str) -> bool:
        """Check if title indicates a support request."""
        for pattern in self.SUPPORT_PATTERNS:
            if pattern.search(title):
                return True
        return False
