from collections.abc import Sequence
from typing import Protocol

from ai_api.llm.models import LLMMessage, LLMResponse


class LLMProvider(Protocol):
    def generate(self, messages: Sequence[LLMMessage]) -> LLMResponse:
        """Generate a response from a list of LLM messages."""
        ...
