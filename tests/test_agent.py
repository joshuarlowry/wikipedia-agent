"""Tests for the Wikipedia agent."""

import pytest
from unittest.mock import Mock, patch, MagicMock, PropertyMock
from src.agent import WikipediaAgent
from src.config import Config
from src.wikipedia.search import WikipediaArticle


class TestWikipediaAgent:
    """Tests for WikipediaAgent class."""

    @patch("src.agent.Config")
    def test_init_ollama(self, mock_config_class):
        """Test agent initialization with Ollama provider (Strands)."""
        mock_config = Mock()
        mock_config.llm_provider = "ollama"
        mock_config.wikipedia_config = {"language": "en"}
        mock_config.ollama_config = {
            "model": "mistral:latest",
            "base_url": "http://localhost:11434",
            "temperature": 0.7,
        }
        mock_config_class.return_value = mock_config

        agent = WikipediaAgent(mock_config)
        assert agent.config == mock_config
        assert agent.model is not None  # Strands model
        assert agent.agent is not None  # Strands Agent

    @patch("src.agent.Config")
    def test_init_openrouter(self, mock_config_class):
        """Test agent initialization with OpenRouter provider (Strands)."""
        mock_config = Mock()
        mock_config.llm_provider = "openrouter"
        mock_config.wikipedia_config = {"language": "en"}
        mock_config.openrouter_config = {
            "model": "anthropic/claude-3.5-sonnet",
            "api_key": "test_key",
            "base_url": "https://openrouter.ai/api/v1",
            "temperature": 0.7,
        }
        mock_config_class.return_value = mock_config

        agent = WikipediaAgent(mock_config)
        assert agent.config == mock_config
        assert agent.model is not None  # Strands model
        assert agent.agent is not None  # Strands Agent

    @patch("src.agent.Config")
    def test_init_invalid_provider(self, mock_config_class):
        """Test agent initialization with invalid provider raises error."""
        mock_config = Mock()
        mock_config.llm_provider = "invalid_provider"
        mock_config.wikipedia_config = {"language": "en"}
        mock_config_class.return_value = mock_config

        with pytest.raises(ValueError, match="Unknown LLM provider"):
            WikipediaAgent(mock_config)

    @pytest.mark.skip(reason="Method removed in Strands implementation - search handled by tools")
    def test_search_wikipedia(self):
        """Test Wikipedia search - deprecated in Strands implementation."""
        pass

    @pytest.mark.skip(reason="Method removed in Strands implementation - formatting handled by tools")
    def test_format_sources(self):
        """Test source formatting - deprecated in Strands implementation."""
        pass

    @pytest.mark.skip(reason="Method removed in Strands implementation - response generation handled by Strands Agent")
    def test_generate_response(self):
        """Test response generation - deprecated in Strands implementation."""
        pass

    @pytest.mark.skip(reason="Query behavior changed in Strands implementation - tools handle article search")
    def test_query_no_articles(self):
        """Test query when no articles are found - behavior handled by Strands tools now."""
        pass

    @patch("src.agent.Config")
    def test_is_ready(self, mock_config_class):
        """Test readiness check (Strands implementation)."""
        mock_config = Mock()
        mock_config.llm_provider = "ollama"
        mock_config.wikipedia_config = {"language": "en"}
        mock_config.ollama_config = {
            "model": "mistral:latest",
            "base_url": "http://localhost:11434"
        }

        agent = WikipediaAgent(mock_config)

        # In Strands implementation, is_ready checks if model exists
        assert agent.is_ready is True
