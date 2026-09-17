# Agent Development Guidelines

This document defines the development rules for AI-assisted work in the Applied AI Engineering Lab.

The goal is to preserve the project's architecture, reviewability, quality standards and Git workflow regardless of which coding agent or development tool is used.

## Repository Workflow

- Never implement changes directly on `main`.
- Start each change from an updated `main` branch.
- Create one focused branch per change.
- Keep pull requests small, focused and reviewable.
- Do not force-push protected branches.
- Do not merge pull requests automatically.
- Do not commit, push, open a pull request or merge unless explicitly instructed.
- Do not delete local or remote branches unless explicitly instructed.
- Avoid mixing unrelated refactors with feature work.
- Preserve repository history and existing Git protections.

## Change Discipline

Before changing code:

1. Inspect the relevant implementation.
2. Inspect related tests and contracts.
3. Understand the current behavior.
4. Determine the smallest change that satisfies the requirement.

During implementation:

- Prefer surgical changes over broad refactors.
- Preserve existing public contracts unless the task explicitly requires changing them.
- Do not introduce new frameworks, libraries or infrastructure dependencies without architectural justification.
- Do not replace working abstractions simply because another approach is more common.
- Do not add speculative abstractions for requirements that do not exist yet.
- Keep architecture explicit and auditable.

## Testing Rules

- Never modify tests only to make a failing implementation pass.
- When a test fails, first determine whether:
  - production code is incorrect;
  - the test expectation is incorrect;
  - the contract intentionally changed.
- Add or update tests when runtime behavior changes.
- Preserve deterministic tests whenever practical.
- Run focused tests during implementation and the complete relevant validation before considering the work finished.

### Backend validation

From the repository root:

```bash
uv run pytest
```

### Frontend validation

From `apps/web`:

```bash
npm run build
npm run lint
```

Return to the repository root after frontend validation.

## Language and Naming

- Source code must use English identifiers.
- Filenames must use English.
- Commit messages must use English.
- Technical documentation must use English.
- Code comments must use English unless there is a strong domain-specific reason otherwise.
- User-facing UI content may use PT-BR when appropriate to the product experience.
- Prefer clear, descriptive names over abbreviations.

## Architecture Principles

Preserve the current architectural direction unless a change explicitly requires otherwise.

The project intentionally favors explicit, lightweight abstractions for:

- LLM providers;
- structured outputs;
- RAG;
- agent runtime;
- tool registration and execution;
- data analysis;
- multi-agent orchestration;
- evaluation;
- observability;
- security and governance.

Do not introduce high-level orchestration frameworks such as LangChain, LangGraph or LlamaIndex into the core architecture without an explicit architectural decision.

Existing abstractions should be extended before introducing parallel implementations when doing so keeps responsibilities clear.

## AI and Agent Reliability

For AI-related features:

- Prefer structured schemas over unvalidated free-form outputs.
- Preserve deterministic validation where possible.
- Maintain execution traceability.
- Consider evaluation impact when changing prompts, providers, tools, RAG behavior or agent orchestration.
- Do not silently weaken safety, authorization or governance controls.
- Do not store raw sensitive prompts, secrets or tool payloads in telemetry unless explicitly designed and reviewed.
- Keep provider-specific behavior behind provider abstractions where applicable.

## Security and Secrets

- Never commit secrets, API keys, credentials or real sensitive customer data.
- Do not expose secrets through frontend configuration, logs, telemetry or API responses.
- Preserve existing prompt-injection, tool-authorization and audit boundaries.
- Any change that expands external access, tool permissions or sensitive-data handling requires explicit review.

## Documentation

Update documentation only when the change affects documented behavior, architecture, setup, roadmap status or public capabilities.

Do not update README, ROADMAP or CHANGELOG mechanically for every small implementation.

Documentation must describe implemented behavior accurately and must not claim production readiness for capabilities that are still local, experimental or incomplete.

## Local Development Environment

The primary local development environment is Windows with PowerShell and VS Code.

When providing commands intended for the developer to run locally:

- prefer PowerShell-compatible commands;
- do not assume Bash-only utilities are available;
- use repository-relative paths whenever practical;
- preserve the existing `uv`, `npm`, Docker and Git workflows;
- do not modify the developer's global environment unless explicitly required and approved.

## Human Review Checkpoint

AI-assisted implementation must preserve a human review checkpoint before changes are published.

Unless explicitly instructed otherwise, after implementing a change:

1. Run the applicable validation.
2. Run `git status`.
3. Run `git diff --check`.
4. Show or summarize the complete relevant diff.
5. Stop before committing or pushing.

Do not automatically stage, commit, push or open a pull request simply because implementation and tests succeeded.

The developer must have an opportunity to inspect the changes locally in VS Code before publication.

## Pull Request Quality

Before a pull request is considered ready:

- inspect the complete diff;
- remove unrelated changes;
- run applicable tests;
- run frontend build/lint when frontend code changed;
- run backend tests when backend behavior changed;
- verify documentation claims;
- verify that no secrets or generated local runtime data were added;
- summarize the change, validation performed and relevant limitations.

## Current Project Direction

The project has completed its initial local portfolio launch as the AI Quality Command Center.

Post-launch development is organized into focused implementation packs.

The completed implementation pack is **Pack 1 — Cloud & Deployment Readiness**.

The current development focus is **Pack 2 — Production Observability**.

Later packs cover:

- Pack 3 — Production Agent State;
- Pack 4 — Enterprise Security Layer;
- Pack 5 — MCP Production Layer;
- Pack 6 — Data Integrations;
- Pack 7 — Multi-provider AI Evaluation.

Changes should respect this staged roadmap and avoid prematurely implementing work assigned to later packs.
