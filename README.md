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

## Current Phase

M1 — AI API Base

## Roadmap

See [ROADMAP.md](./ROADMAP.md).

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
