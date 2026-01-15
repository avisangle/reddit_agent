# Architectural Decisions Log

## ADR-001: Quality Scoring System Architecture (2026-01-14)

### Context
Need to implement quality scoring and historical learning system to prioritize Reddit engagement candidates based on success probability rather than FIFO order.

### Decision
Implement as 4-phase system with feature flags for safe rollout:
1. **Phase 1**: Quality scoring with 7 factors
2. **Phase 2**: Performance data collection
3. **Phase 3**: Historical learning
4. **Phase 4**: Engagement tracking

### Key Architectural Decisions

#### 1. Injection Point for Scoring
**Decision**: Add two new workflow nodes between `select_by_ratio` and `filter_candidates`:
- `score_candidates_node` - Calculate scores
- `sort_by_score_node` - Sort by score with exploration logic

**Rationale**:
- Scores candidates before filtering removes any
- Works with full candidate set
- Minimal changes to existing workflow
- Can be disabled via feature flag without breaking workflow

**Alternative Considered**: Modify `select_candidate_node` directly
**Rejected Because**: Would require re-sorting on every iteration (inefficient)

#### 2. Immutable Dataclass Handling
**Decision**: Use `dataclasses.replace()` to attach `quality_score` field to candidates

**Rationale**:
- Maintains immutability of dataclass pattern
- No need to modify underlying PRAW objects
- Clear separation of concerns

**Alternative Considered**: Make dataclasses mutable
**Rejected Because**: Would violate existing architecture patterns

#### 3. Exploration vs Exploitation
**Decision**: Implement 15% exploration rate - randomly select from top N candidates

**Rationale**:
- Prevents detectable patterns that could lead to shadowban
- Maintains behavioral diversity
- Allows system to discover new opportunities
- Configurable via `SCORE_EXPLORATION_RATE` env var

**Alternative Considered**: Always pick top-scored candidate
**Rejected Because**: Creates predictable patterns, shadowban risk

#### 4. Historical Learning Storage
**Decision**: Create separate `performance_history` table instead of extending `draft_queue`

**Rationale**:
- Separation of concerns (drafts vs performance metrics)
- Allows multiple metric samples over time
- Easier to query for aggregations
- Can track metrics independently of draft lifecycle

**Alternative Considered**: Extend `draft_queue` with all performance fields
**Rejected Because**: Would bloat draft_queue table, mixing concerns

#### 5. Decay Weighting for Historical Learning
**Decision**: Use time-based decay weights (1.0 → 0.7 → 0.4 → 0.2) for 7/30/90+ day buckets

**Rationale**:
- Recent data more relevant than old data
- Reddit communities evolve over time
- Subreddit rules and culture change
- Prevents overfitting to outdated patterns

**Alternative Considered**: Equal weighting for all historical data
**Rejected Because**: Would give too much weight to stale patterns

#### 6. Minimum Sample Size
**Decision**: Require 5 samples before using historical score, else return 0.5 (neutral)

**Rationale**:
- Prevents premature optimization on insufficient data
- Avoids overfitting to small sample size
- 5 samples gives enough signal without requiring months of data
- Neutral 0.5 score doesn't penalize new subreddits

**Alternative Considered**: Use historical score from first sample
**Rejected Because**: High variance with small sample size

#### 7. Scoring Factor Weights
**Decision**: Weighted composite with freshness=0.20 (highest), karma=0.10 (lowest)

**Rationale**:
- Freshness most important (engage while thread is active)
- Historical learning at 0.15 (significant but not dominant)
- All weights configurable via .env for tuning
- Weights normalized in constructor (handles misconfiguration)

**Alternative Considered**: Equal weights for all factors
**Rejected Because**: Not all factors equally important for success

#### 8. Feature Flags Strategy
**Decision**: Independent flags for each phase: `QUALITY_SCORING_ENABLED`, `LEARNING_ENABLED`, `ENGAGEMENT_CHECK_ENABLED`

**Rationale**:
- Safe rollout (can enable incrementally)
- Graceful degradation (workflow works with flags off)
- Easy rollback if issues detected
- Can disable learning without disabling scoring

**Alternative Considered**: Single master flag
**Rejected Because**: All-or-nothing approach too risky

#### 9. Caching Strategy
**Decision**: Cache historical scores for 5 minutes per subreddit

**Rationale**:
- Avoids repeated DB queries during workflow runs
- Historical scores don't change rapidly
- 5 min TTL balances freshness vs performance
- Low memory footprint (only active subreddits cached)

**Alternative Considered**: No caching
**Rejected Because**: Would cause performance issues with DB queries

#### 10. Service Instantiation Pattern
**Decision**: Stateless services with dependency injection via `functools.partial()`

**Rationale**:
- Consistent with existing architecture
- Easy to test (mock dependencies)
- Services composable
- No shared state issues

**Alternative Considered**: Singleton services with global state
**Rejected Because**: Would make testing difficult, violate existing patterns

### Impact
- No breaking changes to existing workflow
- All new DB columns nullable or have defaults
- Backward compatible (old code paths remain functional)
- Can deploy with features disabled for validation

### Status
✅ Approved - Implementation in progress

## ADR-002: Quality Scorer Error Handling (2026-01-14)

### Context
During Phase 1 implementation, need to handle errors in scoring gracefully to avoid workflow failures.

### Decision
Wrap each scoring method in try/except and return 0.5 (neutral) on error. Also wrap overall score_candidate() method.

**Rationale**:
- Scoring failures shouldn't break the entire workflow
- 0.5 neutral score allows candidate to continue (not rejected, not prioritized)
- Detailed error logging for debugging
- Maintains workflow resilience

**Implementation**:
```python
try:
    score = self._score_upvote_ratio(candidate)
except Exception as e:
    logger.warning("upvote_ratio_scoring_failed", error=str(e))
    return 0.5
```

### Impact
- Workflow continues even if scoring fails
- Candidates with failed scoring get neutral priority
- No silent failures (all errors logged)

### Status
✅ Implemented in Phase 1

## ADR-003: Keyword Pattern Compilation (2026-01-14)

### Context
Question signal scoring needs to search for multiple keywords in text, which could be inefficient if done repeatedly.

### Decision
Compile regex patterns once in __init__() and reuse for all candidates.

**Rationale**:
- Regex compilation is expensive
- Keywords are static configuration
- Significant performance improvement for high-volume scoring
- Pattern object is thread-safe

**Implementation**:
```python
help_keywords = [k.strip() for k in settings.score_help_keywords.split(',')]
self._help_pattern = re.compile(
    '|'.join(re.escape(kw) for kw in help_keywords),
    re.IGNORECASE
)
```

### Impact
- Faster scoring (patterns compiled once)
- No performance degradation with scale
- Memory footprint: negligible (2 compiled patterns)

### Status
✅ Implemented in Phase 1
