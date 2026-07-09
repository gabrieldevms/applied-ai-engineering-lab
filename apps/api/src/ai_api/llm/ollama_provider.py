from collections.abc import Sequence
from typing import Any

import httpx

from ai_api.llm.exceptions import LLMProviderError
from ai_api.llm.models import LLMMessage, LLMResponse, LLMUsage


class OllamaProvider:
    provider_name = "ollama"

    def __init__(
        self,
        base_url: str,
        model: str,
        timeout_seconds: float = 120,
        client: Any | None = None,
    ) -> None:
        if not base_url.strip():
            raise ValueError("base_url cannot be empty")

        if not model.strip():
            raise ValueError("model cannot be empty")

        self.base_url = base_url.rstrip("/")
        self.model_name = model
        self.client = client or httpx.Client(
            base_url=self.base_url,
            timeout=timeout_seconds,
        )

    def generate(self, messages: Sequence[LLMMessage]) -> LLMResponse:
        try:
            response = self.client.post(
                "/api/chat",
                json={
                    "model": self.model_name,
                    "messages": [
                        {
                            "role": message.role,
                            "content": message.content,
                        }
                        for message in messages
                    ],
                    "stream": False,
                    "format": "json",
                    "options": {
                        "temperature": 0,
                    },
                },
            )
            response.raise_for_status()
            data = response.json()
        except Exception as exc:
            raise LLMProviderError("Ollama provider request failed.") from exc

        content = self._extract_content(data)

        return LLMResponse(
            content=content,
            provider=self.provider_name,
            model=self.model_name,
            usage=self._extract_usage(data),
        )

    def _extract_content(self, data: dict[str, Any]) -> str:
        message = data.get("message")

        if not isinstance(message, dict):
            raise LLMProviderError(
                "Ollama response did not contain a message object."
            )

        content = message.get("content")

        if not isinstance(content, str) or not content.strip():
            raise LLMProviderError(
                "Ollama response did not contain message content."
            )

        return content

    def _extract_usage(self, data: dict[str, Any]) -> LLMUsage:
        input_tokens = data.get("prompt_eval_count", 0) or 0
        output_tokens = data.get("eval_count", 0) or 0

        return LLMUsage(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=input_tokens + output_tokens,
        )
