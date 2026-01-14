"""
Configuration management with validation for Reddit Comment Engagement Agent.
"""
import re
from pathlib import Path
from typing import List
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Get the directory where this config file lives (project root)
PROJECT_ROOT = Path(__file__).parent.resolve()
ENV_FILE = PROJECT_ROOT / ".env"


class Settings(BaseSettings):
    """Application settings with validation."""
    
    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),  # Use absolute path to .env
        env_file_encoding='utf-8',
        case_sensitive=False,
        extra='ignore'  # Ignore extra env vars not defined in model
    )
    
    # Reddit API
    reddit_client_id: str
    reddit_client_secret: str
    reddit_username: str
    reddit_password: str
    reddit_user_agent: str
    
    # Allowed subreddits
    allowed_subreddits: str = Field(
        description="Comma-separated list of allowed subreddits"
    )
    
    # LLM API (at least one required)
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None
    gemini_api_key: str | None = None
    
    # Notification settings
    notification_type: str = "webhook"  # webhook, telegram, slack
    webhook_url: str = ""
    webhook_secret: str = ""
    public_url: str = "http://localhost:8000"  # Base URL for callbacks
    
    # Telegram settings
    telegram_bot_token: str | None = None
    telegram_chat_id: str | None = None
    
    # Slack settings
    slack_webhook_url: str | None = None
    slack_channel: str | None = None
    slack_signing_secret: str | None = None  # For validating Slack button callbacks
    
    # Database
    database_url: str = "sqlite:///./reddit_agent.db"
    
    # Safety limits
    max_comments_per_day: int = 8
    max_comments_per_run: int = 3
    shadowban_risk_threshold: float = 0.7
    cooldown_period_hours: int = 24
    
    # Reply distribution
    post_reply_ratio: float = 0.3  # 30% posts, 70% comments
    max_post_replies_per_run: int = 1  # Max post replies per run
    max_comment_replies_per_run: int = 2  # Max comment replies per run
    one_comment_per_post: bool = True  # Select only one comment per post for diversity
    
    # Timing
    min_jitter_seconds: int = 900  # 15 minutes
    max_jitter_seconds: int = 3600  # 60 minutes
    
    # Token limits
    max_context_tokens: int = 2000
    
    # Mode
    dry_run: bool = False
    
    @field_validator('reddit_user_agent')
    @classmethod
    def validate_user_agent(cls, v: str) -> str:
        """Validate Reddit user agent format."""
        # Must match: android:com.{name}.{app}:v{version} (by /u/{username})
        pattern = r'^android:com\.\w+\.\w+:v\d+\.\d+.*\(by /u/\w+\)$'
        if not re.match(pattern, v):
            raise ValueError(
                "User agent must match format: "
                "android:com.yourname.appname:v2.1 (by /u/YourUsername)"
            )
        return v
    
    @field_validator('allowed_subreddits')
    @classmethod
    def validate_subreddits(cls, v: str) -> str:
        """Validate subreddits list is not empty."""
        subreddits = [s.strip() for s in v.split(',') if s.strip()]
        if not subreddits:
            raise ValueError("At least one allowed subreddit must be specified")
        return v
    
    @field_validator('openai_api_key', 'anthropic_api_key')
    @classmethod
    def validate_llm_api_key(cls, v: str | None, info) -> str | None:
        """Ensure at least one LLM API key is provided."""
        # This is checked in get_settings()
        return v
    
    @field_validator('post_reply_ratio')
    @classmethod
    def validate_post_reply_ratio(cls, v: float) -> float:
        """Validate post reply ratio is between 0 and 1."""
        if not 0.0 <= v <= 1.0:
            raise ValueError("post_reply_ratio must be between 0.0 and 1.0")
        return v
    
    @property
    def subreddits_list(self) -> List[str]:
        """Get allowed subreddits as a list."""
        return [s.strip() for s in self.allowed_subreddits.split(',') if s.strip()]
    
    @property
    def has_openai(self) -> bool:
        """Check if OpenAI API key is configured."""
        return self.openai_api_key is not None and len(self.openai_api_key) > 0
    
    @property
    def has_anthropic(self) -> bool:
        """Check if Anthropic API key is configured."""
        return self.anthropic_api_key is not None and len(self.anthropic_api_key) > 0
    
    @property
    def has_gemini(self) -> bool:
        """Check if Gemini API key is configured."""
        return self.gemini_api_key is not None and len(self.gemini_api_key) > 0


# Global settings instance
_settings: Settings | None = None


def get_settings() -> Settings:
    """Get or create settings instance."""
    global _settings
    
    if _settings is None:
        _settings = Settings()
        
        # Validate at least one LLM key is present
        if not (_settings.has_openai or _settings.has_anthropic or _settings.has_gemini):
            raise ValueError(
                "At least one LLM API key must be configured "
                "(OPENAI_API_KEY, ANTHROPIC_API_KEY, or GEMINI_API_KEY)"
            )
    
    return _settings


# Export for convenience
__all__ = ['Settings', 'get_settings']
