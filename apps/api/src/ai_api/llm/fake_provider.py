from collections.abc import Sequence

from ai_api.llm.models import LLMMessage, LLMResponse, LLMUsage


class FakeLLMProvider:
    provider_name = "fake"
    model_name = "fake-llm-v1"

    def __init__(
        self,
        response_content: str | None = None,
        response_contents: Sequence[str] | None = None,
    ) -> None:
        if response_content is not None and response_contents is not None:
            raise ValueError(
                "Use either response_content or response_contents, not both."
            )

        if response_contents is not None and len(response_contents) == 0:
            raise ValueError("response_contents cannot be empty.")

        self.response_content = response_content
        self.response_contents = list(response_contents) if response_contents else None
        self.calls = 0

    def generate(self, messages: Sequence[LLMMessage]) -> LLMResponse:
        user_messages = [
            message.content
            for message in messages
            if message.role == "user"
        ]

        latest_user_message = user_messages[-1] if user_messages else ""
        content = self._resolve_response_content(latest_user_message)

        estimated_input_tokens = sum(
            len(message.content.split())
            for message in messages
        )
        estimated_output_tokens = len(content.split())

        return LLMResponse(
            content=content,
            provider=self.provider_name,
            model=self.model_name,
            usage=LLMUsage(
                input_tokens=estimated_input_tokens,
                output_tokens=estimated_output_tokens,
                total_tokens=estimated_input_tokens + estimated_output_tokens,
            ),
        )

    def _resolve_response_content(self, latest_user_message: str) -> str:
        self.calls += 1

        if self.response_contents is not None:
            response_index = min(self.calls - 1, len(self.response_contents) - 1)
            return self.response_contents[response_index]

        if self.response_content is not None:
            return self.response_content

        return f"Fake LLM response for: {latest_user_message}"
