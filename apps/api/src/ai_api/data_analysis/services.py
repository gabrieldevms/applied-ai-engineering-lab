from ai_api.data_analysis.exceptions import SQLGenerationError
from ai_api.data_analysis.parsers import parse_sql_generation_response
from ai_api.data_analysis.prompts import build_sql_generation_messages
from ai_api.data_analysis.schemas import (
    NaturalLanguageSQLRequest,
    SQLGenerationResponse,
)
from ai_api.data_analysis.sql_safety import ReadOnlySQLValidator
from ai_api.llm import LLMProvider, LLMProviderError


class DataAnalystSQLGenerationService:
    def __init__(
        self,
        llm_provider: LLMProvider,
        sql_validator: ReadOnlySQLValidator | None = None,
    ) -> None:
        self.llm_provider = llm_provider
        self.sql_validator = sql_validator or ReadOnlySQLValidator()

    def generate(
        self,
        request: NaturalLanguageSQLRequest,
    ) -> SQLGenerationResponse:
        messages = build_sql_generation_messages(request)

        try:
            llm_response = self.llm_provider.generate(messages)
        except LLMProviderError as exc:
            raise SQLGenerationError(
                "LLM provider failed during SQL generation."
            ) from exc

        candidate = parse_sql_generation_response(
            llm_response.content
        )

        validation = self.sql_validator.validate(candidate.sql)

        return SQLGenerationResponse(
            status=validation.status,
            request=request,
            candidate=candidate,
            validation=validation,
            metadata={
                "service": "data-analyst-sql-generation-v1",
                "llm_provider": llm_response.provider,
                "llm_model": llm_response.model,
            },
        )
