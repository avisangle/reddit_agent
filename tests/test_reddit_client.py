"""
Test Reddit client with safety features (Story 2).
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
import re


class TestAuthorFiltering:
    """Test author filtering logic (AutoMod/Bot Filter)."""
    
    def test_automod_filter_excludes_automoderator(self):
        """Mock comments where author.name is 'AutoModerator'. Assert excluded."""
        from services.reddit_client import RedditClient
        
        # Create mock comment with AutoModerator as author
        mock_comment = Mock()
        mock_comment.author = Mock()
        mock_comment.author.name = "AutoModerator"
        mock_comment.author_is_bot = False
        
        client = RedditClient.__new__(RedditClient)
        assert client._should_skip_author(mock_comment) is True
    
    def test_bot_filter_excludes_bot_usernames(self):
        """Mock comments where author matches bot pattern. Assert excluded."""
        from services.reddit_client import RedditClient
        
        bot_names = ["HelperBot", "AutoAssistant", "reply_bot", "ModeratorBot"]
        client = RedditClient.__new__(RedditClient)
        
        for bot_name in bot_names:
            mock_comment = Mock()
            mock_comment.author = Mock()
            mock_comment.author.name = bot_name
            mock_comment.author_is_bot = False
            assert client._should_skip_author(mock_comment) is True, f"Should skip {bot_name}"
    
    def test_bot_flag_excludes_flagged_bots(self):
        """Mock comments where author_is_bot is True. Assert excluded."""
        from services.reddit_client import RedditClient
        
        mock_comment = Mock()
        mock_comment.author = Mock()
        mock_comment.author.name = "NormalUser"
        mock_comment.author_is_bot = True
        
        client = RedditClient.__new__(RedditClient)
        assert client._should_skip_author(mock_comment) is True
    
    def test_deleted_author_excluded(self):
        """Mock comments where author is None (deleted). Assert excluded."""
        from services.reddit_client import RedditClient
        
        mock_comment = Mock()
        mock_comment.author = None
        
        client = RedditClient.__new__(RedditClient)
        assert client._should_skip_author(mock_comment) is True
    
    def test_normal_user_not_excluded(self):
        """Normal users should not be excluded."""
        from services.reddit_client import RedditClient
        
        mock_comment = Mock()
        mock_comment.author = Mock()
        mock_comment.author.name = "RegularUser123"
        mock_comment.author_is_bot = False
        
        client = RedditClient.__new__(RedditClient)
        assert client._should_skip_author(mock_comment) is False


class TestShadowbanDetection:
    """Test shadowban detection and circuit breaker (Kill-Switch)."""
    
    def test_shadowban_killswitch_raises_exception(self):
        """Mock high shadowban risk. Assert SafetyLockoutException raised."""
        from services.reddit_client import RedditClient, SafetyLockoutException
        
        client = RedditClient.__new__(RedditClient)
        client._error_counts = {"403": 5, "empty_listing": 3}
        client._risk_threshold = 0.7
        client._total_requests = 10
        
        # Mock _calculate_shadowban_risk to return high value
        with patch.object(client, '_calculate_shadowban_risk', return_value=0.8):
            with pytest.raises(SafetyLockoutException) as exc_info:
                client._check_shadowban_risk()
            
            assert "shadowban risk" in str(exc_info.value).lower()
    
    def test_low_risk_does_not_raise(self):
        """Low shadowban risk should not raise exception."""
        from services.reddit_client import RedditClient
        
        client = RedditClient.__new__(RedditClient)
        client._error_counts = {"403": 0, "empty_listing": 1}
        client._risk_threshold = 0.7
        client._total_requests = 100
        
        with patch.object(client, '_calculate_shadowban_risk', return_value=0.1):
            # Should not raise
            client._check_shadowban_risk()
    
    def test_403_error_increments_counter(self):
        """403 errors should increment the error counter."""
        from services.reddit_client import RedditClient
        
        client = RedditClient.__new__(RedditClient)
        client._error_counts = {"403": 0, "empty_listing": 0}
        client._total_requests = 0
        
        client._record_error("403")
        assert client._error_counts["403"] == 1
    
    def test_empty_listing_detection(self):
        """Empty listing response should be tracked."""
        from services.reddit_client import RedditClient
        
        client = RedditClient.__new__(RedditClient)
        client._error_counts = {"403": 0, "empty_listing": 0}
        client._total_requests = 0
        
        client._record_error("empty_listing")
        assert client._error_counts["empty_listing"] == 1


class TestRateLimiting:
    """Test rate limit handling."""
    
    def test_rate_limit_zero_remaining_raises(self):
        """Mock X-Ratelimit-Remaining: 0. Assert RateLimitExceeded raised."""
        from services.reddit_client import RedditClient, RateLimitExceeded
        
        client = RedditClient.__new__(RedditClient)
        client._rate_limit_remaining = 0
        client._rate_limit_reset = 60
        
        with pytest.raises(RateLimitExceeded) as exc_info:
            client._check_rate_limit()
        
        assert "rate limit" in str(exc_info.value).lower()
    
    def test_positive_remaining_does_not_raise(self):
        """Positive remaining requests should not raise."""
        from services.reddit_client import RedditClient
        
        client = RedditClient.__new__(RedditClient)
        client._rate_limit_remaining = 100
        client._rate_limit_reset = 0
        
        # Should not raise
        client._check_rate_limit()


class TestSubredditFiltering:
    """Test subreddit allow-listing."""
    
    def test_allowed_subreddit_passes(self):
        """Comments from allowed subreddits should pass."""
        from services.reddit_client import RedditClient
        
        client = RedditClient.__new__(RedditClient)
        client._allowed_subreddits = ["sysadmin", "learnpython", "startups"]
        
        mock_comment = Mock()
        mock_comment.subreddit = Mock()
        mock_comment.subreddit.display_name = "sysadmin"
        
        assert client._is_allowed_subreddit(mock_comment) is True
    
    def test_disallowed_subreddit_filtered(self):
        """Comments from non-allowed subreddits should be filtered."""
        from services.reddit_client import RedditClient
        
        client = RedditClient.__new__(RedditClient)
        client._allowed_subreddits = ["sysadmin", "learnpython"]
        
        mock_comment = Mock()
        mock_comment.subreddit = Mock()
        mock_comment.subreddit.display_name = "randomsubreddit"
        
        assert client._is_allowed_subreddit(mock_comment) is False


class TestPostDiscovery:
    """Test rising post discovery."""
    
    def test_post_age_filter(self):
        """Posts older than 45 minutes should be filtered."""
        from services.reddit_client import RedditClient
        import time
        
        client = RedditClient.__new__(RedditClient)
        client._max_post_age_seconds = 45 * 60
        
        # Post created 30 minutes ago (should pass)
        recent_post = Mock()
        recent_post.created_utc = time.time() - (30 * 60)
        assert client._is_valid_post_age(recent_post) is True
        
        # Post created 60 minutes ago (should fail)
        old_post = Mock()
        old_post.created_utc = time.time() - (60 * 60)
        assert client._is_valid_post_age(old_post) is False
    
    def test_comment_count_filter(self):
        """Posts should have between 3 and 20 comments."""
        from services.reddit_client import RedditClient
        
        client = RedditClient.__new__(RedditClient)
        client._min_comments = 3
        client._max_comments = 20
        
        # Too few comments
        post_few = Mock()
        post_few.num_comments = 1
        assert client._is_valid_comment_count(post_few) is False
        
        # Just right
        post_ok = Mock()
        post_ok.num_comments = 10
        assert client._is_valid_comment_count(post_ok) is True
        
        # Too many comments
        post_many = Mock()
        post_many.num_comments = 50
        assert client._is_valid_comment_count(post_many) is False
    
    def test_locked_thread_filtered(self):
        """Locked threads should be filtered."""
        from services.reddit_client import RedditClient
        
        client = RedditClient.__new__(RedditClient)
        
        locked_post = Mock()
        locked_post.locked = True
        assert client._is_thread_available(locked_post) is False
        
        open_post = Mock()
        open_post.locked = False
        open_post.removed_by_category = None
        assert client._is_thread_available(open_post) is True
    
    def test_controversial_keyword_filter(self):
        """Posts with controversial keywords should be filtered."""
        from services.reddit_client import RedditClient
        
        client = RedditClient.__new__(RedditClient)
        
        # Post with political keyword in title
        political_post = Mock()
        political_post.id = "123"
        political_post.title = "What do you think about Trump's policies?"
        political_post.selftext = ""
        assert client._has_controversial_keywords(political_post) is True
        
        # Post with keyword in body
        body_political = Mock()
        body_political.id = "124"
        body_political.title = "A normal question"
        body_political.selftext = "This is about the election results"
        assert client._has_controversial_keywords(body_political) is True
        
        # Clean post
        clean_post = Mock()
        clean_post.id = "125"
        clean_post.title = "Best Python libraries for web scraping?"
        clean_post.selftext = "I'm looking for recommendations"
        assert client._has_controversial_keywords(clean_post) is False
    
    def test_controversial_keywords_case_insensitive(self):
        """Keyword matching should be case insensitive."""
        from services.reddit_client import RedditClient
        
        client = RedditClient.__new__(RedditClient)
        
        post = Mock()
        post.id = "126"
        post.title = "BIDEN vs TRUMP debate"
        post.selftext = ""
        assert client._has_controversial_keywords(post) is True


class TestRisingCandidates:
    """Test rising post candidate fetching."""
    
    def test_fetch_rising_candidates_combines_subreddits(self):
        """Should fetch candidates from all allowed subreddits."""
        from services.reddit_client import RedditClient
        
        client = RedditClient.__new__(RedditClient)
        client._allowed_subreddits = ["sysadmin", "learnpython"]
        client._rate_limit_remaining = 100
        client._error_counts = {"403": 0, "empty_listing": 0}
        client._total_requests = 0
        client._risk_threshold = 0.7
        
        # Mock fetch_rising_posts to return empty list
        with patch.object(client, 'fetch_rising_posts', return_value=[]):
            candidates = client.fetch_rising_candidates(limit_per_subreddit=5)
            
            # Should have called for each subreddit
            assert client.fetch_rising_posts.call_count == 2
            assert candidates == []
    
    def test_fetch_rising_candidates_filters_bots(self):
        """Bot authors should be filtered from rising candidates."""
        from services.reddit_client import RedditClient
        
        client = RedditClient.__new__(RedditClient)
        client._allowed_subreddits = ["sysadmin"]
        client._rate_limit_remaining = 100
        client._error_counts = {"403": 0, "empty_listing": 0}
        client._total_requests = 0
        client._risk_threshold = 0.7
        
        # Create mock post with bot comment
        mock_post = Mock()
        mock_post.title = "Test post"
        mock_post.id = "post1"
        mock_comment = Mock()
        mock_comment.id = "comment1"
        mock_comment.author = Mock()
        mock_comment.author.name = "AutoModerator"
        mock_comment.author_is_bot = False
        mock_comment.body = "This is a bot comment"
        mock_comment.permalink = "/r/sysadmin/comments/123"
        mock_comment.parent_id = "t3_post1"
        mock_post.comments = Mock()
        mock_post.comments.replace_more = Mock()
        mock_post.comments.__iter__ = Mock(return_value=iter([mock_comment]))
        mock_post.comments.__getitem__ = Mock(return_value=[mock_comment])
        
        with patch.object(client, 'fetch_rising_posts', return_value=[mock_post]):
            candidates = client.fetch_rising_candidates(limit_per_subreddit=5)
            
            # Bot comment should be filtered out
            assert len(candidates) == 0
