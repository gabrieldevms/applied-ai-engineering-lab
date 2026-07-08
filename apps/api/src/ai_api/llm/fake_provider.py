from collections.abc import Sequence

from ai_api.llm.models import LLMMessage, LLMResponse, LLMUsage


class FakeLLMProvider:
    provider_name = "fake"
    model_name = "fake-llm-v1"

    def generate(self, messages: Sequence[LLMMessage]) -> LLMResponse:
        user_messages = [
            message.content
            for message in messages
            if message.role == "user"
        ]

        latest_user_message = user_messages[-1] if user_messages else ""

        content = f"Fake LLM response for: {latest_user_message}"

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
