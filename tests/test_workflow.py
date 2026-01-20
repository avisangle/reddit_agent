"""
Test LangGraph workflow and agent nodes (Story 9).
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime


class TestWorkflowGraph:
    """Test workflow graph structure."""
    
    def test_graph_has_required_nodes(self):
        """Verify graph has all required nodes."""
        from workflow.graph import create_workflow_graph
        
        graph = create_workflow_graph(
            reddit_client=Mock(),
            context_builder=Mock(),
            rule_engine=Mock(),
            prompt_manager=Mock(),
            generator=Mock(),
            state_manager=Mock(),
            notifier=Mock()
        )
        
        # Check nodes exist
        assert "fetch_candidates" in graph.nodes
        assert "filter_candidates" in graph.nodes
        assert "check_rules" in graph.nodes
        assert "build_context" in graph.nodes
        assert "generate_draft" in graph.nodes
        assert "notify_human" in graph.nodes
    
    def test_graph_has_entry_point(self):
        """Verify graph has entry point."""
        from workflow.graph import create_workflow_graph
        
        graph = create_workflow_graph(
            reddit_client=Mock(),
            context_builder=Mock(),
            rule_engine=Mock(),
            prompt_manager=Mock(),
            generator=Mock(),
            state_manager=Mock(),
            notifier=Mock()
        )
        
        # Entry point should be fetch_candidates
        assert graph.entry_point == "fetch_candidates"


class TestFetchNode:
    """Test fetch candidates node."""
    
    def test_fetch_returns_candidates(self):
        """Fetch node should return post and comment candidate pools."""
        from workflow.nodes import fetch_candidates_node
        from workflow.state import AgentState
        from services.reddit_client import CandidateComment

        mock_client = Mock()
        mock_client.fetch_inbox_replies.return_value = [
            CandidateComment(
                comment=Mock(),
                reddit_id="abc123",
                subreddit="sysadmin",
                body="Test comment",
                author="testuser",
                context_url="https://reddit.com/test",
                post_title="Test post",
                parent_id="t3_parent"
            )
        ]
        mock_client.fetch_rising_posts_as_candidates.return_value = []
        mock_client.fetch_rising_candidates.return_value = []

        state = AgentState(
            candidates=[],
            current_candidate=None,
            context=None,
            draft=None,
            errors=[]
        )

        result = fetch_candidates_node(state, reddit_client=mock_client)

        # Fetch populates comment_candidates from inbox with HIGH priority
        assert len(result["comment_candidates"]) == 1
        assert result["comment_candidates"][0].reddit_id == "abc123"
        assert result["comment_candidates"][0].priority == "HIGH"


class TestFilterNode:
    """Test filter candidates node."""
    
    def test_filters_already_replied(self):
        """Filter out items we've already replied to."""
        from workflow.nodes import filter_candidates_node
        from workflow.state import AgentState
        from services.reddit_client import CandidateComment

        mock_state_manager = Mock()
        mock_state_manager.has_replied.side_effect = lambda x: x == "replied123"
        mock_state_manager.is_retryable.return_value = True

        candidates = [
            CandidateComment(
                comment=Mock(),
                reddit_id="replied123",
                subreddit="test",
                body="Test",
                author="user1",
                context_url="url1",
                post_title="Post",
                parent_id="parent1",
                priority="NORMAL",
                quality_score=0.5
            ),
            CandidateComment(
                comment=Mock(),
                reddit_id="new456",
                subreddit="test",
                body="Test",
                author="user2",
                context_url="url2",
                post_title="Post",
                parent_id="parent2",
                priority="NORMAL",
                quality_score=0.6
            )
        ]

        state = AgentState(
            candidates=candidates,
            current_candidate=None,
            context=None,
            draft=None,
            errors=[]
        )

        result = filter_candidates_node(state, state_manager=mock_state_manager)

        # Should filter out replied item
        assert len(result["candidates"]) == 1
        assert result["candidates"][0].reddit_id == "new456"
    
    def test_filters_non_retryable(self):
        """Filter out items in cooldown."""
        from workflow.nodes import filter_candidates_node
        from workflow.state import AgentState
        from services.reddit_client import CandidateComment

        mock_state_manager = Mock()
        mock_state_manager.has_replied.return_value = False
        mock_state_manager.is_retryable.side_effect = lambda x: x != "cooldown123"

        candidates = [
            CandidateComment(
                comment=Mock(),
                reddit_id="cooldown123",
                subreddit="test",
                body="Test",
                author="user1",
                context_url="url1",
                post_title="Post",
                parent_id="parent1",
                priority="NORMAL",
                quality_score=0.4
            ),
            CandidateComment(
                comment=Mock(),
                reddit_id="ready456",
                subreddit="test",
                body="Test",
                author="user2",
                context_url="url2",
                post_title="Post",
                parent_id="parent2",
                priority="NORMAL",
                quality_score=0.7
            )
        ]

        state = AgentState(
            candidates=candidates,
            current_candidate=None,
            context=None,
            draft=None,
            errors=[]
        )
        
        result = filter_candidates_node(state, state_manager=mock_state_manager)
        
        assert len(result["candidates"]) == 1
        assert result["candidates"][0].reddit_id == "ready456"


class TestRuleCheckNode:
    """Test rule check node."""
    
    def test_skips_restricted_subreddit(self):
        """Skip candidates from restricted subreddits."""
        from workflow.nodes import check_rules_node
        from workflow.state import AgentState
        
        mock_rule_engine = Mock()
        mock_rule_engine.check_compliance.side_effect = lambda x: x != "restrictedSub"
        
        candidates = [
            Mock(reddit_id="c1", subreddit="restrictedSub"),
            Mock(reddit_id="c2", subreddit="allowedSub")
        ]
        
        state = AgentState(
            candidates=candidates,
            current_candidate=None,
            context=None,
            draft=None,
            errors=[]
        )
        
        result = check_rules_node(state, rule_engine=mock_rule_engine)
        
        assert len(result["candidates"]) == 1
        assert result["candidates"][0].subreddit == "allowedSub"


class TestContextNode:
    """Test context building node."""
    
    def test_builds_context_for_candidate(self):
        """Context node should build context string."""
        from workflow.nodes import build_context_node
        from workflow.state import AgentState
        
        mock_builder = Mock()
        mock_builder.build_context.return_value = "[Post Title]\nTest\n\n[Target]\nHelp!"
        
        mock_reddit = Mock()
        mock_reddit.get_comment_context.return_value = {
            "post": Mock(),
            "parent_chain": [],
            "target": Mock()
        }
        
        candidate = Mock(
            reddit_id="test123",
            comment=Mock()
        )
        
        state = AgentState(
            candidates=[candidate],
            current_candidate=candidate,
            context=None,
            draft=None,
            errors=[]
        )
        
        result = build_context_node(state, context_builder=mock_builder, reddit_client=mock_reddit)
        
        assert result["context"] is not None
        assert "[Post Title]" in result["context"]


class TestGenerateNode:
    """Test draft generation node."""
    
    def test_generates_draft(self):
        """Generate node should create draft."""
        from workflow.nodes import generate_draft_node
        from workflow.state import AgentState
        from agents.generator import Draft
        
        mock_generator = Mock()
        mock_generator.generate.return_value = Draft(
            draft_id="draft123",
            reddit_id="test123",
            subreddit="sysadmin",
            content="Helpful reply"
        )
        
        mock_prompt_manager = Mock()
        mock_prompt_manager.get_system_message.return_value = "Be helpful"
        mock_prompt_manager.get_few_shot_examples.return_value = ["Example"]
        
        candidate = Mock(reddit_id="test123", subreddit="sysadmin")
        
        state = AgentState(
            candidates=[candidate],
            current_candidate=candidate,
            context="[Context here]",
            draft=None,
            errors=[]
        )
        
        result = generate_draft_node(
            state,
            generator=mock_generator,
            prompt_manager=mock_prompt_manager
        )
        
        assert result["draft"] is not None
        assert result["draft"].content == "Helpful reply"


class TestNotifyNode:
    """Test notification node."""
    
    def test_sends_notification(self):
        """Notify node should send webhook."""
        from workflow.nodes import notify_human_node
        from workflow.state import AgentState
        from agents.generator import Draft
        
        mock_notifier = Mock()
        mock_notifier.send_draft_notification.return_value = True
        
        mock_state_manager = Mock()
        mock_state_manager.save_draft.return_value = True
        
        draft = Draft(
            draft_id="draft123",
            reddit_id="test123",
            subreddit="sysadmin",
            content="Test reply"
        )
        
        candidate = Mock(
            reddit_id="test123",
            subreddit="sysadmin",
            context_url="https://reddit.com/test"
        )
        
        state = AgentState(
            candidates=[candidate],
            current_candidate=candidate,
            context="Context",
            draft=draft,
            errors=[]
        )
        
        result = notify_human_node(
            state,
            notifier=mock_notifier,
            state_manager=mock_state_manager
        )
        
        # Should have called notifier
        mock_notifier.send_draft_notification.assert_called_once()
        
        # Should have saved draft
        mock_state_manager.save_draft.assert_called_once()


class TestJitterTiming:
    """Test anti-fingerprint jitter."""
    
    def test_jitter_within_range(self):
        """Jitter should be within configured range."""
        from workflow.runner import calculate_jitter
        
        min_jitter = 30
        max_jitter = 90
        
        for _ in range(100):
            jitter = calculate_jitter(min_jitter, max_jitter)
            assert min_jitter <= jitter <= max_jitter
    
    def test_jitter_is_varied(self):
        """Jitter should produce varied results."""
        from workflow.runner import calculate_jitter
        
        results = [calculate_jitter(30, 90) for _ in range(20)]
        unique = set(results)
        
        # Should have multiple unique values
        assert len(unique) > 1


class TestDailyLimitEnforcement:
    """Test daily limit check in workflow."""
    
    def test_stops_at_daily_limit(self):
        """Workflow should stop when daily limit reached."""
        from workflow.nodes import check_daily_limit_node
        from workflow.state import AgentState
        
        mock_state_manager = Mock()
        mock_state_manager.can_post_today.return_value = False
        
        state = AgentState(
            candidates=[],
            current_candidate=None,
            context=None,
            draft=None,
            errors=[]
        )
        
        result = check_daily_limit_node(state, state_manager=mock_state_manager)
        
        assert result["should_continue"] is False
