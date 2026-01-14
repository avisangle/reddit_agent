
# PRD v2.1 – Reddit Comment Engagement Agent (Compliance & Anti-Fingerprint)

## Status
Approved for cautious, compliance-first implementation

## Framework & Stack
- LangGraph (agent orchestration)
- Python
- Reddit API (OAuth2, PRAW / REST)
- SQLite (v1) → Postgres (optional)
- Telegram or Discord Webhooks (HITL approvals)

---

## 1. Objective

Build a **compliance-first, anti-fingerprint Reddit engagement agent** that:

- Responds to comment replies on the user’s posts and comments
- Participates in discussions within strictly allow-listed subreddits
- Discovers early-stage, community-validated discussion posts
- Operates under strict volume limits (**≤ 8 comments/day**)
- Uses low-friction **Human-in-the-Loop (HITL)** approvals
- Minimizes bot-detection and shadowban risk through behavioral randomness

This system explicitly avoids karma optimization, vote manipulation, or artificial amplification.

---

## 2. Explicit Non-Goals

The system will not:
- Optimize for karma, upvotes, or engagement metrics
- Automate Reddit chat or DMs
- Comment outside allow-listed subreddits
- Post promotional or self-referential content in v1
- Operate synchronously or fully autonomously

---

## 3. Core Design Principles

1. Subreddit-first, niche-specific behavior
2. Draft → Human Approval → Post
3. Low frequency, high authenticity
4. Vertical-context awareness over broad context
5. Human-like timing and metadata
6. Compliance over cleverness

---

## 4. Subreddit Allow-Listing (Mandatory)

The agent must only operate within explicitly configured subreddits.

```yaml
allowed_subreddits:
  - sysadmin
  - learnpython
  - startups
```

Any content outside this list must be skipped silently.

---

## 5. Comment Reply Handling

### 5.1 Trigger Conditions
- Unread replies to:
  - User’s posts
  - User’s comments

### 5.2 Author Filtering (Mandatory)
Skip replies if:
- author == "AutoModerator"
- author_is_bot == true
- author account is deleted

This prevents bot loops and AutoModerator interactions.

---

### 5.3 Context Loading Strategy (Vertical First)

The agent must **never** load full threads.

**Required context order:**
1. Post title and body
2. Grandparent comment (if exists)
3. Parent comment
4. Target comment being replied to

Sibling comments are optional and secondary.

---

## 6. Discussion Participation (Discovery)

### 6.1 Discovery Sources
- Subreddit → **rising only** (default)

Optional (guarded):
- Subreddit → new (only if poster_account_age > 30 days)

### 6.2 Selection Rules
- Post age < 45 minutes
- Comment count between 3 and 20
- Thread not locked or removed
- No controversial or political keywords

---

## 7. Comment Generation Rules

### 7.1 Tone & Language Constraints
- Peer-to-peer
- Slightly informal, Reddit-native
- Avoid perfect grammar and formal transitions

**Forbidden phrases:**
- “It’s important to note that…”
- “In summary…”
- “Based on my experience…”

---

### 7.2 Few-Shot Style Enforcement (Mandatory)

Persona is enforced using **few-shot examples**, not YAML alone.

**Implementation requirement:**
- Maintain a small database of high-quality human Reddit comments
- Inject 2–3 stylistically relevant examples into the prompt:

```
Write a reply in a similar tone and style to the examples below.
Do not copy content, only match tone and structure.
```

---

## 8. Human-in-the-Loop (HITL)

### 8.1 HITL Requirement
All comments must be approved by a human before posting in v1.

---

### 8.2 HITL Architecture (Low Friction)

**Preferred v1 approach:**
- Telegram or Discord private channel
- Webhook sends:
  - Draft text
  - Subreddit
  - Link to thread

**Actions:**
- ✅ Approve
- ❌ Reject

Approval should be a **1–second mobile action**.

---

### 8.3 HITL Workflow

```
Agent Run
→ Generate Draft
→ Save to DB
→ Send to Telegram/Discord
→ Exit

Approval Event
→ Poster Job publishes comment
```

LangGraph is used only for draft generation.

---

## 9. Timing, Jitter & Anti-Fingerprint Controls

### 9.1 Comment Timing

**Hard rule:**
- Never use fixed delays

**Required implementation:**
```python
sleep_time = random.uniform(900, 3600)  # 15–60 minutes
```

This prevents detectable timing patterns.

---

### 9.2 Volume Limits

- ≤ 8 comments/day
- ≤ 3 comments per run
- Abort run if limits are reached

---

## 10. Reddit API & Metadata Safety

### 10.1 User Agent Requirement (Mandatory)

PRAW must use a **unique, descriptive user agent**:

```
android:com.yourname.redditcommentagent:v2.1 (by /u/YourUsername)
```

Default or generic user agents are forbidden.

---

## 11. State Persistence & Error Awareness

### 11.1 Required Tables

```sql
replied_items (
  reddit_id TEXT PRIMARY KEY,
  subreddit TEXT,
  status TEXT,        -- SUCCESS, SKIPPED, BANNED, FAILED
  last_attempt DATETIME
);

draft_queue (
  draft_id TEXT PRIMARY KEY,
  reddit_id TEXT,
  subreddit TEXT,
  content TEXT,
  status TEXT         -- PENDING, APPROVED, REJECTED
);

error_log (
  reddit_id TEXT,
  error_type TEXT,    -- 403, 429, SHADOWBAN_SUSPECTED
  message TEXT,
  timestamp DATETIME
);

subreddit_rules_cache (
  subreddit TEXT PRIMARY KEY,
  rules TEXT,
  last_updated DATETIME
);
```

Failures must be recorded to prevent retry loops.

---

## 12. Risk Assessment (Post-Mitigation)

| Risk | Level |
|----|----|
| Permanent account ban | Low (5–8%) |
| Shadowban | Medium-Low |
| Comment removals | Expected |
| Subreddit-specific bans | Possible but contained |

---

## 13. Future Scope (v2 – Separate PRD)

- Topic-based search agent
- Indirect product/SaaS promotion (mandatory HITL)
- Separate posting account
- Long-term trust & warm-up modeling

---

## 14. Feasibility Verdict

With the above constraints, this system is:
- Technically feasible
- Resistant to basic bot fingerprinting
- Aligned with Reddit’s enforcement realities
- Appropriately conservative for long-term use
