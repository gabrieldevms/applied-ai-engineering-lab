from ai_api.config import get_settings
from ai_api.llm.factory import build_llm_provider
from ai_api.rag.answer_generation import RAGAnswerService
from ai_api.rag.fake_responses import DEFAULT_RAG_ANSWER_RESPONSE
from ai_api.rag.semantic_search import SemanticSearchService


def get_rag_answer_service() -> RAGAnswerService:
    settings = get_settings()

    llm_provider = build_llm_provider(
        settings=settings,
        fake_response_content=DEFAULT_RAG_ANSWER_RESPONSE,
    )

    return RAGAnswerService(
        semantic_search_service=SemanticSearchService(),
        llm_provider=llm_provider,
    )
