# Reddit Agent Setup Guide

## 1. Prerequisites

- Python 3.11+
- Docker & Docker Compose (optional but recommended)
- A Reddit account
- One LLM API Key (Gemini recommended, or OpenAI/Anthropic)
- A publicly accessible URL for the callback server (ngrok for local dev)

## 2. Reddit API Configuration

1. Log in to Reddit.
2. Go to [https://www.reddit.com/prefs/apps](https://www.reddit.com/prefs/apps).
3. Click **"create another app..."**.
4. Select **script**.
5. Fill in:
   - **name**: `my-reddit-agent`
   - **redirect uri**: `http://localhost:8080` (unused but required)
6. Click **create app**.
7. Note down:
   - **client ID**: string under the app name (e.g., `By3...`)
   - **client secret**: string next to "secret"

## 3. Environment Setup

Copy the example file:
```bash
cp .env.example .env
```

Edit `.env` and fill in your credentials:

```ini
# Reddit API (Required)
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_USERNAME=your_username
REDDIT_PASSWORD=your_password
REDDIT_USER_AGENT=android:com.yourname.agent:v2.1 (by /u/your_username)

# Subreddits (Required)
ALLOWED_SUBREDDITS=sysadmin,learnpython,startups

# LLM (At least one required - Gemini recommended)
GEMINI_API_KEY=your_gemini_key

# Callback Server (Required for approval buttons)
# IMPORTANT: Must be publicly accessible
PUBLIC_URL=https://your-public-url.com

# Notifications
NOTIFICATION_TYPE=slack
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/xxx/yyy/zzz
```

## 4. Callback Server & PUBLIC_URL

The agent uses a **URL-based approval flow**. When drafts are generated, Slack/Telegram notifications include "Approve" and "Reject" buttons that open browser links to your callback server.

### Why PUBLIC_URL is Required

- Approval buttons in notifications link to `{PUBLIC_URL}/approve?token=xxx`
- The callback server must be reachable from your browser
- Without a valid PUBLIC_URL, approval buttons won't work

### Local Development (with ngrok)

```bash
# Terminal 1: Start ngrok tunnel
ngrok http 8000
# Note the https URL (e.g., https://abc123.ngrok.io)

# Terminal 2: Start callback server with ngrok URL
PUBLIC_URL=https://abc123.ngrok.io python main.py server

# Terminal 3: Run agent
python main.py run --once
```

### Production

Set `PUBLIC_URL` to your deployed server URL (e.g., `https://my-agent.railway.app`).

## 5. Notifications

### Slack (Recommended)

1. Go to [api.slack.com/apps](https://api.slack.com/apps)
2. Create New App → From scratch
3. Enable **Incoming Webhooks**
4. Add a webhook to your workspace and copy the URL
5. Set in `.env`:
   ```ini
   NOTIFICATION_TYPE=slack
   SLACK_WEBHOOK_URL=https://hooks.slack.com/services/xxx/yyy/zzz
   ```

**Note:** No Slack App interactivity setup needed! Buttons use URL links, not Slack callbacks.

### Telegram

1. Create a bot via [@BotFather](https://t.me/botfather)
2. Get your chat ID (send a message to your bot, then check `https://api.telegram.org/bot<TOKEN>/getUpdates`)
3. Set in `.env`:
   ```ini
   NOTIFICATION_TYPE=telegram
   TELEGRAM_BOT_TOKEN=your-bot-token
   TELEGRAM_CHAT_ID=your-chat-id
   ```

### Generic Webhook

```ini
NOTIFICATION_TYPE=webhook
WEBHOOK_URL=https://your-webhook-endpoint
WEBHOOK_SECRET=your-hmac-secret
```

## 6. Running the Agent

### Start Callback Server (Terminal 1)

```bash
# With auto-publish (approved drafts post to Reddit automatically)
python main.py server

# Without auto-publish (use manual publish command)
python main.py server --no-auto-publish
```

### Run Agent (Terminal 2)

```bash
# Single run - fetches candidates, generates drafts, sends notifications
python main.py run --once

# Dry run - no actual posting or notifications
python main.py run --once --dry-run
```

### Manual Publish (if auto-publish disabled)

```bash
python main.py publish --limit 3
```

## 7. Approval Flow

```
Agent Run → Generate Draft → Slack/Telegram Notification
                                      ↓
                            User clicks "Approve"
                                      ↓
                            Browser opens /approve?token=xxx
                                      ↓
                            Draft status → APPROVED
                                      ↓
                            Auto-publish to Reddit (background)
                                      ↓
                            Draft status → PUBLISHED
```

### Security Features

| Feature | Description |
|---------|-------------|
| Token Hashing | SHA-256 hash stored, not plaintext |
| Token Expiry | 48-hour TTL |
| One-Time Use | Token invalidated after use |
| State Machine | Only valid transitions allowed |

## 8. Deployment

### Using Docker Compose

```bash
docker-compose up -d --build
```

This starts:
- Callback Server (Port 8000)
- SQLite Database

Run the agent separately or on a schedule.

### Using Railway / Render / Fly.io

1. Fork this repository
2. Connect to your platform
3. Add all environment variables from `.env`
4. Set `PUBLIC_URL` to your deployed URL
5. Deploy!

### Scheduled Runs

For autonomous operation, set up a cron job or scheduled task:

```bash
# Example: Run every 2 hours
0 */2 * * * cd /path/to/reddit_agent && python main.py run --once
```

## 9. Configuration Reference

### Safety Limits

| Variable | Default | Description |
|----------|---------|-------------|
| `MAX_COMMENTS_PER_DAY` | 8 | Daily comment cap |
| `MAX_COMMENTS_PER_RUN` | 3 | Per-run cap |
| `SHADOWBAN_RISK_THRESHOLD` | 0.7 | Halt if risk exceeds |

### Reply Distribution

| Variable | Default | Description |
|----------|---------|-------------|
| `POST_REPLY_RATIO` | 0.3 | 30% posts, 70% comments |
| `MAX_POST_REPLIES_PER_RUN` | 1 | Max post replies per run |
| `MAX_COMMENT_REPLIES_PER_RUN` | 2 | Max comment replies per run |

### Timing

| Variable | Default | Description |
|----------|---------|-------------|
| `MIN_JITTER_SECONDS` | 900 | Min wait between actions (15 min) |
| `MAX_JITTER_SECONDS` | 3600 | Max wait between actions (60 min) |

## 10. Troubleshooting

### Approval buttons don't work

- Ensure `PUBLIC_URL` is set and publicly accessible
- For local dev, use ngrok and set `PUBLIC_URL` to the ngrok URL
- Check that the callback server is running (`python main.py server`)

### "Token expired" error

- Approval links expire after 48 hours
- Re-run the agent to generate new drafts with fresh tokens

### No candidates found

- Check `ALLOWED_SUBREDDITS` is correctly set
- Verify Reddit credentials are valid
- Check if you have any inbox replies or rising posts in allowed subreddits
