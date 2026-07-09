# Applied AI Engineering Lab

A practical and production-oriented lab for learning and building Applied AI Engineering systems.

## Purpose

This project is a hands-on journey into Applied AI Engineering, focused on building reliable, testable and production-ready AI applications.

The lab covers:

- Software Engineering for AI
- LLM Engineering
- Retrieval-Augmented Generation
- AI Agents
- Model Context Protocol
- Multi-Agent Systems
- Evaluation and Testing for AI
- LLMOps
- Observability
- Cloud Deployment
- Security and Governance

## Main Goal

The main goal is to evolve from a simple AI API into a complete AI Engineering platform with:

- LLM services
- RAG services
- Agent services
- MCP servers
- Multi-agent orchestration
- Evaluation pipelines
- Observability
- CI/CD
- Security practices

## Architecture Vision

```text
User / Interface
      |
      v
API Gateway / Backend
      |
      v
AI Orchestrator
      |
      +--> LLM Service
      +--> RAG Service
      +--> Agent Service
      +--> MCP Client
      +--> Evaluation Service
      +--> Observability Service
      |
      v
External Tools
GitHub | Jira | Database | Files | APIs | Playwright | Documentation
```

## Tech Stack

Initial stack:

- Python
- FastAPI
- Pydantic
- pytest
- uv
- Docker
- PostgreSQL
- GitHub Actions

Future stack:

- LangGraph
- Model Context Protocol
- pgvector
- Qdrant
- OpenTelemetry
- Grafana
- MLflow
- Cloud AI platforms

## Roadmap

See [ROADMAP.md](./ROADMAP.md).

## Module Status

### Completed

* M0 — Foundation
* M1 — AI API Base

### In Progress

* M2 — LLM Engineering

### Upcoming

* M3 — RAG Knowledge Assistant
* M4 — AI Agents
* M5 — MCP QA Server
* M6 — Multi-Agent QA Copilot
* M7 — Evaluation and LLMOps
* M8 — Cloud, Security and Portfolio

### Current Phase

M2 — LLM Engineering

## Repository Structure

```text
applied-ai-engineering-lab/
  apps/
    api/
  packages/
    prompts/
    schemas/
    evals/
    shared/
  docs/
    architecture/
    adr/
    diagrams/
    study-notes/
  infra/
    docker/
    github-actions/
  datasets/
    samples/
  tests/
    unit/
    integration/
    evals/
```

## Current API Capabilities

The current API provides a simple and deterministic foundation for future AI features.

Available endpoints:

### Health Check

```
GET /health
```

Returns the current API status.

Example response:

```
{
  "status": "ok"
}
```

### Text Analysis

```
POST /analyze
```

Receives a text input and returns a structured response with basic text analysis.

Current behavior:

* Returns the original text
* Counts words
* Counts characters
* Returns the requested language
* Returns a deterministic summary message

This endpoint does not use an LLM yet. LLM integration will be introduced in M2 — LLM Engineering.

### Basic Logging

The API includes basic request logging.

Each request logs:

* HTTP method
* Request path
* Response status code
* Request duration in milliseconds

### Basic Error Handling

The API includes basic error handling for request validation errors and unexpected internal errors.

Validation errors return a structured response with:

* Error type
* Error message
* Error details

### Requirement Analysis

    POST /requirements/analyze

Receives a software requirement and returns a structured quality-oriented analysis.

Current behavior:

- Uses the requirement analyzer service
- Builds LLM-ready prompt messages
- Uses a fake LLM provider for now
- Parses the provider response as JSON
- Validates the response with Pydantic schemas
- Returns a structured analysis in Portuguese

The response includes:

- Summary
- Business rules
- Acceptance criteria
- Risks
- Open questions
- Positive test scenarios
- Negative test scenarios
- Edge cases
- Automation opportunities

## Environment Configuration

The project uses environment variables to configure runtime behavior.

Create a local `.env` file based on `.env.example` when needed.

Current variables:

    APP_ENV=local
    LLM_PROVIDER=fake
    REQUIREMENT_ANALYSIS_RETRY_ATTEMPTS=2
    OPENAI_API_KEY=
    OPENAI_MODEL=

The default provider is currently `fake`, which allows local execution without API keys.

## Running the API Locally

Run the API directly with uv:

```
uv run uvicorn ai_api.main:app --reload --app-dir apps/api/src
```

Open:

```
http://127.0.0.1:8000/health
http://127.0.0.1:8000/docs
```

## Running Tests

Run the test suite:

```
uv run pytest
```

## Running with Docker

Build and start the API container:

```
docker compose up --build
```

Open:

```
http://127.0.0.1:8000/health
http://127.0.0.1:8000/docs
```

Stop the containers:

```
docker compose down
```

## Continuous Integration

This project uses GitHub Actions to run automated tests on pull requests and pushes to the main branch.

The CI pipeline currently validates:

- Python setup
- uv dependency installation
- pytest test execution

## Learning Approach

Each module follows a practical engineering cycle:

```text
Understand the concept
      |
      v
Build a small implementation
      |
      v
Test it
      |
      v
Document it
      |
      v
Automate it
      |
      v
Improve the architecture
```

## Local LLM Provider with Ollama

The API also supports Ollama as a local/self-hosted LLM provider.

Example `.env` configuration:

    LLM_PROVIDER=ollama
    OLLAMA_BASE_URL=http://localhost:11434
    OLLAMA_MODEL=llama3.1
    OLLAMA_TIMEOUT_SECONDS=120

Before running the API, make sure Ollama is installed, running, and the selected model is available locally:

    ollama --version
    ollama list
    ollama pull llama3.1

When using Ollama, the requirement analysis flow remains the same:

    request
      -> prompt builder
      -> Ollama provider
      -> JSON parser
      -> Pydantic validation
      -> retry/fallback handling
      -> structured API response

## Real LLM Provider

The API supports environment-based LLM provider selection.

The default provider is:

    LLM_PROVIDER=fake

To use OpenAI locally, create a `.env` file based on `.env.example`:

    LLM_PROVIDER=openai
    OPENAI_API_KEY=your-api-key
    OPENAI_MODEL=your-model

Do not commit the `.env` file.

When using the OpenAI provider, the requirement analysis flow remains the same:

    request
      -> prompt builder
      -> OpenAI provider
      -> JSON parser
      -> Pydantic validation
      -> retry/fallback handling
      -> structured API response

## LLM Provider Diagnostics

The API exposes diagnostic endpoints for LLM provider configuration.

    GET /llm/providers

Returns the active provider and the list of supported providers.

    GET /llm/health

Returns configuration health for the active provider.

This endpoint does not call the model. It only checks environment-based configuration and avoids exposing secrets such as API keys.

## LLM Output Normalization

LLM responses are normalized before schema validation.

The parser accepts:

- Pure JSON objects
- JSON objects inside Markdown code blocks
- JSON objects surrounded by explanatory text

After extraction, the response is still validated by Pydantic schemas.
Invalid schemas are rejected.

## RAG Document Chunking

The API includes a basic document chunking endpoint.

    POST /rag/chunk

It receives raw document text and splits it into smaller chunks.

Current behavior:

- Character-based chunking
- Configurable chunk size
- Configurable chunk overlap
- Source tracking
- Chunk metadata

This is the first step toward the RAG pipeline.
Future steps will include embeddings, vector storage and retrieval.

## RAG Document Ingestion

The API includes a document ingestion endpoint.

    POST /rag/ingest

It receives raw document text, creates a stable document identifier, generates chunks and returns document metadata.

Current behavior:

- Raw text ingestion
- Stable document ID based on source and content hash
- Metadata support
- Chunk generation
- Chunk metadata enrichment
- Source tracking

This is part of the RAG foundation and prepares the project for embeddings, vector storage and semantic retrieval.

## Status

This project is currently in the foundation phase.

## Next Phase — M2: LLM Engineering

The next phase introduces LLM Engineering concepts and implementation practices.

M2 will focus on:

* LLM provider integration
* Prompt templates
* Structured outputs
* JSON schema validation
* Retry strategy
* Fallback strategy
* Requirement analysis with LLMs
* LLM response testing

The goal of M2 is to evolve the deterministic `/analyze` endpoint into the foundation for intelligent and structured AI-powered analysis.
