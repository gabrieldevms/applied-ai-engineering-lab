import type { JsonValue } from "./qaAgent";

export type SemanticSearchDocument = {
  source: string;
  document_text: string;
  title?: string | null;
  metadata?: Record<string, JsonValue>;
};

export type VectorSearchResult = {
  record_id: string;
  text: string;
  score: number;
  metadata: Record<string, JsonValue>;
};

export type SourceCitation = {
  citation_id: string;
  source: string;
  title?: string | null;
  chunk_id: string;
  excerpt: string;
  score: number;
  metadata: Record<string, JsonValue>;
};

export type RetrievalRequest = {
  query: string;
  documents: SemanticSearchDocument[];
  top_k?: number;
  chunk_size?: number;
  chunk_overlap?: number;
};

export type RetrievalResponse = {
  query: string;
  total_indexed_chunks: number;
  total_retrieved_chunks: number;
  retrieved_chunks: VectorSearchResult[];
  metadata: Record<string, JsonValue>;
};

export type RAGAnswerRequest = {
  query: string;
  documents: SemanticSearchDocument[];
  language?: string;
  top_k?: number;
  chunk_size?: number;
  chunk_overlap?: number;
};

export type RAGAnswerResponse = {
  query: string;
  answer: string;
  provider: string;
  model: string;
  total_context_chunks: number;
  context_chunks: VectorSearchResult[];
  citations: SourceCitation[];
  metadata: Record<string, JsonValue>;
};
