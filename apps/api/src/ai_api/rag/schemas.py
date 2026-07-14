from typing import Any
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class DocumentChunkingRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    document_text: str = Field(
        min_length=1,
        description="Raw document text to be chunked.",
    )
    source: str = Field(
        default="manual",
        min_length=1,
        description="Document source identifier.",
    )
    chunk_size: int = Field(
        default=800,
        ge=100,
        le=4000,
        description="Maximum number of characters per chunk.",
    )
    chunk_overlap: int = Field(
        default=120,
        ge=0,
        le=1000,
        description="Number of characters to overlap between chunks.",
    )

    @field_validator("document_text", "source")
    @classmethod
    def text_fields_cannot_be_blank(cls, value: str) -> str:
        cleaned_value = value.strip()

        if not cleaned_value:
            raise ValueError("value cannot be blank")

        return cleaned_value

    @model_validator(mode="after")
    def chunk_overlap_must_be_smaller_than_chunk_size(
        self,
    ) -> "DocumentChunkingRequest":
        if self.chunk_overlap >= self.chunk_size:
            raise ValueError("chunk_overlap must be smaller than chunk_size")

        return self


class DocumentChunk(BaseModel):
    model_config = ConfigDict(extra="forbid")

    chunk_id: str
    source: str
    content: str
    start_index: int
    end_index: int
    chunk_index: int
    metadata: dict[str, Any] = Field(default_factory=dict)


class DocumentChunkingResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source: str
    total_chunks: int
    chunks: list[DocumentChunk]

class DocumentIngestionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    document_text: str = Field(
        min_length=1,
        description="Raw document text to be ingested.",
    )
    source: str = Field(
        default="manual",
        min_length=1,
        description="Document source identifier.",
    )
    title: str | None = Field(
        default=None,
        description="Optional document title.",
    )
    metadata: dict[str, Any] = Field(default_factory=dict)
    chunk_size: int = Field(
        default=800,
        ge=100,
        le=4000,
        description="Maximum number of characters per chunk.",
    )
    chunk_overlap: int = Field(
        default=120,
        ge=0,
        le=1000,
        description="Number of characters to overlap between chunks.",
    )

    @field_validator("document_text", "source")
    @classmethod
    def required_text_fields_cannot_be_blank(cls, value: str) -> str:
        cleaned_value = value.strip()

        if not cleaned_value:
            raise ValueError("value cannot be blank")

        return cleaned_value

    @field_validator("title")
    @classmethod
    def optional_title_cannot_be_blank(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return value

        cleaned_value = value.strip()

        if not cleaned_value:
            raise ValueError("title cannot be blank")

        return cleaned_value

    @model_validator(mode="after")
    def chunk_overlap_must_be_smaller_than_chunk_size(
        self,
    ) -> "DocumentIngestionRequest":
        if self.chunk_overlap >= self.chunk_size:
            raise ValueError("chunk_overlap must be smaller than chunk_size")

        return self


class IngestedDocument(BaseModel):
    model_config = ConfigDict(extra="forbid")

    document_id: str
    source: str
    title: str | None = None
    character_count: int
    metadata: dict[str, Any] = Field(default_factory=dict)


class DocumentIngestionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    document: IngestedDocument
    total_chunks: int
    chunks: list[DocumentChunk]


class TextExtractionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source: str
    filename: str
    content_type: str | None = None
    character_count: int
    text: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class DocumentFileIngestionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    document: IngestedDocument
    total_chunks: int
    chunks: list[DocumentChunk]
    extraction_metadata: dict[str, Any] = Field(default_factory=dict)


class TextEmbeddingRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    texts: list[str] = Field(
        min_length=1,
        max_length=100,
        description="Texts to be embedded.",
    )

    @field_validator("texts")
    @classmethod
    def texts_cannot_contain_blank_values(
        cls,
        values: list[str],
    ) -> list[str]:
        cleaned_values = []

        for value in values:
            cleaned_value = value.strip()

            if not cleaned_value:
                raise ValueError("texts cannot contain blank values")

            cleaned_values.append(cleaned_value)

        return cleaned_values


class TextEmbedding(BaseModel):
    model_config = ConfigDict(extra="forbid")

    embedding_id: str
    text: str
    vector: list[float]
    dimensions: int
    metadata: dict[str, Any] = Field(default_factory=dict)


class TextEmbeddingResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    provider: str
    model: str
    total_embeddings: int
    embeddings: list[TextEmbedding]


class VectorRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    record_id: str = Field(min_length=1)
    text: str = Field(min_length=1)
    vector: list[float] = Field(min_length=1)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("record_id", "text")
    @classmethod
    def required_text_fields_cannot_be_blank(cls, value: str) -> str:
        cleaned_value = value.strip()

        if not cleaned_value:
            raise ValueError("value cannot be blank")

        return cleaned_value


class VectorSearchResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    record_id: str
    text: str
    score: float
    metadata: dict[str, Any] = Field(default_factory=dict)


class SemanticSearchDocument(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source: str = Field(
        min_length=1,
        description="Document source identifier.",
    )
    document_text: str = Field(
        min_length=1,
        description="Raw document text to be indexed for search.",
    )
    title: str | None = Field(
        default=None,
        description="Optional document title.",
    )
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("source", "document_text")
    @classmethod
    def required_fields_cannot_be_blank(cls, value: str) -> str:
        cleaned_value = value.strip()

        if not cleaned_value:
            raise ValueError("value cannot be blank")

        return cleaned_value

    @field_validator("title")
    @classmethod
    def optional_title_cannot_be_blank(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return value

        cleaned_value = value.strip()

        if not cleaned_value:
            raise ValueError("title cannot be blank")

        return cleaned_value


class SemanticSearchRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    query: str = Field(
        min_length=1,
        description="Search query.",
    )
    documents: list[SemanticSearchDocument] = Field(
        min_length=1,
        max_length=20,
        description="Documents to index and search.",
    )
    top_k: int = Field(
        default=3,
        ge=1,
        le=20,
        description="Maximum number of search results.",
    )
    chunk_size: int = Field(
        default=800,
        ge=100,
        le=4000,
    )
    chunk_overlap: int = Field(
        default=120,
        ge=0,
        le=1000,
    )

    @field_validator("query")
    @classmethod
    def query_cannot_be_blank(cls, value: str) -> str:
        cleaned_value = value.strip()

        if not cleaned_value:
            raise ValueError("query cannot be blank")

        return cleaned_value

    @model_validator(mode="after")
    def chunk_overlap_must_be_smaller_than_chunk_size(
        self,
    ) -> "SemanticSearchRequest":
        if self.chunk_overlap >= self.chunk_size:
            raise ValueError("chunk_overlap must be smaller than chunk_size")

        return self


class SemanticSearchResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    query: str
    total_indexed_chunks: int
    total_results: int
    results: list[VectorSearchResult]


class RAGAnswerRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    query: str = Field(
        min_length=1,
        description="Question to be answered using retrieved context.",
    )
    documents: list[SemanticSearchDocument] = Field(
        min_length=1,
        max_length=20,
        description="Documents to index and use as context.",
    )
    language: str = Field(
        default="pt-BR",
        min_length=2,
        max_length=10,
        description="Expected answer language.",
    )
    top_k: int = Field(
        default=3,
        ge=1,
        le=20,
    )
    chunk_size: int = Field(
        default=800,
        ge=100,
        le=4000,
    )
    chunk_overlap: int = Field(
        default=120,
        ge=0,
        le=1000,
    )

    @field_validator("query")
    @classmethod
    def query_cannot_be_blank(cls, value: str) -> str:
        cleaned_value = value.strip()

        if not cleaned_value:
            raise ValueError("query cannot be blank")

        return cleaned_value

    @model_validator(mode="after")
    def chunk_overlap_must_be_smaller_than_chunk_size(
        self,
    ) -> "RAGAnswerRequest":
        if self.chunk_overlap >= self.chunk_size:
            raise ValueError("chunk_overlap must be smaller than chunk_size")

        return self


class RAGAnswerResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    query: str
    answer: str
    provider: str
    model: str
    total_context_chunks: int
    context_chunks: list[VectorSearchResult]
    metadata: dict[str, Any] = Field(default_factory=dict)
