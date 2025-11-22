"""OpenRouter LLM provider implementation."""

import json
from typing import Iterator
import requests
from .base import LLMProvider, LLMResponse


class OpenRouterProvider(LLMProvider):
    """OpenRouter LLM provider."""

    def __init__(
        self,
        model: str,
        api_key: str,
        base_url: str = "https://openrouter.ai/api/v1",
        temperature: float = 0.7,
        **kwargs,
    ):
        """Initialize OpenRouter provider."""
        super().__init__(model, temperature, **kwargs)
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")

        if not self.api_key:
            raise ValueError("OpenRouter API key is required")

    def _get_headers(self) -> dict:
        """Get request headers with authentication."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/wikipedia-agent",
        }

    def generate(self, system_prompt: str, user_prompt: str) -> LLMResponse:
        """Generate a non-streaming response from OpenRouter."""
        url = f"{self.base_url}/chat/completions"

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": self.temperature,
            "stream": False,
        }

        try:
            response = requests.post(
                url, json=payload, headers=self._get_headers(), timeout=120
            )
            response.raise_for_status()
            data = response.json()

            content = data["choices"][0]["message"]["content"]
            finish_reason = data["choices"][0].get("finish_reason")

            return LLMResponse(
                content=content, model=self.model, finish_reason=finish_reason
            )
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"OpenRouter API request failed: {e}")

    def stream_generate(
        self, system_prompt: str, user_prompt: str
    ) -> Iterator[str]:
        """Generate a streaming response from OpenRouter."""
        url = f"{self.base_url}/chat/completions"

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": self.temperature,
            "stream": True,
        }

        try:
            response = requests.post(
                url,
                json=payload,
                headers=self._get_headers(),
                stream=True,
                timeout=120,
            )
            response.raise_for_status()

            for line in response.iter_lines():
                if line:
                    line_str = line.decode("utf-8")
                    if line_str.startswith("data: "):
                        data_str = line_str[6:]  # Remove "data: " prefix
                        if data_str == "[DONE]":
                            break

                        try:
                            data = json.loads(data_str)
                            delta = data["choices"][0].get("delta", {})
                            if "content" in delta:
                                yield delta["content"]
                        except json.JSONDecodeError:
                            continue

        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"OpenRouter streaming request failed: {e}")

    @property
    def is_available(self) -> bool:
        """Check if OpenRouter API is accessible."""
        try:
            url = f"{self.base_url}/models"
            response = requests.get(url, headers=self._get_headers(), timeout=5)
            return response.status_code == 200
        except Exception:
            return False
