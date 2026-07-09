from collections.abc import Sequence
from typing import Any
from openai import OpenAI
from ai_api.llm.exceptions import LLMProviderError
from ai_api.llm.models import LLMMessage, LLMResponse, LLMUsage


class OpenAIProvider:
    provider_name = "openai"

    def __init__(
        self,
        api_key: str,
        model: str,
        client: Any | None = None,
    ) -> None:
        if not api_key.strip():
            raise ValueError("api_key cannot be empty")

        if not model.strip():
            raise ValueError("model cannot be empty")

        self.model_name = model
        self.client = client or OpenAI(api_key=api_key)

    def generate(self, messages: Sequence[LLMMessage]) -> LLMResponse:
        try:
            response = self.client.responses.create(
                model=self.model_name,
                input=self._format_messages(messages),
            )
        except Exception as exc:
            raise LLMProviderError("OpenAI provider request failed.") from exc

        content = getattr(response, "output_text", None)

        if not isinstance(content, str) or not content.strip():
            raise LLMProviderError(
                "OpenAI response did not contain output text."
            )

        return LLMResponse(
            content=content,
            provider=self.provider_name,
            model=self.model_name,
            usage=self._extract_usage(response),
        )

    def _format_messages(self, messages: Sequence[LLMMessage]) -> str:
        return "\n\n".join(
            f"{message.role.upper()}:\n{message.content}"
            for message in messages
        )

    def _extract_usage(self, response: Any) -> LLMUsage | None:
        usage = getattr(response, "usage", None)

        if usage is None:
            return None

        input_tokens = getattr(usage, "input_tokens", 0) or 0
        output_tokens = getattr(usage, "output_tokens", 0) or 0
        total_tokens = getattr(usage, "total_tokens", 0) or (
            input_tokens + output_tokens
        )

        return LLMUsage(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
        )
