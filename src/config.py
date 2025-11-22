"""Configuration management for the Wikipedia agent."""

import os
from pathlib import Path
from typing import Any, Dict
import yaml
from dotenv import load_dotenv


class Config:
    """Configuration manager for the agent."""

    def __init__(self, config_path: str | Path = "config.yaml"):
        """Initialize configuration from YAML file and environment variables."""
        load_dotenv()

        self.config_path = Path(config_path)
        self._config: Dict[str, Any] = {}

        if self.config_path.exists():
            with open(self.config_path, "r") as f:
                self._config = yaml.safe_load(f) or {}

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value using dot notation (e.g., 'llm.provider')."""
        keys = key.split(".")
        value = self._config

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default

        return value if value is not None else default

    @property
    def llm_provider(self) -> str:
        """Get the configured LLM provider."""
        return self.get("llm.provider", "ollama")

    @property
    def ollama_config(self) -> Dict[str, Any]:
        """Get Ollama configuration."""
        return self.get("llm.ollama", {})

    @property
    def openrouter_config(self) -> Dict[str, Any]:
        """Get OpenRouter configuration."""
        config = self.get("llm.openrouter", {})
        # Load API key from environment if specified
        if "api_key_env" in config:
            env_var = config["api_key_env"]
            config["api_key"] = os.getenv(env_var, "")
        return config

    @property
    def wikipedia_config(self) -> Dict[str, Any]:
        """Get Wikipedia configuration."""
        return self.get("wikipedia", {})

    @property
    def agent_config(self) -> Dict[str, Any]:
        """Get agent configuration."""
        return self.get("agent", {})

    @property
    def output_format(self) -> str:
        """Get the output format (mla or json)."""
        return self.get("agent.output_format", "mla")
