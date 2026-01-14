"""
Test configuration validation (Story 0).
"""
import pytest
from config import Settings
from pydantic import ValidationError


def test_valid_user_agent():
    """Test valid Reddit user agent format."""
    valid_agent = "android:com.test.redditagent:v2.1 (by /u/TestUser)"
    settings = Settings(
        reddit_client_id="test",
        reddit_client_secret="test",
        reddit_username="test",
        reddit_password="test",
        reddit_user_agent=valid_agent,
        allowed_subreddits="test",
        openai_api_key="test",
        webhook_url="https://test.com",
        webhook_secret="test"
    )
    assert settings.reddit_user_agent == valid_agent


def test_invalid_user_agent_format():
    """Test invalid user agent raises ValidationError."""
    with pytest.raises(ValidationError) as exc_info:
        Settings(
            reddit_client_id="test",
            reddit_client_secret="test",
            reddit_username="test",
            reddit_password="test",
            reddit_user_agent="invalid-user-agent",
            allowed_subreddits="test",
            openai_api_key="test",
            webhook_url="https://test.com",
            webhook_secret="test"
        )
    assert "User agent must match format" in str(exc_info.value)


def test_empty_subreddits():
    """Test empty subreddits list raises ValidationError."""
    with pytest.raises(ValidationError):
        Settings(
            reddit_client_id="test",
            reddit_client_secret="test",
            reddit_username="test",
            reddit_password="test",
            reddit_user_agent="android:com.test.app:v1.0 (by /u/Test)",
            allowed_subreddits="",
            openai_api_key="test",
            webhook_url="https://test.com",
            webhook_secret="test"
        )


def test_subreddits_list_property():
    """Test subreddits_list property parses correctly."""
    settings = Settings(
        reddit_client_id="test",
        reddit_client_secret="test",
        reddit_username="test",
        reddit_password="test",
        reddit_user_agent="android:com.test.app:v1.0 (by /u/Test)",
        allowed_subreddits="sysadmin, learnpython, startups",
        openai_api_key="test",
        webhook_url="https://test.com",
        webhook_secret="test"
    )
    assert settings.subreddits_list == ["sysadmin", "learnpython", "startups"]


def test_llm_api_key_checker():
    """Test that at least one LLM API key is required."""
    settings = Settings(
        reddit_client_id="test",
        reddit_client_secret="test",
        reddit_username="test",
        reddit_password="test",
        reddit_user_agent="android:com.test.app:v1.0 (by /u/Test)",
        allowed_subreddits="test",
        openai_api_key="test_key",
        anthropic_api_key=None,
        gemini_api_key=None,
        webhook_url="https://test.com",
        webhook_secret="test"
    )
    assert settings.has_openai is True
    assert settings.has_anthropic is False
    assert settings.has_gemini is False


def test_gemini_api_key_accepted():
    """Test that Gemini API key alone satisfies LLM requirement."""
    settings = Settings(
        reddit_client_id="test",
        reddit_client_secret="test",
        reddit_username="test",
        reddit_password="test",
        reddit_user_agent="android:com.test.app:v1.0 (by /u/Test)",
        allowed_subreddits="test",
        openai_api_key=None,
        anthropic_api_key=None,
        gemini_api_key="test_gemini_key",
        webhook_url="https://test.com",
        webhook_secret="test"
    )
    assert settings.has_gemini is True
    assert settings.has_openai is False
    assert settings.has_anthropic is False


def test_has_gemini_property():
    """Test has_gemini property correctly detects configured key."""
    settings = Settings(
        reddit_client_id="test",
        reddit_client_secret="test",
        reddit_username="test",
        reddit_password="test",
        reddit_user_agent="android:com.test.app:v1.0 (by /u/Test)",
        allowed_subreddits="test",
        openai_api_key="test",
        gemini_api_key="gemini_key",
        webhook_url="https://test.com",
        webhook_secret="test"
    )
    assert settings.has_gemini is True
    assert settings.has_openai is True
