"""
Vertical context builder for conversation chains.

Implements Story 3: The Vertical Context Builder
- Loads vertical chain only (no siblings)
- Truncates oldest content when exceeding token limit
- Preserves target comment always
"""
from typing import List, Any, Optional
from dataclasses import dataclass

from utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class ContextSection:
    """A section of context with priority for truncation."""
    label: str
    content: str
    priority: int  # Higher = more important, less likely to truncate
    char_count: int = 0
    
    def __post_init__(self):
        self.char_count = len(self.content)


class ContextBuilder:
    """
    Build vertical conversation context for LLM prompts.
    
    Context order (oldest to newest):
    1. Post title and body
    2. Grandparent comment (if exists)
    3. Parent comment
    4. Target comment being replied to
    
    Rules:
    - Never load full threads
    - Exclude sibling comments
    - Truncate oldest content first if exceeds max_tokens
    """
    
    def __init__(self, max_tokens: int = 2000):
        """
        Initialize context builder.
        
        Args:
            max_tokens: Maximum character count for context
                       (approximated as chars, not actual tokens)
        """
        self.max_tokens = max_tokens
        logger.debug("context_builder_initialized", max_tokens=max_tokens)
    
    def build_context(
        self,
        post: Any,
        target_comment: Any = None,
        parent_chain: List[Any] = None,
        include_author: bool = True,
        is_post_reply: bool = False
    ) -> str:
        """
        Build vertical context string.
        
        Args:
            post: Post/submission object (with title and selftext)
            target_comment: The comment being replied to (None if replying to post)
            parent_chain: List of comments from oldest to target (empty if replying to post)
            include_author: Whether to include author names
            is_post_reply: True if replying directly to a post
            
        Returns:
            Formatted context string
        """
        sections = []
        parent_chain = parent_chain or []
        
        # 1. Post title (highest priority)
        post_title = getattr(post, 'title', '') or ''
        if post_title:
            sections.append(ContextSection(
                label="Post Title",
                content=post_title,
                priority=80  # High priority, keep title
            ))
        
        # 2. Post body (lower priority, truncate first if needed)
        post_body = getattr(post, 'selftext', '') or ''
        if post_body and post_body.strip():
            sections.append(ContextSection(
                label="Post Body",
                content=post_body,
                priority=20  # Low priority, truncate first
            ))
        
        if is_post_reply:
            # For post replies, add a marker indicating direct reply to post
            sections.append(ContextSection(
                label="Instructions",
                content="You are replying directly to this post. Address the main topic and add value with insights, questions, or relevant experience.",
                priority=90
            ))
        else:
            # 3. Parent chain (excluding target, ascending priority)
            if parent_chain:
                # Calculate priority step for parent chain
                chain_length = len(parent_chain)
                
                for i, comment in enumerate(parent_chain[:-1]):  # Exclude last (target)
                    body = getattr(comment, 'body', '') or ''
                    if not body or body == '[deleted]':
                        body = '[deleted]'
                    
                    author = self._get_author_name(comment)
                    
                    # Priority increases as we get closer to target
                    # First parent: 30, second: 50, etc.
                    priority = 30 + (i * 20)
                    
                    label = f"Comment by {author}" if include_author and author else "Comment"
                    
                    sections.append(ContextSection(
                        label=label,
                        content=body,
                        priority=priority
                    ))
            
            # 4. Target comment (highest priority, never truncate)
            if target_comment:
                target_body = getattr(target_comment, 'body', '') or ''
                target_author = self._get_author_name(target_comment)
                
                target_label = f"Reply from {target_author}" if include_author and target_author else "Target Comment"
                
                sections.append(ContextSection(
                    label=target_label,
                    content=target_body,
                    priority=100  # Maximum priority, never truncate
                ))
        
        # Apply truncation if needed
        sections = self._truncate_to_fit(sections)
        
        # Format output
        context = self._format_sections(sections)
        
        logger.info(
            "context_built",
            sections=len(sections),
            total_chars=len(context),
            max_tokens=self.max_tokens
        )
        
        return context
    
    def _get_author_name(self, comment: Any) -> Optional[str]:
        """Extract author name from comment safely."""
        author = getattr(comment, 'author', None)
        if author is None:
            return None
        return getattr(author, 'name', None)
    
    def _truncate_to_fit(self, sections: List[ContextSection]) -> List[ContextSection]:
        """
        Truncate sections to fit within max_tokens.
        
        Strategy:
        - Sort by priority (ascending)
        - Truncate lowest priority first
        - Never truncate target comment
        """
        total_chars = sum(s.char_count for s in sections)
        
        if total_chars <= self.max_tokens:
            return sections
        
        # Sort by priority (lowest first for truncation)
        sections_sorted = sorted(sections, key=lambda s: s.priority)
        
        # Calculate overhead from labels (approx 20 chars per section)
        label_overhead = len(sections) * 25
        available = self.max_tokens - label_overhead
        
        # Reserve space for target (highest priority)
        target_section = sections_sorted[-1]  # Highest priority
        available -= target_section.char_count
        
        # Allocate remaining space to other sections
        truncated = []
        remaining = available
        
        for section in sections_sorted[:-1]:  # Exclude target
            if remaining <= 0:
                # Skip this section entirely
                logger.debug("section_truncated_fully", label=section.label)
                continue
            
            if section.char_count <= remaining:
                # Keep entire section
                truncated.append(section)
                remaining -= section.char_count
            else:
                # Truncate section
                truncated_content = section.content[:remaining] + "..."
                truncated.append(ContextSection(
                    label=section.label,
                    content=truncated_content,
                    priority=section.priority
                ))
                remaining = 0
                logger.debug(
                    "section_truncated",
                    label=section.label,
                    original=section.char_count,
                    truncated=len(truncated_content)
                )
        
        # Add target back and sort by priority for output
        truncated.append(target_section)
        truncated.sort(key=lambda s: s.priority)
        
        return truncated
    
    def _format_sections(self, sections: List[ContextSection]) -> str:
        """Format sections into final context string."""
        lines = []
        
        for section in sections:
            lines.append(f"[{section.label}]")
            lines.append(section.content)
            lines.append("")  # Blank line between sections
        
        return "\n".join(lines).strip()
    
    def build_simple_context(
        self,
        post_title: str,
        post_body: str,
        parent_comment: Optional[str],
        target_comment: str
    ) -> str:
        """
        Build context from simple strings (for testing).
        
        Args:
            post_title: Title of the post
            post_body: Body of the post
            parent_comment: Optional parent comment text
            target_comment: Target comment being replied to
            
        Returns:
            Formatted context string
        """
        sections = []
        
        if post_title:
            sections.append(ContextSection(
                label="Post Title",
                content=post_title,
                priority=80
            ))
        
        if post_body:
            sections.append(ContextSection(
                label="Post Body",
                content=post_body,
                priority=20
            ))
        
        if parent_comment:
            sections.append(ContextSection(
                label="Parent Comment",
                content=parent_comment,
                priority=50
            ))
        
        sections.append(ContextSection(
            label="Target Comment",
            content=target_comment,
            priority=100
        ))
        
        sections = self._truncate_to_fit(sections)
        return self._format_sections(sections)
