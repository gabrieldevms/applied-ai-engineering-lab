import pytest

from ai_api.llm import FakeLLMProvider, LLMProviderError
from ai_api.rag import (
    RAGAnswerGenerationError,
    RAGAnswerService,
    SemanticSearchDocument,
    SemanticSearchService,
)


class FailingLLMProvider:
    provider_name = "failing"
    model_name = "failing-model"

    def generate(self, messages):
        raise LLMProviderError("Provider failed.")


def test_rag_answer_service_should_generate_answer_from_retrieved_context() -> None:
    service = RAGAnswerService(
        semantic_search_service=SemanticSearchService(),
        llm_provider=FakeLLMProvider(
            response_content="O cliente pode gerar boleto após a renegociação."
        ),
    )

    response = service.answer(
        query="Como o cliente gera um boleto?",
        documents=[
            SemanticSearchDocument(
                source="requirement-001",
                title="Renegociação",
                document_text="Após renegociar a dívida, o cliente pode gerar um boleto atualizado.",
                metadata={"domain": "billing"},
            )
        ],
        top_k=1,
        chunk_size=200,
        chunk_overlap=40,
    )

    assert response.answer == "O cliente pode gerar boleto após a renegociação."
    assert response.provider == "fake"
    assert response.model == "fake-llm-v1"
    assert response.total_context_chunks == 1
    assert response.context_chunks[0].metadata["source"] == "requirement-001"
    assert response.metadata["total_indexed_chunks"] == 1


def test_rag_answer_service_should_raise_error_when_llm_provider_fails() -> None:
    service = RAGAnswerService(
        semantic_search_service=SemanticSearchService(),
        llm_provider=FailingLLMProvider(),
    )

    with pytest.raises(
        RAGAnswerGenerationError,
        match="LLM provider failed during RAG answer generation.",
    ):
        service.answer(
            query="Como o cliente gera boleto?",
            documents=[
                SemanticSearchDocument(
                    source="requirement-001",
                    document_text="O cliente pode gerar boleto após renegociação.",
                )
            ],
            top_k=1,
            chunk_size=200,
            chunk_overlap=40,
        )


def test_rag_answer_service_should_raise_error_when_llm_returns_empty_answer() -> None:
    service = RAGAnswerService(
        semantic_search_service=SemanticSearchService(),
        llm_provider=FakeLLMProvider(response_content="   "),
    )

    with pytest.raises(
        RAGAnswerGenerationError,
        match="LLM provider returned an empty answer.",
    ):
        service.answer(
            query="Como o cliente gera boleto?",
            documents=[
                SemanticSearchDocument(
                    source="requirement-001",
                    document_text="O cliente pode gerar boleto após renegociação.",
                )
            ],
            top_k=1,
            chunk_size=200,
            chunk_overlap=40,
        )
