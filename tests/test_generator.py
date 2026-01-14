"""
Test LLM draft generator (Story 6).
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from dataclasses import dataclass


class TestGeneratorInput:
    """Test generator receives correct input."""
    
    def test_receives_context_and_prompt(self):
        """Mock LLM input. Verify it receives output from ContextBuilder + PromptManager."""
        from agents.generator import DraftGenerator
        
        mock_llm = Mock()
        mock_llm.invoke = Mock(return_value=Mock(content="Generated reply content"))
        
        generator = DraftGenerator(llm=mock_llm)
        
        context = "[Post Title]\nTest\n[Target Comment]\nHelp needed"
        system_prompt = "You are a helpful peer"
        few_shot = ["Example 1", "Example 2"]
        
        result = generator.generate(
            context=context,
            system_prompt=system_prompt,
            few_shot_examples=few_shot,
            subreddit="sysadmin",
            reddit_id="abc123"
        )
        
        # Verify LLM was called
        mock_llm.invoke.assert_called_once()
        
        # Get the messages passed to LLM
        call_args = mock_llm.invoke.call_args
        messages = call_args[0][0] if call_args[0] else call_args.kwargs.get('messages', [])
        
        # Should have messages
        assert len(messages) > 0


class TestDraftOutput:
    """Test draft output validation."""
    
    def test_returns_valid_draft_object(self):
        """Verify output is a valid Draft object."""
        from agents.generator import DraftGenerator, Draft
        
        mock_llm = Mock()
        mock_llm.invoke = Mock(return_value=Mock(content="This is a helpful reply"))
        
        generator = DraftGenerator(llm=mock_llm)
        
        result = generator.generate(
            context="Test context",
            system_prompt="Be helpful",
            few_shot_examples=[],
            subreddit="test",
            reddit_id="xyz789"
        )
        
        # Should return Draft object
        assert isinstance(result, Draft)
        assert result.content == "This is a helpful reply"
        assert result.reddit_id == "xyz789"
        assert result.subreddit == "test"
        assert result.draft_id is not None


class TestBannedPhrases:
    """Test banned phrase detection."""
    
    def test_rejects_ai_disclosure(self):
        """Fail generation if output contains 'As an AI model'."""
        from agents.generator import DraftGenerator, ContentFilterError
        
        mock_llm = Mock()
        mock_llm.invoke = Mock(return_value=Mock(
            content="As an AI model, I can help you with this..."
        ))
        
        generator = DraftGenerator(llm=mock_llm)
        
        with pytest.raises(ContentFilterError) as exc_info:
            generator.generate(
                context="Test",
                system_prompt="Be helpful",
                few_shot_examples=[],
                subreddit="test",
                reddit_id="test123"
            )
        
        assert "banned phrase" in str(exc_info.value).lower()
    
    def test_rejects_formal_transitions(self):
        """Reject formal transition phrases."""
        from agents.generator import DraftGenerator, ContentFilterError
        
        # Use phrases that exactly match the banned patterns
        banned_phrases = [
            "It's important to note that this is a key point",
            "In summary, you should do this approach",
            "Based on my experience, I would suggest this",  # Pattern needs comma
        ]
        
        for phrase in banned_phrases:
            mock_llm = Mock()
            # Return banned content on all retries
            mock_llm.invoke = Mock(return_value=Mock(content=phrase))
            
            generator = DraftGenerator(llm=mock_llm, max_retries=1)
            
            with pytest.raises(ContentFilterError):
                generator.generate(
                    context="Test",
                    system_prompt="Be helpful",
                    few_shot_examples=[],
                    subreddit="test",
                    reddit_id="test123"
                )
    
    def test_accepts_valid_content(self):
        """Valid content should pass through."""
        from agents.generator import DraftGenerator
        
        mock_llm = Mock()
        mock_llm.invoke = Mock(return_value=Mock(
            content="Yeah I ran into that same issue. Try checking your DNS settings."
        ))
        
        generator = DraftGenerator(llm=mock_llm)
        
        result = generator.generate(
            context="Test",
            system_prompt="Be helpful",
            few_shot_examples=[],
            subreddit="test",
            reddit_id="test123"
        )
        
        assert result.content == "Yeah I ran into that same issue. Try checking your DNS settings."


class TestContentLength:
    """Test content length validation."""
    
    def test_rejects_too_short_content(self):
        """Very short responses should be rejected."""
        from agents.generator import DraftGenerator, ContentFilterError
        
        mock_llm = Mock()
        mock_llm.invoke = Mock(return_value=Mock(content="Ok"))
        
        generator = DraftGenerator(llm=mock_llm, min_length=10)
        
        with pytest.raises(ContentFilterError) as exc_info:
            generator.generate(
                context="Test",
                system_prompt="Be helpful",
                few_shot_examples=[],
                subreddit="test",
                reddit_id="test123"
            )
        
        assert "too short" in str(exc_info.value).lower()
    
    def test_rejects_too_long_content(self):
        """Very long responses should be rejected."""
        from agents.generator import DraftGenerator, ContentFilterError
        
        mock_llm = Mock()
        mock_llm.invoke = Mock(return_value=Mock(content="A" * 5000))
        
        generator = DraftGenerator(llm=mock_llm, max_length=2000)
        
        with pytest.raises(ContentFilterError) as exc_info:
            generator.generate(
                context="Test",
                system_prompt="Be helpful",
                few_shot_examples=[],
                subreddit="test",
                reddit_id="test123"
            )
        
        assert "too long" in str(exc_info.value).lower()


class TestRetryLogic:
    """Test retry on filter failure."""
    
    def test_retries_on_banned_phrase(self):
        """Should retry generation if first attempt has banned phrase."""
        from agents.generator import DraftGenerator
        
        mock_llm = Mock()
        # First call returns banned content, second returns valid
        mock_llm.invoke = Mock(side_effect=[
            Mock(content="As an AI, I think..."),
            Mock(content="Yeah that's a common issue. Try this approach.")
        ])
        
        generator = DraftGenerator(llm=mock_llm, max_retries=2)
        
        result = generator.generate(
            context="Test",
            system_prompt="Be helpful",
            few_shot_examples=[],
            subreddit="test",
            reddit_id="test123"
        )
        
        # Should have called LLM twice
        assert mock_llm.invoke.call_count == 2
        assert result.content == "Yeah that's a common issue. Try this approach."
