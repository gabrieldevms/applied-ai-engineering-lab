import hashlib
import math
import re
from collections.abc import Sequence
from typing import Protocol

from ai_api.rag.schemas import TextEmbedding, TextEmbeddingResponse


class EmbeddingProvider(Protocol):
    provider_name: str
    model_name: str
    dimensions: int

    def embed(self, texts: Sequence[str]) -> list[list[float]]:
        """Generate embeddings for a list of texts."""
        ...


class FakeEmbeddingProvider:
    provider_name = "fake"
    model_name = "fake-keyword-hash-embedding-v1"

    def __init__(self, dimensions: int = 32) -> None:
        if dimensions < 1:
            raise ValueError("dimensions must be greater than zero")

        self.dimensions = dimensions

    def embed(self, texts: Sequence[str]) -> list[list[float]]:
        cleaned_texts = [text.strip() for text in texts]

        if not cleaned_texts:
            raise ValueError("texts cannot be empty")

        if any(not text for text in cleaned_texts):
            raise ValueError("texts cannot contain blank values")

        return [
            self._embed_text(text)
            for text in cleaned_texts
        ]

    def _embed_text(self, text: str) -> list[float]:
        vector = [0.0 for _ in range(self.dimensions)]
        tokens = self._tokenize(text)

        if not tokens:
            tokens = [text.lower()]

        for token in tokens:
            bucket = self._bucket_for_token(token)
            vector[bucket] += 1.0

        return self._normalize(vector)

    def _tokenize(self, text: str) -> list[str]:
        return re.findall(r"\w+", text.lower())

    def _bucket_for_token(self, token: str) -> int:
        token_hash = hashlib.sha256(
            token.encode("utf-8"),
        ).hexdigest()

        return int(token_hash, 16) % self.dimensions

    def _normalize(self, vector: list[float]) -> list[float]:
        norm = math.sqrt(
            sum(value * value for value in vector)
        )

        if norm == 0:
            return vector

        return [
            round(value / norm, 6)
            for value in vector
        ]


class EmbeddingService:
    def __init__(self, embedding_provider: EmbeddingProvider) -> None:
        self.embedding_provider = embedding_provider

    def embed_texts(
        self,
        texts: Sequence[str],
    ) -> TextEmbeddingResponse:
        cleaned_texts = [text.strip() for text in texts]

        if not cleaned_texts:
            raise ValueError("texts cannot be empty")

        if any(not text for text in cleaned_texts):
            raise ValueError("texts cannot contain blank values")

        vectors = self.embedding_provider.embed(cleaned_texts)

        if len(vectors) != len(cleaned_texts):
            raise ValueError(
                "embedding provider returned unexpected number of vectors"
            )

        embeddings = [
            TextEmbedding(
                embedding_id=self._build_embedding_id(
                    text=text,
                    index=index,
                ),
                text=text,
                vector=vector,
                dimensions=len(vector),
                metadata={
                    "text_hash": self._build_text_hash(text),
                },
            )
            for index, (text, vector) in enumerate(
                zip(cleaned_texts, vectors, strict=True)
            )
        ]

        return TextEmbeddingResponse(
            provider=self.embedding_provider.provider_name,
            model=self.embedding_provider.model_name,
            total_embeddings=len(embeddings),
            embeddings=embeddings,
        )

    def _build_embedding_id(
        self,
        text: str,
        index: int,
    ) -> str:
        text_hash = self._build_text_hash(text)

        return f"embedding-{index}-{text_hash}"

    def _build_text_hash(self, text: str) -> str:
        return hashlib.sha256(
            text.encode("utf-8"),
        ).hexdigest()[:12]
