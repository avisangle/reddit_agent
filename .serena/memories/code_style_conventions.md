# Code Style and Conventions

## General Principles
- Compliance-first approach: all code must adhere to safety constraints
- Type hints throughout (Python 3.10+ union syntax: `str | None`)
- Structured logging with auto-redaction of sensitive data
- Pydantic for all configuration and validation
- SQLAlchemy ORM for database operations

## Python Style

### Formatting
- **Black**: Line length 100 characters
- **isort**: Profile 'black', line length 100
- **Flake8**: Ignore E501, W503, E203

### Code Structure
```python
# Standard module structure:
"""Module docstring."""
import standard_library
import third_party

from local_module import Class

# Constants
CONSTANT_NAME = value

# Class definitions
class ClassName:
    """Class docstring."""
    pass

# Function definitions
def function_name(param: str) -> bool:
    """Function docstring."""
    pass
```

### Naming Conventions
- **Classes**: PascalCase (e.g., `RedditClient`, `WorkflowGraph`)
- **Functions/Methods**: snake_case (e.g., `fetch_candidates`, `check_shadowban_risk`)
- **Variables**: snake_case (e.g., `max_comments`, `user_agent`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `MAX_RETRIES`, `DEFAULT_TIMEOUT`)
- **Private**: Prefix with underscore (e.g., `_internal_method`)

### Type Hints
- Required for all function signatures
- Use modern Python 3.10+ union syntax: `str | None` instead of `Optional[str]`
- Use generics from `typing` module
- Example:
```python
def process_candidate(
    candidate: CandidateComment | CandidatePost,
    context: dict[str, Any],
    settings: Settings
) -> str | None:
    """Process a candidate and return draft."""
    pass
```

### Docstrings
- Use triple double-quotes
- Brief one-line summary for simple functions
- Extended format for complex functions:
```python
def complex_function(param1: str, param2: int) -> bool:
    """
    Brief description.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        Description of return value
        
    Raises:
        ExceptionType: When this exception is raised
    """
    pass
```

## Configuration

### Settings Pattern
- All configuration in `config.py` using Pydantic BaseSettings
- Auto-load from `.env` file
- Type validation and field validators
- Example:
```python
class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding='utf-8',
        case_sensitive=False
    )
    
    field_name: str = Field(description="Description")
    
    @field_validator('field_name')
    def validate_field(cls, v):
        # Validation logic
        return v
```

## Database

### SQLAlchemy Models
- Inherit from `Base` (declarative base)
- Use `__tablename__` explicitly
- Index frequently queried columns
- Example:
```python
class ModelName(Base):
    __tablename__ = "table_name"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    status = Column(String, default="pending", index=True)
```

### Migrations
- Use Alembic for all schema changes
- Descriptive migration names
- Always test migrations (upgrade + downgrade)

## Logging

### Structured Logging
- Use `structlog` for all logging
- Auto-redact sensitive data (tokens, passwords, API keys)
- Include context in all logs
- Example:
```python
import structlog

logger = structlog.get_logger(__name__)

logger.info(
    "event_description",
    user_id=user_id,
    action="action_name",
    result=result
)
```

### Log Levels
- **DEBUG**: Detailed diagnostic information
- **INFO**: General informational messages
- **WARNING**: Warning messages (potential issues)
- **ERROR**: Error messages (actual errors)
- **CRITICAL**: Critical errors (system halt)

## Error Handling

### Custom Exceptions
- Create specific exception classes for domain errors
- Example:
```python
class SafetyLockoutException(Exception):
    """Raised when safety threshold exceeded."""
    pass
```

### Exception Handling Pattern
```python
try:
    operation()
except SpecificException as e:
    logger.error("operation_failed", error=str(e))
    raise
except Exception as e:
    logger.critical("unexpected_error", error=str(e))
    raise
```

## Testing

### Test Structure
- Use `pytest` framework
- Use `conftest.py` for fixtures
- Mock external dependencies (Reddit API, LLM API)
- Example:
```python
def test_function_behavior(mock_dependency):
    """Test description."""
    # Arrange
    input_data = ...
    
    # Act
    result = function(input_data)
    
    # Assert
    assert result == expected_value
```

### Test Naming
- Prefix with `test_`
- Descriptive names: `test_<what>_<condition>_<expected>`
- Example: `test_fetch_candidates_returns_empty_when_no_inbox_items`

### Coverage
- Aim for >80% coverage
- Focus on business logic
- Mock external services

## LangGraph Workflow

### State Management
- Use dataclass for workflow state
- Immutable where possible
- Clear field descriptions

### Node Functions
- One responsibility per node
- Return updated state dictionary
- Handle errors gracefully
- Example:
```python
def node_function(state: WorkflowState) -> dict[str, Any]:
    """Node description."""
    # Process
    result = process(state)
    
    # Return state updates
    return {"field_name": result}
```

## Security Best Practices

### Token Handling
- Never log tokens in plaintext
- Hash tokens before storage (SHA-256)
- Use TTL for all tokens
- One-time use pattern

### PII Scrubbing
- Remove personally identifiable information from all external-facing content
- Use prompt manager for PII scrubbing

### Environment Variables
- Never commit `.env` files
- Use `.env.example` for templates
- Validate all environment variables at startup

## Git Conventions

### Commit Messages
- Format: `<type>: <description>`
- Types: feat, fix, docs, style, refactor, test, chore
- Examples:
  - `feat: add quality scoring system`
  - `fix: prevent duplicate replies on same post`
  - `docs: update README with deployment instructions`

### Branch Naming
- Format: `<type>/<description>`
- Examples: `feature/inbox-priority`, `fix/shadowban-detection`

## File Organization

### Module Structure
```
module/
├── __init__.py       # Module exports
├── main.py           # Main logic
├── helpers.py        # Helper functions
└── exceptions.py     # Custom exceptions
```

### Import Order
1. Standard library
2. Third-party packages
3. Local imports

Example:
```python
import os
from pathlib import Path

import praw
from pydantic import BaseModel

from services.reddit_client import RedditClient
```
