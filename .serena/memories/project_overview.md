# Reddit Comment Engagement Agent - Project Overview

## Purpose
A compliance-first, anti-fingerprint Reddit engagement agent that:
- Responds to comment replies on user's posts and comments
- Participates in discussions within strictly allow-listed subreddits
- Operates under strict volume limits (≤8 comments/day)
- Uses mandatory Human-in-the-Loop (HITL) approvals via Slack/Telegram
- Auto-publishes approved drafts to Reddit
- Minimizes bot-detection and shadowban risk

## Status
- Version: 2.5
- Tests: 136 passing
- Fully operational with AI-powered quality scoring

## Tech Stack

### Core Framework
- **Python**: 3.14.0
- **LangGraph**: ≥0.2.0 (workflow orchestration)
- **LangChain**: ≥0.1.0 (agent framework)

### Reddit Integration
- **PRAW**: ≥7.7.0 (Reddit API wrapper)

### Database
- **SQLAlchemy**: ≥2.0.0 (ORM)
- **Alembic**: ≥1.13.0 (migrations)
- **SQLite**: Default database

### Data Validation
- **Pydantic**: ≥2.5.0 (settings + validation)
- **Pydantic-settings**: ≥2.1.0

### Logging
- **StructLog**: ≥24.1.0 (structured JSON logging)

### API Server
- **FastAPI**: ≥0.109.0 (callback server)
- **Uvicorn**: ≥0.27.0 (ASGI server)

### Admin UI
- **Jinja2**: ≥3.1.0 (templating)
- **BCrypt**: ≥4.0.0 (password hashing)
- **PyJWT**: ≥2.8.0 (authentication)

### Testing
- **pytest**: ≥7.4.0
- **pytest-asyncio**: ≥0.21.0
- **pytest-cov**: ≥4.1.0
- **pytest-mock**: ≥3.12.0

### Code Quality
- **black**: ≥23.12.0 (formatting)
- **flake8**: ≥7.0.0 (linting)
- **isort**: ≥5.13.0 (import sorting)
- **mypy**: ≥1.8.0 (type checking)
- **pre-commit**: ≥3.6.0 (git hooks)

## Architecture Components

### Core Services (services/)
- **reddit_client.py**: Reddit API with shadowban detection
- **context_builder.py**: Vertical context loading
- **rule_engine.py**: Subreddit compliance
- **prompt_manager.py**: Template management + PII scrubbing
- **state_manager.py**: State, tokens, idempotency
- **poster.py**: Publish approved drafts
- **notifiers/**: Slack, Telegram, Webhook

### Agent (agents/)
- **generator.py**: LLM draft generator (Gemini 2.5 Flash)

### Workflow (workflow/)
- **graph.py**: LangGraph workflow (13 nodes)
- **nodes.py**: Workflow node implementations
- **runner.py**: Workflow execution
- **state.py**: Workflow state dataclass

### API (api/)
- **callback_server.py**: FastAPI server for HITL approvals + auto-publish

### Database (models/)
- **database.py**: 6 SQLAlchemy tables
- **schemas.py**: Pydantic validation schemas

### Configuration
- **config.py**: Pydantic settings with validation, auto .env loading

## Database Tables
1. **replied_items**: Track processed Reddit items with cooldowns
2. **draft_queue**: Drafts with approval tokens and status
3. **subreddit_rules_cache**: Cached subreddit rules
4. **error_log**: Error tracking
5. **daily_stats**: Daily comment count tracking
6. **performance_history**: Draft outcomes and engagement metrics

## Key Features

### Quality Scoring System (v2.5)
- 7-factor AI scoring: upvote ratio, karma, freshness, velocity, question signal, depth, historical
- Historical learning from past outcomes per subreddit
- 25% exploration rate to avoid patterns

### Inbox Priority System
- HIGH priority for inbox replies
- Separate cooldowns: 6h inbox, 24h rising content

### Subreddit Diversity
- Max 2 per subreddit (with quality override ≥0.75)
- Max 1 per post (strict)

### Safety Constraints
- ≤8 comments/day (hardcoded)
- ≤3 comments/run (hardcoded)
- HITL required for all drafts
- Shadowban detection circuit breaker
- Anti-fingerprint timing with random jitter

### Security
- SHA-256 hashed approval tokens
- 48-hour token TTL
- One-time use tokens
- State machine validation
