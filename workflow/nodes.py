"""
Workflow nodes for the agent graph.

Each node performs a specific step in the processing pipeline.
"""
from typing import Any, Dict, List, Optional
from functools import partial
from dataclasses import replace

from utils.logging import get_logger

logger = get_logger(__name__)


def fetch_candidates_node(
    state: Any,
    reddit_client: Any,
    settings: Any = None
) -> Dict[str, Any]:
    """
    Fetch candidate posts and comments from Reddit.

    Sources:
    - Inbox replies to our comments (comments only)
    - Rising posts as post candidates
    - Rising post comments as comment candidates (one per post for diversity)
    """
    post_candidates = []
    comment_candidates = []
    errors = []

    # Clear cache at the start of each workflow run to ensure fresh data
    # This prevents duplicate API calls when fetching posts and comments
    reddit_client.clear_cache()

    # Get one_per_post setting
    one_per_post = True
    if settings:
        one_per_post = getattr(settings, 'one_comment_per_post', True)

    # Fetch inbox replies (comments only)
    try:
        inbox_candidates = reddit_client.fetch_inbox_replies(limit=25)
        # Tag inbox candidates with HIGH priority (Phase A)
        inbox_candidates = [replace(c, priority="HIGH") for c in inbox_candidates]
        comment_candidates.extend(inbox_candidates)
        logger.info("inbox_candidates_fetched", count=len(inbox_candidates), priority="HIGH")
    except Exception as e:
        logger.error("inbox_fetch_failed", error=str(e))
        errors.append(f"Inbox fetch failed: {e}")
    
    # Fetch rising posts as post candidates
    try:
        rising_posts = reddit_client.fetch_rising_posts_as_candidates(limit_per_subreddit=5)
        post_candidates.extend(rising_posts)
        logger.info("post_candidates_fetched", count=len(rising_posts))
    except Exception as e:
        logger.error("post_candidates_fetch_failed", error=str(e))
        errors.append(f"Post candidates fetch failed: {e}")
    
    # Fetch rising post comments (one per post for diversity)
    try:
        rising_comments = reddit_client.fetch_rising_candidates(
            limit_per_subreddit=5,
            one_per_post=one_per_post
        )
        comment_candidates.extend(rising_comments)
        logger.info("rising_candidates_fetched", count=len(rising_comments))
    except Exception as e:
        logger.error("rising_fetch_failed", error=str(e))
        errors.append(f"Rising fetch failed: {e}")
    
    # Deduplicate each pool by reddit_id
    def deduplicate(candidates):
        seen_ids = set()
        unique = []
        for c in candidates:
            if c.reddit_id not in seen_ids:
                seen_ids.add(c.reddit_id)
                unique.append(c)
        return unique
    
    post_candidates = deduplicate(post_candidates)
    comment_candidates = deduplicate(comment_candidates)
    
    logger.info(
        "candidates_fetched",
        posts=len(post_candidates),
        comments=len(comment_candidates),
        total=len(post_candidates) + len(comment_candidates)
    )
    
    result = {
        "post_candidates": post_candidates,
        "comment_candidates": comment_candidates,
        "candidates": []  # Will be populated by select_by_ratio_node
    }
    if errors:
        result["errors"] = state.errors + errors
    
    return result


def select_by_ratio_node(
    state: Any,
    settings: Any
) -> Dict[str, Any]:
    """
    Select candidates based on configured post/comment ratio.
    
    Respects:
    - post_reply_ratio (e.g., 0.3 = 30% posts)
    - max_post_replies_per_run
    - max_comment_replies_per_run
    """
    max_per_run = getattr(settings, 'max_comments_per_run', 3)
    post_ratio = getattr(settings, 'post_reply_ratio', 0.3)
    max_post_replies = getattr(settings, 'max_post_replies_per_run', 1)
    max_comment_replies = getattr(settings, 'max_comment_replies_per_run', 2)
    
    post_candidates = state.post_candidates or []
    comment_candidates = state.comment_candidates or []
    
    # Calculate target counts (use round to avoid always rounding down)
    target_posts = min(
        round(max_per_run * post_ratio),
        max_post_replies,
        len(post_candidates)
    )
    target_comments = min(
        max_per_run - target_posts,
        max_comment_replies,
        len(comment_candidates)
    )
    
    # If not enough posts, fill with more comments
    if target_posts < int(max_per_run * post_ratio) and len(comment_candidates) > target_comments:
        extra_comments = min(
            max_per_run - target_posts - target_comments,
            len(comment_candidates) - target_comments
        )
        target_comments += extra_comments
    
    # Select candidates
    selected_posts = post_candidates[:target_posts]
    selected_comments = comment_candidates[:target_comments]
    
    # Merge into unified candidates list (posts first, then comments)
    candidates = selected_posts + selected_comments
    
    logger.info(
        "candidates_selected_by_ratio",
        posts=len(selected_posts),
        comments=len(selected_comments),
        total=len(candidates),
        ratio=post_ratio
    )
    
    return {"candidates": candidates}


def score_candidates_node(
    state: Any,
    quality_scorer: Any
) -> Dict[str, Any]:
    """
    Score all candidates for quality ranking.

    Attaches quality_score to each candidate using the QualityScorer service.

    Args:
        state: Current workflow state
        quality_scorer: QualityScorer instance (or None if disabled)

    Returns:
        Dict with updated candidates list
    """
    if not quality_scorer or not state.candidates:
        # Scoring disabled or no candidates, pass through
        return {}

    scored_candidates = []
    for candidate in state.candidates:
        try:
            scored = quality_scorer.score_candidate(candidate)
            scored_candidates.append(scored)
        except Exception as e:
            logger.error(
                "candidate_scoring_error",
                reddit_id=candidate.reddit_id,
                error=str(e)
            )
            # Keep candidate with default score on error
            scored_candidates.append(candidate)

    if scored_candidates:
        avg_score = sum(c.quality_score for c in scored_candidates) / len(scored_candidates)
        logger.info(
            "candidates_scored",
            count=len(scored_candidates),
            avg_score=round(avg_score, 3)
        )

    return {"candidates": scored_candidates}


def sort_by_score_node(
    state: Any,
    settings: Any
) -> Dict[str, Any]:
    """
    Sort candidates by priority and quality score with exploration logic.

    Phase A: Sort by (priority, quality_score) - HIGH priority first
    Implements exploration vs exploitation:
    - (100 - exploration_rate)% of the time: sort by priority + score descending
    - exploration_rate% of the time: randomize top N to avoid patterns

    Args:
        state: Current workflow state
        settings: Application settings

    Returns:
        Dict with sorted candidates list
    """
    import random

    if not state.candidates:
        return {}

    # Phase A: Sort by priority first (HIGH before NORMAL), then by quality score
    # Priority ordering: HIGH=0, NORMAL=1 (so HIGH comes first when sorted ascending)
    priority_order = {"HIGH": 0, "NORMAL": 1}
    sorted_candidates = sorted(
        state.candidates,
        key=lambda c: (priority_order.get(c.priority, 1), -c.quality_score)
        # Negative quality_score for descending order within same priority
    )

    # Apply exploration logic
    exploration_rate = getattr(settings, 'score_exploration_rate', 0.15)
    top_n = getattr(settings, 'score_top_n_random', 3)

    if random.random() < exploration_rate and len(sorted_candidates) >= top_n:
        # Exploration: randomize top N
        top_pool = sorted_candidates[:top_n]
        rest = sorted_candidates[top_n:]
        random.shuffle(top_pool)
        sorted_candidates = top_pool + rest

        logger.info(
            "exploration_applied",
            top_n=top_n,
            exploration_rate=exploration_rate
        )

    if sorted_candidates:
        logger.info(
            "candidates_sorted",
            count=len(sorted_candidates),
            top_priority=sorted_candidates[0].priority,
            top_score=round(sorted_candidates[0].quality_score, 3),
            bottom_score=round(sorted_candidates[-1].quality_score, 3)
        )

    return {"candidates": sorted_candidates}


def diversity_select_node(
    state: Any,
    settings: Any
) -> Dict[str, Any]:
    """
    Apply diversity filtering to prevent clustering in same subreddit/post.

    Phase B: Balanced distribution with flexibility
    - Max 2 per subreddit (allow 3rd if quality_score > 0.75)
    - Max 1 per post (strict - prevent spam)
    - Greedy selection maintaining diversity

    Args:
        state: Current workflow state
        settings: Application settings

    Returns:
        Dict with filtered candidates list
    """
    if not state.candidates:
        return {}

    max_per_subreddit = getattr(settings, 'max_per_subreddit', 2)
    max_per_post = getattr(settings, 'max_per_post', 1)
    quality_boost_threshold = getattr(settings, 'diversity_quality_boost_threshold', 0.75)

    selected = []
    subreddit_counts = {}
    selected_post_ids = set()

    for candidate in state.candidates:
        subreddit = candidate.subreddit
        post_id = getattr(candidate, 'post_id', '')  # Empty for posts
        quality_score = candidate.quality_score

        # Check post duplication (strict - max 1 per post)
        if post_id and post_id in selected_post_ids:
            logger.info(
                "candidate_skipped_duplicate_post",
                reddit_id=candidate.reddit_id,
                post_id=post_id,
                subreddit=subreddit
            )
            continue

        # Check subreddit diversity (flexible - allow quality boost)
        current_count = subreddit_counts.get(subreddit, 0)
        if current_count >= max_per_subreddit:
            # Allow 3rd+ if quality is exceptional
            if quality_score >= quality_boost_threshold:
                logger.info(
                    "diversity_quality_boost",
                    reddit_id=candidate.reddit_id,
                    subreddit=subreddit,
                    count=current_count,
                    quality_score=round(quality_score, 3)
                )
            else:
                logger.info(
                    "candidate_skipped_subreddit_limit",
                    reddit_id=candidate.reddit_id,
                    subreddit=subreddit,
                    count=current_count,
                    max=max_per_subreddit
                )
                continue

        # Accept candidate
        selected.append(candidate)
        subreddit_counts[subreddit] = current_count + 1
        if post_id:
            selected_post_ids.add(post_id)

    logger.info(
        "diversity_applied",
        original=len(state.candidates),
        selected=len(selected),
        subreddits=len(subreddit_counts),
        unique_posts=len(selected_post_ids)
    )

    return {"candidates": selected}


def filter_candidates_node(
    state: Any,
    state_manager: Any
) -> Dict[str, Any]:
    """
    Filter candidates based on:
    - Already replied
    - In cooldown (failed recently)
    - Daily limit
    """
    filtered = []
    skipped_replied = 0
    skipped_cooldown = 0

    for candidate in state.candidates:
        reddit_id = candidate.reddit_id

        # Skip if already replied successfully
        if state_manager.has_replied(reddit_id):
            logger.info(
                "candidate_filtered",
                filter_reason="already_replied",
                reddit_id=reddit_id,
                priority=candidate.priority,
                quality_score=round(candidate.quality_score, 3)
            )
            skipped_replied += 1
            continue

        # Skip if in cooldown
        if not state_manager.is_retryable(reddit_id):
            logger.info(
                "candidate_filtered",
                filter_reason="in_cooldown",
                reddit_id=reddit_id,
                priority=candidate.priority,
                quality_score=round(candidate.quality_score, 3)
            )
            skipped_cooldown += 1
            continue

        filtered.append(candidate)

    logger.info(
        "candidates_filtered_summary",
        original=len(state.candidates),
        remaining=len(filtered),
        skipped_replied=skipped_replied,
        skipped_cooldown=skipped_cooldown
    )

    return {"candidates": filtered}


def check_rules_node(
    state: Any,
    rule_engine: Any
) -> Dict[str, Any]:
    """
    Check subreddit rules compliance.
    
    Filters out candidates from restricted subreddits.
    """
    compliant = []
    
    for candidate in state.candidates:
        subreddit = candidate.subreddit
        
        if rule_engine.check_compliance(subreddit):
            compliant.append(candidate)
        else:
            logger.info(
                "candidate_filtered_rules",
                reddit_id=candidate.reddit_id,
                subreddit=subreddit
            )
    
    return {"candidates": compliant}


def check_daily_limit_node(
    state: Any,
    state_manager: Any
) -> Dict[str, Any]:
    """
    Check if daily posting limit has been reached.
    """
    can_post = state_manager.can_post_today()
    
    if not can_post:
        logger.warning("daily_limit_reached")
    
    return {"should_continue": can_post}


def select_candidate_node(
    state: Any
) -> Dict[str, Any]:
    """
    Select the next candidate to process.
    """
    if not state.candidates:
        return {
            "current_candidate": None,
            "should_continue": False
        }
    
    # Take first candidate
    candidate = state.candidates[0]
    remaining = state.candidates[1:]
    
    logger.info(
        "candidate_selected",
        reddit_id=candidate.reddit_id,
        subreddit=candidate.subreddit
    )
    
    return {
        "current_candidate": candidate,
        "candidates": remaining
    }


def build_context_node(
    state: Any,
    context_builder: Any,
    reddit_client: Any
) -> Dict[str, Any]:
    """
    Build conversation context for the LLM.
    
    Handles both post and comment candidates.
    """
    candidate = state.current_candidate
    
    if not candidate:
        return {"context": None}
    
    try:
        # Check candidate type
        candidate_type = getattr(candidate, 'candidate_type', 'comment')
        
        if candidate_type == "post":
            # Post reply context
            context_data = reddit_client.get_post_context(candidate.submission)
            context = context_builder.build_context(
                post=context_data["post"],
                is_post_reply=True
            )
        else:
            # Comment reply context
            comment = candidate.comment
            context_data = reddit_client.get_comment_context(comment)
            context = context_builder.build_context(
                post=context_data["post"],
                target_comment=comment,
                parent_chain=context_data["parent_chain"],
                is_post_reply=False
            )
        
        logger.info(
            "context_built",
            reddit_id=candidate.reddit_id,
            context_length=len(context),
            candidate_type=candidate_type
        )
        
        return {"context": context}
        
    except Exception as e:
        logger.error(
            "context_build_failed",
            reddit_id=candidate.reddit_id,
            error=str(e)
        )
        return {
            "context": None,
            "errors": state.errors + [f"Context build failed: {e}"]
        }


def generate_draft_node(
    state: Any,
    generator: Any,
    prompt_manager: Any
) -> Dict[str, Any]:
    """
    Generate a draft reply using the LLM.
    """
    candidate = state.current_candidate
    context = state.context
    
    if not candidate or not context:
        return {"draft": None}
    
    try:
        # Check if this is a post reply
        candidate_type = getattr(candidate, 'candidate_type', 'comment')
        is_post_reply = candidate_type == "post"
        
        # Get prompt components
        system_prompt = prompt_manager.get_system_message(
            candidate.subreddit,
            is_post_reply=is_post_reply
        )
        few_shot = prompt_manager.get_few_shot_examples(candidate.subreddit)
        
        # Generate draft
        draft = generator.generate(
            context=context,
            system_prompt=system_prompt,
            few_shot_examples=few_shot,
            subreddit=candidate.subreddit,
            reddit_id=candidate.reddit_id
        )
        
        logger.info(
            "draft_generated",
            draft_id=draft.draft_id,
            reddit_id=candidate.reddit_id,
            candidate_type=candidate_type
        )
        
        return {"draft": draft}
        
    except Exception as e:
        logger.error(
            "draft_generation_failed",
            reddit_id=candidate.reddit_id,
            error=str(e)
        )
        return {
            "draft": None,
            "errors": state.errors + [f"Generation failed: {e}"]
        }


def notify_human_node(
    state: Any,
    notifier: Any,
    state_manager: Any
) -> Dict[str, Any]:
    """
    Send draft for human approval.

    - Save draft to queue (returns approval token)
    - Send webhook notification with approval token
    - Record initial PENDING performance outcome (Phase 2)
    """
    draft = state.draft
    candidate = state.current_candidate

    if not draft or not candidate:
        return {}

    try:
        # Save to draft queue - returns approval_token
        # Phase 2: Pass candidate_type and quality_score
        approval_token = state_manager.save_draft(
            draft_id=draft.draft_id,
            reddit_id=draft.reddit_id,
            subreddit=draft.subreddit,
            content=draft.content,
            context_url=candidate.context_url,
            candidate_type=candidate.candidate_type,
            quality_score=candidate.quality_score
        )

        if not approval_token:
            logger.warning("draft_already_exists", draft_id=draft.draft_id)
            return {}

        # Phase 2: Record initial PENDING outcome
        try:
            state_manager.record_performance_outcome(
                draft_id=draft.draft_id,
                subreddit=candidate.subreddit,
                candidate_type=candidate.candidate_type,
                quality_score=candidate.quality_score,
                outcome="PENDING"
            )
        except Exception as e:
            # Don't fail workflow if performance tracking fails
            logger.warning("performance_tracking_failed", draft_id=draft.draft_id, error=str(e))

        # Send notification with approval token
        notifier.send_draft_notification(
            draft_id=draft.draft_id,
            subreddit=draft.subreddit,
            content=draft.content,
            thread_url=candidate.context_url,
            approval_token=approval_token
        )

        logger.info(
            "human_notified",
            draft_id=draft.draft_id
        )

        return {
            "processed_count": state.processed_count + 1
        }

    except Exception as e:
        logger.error(
            "notification_failed",
            draft_id=draft.draft_id,
            error=str(e)
        )
        return {
            "errors": state.errors + [f"Notification failed: {e}"]
        }


def should_continue(state: Any) -> str:
    """
    Determine next node based on state.
    
    Returns node name to route to.
    """
    if not state.should_continue:
        return "end"
    
    if not state.candidates and not state.current_candidate:
        return "end"
    
    return "select_candidate"
