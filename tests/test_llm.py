"""Tests for LLM providers."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.llm import LLMResponse, OllamaProvider, OpenRouterProvider


class TestOllamaProvider:
    """Tests for OllamaProvider."""

    def test_init(self):
        """Test OllamaProvider initialization."""
        provider = OllamaProvider(
            model="llama3.2", base_url="http://localhost:11434", temperature=0.7
        )
        assert provider.model == "llama3.2"
        assert provider.base_url == "http://localhost:11434"
        assert provider.temperature == 0.7

    def test_base_url_strip_slash(self):
        """Test that trailing slash is removed from base URL."""
        provider = OllamaProvider(model="llama3.2", base_url="http://localhost:11434/")
        assert provider.base_url == "http://localhost:11434"

    @patch("src.llm.ollama.requests.post")
    def test_generate(self, mock_post):
        """Test non-streaming generation."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "response": "Test response",
            "done_reason": "stop",
        }
        mock_post.return_value = mock_response

        provider = OllamaProvider(model="llama3.2")
        response = provider.generate("System prompt", "User prompt")

        assert isinstance(response, LLMResponse)
        assert response.content == "Test response"
        assert response.model == "llama3.2"
        assert response.finish_reason == "stop"

    @patch("src.llm.ollama.requests.post")
    def test_stream_generate(self, mock_post):
        """Test streaming generation."""
        mock_response = Mock()
        mock_response.iter_lines.return_value = [
            b'{"response": "Hello", "done": false}',
            b'{"response": " world", "done": false}',
            b'{"response": "!", "done": true}',
        ]
        mock_post.return_value = mock_response

        provider = OllamaProvider(model="llama3.2")
        chunks = list(provider.stream_generate("System prompt", "User prompt"))

        assert chunks == ["Hello", " world", "!"]

    @patch("src.llm.ollama.requests.get")
    def test_is_available(self, mock_get):
        """Test availability check."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        provider = OllamaProvider(model="llama3.2")
        assert provider.is_available is True


class TestOpenRouterProvider:
    """Tests for OpenRouterProvider."""

    def test_init(self):
        """Test OpenRouterProvider initialization."""
        provider = OpenRouterProvider(
            model="anthropic/claude-3.5-sonnet",
            api_key="test_key",
            temperature=0.7,
        )
        assert provider.model == "anthropic/claude-3.5-sonnet"
        assert provider.api_key == "test_key"
        assert provider.temperature == 0.7

    def test_init_no_api_key(self):
        """Test initialization without API key raises error."""
        with pytest.raises(ValueError, match="API key is required"):
            OpenRouterProvider(model="test-model", api_key="")

    @patch("src.llm.openrouter.requests.post")
    def test_generate(self, mock_post):
        """Test non-streaming generation."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [
                {"message": {"content": "Test response"}, "finish_reason": "stop"}
            ]
        }
        mock_post.return_value = mock_response

        provider = OpenRouterProvider(
            model="anthropic/claude-3.5-sonnet", api_key="test_key"
        )
        response = provider.generate("System prompt", "User prompt")

        assert isinstance(response, LLMResponse)
        assert response.content == "Test response"
        assert response.finish_reason == "stop"

    @patch("src.llm.openrouter.requests.post")
    def test_stream_generate(self, mock_post):
        """Test streaming generation."""
        mock_response = Mock()
        mock_response.iter_lines.return_value = [
            b'data: {"choices": [{"delta": {"content": "Hello"}}]}',
            b'data: {"choices": [{"delta": {"content": " world"}}]}',
            b"data: [DONE]",
        ]
        mock_post.return_value = mock_response

        provider = OpenRouterProvider(
            model="anthropic/claude-3.5-sonnet", api_key="test_key"
        )
        chunks = list(provider.stream_generate("System prompt", "User prompt"))

        assert chunks == ["Hello", " world"]

    @patch("src.llm.openrouter.requests.get")
    def test_is_available(self, mock_get):
        """Test availability check."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        provider = OpenRouterProvider(
            model="anthropic/claude-3.5-sonnet", api_key="test_key"
        )
        assert provider.is_available is True

    def test_get_headers(self):
        """Test header generation."""
        provider = OpenRouterProvider(
            model="anthropic/claude-3.5-sonnet", api_key="test_key"
        )
        headers = provider._get_headers()

        assert headers["Authorization"] == "Bearer test_key"
        assert headers["Content-Type"] == "application/json"
