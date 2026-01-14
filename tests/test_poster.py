"""
Tests for the comment poster service.
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime


class TestCommentPoster:
    """Test comment poster functionality."""
    
    def test_publish_single_success(self):
        """Successfully publish a single draft."""
        from services.poster import CommentPoster, PublishResult
        
        # Mock dependencies
        mock_reddit = Mock()
        mock_reddit.reddit = Mock()
        mock_reddit.reddit.comment = Mock(return_value=Mock())
        mock_reddit.post_comment = Mock(return_value="comment123")
        
        mock_state = Mock()
        mock_state.can_post_today = Mock(return_value=True)
        mock_state.update_draft_status = Mock(return_value=True)
        mock_state.mark_replied = Mock()
        mock_state.increment_daily_count = Mock()
        
        # Create poster
        poster = CommentPoster(
            reddit_client=mock_reddit,
            state_manager=mock_state,
            dry_run=False
        )
        
        # Mock draft
        draft = Mock()
        draft.draft_id = "draft1"
        draft.reddit_id = "t1_abc123"
        draft.content = "Test reply"
        draft.subreddit = "sysadmin"
        
        result = poster.publish_single(draft)
        
        assert result.success is True
        assert result.comment_id == "comment123"
        mock_state.update_draft_status.assert_called_with("draft1", "PUBLISHED")
        mock_state.mark_replied.assert_called_with("t1_abc123", "sysadmin", "SUCCESS")
        mock_state.increment_daily_count.assert_called_once()
    
    def test_publish_blocked_by_daily_limit(self):
        """Publish should be blocked when daily limit reached."""
        from services.poster import CommentPoster
        
        mock_reddit = Mock()
        mock_state = Mock()
        mock_state.can_post_today = Mock(return_value=False)
        
        poster = CommentPoster(
            reddit_client=mock_reddit,
            state_manager=mock_state
        )
        
        draft = Mock()
        draft.draft_id = "draft1"
        draft.reddit_id = "t1_abc123"
        
        result = poster.publish_single(draft)
        
        assert result.success is False
        assert "Daily limit" in result.error
    
    def test_publish_dry_run_does_not_post(self):
        """Dry run should not actually post."""
        from services.poster import CommentPoster
        
        mock_reddit = Mock()
        mock_reddit.reddit = Mock()
        mock_reddit.reddit.comment = Mock(return_value=Mock())
        mock_reddit.post_comment = Mock(return_value=None)  # Returns None in dry run
        
        mock_state = Mock()
        mock_state.can_post_today = Mock(return_value=True)
        mock_state.update_draft_status = Mock()
        mock_state.mark_replied = Mock()
        mock_state.increment_daily_count = Mock()
        
        poster = CommentPoster(
            reddit_client=mock_reddit,
            state_manager=mock_state,
            dry_run=True
        )
        
        draft = Mock()
        draft.draft_id = "draft1"
        draft.reddit_id = "t1_abc123"
        draft.content = "Test"
        draft.subreddit = "test"
        
        result = poster.publish_single(draft)
        
        assert result.success is True
        # Should not increment daily count in dry run
        mock_state.increment_daily_count.assert_not_called()
    
    def test_publish_approved_respects_limit(self):
        """Should only publish up to the limit."""
        from services.poster import CommentPoster
        
        mock_reddit = Mock()
        mock_reddit.reddit = Mock()
        mock_reddit.reddit.comment = Mock(return_value=Mock())
        mock_reddit.post_comment = Mock(return_value="comment123")
        
        mock_state = Mock()
        mock_state.can_post_today = Mock(return_value=True)
        mock_state.get_approved_drafts = Mock(return_value=[Mock(
            draft_id=f"draft{i}",
            reddit_id=f"t1_abc{i}",
            content="Test",
            subreddit="test"
        ) for i in range(5)])
        mock_state.update_draft_status = Mock()
        mock_state.mark_replied = Mock()
        mock_state.increment_daily_count = Mock()
        
        poster = CommentPoster(
            reddit_client=mock_reddit,
            state_manager=mock_state,
            dry_run=True  # Use dry run to avoid jitter sleep
        )
        
        results = poster.publish_approved(limit=3)
        
        # Should request only 3
        mock_state.get_approved_drafts.assert_called_with(limit=3)
    
    def test_publish_handles_error_gracefully(self):
        """Errors should be caught and marked as failed."""
        from services.poster import CommentPoster
        
        mock_reddit = Mock()
        mock_reddit.reddit = Mock()
        mock_reddit.reddit.comment = Mock(side_effect=Exception("API Error"))
        
        mock_state = Mock()
        mock_state.can_post_today = Mock(return_value=True)
        mock_state.mark_replied = Mock()
        
        poster = CommentPoster(
            reddit_client=mock_reddit,
            state_manager=mock_state
        )
        
        draft = Mock()
        draft.draft_id = "draft1"
        draft.reddit_id = "t1_abc123"
        draft.content = "Test"
        draft.subreddit = "test"
        
        result = poster.publish_single(draft)
        
        assert result.success is False
        assert "API Error" in result.error
        mock_state.mark_replied.assert_called_with("t1_abc123", "test", "FAILED")
    
    def test_jitter_applied_between_posts(self):
        """Jitter should be applied between posts (not in dry run)."""
        from services.poster import CommentPoster
        
        poster = CommentPoster(
            reddit_client=Mock(),
            state_manager=Mock(),
            min_jitter=30,
            max_jitter=120
        )
        
        jitter = poster._get_jitter()
        
        assert 30 <= jitter <= 120
    
    def test_fetch_parent_handles_prefixes(self):
        """Should handle different Reddit ID prefixes."""
        from services.poster import CommentPoster
        
        mock_reddit = Mock()
        mock_reddit.reddit = Mock()
        mock_reddit.reddit.comment = Mock(return_value=Mock())
        mock_reddit.reddit.submission = Mock(return_value=Mock())
        
        poster = CommentPoster(
            reddit_client=mock_reddit,
            state_manager=Mock()
        )
        
        # Comment prefix
        poster._fetch_parent_comment("t1_abc123")
        mock_reddit.reddit.comment.assert_called_with("abc123")
        
        # Submission prefix
        poster._fetch_parent_comment("t3_xyz789")
        mock_reddit.reddit.submission.assert_called_with("xyz789")
        
        # No prefix (assume comment)
        poster._fetch_parent_comment("def456")
        mock_reddit.reddit.comment.assert_called_with("def456")
