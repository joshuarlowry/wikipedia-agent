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
        """Test agent initialization with Ollama provider."""
        mock_config = Mock()
        mock_config.llm_provider = "ollama"
        mock_config.wikipedia_config = {"language": "en"}
        mock_config.ollama_config = {
            "model": "llama3.2",
            "base_url": "http://localhost:11434",
            "temperature": 0.7,
        }
        mock_config_class.return_value = mock_config

        agent = WikipediaAgent(mock_config)
        assert agent.config == mock_config
        assert agent.llm is not None

    @patch("src.agent.Config")
    def test_init_openrouter(self, mock_config_class):
        """Test agent initialization with OpenRouter provider."""
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
        assert agent.llm is not None

    @patch("src.agent.Config")
    def test_init_invalid_provider(self, mock_config_class):
        """Test agent initialization with invalid provider raises error."""
        mock_config = Mock()
        mock_config.llm_provider = "invalid_provider"
        mock_config.wikipedia_config = {"language": "en"}
        mock_config_class.return_value = mock_config

        with pytest.raises(ValueError, match="Unknown LLM provider"):
            WikipediaAgent(mock_config)

    @patch("src.agent.WikipediaSearch")
    @patch("src.agent.Config")
    def test_search_wikipedia(self, mock_config_class, mock_wiki_search):
        """Test Wikipedia search."""
        mock_config = Mock()
        mock_config.llm_provider = "ollama"
        mock_config.wikipedia_config = {
            "language": "en",
            "max_articles": 3,
            "max_chars_per_article": 3000,
        }
        mock_config.ollama_config = {"model": "llama3.2"}

        mock_article = WikipediaArticle(
            title="Test Article",
            url="https://test.com",
            summary="Summary",
            content="Content",
        )

        mock_search_instance = Mock()
        mock_search_instance.search_and_retrieve.return_value = [mock_article]
        mock_wiki_search.return_value = mock_search_instance

        agent = WikipediaAgent(mock_config)
        articles = agent.search_wikipedia("test query")

        assert len(articles) == 1
        assert articles[0].title == "Test Article"

    @patch("src.agent.Config")
    def test_format_sources(self, mock_config_class):
        """Test source formatting."""
        mock_config = Mock()
        mock_config.llm_provider = "ollama"
        mock_config.wikipedia_config = {"language": "en"}
        mock_config.ollama_config = {"model": "llama3.2"}

        articles = [
            WikipediaArticle(
                title="Article 1",
                url="https://test1.com",
                summary="Summary 1",
                content="Content 1",
            ),
            WikipediaArticle(
                title="Article 2",
                url="https://test2.com",
                summary="Summary 2",
                content="Content 2",
            ),
        ]

        agent = WikipediaAgent(mock_config)
        formatted = agent._format_sources(articles)

        assert "Source 1: Article 1" in formatted
        assert "Source 2: Article 2" in formatted
        assert "https://test1.com" in formatted
        assert "Content 1" in formatted

    @patch("src.agent.Config")
    def test_generate_response(self, mock_config_class):
        """Test response generation."""
        mock_config = Mock()
        mock_config.llm_provider = "ollama"
        mock_config.wikipedia_config = {"language": "en"}
        mock_config.ollama_config = {"model": "llama3.2"}

        articles = [
            WikipediaArticle(
                title="Test",
                url="https://test.com",
                summary="Summary",
                content="Content",
            )
        ]

        agent = WikipediaAgent(mock_config)

        # Mock the LLM
        mock_response = Mock()
        mock_response.content = "Generated response with Works Cited section"
        agent.llm.generate = Mock(return_value=mock_response)

        response = agent.generate_response("What is test?", articles)
        assert response == "Generated response with Works Cited section"
        agent.llm.generate.assert_called_once()

    @patch("src.agent.Config")
    def test_query_no_articles(self, mock_config_class):
        """Test query when no articles are found."""
        mock_config = Mock()
        mock_config.llm_provider = "ollama"
        mock_config.wikipedia_config = {"language": "en"}
        mock_config.ollama_config = {"model": "llama3.2"}

        agent = WikipediaAgent(mock_config)
        agent.search_wikipedia = Mock(return_value=[])

        response = agent.query("nonexistent query", stream=False)
        assert "No Wikipedia articles found" in response

    @patch("src.agent.Config")
    def test_is_ready(self, mock_config_class):
        """Test readiness check."""
        mock_config = Mock()
        mock_config.llm_provider = "ollama"
        mock_config.wikipedia_config = {"language": "en"}
        mock_config.ollama_config = {"model": "llama3.2"}

        agent = WikipediaAgent(mock_config)

        # Mock the is_available property
        type(agent.llm).is_available = PropertyMock(return_value=True)

        assert agent.is_ready is True
