# Provider Configuration Strategy

## Objective

This document defines the provider configuration strategy for the Applied AI Engineering Lab and the AI Quality Command Center.

The goal is to keep LLM provider configuration safe, explicit and environment-driven while preserving the local-first nature of the project.

This strategy is part of the M8 security and governance baseline.

## Context

The platform currently supports multiple LLM providers through a provider abstraction layer.

Current providers:

- `fake`
- `ollama`
- `openai`

The project also plans future provider extensions, such as:

- Anthropic Claude
- Google Gemini
- Azure OpenAI
- other compatible providers

Because providers may require credentials, network access, model identifiers, timeouts and pricing assumptions, provider configuration must follow clear safety boundaries.

## Current Provider Roles

### Fake Provider

The Fake provider is the safest default provider.

It is used for:

- local development
- automated tests
- deterministic evaluations
- schema validation
- retry and fallback testing
- examples that should not require API keys

Characteristics:

- requires no credentials
- does not call external services
- provides deterministic behavior
- is safe for CI and local demos

Recommended environments:

- local
- test
- CI
- documentation examples

### Ollama Provider

The Ollama provider is used for local LLM execution.

It is useful for:

- local experimentation
- offline or self-hosted model workflows
- demos without external API billing
- testing provider abstraction against real model behavior

Characteristics:

- usually runs on `localhost`
- requires a local Ollama service
- does not require cloud API keys
- model behavior may vary depending on the installed model

Recommended environments:

- local
- experimental development
- controlled demos

### OpenAI Provider

The OpenAI provider is used for external hosted LLM execution.

It is useful for:

- testing with production-grade hosted models
- comparing local and cloud model behavior
- evaluating provider-specific output quality
- validating structured LLM workflows against real hosted APIs

Characteristics:

- requires an API key
- may generate cost
- depends on external network availability
- should never expose credentials to the frontend
- should be configured only through secure backend environment variables

Recommended environments:

- local development with explicit `.env`
- controlled demos
- future server-side staging/production environments

## Configuration Principles

Provider configuration must follow these principles:

### 1. Backend-owned configuration

Provider configuration must be owned by the backend.

The frontend may display provider status, selected provider names or model labels, but it must not own credentials or sensitive provider configuration.

### 2. Environment-driven settings

Provider configuration should come from environment variables or future secret management systems.

Configuration must not be hardcoded into application code.

### 3. Safe local defaults

The default configuration should be safe to run without paid providers or secrets.

The default provider should remain suitable for local development and automated validation.

### 4. No secrets in source control

API keys, tokens and provider credentials must never be committed.

Local `.env` files must remain ignored by Git.

Only `.env.example` should be committed.

### 5. Explicit provider selection

Provider selection must be explicit through configuration.

A workflow should not silently switch to a paid or external provider unless configured to do so.

### 6. Clear provider diagnostics

The backend should expose safe provider diagnostics that help validate configuration without leaking secrets.

Diagnostics may include:

- active provider name
- configured model name
- provider availability
- health status
- error category

Diagnostics must not include:

- API keys
- raw tokens
- secret values
- Authorization headers
- sensitive request payloads

## Current Environment Variables

Current relevant provider configuration variables include:

```env
LLM_PROVIDER=fake
OPENAI_API_KEY=
OPENAI_MODEL=
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1
OLLAMA_TIMEOUT_SECONDS=120
```

Storage-related variables include:

```env
STORAGE_BACKEND=local_jsonl
STORAGE_BASE_DIR=.data
AI_USAGE_RECORDS_PATH=observability/usage-records.jsonl
EVALUATION_TELEMETRY_EVENTS_PATH=observability/evaluation-telemetry-events.jsonl
RETRIEVAL_QUALITY_RECORDS_PATH=observability/retrieval-quality-records.jsonl
AGENT_EXECUTION_RECORDS_PATH=observability/agent-execution-records.jsonl
MULTI_AGENT_EXECUTION_RECORDS_PATH=observability/multi-agent-execution-records.jsonl
```

## Frontend Boundaries

The AI Quality Command Center may show provider-related information, but it must respect strict security boundaries.

The frontend may display:

- active provider name
- configured model name
- provider health status
- provider availability
- supported provider list
- usage and cost estimates
- provider diagnostics returned safely by the backend

The frontend must not display or store:

- API keys
- access tokens
- raw secrets
- secret environment variable values
- Authorization headers
- full provider credentials
- sensitive backend configuration

The frontend must not send provider secrets directly to the browser in the current local architecture.

## Provider Settings UI Strategy

The current Provider and Model Settings UI is intended for local visibility and demonstration.

Its role is to help users understand:

- which provider is active
- which providers are supported
- whether the backend provider configuration is healthy
- which model is configured
- whether the current setup is local/demo-oriented

It should not be treated as a production settings administration panel yet.

A future production-ready provider settings experience would require:

- authentication
- authorization
- user or tenant isolation
- encrypted secret storage
- audit logs
- controlled update workflows
- provider usage policies
- role-based access control

## Secrets Management Strategy

### Current local strategy

For local development:

- use `.env`
- keep `.env` out of Git
- document supported variables in `.env.example`
- prefer `fake` provider by default
- use `ollama` for local real-model demos
- use `openai` only when explicitly configured

### Future production strategy

For production-like deployment, secrets should be managed through a dedicated secret management mechanism.

Possible options include:

- cloud provider secret managers
- container orchestration secrets
- encrypted environment variables in deployment platforms
- dedicated vault systems

Production secrets should support:

- rotation
- least-privilege access
- auditability
- environment isolation
- revocation
- separation between application runtime and source code

## Environment Strategy

### Local

Recommended local defaults:

```env
APP_ENV=local
LLM_PROVIDER=fake
STORAGE_BACKEND=local_jsonl
```

Local development may optionally use:

```env
LLM_PROVIDER=ollama
```

or:

```env
LLM_PROVIDER=openai
```

when the developer intentionally configures an API key.

### Test and CI

Recommended test and CI defaults:

```env
APP_ENV=test
LLM_PROVIDER=fake
STORAGE_BACKEND=memory
```

or controlled local JSONL storage when persistence behavior is under test.

Tests should not require external provider credentials by default.

### Future Staging

A future staging environment may use:

- hosted LLM provider
- managed secrets
- persistent database storage
- persistent vector storage
- authentication
- audit logs
- external monitoring

### Future Production

A future production environment should require:

- managed secret storage
- authentication and authorization
- multi-user or tenant isolation
- provider access policies
- provider cost controls
- prompt and tool safety controls
- observability and monitoring
- auditability for sensitive operations

## Cost and Usage Considerations

Provider configuration has cost implications.

External hosted providers may generate cost based on:

- input tokens
- output tokens
- model selection
- retries
- fallback calls
- agent tool loops
- multi-agent workflows
- evaluation runs

The project already tracks usage and cost estimates, but provider billing reconciliation is not implemented.

Current cost tracking should be treated as:

- useful for local analysis
- useful for telemetry
- useful for portfolio demonstration
- not a replacement for provider billing systems

Future provider configuration should support:

- cost limits
- model usage policies
- maximum tokens
- maximum retries
- per-environment provider restrictions
- per-user or per-tenant usage controls

## Security Risks

Provider configuration introduces several risks.

### Secret leakage

Risk:

- API keys may be accidentally exposed through code, logs, frontend payloads or documentation.

Mitigation:

- never commit secrets
- never expose secrets to frontend
- redact sensitive values from logs
- keep `.env.example` secret-free
- use managed secrets in production

### Accidental paid provider usage

Risk:

- local or CI workflows may accidentally call a paid provider.

Mitigation:

- default to `fake`
- require explicit provider selection
- use deterministic tests by default
- avoid external providers in CI unless explicitly configured

### Unsafe provider switching

Risk:

- workflows may behave differently across providers.

Mitigation:

- expose provider diagnostics
- keep structured output validation
- run regression evaluations
- compare outputs through evaluation suites
- document provider-specific behavior

### Prompt and data exposure

Risk:

- sensitive prompts, requirements, documents or table data may be sent to external providers.

Mitigation:

- clearly distinguish local and hosted providers
- document provider behavior
- add sensitive data handling policies
- add future prompt injection and data leakage protections
- avoid using sensitive real data in local demos

### Frontend configuration exposure

Risk:

- frontend settings screens may expose configuration that should remain server-side.

Mitigation:

- expose only safe metadata
- keep credentials backend-only
- avoid frontend secret input until authentication and secure storage exist
- document settings UI limitations

## Logging and Redaction Rules

Provider-related logs should never include:

- API keys
- bearer tokens
- authorization headers
- raw secret values
- full credential objects

Logs may include:

- provider name
- model name
- request status
- duration
- error category
- retry count
- fallback count
- token usage
- estimated cost
- run ID
- component name
- operation name

Any future logging expansion should include redaction rules before adding more provider metadata.

## Governance Rules

The following governance rules apply to provider configuration:

1. The backend is the source of truth for provider configuration.
2. Provider credentials must not be sent to the frontend.
3. The default provider should be safe for local development and CI.
4. Hosted providers must be explicitly configured.
5. Provider diagnostics must not leak secrets.
6. Cost and usage telemetry should be collected when possible.
7. Provider-specific behavior should be evaluated through regression suites.
8. Production provider configuration requires authentication, authorization and managed secrets.
9. Provider settings UI must remain read-only/demo-oriented until secure write workflows exist.
10. Sensitive data handling must be defined before using real production data with hosted providers.

## Current Implementation Status

Implemented:

- Provider abstraction
- Fake provider
- Ollama provider
- OpenAI provider
- Environment-based provider selection
- Provider diagnostics
- Provider and Model Settings UI
- Token and cost tracking foundation
- Persistent local usage telemetry
- Evaluation and regression suites

Partially implemented:

- Provider observability
- Provider cost visibility
- Provider health visibility
- Local provider configuration documentation

Not implemented yet:

- Managed secret storage
- Production provider settings administration
- Authentication and authorization
- Multi-user isolation
- Provider access policies
- Provider cost limits
- Sensitive data classification
- Prompt injection protection baseline
- Tool authorization boundaries
- Audit logs for provider configuration changes

## Future Work

Future provider configuration improvements may include:

- dedicated safe provider configuration API
- redacted provider configuration endpoint
- provider policy registry
- per-environment provider allowlist
- per-provider cost limits
- per-provider token limits
- secure provider settings administration
- encrypted secret storage
- audit logs
- provider usage dashboards
- provider comparison evaluations
- Anthropic provider support
- Google Gemini provider support
- Azure OpenAI provider support

## Summary

The provider configuration strategy keeps the project local-first, safe by default and ready for production-oriented evolution.

The current approach is:

```text
safe defaults
  ↓
backend-owned configuration
  ↓
environment-driven provider selection
  ↓
no frontend secrets
  ↓
safe provider diagnostics
  ↓
usage and cost telemetry
  ↓
future managed secrets and governance
```

This allows the AI Quality Command Center to demonstrate realistic provider workflows without exposing credentials or pretending that local demo settings are production-ready security controls.
