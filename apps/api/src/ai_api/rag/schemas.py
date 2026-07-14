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
