"""Tests for configuration management."""

import pytest
import tempfile
import os
from pathlib import Path
from src.config import Config


class TestConfig:
    """Tests for Config class."""

    def test_init_with_nonexistent_file(self):
        """Test initialization with non-existent config file."""
        config = Config("nonexistent.yaml")
        assert config._config == {}

    def test_init_with_valid_file(self):
        """Test initialization with valid config file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("llm:\n  provider: ollama\n  ollama:\n    model: llama3.2\n")
            temp_path = f.name

        try:
            config = Config(temp_path)
            assert config.get("llm.provider") == "ollama"
            assert config.get("llm.ollama.model") == "llama3.2"
        finally:
            os.unlink(temp_path)

    def test_get_with_dot_notation(self):
        """Test get method with dot notation."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("a:\n  b:\n    c: value\n")
            temp_path = f.name

        try:
            config = Config(temp_path)
            assert config.get("a.b.c") == "value"
            assert config.get("a.b") == {"c": "value"}
        finally:
            os.unlink(temp_path)

    def test_get_with_default(self):
        """Test get method with default value."""
        config = Config("nonexistent.yaml")
        assert config.get("missing.key", "default") == "default"

    def test_llm_provider_property(self):
        """Test llm_provider property."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("llm:\n  provider: openrouter\n")
            temp_path = f.name

        try:
            config = Config(temp_path)
            assert config.llm_provider == "openrouter"
        finally:
            os.unlink(temp_path)

    def test_ollama_config_property(self):
        """Test ollama_config property."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("llm:\n  ollama:\n    model: llama3.2\n    base_url: http://localhost:11434\n")
            temp_path = f.name

        try:
            config = Config(temp_path)
            ollama_config = config.ollama_config
            assert ollama_config["model"] == "llama3.2"
            assert ollama_config["base_url"] == "http://localhost:11434"
        finally:
            os.unlink(temp_path)

    def test_openrouter_config_with_env(self):
        """Test openrouter_config property with environment variable."""
        os.environ["TEST_API_KEY"] = "secret_key"

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("llm:\n  openrouter:\n    api_key_env: TEST_API_KEY\n    model: test-model\n")
            temp_path = f.name

        try:
            config = Config(temp_path)
            openrouter_config = config.openrouter_config
            assert openrouter_config["api_key"] == "secret_key"
        finally:
            os.unlink(temp_path)
            del os.environ["TEST_API_KEY"]

    def test_wikipedia_config_property(self):
        """Test wikipedia_config property."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("wikipedia:\n  language: en\n  max_articles: 5\n")
            temp_path = f.name

        try:
            config = Config(temp_path)
            wiki_config = config.wikipedia_config
            assert wiki_config["language"] == "en"
            assert wiki_config["max_articles"] == 5
        finally:
            os.unlink(temp_path)

    def test_agent_config_property(self):
        """Test agent_config property."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("agent:\n  stream_response: true\n  enforce_citations: true\n")
            temp_path = f.name

        try:
            config = Config(temp_path)
            agent_config = config.agent_config
            assert agent_config["stream_response"] is True
            assert agent_config["enforce_citations"] is True
        finally:
            os.unlink(temp_path)
