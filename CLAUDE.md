# CLAUDE.md - AI Assistant Context

This file provides context for AI assistants working on the Reddit Comment Engagement Agent project.

## Project Overview

| Field | Value |
|-------|-------|
| **Name** | Reddit Comment Engagement Agent |
| **Version** | 2.5 |
| **Status** | ✅ Fully Operational with Smart Selection |
| **Architecture** | LangGraph-based agent with AI-powered quality scoring |
| **Tests** | 136 tests passing |
| **Migrations** | 4 (latest: 004_add_candidate_type_cooldown) |

### Purpose

A compliance-first, anti-fingerprint Reddit engagement agent that:
- Responds to comment replies on user's posts and comments
- Participates in discussions within strictly allow-listed subreddits
- Operates under strict volume limits (≤8 comments/day)
- Uses mandatory Human-in-the-Loop (HITL) approvals via Slack/Telegram
- **Auto-publishes approved drafts to Reddit**
- Minimizes bot-detection and shadowban risk

### How to Run

**IMPORTANT**: Always activate the virtual environment before running any Python commands!

```bash
# Activate virtual environment (REQUIRED for all Python commands)
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate  # Windows

# Start the callback server (handles approvals + auto-publish)
python main.py server

# In another terminal: Run agent to fetch candidates and generate drafts
python main.py run --once

# Dry run mode (no actual posting)
python main.py run --once --dry-run

# Manual publish (if auto-publish disabled)
python main.py publish --limit 3
```

### Virtual Environment

**Location**: `/Users/avinashsangle/AI/Personal/reddit_agent/venv/`

**Critical**: ALL Python commands (python, pip, pytest, alembic) MUST be run with the venv activated. This includes:
- Installing packages: `source venv/bin/activate && pip install <package>`
- Running scripts: `source venv/bin/activate && python main.py`
- Database migrations: `source venv/bin/activate && alembic upgrade head`
- Running tests: `source venv/bin/activate && pytest`

**Never run**: `pip install` or `python` commands without activating venv first!

---

## Implementation Status

### ✅ Complete

| Component | Description |
|-----------|-------------|
| **Config** | Pydantic settings with validation, auto `.env` loading |
| **Database** | 6 SQLAlchemy tables with Alembic migrations (4 versions) |
| **Logging** | Structured JSON logging with auto-redaction |
| **Reddit Client** | PRAW wrapper with shadowban detection, bot filtering |
| **Context Builder** | Vertical-first context loading |
| **Rule Engine** | Subreddit compliance with cache |
| **Prompt Manager** | YAML templates, 5 personas, PII scrubbing |
| **Generator** | Gemini 2.5 Flash LLM integration |
| **State Manager** | Idempotency, separate cooldowns (6h inbox / 24h rising) |
| **Notifiers** | Slack, Telegram, Webhook - all with URL-based approval |
| **Workflow** | LangGraph with 13 nodes, quality-driven selection |
| **Post Replies** | Direct post reply support with configurable ratio |
| **HITL Approval** | URL-based approval flow (no Slack App required) |
| **Auto-Publish** | Approved drafts auto-post to Reddit |
| **Security** | Hashed tokens, 48h TTL, one-time use, state machine |
| **Quality Scoring** | 7-factor AI scoring (upvote ratio, karma, freshness, velocity, question signal, depth, historical) |
| **Historical Learning** | Learns from past performance per subreddit with decay weighting |
| **Engagement Tracking** | Fetches 24h metrics (upvotes, replies) for published comments |
| **Inbox Priority** | HIGH priority tagging for inbox replies (Phase A) |
| **Subreddit Diversity** | Max 2/subreddit, max 1/post with quality overrides (Phase B) |
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

## Workflow Nodes (13-Node Pipeline)

```
fetch_candidates → select_by_ratio → score_candidates → filter_candidates →
check_rules → sort_by_score → diversity_select → check_daily_limit →
select_candidate → build_context → generate_draft → notify_human → (loop or end)
```

| Node | Purpose |
|------|---------|
| `fetch_candidates` | Get inbox replies (HIGH priority) + rising posts/comments |
| `select_by_ratio` | Apply post/comment ratio distribution (30% posts, 70% comments) |
| `score_candidates` | AI scoring with 7 factors (quality_score) |
| `filter_candidates` | Remove already-replied items and those in cooldown |
| `check_rules` | Verify subreddit compliance |
| `sort_by_score` | Sort by (priority, quality_score) with 25% exploration |
| `diversity_select` | Apply diversity (max 2/subreddit, max 1/post) |
| `check_daily_limit` | Enforce ≤8 comments/day limit |
| `select_candidate` | Pick next candidate to process |
| `build_context` | Load vertical context chain |
| `generate_draft` | LLM generates reply draft |
| `notify_human` | Send to Slack/Telegram for approval |
| `(loop)` | Loop back to check_daily_limit if more candidates remain |

---

## Database Tables

| Table | Purpose |
|-------|---------|
| `replied_items` | Track processed Reddit items with candidate_type for cooldowns |
| `draft_queue` | Drafts with approval_token_hash, status, performance fields |
| `subreddit_rules_cache` | Cached subreddit rules |
| `error_log` | Error tracking for debugging |
| `daily_stats` | Daily comment count tracking |
| `performance_history` | Draft outcomes and 24h engagement metrics for learning |

---

## Commands Reference

| Command | Description |
|---------|-------------|
| `python main.py server` | Start callback server with auto-publish |
| `python main.py server --no-auto-publish` | Server without auto-publish |
| `python main.py run --once` | Single workflow run with quality scoring |
| `python main.py run --once --dry-run` | Test without posting |
| `python main.py publish --limit 3` | Manual publish approved drafts |
| `python main.py check-engagement --limit 50` | Check 24h engagement metrics for published drafts |
| `python main.py health` | Show health status |
| `pytest -v` | Run tests (136 tests) |
| `alembic upgrade head` | Apply migrations (current: 004) |

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

## Quality Scoring & Intelligent Selection

### Phase 1-4: Quality Scoring System
- **7-factor scoring**: Upvote ratio, author karma, freshness, velocity, question signal, thread depth, historical performance
- **Historical learning**: Learns from past outcomes per subreddit with time-decay weighting
- **Engagement tracking**: Fetches 24h metrics (upvotes, replies) for published comments
- **Exploration rate**: 25% randomization to avoid patterns

### Phase A: Inbox Priority System
- **HIGH priority**: Inbox replies tagged HIGH, processed before rising content
- **Separate cooldowns**: 6h for inbox (forgiving), 24h for rising content
- **Priority sorting**: Sort by (priority, quality_score) tuple

### Phase B: Subreddit Diversity System
- **Max 2 per subreddit**: Flexible limit with quality boost override (≥0.75)
- **Max 1 per post**: Strict limit to prevent spam
- **Quality override**: Exceptional candidates (score ≥0.75) can bypass subreddit limit

### Configuration (.env)

```bash
# Phase A: Inbox Priority
INBOX_PRIORITY_ENABLED=True
INBOX_COOLDOWN_HOURS=6
RISING_COOLDOWN_HOURS=24

# Phase B: Diversity
DIVERSITY_ENABLED=True
MAX_PER_SUBREDDIT=2
MAX_PER_POST=1
DIVERSITY_QUALITY_BOOST_THRESHOLD=0.75

# Exploration (Phase B)
SCORE_EXPLORATION_RATE=0.25  # 25% randomization
SCORE_TOP_N_RANDOM=5  # Randomize top 5
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

## Documentation

### Dual Documentation Approach

This project uses a hybrid documentation strategy to serve both public-facing users and local development:

**📚 Bio Site Documentation** (Public)
- **URL**: [https://avinashsangle.com/projects/reddit-agent](https://avinashsangle.com/projects/reddit-agent)
- **Purpose**: Comprehensive public-facing guide for users discovering the project
- **Content**:
  - Complete setup and installation guide
  - Configuration walkthrough
  - Architecture overview
  - Web dashboard features
  - FAQ and troubleshooting
  - SEO-optimized for search engines
- **Audience**: First-time users, researchers, potential collaborators

**💻 Local Documentation** (Development)
- **Location**: `web-app/docs/` (Next.js app)
- **Run**: `cd web-app/docs && npm install && npm run dev`
- **Port**: localhost:3001 (separate from main web-app)
- **Purpose**: Technical reference with live examples
- **Content**: Same as bio site but with interactive admin UI access
- **Audience**: Developers running the project locally

**🔗 Cross-Linking**
- README.md includes badge linking to bio site
- Bio site links back to GitHub repo
- Both documentation sources kept in sync quarterly

**✅ Maintenance**
- Update bio site page when major features added
- Refresh screenshots when UI changes
- Add FAQ entries from user feedback
- Keep tech stack versions current

---

## Key Files to Read

1. **This file** - Project overview and status
2. [config.py](config.py) - All configuration options
3. [workflow/graph.py](workflow/graph.py) - Workflow structure
4. [services/reddit_client.py](services/reddit_client.py) - Reddit API integration
5. [api/callback_server.py](api/callback_server.py) - Approval + auto-publish
6. [prompts/templates.yaml](prompts/templates.yaml) - Persona templates

---

**Last Updated:** 2026-01-30
**Version:** 2.5
**Features:** Quality Scoring + Historical Learning + Inbox Priority + Subreddit Diversity
