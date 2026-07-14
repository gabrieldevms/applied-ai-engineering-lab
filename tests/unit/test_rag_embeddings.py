import pytest

from ai_api.rag import EmbeddingService, FakeEmbeddingProvider


def test_fake_embedding_provider_should_generate_embedding_vector() -> None:
    provider = FakeEmbeddingProvider(dimensions=16)

    vectors = provider.embed(
        ["Como cliente, quero renegociar minha dívida."]
    )

    assert len(vectors) == 1
    assert len(vectors[0]) == 16
    assert all(isinstance(value, float) for value in vectors[0])


def test_fake_embedding_provider_should_be_deterministic() -> None:
    provider = FakeEmbeddingProvider(dimensions=16)

    first_vector = provider.embed(["Texto do documento."])[0]
    second_vector = provider.embed(["Texto do documento."])[0]

    assert first_vector == second_vector


def test_fake_embedding_provider_should_generate_different_vectors_for_different_texts() -> None:
    provider = FakeEmbeddingProvider(dimensions=16)

    first_vector = provider.embed(["Texto sobre boleto."])[0]
    second_vector = provider.embed(["Texto sobre login."])[0]

    assert first_vector != second_vector


def test_fake_embedding_provider_should_reject_blank_text() -> None:
    provider = FakeEmbeddingProvider(dimensions=16)

    with pytest.raises(
        ValueError,
        match="texts cannot contain blank values",
    ):
        provider.embed(["   "])


def test_embedding_service_should_return_structured_response() -> None:
    provider = FakeEmbeddingProvider(dimensions=16)
    service = EmbeddingService(embedding_provider=provider)

    response = service.embed_texts(
        [
            "Como cliente, quero renegociar minha dívida.",
            "Como cliente, quero consultar meus boletos.",
        ]
    )

    assert response.provider == "fake"
    assert response.model == "fake-keyword-hash-embedding-v1"
    assert response.total_embeddings == 2
    assert len(response.embeddings) == 2
    assert response.embeddings[0].dimensions == 16
    assert response.embeddings[0].embedding_id.startswith("embedding-0-")
    assert response.embeddings[1].embedding_id.startswith("embedding-1-")


def test_embedding_service_should_reject_empty_text_list() -> None:
    provider = FakeEmbeddingProvider(dimensions=16)
    service = EmbeddingService(embedding_provider=provider)

    with pytest.raises(
        ValueError,
        match="texts cannot be empty",
    ):
        service.embed_texts([])
