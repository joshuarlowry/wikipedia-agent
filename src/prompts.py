"""Prompt template management."""

from pathlib import Path
from typing import Dict
import yaml


class PromptManager:
    """Manages prompt templates for the agent."""

    def __init__(self, prompts_dir: str | Path = "prompts"):
        """Initialize prompt manager."""
        self.prompts_dir = Path(prompts_dir)
        self._templates: Dict[str, str] = {}
        self._load_templates()

    def _load_templates(self):
        """Load prompt templates from YAML file."""
        system_file = self.prompts_dir / "system.yaml"
        if system_file.exists():
            with open(system_file, "r") as f:
                self._templates = yaml.safe_load(f) or {}

    def get_system_prompt(self, mode: str = "mla") -> str:
        """Get the system prompt for the specified mode."""
        if mode == "json":
            return self._templates.get("system_prompt_json", "")
        return self._templates.get("system_prompt", "")

    def get_user_template(self) -> str:
        """Get the user prompt template."""
        return self._templates.get("user_template", "")

    def format_user_prompt(
        self, question: str, sources: str, citations: str
    ) -> str:
        """Format the user prompt with provided data."""
        template = self.get_user_template()
        return template.format(
            question=question, sources=sources, citations=citations
        )
