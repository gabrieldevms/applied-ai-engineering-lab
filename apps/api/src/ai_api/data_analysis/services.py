from ai_api.data_analysis.exceptions import SQLGenerationError
from ai_api.data_analysis.parsers import parse_sql_generation_response
from ai_api.data_analysis.prompts import build_sql_generation_messages
from ai_api.data_analysis.schemas import (
    NaturalLanguageSQLRequest,
    SQLExecutionRequest,
    SQLGenerationResponse,
    SQLWorkflowRequest,
    SQLWorkflowResponse,
)
from ai_api.data_analysis.sql_execution import SQLiteReadOnlyQueryExecutor
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


class DataAnalystSQLWorkflowService:
    def __init__(
        self,
        sql_generation_service: DataAnalystSQLGenerationService,
        query_executor: SQLiteReadOnlyQueryExecutor | None = None,
    ) -> None:
        self.sql_generation_service = sql_generation_service
        self.query_executor = query_executor or SQLiteReadOnlyQueryExecutor()

    def run(
        self,
        request: SQLWorkflowRequest,
    ) -> SQLWorkflowResponse:
        generation_request = NaturalLanguageSQLRequest(
            question=request.question,
            database_schema=request.database_schema,
            language=request.language,
            metadata={
                **request.metadata,
                "workflow_step": "sql_generation",
            },
        )

        generation = self.sql_generation_service.generate(
            generation_request
        )

        if generation.status == "blocked":
            return SQLWorkflowResponse(
                status="blocked",
                generation=generation,
                execution=None,
                evidence=None,
                metadata={
                    "service": "data-analyst-sql-workflow-v1",
                    "executed": False,
                    "blocked_reason": "generated_sql_failed_safety_validation",
                },
            )

        execution_request = SQLExecutionRequest(
            sql=generation.candidate.sql,
            database_schema=request.database_schema,
            table_data=request.table_data,
            max_rows=request.max_rows,
            metadata={
                **request.metadata,
                "workflow_step": "sql_execution",
            },
        )

        execution = self.query_executor.execute(execution_request)

        return SQLWorkflowResponse(
            status=execution.status,
            generation=generation,
            execution=execution,
            evidence=execution.evidence,
            metadata={
                "service": "data-analyst-sql-workflow-v1",
                "executed": execution.status == "executed",
                "generation_status": generation.status,
                "execution_status": execution.status,
            },
        )
