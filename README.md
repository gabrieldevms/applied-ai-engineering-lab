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
