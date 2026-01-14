"""
Test monitoring and metrics (Story 10).
"""
import pytest
from unittest.mock import Mock


class TestMetrics:
    """Test metrics collection."""
    
    def test_increment_counter(self):
        """Counter increments should work."""
        from utils.monitoring import MetricsCollector
        
        collector = MetricsCollector()
        
        assert collector.metrics.drafts_generated == 0
        collector.increment("drafts_generated")
        assert collector.metrics.drafts_generated == 1
        collector.increment("drafts_generated", 5)
        assert collector.metrics.drafts_generated == 6
    
    def test_record_timing(self):
        """Timing records should update averages."""
        from utils.monitoring import MetricsCollector
        
        collector = MetricsCollector()
        
        collector.record_timing("generation", 100)
        collector.record_timing("generation", 200)
        
        # Average should be 150
        assert collector.metrics.avg_generation_time_ms == 150.0
    
    def test_update_safety(self):
        """Safety metrics should update."""
        from utils.monitoring import MetricsCollector
        
        collector = MetricsCollector()
        
        collector.update_safety(
            shadowban_risk=0.3,
            rate_limit_remaining=50,
            daily_count=5,
            daily_limit=8
        )
        
        assert collector.metrics.shadowban_risk == 0.3
        assert collector.metrics.rate_limit_remaining == 50
        assert collector.metrics.daily_count == 5


class TestHealthStatus:
    """Test health status reporting."""
    
    def test_healthy_status(self):
        """Normal metrics should report healthy."""
        from utils.monitoring import MetricsCollector
        
        collector = MetricsCollector()
        status = collector.get_health_status()
        
        assert status["status"] == "healthy"
        assert len(status["warnings"]) == 0
    
    def test_degraded_on_high_risk(self):
        """High shadowban risk should report degraded."""
        from utils.monitoring import MetricsCollector
        
        collector = MetricsCollector()
        collector.update_safety(
            shadowban_risk=0.7,
            rate_limit_remaining=100,
            daily_count=0,
            daily_limit=8
        )
        
        status = collector.get_health_status()
        
        assert status["status"] == "degraded"
        assert any("shadowban" in w.lower() for w in status["warnings"])
    
    def test_warning_on_daily_limit(self):
        """Reaching daily limit should add warning."""
        from utils.monitoring import MetricsCollector
        
        collector = MetricsCollector()
        collector.update_safety(
            shadowban_risk=0.1,
            rate_limit_remaining=100,
            daily_count=8,
            daily_limit=8
        )
        
        status = collector.get_health_status()
        
        assert any("daily limit" in w.lower() for w in status["warnings"])


class TestPrometheusExport:
    """Test Prometheus metrics export."""
    
    def test_export_format(self):
        """Export should be valid Prometheus format."""
        from utils.monitoring import MetricsCollector
        
        collector = MetricsCollector()
        collector.increment("drafts_generated", 10)
        collector.increment("api_errors", 2)
        
        output = collector.export_prometheus()
        
        # Should contain metric names
        assert "reddit_agent_drafts_generated 10" in output
        assert "reddit_agent_api_errors 2" in output
        
        # Should have TYPE declarations
        assert "# TYPE reddit_agent_drafts_generated counter" in output
    
    def test_export_includes_gauges(self):
        """Export should include gauge metrics."""
        from utils.monitoring import MetricsCollector
        
        collector = MetricsCollector()
        collector.update_safety(
            shadowban_risk=0.25,
            rate_limit_remaining=75,
            daily_count=3,
            daily_limit=8
        )
        
        output = collector.export_prometheus()
        
        assert "reddit_agent_shadowban_risk 0.25" in output
        assert "reddit_agent_rate_limit_remaining 75" in output
