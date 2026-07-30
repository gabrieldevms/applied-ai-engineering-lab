# Applied AI Engineering Lab

A practical and production-oriented laboratory for designing, building, testing and evolving reliable AI systems for software engineering and quality assurance.

The project starts with a structured AI API and incrementally evolves toward RAG applications, tool-using agents, MCP servers, multi-agent workflows, evaluation pipelines, observability and production-like deployment.

## Project Status

**Current module:** M6 — Multi-Agent QA Copilot completed
**Latest completed milestone:** Multi-Agent QA Copilot with API, MCP exposure and deterministic evaluation
**Next milestone:** M7 — Evaluation and LLMOps

The project currently includes:

- FastAPI AI service foundation
- LLM provider abstraction with Fake, OpenAI and Ollama providers
- Structured requirement analysis
- RAG Knowledge Assistant
- AI Agent runtime foundation
- QA Agent
- Data Analyst Agent
- QA Agent and Data Analyst Agent integration
- File ingestion expansion for text, PDF, DOCX, CSV and Excel files
- Structured table extraction
- Safe read-only SQL generation and execution
- SQL workflow regression suite
- MCP QA Server exposing project capabilities through MCP
- Multi-Agent QA Copilot
- Multi-agent communication contracts
- Multi-agent failure and conflict handling
- Multi-agent final QA report generation
- Multi-agent data validation evidence
- Multi-agent deterministic evaluation

For detailed reviews, see:

- [M4 — AI Agents Module Review](docs/study-notes/04-ai-agents-module-review.md)
- [File Ingestion Expansion Review](docs/study-notes/05-file-ingestion-expansion-review.md)
- [Multi Agent QA Copilot](docs/study-notes/07-multi-agent-qa-copilot-review.md)

| Module                             | Status         | Scope                                                                              |
| ---------------------------------- | -------------- | ---------------------------------------------------------------------------------- |
| M0 — Foundation                    | ✅ Completed    | Repository, workflow, documentation and architecture foundation                    |
| M1 — AI API Base                   | ✅ Completed    | FastAPI, schemas, tests, Docker, CI, logging and error handling                    |
| M2 — LLM Engineering               | ✅ Completed    | Providers, prompts, structured outputs, retries, fallback and requirement analysis |
| M3 — RAG Knowledge Assistant       | ✅ Completed    | Ingestion, chunking, embeddings, retrieval, answers, citations and evaluation      |
| M4 — AI Agents                     | ✅ Completed    | Runtime, tools, execution, planning, QA Agent and safety controls                  |
| Pre-M5 — File Ingestion Expansion  | ✅ Completed    | Multi-format text extraction and structured table extraction                       |
| Pre-M5 — Data Analyst Agent        | ✅ Completed    | SQL generation, read-only validation, controlled execution and evaluation          |
| M5 — MCP QA Server                 | ✅ Completed        | MCP tools focused on QA and software engineering                                   |
| M6 — Multi-Agent QA Copilot        | ✅ Completed       | Specialized QA agents and orchestration                                            |
| M7 — Evaluation and LLMOps         | ⏳ Next     | Evaluation pipelines, observability, cost and latency tracking                     |
| M8 — Cloud, Security and Portfolio | ⏳ Planned      | Deployment, security, governance and portfolio presentation                        |

See the complete [project roadmap](ROADMAP.md).

## Why This Project Exists

Many AI examples stop at a prompt, notebook or direct model call.

This laboratory explores the engineering practices required to build AI systems that are:

* modular and maintainable;
* provider-independent;
* validated with structured schemas;
* observable and testable;
* grounded in retrieved information;
* capable of using controlled tools;
* designed with explicit execution boundaries;
* prepared for evaluation and production-like operation.

The project also connects Applied AI Engineering with practical QA use cases such as:

* software requirement analysis;
* acceptance criteria identification;
* risk discovery;
* test scenario generation;
* documentation retrieval;
* test automation support;
* controlled QA agent workflows.

## Current Capabilities

### LLM Engineering

The API provides a reusable LLM integration layer with:

* provider abstraction;
* Fake, OpenAI and Ollama providers;
* environment-based provider selection;
* prompt builders;
* structured Pydantic outputs;
* JSON extraction and normalization;
* retry strategies;
* fallback providers;
* provider diagnostics;
* provider-level error handling.

### Requirement Analysis

Software requirements can be analyzed through a structured quality-oriented workflow.

The analysis may include:

* requirement summary;
* business rules;
* acceptance criteria;
* risks;
* open questions;
* positive test scenarios;
* negative test scenarios;
* edge cases;
* automation opportunities.

### RAG Knowledge Assistant

The RAG foundation currently supports:

* raw text ingestion;
* text file ingestion;
* `.txt`, `.md`, `.markdown`, `.pdf`, `.docx`, `.csv` and `.xlsx` text extraction;
* configurable document chunking;
* stable document identifiers;
* chunk and source metadata;
* deterministic embeddings;
* in-memory vector storage;
* cosine similarity search;
* semantic search;
* reusable context retrieval;
* LLM-based answer generation;
* source citations;
* deterministic RAG evaluation.
* structured table extraction for CSV, XLSX and DOCX files;
* dedicated text and table extraction endpoints.

### File Ingestion

- extensible file extractor registry;
- normalized text extraction for TXT and Markdown;
- PDF text extraction;
- DOCX paragraph and table text extraction;
- CSV text extraction with delimiter detection;
- Excel text extraction by sheet;
- structured table extraction for CSV, XLSX and DOCX tables;
- dedicated `/rag/extract-text` and `/rag/extract-tables` extraction paths.

### AI Agent Foundation

- controlled agent runtime with explicit execution steps;
- agent request, response and execution trace schemas;
- schema-driven Tool Registry;
- controlled Tool Execution Service;
- direct and runtime-based tool calling;
- specialized QA Agent;
- LLM-based agent planning;
- automatic tool selection;
- multi-step workflow execution;
- in-memory execution state snapshots;
- policy-based human approval flow;
- agent safety limits and violation reporting;
- persistent JSONL execution logs;
- deterministic agent execution evaluation;
- evaluation metrics for traceability, completion, safety, approval control and objective alignment.

### Agent Tools

The Tool Registry currently describes:

| Tool                      | Registered | Executable | Purpose                                           |
| ------------------------- | ---------: | ---------: | ------------------------------------------------- |
| `rag.retrieve`            |          ✅ |          ✅ | Retrieve relevant document chunks                 |
| `requirements.analyze`    |          ✅ |          ✅ | Analyze software requirements                     |
| `rag.answer`              |          ✅ |          ✅ | Generate a grounded answer from retrieved context |
| `data_analysis.agent.run` |          ✅ |          ✅ | Run the Data Analyst Agent as a specialized tool  |

Tool execution is centralized in the `ToolExecutionService`. The service validates the requested tool against the registry and only allows tools with explicit execution handlers.

The `data_analysis.agent.run` tool allows the generic Agent Runtime and the QA Agent to execute controlled data analysis workflows through the Data Analyst Agent.

### QA Agent

The project includes a specialized QA Agent that coordinates existing tools around software quality workflows.

The QA Agent currently supports:

* software requirement analysis;
* optional supporting knowledge documents;
* RAG retrieval when documents are provided;
* requirement analysis through the agent tool execution layer;
* optional data validation through the Data Analyst Agent;
* automatic data validation selection;
* data validation modes: `auto`, `required` and `disabled`;
* structured QA-oriented output;
* data validation evidence when applicable;
* full execution trace;
* deterministic QA Agent evaluation.

### Data Analyst Agent

The project includes a specialized Data Analyst Agent for controlled data validation workflows.

The Data Analyst Agent currently supports:

* database schema representation;
* table and column metadata;
* natural-language SQL generation;
* structured SQL parsing;
* read-only SQL safety validation;
* unsafe SQL blocking;
* controlled in-memory SQLite execution;
* SQL workflow generation and execution;
* query result evidence;
* deterministic Data Analyst Agent evaluation;
* execution through the generic Agent Runtime as `data_analysis.agent.run`;
* SQL workflow regression scenarios.

### MCP QA Server

The project includes a FastMCP-based MCP server that exposes selected capabilities through Model Context Protocol tools.

Available MCP tools:

- `get_project_status`
- `list_agent_tools`
- `list_specialized_agents`
- `analyze_requirement`
- `retrieve_rag_context`
- `answer_with_rag`
- `run_qa_agent`
- `run_data_analyst_agent`
- `run_sql_regression_suite`

Local MCP smoke test:

```powershell
$env:PYTHONPATH = "apps/api/src"
uv run python scripts/mcp_client_smoke.py
```

### Multi-Agent QA Copilot

The project includes a Multi-Agent QA Copilot that orchestrates specialized QA agents around a shared quality-engineering workflow.

Current agents:

- `orchestrator_agent`
- `requirement_analyst_agent`
- `functional_qa_agent`
- `test_automation_agent`
- `reviewer_agent`
- `report_agent`

Current capabilities:

- shared execution state
- artifacts and messages
- execution trace
- communication contracts
- contract validation
- failure handling
- conflict detection
- final QA report generation
- quality gate metadata
- Requirement Analysis service integration
- Data Analyst Agent integration
- data validation evidence
- deterministic evaluation
- API execution endpoint
- API evaluation endpoint
- MCP tool exposure

API endpoints:

- `POST /multi-agent/qa-copilot/run`
- `POST /multi-agent/qa-copilot/evaluate`

MCP tool:

- `run_multi_agent_qa_copilot`

## Architecture

```mermaid
flowchart TB
    Client[Client / API Consumer] --> API[FastAPI Application]

    API --> Diagnostics[Health and Provider Diagnostics]
    API --> Requirements[Requirement Analysis]
    API --> RAG[RAG Services]
    API --> Agents[Agent Runtime]
    API --> DataAnalysis[Data Analysis Services]

    Requirements --> LLM[LLM Provider Abstraction]
    RAG --> LLM

    LLM --> FakeLLM[Fake Provider]
    LLM --> Ollama[Ollama Provider]
    LLM --> OpenAI[OpenAI Provider]

    RAG --> Ingestion[Ingestion and Text Extraction]
    Ingestion --> Chunking[Document Chunking]
    Chunking --> Embeddings[Embedding Service]
    Embeddings --> VectorStore[In-Memory Vector Store]
    VectorStore --> Retrieval[Retrieval Service]
    Retrieval --> Answer[RAG Answer Generation]
    Answer --> Citations[Source Citations]
    Answer --> Evaluation[RAG Evaluation]

    Agents --> Runtime[Controlled Agent Runtime]
    Runtime --> Registry[Tool Registry]
    Registry --> Executor[Tool Execution Service]
    Executor --> RetrieveTool[rag.retrieve]
    Executor --> RequirementTool[requirements.analyze]
    Executor --> RAGAnswerTool[rag.answer]
    Executor --> DataAnalystTool[data_analysis.agent.run]

    Agents --> QAAgent[QA Agent]
    QAAgent --> RequirementTool
    QAAgent --> RetrieveTool
    QAAgent --> DataAnalystTool

    DataAnalystTool --> DataAnalystAgent[Data Analyst Agent]
    DataAnalystAgent --> SQLGeneration[SQL Generation]
    DataAnalystAgent --> SQLSafety[Read-Only SQL Validation]
    DataAnalystAgent --> SQLExecution[Controlled SQLite Execution]
    DataAnalystAgent --> SQLEvidence[Query Evidence]

    DataAnalysis --> SQLGeneration
    DataAnalysis --> SQLSafety
    DataAnalysis --> SQLExecution
```

The architecture intentionally separates:

* API transport;
* domain services;
* model providers;
* prompts and schemas;
* retrieval infrastructure;
* agent runtime;
* tool registration;
* tool execution.

This separation allows individual components to be tested and replaced without coupling the entire application to one model provider or framework.

## API Endpoints

Interactive OpenAPI documentation is available at:

```text
http://127.0.0.1:8000/docs
```

### Core and LLM

| Method | Endpoint                | Description                                 |
| ------ | ----------------------- | ------------------------------------------- |
| `GET`  | `/health`               | API health check                            |
| `GET`  | `/llm/providers`        | List supported and active LLM providers     |
| `GET`  | `/llm/health`           | Validate the active provider configuration  |
| `POST` | `/analyze`              | Run the initial deterministic text analysis |
| `POST` | `/requirements/analyze` | Analyze a software requirement              |

### RAG

| Method | Endpoint            | Description                                        |
| ------ | ------------------- | -------------------------------------------------- |
| `POST` | `/rag/extract-text` | Extract normalized text from a supported file      |
| `POST` | `/rag/extract-tables` | Extract structured tables from CSV, XLSX and DOCX files |
| `POST` | `/rag/chunk`        | Split document text into configurable chunks       |
| `POST` | `/rag/ingest`       | Ingest raw text and generate document metadata     |
| `POST` | `/rag/ingest-file`  | Extract, ingest and chunk an uploaded file         |
| `POST` | `/rag/embed`        | Generate deterministic embedding vectors           |
| `POST` | `/rag/search`       | Run semantic search over supplied documents        |
| `POST` | `/rag/retrieve`     | Retrieve the most relevant document chunks         |
| `POST` | `/rag/answer`       | Generate a grounded answer using retrieved context |
| `POST` | `/rag/evaluate`     | Evaluate an answer, context and citations          |

### Agents

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `POST` | `/agents/run` | Run the deterministic base agent runtime |
| `GET` | `/agents/tools` | List registered agent tools |
| `POST` | `/agents/tools/execute` | Execute a registered tool directly |
| `POST` | `/agents/qa/run` | Run the specialized QA Agent |
| `POST` | `/agents/plan` | Generate a structured agent plan with an LLM |
| `POST` | `/agents/tools/select` | Select executable tools from an agent plan |
| `POST` | `/agents/execute` | Run the complete controlled multi-step agent workflow |
| `GET` | `/agents/logs` | List persisted agent execution log events |
| `GET` | `/agents/logs/{run_id}` | List execution log events for a specific run |
| `POST` | `/agents/evaluate` | Evaluate an agent execution using deterministic quality checks |
| `GET` | `/agents/specialized` | List specialized agents |
| `POST` | `/agents/qa/evaluate` | Evaluate a QA Agent response using deterministic quality checks |

### Data Analysis

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `POST` | `/data-analysis/sql/generate` | Generate a SQL candidate from a natural-language question |
| `POST` | `/data-analysis/sql/execute` | Execute a read-only SQL query in controlled in-memory SQLite |
| `POST` | `/data-analysis/sql/run` | Generate, validate and execute a SQL workflow |
| `POST` | `/data-analysis/agent/run` | Run the specialized Data Analyst Agent |
| `POST` | `/data-analysis/agent/evaluate` | Evaluate a Data Analyst Agent response |
| `POST` | `/data-analysis/sql/regression/run` | Run SQL workflow regression scenarios |

### Multi-Agent QA Copilot

| `POST` | `multi-agent/qa-copilot/run` |
| `POST` | `multi-agent/qa-copilot/evaluate` |

## Technology Stack

### Current stack

* Python 3.12+
* FastAPI
* Pydantic
* Pydantic Settings
* pytest
* HTTPX
* OpenAI Python SDK
* Ollama
* uv
* Docker
* Docker Compose
* GitHub Actions

### Planned evolution

Future modules may introduce:

* persistent vector databases;
* pgvector or Qdrant;
* LangGraph or equivalent orchestration;
* Model Context Protocol;
* OpenTelemetry;
* Grafana;
* MLflow;
* cloud AI services;
* persistent agent state;
* evaluation datasets and regression pipelines.

Planned technologies are tracked in the [roadmap](ROADMAP.md) and should not be interpreted as current dependencies.

## Repository Structure

```text
applied-ai-engineering-lab/
├── .github/
│   └── workflows/
│       └── ci.yml
├── apps/
│   └── api/
│       ├── Dockerfile
│       └── src/
│           └── ai_api/
│               ├── agents/
│               ├── llm/
│               ├── rag/
│               ├── requirements/
│               ├── config.py
│               ├── main.py
│               └── schemas.py
├── docs/
│   ├── adr/
│   ├── architecture/
│   └── study-notes/
├── tests/
│   └── unit/
├── .env.example
├── CHANGELOG.md
├── CONTRIBUTING.md
├── ROADMAP.md
├── docker-compose.yml
├── pyproject.toml
└── uv.lock
```

## Getting Started

### Prerequisites

Install the following tools:

* Python 3.12 or newer;
* uv;
* Git;
* Docker and Docker Compose, when using containers;
* Ollama, when using a local LLM.

### Clone the repository

```bash
git clone https://github.com/gabrieldevms/applied-ai-engineering-lab.git
cd applied-ai-engineering-lab
```

### Install dependencies

```bash
uv sync --dev
```

### Configure the environment

Create a local `.env` file based on `.env.example`.

Linux or macOS:

```bash
cp .env.example .env
```

PowerShell:

```powershell
Copy-Item .env.example .env
```

The project works locally with the Fake provider and does not require an external API key by default.

### Run the API

```bash
uv run uvicorn ai_api.main:app --reload --app-dir apps/api/src
```

Open:

```text
http://127.0.0.1:8000/health
http://127.0.0.1:8000/docs
```

## Environment Configuration

| Variable                              | Default                  | Description                           |
| ------------------------------------- | ------------------------ | ------------------------------------- |
| `APP_ENV`                             | `local`                  | Current application environment       |
| `LLM_PROVIDER`                        | `fake`                   | Active LLM provider                   |
| `REQUIREMENT_ANALYSIS_RETRY_ATTEMPTS` | `2`                      | Maximum requirement-analysis attempts |
| `OPENAI_API_KEY`                      | empty                    | OpenAI API credential                 |
| `OPENAI_MODEL`                        | empty                    | OpenAI model identifier               |
| `OLLAMA_BASE_URL`                     | `http://localhost:11434` | Ollama server address                 |
| `OLLAMA_MODEL`                        | `llama3.1`               | Local Ollama model                    |
| `OLLAMA_TIMEOUT_SECONDS`              | `120`                    | Ollama request timeout                |
| `EMBEDDING_PROVIDER`                  | `fake`                   | Active embedding provider             |
| `EMBEDDING_DIMENSIONS`                | `32`                     | Deterministic embedding vector size   |

Never commit a local `.env` file or API credentials.

## LLM Providers

### Fake Provider

The default provider is deterministic and requires no external service.

```env
LLM_PROVIDER=fake
```

It is useful for:

* local development;
* automated tests;
* schema validation;
* retry and fallback tests;
* deterministic agent tools.

### Ollama

Ollama enables local and self-hosted LLM execution.

Ensure Ollama is running and the configured model is installed:

```bash
ollama --version
ollama list
ollama pull llama3.1
```

Configure the environment:

```env
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1
OLLAMA_TIMEOUT_SECONDS=120
```

Then start the API normally.

### OpenAI

Configure the provider using environment variables:

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=your-api-key
OPENAI_MODEL=your-model
```

The provider implementation is isolated behind the shared LLM interface, allowing the application services to remain independent of the selected model vendor.

## Running with Docker

Build and start the API:

```bash
docker compose up --build
```

Open:

```text
http://127.0.0.1:8000/health
http://127.0.0.1:8000/docs
```

Stop the containers:

```bash
docker compose down
```

## Running Tests

Run the complete test suite:

```bash
uv run pytest
```

The test suite covers areas such as:

* API behavior;
* request and response schemas;
* application settings;
* LLM providers;
* provider diagnostics;
* output normalization;
* requirement analysis;
* retry and fallback behavior;
* document extraction and ingestion;
* embeddings and vector search;
* semantic retrieval;
* RAG answer generation;
* RAG answer tool execution;
* citations;
* RAG evaluation;
* agent runtime;
* tool registry;
* tool execution;
* agent tool calling;* specialized QA Agent;
* Data Analyst Agent;
* SQL safety validation;
* controlled SQL execution;
* QA Agent data validation selection;
* QA Agent evaluation with data evidence;
* Data Analyst Agent evaluation;
* SQL workflow regression scenarios.

## Continuous Integration

GitHub Actions runs the automated test suite on:

* pull requests targeting `main`;
* pushes to `main`.

The current CI workflow:

1. checks out the repository;
2. configures Python 3.12;
3. installs uv;
4. synchronizes locked dependencies;
5. runs pytest.

## Current Limitations

- PDF extraction depends on text being extractable from the PDF;
- scanned PDFs and OCR are not supported;
- legacy `.doc` and `.xls` files are not supported;
- structured table extraction does not yet infer semantic column types;
- embeddings and vector storage still use deterministic local implementations intended for development and testing;
- SQL execution is currently limited to controlled in-memory SQLite;
- external database connectors are not implemented yet;
- NoSQL data source support is not implemented yet;
- execution logs are persisted locally as JSONL files instead of a production database;
- agent approval is policy-based and synchronous;
- there is no external human approval interface yet;
- agent evaluation is currently deterministic and rule-based;
- LLM-as-judge evaluation is not implemented yet;
- authentication, authorization and multi-user isolation are not implemented;
- the project does not yet provide a deployed frontend;
- MCP server capabilities are not implemented yet.
- Multi-agent reasoning is still mostly deterministic.
- Functional QA, Test Automation, Reviewer and Report agents are not yet LLM-backed.
- Multi-agent conflict detection exists, but automatic conflict resolution is not implemented yet.
- Multi-agent evaluation is deterministic and does not include LLM-as-judge yet.
- Production MCP hosting is not defined yet.

These limitations define the boundary between the implemented foundation and the upcoming MCP, orchestration, evaluation and production capabilities.

## Next Milestone: M7 — Evaluation and LLMOps

The next milestone will focus on continuously evaluating, observing and improving LLM, RAG and agent behavior.

Planned capabilities:

- Prompt regression tests
- Golden evaluation dataset
- LLM output evaluation suite
- RAG regression evaluation suite
- Agent regression evaluation suite
- Multi-Agent QA Copilot regression evaluation
- Tool-calling evaluation
- LLM-as-judge evaluation prototype
- CI evaluation pipeline
- Structured AI execution telemetry
- Token usage tracking
- Cost tracking
- Latency tracking
- Retrieval quality metrics
- Agent execution metrics
- Multi-agent execution metrics
- Observability dashboard

The planned short-term implementation order is:

```text
M5 — MCP QA Server
  ↓
M6 — Multi-Agent QA Copilot
  ↓
M7 — Evaluation and LLMOps
```

## Engineering Approach

Each capability follows the same development cycle:

```text
Understand the problem
        ↓
Define contracts and schemas
        ↓
Implement a small vertical slice
        ↓
Add deterministic tests
        ↓
Expose the capability through the API
        ↓
Document architectural decisions
        ↓
Integrate it into larger workflows
```

The repository favors explicit abstractions and controlled execution over hidden framework behavior.

## Documentation

* [Roadmap](ROADMAP.md)
* [Changelog](CHANGELOG.md)
* [Contributing Guide](CONTRIBUTING.md)
* [Initial Architecture](docs/architecture/initial-architecture.md)
* [Architecture Decision Records](docs/adr/)
* [Study Notes](docs/study-notes/)

## Learning Goals

By the end of the roadmap, the project aims to demonstrate practical experience with:

* Applied AI system architecture;
* LLM provider integration;
* prompt and structured-output engineering;
* RAG pipelines;
* vector retrieval;
* AI agents and tool use;
* Model Context Protocol;
* multi-agent orchestration;
* AI evaluation and testing;
* LLMOps and observability;
* AI security and governance;
* CI/CD for AI applications;
* production-oriented engineering practices.

## Project Nature

This repository is an educational and portfolio project developed incrementally.

It is production-oriented, but it should not be considered a complete production system yet. Each module introduces additional reliability, persistence, observability, security and operational capabilities.
