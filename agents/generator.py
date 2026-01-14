"""
LLM draft generator with content filtering.

Implements Story 6: The Generator (LLM)
- Generate draft replies using LLM
- Banned phrase detection
- Content length validation
- Retry logic
"""
import re
import uuid
from typing import List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime

from utils.logging import get_logger

logger = get_logger(__name__)


class ContentFilterError(Exception):
    """Raised when generated content fails validation."""
    pass


@dataclass
class Draft:
    """A generated draft reply."""
    draft_id: str
    reddit_id: str
    subreddit: str
    content: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def __post_init__(self):
        if not self.draft_id:
            self.draft_id = str(uuid.uuid4())


class DraftGenerator:
    """
    Generate draft replies using LLM.
    
    Features:
    - Content generation with context
    - Banned phrase filtering
    - Length validation
    - Retry on filter failure
    """
    
    # Banned phrases that indicate AI-generated content
    BANNED_PHRASES = [
        r"as an ai\b",
        r"as a language model",
        r"i'm an ai",
        r"i am an ai",
        r"it'?s important to note that",
        r"in summary,",
        r"in conclusion,",
        r"based on my experience,",
        r"i don'?t have personal",
        r"i cannot provide",
        r"as an assistant",
        r"i hope this helps!$",
        r"feel free to ask",
        r"let me know if you",
        r"i'd be happy to",
    ]
    
    # Compiled patterns
    BANNED_PATTERNS = [re.compile(p, re.IGNORECASE) for p in BANNED_PHRASES]
    
    def __init__(
        self,
        llm: Optional[Any] = None,
        min_length: int = 20,
        max_length: int = 2000,
        max_retries: int = 3
    ):
        """
        Initialize draft generator.
        
        Args:
            llm: LangChain LLM instance
            min_length: Minimum content length
            max_length: Maximum content length
            max_retries: Max retries on filter failure
        """
        self.llm = llm
        self.min_length = min_length
        self.max_length = max_length
        self.max_retries = max_retries
        
        logger.debug(
            "generator_initialized",
            min_length=min_length,
            max_length=max_length,
            max_retries=max_retries
        )
    
    def generate(
        self,
        context: str,
        system_prompt: str,
        few_shot_examples: List[str],
        subreddit: str,
        reddit_id: str
    ) -> Draft:
        """
        Generate a draft reply.
        
        Args:
            context: Conversation context
            system_prompt: System instructions
            few_shot_examples: Example replies for style
            subreddit: Target subreddit
            reddit_id: Reddit ID of item being replied to
            
        Returns:
            Draft object with generated content
            
        Raises:
            ContentFilterError: If content fails validation after retries
        """
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                # Build messages for LLM
                messages = self._build_messages(
                    context=context,
                    system_prompt=system_prompt,
                    few_shot_examples=few_shot_examples
                )
                
                # Call LLM
                response = self.llm.invoke(messages)
                content = response.content.strip()
                
                # Validate content
                self._validate_content(content)
                
                # Create draft
                draft = Draft(
                    draft_id=str(uuid.uuid4()),
                    reddit_id=reddit_id,
                    subreddit=subreddit,
                    content=content
                )
                
                logger.info(
                    "draft_generated",
                    reddit_id=reddit_id,
                    subreddit=subreddit,
                    content_length=len(content),
                    attempt=attempt + 1
                )
                
                return draft
                
            except ContentFilterError as e:
                last_error = e
                logger.warning(
                    "content_filter_failed",
                    reddit_id=reddit_id,
                    attempt=attempt + 1,
                    error=str(e)
                )
                continue
        
        # All retries failed
        raise ContentFilterError(
            f"Content generation failed after {self.max_retries} attempts: {last_error}"
        )
    
    def _build_messages(
        self,
        context: str,
        system_prompt: str,
        few_shot_examples: List[str]
    ) -> List[dict]:
        """Build message list for LLM."""
        messages = []
        
        # System message
        system_content = f"{system_prompt}\n\n"
        
        if few_shot_examples:
            system_content += "Example replies (match this tone and style):\n"
            for i, example in enumerate(few_shot_examples, 1):
                system_content += f"{i}. {example}\n"
        
        system_content += """
Guidelines:
- Write a natural, helpful reply
- Match the tone and style of the examples
- Avoid formal language and AI-like phrases
- Be concise but helpful
- Do not include phrases like "As an AI" or "In summary"
"""
        
        messages.append({
            "role": "system",
            "content": system_content
        })
        
        # User message with context
        user_content = f"""Write a reply to the following Reddit conversation:

{context}

Your reply:"""
        
        messages.append({
            "role": "user",
            "content": user_content
        })
        
        return messages
    
    def _validate_content(self, content: str) -> None:
        """
        Validate generated content.
        
        Raises:
            ContentFilterError: If content fails validation
        """
        # Check length
        if len(content) < self.min_length:
            raise ContentFilterError(f"Content too short ({len(content)} < {self.min_length})")
        
        if len(content) > self.max_length:
            raise ContentFilterError(f"Content too long ({len(content)} > {self.max_length})")
        
        # Check banned phrases
        for pattern in self.BANNED_PATTERNS:
            if pattern.search(content):
                raise ContentFilterError(f"Content contains banned phrase matching: {pattern.pattern}")
        
        # Check for empty or whitespace-only
        if not content.strip():
            raise ContentFilterError("Content is empty or whitespace-only")
        
        logger.debug("content_validated", length=len(content))
    
    def validate_content(self, content: str) -> bool:
        """
        Check if content passes validation.
        
        Args:
            content: Content to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            self._validate_content(content)
            return True
        except ContentFilterError:
            return False
