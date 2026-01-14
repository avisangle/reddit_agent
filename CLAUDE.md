# CLAUDE.md - AI Assistant Context

This file provides context for AI assistants working on the Reddit Comment Engagement Agent project.

## Project Overview

| Field | Value |
|-------|-------|
| **Name** | Reddit Comment Engagement Agent |
| **Version** | 2.4 |
| **Status** | ✅ Fully Operational with Auto-Publish |
| **Architecture** | LangGraph-based agent with compliance-first design |
| **Tests** | 136 tests passing |

### Purpose

A compliance-first, anti-fingerprint Reddit engagement agent that:
- Responds to comment replies on user's posts and comments
- Participates in discussions within strictly allow-listed subreddits
- Operates under strict volume limits (≤8 comments/day)
- Uses mandatory Human-in-the-Loop (HITL) approvals via Slack/Telegram
- **Auto-publishes approved drafts to Reddit**
- Minimizes bot-detection and shadowban risk

### How to Run

```bash
# Start the callback server (handles approvals + auto-publish)
python main.py server

# In another terminal: Run agent to fetch candidates and generate drafts
python main.py run --once

# Dry run mode (no actual posting)
python main.py run --once --dry-run

# Manual publish (if auto-publish disabled)
python main.py publish --limit 3
```

---

## Implementation Status

### ✅ Complete

| Component | Description |
|-----------|-------------|
| **Config** | Pydantic settings with validation, auto `.env` loading |
| **Database** | 5 SQLAlchemy tables with Alembic migrations |
| **Logging** | Structured JSON logging with auto-redaction |
| **Reddit Client** | PRAW wrapper with shadowban detection, bot filtering |
| **Context Builder** | Vertical-first context loading |
| **Rule Engine** | Subreddit compliance with cache |
| **Prompt Manager** | YAML templates, 5 personas, PII scrubbing |
| **Generator** | Gemini 2.5 Flash LLM integration |
| **State Manager** | Idempotency, cooldowns, secure token handling |
| **Notifiers** | Slack, Telegram, Webhook - all with URL-based approval |
| **Workflow** | LangGraph with 9 nodes, safety gates |
| **Post Replies** | Direct post reply support with configurable ratio |
| **HITL Approval** | URL-based approval flow (no Slack App required) |
| **Auto-Publish** | Approved drafts auto-post to Reddit |
| **Security** | Hashed tokens, 48h TTL, one-time use, state machine |
| **CI/CD** | GitHub Actions, pre-commit hooks |

### ⏳ Pending (Nice to Have)

| Item | Priority | Description |
|------|----------|-------------|
| **Monitoring Dashboard** | Low | Visualize daily stats, error rates, shadowban risk |
| **Multiple LLM Fallback** | Low | Fall back to OpenAI/Anthropic if Gemini fails |
| **Scheduled Runs** | Low | Cron-style scheduling for autonomous operation |

---

## Approval Flow

The agent uses a **URL-based approval flow** that works with Slack, Telegram, and Webhooks without requiring complex OAuth or interactivity endpoints.

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Agent Run   │────▶│ Slack/Telegram│────▶│   Browser    │
│ Generate Draft│     │  Notification │     │ /approve?... │
└──────────────┘     └──────────────┘     └──────────────┘
                                                   │
                                                   ▼
                     ┌──────────────┐     ┌──────────────┐
                     │   Reddit     │◀────│ Auto-Publish │
                     │   Comment    │     │ (Background) │
                     └──────────────┘     └──────────────┘
```

### Security Features

| Feature | Implementation |
|---------|----------------|
| **Token Hashing** | SHA-256 hash stored, not plaintext |
| **Token Expiry** | 48-hour TTL |
| **One-Time Use** | Token invalidated after approve/reject |
| **State Machine** | Only valid transitions (PENDING→APPROVED→PUBLISHED) |
| **Security Headers** | Referrer-Policy, X-Frame-Options, X-Content-Type-Options |

---

## Project Structure

```
reddit_agent/
├── config.py                    # Pydantic settings with validation
├── main.py                      # CLI entry point (run, server, publish)
│
├── models/
│   ├── database.py             # SQLAlchemy models (5 tables)
│   └── schemas.py              # Pydantic validation schemas
│
├── services/
│   ├── reddit_client.py        # Reddit API with shadowban detection
│   ├── context_builder.py      # Vertical context loading
│   ├── rule_engine.py          # Subreddit compliance
│   ├── prompt_manager.py       # Template management + PII scrubbing
│   ├── state_manager.py        # State, tokens, idempotency
│   ├── notification.py         # Webhook notifier
│   ├── poster.py               # Publish approved drafts
│   └── notifiers/
│       ├── slack.py            # Slack with URL buttons
│       ├── telegram.py         # Telegram with URL buttons
│       └── webhook.py          # Generic webhook
│
├── agents/
│   └── generator.py            # LLM draft generator (Gemini)
│
├── workflow/
│   ├── graph.py                # LangGraph workflow definition
│   ├── nodes.py                # 9 workflow nodes
│   ├── runner.py               # Workflow execution
│   └── state.py                # Workflow state dataclass
│
├── api/
│   └── callback_server.py      # FastAPI: /approve endpoint + auto-publish
│
├── prompts/
│   └── templates.yaml          # 5 persona templates with few-shot examples
│
├── utils/
│   └── logging.py              # Structured JSON logging
│
├── tests/                       # 136 tests
├── migrations/                  # Alembic migrations
└── .github/workflows/ci.yml    # GitHub Actions
```

---

## Configuration

### Required Environment Variables

```bash
# Reddit API
REDDIT_CLIENT_ID=xxx
REDDIT_CLIENT_SECRET=xxx
REDDIT_USERNAME=xxx
REDDIT_PASSWORD=xxx
REDDIT_USER_AGENT=android:com.yourname.app:v2.1 (by /u/YourUsername)

# Subreddits (comma-separated)
ALLOWED_SUBREDDITS=sysadmin,learnpython,startups

# LLM (at least one required)
GEMINI_API_KEY=xxx          # Recommended
# OPENAI_API_KEY=xxx        # Alternative
# ANTHROPIC_API_KEY=xxx     # Alternative

# Notifications
NOTIFICATION_TYPE=slack     # slack, telegram, or webhook
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/xxx

# Callback Server (REQUIRED for approval buttons to work)
PUBLIC_URL=https://your-public-url.com  # Must be publicly accessible
```

### Safety Limits (Hardcoded)

```python
max_comments_per_day: int = 8      # Daily limit
max_comments_per_run: int = 3      # Per-run limit
shadowban_risk_threshold: float = 0.7
post_reply_ratio: float = 0.3      # 30% posts, 70% comments
```

---

## Workflow Nodes

```
fetch_candidates → filter_candidates → select_by_ratio → check_daily_limit
                                                              ↓
                        notify_human ← generate_draft ← build_context ← select_candidate
                                                              ↓
                                                         check_rules
```

| Node | Purpose |
|------|---------|
| `fetch_candidates` | Get inbox replies + rising posts/comments |
| `filter_candidates` | Remove already-processed items |
| `select_by_ratio` | Apply post/comment ratio distribution |
| `check_daily_limit` | Enforce ≤8 comments/day |
| `select_candidate` | Pick next candidate to process |
| `build_context` | Load vertical context chain |
| `check_rules` | Verify subreddit compliance |
| `generate_draft` | LLM generates reply draft |
| `notify_human` | Send to Slack/Telegram for approval |

---

## Database Tables

| Table | Purpose |
|-------|---------|
| `replied_items` | Track processed Reddit items |
| `draft_queue` | Drafts with approval_token_hash, status tracking |
| `subreddit_rules_cache` | Cached subreddit rules |
| `error_log` | Error tracking for debugging |
| `daily_stats` | Daily comment count tracking |

---

## Commands Reference

| Command | Description |
|---------|-------------|
| `python main.py server` | Start callback server with auto-publish |
| `python main.py server --no-auto-publish` | Server without auto-publish |
| `python main.py run --once` | Single workflow run |
| `python main.py run --once --dry-run` | Test without posting |
| `python main.py publish --limit 3` | Manual publish approved drafts |
| `python main.py health` | Show health status |
| `pytest -v` | Run tests |
| `alembic upgrade head` | Apply migrations |

---

## Testing

```bash
# Run all tests
pytest -v

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_reddit_client.py -v
```

---

## Safety Constraints (Non-Negotiable)

| Constraint | Enforcement |
|------------|-------------|
| ≤8 comments/day | `daily_stats` table check |
| ≤3 comments/run | Workflow runner limit |
| HITL required | All drafts require human approval |
| Subreddit allow-list | Only operates in configured subreddits |
| Bot filtering | Skips AutoModerator, bot-pattern authors |
| Shadowban detection | Circuit breaker halts on high risk |
| Anti-fingerprint timing | Random jitter between actions |
| Token security | Hashed, expiring, one-time-use tokens |

---

## Key Files to Read

1. **This file** - Project overview and status
2. [config.py](config.py) - All configuration options
3. [workflow/graph.py](workflow/graph.py) - Workflow structure
4. [services/reddit_client.py](services/reddit_client.py) - Reddit API integration
5. [api/callback_server.py](api/callback_server.py) - Approval + auto-publish
6. [prompts/templates.yaml](prompts/templates.yaml) - Persona templates

---

**Last Updated:** 2026-01-13  
**Version:** 2.4
