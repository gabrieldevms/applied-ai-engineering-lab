# Applied AI Engineering Lab — Roadmap

This roadmap tracks the incremental development of a production-oriented Applied AI Engineering laboratory focused on software engineering and quality assurance.

## Current Status

**Current module:** Pre-M5 Applied AI Extensions  
**Latest completed milestone:** SQL workflow regression dataset  
**Next milestone:** M5 — MCP QA Server  

The short-term implementation order is:

```text
M5 — MCP QA Server
  ↓
M6 — Multi-Agent QA Copilot
  ↓
M7 — Evaluation and LLMOps
```

| Module                             | Status      |
| ---------------------------------- | ----------- |
| M0 — Foundation                    | Completed   |
| M1 — AI API Base                   | Completed   |
| M2 — LLM Engineering               | Completed   |
| M3 — RAG Knowledge Assistant       | Completed   |
| M4 — AI Agents                     | Completed   |
| M5 — MCP QA Server                 | Next        |
| M6 — Multi-Agent QA Copilot        | Planned     |
| M7 — Evaluation and LLMOps         | Planned     |
| M8 — Cloud, Security and Portfolio | Planned     |

---

## M0 — Foundation

**Goal:** Prepare the repository, development workflow, documentation and initial architecture.

* [x] Repository structure
* [x] GitHub Project board
* [x] Issue templates
* [x] Pull request template
* [x] Initial README
* [x] Initial roadmap
* [x] Initial architecture document
* [x] ADR template
* [x] First architecture decision record
* [x] Local development environment validation

---

## M1 — AI API Base

**Goal:** Create the first production-oriented API foundation.

* [x] FastAPI project setup
* [x] Health check endpoint
* [x] Analyze text endpoint
* [x] Pydantic schemas
* [x] Unit tests with pytest
* [x] Dockerfile
* [x] GitHub Actions CI pipeline
* [x] Basic logging
* [x] Basic error handling

---

## M2 — LLM Engineering

**Goal:** Integrate large language models through structured, testable and provider-independent components.

* [x] LLM provider abstraction
* [x] Prompt templates
* [x] Structured outputs
* [x] JSON Schema validation
* [x] Retry strategy
* [x] Fallback strategy
* [x] Requirement Analyzer
* [x] LLM response tests
* [x] Requirement Analysis API endpoint
* [x] Environment-based provider settings
* [x] OpenAI provider
* [x] Ollama provider
* [x] LLM provider diagnostic endpoints
* [x] LLM output normalization

---

## M3 — RAG Knowledge Assistant

**Goal:** Build a document-based AI assistant capable of retrieving information and generating grounded answers with citations.

### Functional milestones

* [x] Document ingestion
* [x] Text extraction
* [x] Chunking strategy
* [x] Embeddings
* [x] Vector store foundation
* [x] Semantic search
* [x] Context retrieval
* [x] RAG answer generation
* [x] Source citations
* [x] RAG evaluation

### Technical breakdown

#### Document processing

* [x] Basic text chunking service
* [x] Chunking API endpoint
* [x] Document ingestion service
* [x] Document ingestion API endpoint
* [x] Text extraction service
* [x] Text extraction API endpoint
* [x] File ingestion pipeline
* [x] File ingestion API endpoint

#### Embeddings and storage

* [x] Embedding provider abstraction
* [x] Fake embedding provider
* [x] Embedding service
* [x] Embedding API endpoint
* [x] Vector store abstraction
* [x] In-memory vector store
* [x] Cosine similarity search

#### Search and retrieval

* [x] Semantic Search Service
* [x] Semantic search API endpoint
* [x] Retrieval service

#### Answer generation and citations

* [x] RAG answer prompt
* [x] RAG answer generation service
* [x] RAG answer API endpoint
* [x] Source citation builder
* [x] RAG answer citations

#### Evaluation

* [x] RAG evaluation service
* [x] RAG evaluation API endpoint
* [x] Deterministic evaluation metrics

---

## M4 — AI Agents

**Goal:** Build controlled AI agents capable of using tools and executing observable multi-step workflows.

### Agent foundation

* [x] Agent runtime foundation
* [x] Agent request and response schemas
* [x] Agent execution trace
* [x] Tool Registry
* [x] Tool Execution Service
* [x] Tool calling

### Agent tools

* [x] RAG Retrieval Tool
* [x] Requirement Analysis Tool
* [x] RAG Answer Tool execution handler

### Specialized agent

* [x] QA Agent

### Agent orchestration

* [x] Agent planning with LLM
* [x] Automatic tool selection
* [x] Multi-step agent execution
* [x] Memory and execution state

### Control and reliability

* [x] Human approval flow
* [x] Persistent agent execution logs
* [x] Agent safety limits
* [x] Agent evaluation

Detailed review:

- [M4 — AI Agents Module Review](docs/study-notes/04-ai-agents-module-review.md)

## Pre-M5 Applied AI Extensions

These extensions improve the practical usefulness of the platform before MCP integration.

### File ingestion expansion

Goal: support real-world business and technical documents in RAG and agent workflows.

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

### Data Analyst Agent foundation

Goal: introduce controlled data analysis and database validation workflows that can collaborate with the QA Agent.

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

Goal: allow QA workflows to use controlled data validation when requirements depend on database-like evidence.

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

- External database connectors
- Database credentials management
- Query cost estimation
- Persistent SQL regression dataset files
- NoSQL data source abstraction
- LLM-based tool selection
- LLM-as-judge evaluation

---

## M5 — MCP QA Server

Status: Completed

Goal: expose selected QA and software engineering capabilities through the Model Context Protocol.

Completed:

- [x] MCP server setup
- [x] MCP tool definitions
- [x] Requirement Analysis MCP tool
- [x] RAG Retrieval MCP tool
- [x] RAG Answer MCP tool
- [x] QA Agent MCP tool
- [x] Data Analyst Agent MCP tool
- [x] SQL Workflow Regression MCP tool
- [x] MCP client validation
- [x] MCP tool tests
- [x] MCP security boundaries
- [x] MCP usage documentation
- [x] MCP smoke test script
- [x] FastMCP CLI wrapper for local inspection
- [x] M5 final review documentation

Current limitations:

- MCP server is validated locally, not deployed.
- MCP tools do not yet include authentication or authorization.
- MCP execution currently uses in-process services.
- SQL execution remains limited to controlled in-memory SQLite table data.
- No external database connection is introduced.
- No production MCP hosting strategy has been defined yet.

---

## M6 — Multi-Agent QA Copilot

Status: Completed

Goal: orchestrate multiple specialized agents around a shared quality-engineering workflow.

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

Current limitations:

- Agent reasoning is still mostly deterministic.
- Only the Requirement Analyst Agent is connected to the existing LLM-backed requirement analysis service.
- Functional QA, Test Automation, Reviewer and Report agents are not yet LLM-backed.
- Conflict detection exists, but automatic conflict resolution is not implemented yet.
- Failure handling exists, but retry policies per agent are not implemented yet.
- Data validation requires explicit structured input.
- External database connections are not supported.
- MCP exposure exists, but production MCP hosting is not defined.
- Evaluation is deterministic and does not include LLM-as-judge yet.
- Authentication and authorization are not implemented.

---

## M7 — Evaluation and LLMOps

Status: Planned

Goal: continuously evaluate, observe and improve the behavior of LLM, RAG and agent components.

### Evaluation

- [ ] Prompt regression tests
- [ ] Golden evaluation dataset
- [ ] LLM output evaluation suite
- [ ] RAG regression evaluation suite
- [ ] Agent regression evaluation suite
- [ ] Multi-Agent QA Copilot regression evaluation
- [ ] Tool-calling evaluation
- [ ] LLM-as-judge evaluation prototype
- [ ] CI evaluation pipeline

### Observability

- [ ] Structured AI execution telemetry
- [ ] Token usage tracking
- [ ] Cost tracking
- [ ] Latency tracking
- [ ] Error and fallback tracking
- [ ] Retrieval quality metrics
- [ ] Agent execution metrics
- [ ] Multi-agent execution metrics
- [ ] Observability dashboard

---

## M8 — Cloud, Security and Portfolio

**Goal:** Prepare the project for production-like deployment, governance and professional presentation.

### Cloud and operations

* [ ] Cloud deployment
* [ ] Environment-specific configuration
* [ ] Persistent vector storage
* [ ] Persistent agent state
* [ ] Deployment pipeline
* [ ] Production health checks

### Security and governance

* [ ] Secrets management
* [ ] Authentication and access control
* [ ] Prompt injection protection
* [ ] Tool authorization boundaries
* [ ] Sensitive data handling
* [ ] Audit logs
* [ ] AI governance documentation

### Documentation and portfolio

* [ ] Updated architecture documentation
* [ ] Architecture diagrams
* [ ] Complete API usage examples
* [ ] Portfolio-oriented README
* [ ] Demonstration scenarios
* [ ] GitHub project presentation
* [ ] LinkedIn project presentation
* [ ] Final technical case study

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
Cloud-ready AI engineering portfolio
```

Each module builds on the contracts, tests and architectural decisions introduced by the previous modules.
