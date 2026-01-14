# Quality Scoring & Historical Learning - Implementation Plan

## Overview

This document describes the implementation plan for a quality scoring system that ranks candidates based on engagement potential, plus a historical learning component that improves selection over time based on past performance.

**Version:** 1.0  
**Status:** Proposed  
**Priority:** Medium  

---

## 1. Problem Statement

### Current Behavior

The agent currently selects candidates in the order they are fetched:
1. Inbox replies first
2. Rising posts/comments in fetch order
3. No quality differentiation between candidates

### Issues

- High-quality engagement opportunities may be missed
- No learning from past successes/failures
- Equal treatment of low-value and high-value threads
- No consideration of engagement potential signals

### Goals

1. Score candidates by predicted engagement quality
2. Prioritize candidates most likely to succeed
3. Learn from historical approval/rejection/engagement data
4. Maintain configurability for different use cases

---

## 2. Quality Scoring System

### 2.1 Scoring Factors

Each candidate receives a composite score (0.0 to 1.0) based on weighted factors:

| Factor | Weight | Description |
|--------|--------|-------------|
| **Upvote Ratio** | 0.15 | Post/comment upvote ratio (higher = healthier discussion) |
| **Author Karma** | 0.10 | Author's combined karma (filters low-quality accounts) |
| **Thread Freshness** | 0.20 | How recently the thread was active |
| **Engagement Velocity** | 0.15 | Rate of new comments in the thread |
| **Question Signal** | 0.15 | Contains question marks or help-seeking language |
| **Thread Depth** | 0.10 | Optimal depth for engagement (not too shallow, not too deep) |
| **Historical Subreddit Score** | 0.15 | Learned score based on past performance in this subreddit |

**Total Weight:** 1.0

### 2.2 Factor Definitions

#### Upvote Ratio (0.15)
- **Source:** `submission.upvote_ratio` or `comment.score`
- **Scoring:**
  - `>= 0.90` → 1.0 (excellent reception)
  - `>= 0.75` → 0.8 (good reception)
  - `>= 0.60` → 0.5 (mixed reception)
  - `< 0.60` → 0.2 (controversial - risky)
- **Default Thresholds:**
  - `SCORE_UPVOTE_EXCELLENT=0.90`
  - `SCORE_UPVOTE_GOOD=0.75`
  - `SCORE_UPVOTE_MIXED=0.60`

#### Author Karma (0.10)
- **Source:** `author.link_karma + author.comment_karma`
- **Scoring:**
  - `>= 10000` → 1.0 (established user)
  - `>= 1000` → 0.8 (active user)
  - `>= 100` → 0.5 (regular user)
  - `< 100` → 0.3 (new/low-activity account)
- **Default Thresholds:**
  - `SCORE_KARMA_ESTABLISHED=10000`
  - `SCORE_KARMA_ACTIVE=1000`
  - `SCORE_KARMA_REGULAR=100`
- **Note:** Very low karma may indicate throwaway or spam accounts

#### Thread Freshness (0.20)
- **Source:** Time since last activity (post created or last comment)
- **Scoring:**
  - `< 15 min` → 1.0 (hot thread)
  - `< 30 min` → 0.8 (active thread)
  - `< 60 min` → 0.6 (warm thread)
  - `< 120 min` → 0.4 (cooling down)
  - `>= 120 min` → 0.2 (stale)
- **Default Thresholds (seconds):**
  - `SCORE_FRESHNESS_HOT=900`
  - `SCORE_FRESHNESS_ACTIVE=1800`
  - `SCORE_FRESHNESS_WARM=3600`
  - `SCORE_FRESHNESS_COOLING=7200`

#### Engagement Velocity (0.15)
- **Source:** `num_comments / post_age_minutes`
- **Scoring:**
  - `>= 1.0 comments/min` → 1.0 (viral)
  - `>= 0.5 comments/min` → 0.8 (high engagement)
  - `>= 0.2 comments/min` → 0.6 (moderate engagement)
  - `>= 0.1 comments/min` → 0.4 (low engagement)
  - `< 0.1 comments/min` → 0.2 (minimal activity)
- **Default Thresholds:**
  - `SCORE_VELOCITY_VIRAL=1.0`
  - `SCORE_VELOCITY_HIGH=0.5`
  - `SCORE_VELOCITY_MODERATE=0.2`
  - `SCORE_VELOCITY_LOW=0.1`

#### Question Signal (0.15)
- **Source:** Text analysis of title/body
- **Scoring:**
  - Contains `?` in title → +0.4
  - Contains help keywords (`how do I`, `help`, `advice`, `recommend`, `suggest`, `anyone know`) → +0.3
  - Contains problem keywords (`issue`, `problem`, `error`, `stuck`, `struggling`) → +0.3
  - No signals → 0.2
- **Capped at 1.0**
- **Default Keywords (configurable):**
  - `SCORE_HELP_KEYWORDS=how do I,help,advice,recommend,suggest,anyone know`
  - `SCORE_PROBLEM_KEYWORDS=issue,problem,error,stuck,struggling,trouble`

#### Thread Depth (0.10)
- **Source:** Number of comments in thread
- **Scoring (optimal engagement window):**
  - `5-15 comments` → 1.0 (ideal - enough context, room to contribute)
  - `3-5 comments` → 0.8 (early but viable)
  - `15-30 comments` → 0.7 (getting crowded)
  - `< 3 comments` → 0.4 (too early, may die)
  - `> 30 comments` → 0.3 (too crowded, low visibility)
- **Default Thresholds:**
  - `SCORE_DEPTH_IDEAL_MIN=5`
  - `SCORE_DEPTH_IDEAL_MAX=15`
  - `SCORE_DEPTH_EARLY_MIN=3`
  - `SCORE_DEPTH_CROWDED_MAX=30`

#### Historical Subreddit Score (0.15)
- **Source:** Learned from past performance (see Section 3)
- **Scoring:** Weighted average of past outcomes in this subreddit
- **Default:** 0.5 (neutral) for new subreddits with no history

### 2.3 Composite Score Calculation

```
final_score = (
    upvote_score * 0.15 +
    karma_score * 0.10 +
    freshness_score * 0.20 +
    velocity_score * 0.15 +
    question_score * 0.15 +
    depth_score * 0.10 +
    historical_score * 0.15
)
```

### 2.4 Score Weights Configuration

All weights should be configurable via environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `SCORE_WEIGHT_UPVOTE` | 0.15 | Weight for upvote ratio factor |
| `SCORE_WEIGHT_KARMA` | 0.10 | Weight for author karma factor |
| `SCORE_WEIGHT_FRESHNESS` | 0.20 | Weight for thread freshness factor |
| `SCORE_WEIGHT_VELOCITY` | 0.15 | Weight for engagement velocity factor |
| `SCORE_WEIGHT_QUESTION` | 0.15 | Weight for question signal factor |
| `SCORE_WEIGHT_DEPTH` | 0.10 | Weight for thread depth factor |
| `SCORE_WEIGHT_HISTORICAL` | 0.15 | Weight for historical learning factor |

**Validation:** Weights must sum to 1.0 (normalized if not)

### 2.5 Minimum Score Threshold

Candidates below a minimum score should be filtered out:

| Variable | Default | Description |
|----------|---------|-------------|
| `SCORE_MINIMUM_THRESHOLD` | 0.35 | Minimum score to be considered |
| `SCORE_MINIMUM_FOR_POST` | 0.40 | Higher threshold for post replies |

---

## 3. Historical Performance Learning

### 3.1 Data Collection

Track outcomes for every draft generated:

| Event | Data Captured |
|-------|---------------|
| **Draft Generated** | subreddit, candidate_type, quality_score, timestamp |
| **Draft Approved** | approval_time, approver (if tracked) |
| **Draft Rejected** | rejection_time, reason (if provided) |
| **Draft Published** | publish_time, comment_id |
| **Engagement Received** | upvotes, replies (checked after 24h) |

### 3.2 New Database Table: `performance_history`

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER | Primary key |
| `draft_id` | VARCHAR | Reference to draft |
| `subreddit` | VARCHAR | Subreddit name |
| `candidate_type` | VARCHAR | "post" or "comment" |
| `quality_score` | FLOAT | Score at time of selection |
| `outcome` | VARCHAR | APPROVED, REJECTED, PUBLISHED, IGNORED |
| `engagement_score` | FLOAT | Post-publish engagement (nullable) |
| `upvotes_24h` | INTEGER | Upvotes after 24 hours (nullable) |
| `replies_24h` | INTEGER | Replies received after 24 hours (nullable) |
| `created_at` | TIMESTAMP | When draft was created |
| `outcome_at` | TIMESTAMP | When outcome was determined |

### 3.3 Subreddit Performance Aggregation

Maintain rolling statistics per subreddit:

| Metric | Calculation |
|--------|-------------|
| **Approval Rate** | approved_count / total_drafts |
| **Publish Rate** | published_count / approved_count |
| **Avg Engagement** | mean(engagement_score) for published |
| **Success Rate** | (upvotes_24h >= 5) / published_count |

### 3.4 Historical Score Calculation

For each subreddit, calculate a historical performance score:

```
historical_score = (
    approval_rate * 0.30 +
    publish_rate * 0.20 +
    normalized_engagement * 0.30 +
    success_rate * 0.20
)
```

**Decay Factor:** Recent outcomes weighted more heavily than old ones
- Last 7 days: weight 1.0
- 7-30 days: weight 0.7
- 30-90 days: weight 0.4
- Older: weight 0.2

**Minimum Sample Size:** Require at least 5 outcomes before using historical score (otherwise use default 0.5)

### 3.5 Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `LEARNING_ENABLED` | true | Enable/disable historical learning |
| `LEARNING_MIN_SAMPLES` | 5 | Minimum samples before using learned score |
| `LEARNING_DECAY_RECENT_DAYS` | 7 | Days considered "recent" |
| `LEARNING_DECAY_MEDIUM_DAYS` | 30 | Days considered "medium-term" |
| `LEARNING_DECAY_OLD_DAYS` | 90 | Days considered "old" |
| `LEARNING_WEIGHT_APPROVAL` | 0.30 | Weight for approval rate |
| `LEARNING_WEIGHT_PUBLISH` | 0.20 | Weight for publish rate |
| `LEARNING_WEIGHT_ENGAGEMENT` | 0.30 | Weight for engagement score |
| `LEARNING_WEIGHT_SUCCESS` | 0.20 | Weight for success rate |

### 3.6 Engagement Tracking Job

A background job to fetch engagement metrics for published comments:

**Trigger:** Run 24 hours after each comment is published

**Process:**
1. Query `draft_queue` for PUBLISHED drafts where `engagement_checked = false`
2. For each draft, fetch the comment from Reddit API
3. Record upvotes, reply count
4. Calculate engagement_score: `log(upvotes + 1) + (replies * 2)`
5. Update `performance_history` table
6. Mark `engagement_checked = true`

**Configuration:**
| Variable | Default | Description |
|----------|---------|-------------|
| `ENGAGEMENT_CHECK_DELAY_HOURS` | 24 | Hours to wait before checking engagement |
| `ENGAGEMENT_CHECK_ENABLED` | true | Enable/disable engagement tracking |

---

## 4. Implementation Phases

### Phase 1: Quality Scoring (Week 1)

**Files to Create/Modify:**
- `services/quality_scorer.py` - New scoring service
- `config.py` - Add scoring configuration variables
- `workflow/nodes.py` - Integrate scoring into candidate selection

**Tasks:**
1. Create `QualityScorer` class with all factor calculations
2. Add configuration variables to `config.py`
3. Create `score_candidate()` method that returns composite score
4. Modify `fetch_candidates_node` to score all candidates
5. Add new `sort_by_score_node` after filtering
6. Update `select_candidate_node` to pick highest-scored candidate
7. Add logging for score breakdown

**Testing:**
- Unit tests for each scoring factor
- Integration test for composite scoring
- Test configuration overrides

### Phase 2: Historical Data Collection (Week 2)

**Files to Create/Modify:**
- `models/database.py` - Add `performance_history` table
- `migrations/` - New Alembic migration
- `services/state_manager.py` - Add performance tracking methods
- `api/callback_server.py` - Record approval/rejection outcomes

**Tasks:**
1. Create `performance_history` table schema
2. Generate Alembic migration
3. Add `record_outcome()` method to StateManager
4. Update approval endpoint to record outcomes
5. Update rejection endpoint to record outcomes
6. Update poster to record publish outcomes

**Testing:**
- Verify data is recorded correctly
- Test outcome state transitions

### Phase 3: Historical Learning (Week 3)

**Files to Create/Modify:**
- `services/performance_tracker.py` - New learning service
- `services/quality_scorer.py` - Integrate historical scores
- `config.py` - Add learning configuration

**Tasks:**
1. Create `PerformanceTracker` class
2. Implement subreddit aggregation queries
3. Implement decay-weighted scoring
4. Integrate historical score into `QualityScorer`
5. Add cache for performance scores (avoid repeated DB queries)

**Testing:**
- Test with mock historical data
- Verify decay calculations
- Test minimum sample threshold

### Phase 4: Engagement Tracking (Week 4)

**Files to Create/Modify:**
- `services/engagement_checker.py` - New background job
- `main.py` - Add CLI command for engagement check
- `models/database.py` - Add engagement columns to draft_queue

**Tasks:**
1. Create engagement checking service
2. Add `check-engagement` CLI command
3. Implement Reddit API calls to fetch comment stats
4. Calculate and store engagement scores
5. Add scheduling documentation

**Testing:**
- Mock Reddit API responses
- Test engagement score calculation
- Verify database updates

---

## 5. Configuration Summary

### Scoring Weights (.env)

```ini
# Quality Scoring Weights (must sum to 1.0)
SCORE_WEIGHT_UPVOTE=0.15
SCORE_WEIGHT_KARMA=0.10
SCORE_WEIGHT_FRESHNESS=0.20
SCORE_WEIGHT_VELOCITY=0.15
SCORE_WEIGHT_QUESTION=0.15
SCORE_WEIGHT_DEPTH=0.10
SCORE_WEIGHT_HISTORICAL=0.15

# Minimum Score Thresholds
SCORE_MINIMUM_THRESHOLD=0.35
SCORE_MINIMUM_FOR_POST=0.40
```

### Scoring Factor Thresholds (.env)

```ini
# Upvote Ratio Thresholds
SCORE_UPVOTE_EXCELLENT=0.90
SCORE_UPVOTE_GOOD=0.75
SCORE_UPVOTE_MIXED=0.60

# Author Karma Thresholds
SCORE_KARMA_ESTABLISHED=10000
SCORE_KARMA_ACTIVE=1000
SCORE_KARMA_REGULAR=100

# Thread Freshness Thresholds (seconds)
SCORE_FRESHNESS_HOT=900
SCORE_FRESHNESS_ACTIVE=1800
SCORE_FRESHNESS_WARM=3600
SCORE_FRESHNESS_COOLING=7200

# Engagement Velocity Thresholds (comments/minute)
SCORE_VELOCITY_VIRAL=1.0
SCORE_VELOCITY_HIGH=0.5
SCORE_VELOCITY_MODERATE=0.2
SCORE_VELOCITY_LOW=0.1

# Thread Depth Thresholds
SCORE_DEPTH_IDEAL_MIN=5
SCORE_DEPTH_IDEAL_MAX=15
SCORE_DEPTH_EARLY_MIN=3
SCORE_DEPTH_CROWDED_MAX=30

# Question Signal Keywords
SCORE_HELP_KEYWORDS=how do I,help,advice,recommend,suggest,anyone know
SCORE_PROBLEM_KEYWORDS=issue,problem,error,stuck,struggling,trouble
```

### Historical Learning (.env)

```ini
# Learning System
LEARNING_ENABLED=true
LEARNING_MIN_SAMPLES=5
LEARNING_DECAY_RECENT_DAYS=7
LEARNING_DECAY_MEDIUM_DAYS=30
LEARNING_DECAY_OLD_DAYS=90

# Learning Weights
LEARNING_WEIGHT_APPROVAL=0.30
LEARNING_WEIGHT_PUBLISH=0.20
LEARNING_WEIGHT_ENGAGEMENT=0.30
LEARNING_WEIGHT_SUCCESS=0.20

# Engagement Tracking
ENGAGEMENT_CHECK_ENABLED=true
ENGAGEMENT_CHECK_DELAY_HOURS=24
```

---

## 6. Workflow Changes

### Current Flow
```
fetch_candidates → filter_candidates → select_by_ratio → check_daily_limit → select_candidate → ...
```

### New Flow
```
fetch_candidates → score_candidates → filter_candidates → select_by_ratio → sort_by_score → check_daily_limit → select_candidate → ...
```

### New Nodes

| Node | Position | Purpose |
|------|----------|---------|
| `score_candidates_node` | After fetch | Calculate quality score for each candidate |
| `sort_by_score_node` | After select_by_ratio | Sort candidates by score descending |

---

## 7. Observability

### Logging

Add structured logging for scoring decisions:

```json
{
  "event": "candidate_scored",
  "reddit_id": "abc123",
  "subreddit": "learnpython",
  "scores": {
    "upvote": 0.8,
    "karma": 0.5,
    "freshness": 1.0,
    "velocity": 0.6,
    "question": 0.7,
    "depth": 0.8,
    "historical": 0.55
  },
  "final_score": 0.72,
  "selected": true
}
```

### Metrics

Track in `daily_stats` or new metrics table:

- Average quality score of selected candidates
- Score distribution (histogram)
- Historical score trend per subreddit
- Approval rate vs. quality score correlation

---

## 8. Future Enhancements

### Not in Scope (v1)

1. **ML-based Scoring** - Train a model on historical data to predict engagement
2. **Author Relationship Tracking** - Avoid repeatedly engaging same authors
3. **Semantic Deduplication** - Use embeddings to detect similar threads
4. **Topic Relevance Matching** - Score based on persona expertise areas
5. **Time-of-Day Optimization** - Learn best times to engage per subreddit

### Potential v2 Features

- A/B testing of scoring weights
- Per-subreddit weight customization
- Automatic weight tuning based on outcomes
- Dashboard for performance visualization

---

## 9. Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Over-optimization leads to obvious patterns | Shadowban risk | Keep minimum randomness, don't always pick top score |
| Historical data biases toward certain subreddits | Missed opportunities | Exploration factor: occasionally pick lower-scored candidates |
| Reddit API rate limits for engagement checking | Feature degradation | Batch checks, respect rate limits, graceful degradation |
| Complex scoring slows down candidate selection | Performance impact | Cache scores, optimize DB queries |

### Exploration vs. Exploitation

To prevent over-optimization and maintain behavioral diversity:

| Variable | Default | Description |
|----------|---------|-------------|
| `SCORE_EXPLORATION_RATE` | 0.15 | 15% chance to pick random candidate instead of top |
| `SCORE_TOP_N_RANDOM` | 3 | When exploring, pick randomly from top N candidates |

---

## 10. Success Criteria

| Metric | Target | Measurement |
|--------|--------|-------------|
| Approval Rate | +20% vs. baseline | Compare 30 days before/after |
| Engagement (upvotes) | +30% average | Mean upvotes on published comments |
| Reply Rate | +25% | Percentage of comments receiving replies |
| Subreddit Learning Accuracy | >70% | Predicted vs. actual approval rate |

---

**Document Created:** 2025-01-14  
**Author:** AI Assistant  
**Review Status:** Pending
