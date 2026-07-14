# Applied AI Engineering Lab — Roadmap

## M0 — Foundation

Goal: prepare the repository, workflow, documentation and initial architecture.

- [x] Repository structure
- [x] GitHub Project board
- [x] Issue templates
- [x] Pull request template
- [x] Initial README
- [x] Initial roadmap
- [x] Initial architecture document
- [x] ADR template
- [x] First architecture decision record
- [x] Local development environment validation

## M1 — AI API Base

Goal: create the first production-oriented API foundation.

- [x] FastAPI project setup
- [x] Health check endpoint
- [x] Analyze text endpoint
- [x] Pydantic schemas
- [x] Unit tests with pytest
- [x] Dockerfile
- [x] GitHub Actions CI pipeline
- [x] Basic logging
- [x] Basic error handling

## M2 — LLM Engineering

Goal: integrate LLMs in a structured and reliable way.

- [x] LLM provider abstraction
- [x] Prompt templates
- [x] Structured outputs
- [x] JSON schema validation
- [x] Retry strategy
- [x] Fallback strategy
- [x] Requirement analyzer
- [x] LLM response tests
- [x] Requirement analysis API endpoint
- [x] Environment-based provider settings
- [x] OpenAI provider
- [x] Ollama provider
- [x] LLM provider diagnostics endpoints
- [x] LLM output normalization

## M3 — RAG Knowledge Assistant

Goal: build a document-based AI assistant.

- [x] Document ingestion
- [x] Text extraction
- [x] Chunking strategy
- [x] Embeddings
- [x] Vector database
- [x] Semantic search
- [x] RAG answer generation
- [x] Source citation
- [x] RAG evaluation

### Technical breakdown

- [x] Basic text chunking service
- [x] Chunking API endpoint
- [x] Document ingestion service
- [x] Document ingestion API endpoint
- [x] Text extraction service
- [x] Text extraction API endpoint
- [x] File ingestion pipeline
- [x] File ingestion API endpoint
- [x] Embedding provider abstraction
- [x] Fake embedding provider
- [x] Embedding service
- [x] Embedding API endpoint
- [x] Vector store abstraction
- [x] In-memory vector store
- [x] Cosine similarity search
- [x] SemanticSearchService
- [x] Semantic search API endpoint
- [x] RAG answer prompt
- [x] RAG answer generation service
- [x] RAG answer API endpoint
- [x] Source citation builder
- [x] RAG answer citations
- [x] RAG evaluation service
- [x] RAG evaluation API endpoint
- [x] Retrieval service
- [x] Deterministic evaluation metrics

## M4 — AI Agents

Goal: build AI agents with tools and controlled execution.

- [ ] Tool calling
- [ ] Agent service
- [ ] QA agent
- [ ] Memory and state
- [ ] Human approval flow
- [ ] Agent execution logs

## M5 — MCP QA Server

Goal: create an MCP server focused on QA and software engineering tasks.

- [ ] MCP server setup
- [ ] Tool definitions
- [ ] Requirement analysis tool
- [ ] Test case generation tool
- [ ] Playwright review tool
- [ ] Documentation search tool
- [ ] MCP client integration

## M6 — Multi-Agent QA Copilot

Goal: orchestrate multiple specialized agents.

- [ ] Orchestrator agent
- [ ] Requirement analyst agent
- [ ] QA functional agent
- [ ] Automation agent
- [ ] Reviewer agent
- [ ] Report agent
- [ ] Shared execution state
- [ ] Final report generation

## M7 — Evaluation and LLMOps

Goal: evaluate, monitor and improve AI behavior.

- [ ] Prompt tests
- [ ] Golden dataset
- [ ] RAG evaluation
- [ ] Agent evaluation
- [ ] CI evaluation pipeline
- [ ] Cost tracking
- [ ] Latency tracking
- [ ] Observability dashboard

## M8 — Cloud, Security and Portfolio

Goal: prepare the project for production-like deployment and presentation.

- [ ] Cloud deployment
- [ ] Secrets management
- [ ] Access control
- [ ] Prompt injection protection
- [ ] Audit logs
- [ ] Architecture documentation
- [ ] Portfolio README
- [ ] LinkedIn/GitHub presentation
