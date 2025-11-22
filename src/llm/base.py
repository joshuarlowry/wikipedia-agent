"""Base LLM provider interface."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Iterator, Optional


@dataclass
class LLMResponse:
    """Response from an LLM."""

    content: str
    model: str
    finish_reason: Optional[str] = None


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    def __init__(self, model: str, temperature: float = 0.7, **kwargs):
        """Initialize LLM provider."""
        self.model = model
        self.temperature = temperature
        self.kwargs = kwargs

    @abstractmethod
    def generate(self, system_prompt: str, user_prompt: str) -> LLMResponse:
        """
        Generate a response from the LLM.

        Args:
            system_prompt: System prompt/instructions
            user_prompt: User query/prompt

        Returns:
            LLMResponse object with the generated content
        """
        pass

    @abstractmethod
    def stream_generate(
        self, system_prompt: str, user_prompt: str
    ) -> Iterator[str]:
        """
        Generate a streaming response from the LLM.

        Args:
            system_prompt: System prompt/instructions
            user_prompt: User query/prompt

        Yields:
            Chunks of generated text
        """
        pass

    @property
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the LLM provider is available/reachable."""
        pass
