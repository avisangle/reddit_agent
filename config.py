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

    # Quality Scoring System
    quality_scoring_enabled: bool = True

    # Score Weights (must sum to 1.0, will be normalized)
    score_weight_upvote: float = 0.15
    score_weight_karma: float = 0.10
    score_weight_freshness: float = 0.20
    score_weight_velocity: float = 0.15
    score_weight_question: float = 0.15
    score_weight_depth: float = 0.10
    score_weight_historical: float = 0.15

    # Minimum Score Thresholds
    score_minimum_threshold: float = 0.35
    score_minimum_for_post: float = 0.40

    # Upvote Ratio Thresholds
    score_upvote_excellent: float = 0.90
    score_upvote_good: float = 0.75
    score_upvote_mixed: float = 0.60

    # Author Karma Thresholds
    score_karma_established: int = 10000
    score_karma_active: int = 1000
    score_karma_regular: int = 100

    # Thread Freshness Thresholds (seconds)
    score_freshness_hot: int = 900  # 15 min
    score_freshness_active: int = 1800  # 30 min
    score_freshness_warm: int = 3600  # 60 min
    score_freshness_cooling: int = 7200  # 120 min

    # Engagement Velocity Thresholds (comments/minute)
    score_velocity_viral: float = 1.0
    score_velocity_high: float = 0.5
    score_velocity_moderate: float = 0.2
    score_velocity_low: float = 0.1

    # Thread Depth Thresholds
    score_depth_ideal_min: int = 5
    score_depth_ideal_max: int = 15
    score_depth_early_min: int = 3
    score_depth_crowded_max: int = 30

    # Question Signal Keywords (comma-separated)
    score_help_keywords: str = "how do I,help,advice,recommend,suggest,anyone know"
    score_problem_keywords: str = "issue,problem,error,stuck,struggling,trouble"

    # Exploration vs Exploitation
    score_exploration_rate: float = 0.25  # 25% random selection (Phase B: increased for variety)
    score_top_n_random: int = 5  # Randomize top 5 (Phase B: increased from 3)

    # Historical Learning System (Phase 3)
    learning_enabled: bool = True  # Enable historical learning
    learning_min_samples: int = 5  # Minimum samples before using historical score
    learning_decay_recent_days: int = 7  # Recent data (weight 1.0)
    learning_decay_medium_days: int = 30  # Medium age (weight 0.7)
    learning_decay_old_days: int = 90  # Old data (weight 0.4), older = 0.2

    # Learning Component Weights (must sum to 1.0)
    learning_weight_approval: float = 0.30  # Approval rate weight
    learning_weight_publish: float = 0.20  # Publish rate weight
    learning_weight_engagement: float = 0.30  # Engagement score weight
    learning_weight_success: float = 0.20  # Success rate weight

    # Engagement Tracking (Phase 4)
    engagement_check_enabled: bool = True  # Enable engagement tracking
    engagement_check_delay_hours: int = 24  # Check engagement after 24 hours

    # Inbox Priority System (Phase A)
    inbox_priority_enabled: bool = True  # Enable inbox priority over rising content
    inbox_priority_min_score: float = 0.35  # Minimum quality score for inbox prioritization
    inbox_cooldown_hours: int = 6  # Cooldown for failed inbox replies (more forgiving)
    rising_cooldown_hours: int = 24  # Cooldown for failed rising content (standard)

    # Subreddit Diversity System (Phase B)
    diversity_enabled: bool = True  # Enable diversity filtering
    max_per_subreddit: int = 2  # Maximum drafts per subreddit per run (flexible)
    max_per_post: int = 1  # Maximum drafts per post (strict - prevents spam)
    diversity_quality_boost_threshold: float = 0.75  # Allow 3rd+ from subreddit if quality exceeds this

    # Admin Authentication (Phase 1 - Frontend)
    admin_password_hash: str = ""  # Bcrypt hash of admin password (generate with: python -c "import bcrypt; print(bcrypt.hashpw(b'password', bcrypt.gensalt(12)).decode())")
    admin_jwt_secret: str = ""  # Secret for JWT signing (generate with: python -c "import secrets; print(secrets.token_urlsafe(32))")
    admin_session_hours: int = 24  # Session validity in hours

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
