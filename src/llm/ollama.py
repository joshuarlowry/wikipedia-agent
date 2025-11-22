"""Ollama LLM provider implementation."""

import json
from typing import Iterator
import requests
from .base import LLMProvider, LLMResponse


class OllamaProvider(LLMProvider):
    """Ollama LLM provider."""

    def __init__(
        self,
        model: str,
        base_url: str = "http://localhost:11434",
        temperature: float = 0.7,
        **kwargs,
    ):
        """Initialize Ollama provider."""
        super().__init__(model, temperature, **kwargs)
        self.base_url = base_url.rstrip("/")
        self.api_url = f"{self.base_url}/api"

    def generate(self, system_prompt: str, user_prompt: str) -> LLMResponse:
        """Generate a non-streaming response from Ollama."""
        url = f"{self.api_url}/generate"

        # Combine system and user prompts
        full_prompt = f"{system_prompt}\n\n{user_prompt}"

        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "stream": False,
            "options": {"temperature": self.temperature},
        }

        try:
            response = requests.post(url, json=payload, timeout=120)
            response.raise_for_status()
            data = response.json()

            return LLMResponse(
                content=data.get("response", ""),
                model=self.model,
                finish_reason=data.get("done_reason"),
            )
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Ollama API request failed: {e}")

    def stream_generate(
        self, system_prompt: str, user_prompt: str
    ) -> Iterator[str]:
        """Generate a streaming response from Ollama."""
        url = f"{self.api_url}/generate"

        # Combine system and user prompts
        full_prompt = f"{system_prompt}\n\n{user_prompt}"

        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "stream": True,
            "options": {"temperature": self.temperature},
        }

        try:
            response = requests.post(url, json=payload, stream=True, timeout=120)
            response.raise_for_status()

            for line in response.iter_lines():
                if line:
                    data = json.loads(line)
                    if "response" in data:
                        yield data["response"]

        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Ollama streaming request failed: {e}")

    @property
    def is_available(self) -> bool:
        """Check if Ollama is running and accessible."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception:
            return False
