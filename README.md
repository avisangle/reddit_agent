# Reddit Comment Engagement Agent

A compliance-first, anti-fingerprint Reddit engagement agent that responds to comment replies and participates in allow-listed subreddits with strict volume limits and mandatory human approval.

[![Documentation](https://img.shields.io/badge/Documentation-Visit%20Site-blue)](https://avinashsangle.com/projects/reddit-agent)

## Status: ✅ Fully Operational with Smart Selection

| Metric | Value |
|--------|-------|
| Version | 2.5 |
| Tests | 136 passing |
| LLM | Gemini 2.5 Flash |
| Notifications | Slack, Telegram, Webhook |
| Auto-Publish | ✅ Enabled |
| Migrations | 4 (latest: 004_add_candidate_type_cooldown) |
| Quality Scoring | ✅ AI-powered 7-factor scoring |

## Features

### ✅ Core Functionality
- **Dual-mode engagement** - Reply to both posts and comments
- **Inbox monitoring** - Respond to replies on your posts/comments (HIGH priority)
- **Rising post discovery** - Find engaging posts in allowed subreddits
- **LLM-powered drafts** - Natural, persona-matched responses
- **Auto-publish** - Approved drafts automatically post to Reddit

### ✅ AI-Powered Selection
- **7-factor quality scoring** - Upvote ratio, karma, freshness, velocity, question signal, depth, historical
- **Historical learning** - Learns from past performance per subreddit with time decay
- **Engagement tracking** - Fetches 24h metrics (upvotes, replies) for published comments
- **Inbox priority** - HIGH priority for inbox replies, processed first
- **Subreddit diversity** - Max 2/subreddit, max 1/post with quality overrides
- **Exploration** - 25% randomization to avoid detection patterns

### ✅ Safety & Compliance
- **Volume limits** - ≤8 comments/day, ≤3 per run (hardcoded)
- **Human-in-the-Loop** - All drafts require approval via Slack/Telegram
- **Shadowban detection** - Circuit breaker halts on high risk
- **Subreddit allow-listing** - Only operates in configured subreddits
- **Bot filtering** - Skips AutoModerator and bot accounts
- **Anti-fingerprint** - Random jitter between actions

### ✅ Security
- **Token hashing** - SHA-256 hashed approval tokens
- **Token expiry** - 48-hour TTL on approval links
- **One-time use** - Tokens invalidated after use
- **State machine** - Only valid status transitions allowed
- **Security headers** - Referrer-Policy, X-Frame-Options

### ✅ Operations
- **Structured logging** - JSON logs with auto-redaction
- **Database tracking** - SQLite with Alembic migrations
- **CI/CD** - GitHub Actions + pre-commit hooks
- **Dry-run mode** - Test without posting

## Quick Start

### 1. Installation

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configuration

```bash
cp .env.example .env
# Edit .env with your credentials
```

**Required:**
- Reddit API credentials
- At least one LLM key (Gemini recommended)
- Slack/Telegram webhook URL for notifications
- `PUBLIC_URL` for approval button links

### 3. Database Setup

```bash
alembic upgrade head
```

### 4. Run

```bash
# Terminal 1: Start callback server (handles approvals + auto-publish)
python main.py server

# Terminal 2: Run agent (fetches candidates, generates drafts)
python main.py run --once

# Dry run - no actual posting
python main.py run --once --dry-run
```

## How It Works

```
┌─────────────────────────────────────────────────────────────────────┐
│                   LangGraph 13-Node Workflow                        │
├─────────────────────────────────────────────────────────────────────┤
│ fetch → ratio → score → filter → rules → sort → diversity → limit  │
│                                              ↓                      │
│          notify ← generate ← context ← select                       │
└─────────────────────────────────────────────────────────────────────┘
        │
        ↓ (inbox prioritized, quality-scored, diversity-filtered)
```
                            │
          ┌─────────────────┼─────────────────┐
          ↓                 ↓                 ↓
    ┌──────────┐     ┌──────────┐     ┌──────────┐
    │  Reddit  │     │  Gemini  │     │  Slack   │
    │  Client  │     │   LLM    │     │ Notifier │
    └──────────┘     └──────────┘     └──────────┘
                                            │
                                            ▼
                                    ┌──────────────┐
                                    │ User clicks  │
                                    │ Approve/Reject│
                                    └──────────────┘
                                            │
                                            ▼
                                    ┌──────────────┐
                                    │ Auto-publish │
                                    │ to Reddit    │
                                    └──────────────┘
```

### Approval Flow

1. Agent generates draft → sends to Slack/Telegram with approval buttons
2. User clicks "Approve" → browser opens `/approve?token=...`
3. Draft status changes to APPROVED
4. **Auto-publish**: Draft immediately posted to Reddit in background
5. Draft status changes to PUBLISHED

## Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `REDDIT_CLIENT_ID` | Yes | Reddit OAuth client ID |
| `REDDIT_CLIENT_SECRET` | Yes | Reddit OAuth secret |
| `REDDIT_USERNAME` | Yes | Reddit account username |
| `REDDIT_PASSWORD` | Yes | Reddit account password |
| `REDDIT_USER_AGENT` | Yes | Format: `android:com.name.app:v2.1 (by /u/User)` |
| `ALLOWED_SUBREDDITS` | Yes | Comma-separated list |
| `GEMINI_API_KEY` | * | Gemini API key |
| `OPENAI_API_KEY` | * | OpenAI API key |
| `ANTHROPIC_API_KEY` | * | Anthropic API key |
| `NOTIFICATION_TYPE` | Yes | `slack`, `telegram`, or `webhook` |
| `SLACK_WEBHOOK_URL` | ** | Slack incoming webhook |
| `TELEGRAM_BOT_TOKEN` | ** | Telegram bot token |
| `TELEGRAM_CHAT_ID` | ** | Telegram chat ID |
| `PUBLIC_URL` | Yes | Public URL for approval links |

\* At least one LLM key required  
\** Required based on NOTIFICATION_TYPE

### Safety Limits

```python
max_comments_per_day = 8       # Daily cap
max_comments_per_run = 3       # Per-run cap
post_reply_ratio = 0.3         # 30% posts, 70% comments
shadowban_risk_threshold = 0.7 # Halt threshold
token_ttl_hours = 48           # Approval link expiry
```

## Commands

| Command | Description |
|---------|-------------|
| `python main.py server` | Start callback server with auto-publish |
| `python main.py server --no-auto-publish` | Server without auto-publish |
| `python main.py run --once` | Single workflow run |
| `python main.py run --once --dry-run` | Test without posting |
| `python main.py publish --limit 3` | Manual publish (if auto-publish disabled) |
| `python main.py health` | Show health status |

## Project Structure

```
reddit_agent/
├── config.py              # Settings with validation
├── main.py                # CLI entry point
├── models/                # Database & schemas
├── services/              # Core business logic
│   ├── reddit_client.py   # Reddit API wrapper
│   ├── context_builder.py # Context chain loading
│   ├── rule_engine.py     # Subreddit compliance
│   ├── prompt_manager.py  # Template + PII scrubbing
│   ├── state_manager.py   # State, tokens, idempotency
│   ├── poster.py          # Publish drafts
│   └── notifiers/         # Slack, Telegram, Webhook
├── agents/generator.py    # LLM draft generation
├── workflow/              # LangGraph orchestration
├── api/callback_server.py # HITL approval + auto-publish
├── prompts/templates.yaml # 5 persona templates
└── tests/                 # 136 tests
```

## Testing

```bash
pytest -v                          # All tests
pytest --cov=. --cov-report=html   # With coverage
pytest tests/test_reddit_client.py # Specific file
```

## Deployment

### Local Development (with ngrok)

```bash
# Terminal 1: Start ngrok
ngrok http 8000

# Terminal 2: Start server (use ngrok URL as PUBLIC_URL)
PUBLIC_URL=https://xxxx.ngrok.io python main.py server

# Terminal 3: Run agent
python main.py run --once
```

### Production

1. Deploy callback server to cloud (Railway, Fly.io, etc.)
2. Set `PUBLIC_URL` to your deployed URL
3. Run agent on schedule (cron, GitHub Actions, etc.)

## License

Private project - All rights reserved

---

**⚠️ Use responsibly and ethically. Respect Reddit's Terms of Service.**
