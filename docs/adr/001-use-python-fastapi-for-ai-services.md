# ADR 001 — Use Python and FastAPI for AI Services

## Status

Accepted

## Context

The project needs a backend stack suitable for building APIs, integrating LLM providers, validating structured data, running tests and evolving into RAG, agents, MCP and LLMOps components.

The stack should be simple enough for fast learning, but strong enough to support production-oriented practices.

## Decision

We will use Python as the main language and FastAPI as the main API framework for the initial AI services.

## Consequences

### Positive

- Python has a strong ecosystem for AI, ML and automation.
- FastAPI is suitable for building modern APIs.
- Pydantic provides strong data validation.
- pytest can be used for unit and integration tests.
- The stack works well with Docker and CI/CD.
- The ecosystem supports future integrations with LLMs, RAG, agents and evaluation tools.

### Negative

- Some frontend or agent integrations may still require TypeScript.
- Performance-sensitive components may require optimization later.
- Async patterns must be used carefully.

## Alternatives Considered

### Node.js with TypeScript

Good option for full-stack applications and some agent tooling, but Python has a stronger ecosystem for AI and ML.

### Java with Spring Boot

Strong enterprise option, but heavier for the current learning and prototyping goals.

### Go

Good performance and simplicity, but weaker ecosystem for AI experimentation compared to Python.
