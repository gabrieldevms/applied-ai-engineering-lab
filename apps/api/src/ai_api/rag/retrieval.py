from ai_api.rag.chunking import TextChunker
from ai_api.rag.embeddings import EmbeddingService, FakeEmbeddingProvider
from ai_api.rag.schemas import (
    RetrievalResponse,
    SemanticSearchDocument,
    VectorRecord,
)
from ai_api.rag.vector_store import InMemoryVectorStore


class RetrievalService:
    def __init__(
        self,
        chunker: TextChunker | None = None,
        embedding_service: EmbeddingService | None = None,
        vector_store: InMemoryVectorStore | None = None,
    ) -> None:
        self.chunker = chunker or TextChunker()
        self.embedding_service = embedding_service or EmbeddingService(
            embedding_provider=FakeEmbeddingProvider(),
        )
        self.vector_store = vector_store or InMemoryVectorStore()

    def retrieve(
        self,
        query: str,
        documents: list[SemanticSearchDocument],
        top_k: int = 3,
        chunk_size: int = 800,
        chunk_overlap: int = 120,
    ) -> RetrievalResponse:
        cleaned_query = query.strip()

        if not cleaned_query:
            raise ValueError("query cannot be blank")

        if not documents:
            raise ValueError("documents cannot be empty")

        self.vector_store.clear()

        vector_records = self._build_vector_records(
            documents=documents,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

        self.vector_store.upsert(vector_records)

        query_embedding = self.embedding_service.embed_texts(
            [cleaned_query],
        ).embeddings[0]

        retrieved_chunks = self.vector_store.search(
            query_vector=query_embedding.vector,
            top_k=top_k,
        )

        return RetrievalResponse(
            query=cleaned_query,
            total_indexed_chunks=len(vector_records),
            total_retrieved_chunks=len(retrieved_chunks),
            retrieved_chunks=retrieved_chunks,
            metadata={
                "top_k": top_k,
                "chunk_size": chunk_size,
                "chunk_overlap": chunk_overlap,
            },
        )

    def _build_vector_records(
        self,
        documents: list[SemanticSearchDocument],
        chunk_size: int,
        chunk_overlap: int,
    ) -> list[VectorRecord]:
        vector_records: list[VectorRecord] = []

        for document in documents:
            chunking_response = self.chunker.chunk(
                document_text=document.document_text,
                source=document.source,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
            )

            chunk_texts = [
                chunk.content
                for chunk in chunking_response.chunks
            ]

            embedding_response = self.embedding_service.embed_texts(
                chunk_texts,
            )

            for chunk, embedding in zip(
                chunking_response.chunks,
                embedding_response.embeddings,
                strict=True,
            ):
                vector_records.append(
                    VectorRecord(
                        record_id=chunk.chunk_id,
                        text=chunk.content,
                        vector=embedding.vector,
                        metadata={
                            **document.metadata,
                            **chunk.metadata,
                            "source": document.source,
                            "title": document.title or "",
                            "chunk_id": chunk.chunk_id,
                            "chunk_index": str(chunk.chunk_index),
                            "start_index": str(chunk.start_index),
                            "end_index": str(chunk.end_index),
                        },
                    )
                )

        return vector_records
