from ai_api.rag.chunking import TextChunker
from ai_api.rag.embeddings import EmbeddingService
from ai_api.rag.retrieval import RetrievalService
from ai_api.rag.schemas import (
    SemanticSearchDocument,
    SemanticSearchResponse,
)
from ai_api.rag.vector_store import InMemoryVectorStore


class SemanticSearchService:
    def __init__(
        self,
        retrieval_service: RetrievalService | None = None,
        chunker: TextChunker | None = None,
        embedding_service: EmbeddingService | None = None,
        vector_store: InMemoryVectorStore | None = None,
    ) -> None:
        self.retrieval_service = retrieval_service or RetrievalService(
            chunker=chunker,
            embedding_service=embedding_service,
            vector_store=vector_store,
        )

    def search(
        self,
        query: str,
        documents: list[SemanticSearchDocument],
        top_k: int = 3,
        chunk_size: int = 800,
        chunk_overlap: int = 120,
    ) -> SemanticSearchResponse:
        retrieval_response = self.retrieval_service.retrieve(
            query=query,
            documents=documents,
            top_k=top_k,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

        return SemanticSearchResponse(
            query=retrieval_response.query,
            total_indexed_chunks=retrieval_response.total_indexed_chunks,
            total_results=retrieval_response.total_retrieved_chunks,
            results=retrieval_response.retrieved_chunks,
        )
