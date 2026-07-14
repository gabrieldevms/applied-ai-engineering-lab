from collections.abc import Sequence

from ai_api.llm import LLMMessage
from ai_api.rag.schemas import VectorSearchResult


RAG_ANSWER_SYSTEM_PROMPT = """
Você é um assistente de IA especializado em responder perguntas com base em contexto recuperado.

Regras:
- Responda apenas com base nos contextos fornecidos.
- Não invente informações.
- Se o contexto não for suficiente, diga claramente que não há informação suficiente.
- Seja objetivo, claro e útil.
- Responda no idioma solicitado pelo usuário.
""".strip()


def build_rag_answer_messages(
    query: str,
    context_chunks: Sequence[VectorSearchResult],
    language: str = "pt-BR",
) -> list[LLMMessage]:
    cleaned_query = query.strip()

    if not cleaned_query:
        raise ValueError("query cannot be blank")

    if not context_chunks:
        raise ValueError("context_chunks cannot be empty")

    formatted_context = "\n\n".join(
        _format_context_chunk(index=index, chunk=chunk)
        for index, chunk in enumerate(context_chunks, start=1)
    )

    user_prompt = f"""
Idioma da resposta: {language}

Pergunta:
{cleaned_query}

Contextos recuperados:
{formatted_context}

Responda à pergunta usando apenas os contextos recuperados.
""".strip()

    return [
        LLMMessage(role="system", content=RAG_ANSWER_SYSTEM_PROMPT),
        LLMMessage(role="user", content=user_prompt),
    ]


def _format_context_chunk(
    index: int,
    chunk: VectorSearchResult,
) -> str:
    source = chunk.metadata.get("source", "unknown")
    title = chunk.metadata.get("title", "")
    chunk_id = chunk.metadata.get("chunk_id", chunk.record_id)

    return f"""
[Contexto {index}]
Fonte: {source}
Título: {title}
Chunk ID: {chunk_id}
Score: {chunk.score}

Conteúdo:
{chunk.text}
""".strip()
