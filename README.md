# Applied AI Engineering Lab

A production-oriented Applied AI Engineering laboratory focused on software quality, QA workflows, AI agents, RAG, evaluation, observability and governance.

The project evolved into the **AI Quality Command Center**: a local-first platform that demonstrates how AI systems can be designed, tested, observed and governed in a software quality context.

## What This Project Is

Most AI demos stop at a prompt, chatbot or notebook.

This project explores what comes after that:

- How do we structure LLM applications beyond direct model calls?
- How do we validate AI outputs with schemas and tests?
- How do we build RAG workflows with retrieval and citations?
- How do we let agents use tools safely?
- How do we evaluate LLM, RAG, agent and multi-agent behavior?
- How do we observe token usage, cost, latency, quality and failures?
- How do we record security-relevant events such as blocked tool calls and prompt injection risks?
- How can AI be applied to real QA and software quality workflows?

The result is a local AI Quality Engineering platform built around explicit architecture, repeatable evaluation, observability and governance.

## Current Status

- **Current module:** Cloud, Security and Portfolio in progress
- **Latest completed milestone:** Final launch documentation status
- **Next focus:** Local portfolio launch validation and post-launch implementation planning

The current version is suitable for:

- local demonstrations;
- architecture discussions;
- AI Engineering and QA Engineering learning.

It is production-oriented, but it is not a complete production SaaS product yet.

## Product: AI Quality Command Center

M8 introduced the **AI Quality Command Center**, a React and TypeScript frontend connected to the FastAPI backend.

The Command Center provides a local product experience for:

- QA Agent workflows;
- Multi-Agent QA Copilot workflows;
- RAG retrieval and grounded answers;
- Data Analyst Agent workflows;
- AI evaluation and regression visibility;
- observability dashboard;
- execution history;
- run details drill-down;
- usage and cost tracking;
- risk and recommendation panels;
- provider and model settings;
- security and governance endpoints.

The current product flow is:

~~~text
Run an AI workflow
        ↓
Persist telemetry locally
        ↓
Inspect execution history
        ↓
Drill into run details
        ↓
Review observability signals
        ↓
Track risks, usage and governance events
~~~

## Why This Project Exists

Many AI examples demonstrate that a model can answer a question.

This project focuses on the engineering work required to make AI systems:

- modular;
- testable;
- observable;
- auditable;
- provider-independent;
- schema-driven;
- safer to operate;
- useful for real software quality workflows.

The project connects Applied AI Engineering with QA use cases such as:

- requirement analysis;
- acceptance criteria extraction;
- risk identification;
- test scenario generation;
- test automation planning;
- documentation retrieval;
- controlled data validation;
- AI quality evaluation;
- agent and multi-agent observability.

## Who This Project Is For

This project is designed for:

- QA Engineers exploring AI applied to software quality;
- Software Engineers learning practical LLM application architecture;
- AI Engineering learners studying RAG, agents, evaluation and observability;
- technical recruiters and reviewers assessing portfolio depth;
- engineering leaders interested in AI quality, governance and LLMOps patterns.

## Key Capabilities

| Area | What is implemented |
| --- | --- |
| LLM Engineering | Provider abstraction, Fake/OpenAI/Ollama providers, prompts, structured outputs, retries, fallback and diagnostics |
| Requirement Analysis | Structured QA-oriented analysis with risks, rules, acceptance criteria, scenarios and automation opportunities |
| RAG | Ingestion, chunking, deterministic embeddings, semantic search, grounded answers, citations and RAG evaluation |
| File Ingestion | TXT, Markdown, PDF, DOCX, CSV and XLSX extraction, including structured table extraction |
| Agent Runtime | Controlled runtime, execution trace, Tool Registry, Tool Execution Service, planning and tool selection |
| QA Agent | Requirement analysis, RAG support, optional data validation and deterministic evaluation |
| Data Analyst Agent | Natural-language SQL generation, read-only validation, unsafe SQL blocking and controlled SQLite execution |
| Multi-Agent QA Copilot | Specialized QA agents, shared state, artifacts, contracts, conflict handling and final QA report generation |
| MCP QA Server | FastMCP server exposing selected QA, RAG, agent, data analysis and multi-agent capabilities |
| Evaluation and LLMOps | Golden dataset, prompt regression, LLM/RAG/agent/tool-calling/multi-agent evaluation and CI quality checks |
| Observability | Usage, cost, latency, retrieval quality, agent execution, multi-agent execution, dashboard and execution history |
| Security and Governance | Safe provider config, prompt injection detection, tool authorization, telemetry and audit log events |

## Architecture Overview

~~~mermaid
flowchart TB
    User[User / QA Engineer / AI Engineer] --> Frontend[AI Quality Command Center]

    Frontend --> API[FastAPI Backend]

    API --> LLM[LLM Provider Layer]
    API --> RAG[RAG Services]
    API --> Agents[Agent Runtime and Tools]
    API --> Data[Data Analyst Services]
    API --> MultiAgent[Multi-Agent QA Copilot]
    API --> MCP[MCP QA Server]
    API --> Evals[Evaluation and LLMOps]
    API --> Obs[Observability Services]
    API --> Sec[Security and Governance]

    LLM --> Fake[Fake Provider]
    LLM --> Ollama[Ollama Provider]
    LLM --> OpenAI[OpenAI Provider]

    RAG --> Storage[Local JSONL / In-memory Storage]
    Agents --> Storage
    Data --> Storage
    MultiAgent --> Storage
    Evals --> Storage
    Obs --> Storage
    Sec --> Storage

    Storage --> History[Execution History]
    Storage --> Dashboard[Observability Dashboard]

    History --> Frontend
    Dashboard --> Frontend
~~~

The architecture intentionally separates:

- frontend product experience;
- API transport;
- domain services;
- LLM providers;
- prompt and schema contracts;
- RAG infrastructure;
- agent runtime;
- tool registration and execution;
- data analysis workflows;
- multi-agent orchestration;
- evaluation services;
- observability services;
- security and governance services;
- local persistent storage.

This makes the system easier to test, explain, evolve and replace component by component.

## Engineering Approach

Each capability follows the same development cycle:

~~~text
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
Integrate into larger workflows
~~~

The repository favors explicit abstractions and controlled execution over hidden framework behavior.

The project currently does **not** use LangChain, LangGraph or LlamaIndex as core dependencies. Instead, it implements its own lightweight runtime, tool registry, RAG services, evaluation layer and governance controls. These frameworks may be explored later as optional integrations.

## Main Workflows

### 1. Requirement Analysis

A software requirement can be analyzed into:

- business rules;
- acceptance criteria;
- risks;
- open questions;
- positive scenarios;
- negative scenarios;
- edge cases;
- automation opportunities.

### 2. RAG Knowledge Assistant

Documents can be ingested, chunked, searched and used to generate grounded answers with source-aware context.

Supported inputs include:

- TXT;
- Markdown;
- PDF;
- DOCX;
- CSV;
- XLSX.

### 3. QA Agent

The QA Agent coordinates quality-oriented workflows using controlled tools.

It supports requirement analysis, optional RAG context and optional data validation through the Data Analyst Agent.

### 4. Data Analyst Agent

The Data Analyst Agent supports controlled data validation workflows.

It can generate SQL from natural language, validate read-only safety and execute approved queries against controlled in-memory SQLite data.

### 5. Multi-Agent QA Copilot

The Multi-Agent QA Copilot orchestrates specialized agents:

- Orchestrator Agent;
- Requirement Analyst Agent;
- Functional QA Agent;
- Test Automation Agent;
- Reviewer Agent;
- Report Agent.

It produces a structured QA report with artifacts, traceability, quality gates and optional data validation evidence.

### 6. Evaluation and LLMOps

The project includes deterministic evaluation suites for:

- golden dataset scenarios;
- prompt regression;
- LLM outputs;
- RAG behavior;
- agent behavior;
- tool calling;
- multi-agent workflows;
- controlled LLM-as-judge checks.

### 7. Observability

The observability layer tracks:

- latency;
- errors;
- fallback usage;
- token usage;
- estimated cost;
- retrieval quality;
- agent execution health;
- multi-agent execution health;
- dashboard risks;
- recommendations.

### 8. Security and Governance

The security and governance foundation includes:

- safe provider configuration strategy;
- hardened provider settings exposure;
- prompt injection detection baseline;
- prompt injection telemetry;
- prompt injection audit events;
- tool risk classification;
- tool authorization enforcement;
- blocked tool-call telemetry;
- blocked tool-call audit events;
- sensitive data handling policy;
- audit log service foundation.

## API Surface

Interactive OpenAPI documentation is available at:

~~~text
http://127.0.0.1:8000/docs
~~~

Main endpoint groups:

| Group | Examples |
| --- | --- |
| Core and LLM | `/health`, `/llm/providers`, `/llm/health`, `/requirements/analyze` |
| RAG | `/rag/extract-text`, `/rag/extract-tables`, `/rag/retrieve`, `/rag/answer`, `/rag/evaluate` |
| Agents | `/agents/run`, `/agents/tools`, `/agents/tools/execute`, `/agents/qa/run`, `/agents/execute` |
| Data Analysis | `/data-analysis/sql/generate`, `/data-analysis/sql/execute`, `/data-analysis/agent/run` |
| Multi-Agent | `/multi-agent/qa-copilot/run`, `/multi-agent/qa-copilot/evaluate` |
| Evaluation | `/evals/golden-dataset/run`, `/evals/prompt-regression/run`, `/evals/ci/pipeline/run` |
| Observability | `/observability/dashboard`, `/observability/execution-history`, `/observability/usage/records` |
| Security | `/security/prompt-injection/assess`, `/security/blocked-tool-calls`, `/security/audit/events` |

For the full API contract, use the OpenAPI docs after starting the backend.

## Technology Stack

### Backend

- Python 3.12+
- FastAPI
- Pydantic
- Pydantic Settings
- pytest
- HTTPX
- SQLite
- FastMCP
- OpenAI Python SDK
- Ollama
- uv
- Docker
- Docker Compose
- GitHub Actions

### Frontend

- Vite
- React
- TypeScript
- CSS modules / local styles
- typed API clients
- reusable dashboard and console components

### Storage

Current local persistence uses JSONL files for observability and security records.

This is suitable for local development, demos and portfolio presentation, but not yet a production database strategy.

## Repository Structure

~~~text
applied-ai-engineering-lab/
├── .github/
│   └── workflows/
├── apps/
│   ├── api/
│   │   └── src/
│   │       └── ai_api/
│   │           ├── agents/
│   │           ├── data_analysis/
│   │           ├── evals/
│   │           ├── llm/
│   │           ├── mcp_server/
│   │           ├── multi_agent/
│   │           ├── rag/
│   │           ├── requirements/
│   │           ├── security/
│   │           ├── storage/
│   │           └── main.py
│   └── web/
│       └── src/
│           ├── api/
│           ├── components/
│           ├── hooks/
│           ├── pages/
│           ├── styles/
│           └── types/
├── docs/
│   ├── adr/
│   ├── architecture/
│   ├── case-study/
│   ├── demos/
│   ├── diagrams/
│   ├── security/
│   └── study-notes/
├── scripts/
├── tests/
├── CHANGELOG.md
├── CONTRIBUTING.md
├── ROADMAP.md
├── docker-compose.yml
├── pyproject.toml
└── uv.lock
~~~

## Getting Started

### Prerequisites

Install:

- Python 3.12 or newer;
- uv;
- Git;
- Docker and Docker Compose, when using containers;
- Node.js and npm, for the frontend;
- Ollama, when using a local LLM provider.

### Clone the repository

~~~bash
git clone https://github.com/gabrieldevms/applied-ai-engineering-lab.git
cd applied-ai-engineering-lab
~~~

### Install backend dependencies

~~~bash
uv sync --dev
~~~

### Configure environment

Create a local `.env` file based on `.env.example`.

PowerShell:

~~~powershell
Copy-Item .env.example .env
~~~

Linux or macOS:

~~~bash
cp .env.example .env
~~~

The project works locally with the Fake provider and does not require an external API key by default.

### Run the API

~~~bash
uv run uvicorn ai_api.main:app --reload --app-dir apps/api/src
~~~

Open:

~~~text
http://127.0.0.1:8000/health
http://127.0.0.1:8000/docs
~~~

### Run the frontend

~~~powershell
cd apps\web
npm install
npm run dev
~~~

Open the local Vite URL shown in the terminal.

## LLM Providers

### Fake Provider

The default provider is deterministic and requires no external service.

~~~env
LLM_PROVIDER=fake
~~~

Recommended for:

- local development;
- automated tests;
- deterministic demos;
- schema validation;
- evaluation workflows.

### Ollama

Ollama enables local LLM execution.

~~~env
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1
OLLAMA_TIMEOUT_SECONDS=120
~~~

### OpenAI

OpenAI can be enabled with environment variables.

~~~env
LLM_PROVIDER=openai
OPENAI_API_KEY=your-api-key
OPENAI_MODEL=your-model
~~~

Do not commit API keys or local `.env` files.

## Running with Docker

~~~bash
docker compose up --build
~~~

Open:

~~~text
http://127.0.0.1:8000/health
http://127.0.0.1:8000/docs
~~~

Stop containers:

~~~bash
docker compose down
~~~

## Running Tests

Run the complete test suite:

~~~bash
uv run pytest
~~~

The tests cover API behavior, schemas, LLM providers, requirement analysis, RAG, file ingestion, agents, tool execution, SQL safety, MCP tools, multi-agent workflows, evaluation, observability, telemetry, prompt injection detection, tool authorization and audit logging.

## Demo and Portfolio Materials

Recommended reading order:

1. [Architecture](docs/architecture/initial-architecture.md)
2. [Launch Demo Script](docs/demos/launch-demo-script.md)
3. [AI Quality Command Center Case Study](docs/case-study/ai-quality-command-center-case-study.md)
4. [Current Capabilities Reference](docs/reference/current-capabilities-reference.md)
5. [Security and Governance Baseline](docs/security/security-and-governance-baseline.md)
6. [Roadmap](ROADMAP.md)

Demo documents:

- [Demonstration Scenarios](docs/demos/demonstration-scenarios.md)
- [Launch Demo Script](docs/demos/launch-demo-script.md)

Portfolio document:

- [AI Quality Command Center Case Study](docs/case-study/ai-quality-command-center-case-study.md)

Technical reference:

- [Current Capabilities Reference](docs/reference/current-capabilities-reference.md)

## Documentation

- [Roadmap](ROADMAP.md)
- [Changelog](CHANGELOG.md)
- [Contributing Guide](CONTRIBUTING.md)
- [Architecture](docs/architecture/initial-architecture.md)
- [Demonstration Scenarios](docs/demos/demonstration-scenarios.md)
- [Launch Demo Script](docs/demos/launch-demo-script.md)
- [AI Quality Command Center Case Study](docs/case-study/ai-quality-command-center-case-study.md)
- [Current Capabilities Reference](docs/reference/current-capabilities-reference.md)
- [Provider Configuration Strategy](docs/security/provider-configuration-strategy.md)
- [Security and Governance Baseline](docs/security/security-and-governance-baseline.md)
- [Prompt Injection Protection Baseline](docs/security/prompt-injection-protection-baseline.md)
- [Sensitive Data Handling Policy](docs/security/sensitive-data-handling-policy.md)
- [Audit Log Schema](docs/security/audit-log-schema.md)
- [Tool Authorization Boundaries](docs/security/tool-authorization-boundaries.md)
- [Architecture Decision Records](docs/adr/)
- [Study Notes](docs/study-notes/)

## Current Limitations

The current version is optimized for local development, learning and portfolio demonstration.

Known limitations:

- no cloud deployment yet;
- no production authentication or access control yet;
- no multi-user isolation yet;
- no production secrets manager yet;
- no production database storage yet;
- local JSONL storage is not production-grade persistence;
- persistent vector database storage is not implemented yet;
- persistent agent state and session resume are not implemented yet;
- production monitoring integrations are not implemented yet;
- production MCP hosting is not defined yet;
- audit log UI and retention policy are not implemented yet;
- prompt injection detection is currently a deterministic baseline, not complete adversarial protection;
- SQL execution is currently limited to controlled in-memory SQLite;
- external SQL and NoSQL connectors are not implemented yet;
- some specialized agents still use deterministic behavior instead of full LLM-backed reasoning;
- frontend console execution results are currently kept in local React page state;
- the project does not yet provide a deployed frontend.

These limitations define the boundary between the implemented local AI engineering product and future production hardening.

## Post-launch Roadmap

After the M8 local portfolio launch, the project will continue through focused implementation packs.

### Pack 1 — Cloud & Deployment

- cloud deployment;
- deployment pipeline;
- production health checks.

### Pack 2 — Production Observability

- production monitoring;
- persistent evaluation artifacts;
- more robust dashboards and scorecards.

### Pack 3 — Production Agent State

- persistent vector storage;
- persistent agent state;
- session resume and memory persistence.

### Pack 4 — Security Enterprise Layer

- authentication;
- access control;
- multi-user isolation;
- secrets management.

### Pack 5 — MCP Production Layer

- production MCP hosting;
- external tool/server strategy.

### Pack 6 — Data Integrations

- external SQL connectors;
- NoSQL connectors;
- credential handling;
- read-only governance.

### Pack 7 — Multi-provider AI Evaluation

- additional LLM providers;
- Anthropic Claude provider;
- Google Gemini provider;
- provider comparison evaluation;
- latency, cost and quality benchmarks.

## Learning Goals

The project demonstrates practical experience with:

- Applied AI system architecture;
- LLM provider integration;
- prompt and structured-output engineering;
- RAG pipelines;
- AI agents and tool use;
- Model Context Protocol;
- multi-agent orchestration;
- AI evaluation and testing;
- LLMOps and observability;
- AI security and governance;
- CI/CD for AI applications;
- production-oriented engineering practices;
- portfolio-grade AI platform design.

## Project Nature

This repository is an educational and portfolio project developed incrementally.

It is production-oriented, but it should not be considered a complete production system yet. Each module introduces additional reliability, persistence, observability, security and operational capabilities.

---

Developed by Gabriel Moreira.
