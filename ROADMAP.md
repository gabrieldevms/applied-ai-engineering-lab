# Applied AI Engineering Lab — Roadmap

This roadmap tracks the incremental development of a production-oriented Applied AI Engineering laboratory focused on software engineering and quality assurance.

## Current Status

**Current module:** M8 — Cloud, Security and Portfolio in progress  
**Latest completed milestone:** Security audit integration for blocked tool calls and prompt injection events  
**Next focus:** Security/governance documentation synchronization, launch demo script, final technical case study and portfolio presentation  

The short-term implementation order is:

```text
M7 — Evaluation and LLMOps
  ↓
M8 — AI Quality Command Center product experience
  ↓
Persistent observability and execution history
  ↓
Security, governance and portfolio documentation
  ↓
Cloud and production deployment direction
```

| Module                             | Status      |
| ---------------------------------- | ----------- |
| M0 — Foundation                    | Completed   |
| M1 — AI API Base                   | Completed   |
| M2 — LLM Engineering               | Completed   |
| M3 — RAG Knowledge Assistant       | Completed   |
| M4 — AI Agents                     | Completed   |
| Pre-M5 — File Ingestion Expansion  | Completed   |
| Pre-M5 — Data Analyst Agent        | Completed   |
| M5 — MCP QA Server                 | Completed   |
| M6 — Multi-Agent QA Copilot        | Completed   |
| M7 — Evaluation and LLMOps         | Completed   |
| M8 — Cloud, Security and Portfolio | In Progress |

---

## M0 — Foundation

**Status:** Completed

**Goal:** Prepare the repository, development workflow, documentation and initial architecture.

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

---

## M1 — AI API Base

**Status:** Completed

**Goal:** Create the first production-oriented API foundation.

- [x] FastAPI project setup
- [x] Health check endpoint
- [x] Analyze text endpoint
- [x] Pydantic schemas
- [x] Unit tests with pytest
- [x] Dockerfile
- [x] GitHub Actions CI pipeline
- [x] Basic logging
- [x] Basic error handling

---

## M2 — LLM Engineering

**Status:** Completed

**Goal:** Integrate large language models through structured, testable and provider-independent components.

- [x] LLM provider abstraction
- [x] Prompt templates
- [x] Structured outputs
- [x] JSON Schema validation
- [x] Retry strategy
- [x] Fallback strategy
- [x] Requirement Analyzer
- [x] LLM response tests
- [x] Requirement Analysis API endpoint
- [x] Environment-based provider settings
- [x] OpenAI provider
- [x] Ollama provider
- [x] LLM provider diagnostic endpoints
- [x] LLM output normalization

---

## M3 — RAG Knowledge Assistant

**Status:** Completed

**Goal:** Build a document-based AI assistant capable of retrieving information and generating grounded answers with citations.

### Functional milestones

- [x] Document ingestion
- [x] Text extraction
- [x] Chunking strategy
- [x] Embeddings
- [x] Vector store foundation
- [x] Semantic search
- [x] Context retrieval
- [x] RAG answer generation
- [x] Source citations
- [x] RAG evaluation

### Technical breakdown

#### Document processing

- [x] Basic text chunking service
- [x] Chunking API endpoint
- [x] Document ingestion service
- [x] Document ingestion API endpoint
- [x] Text extraction service
- [x] Text extraction API endpoint
- [x] File ingestion pipeline
- [x] File ingestion API endpoint

#### Embeddings and storage

- [x] Embedding provider abstraction
- [x] Fake embedding provider
- [x] Embedding service
- [x] Embedding API endpoint
- [x] Vector store abstraction
- [x] In-memory vector store
- [x] Cosine similarity search

#### Search and retrieval

- [x] Semantic Search Service
- [x] Semantic search API endpoint
- [x] Retrieval service

#### Answer generation and citations

- [x] RAG answer prompt
- [x] RAG answer generation service
- [x] RAG answer API endpoint
- [x] Source citation builder
- [x] RAG answer citations

#### Evaluation

- [x] RAG evaluation service
- [x] RAG evaluation API endpoint
- [x] Deterministic evaluation metrics

---

## M4 — AI Agents

**Status:** Completed

**Goal:** Build controlled AI agents capable of using tools and executing observable multi-step workflows.

### Agent foundation

- [x] Agent runtime foundation
- [x] Agent request and response schemas
- [x] Agent execution trace
- [x] Tool Registry
- [x] Tool Execution Service
- [x] Tool calling

### Agent tools

- [x] RAG Retrieval Tool
- [x] Requirement Analysis Tool
- [x] RAG Answer Tool execution handler

### Specialized agent

- [x] QA Agent

### Agent orchestration

- [x] Agent planning with LLM
- [x] Automatic tool selection
- [x] Multi-step agent execution
- [x] Memory and execution state

### Control and reliability

- [x] Human approval flow
- [x] Persistent agent execution logs
- [x] Agent safety limits
- [x] Agent evaluation

Detailed review:

- [M4 — AI Agents Module Review](docs/study-notes/04-ai-agents-module-review.md)

---

## Pre-M5 — File Ingestion Expansion

**Status:** Completed

**Goal:** Support real-world business and technical documents in RAG and agent workflows.

- [x] PDF text extraction
- [x] DOCX text extraction
- [x] CSV ingestion
- [x] Excel and spreadsheet ingestion
- [x] Structured table extraction
- [x] File metadata normalization
- [x] Extraction and ingestion tests
- [x] RAG integration validation

Detailed review:

- [File Ingestion Expansion Review](docs/study-notes/05-file-ingestion-expansion-review.md)

Current limitations:

- Scanned PDFs and OCR are not supported.
- Legacy `.doc` and `.xls` files are not supported.
- Structured table extraction does not yet infer semantic column types.

---

## Pre-M5 — Data Analyst Agent

**Status:** Completed

**Goal:** Introduce controlled data analysis and database validation workflows that can collaborate with the QA Agent.

### Data Analyst Agent foundation

- [x] Database schema representation
- [x] Table and column metadata
- [x] Natural-language-to-SQL request schema
- [x] Structured SQL generation
- [x] SQL explanation
- [x] Read-only query validation
- [x] Unsafe query blocking
- [x] Query execution abstraction
- [x] Controlled in-memory SQLite execution
- [x] Result evidence schemas
- [x] SQL generate + execute workflow
- [x] Data Analyst Agent
- [x] Data Analyst Agent evaluation
- [x] SQL workflow regression dataset

### QA Agent and Data Analyst integration

- [x] Specialized Agent Registry
- [x] Data Analyst Agent tool adapter
- [x] `data_analysis.agent.run` tool registration
- [x] QA Agent integration with the Data Analyst Agent
- [x] Optional QA Agent data validation
- [x] Automatic data validation selection
- [x] Data validation modes: `auto`, `required` and `disabled`
- [x] QA Agent evaluation with data evidence
- [x] Tool trace validation for QA/data workflows

Current limitations:

- External database connectors are not implemented.
- Database credentials management is not implemented.
- Query cost estimation is not implemented.
- Persistent SQL regression dataset files are not implemented.
- NoSQL data source abstraction is planned for future evolution.

---

## M5 — MCP QA Server

**Status:** Completed

**Goal:** Expose selected QA and software engineering capabilities through the Model Context Protocol.

Completed:

- [x] MCP server setup
- [x] MCP tool definitions
- [x] Requirement Analysis MCP tool
- [x] RAG Retrieval MCP tool
- [x] RAG Answer MCP tool
- [x] QA Agent MCP tool
- [x] Data Analyst Agent MCP tool
- [x] SQL Workflow Regression MCP tool
- [x] Multi-Agent QA Copilot MCP tool
- [x] MCP client validation
- [x] MCP tool tests
- [x] MCP security boundaries
- [x] MCP usage documentation
- [x] MCP smoke test script
- [x] FastMCP CLI wrapper for local inspection
- [x] M5 final review documentation

Detailed review:

- [M5 — MCP QA Server Review](docs/study-notes/06-mcp-qa-server-review.md)

Current limitations:

- MCP server is validated locally, not deployed.
- MCP tools do not yet include authentication or authorization.
- MCP execution currently uses in-process services.
- SQL execution remains limited to controlled in-memory SQLite table data.
- No external database connection is introduced.
- No production MCP hosting strategy has been defined yet.

---

## M6 — Multi-Agent QA Copilot

**Status:** Completed

**Goal:** Orchestrate multiple specialized agents around a shared quality-engineering workflow.

Completed:

- [x] Orchestrator Agent
- [x] Requirement Analyst Agent
- [x] Functional QA Agent
- [x] Test Automation Agent
- [x] Reviewer Agent
- [x] Report Agent
- [x] Shared execution state
- [x] Multi-agent artifacts
- [x] Multi-agent messages
- [x] Multi-agent execution trace
- [x] Inter-agent communication contracts
- [x] Contract validation
- [x] Conflict and failure handling
- [x] Failure strategies: `stop_on_failure` and `continue_on_failure`
- [x] Skipped agent handling
- [x] Shared-state conflict detection
- [x] Final QA report generation
- [x] Quality gate metadata
- [x] Requirement Analysis service integration
- [x] Data Analyst Agent integration
- [x] Data validation evidence in final reports
- [x] Multi-Agent QA Copilot API endpoint
- [x] Multi-Agent QA Copilot MCP tool
- [x] Multi-Agent QA Copilot deterministic evaluation
- [x] Multi-Agent QA Copilot evaluation API endpoint
- [x] M6 final review documentation

Detailed review:

- [M6 — Multi-Agent QA Copilot Review](docs/study-notes/07-multi-agent-qa-copilot-review.md)

Current limitations:

- Agent reasoning is still mostly deterministic.
- Only the Requirement Analyst Agent is connected to the existing LLM-backed requirement analysis service.
- Functional QA, Test Automation, Reviewer and Report agents are not yet fully LLM-backed.
- Conflict detection exists, but automatic conflict resolution is not implemented yet.
- Failure handling exists, but retry policies per agent are not implemented yet.
- Data validation requires explicit structured input.
- External database connections are not supported.
- MCP exposure exists, but production MCP hosting is not defined.
- Authentication and authorization are not implemented.

---

## M7 — Evaluation and LLMOps

**Status:** Completed

**Goal:** Continuously evaluate, observe and improve the behavior of LLM, RAG, agent and multi-agent components.

M7 introduced the evaluation, regression, telemetry and observability foundation of the project.

### Evaluation

- [x] Golden evaluation dataset
- [x] Golden evaluation dataset runner
- [x] Prompt regression tests foundation
- [x] AI evaluation report aggregation
- [x] LLM output evaluation suite
- [x] RAG regression evaluation suite
- [x] Agent regression evaluation suite
- [x] Multi-Agent QA Copilot regression evaluation
- [x] Tool-calling evaluation
- [x] LLM-as-judge evaluation prototype
- [x] CI evaluation pipeline

### Observability

- [x] Structured AI execution telemetry
- [x] Token usage tracking
- [x] Cost tracking
- [x] Latency tracking
- [x] Error and fallback tracking
- [x] Retrieval quality metrics
- [x] Agent execution metrics
- [x] Multi-agent execution metrics
- [x] Observability dashboard

### Evaluation endpoints

- [x] `GET /evals/golden-dataset`
- [x] `GET /evals/golden-dataset/validation`
- [x] `POST /evals/golden-dataset/validate`
- [x] `POST /evals/golden-dataset/run`
- [x] `GET /evals/prompt-regression/suite`
- [x] `POST /evals/prompt-regression/run`
- [x] `POST /evals/reports/aggregate`
- [x] `GET /evals/llm-output/suite`
- [x] `POST /evals/llm-output/run`
- [x] `GET /evals/rag-regression/suite`
- [x] `POST /evals/rag-regression/run`
- [x] `GET /evals/agent-regression/suite`
- [x] `POST /evals/agent-regression/run`
- [x] `GET /evals/tool-calling/suite`
- [x] `POST /evals/tool-calling/run`
- [x] `GET /evals/multi-agent-copilot-regression/suite`
- [x] `POST /evals/multi-agent-copilot-regression/run`
- [x] `GET /evals/llm-as-judge/suite`
- [x] `POST /evals/llm-as-judge/run`
- [x] `POST /evals/ci/pipeline/run`

### Telemetry and observability endpoints

- [x] `POST /evals/telemetry/events`
- [x] `GET /evals/telemetry/events`
- [x] `POST /evals/telemetry/summary`
- [x] `GET /evals/telemetry/summary`
- [x] `POST /observability/usage/records`
- [x] `GET /observability/usage/records`
- [x] `POST /observability/usage/summary`
- [x] `GET /observability/usage/summary`
- [x] `POST /observability/retrieval-quality/records`
- [x] `GET /observability/retrieval-quality/records`
- [x] `POST /observability/retrieval-quality/summary`
- [x] `GET /observability/retrieval-quality/summary`
- [x] `POST /observability/agent-execution/records`
- [x] `GET /observability/agent-execution/records`
- [x] `POST /observability/agent-execution/summary`
- [x] `GET /observability/agent-execution/summary`
- [x] `POST /observability/multi-agent-execution/records`
- [x] `GET /observability/multi-agent-execution/records`
- [x] `POST /observability/multi-agent-execution/summary`
- [x] `GET /observability/multi-agent-execution/summary`
- [x] `GET /observability/dashboard`

### CI evaluation pipeline

- [x] Deterministic AI evaluation pipeline service
- [x] AI evaluation pipeline API endpoint
- [x] AI evaluation pipeline script
- [x] GitHub Actions workflow for AI evaluation
- [x] Quality gate support
- [x] Pipeline report output

### Detailed review

- [M7 — Evaluation and LLMOps Review](docs/study-notes/08-evaluation-and-llmops-review.md)

Current limitations:

- Evaluation datasets are still small and deterministic.
- Historical telemetry is persisted locally through JSONL files for key observability records, but production database storage is not implemented yet.
- Token and cost tracking depends on caller-provided pricing data.
- Cost calculation is an estimate and not provider billing reconciliation.
- Retrieval quality metrics depend on caller-provided relevance and similarity signals.
- The Observability Dashboard is available through backend APIs and the frontend Command Center, but external monitoring integrations are not implemented yet.
- OpenTelemetry, Grafana and external monitoring integrations are not implemented yet.
- Authentication, authorization and multi-user isolation are not implemented yet.

---

## M8 — Cloud, Security and Portfolio

**Status:** In Progress

**Goal:** Prepare the project for production-like deployment, governance, frontend experience and professional presentation.

M8 transforms the backend platform foundation into a more demonstrable and portfolio-ready AI engineering product through the AI Quality Command Center, persistent local observability, execution history, security and governance controls, and portfolio documentation.

### Cloud and operations

- [ ] Cloud deployment
- [x] Environment-based local storage configuration
- [ ] Environment-specific deployment configuration
- [ ] Persistent vector storage
- [x] Persistent evaluation telemetry storage
- [ ] Persistent evaluation result and artifact storage
- [x] Persistent observability storage foundation
- [x] Persistent usage tracking storage
- [x] Persistent retrieval quality telemetry storage
- [x] Persistent agent execution telemetry storage
- [x] Persistent multi-agent execution telemetry storage
- [ ] Persistent agent state
- [ ] Deployment pipeline
- [ ] Production health checks
- [ ] Production MCP hosting direction
- [ ] Production monitoring direction

#### Completed implementation focus

- [x] Persistent Storage Foundation
- [x] Usage Tracking persistence
- [x] Evaluation Telemetry persistence
- [x] Retrieval Quality Telemetry persistence
- [x] Agent Execution Telemetry persistence
- [x] Multi-Agent Execution Telemetry persistence
- [x] Execution History backend read model
- [x] Execution History UI
- [x] Execution History run details
- [x] Console Telemetry Integration
- [x] Live Observability Dashboard behavior

#### Remaining cloud and operations work

- [ ] Cloud deployment
- [ ] Deployment pipeline
- [ ] Production health checks
- [ ] Persistent vector storage
- [ ] Persistent agent state
- [ ] Persistent evaluation result and artifact storage
- [ ] Production MCP hosting direction
- [ ] Production monitoring direction

### Security and governance

- [x] Safe provider configuration strategy
- [x] Hardened provider settings exposure
- [x] Security and governance baseline documentation
- [x] Prompt injection protection baseline documentation
- [x] Prompt injection detection baseline
- [x] Prompt injection telemetry integration
- [x] Prompt injection audit event recording
- [x] Tool authorization boundaries documentation
- [x] Tool risk classification
- [x] Tool authorization checks enforced during tool execution
- [x] Sensitive data handling policy
- [x] Audit log schema documentation
- [x] Audit log service
- [x] Blocked tool-call telemetry
- [x] Blocked tool-call audit event recording
- [ ] Secrets management
- [ ] Authentication and access control
- [ ] Multi-user isolation
- [ ] Production-grade prompt injection protection
- [ ] Audit log UI
- [ ] Production audit retention policy
- [ ] AI governance documentation

### Frontend and product experience

- [x] Frontend architecture decision
- [x] AI Quality Command Center foundation
- [x] Backend dashboard integration
- [x] Evaluation Center UI
- [x] Observability Center UI
- [x] Execution History UI
- [x] Execution History run details
- [x] QA Agent Console
- [x] Multi-Agent QA Copilot Console
- [x] RAG Console
- [x] Data Analyst Agent Console
- [x] Provider and model settings UI
- [x] Usage and cost visualization
- [x] Risk and recommendation panels
- [x] QA Agent Console telemetry integration
- [x] Multi-Agent QA Copilot Console telemetry integration
- [x] RAG Console telemetry integration
- [x] Data Analyst Console telemetry integration
- [x] Live Observability Dashboard behavior

> Current note: the first AI Quality Command Center frontend/product experience is completed for local demonstrations. The backend has persistent local JSONL storage for core observability telemetry, execution history read models, console telemetry integration and live dashboard behavior. Security and governance now include safe provider configuration, prompt injection assessment, prompt injection telemetry, tool authorization enforcement, blocked tool-call telemetry and audit log events for blocked tool calls and high-risk prompt injection assessments. Production cloud deployment, authentication, multi-user isolation, persistent vector storage, persistent agent state, production monitoring and production MCP hosting remain post-launch work.

### Documentation and portfolio

- [x] Updated architecture documentation
- [ ] Architecture diagrams
- [ ] Complete API usage examples
- [x] Portfolio-oriented README foundation
- [x] Demonstration scenarios
- [x] Launch demo script
- [x] Security and governance baseline
- [ ] GitHub project presentation
- [ ] LinkedIn project presentation
- [x] Final technical case study
- [ ] Final launch README polish

### Final M8 launch focus

- [ ] Final M8 roadmap synchronization
- [x] Launch demo script
- [x] Final technical case study
- [ ] Final portfolio README polish
- [ ] GitHub project presentation
- [ ] LinkedIn project presentation

---

## Future Extensions

Potential future extensions after M8 include:

### Post-launch Implementation Packs

After the M8 local portfolio launch, the project will continue evolving through focused implementation packs designed to support both technical growth and public portfolio updates.

#### Pack 1 — Cloud & Deployment

- [ ] Cloud deployment
- [ ] Deployment pipeline
- [ ] Production health checks

#### Pack 2 — Production Observability

- [ ] Production monitoring
- [ ] Persistent evaluation artifacts
- [ ] More robust dashboards and scorecards

#### Pack 3 — Production Agent State

- [ ] Persistent vector storage
- [ ] Persistent agent state
- [ ] Session resume and memory persistence

#### Pack 4 — Security Enterprise Layer

- [ ] Authentication
- [ ] Access control
- [ ] Multi-user isolation
- [ ] Secrets management

#### Pack 5 — MCP Production Layer

- [ ] Production MCP hosting
- [ ] External tool/server strategy

#### Pack 6 — Data Integrations

- [ ] External SQL connectors
- [ ] NoSQL connectors
- [ ] Credential handling
- [ ] Read-only governance

#### Pack 7 — Multi-provider AI Evaluation

- [ ] Additional LLM providers
- [ ] Anthropic Claude provider
- [ ] Google Gemini provider
- [ ] Provider comparison evaluation
- [ ] Latency, cost and quality benchmarks

### Additional LLM Providers

- [ ] Anthropic Claude provider
- [ ] Google Gemini provider
- [ ] Provider comparison evaluation
- [ ] Multi-provider benchmark datasets
- [ ] Provider-specific latency, cost and quality comparison

### Data Analyst Agent Evolution

- [ ] External SQL database connectors
- [ ] Read-only database credential handling
- [ ] Query cost estimation
- [ ] Persistent SQL regression datasets
- [ ] NoSQL data source abstraction
- [ ] Natural-language analytics workflows
- [ ] Data validation dashboards

### AI Quality Engineering Evolution

- [ ] Quality evaluation for AI agents
- [ ] Quality evaluation for AI systems
- [ ] Agent reliability scoring
- [ ] Prompt quality scoring
- [ ] RAG quality dashboards
- [ ] Production LLMOps scorecards

---

## Target Project Evolution

```text
Structured AI API
        ↓
Reliable LLM integration
        ↓
Document-based RAG assistant
        ↓
Tool-using QA Agent
        ↓
Controlled Data Analyst Agent
        ↓
QA and Data Agent integration
        ↓
MCP QA Server
        ↓
Multi-Agent QA Copilot
        ↓
Evaluation and LLMOps
        ↓
AI Quality Command Center
        ↓
Persistent observability and execution history
        ↓
Security, governance and portfolio documentation
        ↓
Cloud and production deployment direction
```

Each module builds on the contracts, tests and architectural decisions introduced by the previous modules.
