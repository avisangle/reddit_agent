"""
Agent state definition for LangGraph workflow.
"""
from typing import List, Optional, Any, TypedDict
from dataclasses import dataclass, field


@dataclass
class AgentState:
    """
    State container for the agent workflow.
    
    Passed between nodes in the graph, accumulating data
    as the workflow progresses.
    """
    # Candidates to process
    candidates: List[Any] = field(default_factory=list)
    
    # Separate candidate pools for ratio-based selection
    post_candidates: List[Any] = field(default_factory=list)
    comment_candidates: List[Any] = field(default_factory=list)
    
    # Current candidate being processed
    current_candidate: Optional[Any] = None
    
    # Built context for LLM
    context: Optional[str] = None
    
    # Generated draft
    draft: Optional[Any] = None
    
    # Errors encountered
    errors: List[str] = field(default_factory=list)
    
    # Control flags
    should_continue: bool = True
    processed_count: int = 0
    
    # Reply type counters
    post_replies_count: int = 0
    comment_replies_count: int = 0
    
    def add_error(self, error: str) -> None:
        """Add an error to the list."""
        self.errors.append(error)
    
    def has_candidates(self) -> bool:
        """Check if there are candidates to process."""
        return len(self.candidates) > 0
    
    def next_candidate(self) -> Optional[Any]:
        """Get next candidate and set as current."""
        if self.candidates:
            self.current_candidate = self.candidates.pop(0)
            return self.current_candidate
        return None
    
    def reset_for_next(self) -> None:
        """Reset state for processing next candidate."""
        self.current_candidate = None
        self.context = None
        self.draft = None


class WorkflowState(TypedDict, total=False):
    """TypedDict version for LangGraph compatibility."""
    candidates: List[Any]
    post_candidates: List[Any]
    comment_candidates: List[Any]
    current_candidate: Optional[Any]
    context: Optional[str]
    draft: Optional[Any]
    errors: List[str]
    should_continue: bool
    processed_count: int
    post_replies_count: int
    comment_replies_count: int
