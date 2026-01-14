"""
Test prompt management system (Story 5).
"""
import pytest
from unittest.mock import Mock, patch
import os
import tempfile
import yaml


class TestExternalLoading:
    """Test external template loading."""
    
    def test_loads_templates_from_yaml(self, tmp_path):
        """Verify PromptManager loads templates from prompts/templates.yaml. Fail if file missing."""
        from services.prompt_manager import PromptManager
        
        # Create temporary YAML file
        templates = {
            "technical_peer": {
                "subreddits": ["sysadmin", "devops"],
                "system_prompt": "You are a helpful technical peer on Reddit.",
                "few_shot_examples": [
                    "Yeah I ran into that too. Check if...",
                    "That's usually a permissions thing..."
                ]
            }
        }
        
        yaml_path = tmp_path / "templates.yaml"
        with open(yaml_path, 'w') as f:
            yaml.dump(templates, f)
        
        manager = PromptManager(templates_path=str(yaml_path))
        
        # Should load successfully
        assert "technical_peer" in manager.templates
        assert manager.templates["technical_peer"]["subreddits"] == ["sysadmin", "devops"]
    
    def test_fails_if_file_missing(self):
        """Fail if templates file is missing."""
        from services.prompt_manager import PromptManager, TemplateLoadError
        
        with pytest.raises(TemplateLoadError):
            PromptManager(templates_path="/nonexistent/path/templates.yaml")


class TestTemplateSelection:
    """Test template selection by subreddit."""
    
    def test_selects_template_for_subreddit(self, tmp_path):
        """Request template for r/sysadmin. Assert 'technical_peer' template returned."""
        from services.prompt_manager import PromptManager
        
        templates = {
            "technical_peer": {
                "subreddits": ["sysadmin", "devops"],
                "system_prompt": "Technical peer prompt",
                "few_shot_examples": ["Example 1"]
            },
            "casual": {
                "subreddits": ["startups", "learnpython"],
                "system_prompt": "Casual prompt",
                "few_shot_examples": ["Example 2"]
            }
        }
        
        yaml_path = tmp_path / "templates.yaml"
        with open(yaml_path, 'w') as f:
            yaml.dump(templates, f)
        
        manager = PromptManager(templates_path=str(yaml_path))
        template = manager.get_template_for_subreddit("sysadmin")
        
        assert template is not None
        assert template["system_prompt"] == "Technical peer prompt"
    
    def test_returns_default_for_unknown_subreddit(self, tmp_path):
        """Unknown subreddit should return default template."""
        from services.prompt_manager import PromptManager
        
        templates = {
            "default": {
                "subreddits": [],
                "system_prompt": "Default prompt",
                "few_shot_examples": []
            },
            "technical_peer": {
                "subreddits": ["sysadmin"],
                "system_prompt": "Technical prompt",
                "few_shot_examples": []
            }
        }
        
        yaml_path = tmp_path / "templates.yaml"
        with open(yaml_path, 'w') as f:
            yaml.dump(templates, f)
        
        manager = PromptManager(templates_path=str(yaml_path))
        template = manager.get_template_for_subreddit("unknownsubreddit")
        
        # Should fallback to default
        assert template["system_prompt"] == "Default prompt"


class TestPIIScrubbing:
    """Test PII scrubbing."""
    
    def test_scrubs_email_addresses(self):
        """Pass string with email address. Assert returned string has [REDACTED]."""
        from services.prompt_manager import PromptManager
        
        manager = PromptManager.__new__(PromptManager)
        manager.templates = {}
        
        text = "Contact me at john.doe@example.com for more info"
        scrubbed = manager.scrub_pii(text)
        
        assert "john.doe@example.com" not in scrubbed
        assert "[REDACTED_EMAIL]" in scrubbed
    
    def test_scrubs_phone_numbers(self):
        """Phone numbers should be scrubbed."""
        from services.prompt_manager import PromptManager
        
        manager = PromptManager.__new__(PromptManager)
        manager.templates = {}
        
        text = "Call me at 555-123-4567 or (555) 987-6543"
        scrubbed = manager.scrub_pii(text)
        
        assert "555-123-4567" not in scrubbed
        assert "[REDACTED_PHONE]" in scrubbed
    
    def test_preserves_normal_text(self):
        """Normal text should be preserved."""
        from services.prompt_manager import PromptManager
        
        manager = PromptManager.__new__(PromptManager)
        manager.templates = {}
        
        text = "This is a normal comment about Python programming"
        scrubbed = manager.scrub_pii(text)
        
        assert scrubbed == text
    
    def test_scrubs_credit_card_numbers(self):
        """Credit card numbers should be scrubbed."""
        from services.prompt_manager import PromptManager
        
        manager = PromptManager.__new__(PromptManager)
        manager.templates = {}
        
        text = "My card is 4111-1111-1111-1111"
        scrubbed = manager.scrub_pii(text)
        
        assert "4111-1111-1111-1111" not in scrubbed
        assert "[REDACTED_CREDIT_CARD]" in scrubbed
    
    def test_scrubs_ip_addresses(self):
        """IP addresses should be scrubbed."""
        from services.prompt_manager import PromptManager
        
        manager = PromptManager.__new__(PromptManager)
        manager.templates = {}
        
        text = "Server is at 192.168.1.100"
        scrubbed = manager.scrub_pii(text)
        
        assert "192.168.1.100" not in scrubbed
        assert "[REDACTED_IP_ADDRESS]" in scrubbed
    
    def test_scrubs_ssn(self):
        """SSN should be scrubbed."""
        from services.prompt_manager import PromptManager
        
        manager = PromptManager.__new__(PromptManager)
        manager.templates = {}
        
        text = "My SSN is 123-45-6789"
        scrubbed = manager.scrub_pii(text)
        
        assert "123-45-6789" not in scrubbed
        assert "[REDACTED_SSN]" in scrubbed
    
    def test_scrubs_multiple_pii_types(self):
        """Multiple PII types in one string should all be scrubbed."""
        from services.prompt_manager import PromptManager
        
        manager = PromptManager.__new__(PromptManager)
        manager.templates = {}
        
        text = "Email me at test@example.com, call 555-123-4567, server at 10.0.0.1"
        scrubbed = manager.scrub_pii(text)
        
        assert "test@example.com" not in scrubbed
        assert "555-123-4567" not in scrubbed
        assert "10.0.0.1" not in scrubbed
        assert "[REDACTED_EMAIL]" in scrubbed
        assert "[REDACTED_PHONE]" in scrubbed
        assert "[REDACTED_IP_ADDRESS]" in scrubbed


class TestPromptBuilding:
    """Test prompt building with context and few-shot examples."""
    
    def test_builds_prompt_with_context(self, tmp_path):
        """Prompt should include context and few-shot examples."""
        from services.prompt_manager import PromptManager
        
        templates = {
            "technical_peer": {
                "subreddits": ["sysadmin"],
                "system_prompt": "You are a helpful technical peer.",
                "few_shot_examples": [
                    "Yeah I ran into that too.",
                    "That's usually a permissions thing."
                ]
            }
        }
        
        yaml_path = tmp_path / "templates.yaml"
        with open(yaml_path, 'w') as f:
            yaml.dump(templates, f)
        
        manager = PromptManager(templates_path=str(yaml_path))
        
        context = "[Post Title]\nHelp with DNS\n\n[Target Comment]\nI can't resolve hostnames"
        
        prompt = manager.build_prompt(
            subreddit="sysadmin",
            context=context
        )
        
        # Should include system prompt
        assert "helpful technical peer" in prompt.lower() or "technical peer" in prompt
        
        # Should include at least one few-shot example
        assert "ran into that" in prompt or "permissions" in prompt
        
        # Should include context
        assert "DNS" in prompt or "resolve hostnames" in prompt
    
    def test_scrubs_pii_in_context(self, tmp_path):
        """PII in context should be scrubbed before sending to LLM."""
        from services.prompt_manager import PromptManager
        
        templates = {
            "default": {
                "subreddits": [],
                "system_prompt": "Default",
                "few_shot_examples": []
            }
        }
        
        yaml_path = tmp_path / "templates.yaml"
        with open(yaml_path, 'w') as f:
            yaml.dump(templates, f)
        
        manager = PromptManager(templates_path=str(yaml_path))
        
        context = "Contact me at secret@email.com for help"
        prompt = manager.build_prompt(subreddit="test", context=context)
        
        assert "secret@email.com" not in prompt
