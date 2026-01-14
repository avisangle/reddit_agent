"""
Test vertical context builder (Story 3).
"""
import pytest
from unittest.mock import Mock, MagicMock


class TestVerticalChain:
    """Test vertical context chain building."""
    
    def test_vertical_chain_order(self):
        """Mock thread: Root -> A -> B -> C (Target). Assert output contains [Root]...[A]...[B]...[C]."""
        from services.context_builder import ContextBuilder
        
        # Create mock comment chain
        root_post = Mock()
        root_post.title = "Root Post Title"
        root_post.selftext = "Root post body content"
        root_post.id = "root123"
        
        comment_a = Mock()
        comment_a.body = "Comment A content"
        comment_a.id = "a123"
        comment_a.parent_id = "t3_root123"  # t3_ = post
        
        comment_b = Mock()
        comment_b.body = "Comment B content"
        comment_b.id = "b123"
        comment_b.parent_id = "t1_a123"  # t1_ = comment
        
        comment_c = Mock()  # Target
        comment_c.body = "Comment C content (target)"
        comment_c.id = "c123"
        comment_c.parent_id = "t1_b123"
        
        builder = ContextBuilder()
        context = builder.build_context(
            post=root_post,
            target_comment=comment_c,
            parent_chain=[comment_a, comment_b, comment_c]
        )
        
        # Verify order: Root -> A -> B -> C
        assert "Root Post Title" in context
        assert "Root post body content" in context
        assert "Comment A content" in context
        assert "Comment B content" in context
        assert "Comment C content (target)" in context
        
        # Verify correct order by checking positions
        pos_root = context.find("Root Post Title")
        pos_a = context.find("Comment A content")
        pos_b = context.find("Comment B content")
        pos_c = context.find("Comment C content")
        
        assert pos_root < pos_a < pos_b < pos_c


class TestSiblingExclusion:
    """Test sibling comment exclusion."""
    
    def test_siblings_not_included(self):
        """Ensure siblings of A and B are NOT included."""
        from services.context_builder import ContextBuilder
        
        root_post = Mock()
        root_post.title = "Post Title"
        root_post.selftext = "Post body"
        
        # Parent comment
        parent = Mock()
        parent.body = "Parent comment"
        parent.id = "parent123"
        
        # Target comment (child of parent)
        target = Mock()
        target.body = "Target comment"
        target.id = "target123"
        target.parent_id = "t1_parent123"
        
        # Sibling of target (should NOT be included)
        sibling = Mock()
        sibling.body = "Sibling comment SHOULD NOT APPEAR"
        sibling.id = "sibling123"
        sibling.parent_id = "t1_parent123"
        
        builder = ContextBuilder()
        context = builder.build_context(
            post=root_post,
            target_comment=target,
            parent_chain=[parent, target]
        )
        
        # Sibling should NOT be in context
        assert "Sibling comment SHOULD NOT APPEAR" not in context
        
        # Parent and target should be present
        assert "Parent comment" in context
        assert "Target comment" in context


class TestTokenLimit:
    """Test token limit truncation."""
    
    def test_truncates_oldest_content(self):
        """Assert string truncates oldest content (Root Body) if total length > MAX_TOKENS."""
        from services.context_builder import ContextBuilder
        
        # Create very long post body
        long_body = "A" * 5000  # Very long body
        
        root_post = Mock()
        root_post.title = "Short Title"
        root_post.selftext = long_body
        
        target = Mock()
        target.body = "Target comment that should be preserved"
        target.id = "target123"
        target.author = None
        
        builder = ContextBuilder(max_tokens=500)
        context = builder.build_context(
            post=root_post,
            target_comment=target,
            parent_chain=[target]
        )
        
        # Context should be significantly reduced from original 5000+ chars
        assert len(context) < 1000
        
        # Target should still be present (most important)
        assert "Target comment that should be preserved" in context
    
    def test_preserves_target_comment(self):
        """Target comment should always be preserved even with truncation."""
        from services.context_builder import ContextBuilder
        
        root_post = Mock()
        root_post.title = "X" * 500
        root_post.selftext = "Y" * 500
        
        parent = Mock()
        parent.body = "Z" * 500
        parent.id = "p123"
        
        target = Mock()
        target.body = "CRITICAL_TARGET_CONTENT"
        target.id = "t123"
        
        builder = ContextBuilder(max_tokens=200)
        context = builder.build_context(
            post=root_post,
            target_comment=target,
            parent_chain=[parent, target]
        )
        
        # Target must be preserved
        assert "CRITICAL_TARGET_CONTENT" in context


class TestContextFormat:
    """Test context output format."""
    
    def test_context_format_structure(self):
        """Verify context has proper structure with labels."""
        from services.context_builder import ContextBuilder
        
        root_post = Mock()
        root_post.title = "Test Title"
        root_post.selftext = "Test body"
        
        parent = Mock()
        parent.body = "Parent text"
        parent.id = "p1"
        parent.author = Mock()
        parent.author.name = "ParentUser"
        
        target = Mock()
        target.body = "Target text"
        target.id = "t1"
        target.author = Mock()
        target.author.name = "TargetUser"
        
        builder = ContextBuilder()
        context = builder.build_context(
            post=root_post,
            target_comment=target,
            parent_chain=[parent, target]
        )
        
        # Should have structural indicators
        assert "[Post Title]" in context or "Post:" in context
        assert "Test Title" in context
        assert "Parent text" in context
        assert "Target text" in context


class TestEmptyHandling:
    """Test handling of empty/missing content."""
    
    def test_handles_empty_post_body(self):
        """Posts with no body (link posts) should be handled."""
        from services.context_builder import ContextBuilder
        
        root_post = Mock()
        root_post.title = "Link Post Title"
        root_post.selftext = ""  # Empty for link posts
        
        target = Mock()
        target.body = "Comment on link post"
        target.id = "t1"
        
        builder = ContextBuilder()
        context = builder.build_context(
            post=root_post,
            target_comment=target,
            parent_chain=[target]
        )
        
        assert "Link Post Title" in context
        assert "Comment on link post" in context
    
    def test_handles_deleted_parent_comment(self):
        """Deleted parent comments should show placeholder."""
        from services.context_builder import ContextBuilder
        
        root_post = Mock()
        root_post.title = "Title"
        root_post.selftext = "Body"
        
        deleted_parent = Mock()
        deleted_parent.body = "[deleted]"
        deleted_parent.id = "d1"
        deleted_parent.author = None
        
        target = Mock()
        target.body = "Reply to deleted"
        target.id = "t1"
        
        builder = ContextBuilder()
        context = builder.build_context(
            post=root_post,
            target_comment=target,
            parent_chain=[deleted_parent, target]
        )
        
        # Should handle gracefully
        assert "Reply to deleted" in context
