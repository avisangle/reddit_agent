"""
Workflow runner with anti-fingerprint timing.

Implements the main execution loop with jitter for safety.
"""
import time
import random
from typing import Any, Optional
from dataclasses import dataclass

from .state import AgentState
from .graph import create_workflow_graph
from utils.logging import get_logger

logger = get_logger(__name__)


def calculate_jitter(min_seconds: int, max_seconds: int) -> float:
    """
    Calculate random jitter within range.
    
    Args:
        min_seconds: Minimum wait time
        max_seconds: Maximum wait time
        
    Returns:
        Random float between min and max
    """
    return random.uniform(min_seconds, max_seconds)


@dataclass
class RunResult:
    """Result of a workflow run."""
    processed_count: int
    error_count: int
    errors: list
    duration_seconds: float


class WorkflowRunner:
    """
    Execute the agent workflow with safety features.
    
    Features:
    - Anti-fingerprint jitter between operations
    - Dry-run mode for testing
    - Graceful error handling
    - Run limits
    """
    
    def __init__(
        self,
        reddit_client: Any,
        context_builder: Any,
        rule_engine: Any,
        prompt_manager: Any,
        generator: Any,
        state_manager: Any,
        notifier: Any,
        quality_scorer: Any = None,
        settings: Any = None,
        min_jitter: int = 30,
        max_jitter: int = 90,
        max_per_run: int = 3,
        dry_run: bool = False
    ):
        """
        Initialize workflow runner.

        Args:
            reddit_client: Reddit API client
            context_builder: Context builder
            rule_engine: Rule engine
            prompt_manager: Prompt manager
            generator: Draft generator
            state_manager: State manager
            notifier: Webhook notifier
            quality_scorer: Quality scorer (optional, Phase 1)
            settings: Configuration settings
            min_jitter: Minimum seconds between operations
            max_jitter: Maximum seconds between operations
            max_per_run: Maximum drafts per run
            dry_run: If True, don't actually post or notify
        """
        self._reddit_client = reddit_client
        self._context_builder = context_builder
        self._rule_engine = rule_engine
        self._prompt_manager = prompt_manager
        self._generator = generator
        self._state_manager = state_manager
        self._notifier = notifier
        self._settings = settings
        self._min_jitter = min_jitter
        self._max_jitter = max_jitter
        self._max_per_run = max_per_run
        self._dry_run = dry_run
        
        # Create workflow graph
        self._graph = create_workflow_graph(
            reddit_client=reddit_client,
            context_builder=context_builder,
            rule_engine=rule_engine,
            prompt_manager=prompt_manager,
            generator=generator,
            state_manager=state_manager,
            notifier=notifier,
            quality_scorer=quality_scorer,
            settings=settings
        )
        
        logger.info(
            "workflow_runner_initialized",
            min_jitter=min_jitter,
            max_jitter=max_jitter,
            max_per_run=max_per_run,
            dry_run=dry_run
        )
    
    def run(self) -> RunResult:
        """
        Execute the workflow.
        
        Returns:
            RunResult with statistics
        """
        start_time = time.time()
        
        logger.info("workflow_run_started", dry_run=self._dry_run)
        
        # Initialize state
        state = AgentState(
            candidates=[],
            current_candidate=None,
            context=None,
            draft=None,
            errors=[],
            should_continue=True,
            processed_count=0
        )
        
        try:
            # Compile and run graph
            compiled = self._graph.compile()
            
            # Execute with streaming
            final_state = None
            for step in compiled.stream(state):
                # LangGraph stream returns dict with node name as key
                # Extract the actual state from the step
                if isinstance(step, dict):
                    # Get the state from the first (and only) node output
                    for node_name, node_state in step.items():
                        final_state = node_state
                else:
                    final_state = step
                
                # Apply jitter between steps
                if not self._dry_run:
                    jitter = calculate_jitter(self._min_jitter // 10, self._max_jitter // 10)
                    time.sleep(jitter)
                
                # Check run limit - handle both dict and object states
                processed_count = (
                    final_state.get('processed_count', 0) if isinstance(final_state, dict)
                    else getattr(final_state, 'processed_count', 0)
                )
                if processed_count >= self._max_per_run:
                    logger.info(
                        "run_limit_reached",
                        count=processed_count
                    )
                    break
            
            # Compile results - handle both dict and object states
            if final_state is None:
                processed = 0
                errors = []
            elif isinstance(final_state, dict):
                processed = final_state.get('processed_count', 0)
                errors = final_state.get('errors', [])
            else:
                processed = getattr(final_state, 'processed_count', 0)
                errors = getattr(final_state, 'errors', [])
            
            duration = time.time() - start_time
            
            result = RunResult(
                processed_count=processed,
                error_count=len(errors),
                errors=errors,
                duration_seconds=duration
            )
            
            logger.info(
                "workflow_run_completed",
                processed=result.processed_count,
                errors=result.error_count,
                duration=result.duration_seconds
            )
            
            return result
            
        except Exception as e:
            logger.error("workflow_run_failed", error=str(e))
            
            duration = time.time() - start_time
            return RunResult(
                processed_count=0,
                error_count=1,
                errors=[str(e)],
                duration_seconds=duration
            )
    
    def run_single(self, reddit_id: str) -> Optional[Any]:
        """
        Process a single item by reddit_id.
        
        Useful for reprocessing or testing.
        
        Args:
            reddit_id: Reddit item ID to process
            
        Returns:
            Draft if generated, None otherwise
        """
        logger.info("single_run_started", reddit_id=reddit_id)
        
        # This would need implementation to fetch specific comment
        # For now, return None as placeholder
        return None
    
    @property
    def dry_run(self) -> bool:
        return self._dry_run
    
    @dry_run.setter
    def dry_run(self, value: bool) -> None:
        self._dry_run = value
        logger.info("dry_run_mode_changed", dry_run=value)
