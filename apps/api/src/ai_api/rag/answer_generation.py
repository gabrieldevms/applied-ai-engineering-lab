from ai_api.llm import LLMProvider, LLMProviderError
from ai_api.rag.exceptions import RAGAnswerGenerationError
from ai_api.rag.prompts import build_rag_answer_messages
from ai_api.rag.schemas import (
    RAGAnswerResponse,
    SemanticSearchDocument,
)
from ai_api.rag.semantic_search import SemanticSearchService
from ai_api.rag.citations import build_source_citations


class RAGAnswerService:
    def __init__(
        self,
        semantic_search_service: SemanticSearchService,
        llm_provider: LLMProvider,
    ) -> None:
        self.semantic_search_service = semantic_search_service
        self.llm_provider = llm_provider

    def answer(
        self,
        query: str,
        documents: list[SemanticSearchDocument],
        language: str = "pt-BR",
        top_k: int = 3,
        chunk_size: int = 800,
        chunk_overlap: int = 120,
    ) -> RAGAnswerResponse:
        search_response = self.semantic_search_service.search(
            query=query,
            documents=documents,
            top_k=top_k,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

        if not search_response.results:
            raise RAGAnswerGenerationError(
                "No context chunks were retrieved for the query."
            )

        messages = build_rag_answer_messages(
            query=search_response.query,
            context_chunks=search_response.results,
            language=language,
        )

        try:
            llm_response = self.llm_provider.generate(messages)
        except LLMProviderError as exc:
            raise RAGAnswerGenerationError(
                "LLM provider failed during RAG answer generation."
            ) from exc

        answer = llm_response.content.strip()

        if not answer:
            raise RAGAnswerGenerationError(
                "LLM provider returned an empty answer."
            )
        
        citations = build_source_citations(search_response.results)

        return RAGAnswerResponse(
            query=search_response.query,
            answer=answer,
            provider=llm_response.provider,
            model=llm_response.model,
            total_context_chunks=len(search_response.results),
            context_chunks=search_response.results,
            citations=citations,
            metadata={
                "total_indexed_chunks": search_response.total_indexed_chunks,
                "language": language,
            },
        )
