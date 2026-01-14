"""
Test subreddit rule interpreter and cache (Story 4).
"""
import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta


class TestKeywordBlocking:
    """Test keyword-based blocking."""
    
    def test_keyword_block_no_support_threads(self):
        """Mock rules containing 'No support threads'. Input title 'Help me'. Assert is_compliant() returns False."""
        from services.rule_engine import RuleEngine
        
        engine = RuleEngine()
        rules = "1. No support threads\n2. Be respectful"
        
        result = engine.is_compliant(
            subreddit="test",
            rules=rules,
            post_title="Help me with my Python code"
        )
        
        assert result is False
    
    def test_compliant_post_passes(self):
        """Post that doesn't trigger rules should pass."""
        from services.rule_engine import RuleEngine
        
        engine = RuleEngine()
        rules = "1. No support threads\n2. Be respectful"
        
        result = engine.is_compliant(
            subreddit="test",
            rules=rules,
            post_title="Discussion: New Python features in 3.12"
        )
        
        assert result is True
    
    def test_no_bots_rule_detected(self):
        """Rules containing 'No bots' should flag for restriction."""
        from services.rule_engine import RuleEngine
        
        engine = RuleEngine()
        rules = "1. No bots allowed\n2. Human posts only"
        
        has_bot_restriction = engine.has_bot_restriction(rules)
        assert has_bot_restriction is True
    
    def test_no_bot_restriction_when_absent(self):
        """Rules without bot mention should not flag."""
        from services.rule_engine import RuleEngine
        
        engine = RuleEngine()
        rules = "1. Be respectful\n2. Stay on topic"
        
        has_bot_restriction = engine.has_bot_restriction(rules)
        assert has_bot_restriction is False


class TestCacheFirstBlocking:
    """Test cache-first compliance checking."""
    
    def test_cache_first_blocking_no_network(self):
        """
        Pre-seed subreddit_rules_cache with subreddit='r/foo', status='RESTRICTED'.
        Call check_compliance('r/foo').
        Assert: Returns False WITHOUT making any network calls.
        """
        from services.rule_engine import RuleEngine, RuleCache
        
        # Create cache with restricted subreddit
        cache = RuleCache()
        cache.set("foo", rules="No bots", status="RESTRICTED")
        
        # Create mock network function that should NOT be called
        mock_fetch = Mock(side_effect=Exception("Network should not be called!"))
        
        engine = RuleEngine(cache=cache, fetch_rules_fn=mock_fetch)
        
        # Check compliance
        result = engine.check_compliance("foo")
        
        # Should return False (restricted)
        assert result is False
        
        # Network should NOT have been called
        mock_fetch.assert_not_called()
    
    def test_cache_miss_fetches_from_network(self):
        """Cache miss should trigger network fetch."""
        from services.rule_engine import RuleEngine, RuleCache
        
        cache = RuleCache()  # Empty cache
        
        mock_fetch = Mock(return_value="1. Be nice\n2. Stay on topic")
        
        engine = RuleEngine(cache=cache, fetch_rules_fn=mock_fetch)
        
        # Check compliance for uncached subreddit
        result = engine.check_compliance("newsubreddit")
        
        # Network SHOULD be called
        mock_fetch.assert_called_once_with("newsubreddit")


class TestBotBanDetection:
    """Test bot ban detection and status update."""
    
    def test_bot_ban_updates_status_to_restricted(self):
        """Mock rules 'No bots'. Assert status updates to RESTRICTED."""
        from services.rule_engine import RuleEngine, RuleCache
        
        cache = RuleCache()
        mock_fetch = Mock(return_value="1. No bots or automation\n2. Human posts only")
        
        engine = RuleEngine(cache=cache, fetch_rules_fn=mock_fetch)
        
        # Check subreddit with bot ban rules
        engine.check_compliance("strictsub")
        
        # Cache should now have RESTRICTED status
        cached = cache.get("strictsub")
        assert cached is not None
        assert cached["status"] == "RESTRICTED"
    
    def test_allowed_subreddit_caches_as_allowed(self):
        """Subreddits without restrictions should cache as ALLOWED."""
        from services.rule_engine import RuleEngine, RuleCache
        
        cache = RuleCache()
        mock_fetch = Mock(return_value="1. Be respectful\n2. Stay on topic")
        
        engine = RuleEngine(cache=cache, fetch_rules_fn=mock_fetch)
        
        engine.check_compliance("friendlysub")
        
        cached = cache.get("friendlysub")
        assert cached is not None
        assert cached["status"] == "ALLOWED"


class TestRuleParsing:
    """Test rule text parsing."""
    
    def test_parses_numbered_rules(self):
        """Parse numbered rule format."""
        from services.rule_engine import RuleEngine
        
        engine = RuleEngine()
        rules_text = """
        1. No spam
        2. Be respectful
        3. No support questions
        """
        
        parsed = engine.parse_rules(rules_text)
        assert len(parsed) >= 3
        assert any("spam" in rule.lower() for rule in parsed)
    
    def test_parses_bullet_rules(self):
        """Parse bullet point format."""
        from services.rule_engine import RuleEngine
        
        engine = RuleEngine()
        rules_text = """
        • No spam
        • Be kind
        - Stay on topic
        """
        
        parsed = engine.parse_rules(rules_text)
        assert len(parsed) >= 3


class TestCacheExpiry:
    """Test cache expiration."""
    
    def test_stale_cache_triggers_refresh(self):
        """Stale cache entries should trigger network refresh."""
        from services.rule_engine import RuleEngine, RuleCache
        
        cache = RuleCache(max_age_hours=24)
        
        # Add stale entry (25 hours old)
        cache.set(
            "oldcache",
            rules="Old rules",
            status="ALLOWED",
            timestamp=datetime.utcnow() - timedelta(hours=25)
        )
        
        mock_fetch = Mock(return_value="New rules")
        engine = RuleEngine(cache=cache, fetch_rules_fn=mock_fetch)
        
        # Check compliance - should refresh
        engine.check_compliance("oldcache")
        
        # Network should be called due to stale cache
        mock_fetch.assert_called_once()
    
    def test_fresh_cache_skips_network(self):
        """Fresh cache should not trigger network."""
        from services.rule_engine import RuleEngine, RuleCache
        
        cache = RuleCache(max_age_hours=24)
        
        # Add fresh entry (1 hour old)
        cache.set(
            "freshcache",
            rules="Fresh rules",
            status="ALLOWED",
            timestamp=datetime.utcnow() - timedelta(hours=1)
        )
        
        mock_fetch = Mock(side_effect=Exception("Should not call network"))
        engine = RuleEngine(cache=cache, fetch_rules_fn=mock_fetch)
        
        # Check compliance - should use cache
        result = engine.check_compliance("freshcache")
        
        # Network should NOT be called
        mock_fetch.assert_not_called()
        assert result is True  # ALLOWED status


class TestPoliticalKeywordFiltering:
    """Test political/controversial keyword detection."""
    
    def test_political_keywords_flagged(self):
        """Posts with political keywords should be flagged."""
        from services.rule_engine import RuleEngine
        
        engine = RuleEngine()
        
        political_titles = [
            "Biden's new policy is terrible",
            "Vote for Trump in 2024",
            "Political debate about abortion",
        ]
        
        for title in political_titles:
            assert engine.has_controversial_content(title) is True
    
    def test_neutral_content_passes(self):
        """Neutral content should not be flagged."""
        from services.rule_engine import RuleEngine
        
        engine = RuleEngine()
        
        neutral_titles = [
            "How to set up a Python virtual environment",
            "Best practices for Docker deployment",
            "Question about AWS Lambda costs",
        ]
        
        for title in neutral_titles:
            assert engine.has_controversial_content(title) is False
