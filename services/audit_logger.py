"""
Audit logging service for admin actions.

Records all administrative actions to the database with redacted sensitive data.
"""
import json
import re
from datetime import datetime
from typing import Dict, Any, Optional

from sqlalchemy.orm import Session

from models.database import AdminAuditLog, get_session_local
from utils.logging import get_logger

logger = get_logger(__name__)

# Sensitive field patterns to redact (case-insensitive keywords)
SENSITIVE_KEYWORDS = [
    'password', 'secret', 'key', 'token', 'auth',
    'api_key', 'client_secret', 'webhook_url'
]


class AuditLogger:
    """Service for logging admin actions with automatic sensitive data redaction."""

    def __init__(self):
        """Initialize audit logger."""
        # Create case-insensitive regex from keywords
        pattern = '|'.join(SENSITIVE_KEYWORDS)
        self.sensitive_regex = re.compile(pattern, re.IGNORECASE)

    def _redact_sensitive_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Redact sensitive fields from data dictionary.

        Args:
            data: Dictionary potentially containing sensitive data

        Returns:
            Dictionary with sensitive values redacted
        """
        redacted = {}

        for key, value in data.items():
            # Check if key matches sensitive pattern
            if self.sensitive_regex.search(key):
                # Redact value (show first 3 and last 4 chars for reference)
                if isinstance(value, str) and len(value) > 10:
                    redacted[key] = f"***...{value[-4:]}"
                else:
                    redacted[key] = "***"
            elif isinstance(value, dict):
                # Recursively redact nested dictionaries
                redacted[key] = self._redact_sensitive_data(value)
            else:
                # Keep non-sensitive values as-is
                redacted[key] = value

        return redacted

    def log_action(
        self,
        action: str,
        ip_address: str,
        success: bool = True,
        details: Optional[Dict[str, Any]] = None,
        user_agent: Optional[str] = None,
        session: Optional[Session] = None
    ) -> None:
        """
        Log an admin action to the audit log.

        Args:
            action: Action type (LOGIN, ENV_UPDATE, BACKUP_RESTORE, etc.)
            ip_address: Client IP address
            success: Whether the action was successful
            details: Additional details about the action (will be redacted)
            user_agent: Client user agent string
            session: Database session (creates new one if not provided)
        """
        # Redact sensitive data from details
        redacted_details = None
        if details:
            redacted_details = self._redact_sensitive_data(details)

        # Convert details to JSON string
        details_json = None
        if redacted_details:
            try:
                details_json = json.dumps(redacted_details)
            except Exception as e:
                logger.error("failed_to_serialize_audit_details", error=str(e))
                details_json = json.dumps({"error": "serialization_failed"})

        # Create audit log entry
        entry = AdminAuditLog(
            timestamp=datetime.utcnow(),
            action=action,
            ip_address=ip_address,
            user_agent=user_agent,
            details=details_json,
            success=success
        )

        # Save to database
        should_close = False
        if session is None:
            SessionLocal = get_session_local()
            session = SessionLocal()
            should_close = True

        try:
            session.add(entry)
            session.commit()

            logger.info(
                "audit_logged",
                action=action,
                ip_address=ip_address,
                success=success
            )
        except Exception as e:
            session.rollback()
            logger.error(
                "audit_log_failed",
                action=action,
                error=str(e)
            )
        finally:
            if should_close:
                session.close()

    def log_login(
        self,
        ip_address: str,
        success: bool,
        user_agent: Optional[str] = None,
        reason: Optional[str] = None
    ) -> None:
        """
        Log a login attempt.

        Args:
            ip_address: Client IP address
            success: Whether login was successful
            user_agent: Client user agent string
            reason: Reason for failure (if applicable)
        """
        details = {}
        if reason:
            details["reason"] = reason

        self.log_action(
            action="LOGIN",
            ip_address=ip_address,
            success=success,
            details=details if details else None,
            user_agent=user_agent
        )

    def log_env_update(
        self,
        ip_address: str,
        changed_fields: list,
        success: bool,
        user_agent: Optional[str] = None
    ) -> None:
        """
        Log an .env file update.

        Args:
            ip_address: Client IP address
            changed_fields: List of field names that were changed
            success: Whether update was successful
            user_agent: Client user agent string
        """
        self.log_action(
            action="ENV_UPDATE",
            ip_address=ip_address,
            success=success,
            details={"changed_fields": changed_fields},
            user_agent=user_agent
        )

    def log_backup_restore(
        self,
        ip_address: str,
        backup_file: str,
        success: bool,
        user_agent: Optional[str] = None
    ) -> None:
        """
        Log a backup restore operation.

        Args:
            ip_address: Client IP address
            backup_file: Name of backup file being restored
            success: Whether restore was successful
            user_agent: Client user agent string
        """
        self.log_action(
            action="BACKUP_RESTORE",
            ip_address=ip_address,
            success=success,
            details={"backup_file": backup_file},
            user_agent=user_agent
        )

    def get_recent_logs(
        self,
        limit: int = 100,
        action_filter: Optional[str] = None,
        session: Optional[Session] = None
    ) -> list:
        """
        Retrieve recent audit logs.

        Args:
            limit: Maximum number of logs to retrieve
            action_filter: Filter by action type (optional)
            session: Database session (creates new one if not provided)

        Returns:
            List of AdminAuditLog objects
        """
        should_close = False
        if session is None:
            SessionLocal = get_session_local()
            session = SessionLocal()
            should_close = True

        try:
            query = session.query(AdminAuditLog).order_by(
                AdminAuditLog.timestamp.desc()
            )

            if action_filter:
                query = query.filter(AdminAuditLog.action == action_filter)

            logs = query.limit(limit).all()
            return logs
        finally:
            if should_close:
                session.close()
