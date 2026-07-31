import { postJson } from "./httpClient";
import type {
  RAGAnswerRequest,
  RAGAnswerResponse,
  RetrievalRequest,
  RetrievalResponse,
} from "../types/rag";

export function retrieveRAGContext(
  payload: RetrievalRequest,
): Promise<RetrievalResponse> {
  return postJson<RetrievalRequest, RetrievalResponse>(
    "/api/rag/retrieve",
    payload,
  );
}

export function generateRAGAnswer(
  payload: RAGAnswerRequest,
): Promise<RAGAnswerResponse> {
  return postJson<RAGAnswerRequest, RAGAnswerResponse>(
    "/api/rag/answer",
    payload,
  );
}
