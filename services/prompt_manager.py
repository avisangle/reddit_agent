"""
Prompt management system with external templates.

Implements Story 5: Prompt & Few-Shot Management
- External YAML template loading
- Subreddit-based template selection
- PII scrubbing
- Few-shot example injection
"""
import re
import yaml
from typing import Dict, List, Optional, Any
from pathlib import Path

from utils.logging import get_logger

logger = get_logger(__name__)


class TemplateLoadError(Exception):
    """Raised when template file cannot be loaded."""
    pass


class PromptManager:
    """
    Manage prompt templates and few-shot examples.
    
    Features:
    - Load templates from external YAML
    - Select template by subreddit
    - PII scrubbing
    - Build complete prompts with context
    """
    
    # PII Patterns for comprehensive scrubbing
    PII_PATTERNS = {
        # Email addresses
        "email": re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
        
        # Phone numbers (US and international formats)
        "phone": re.compile(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'),
        
        # Social Security Numbers
        "ssn": re.compile(r'\b\d{3}-\d{2}-\d{4}\b'),
        
        # Credit card numbers (basic patterns)
        "credit_card": re.compile(r'\b(?:\d{4}[-\s]?){3}\d{4}\b'),
        
        # IP addresses (IPv4)
        "ip_address": re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b'),
        
        # URLs with potential tokens/keys
        "url_with_token": re.compile(r'https?://[^\s]*[?&](token|key|api_key|secret|password|auth)=[^\s&]+', re.IGNORECASE),
        
        # AWS access keys
        "aws_key": re.compile(r'\b(AKIA|ABIA|ACCA|ASIA)[A-Z0-9]{16}\b'),
        
        # Generic API keys (long alphanumeric strings)
        "api_key": re.compile(r'\b[A-Za-z0-9_-]{32,}\b'),
    }
    
    # Legacy patterns for backwards compatibility
    EMAIL_PATTERN = PII_PATTERNS["email"]
    PHONE_PATTERN = PII_PATTERNS["phone"]
    SSN_PATTERN = PII_PATTERNS["ssn"]
    
    def __init__(self, templates_path: Optional[str] = None):
        """
        Initialize prompt manager.
        
        Args:
            templates_path: Path to YAML templates file
            
        Raises:
            TemplateLoadError: If templates file cannot be loaded
        """
        self.templates: Dict[str, Any] = {}
        self._subreddit_map: Dict[str, str] = {}
        
        if templates_path is None:
            # Default path
            templates_path = str(Path(__file__).parent.parent / "prompts" / "templates.yaml")
        
        self._load_templates(templates_path)
    
    def _load_templates(self, path: str) -> None:
        """Load templates from YAML file."""
        try:
            with open(path, 'r') as f:
                self.templates = yaml.safe_load(f) or {}
            
            # Build subreddit -> template mapping
            for template_name, template in self.templates.items():
                subreddits = template.get('subreddits', [])
                for sub in subreddits:
                    self._subreddit_map[sub.lower()] = template_name
            
            logger.info(
                "templates_loaded",
                count=len(self.templates),
                path=path
            )
            
        except FileNotFoundError:
            logger.error("templates_file_not_found", path=path)
            raise TemplateLoadError(f"Templates file not found: {path}")
        except yaml.YAMLError as e:
            logger.error("templates_parse_error", path=path, error=str(e))
            raise TemplateLoadError(f"Failed to parse templates: {e}")
    
    def get_template_for_subreddit(self, subreddit: str) -> Dict[str, Any]:
        """
        Get the appropriate template for a subreddit.
        
        Args:
            subreddit: Subreddit name
            
        Returns:
            Template dict with system_prompt, few_shot_examples, etc.
        """
        subreddit = subreddit.lower().replace('r/', '')
        
        # Look up in mapping
        template_name = self._subreddit_map.get(subreddit)
        
        if template_name and template_name in self.templates:
            logger.debug("template_found", subreddit=subreddit, template=template_name)
            return self.templates[template_name]
        
        # Fallback to default
        if 'default' in self.templates:
            logger.debug("using_default_template", subreddit=subreddit)
            return self.templates['default']
        
        # Return first template if no default
        if self.templates:
            first_template = next(iter(self.templates.values()))
            logger.debug("using_first_template", subreddit=subreddit)
            return first_template
        
        # Empty fallback
        return {
            "system_prompt": "You are a helpful Reddit user.",
            "few_shot_examples": []
        }
    
    def scrub_pii(self, text: str) -> str:
        """
        Remove personally identifiable information from text.
        
        Scrubs:
        - Email addresses
        - Phone numbers
        - Social Security Numbers
        - Credit card numbers
        - IP addresses
        - URLs with tokens/keys
        - AWS access keys
        - Generic API keys
        
        Args:
            text: Input text
            
        Returns:
            Text with PII redacted
        """
        redaction_count = 0
        
        for pii_type, pattern in self.PII_PATTERNS.items():
            matches = pattern.findall(text)
            if matches:
                redaction_count += len(matches)
                text = pattern.sub(f'[REDACTED_{pii_type.upper()}]', text)
        
        if redaction_count > 0:
            logger.debug("pii_scrubbed", count=redaction_count)
        
        return text
    
    def build_prompt(
        self,
        subreddit: str,
        context: str,
        max_examples: int = 3
    ) -> str:
        """
        Build a complete prompt for the LLM.
        
        Args:
            subreddit: Target subreddit
            context: Conversation context from ContextBuilder
            max_examples: Maximum few-shot examples to include
            
        Returns:
            Complete prompt string
        """
        template = self.get_template_for_subreddit(subreddit)
        
        # Scrub PII from context
        clean_context = self.scrub_pii(context)
        
        # Build prompt parts
        parts = []
        
        # System prompt
        system_prompt = template.get('system_prompt', 'You are a helpful Reddit user.')
        parts.append(f"### Instructions\n{system_prompt}")
        
        # Few-shot examples
        examples = template.get('few_shot_examples', [])[:max_examples]
        if examples:
            parts.append("\n### Example Replies (match this tone)")
            for i, example in enumerate(examples, 1):
                parts.append(f"{i}. {example}")
        
        # Guidelines
        parts.append("\n### Guidelines")
        parts.append("- Write a reply in a similar tone and style to the examples above")
        parts.append("- Do not copy content, only match tone and structure")
        parts.append("- Be helpful and genuine, like a real Reddit user")
        parts.append("- Avoid formal language and AI-like phrases")
        parts.append("- Keep it concise but helpful")
        
        # Context
        parts.append(f"\n### Conversation Context\n{clean_context}")
        
        # Request
        parts.append("\n### Your Reply")
        parts.append("Write a helpful, natural reply to the target comment:")
        
        prompt = "\n".join(parts)
        
        logger.info(
            "prompt_built",
            subreddit=subreddit,
            prompt_length=len(prompt),
            examples_used=len(examples)
        )
        
        return prompt
    
    def get_system_message(self, subreddit: str, is_post_reply: bool = False) -> str:
        """
        Get the system prompt for a subreddit.
        
        Args:
            subreddit: Target subreddit
            is_post_reply: True if replying directly to a post
            
        Returns:
            System prompt string
        """
        template = self.get_template_for_subreddit(subreddit)
        
        if is_post_reply:
            # Use post-specific prompt if available, else fall back to default
            return template.get('post_reply_prompt', template.get('system_prompt', 'You are a helpful Reddit user.'))
        
        return template.get('system_prompt', 'You are a helpful Reddit user.')
    
    def get_few_shot_examples(self, subreddit: str, max_examples: int = 3) -> List[str]:
        """Get few-shot examples for a subreddit."""
        template = self.get_template_for_subreddit(subreddit)
        return template.get('few_shot_examples', [])[:max_examples]
