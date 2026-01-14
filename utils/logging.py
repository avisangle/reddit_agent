"""
Structured JSON logging with secret redaction.
"""
import logging
import sys
from typing import Any, Dict
import structlog


# Secrets to redact from logs
REDACTED_KEYS = {
    'token', 'secret', 'password', 'api_key', 
    'client_secret', 'webhook_secret', 'auth'
}


def redact_processor(logger: Any, method_name: str, event_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Redact sensitive information from logs."""
    for key, value in event_dict.items():
        if any(secret in key.lower() for secret in REDACTED_KEYS):
            event_dict[key] = '[REDACTED]'
    return event_dict


def configure_logging():
    """Configure structured logging."""
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            redact_processor,  # Custom redaction
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()  # JSON output
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    # Configure root logger
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=logging.INFO,
    )


def get_logger(name: str = __name__) -> structlog.stdlib.BoundLogger:
    """
    Get a configured logger instance.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Configured structlog logger
        
    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("draft_generated", reddit_id="abc123", subreddit="sysadmin")
        {"event": "draft_generated", "reddit_id": "abc123", "subreddit": "sysadmin", ...}
    """
    return structlog.get_logger(name)


# Configure on module import
configure_logging()
