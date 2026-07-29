import json

from ai_api.data_analysis.schemas import NaturalLanguageSQLRequest
from ai_api.llm import LLMMessage


def build_sql_generation_messages(
    request: NaturalLanguageSQLRequest,
) -> list[LLMMessage]:
    schema_json = json.dumps(
        request.database_schema.model_dump(),
        ensure_ascii=False,
        indent=2,
    )

    return [
        LLMMessage(
            role="system",
            content=(
                "You are a careful data analyst assistant specialized in "
                "read-only SQL generation for QA and business validation.\n\n"
                "Rules:\n"
                "- Return only one valid JSON object.\n"
                "- Do not use Markdown.\n"
                "- Generate only read-only SQL.\n"
                "- Only SELECT or WITH statements are allowed.\n"
                "- Never generate INSERT, UPDATE, DELETE, DROP, ALTER, "
                "TRUNCATE, CREATE, MERGE, EXEC, GRANT, REVOKE or similar "
                "unsafe commands.\n"
                "- Do not generate multiple SQL statements.\n"
                "- Use only tables and columns present in the provided schema.\n"
                "- Do not translate table names or column names.\n"
                "- Keep SQL identifiers exactly as they appear in the schema.\n"
                "- Write explanation and assumptions in the requested language.\n\n"
                "The JSON object must follow this shape:\n"
                "{\n"
                '  "sql": "SELECT ...",\n'
                '  "explanation": "Explain the query in the requested language.",\n'
                '  "assumptions": ["Assumption 1 in the requested language"]\n'
                "}"
            ),
        ),
        LLMMessage(
            role="user",
            content=(
                f"Requested language: {request.language}\n\n"
                f"Question:\n{request.question}\n\n"
                f"Database schema:\n{schema_json}"
            ),
        ),
    ]
