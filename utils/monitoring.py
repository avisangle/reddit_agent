"""
Monitoring and metrics for Reddit Agent.

Provides health checks, metrics, and alerting integration.
"""
import time
from datetime import datetime, date
from typing import Dict, Any, Optional
from dataclasses import dataclass, field, asdict
from functools import wraps

from utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class Metrics:
    """Agent metrics container."""
    # Counters
    drafts_generated: int = 0
    drafts_approved: int = 0
    drafts_rejected: int = 0
    drafts_published: int = 0
    
    # Error counts
    api_errors: int = 0
    generation_errors: int = 0
    webhook_errors: int = 0
    
    # Timing
    avg_generation_time_ms: float = 0.0
    avg_context_build_time_ms: float = 0.0
    
    # Safety
    shadowban_risk: float = 0.0
    rate_limit_remaining: int = 100
    daily_count: int = 0
    daily_limit: int = 8
    
    # Timestamps
    last_run: Optional[str] = None
    last_success: Optional[str] = None
    last_error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class MetricsCollector:
    """
    Collect and expose agent metrics.
    
    Features:
    - Counter increments
    - Timing measurements  
    - Health status
    - Prometheus-compatible export (optional)
    """
    
    def __init__(self):
        self._metrics = Metrics()
        self._timing_samples: Dict[str, list] = {
            "generation": [],
            "context_build": []
        }
        self._max_samples = 100
    
    @property
    def metrics(self) -> Metrics:
        return self._metrics
    
    def increment(self, counter: str, value: int = 1) -> None:
        """Increment a counter."""
        if hasattr(self._metrics, counter):
            current = getattr(self._metrics, counter)
            setattr(self._metrics, counter, current + value)
    
    def record_timing(self, operation: str, duration_ms: float) -> None:
        """Record timing sample."""
        if operation in self._timing_samples:
            samples = self._timing_samples[operation]
            samples.append(duration_ms)
            
            # Keep only recent samples
            if len(samples) > self._max_samples:
                samples.pop(0)
            
            # Update average
            avg = sum(samples) / len(samples)
            if operation == "generation":
                self._metrics.avg_generation_time_ms = avg
            elif operation == "context_build":
                self._metrics.avg_context_build_time_ms = avg
    
    def update_safety(
        self,
        shadowban_risk: float,
        rate_limit_remaining: int,
        daily_count: int,
        daily_limit: int
    ) -> None:
        """Update safety metrics."""
        self._metrics.shadowban_risk = shadowban_risk
        self._metrics.rate_limit_remaining = rate_limit_remaining
        self._metrics.daily_count = daily_count
        self._metrics.daily_limit = daily_limit
    
    def mark_run(self) -> None:
        """Mark a workflow run."""
        self._metrics.last_run = datetime.utcnow().isoformat()
    
    def mark_success(self) -> None:
        """Mark a successful operation."""
        self._metrics.last_success = datetime.utcnow().isoformat()
    
    def mark_error(self) -> None:
        """Mark an error."""
        self._metrics.last_error = datetime.utcnow().isoformat()
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get overall health status."""
        m = self._metrics
        
        # Determine health
        is_healthy = True
        warnings = []
        
        if m.shadowban_risk > 0.5:
            is_healthy = False
            warnings.append(f"High shadowban risk: {m.shadowban_risk:.2f}")
        
        if m.rate_limit_remaining < 10:
            warnings.append(f"Low rate limit: {m.rate_limit_remaining}")
        
        if m.daily_count >= m.daily_limit:
            warnings.append("Daily limit reached")
        
        if m.api_errors > 10:
            warnings.append(f"High API error count: {m.api_errors}")
        
        return {
            "status": "healthy" if is_healthy else "degraded",
            "warnings": warnings,
            "metrics": m.to_dict(),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def export_prometheus(self) -> str:
        """Export metrics in Prometheus format."""
        m = self._metrics
        lines = [
            f"# HELP reddit_agent_drafts_generated Total drafts generated",
            f"# TYPE reddit_agent_drafts_generated counter",
            f"reddit_agent_drafts_generated {m.drafts_generated}",
            "",
            f"# HELP reddit_agent_drafts_approved Total drafts approved",
            f"# TYPE reddit_agent_drafts_approved counter", 
            f"reddit_agent_drafts_approved {m.drafts_approved}",
            "",
            f"# HELP reddit_agent_drafts_published Total drafts published",
            f"# TYPE reddit_agent_drafts_published counter",
            f"reddit_agent_drafts_published {m.drafts_published}",
            "",
            f"# HELP reddit_agent_api_errors API error count",
            f"# TYPE reddit_agent_api_errors counter",
            f"reddit_agent_api_errors {m.api_errors}",
            "",
            f"# HELP reddit_agent_shadowban_risk Current shadowban risk",
            f"# TYPE reddit_agent_shadowban_risk gauge",
            f"reddit_agent_shadowban_risk {m.shadowban_risk}",
            "",
            f"# HELP reddit_agent_rate_limit_remaining Rate limit remaining",
            f"# TYPE reddit_agent_rate_limit_remaining gauge",
            f"reddit_agent_rate_limit_remaining {m.rate_limit_remaining}",
            "",
            f"# HELP reddit_agent_daily_count Daily comment count",
            f"# TYPE reddit_agent_daily_count gauge",
            f"reddit_agent_daily_count {m.daily_count}",
            "",
            f"# HELP reddit_agent_generation_time_ms Average generation time",
            f"# TYPE reddit_agent_generation_time_ms gauge",
            f"reddit_agent_generation_time_ms {m.avg_generation_time_ms}",
            ""
        ]
        return "\n".join(lines)


def timed(operation: str):
    """Decorator to time function execution."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, collector: MetricsCollector = None, **kwargs):
            start = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration_ms = (time.time() - start) * 1000
                if collector:
                    collector.record_timing(operation, duration_ms)
        return wrapper
    return decorator


# Global metrics collector
_collector: Optional[MetricsCollector] = None


def get_metrics_collector() -> MetricsCollector:
    """Get global metrics collector."""
    global _collector
    if _collector is None:
        _collector = MetricsCollector()
    return _collector
