"""
LangGraph workflow graph definition.

Defines the agent workflow as a directed graph with nodes and edges.
"""
from typing import Any, Dict
from functools import partial

from langgraph.graph import StateGraph, END

from .state import AgentState
from .nodes import (
    fetch_candidates_node,
    select_by_ratio_node,
    score_candidates_node,
    filter_candidates_node,
    check_rules_node,
    sort_by_score_node,
    diversity_select_node,
    check_daily_limit_node,
    select_candidate_node,
    build_context_node,
    generate_draft_node,
    notify_human_node,
    should_continue
)
from utils.logging import get_logger

logger = get_logger(__name__)


class WorkflowGraph:
    """
    Wrapper around LangGraph StateGraph with node tracking.
    """
    
    def __init__(self, graph: StateGraph):
        self._graph = graph
        self._nodes = set()
        self._entry_point = None
    
    @property
    def nodes(self) -> set:
        return self._nodes
    
    @property
    def entry_point(self) -> str:
        return self._entry_point
    
    def add_node(self, name: str, func: Any) -> None:
        self._nodes.add(name)
        self._graph.add_node(name, func)
    
    def set_entry_point(self, name: str) -> None:
        self._entry_point = name
        self._graph.set_entry_point(name)
    
    def add_edge(self, from_node: str, to_node: str) -> None:
        self._graph.add_edge(from_node, to_node)
    
    def add_conditional_edges(self, from_node: str, condition: Any, mapping: Dict) -> None:
        self._graph.add_conditional_edges(from_node, condition, mapping)
    
    def compile(self) -> Any:
        return self._graph.compile()


def create_workflow_graph(
    reddit_client: Any,
    context_builder: Any,
    rule_engine: Any,
    prompt_manager: Any,
    generator: Any,
    state_manager: Any,
    notifier: Any,
    quality_scorer: Any = None,
    settings: Any = None
) -> WorkflowGraph:
    """
    Create the agent workflow graph.

    Flow:
    1. fetch_candidates - Get posts and comments from inbox/rising
    2. select_by_ratio - Select candidates based on post/comment ratio
    3. score_candidates - Score candidates for quality ranking
    4. filter_candidates - Remove already-replied, cooldown
    5. check_rules - Filter restricted subreddits
    6. sort_by_score - Sort by priority + quality score with exploration
    7. diversity_select - Apply subreddit/post diversity filtering (Phase B)
    8. check_daily_limit - Stop if at limit
    9. select_candidate - Pick next to process
    10. build_context - Build conversation context
    11. generate_draft - Generate reply with LLM
    12. notify_human - Save draft and send webhook
    13. Loop back to check_daily_limit or end

    Args:
        reddit_client: Reddit API client
        context_builder: Context builder service
        rule_engine: Subreddit rule engine
        prompt_manager: Prompt template manager
        generator: LLM draft generator
        state_manager: State manager for persistence
        notifier: Webhook notifier
        quality_scorer: Quality scoring service (optional, Phase 1)
        settings: Configuration settings

    Returns:
        Configured WorkflowGraph
    """
    # Create state graph
    graph = StateGraph(AgentState)
    wrapper = WorkflowGraph(graph)
    
    # Bind dependencies to nodes
    fetch_node = partial(fetch_candidates_node, reddit_client=reddit_client, settings=settings)
    ratio_node = partial(select_by_ratio_node, settings=settings)
    score_node = partial(score_candidates_node, quality_scorer=quality_scorer)
    filter_node = partial(filter_candidates_node, state_manager=state_manager)
    rules_node = partial(check_rules_node, rule_engine=rule_engine)
    sort_node = partial(sort_by_score_node, settings=settings)
    diversity_node = partial(diversity_select_node, settings=settings)
    limit_node = partial(check_daily_limit_node, state_manager=state_manager)
    context_node = partial(
        build_context_node,
        context_builder=context_builder,
        reddit_client=reddit_client
    )
    generate_node = partial(
        generate_draft_node,
        generator=generator,
        prompt_manager=prompt_manager
    )
    notify_node = partial(
        notify_human_node,
        notifier=notifier,
        state_manager=state_manager
    )
    
    # Add nodes
    wrapper.add_node("fetch_candidates", fetch_node)
    wrapper.add_node("select_by_ratio", ratio_node)
    wrapper.add_node("score_candidates", score_node)
    wrapper.add_node("filter_candidates", filter_node)
    wrapper.add_node("check_rules", rules_node)
    wrapper.add_node("sort_by_score", sort_node)
    wrapper.add_node("diversity_select", diversity_node)
    wrapper.add_node("check_daily_limit", limit_node)
    wrapper.add_node("select_candidate", select_candidate_node)
    wrapper.add_node("build_context", context_node)
    wrapper.add_node("generate_draft", generate_node)
    wrapper.add_node("notify_human", notify_node)
    
    # Set entry point
    wrapper.set_entry_point("fetch_candidates")
    
    # Add edges (linear flow with loop)
    wrapper.add_edge("fetch_candidates", "select_by_ratio")
    wrapper.add_edge("select_by_ratio", "score_candidates")
    wrapper.add_edge("score_candidates", "filter_candidates")
    wrapper.add_edge("filter_candidates", "check_rules")
    wrapper.add_edge("check_rules", "sort_by_score")
    wrapper.add_edge("sort_by_score", "diversity_select")
    wrapper.add_edge("diversity_select", "check_daily_limit")
    
    # Conditional: check daily limit
    wrapper.add_conditional_edges(
        "check_daily_limit",
        lambda state: "continue" if state.should_continue else "end",
        {
            "continue": "select_candidate",
            "end": END
        }
    )
    
    # Conditional: select candidate
    wrapper.add_conditional_edges(
        "select_candidate",
        lambda state: "process" if state.current_candidate else "end",
        {
            "process": "build_context",
            "end": END
        }
    )
    
    wrapper.add_edge("build_context", "generate_draft")
    wrapper.add_edge("generate_draft", "notify_human")
    
    # Loop back or end
    wrapper.add_conditional_edges(
        "notify_human",
        should_continue,
        {
            "select_candidate": "check_daily_limit",
            "end": END
        }
    )
    
    logger.info(
        "workflow_graph_created",
        nodes=list(wrapper.nodes)
    )
    
    return wrapper
