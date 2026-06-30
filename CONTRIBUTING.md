# Contributing Guide

This project follows a simple engineering workflow designed for learning, building and documenting Applied AI Engineering systems.

The goal is to keep the project organized, traceable and close to a real software engineering workflow.

## Workflow

Every change should follow this cycle:

```
Issue
  -> Branch
  -> Implementation
  -> Tests
  -> Documentation
  -> Pull Request
  -> Review
  -> Merge
```

## Branch Naming

Use short and clear branch names.

Examples:

```
docs/initial-project-documentation
feature/ai-api-base
feature/llm-structured-output
feature/rag-ingestion
feature/mcp-qa-server
refactor/api-project-structure
fix/docker-build
```

Recommended prefixes:

* `docs/` for documentation changes
* `feature/` for new features
* `fix/` for bug fixes
* `refactor/` for code restructuring
* `test/` for test-related changes
* `chore/` for maintenance tasks

## Commit Convention

Use simple conventional commits.

Examples:

```
chore: initialize project structure
docs: add initial architecture document
feature: add health check endpoint
test: add unit tests for analyze endpoint
refactor: improve api project structure
fix: handle invalid input error
```

Common prefixes:

* `chore`
* `docs`
* `feature`
* `test`
* `refactor`
* `fix`

## Pull Request Requirements

Each Pull Request should explain:

* What was changed
* Why it was changed
* How it was tested
* What risks exist
* What documentation was updated

## Pull Request Checklist

Before opening a Pull Request, check:

* [ ] The related issue exists
* [ ] The branch name is clear
* [ ] The change is focused
* [ ] The code or documentation is readable
* [ ] Tests were added or updated when needed
* [ ] Documentation was updated when needed
* [ ] No secrets were committed
* [ ] The change is aligned with the roadmap

## Definition of Done

A task is done when:

* [ ] The acceptance criteria are met
* [ ] The code or documentation is committed
* [ ] Tests were added or updated when needed
* [ ] No secrets were committed
* [ ] The README or documentation was updated when needed
* [ ] The related issue is linked
* [ ] The Pull Request is merged
* [ ] The project board is updated

## Documentation Standards

Documentation should be clear, objective and useful.

Main documentation files should preferably be written in English because this project is also intended to be used as a technical portfolio.

Study notes may be written in Portuguese when the goal is personal learning and deeper understanding.

Recommended structure:

* `README.md` for project overview
* `ROADMAP.md` for learning and implementation phases
* `CHANGELOG.md` for relevant changes
* `CONTRIBUTING.md` for workflow rules
* `docs/architecture/` for architecture documents
* `docs/adr/` for architectural decisions
* `docs/study-notes/` for personal study notes

## Architecture Decision Records

Architectural decisions should be documented using ADR files inside:

```
docs/adr/
```

Each ADR should explain:

* Context
* Decision
* Consequences
* Alternatives considered

## Secrets and Sensitive Data

Never commit:

* API keys
* Access tokens
* Passwords
* Private credentials
* Production data
* Sensitive personal data
* Internal company data

Use environment variables and `.env` files for local secrets.

A `.env.example` file may be used to document required environment variables without exposing real values.

## Learning Principle

This project is not only about making things work.

It is about learning how to build AI systems with engineering discipline:

```
Understand the concept
  -> Build a small implementation
  -> Test it
  -> Document it
  -> Automate it
  -> Improve the architecture
```
