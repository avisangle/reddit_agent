"""
.env file management service.

Provides safe CRUD operations for environment variables with:
- Timestamped backups before every write
- Pydantic validation against Settings model
- Diff preview for changes
- Backup restoration
- Automatic cleanup (keep last 10 backups)
"""
import os
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pydantic import ValidationError

from config import get_settings, Settings
from utils.logging import get_logger

logger = get_logger(__name__)


class EnvManager:
    """Manage .env file with validation and backups."""

    def __init__(self, env_path: str = ".env"):
        """
        Initialize EnvManager.

        Args:
            env_path: Path to .env file
        """
        self.env_path = Path(env_path)
        self.backup_dir = self.env_path.parent
        self.max_backups = 10

    def load_env(self) -> Dict[str, str]:
        """
        Load .env file into dictionary.

        Returns:
            Dict mapping variable names to values

        Raises:
            FileNotFoundError: If .env doesn't exist
        """
        if not self.env_path.exists():
            logger.error("env_file_not_found", path=str(self.env_path))
            raise FileNotFoundError(f".env file not found at {self.env_path}")

        env_vars = {}

        with open(self.env_path, 'r') as f:
            for line in f:
                line = line.strip()

                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue

                # Parse KEY=VALUE
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()

                    # Strip inline comments (e.g., "0.3 #comment" -> "0.3")
                    if '#' in value:
                        value = value.split('#')[0].strip()

                    # Remove quotes if present
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]

                    env_vars[key] = value

        logger.info("env_loaded", count=len(env_vars))
        return env_vars

    def save_env(self, env_vars: Dict[str, str], create_backup: bool = True) -> None:
        """
        Save environment variables to .env file.

        Args:
            env_vars: Dictionary of environment variables
            create_backup: Whether to create backup before writing

        Raises:
            ValidationError: If env_vars don't pass Pydantic validation
        """
        # Validate with Pydantic Settings
        validation_errors = self.validate_env(env_vars)
        if validation_errors:
            logger.error("env_validation_failed", errors=validation_errors)
            raise ValidationError(validation_errors, Settings)

        # Create backup before writing
        if create_backup and self.env_path.exists():
            self._create_backup()

        # Write to .env file
        with open(self.env_path, 'w') as f:
            # Group variables for readability
            self._write_section(f, env_vars, "Reddit API", [
                "REDDIT_CLIENT_ID",
                "REDDIT_CLIENT_SECRET",
                "REDDIT_USERNAME",
                "REDDIT_PASSWORD",
                "REDDIT_USER_AGENT"
            ])

            self._write_section(f, env_vars, "Subreddits", [
                "ALLOWED_SUBREDDITS"
            ])

            self._write_section(f, env_vars, "LLM API Keys", [
                "GEMINI_API_KEY",
                "OPENAI_API_KEY",
                "ANTHROPIC_API_KEY"
            ])

            self._write_section(f, env_vars, "Notifications", [
                "NOTIFICATION_TYPE",
                "SLACK_WEBHOOK_URL",
                "SLACK_CHANNEL",
                "TELEGRAM_BOT_TOKEN",
                "TELEGRAM_CHAT_ID",
                "WEBHOOK_URL",
                "WEBHOOK_SECRET",
                "PUBLIC_URL"
            ])

            self._write_section(f, env_vars, "Safety Limits", [
                "MAX_COMMENTS_PER_DAY",
                "MAX_COMMENTS_PER_RUN",
                "SHADOWBAN_RISK_THRESHOLD",
                "COOLDOWN_PERIOD_HOURS",
                "POST_REPLY_RATIO",
                "MAX_POST_REPLIES_PER_RUN",
                "MAX_COMMENT_REPLIES_PER_RUN",
                "MIN_JITTER_SECONDS",
                "MAX_JITTER_SECONDS",
                "DRY_RUN"
            ])

            self._write_section(f, env_vars, "Phase A: Inbox Priority", [
                "INBOX_PRIORITY_ENABLED",
                "INBOX_COOLDOWN_HOURS",
                "RISING_COOLDOWN_HOURS"
            ])

            self._write_section(f, env_vars, "Phase B: Diversity", [
                "DIVERSITY_ENABLED",
                "MAX_PER_SUBREDDIT",
                "MAX_PER_POST",
                "DIVERSITY_QUALITY_BOOST_THRESHOLD"
            ])

            self._write_section(f, env_vars, "Quality Scoring", [
                "QUALITY_SCORING_ENABLED",
                "SCORE_EXPLORATION_RATE",
                "SCORE_TOP_N_RANDOM"
            ])

            self._write_section(f, env_vars, "Admin", [
                "ADMIN_PASSWORD_HASH",
                "ADMIN_JWT_SECRET",
                "ADMIN_SESSION_HOURS"
            ])

            # Write any remaining variables not in sections
            written_keys = set()
            for section_keys in [
                ["REDDIT_CLIENT_ID", "REDDIT_CLIENT_SECRET", "REDDIT_USERNAME", "REDDIT_PASSWORD", "REDDIT_USER_AGENT"],
                ["ALLOWED_SUBREDDITS"],
                ["GEMINI_API_KEY", "OPENAI_API_KEY", "ANTHROPIC_API_KEY"],
                ["NOTIFICATION_TYPE", "SLACK_WEBHOOK_URL", "SLACK_CHANNEL", "TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID", "WEBHOOK_URL", "WEBHOOK_SECRET", "PUBLIC_URL"],
                ["MAX_COMMENTS_PER_DAY", "MAX_COMMENTS_PER_RUN", "SHADOWBAN_RISK_THRESHOLD", "COOLDOWN_PERIOD_HOURS", "POST_REPLY_RATIO", "MAX_POST_REPLIES_PER_RUN", "MAX_COMMENT_REPLIES_PER_RUN", "MIN_JITTER_SECONDS", "MAX_JITTER_SECONDS", "DRY_RUN"],
                ["INBOX_PRIORITY_ENABLED", "INBOX_COOLDOWN_HOURS", "RISING_COOLDOWN_HOURS"],
                ["DIVERSITY_ENABLED", "MAX_PER_SUBREDDIT", "MAX_PER_POST", "DIVERSITY_QUALITY_BOOST_THRESHOLD"],
                ["QUALITY_SCORING_ENABLED", "SCORE_EXPLORATION_RATE", "SCORE_TOP_N_RANDOM"],
                ["ADMIN_PASSWORD_HASH", "ADMIN_JWT_SECRET", "ADMIN_SESSION_HOURS"]
            ]:
                written_keys.update(section_keys)

            remaining = {k: v for k, v in env_vars.items() if k not in written_keys}
            if remaining:
                f.write("\n# Other Settings\n")
                for key, value in sorted(remaining.items()):
                    f.write(f"{key}={value}\n")

        logger.info("env_saved", count=len(env_vars))

        # Cleanup old backups
        self._cleanup_backups()

    def _write_section(self, f, env_vars: Dict[str, str], section_name: str, keys: List[str]) -> None:
        """Write a section of environment variables."""
        f.write(f"\n# {section_name}\n")
        for key in keys:
            if key in env_vars:
                value = env_vars[key]
                f.write(f"{key}={value}\n")

    def validate_env(self, env_vars: Dict[str, str]) -> Optional[List[Dict]]:
        """
        Validate environment variables against Pydantic Settings model.

        Args:
            env_vars: Dictionary of environment variables to validate

        Returns:
            List of validation errors, or None if valid
        """
        try:
            # Temporarily set environment variables for validation
            original_env = {}
            for key, value in env_vars.items():
                original_env[key] = os.environ.get(key)
                os.environ[key] = value

            # Try to instantiate Settings (triggers validation)
            Settings()

            # Restore original environment
            for key in env_vars.keys():
                if original_env[key] is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = original_env[key]

            return None

        except ValidationError as e:
            # Restore original environment
            for key in env_vars.keys():
                if original_env.get(key) is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = original_env[key]

            return e.errors()

    def preview_changes(self, current_env: Dict[str, str], new_env: Dict[str, str]) -> Dict[str, Dict]:
        """
        Generate diff between current and new environment variables.

        Args:
            current_env: Current .env values
            new_env: New .env values to apply

        Returns:
            Dict mapping variable names to change info:
            {
                "GEMINI_API_KEY": {
                    "old": "***...abc123",
                    "new": "***...xyz789",
                    "changed": True,
                    "is_secret": True
                }
            }
        """
        diff = {}

        # Check all keys in new_env
        all_keys = set(current_env.keys()) | set(new_env.keys())

        for key in sorted(all_keys):
            old_value = current_env.get(key, "")
            new_value = new_env.get(key, "")

            is_secret = self._is_secret_field(key)

            # Mask secrets in diff
            if is_secret:
                old_display = self._mask_secret(old_value)
                new_display = self._mask_secret(new_value)
            else:
                old_display = old_value
                new_display = new_value

            diff[key] = {
                "old": old_display,
                "new": new_display,
                "changed": old_value != new_value,
                "is_secret": is_secret
            }

        return diff

    def _is_secret_field(self, key: str) -> bool:
        """Check if field contains sensitive data."""
        secret_keywords = [
            "PASSWORD", "SECRET", "KEY", "TOKEN", "HASH", "WEBHOOK"
        ]
        return any(keyword in key.upper() for keyword in secret_keywords)

    def _mask_secret(self, value: str) -> str:
        """Mask secret value, showing only last 6 characters."""
        if not value or len(value) <= 6:
            return "***"
        return f"***...{value[-6:]}"

    def _create_backup(self) -> str:
        """
        Create timestamped backup of .env file.

        Returns:
            Path to backup file
        """
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        backup_path = self.backup_dir / f".env.backup.{timestamp}"

        shutil.copy2(self.env_path, backup_path)

        logger.info("env_backup_created", backup_path=str(backup_path))
        return str(backup_path)

    def _cleanup_backups(self) -> None:
        """Keep only the last N backups, delete older ones."""
        backups = self.list_backups()

        if len(backups) > self.max_backups:
            # Sort by timestamp (newest first)
            backups.sort(reverse=True)

            # Delete old backups
            for backup_info in backups[self.max_backups:]:
                backup_path = Path(backup_info["path"])
                backup_path.unlink()
                logger.info("env_backup_deleted", path=str(backup_path))

    def list_backups(self) -> List[Dict]:
        """
        List all .env backup files.

        Returns:
            List of backup info dicts, sorted by timestamp (newest first)
        """
        backups = []

        for backup_file in self.backup_dir.glob(".env.backup.*"):
            # Extract timestamp from filename
            try:
                timestamp_str = backup_file.name.split(".")[-1]
                timestamp = datetime.strptime(timestamp_str, "%Y%m%d%H%M%S")

                backups.append({
                    "path": str(backup_file),
                    "timestamp": timestamp.isoformat(),
                    "timestamp_display": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                    "size_bytes": backup_file.stat().st_size
                })
            except (ValueError, IndexError):
                # Invalid backup filename, skip
                continue

        # Sort by timestamp (newest first)
        backups.sort(key=lambda x: x["timestamp"], reverse=True)

        return backups

    def restore_backup(self, backup_path: str) -> None:
        """
        Restore .env file from a backup.

        Args:
            backup_path: Path to backup file to restore

        Raises:
            FileNotFoundError: If backup file doesn't exist
        """
        backup = Path(backup_path)

        if not backup.exists():
            logger.error("backup_not_found", path=backup_path)
            raise FileNotFoundError(f"Backup not found: {backup_path}")

        # Create backup of current .env before restoring
        if self.env_path.exists():
            self._create_backup()

        # Restore from backup
        shutil.copy2(backup, self.env_path)

        logger.info("env_restored_from_backup", backup_path=backup_path)

    def get_field_metadata(self) -> Dict[str, Dict]:
        """
        Get metadata for all .env fields (for frontend rendering).

        Returns:
            Dict mapping field names to metadata:
            {
                "REDDIT_CLIENT_ID": {
                    "label": "Reddit Client ID",
                    "type": "text",
                    "required": True,
                    "secret": False,
                    "group": "Reddit API"
                }
            }
        """
        return {
            # Reddit API
            "REDDIT_CLIENT_ID": {
                "label": "Client ID",
                "type": "text",
                "required": True,
                "secret": False,
                "group": "Reddit API"
            },
            "REDDIT_CLIENT_SECRET": {
                "label": "Client Secret",
                "type": "password",
                "required": True,
                "secret": True,
                "group": "Reddit API"
            },
            "REDDIT_USERNAME": {
                "label": "Username",
                "type": "text",
                "required": True,
                "secret": False,
                "group": "Reddit API"
            },
            "REDDIT_PASSWORD": {
                "label": "Password",
                "type": "password",
                "required": True,
                "secret": True,
                "group": "Reddit API"
            },
            "REDDIT_USER_AGENT": {
                "label": "User Agent",
                "type": "text",
                "required": True,
                "secret": False,
                "group": "Reddit API"
            },

            # Subreddits
            "ALLOWED_SUBREDDITS": {
                "label": "Allowed Subreddits (comma-separated)",
                "type": "text",
                "required": True,
                "secret": False,
                "group": "Subreddits"
            },

            # LLM Keys
            "GEMINI_API_KEY": {
                "label": "Gemini API Key",
                "type": "password",
                "required": False,
                "secret": True,
                "group": "LLM Keys"
            },
            "OPENAI_API_KEY": {
                "label": "OpenAI API Key",
                "type": "password",
                "required": False,
                "secret": True,
                "group": "LLM Keys"
            },
            "ANTHROPIC_API_KEY": {
                "label": "Anthropic API Key",
                "type": "password",
                "required": False,
                "secret": True,
                "group": "LLM Keys"
            },

            # Notifications
            "NOTIFICATION_TYPE": {
                "label": "Notification Type",
                "type": "select",
                "required": True,
                "secret": False,
                "group": "Notifications",
                "options": ["slack", "telegram", "webhook"]
            },
            "SLACK_WEBHOOK_URL": {
                "label": "Slack Webhook URL",
                "type": "password",
                "required": False,
                "secret": True,
                "group": "Notifications"
            },
            "SLACK_CHANNEL": {
                "label": "Slack Channel",
                "type": "text",
                "required": False,
                "secret": False,
                "group": "Notifications"
            },
            "TELEGRAM_BOT_TOKEN": {
                "label": "Telegram Bot Token",
                "type": "password",
                "required": False,
                "secret": True,
                "group": "Notifications"
            },
            "TELEGRAM_CHAT_ID": {
                "label": "Telegram Chat ID",
                "type": "text",
                "required": False,
                "secret": False,
                "group": "Notifications"
            },
            "WEBHOOK_URL": {
                "label": "Webhook URL",
                "type": "text",
                "required": False,
                "secret": False,
                "group": "Notifications"
            },
            "WEBHOOK_SECRET": {
                "label": "Webhook Secret",
                "type": "password",
                "required": False,
                "secret": True,
                "group": "Notifications"
            },
            "PUBLIC_URL": {
                "label": "Public URL (for approval callbacks)",
                "type": "text",
                "required": True,
                "secret": False,
                "group": "Notifications"
            },

            # Safety Limits
            "MAX_COMMENTS_PER_DAY": {
                "label": "Max Comments Per Day (1-10)",
                "type": "number",
                "required": True,
                "secret": False,
                "group": "Safety Limits",
                "min": 1,
                "max": 10,
                "description": "Maximum number of comments allowed per day across all runs (hard limit)"
            },
            "MAX_COMMENTS_PER_RUN": {
                "label": "Max Comments Per Run (1-5)",
                "type": "number",
                "required": True,
                "secret": False,
                "group": "Safety Limits",
                "min": 1,
                "max": 5,
                "description": "Maximum number of comments to post in a single workflow run"
            },
            "SHADOWBAN_RISK_THRESHOLD": {
                "label": "Shadowban Risk Threshold (0.0-1.0)",
                "type": "number",
                "required": True,
                "secret": False,
                "group": "Safety Limits",
                "min": 0.0,
                "max": 1.0,
                "step": 0.1,
                "description": "Risk threshold for shadowban detection. Higher = more cautious (recommended: 0.7)"
            },
            "COOLDOWN_PERIOD_HOURS": {
                "label": "Cooldown Period (hours)",
                "type": "number",
                "required": True,
                "secret": False,
                "group": "Safety Limits",
                "min": 1,
                "max": 168,
                "description": "Hours to wait before replying to the same post again (prevents spam)"
            },
            "POST_REPLY_RATIO": {
                "label": "Post Reply Ratio (0.0-1.0)",
                "type": "number",
                "required": True,
                "secret": False,
                "group": "Safety Limits",
                "min": 0.0,
                "max": 1.0,
                "step": 0.1,
                "description": "Ratio of post replies to comment replies (0.3 = 30% posts, 70% comments)"
            },
            "MAX_POST_REPLIES_PER_RUN": {
                "label": "Max Post Replies Per Run",
                "type": "number",
                "required": True,
                "secret": False,
                "group": "Safety Limits",
                "min": 0,
                "max": 5,
                "description": "Maximum number of direct post replies in a single run"
            },
            "MAX_COMMENT_REPLIES_PER_RUN": {
                "label": "Max Comment Replies Per Run",
                "type": "number",
                "required": True,
                "secret": False,
                "group": "Safety Limits",
                "min": 0,
                "max": 5,
                "description": "Maximum number of comment replies in a single run"
            },
            "MIN_JITTER_SECONDS": {
                "label": "Min Jitter (seconds)",
                "type": "number",
                "required": False,
                "secret": False,
                "group": "Safety Limits",
                "min": 0,
                "max": 60,
                "description": "Minimum random delay between actions to avoid detection patterns (default: 5)"
            },
            "MAX_JITTER_SECONDS": {
                "label": "Max Jitter (seconds)",
                "type": "number",
                "required": False,
                "secret": False,
                "group": "Safety Limits",
                "min": 0,
                "max": 300,
                "description": "Maximum random delay between actions to avoid detection patterns (default: 15)"
            },
            "DRY_RUN": {
                "label": "Dry Run Mode",
                "type": "checkbox",
                "required": False,
                "secret": False,
                "group": "Safety Limits",
                "description": "Enable to test without actually posting to Reddit (default: False)"
            },

            # Phase A: Inbox Priority
            "INBOX_PRIORITY_ENABLED": {
                "label": "Enable Inbox Priority",
                "type": "checkbox",
                "required": False,
                "secret": False,
                "group": "Phase A: Inbox Priority",
                "description": "Prioritize replies to your comments/posts over rising content (default: True)"
            },
            "INBOX_COOLDOWN_HOURS": {
                "label": "Inbox Cooldown (hours)",
                "type": "number",
                "required": False,
                "secret": False,
                "group": "Phase A: Inbox Priority",
                "min": 1,
                "max": 48,
                "description": "Cooldown period for inbox items (more forgiving than rising) (default: 6)"
            },
            "RISING_COOLDOWN_HOURS": {
                "label": "Rising Cooldown (hours)",
                "type": "number",
                "required": False,
                "secret": False,
                "group": "Phase A: Inbox Priority",
                "min": 12,
                "max": 168,
                "description": "Cooldown period for rising posts/comments (default: 24)"
            },

            # Phase B: Diversity
            "DIVERSITY_ENABLED": {
                "label": "Enable Diversity",
                "type": "checkbox",
                "required": False,
                "secret": False,
                "group": "Phase B: Diversity",
                "description": "Limit comments per subreddit/post to avoid spam patterns (default: True)"
            },
            "MAX_PER_SUBREDDIT": {
                "label": "Max Per Subreddit",
                "type": "number",
                "required": False,
                "secret": False,
                "group": "Phase B: Diversity",
                "min": 1,
                "max": 5,
                "description": "Maximum comments per subreddit per run (default: 2)"
            },
            "MAX_PER_POST": {
                "label": "Max Per Post",
                "type": "number",
                "required": False,
                "secret": False,
                "group": "Phase B: Diversity",
                "min": 1,
                "max": 3,
                "description": "Maximum comments per post (default: 1, strict limit)"
            },
            "DIVERSITY_QUALITY_BOOST_THRESHOLD": {
                "label": "Quality Boost Threshold (0.5-1.0)",
                "type": "number",
                "required": False,
                "secret": False,
                "group": "Phase B: Diversity",
                "min": 0.5,
                "max": 1.0,
                "step": 0.05,
                "description": "Quality score threshold to bypass subreddit limit (default: 0.75)"
            },

            # Quality Scoring
            "QUALITY_SCORING_ENABLED": {
                "label": "Enable Quality Scoring",
                "type": "checkbox",
                "required": False,
                "secret": False,
                "group": "Quality Scoring",
                "description": "Use AI-powered quality scoring to rank candidates (default: True)"
            },
            "SCORE_EXPLORATION_RATE": {
                "label": "Exploration Rate (0.0-1.0)",
                "type": "number",
                "required": False,
                "secret": False,
                "group": "Quality Scoring",
                "min": 0.0,
                "max": 1.0,
                "step": 0.05,
                "description": "Percentage of candidates to select randomly to avoid patterns (default: 0.25 = 25%)"
            },
            "SCORE_TOP_N_RANDOM": {
                "label": "Top N Random",
                "type": "number",
                "required": False,
                "secret": False,
                "group": "Quality Scoring",
                "min": 1,
                "max": 10,
                "description": "Randomly select from top N candidates during exploration (default: 5)"
            },
        }
