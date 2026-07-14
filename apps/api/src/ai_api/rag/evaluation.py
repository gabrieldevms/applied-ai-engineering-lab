import re
from collections.abc import Sequence

from ai_api.rag.schemas import (
    RAGEvaluationMetric,
    RAGEvaluationResponse,
    SourceCitation,
    VectorSearchResult,
)


STOPWORDS = {
    "a",
    "ao",
    "aos",
    "as",
    "com",
    "como",
    "da",
    "das",
    "de",
    "do",
    "dos",
    "e",
    "em",
    "o",
    "os",
    "para",
    "por",
    "que",
    "um",
    "uma",
}


class RAGEvaluationService:
    def evaluate(
        self,
        query: str,
        answer: str,
        context_chunks: Sequence[VectorSearchResult],
        citations: Sequence[SourceCitation] | None = None,
        minimum_overall_score: float = 0.6,
    ) -> RAGEvaluationResponse:
        cleaned_query = query.strip()
        cleaned_answer = answer.strip()
        citation_list = list(citations or [])

        if not cleaned_query:
            raise ValueError("query cannot be blank")

        if not cleaned_answer:
            raise ValueError("answer cannot be blank")

        if not context_chunks:
            raise ValueError("context_chunks cannot be empty")

        metrics = [
            self._evaluate_context_relevance(context_chunks),
            self._evaluate_answer_groundedness(
                answer=cleaned_answer,
                context_chunks=context_chunks,
            ),
            self._evaluate_query_alignment(
                query=cleaned_query,
                answer=cleaned_answer,
            ),
            self._evaluate_citation_coverage(
                answer=cleaned_answer,
                context_chunks=context_chunks,
                citations=citation_list,
            ),
        ]

        overall_score = round(
            sum(metric.score for metric in metrics) / len(metrics),
            6,
        )

        issues = [
            metric.details
            for metric in metrics
            if not metric.passed
        ]

        return RAGEvaluationResponse(
            overall_score=overall_score,
            passed=overall_score >= minimum_overall_score
            and all(metric.passed for metric in metrics),
            metrics=metrics,
            issues=issues,
            metadata={
                "minimum_overall_score": minimum_overall_score,
                "total_context_chunks": len(context_chunks),
                "total_citations": len(citation_list),
            },
        )

    def _evaluate_context_relevance(
        self,
        context_chunks: Sequence[VectorSearchResult],
    ) -> RAGEvaluationMetric:
        average_score = sum(
            self._clamp_score(chunk.score)
            for chunk in context_chunks
        ) / len(context_chunks)

        score = round(average_score, 6)

        return RAGEvaluationMetric(
            name="context_relevance",
            score=score,
            passed=score >= 0.2,
            details=(
                "Retrieved context has acceptable relevance."
                if score >= 0.2
                else "Retrieved context relevance is too low."
            ),
        )

    def _evaluate_answer_groundedness(
        self,
        answer: str,
        context_chunks: Sequence[VectorSearchResult],
    ) -> RAGEvaluationMetric:
        answer_tokens = self._tokenize(answer)
        context_tokens = self._tokenize(
            " ".join(chunk.text for chunk in context_chunks)
        )

        if not answer_tokens:
            score = 0.0
        else:
            overlap = answer_tokens.intersection(context_tokens)
            score = len(overlap) / len(answer_tokens)

        score = round(score, 6)

        return RAGEvaluationMetric(
            name="answer_groundedness",
            score=score,
            passed=score >= 0.3,
            details=(
                "Answer appears grounded in retrieved context."
                if score >= 0.3
                else "Answer has low lexical overlap with retrieved context."
            ),
        )

    def _evaluate_query_alignment(
        self,
        query: str,
        answer: str,
    ) -> RAGEvaluationMetric:
        query_tokens = self._tokenize(query)
        answer_tokens = self._tokenize(answer)

        if not query_tokens:
            score = 0.0
        else:
            overlap = query_tokens.intersection(answer_tokens)
            score = len(overlap) / len(query_tokens)

        score = round(score, 6)

        return RAGEvaluationMetric(
            name="query_alignment",
            score=score,
            passed=score >= 0.2,
            details=(
                "Answer appears aligned with the query."
                if score >= 0.2
                else "Answer has low alignment with the query."
            ),
        )

    def _evaluate_citation_coverage(
        self,
        answer: str,
        context_chunks: Sequence[VectorSearchResult],
        citations: Sequence[SourceCitation],
    ) -> RAGEvaluationMetric:
        if not citations:
            return RAGEvaluationMetric(
                name="citation_coverage",
                score=0.0,
                passed=False,
                details="No citations were provided.",
            )

        context_chunk_ids = {
            chunk.metadata.get("chunk_id", chunk.record_id)
            for chunk in context_chunks
        }
        cited_chunk_ids = {
            citation.chunk_id
            for citation in citations
        }

        matched_citations = cited_chunk_ids.intersection(context_chunk_ids)
        chunk_coverage = len(matched_citations) / len(context_chunk_ids)

        citation_references_in_answer = sum(
            1
            for citation in citations
            if f"[{citation.citation_id}]" in answer
        )
        answer_reference_score = citation_references_in_answer / len(citations)

        score = round(
            (chunk_coverage * 0.7) + (answer_reference_score * 0.3),
            6,
        )

        return RAGEvaluationMetric(
            name="citation_coverage",
            score=score,
            passed=score >= 0.5,
            details=(
                "Citations cover retrieved context adequately."
                if score >= 0.5
                else "Citation coverage is incomplete or missing from answer."
            ),
        )

    def _tokenize(self, text: str) -> set[str]:
        tokens = re.findall(r"\w+", text.lower())

        return {
            token
            for token in tokens
            if token not in STOPWORDS and len(token) > 2
        }

    def _clamp_score(self, score: float) -> float:
        return max(0.0, min(score, 1.0))
