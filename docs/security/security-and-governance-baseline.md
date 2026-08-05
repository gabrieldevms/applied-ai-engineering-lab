# Security and Governance Baseline

This document describes the current security and governance baseline of the Applied AI Engineering Lab and the AI Quality Command Center.

The goal is not to claim production-grade security. The goal is to make the current trust boundaries, implemented controls, known limitations and future hardening path explicit.

## Current Scope

The project is currently a local-first AI engineering and portfolio platform.

It includes:

- local API execution;
- local frontend execution;
- local JSONL persistence;
- controlled LLM provider configuration;
- deterministic prompt injection assessment;
- tool risk classification;
- tool authorization checks;
- telemetry for security-relevant events;
- audit log service foundation;
- documentation for sensitive data, prompt injection, provider configuration and tool authorization.

The project is production-oriented, but it is not a complete production system yet.

## Security Principles

The current baseline follows these principles:

~~~text
minimize exposed secrets
        ↓
avoid storing raw sensitive payloads
        ↓
make tool execution explicit
        ↓
classify tool risk
        ↓
enforce authorization before execution
        ↓
record telemetry for operational visibility
        ↓
record audit events for security decisions
        ↓
document limitations honestly
~~~

## Implemented Controls

### Provider Configuration Safety

Implemented controls:

- provider selection is backend-owned and environment-based;
- provider health responses expose safe configuration metadata only;
- API keys are not returned by health or settings endpoints;
- raw provider URLs are not exposed through the frontend provider settings view;
- the frontend displays sanitized provider status and logical configuration fields.

Related document:

- [Provider Configuration Strategy](provider-configuration-strategy.md)

### Prompt Injection Baseline

Implemented controls:

- deterministic prompt injection detection service;
- prompt injection assessment endpoint;
- risk levels: `none`, `low`, `medium`, `high`;
- recommended actions: `allow`, `allow_with_warning`, `require_review`, `block`;
- high-risk assessments require blocking;
- prompt injection telemetry for relevant assessments;
- prompt injection audit events for high-risk/blocking assessments;
- original assessed text is not stored in telemetry or audit events.

Current endpoint:

- `POST /security/prompt-injection/assess`

Telemetry endpoint:

- `GET /security/prompt-injection/records`

Audit endpoint:

- `GET /security/audit/events`

Related document:

- [Prompt Injection Protection Baseline](prompt-injection-protection-baseline.md)

### Tool Authorization

Implemented controls:

- registered tools include security metadata;
- tools have risk classification;
- tool execution is centralized in `ToolExecutionService`;
- authorization is checked before handler execution;
- caller type and environment are validated;
- human approval requirement can block tool execution;
- high prompt injection risk can block tools that require prompt injection assessment;
- blocked tool calls are recorded as telemetry;
- blocked tool calls are recorded as audit events.

Current telemetry endpoint:

- `GET /security/blocked-tool-calls`

Current audit endpoint:

- `GET /security/audit/events`

Related document:

- [Tool Authorization Boundaries](tool-authorization-boundaries.md)

### Sensitive Data Handling

Implemented controls and policies:

- sensitive payloads should not be stored in telemetry by default;
- prompt injection telemetry does not store the assessed input text;
- blocked tool-call telemetry does not store raw tool arguments;
- audit events are designed to store decisions and sanitized metadata, not raw payloads;
- `.env` and credentials must not be committed;
- local JSONL data is treated as development/demo storage.

Related document:

- [Sensitive Data Handling Policy](sensitive-data-handling-policy.md)

### Audit Logs

Implemented controls:

- audit event schema documentation;
- audit log service foundation;
- in-memory audit event store;
- local JSONL audit event store;
- audit event listing endpoint;
- blocked tool-call audit event recording;
- prompt injection audit event recording.

Current endpoint:

- `GET /security/audit/events`

Related document:

- [Audit Log Schema](audit-log-schema.md)

## Current Security Endpoints

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `POST` | `/security/prompt-injection/assess` | Assess prompt injection risk for a text |
| `GET` | `/security/prompt-injection/records` | List prompt injection telemetry records |
| `GET` | `/security/blocked-tool-calls` | List blocked tool-call telemetry records |
| `GET` | `/security/audit/events` | List security audit log events |

## Current Trust Boundaries

### Frontend

The frontend is a local product interface for demonstration and portfolio usage.

Current limitations:

- no user authentication;
- no role-based access control;
- no multi-user isolation;
- console state is local to React page state;
- provider configuration is read-only and sanitized.

### Backend API

The backend exposes AI, RAG, agent, evaluation, observability and security endpoints.

Current controls:

- schema validation with Pydantic;
- controlled tool execution;
- tool authorization enforcement;
- prompt injection risk assessment;
- telemetry and audit logging for selected security events.

Current limitations:

- no external authentication;
- no API authorization layer;
- no rate limiting;
- no production secrets manager;
- no tenant isolation;
- no production database.

### Storage

Current storage is local JSONL.

Current controls:

- configurable storage backend;
- configurable base directory;
- separate JSONL files for observability and security records.

Current limitations:

- local JSONL is not production-grade storage;
- no encryption at rest;
- no retention policy;
- no access control;
- no audit log UI;
- no tamper-resistant audit storage.

### LLM Providers

Current providers:

- Fake provider;
- Ollama provider;
- OpenAI provider.

Current controls:

- provider abstraction;
- environment-based provider selection;
- safe provider diagnostics;
- sanitized provider settings exposure.

Current limitations:

- no centralized secrets manager;
- no per-user provider credentials;
- no provider usage policy enforcement beyond local configuration;
- no production provider governance workflow.

### MCP

The MCP server exposes selected project capabilities locally.

Current controls:

- explicit MCP tool definitions;
- local smoke validation;
- tool inventory documentation.

Current limitations:

- no production MCP hosting;
- no MCP authentication;
- no MCP-specific audit integration yet;
- no external MCP gateway.

## What This Baseline Does Not Claim

This baseline does not claim that the project is production-secure.

The following are not implemented yet:

- production authentication;
- role-based access control;
- multi-user isolation;
- tenant isolation;
- production secrets management;
- production database storage;
- persistent vector database storage;
- production audit retention;
- tamper-resistant audit logs;
- audit log UI;
- OpenTelemetry integration;
- external SIEM integration;
- production monitoring;
- production MCP hosting;
- production deployment pipeline.

## Current Status Summary

Implemented:

- provider configuration strategy;
- hardened provider settings exposure;
- prompt injection baseline documentation;
- prompt injection detection baseline;
- prompt injection telemetry;
- prompt injection audit events;
- tool authorization boundaries documentation;
- tool risk classification;
- tool authorization enforcement;
- blocked tool-call telemetry;
- blocked tool-call audit events;
- sensitive data handling policy;
- audit log schema documentation;
- audit log service foundation.

Still future work:

- authentication and access control;
- multi-user isolation;
- secrets management;
- production monitoring;
- production audit storage and retention;
- audit log UI;
- production MCP hosting;
- cloud deployment;
- deployment pipeline.

## Recommended Next Steps

Before a production deployment, the project should add:

1. authentication and access control;
2. role-based authorization for sensitive endpoints;
3. secrets management;
4. production database storage;
5. audit retention rules;
6. audit log UI;
7. rate limiting;
8. OpenTelemetry instrumentation;
9. production monitoring dashboards;
10. cloud deployment pipeline;
11. production MCP hosting strategy.

## Portfolio Positioning

For portfolio and demonstration purposes, this security baseline shows that the project considers:

- prompt injection risk;
- tool authorization;
- safe provider configuration;
- sensitive data handling;
- auditability;
- observability;
- explicit trust boundaries;
- honest production limitations.

The project should be presented as a local-first, production-oriented AI Quality Engineering platform, not as a fully production-ready SaaS product.
