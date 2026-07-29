from ai_api.config import get_settings
from ai_api.data_analysis.fake_responses import (
    DEFAULT_SQL_GENERATION_RESPONSE_JSON,
)
from ai_api.data_analysis.services import DataAnalystSQLGenerationService
from ai_api.data_analysis.sql_execution import SQLiteReadOnlyQueryExecutor
from ai_api.llm import build_llm_provider


def get_data_analyst_sql_generation_service() -> DataAnalystSQLGenerationService:
    settings = get_settings()

    provider = build_llm_provider(
        settings=settings,
        fake_response_content=DEFAULT_SQL_GENERATION_RESPONSE_JSON,
    )

    return DataAnalystSQLGenerationService(
        llm_provider=provider,
    )


def get_sql_query_executor() -> SQLiteReadOnlyQueryExecutor:
    return SQLiteReadOnlyQueryExecutor()
