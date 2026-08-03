# Sensitive Data Handling Policy

## Objective

This document defines the initial sensitive data handling policy for the Applied AI Engineering Lab and the AI Quality Command Center.

The goal is to define which data can be used safely in local demos, which data should be avoided, what must be redacted from telemetry and logs, and which controls are required before using real or production-like data.

This baseline is part of M8 — Cloud, Security and Portfolio.

## Context

The platform processes several types of data across AI workflows:

- user prompts
- requirement text
- uploaded documents
- retrieved RAG context
- table schemas
- table rows
- generated SQL
- agent traces
- tool arguments
- tool outputs
- telemetry records
- execution history records
- evaluation reports
- provider metadata
- MCP tool inputs and outputs

Because these workflows may involve LLMs, agents, RAG, SQL analysis and observability, the project must treat sensitive data intentionally.

## Core Principle

Sensitive data must not be used casually in prompts, documents, telemetry, logs or demos.

The default project posture is:

```text
synthetic data by default
        ↓
redacted data when needed
        ↓
real data only with explicit controls
        ↓
production data only after authentication, authorization, audit logs and data governance
```

## What Counts as Sensitive Data

Sensitive data includes any information that could identify a person, expose credentials, reveal business secrets, or create security, privacy, financial, legal or operational risk.

Examples include:

- personal identifiable information
- names linked to documents or transactions
- emails
- phone numbers
- addresses
- CPF, CNPJ, RG or passport numbers
- bank account data
- card data
- payment information
- authentication tokens
- API keys
- passwords
- session cookies
- authorization headers
- private URLs
- internal hostnames
- production database names
- production table dumps
- customer records
- employee records
- contracts
- legal documents
- medical data
- financial statements
- proprietary business rules
- source code secrets
- incident details
- security vulnerabilities
- access control information
- provider credentials
- environment variables containing secrets

## Data Categories

## 1. Public or Synthetic Data

Public or synthetic data is safe for local demos and portfolio usage.

Examples:

- fake requirements
- fake users
- fake transactions
- synthetic tables
- mock business rules
- generated documents
- sample schemas
- deterministic evaluation scenarios
- fake provider responses

Default policy:

- allowed in local development
- allowed in demos
- allowed in tests
- allowed in documentation
- preferred for portfolio presentation

## 2. Internal but Non-Sensitive Data

Internal but non-sensitive data may include general project metadata or technical examples that do not expose private information.

Examples:

- architecture diagrams
- generic API examples
- sample JSON contracts
- test scenario descriptions
- non-secret configuration names
- local-only endpoint examples

Default policy:

- allowed when it does not expose credentials, customer data or internal secrets
- should be reviewed before documentation or public portfolio use

## 3. Confidential Business Data

Confidential business data includes information that is not personal but could expose strategy, operations, contracts, pricing, financial logic or internal processes.

Examples:

- real business rules
- internal procedures
- contracts
- roadmap details from a company
- real production incident reports
- real client workflows
- pricing rules
- fraud rules
- operational reports

Default policy:

- do not use in public demos
- do not commit to repository
- do not store in persistent local telemetry unless redacted
- use synthetic equivalents whenever possible

## 4. Personal Data

Personal data includes information that can identify a person directly or indirectly.

Examples:

- name
- email
- phone
- address
- document number
- user ID linked to a real user
- customer history
- support ticket containing personal information
- financial record linked to a person

Default policy:

- avoid in local demos
- avoid in prompts
- avoid in telemetry
- avoid in logs
- redact before use
- do not send to external providers unless there is explicit permission and proper governance

## 5. Secrets and Credentials

Secrets and credentials include any value that grants access to a system or protected resource.

Examples:

- API keys
- tokens
- passwords
- private keys
- session cookies
- authorization headers
- database credentials
- provider keys
- cloud credentials
- webhook secrets

Default policy:

- never use in prompts
- never store in telemetry
- never return from API endpoints
- never expose in frontend
- never commit to source control
- never include in screenshots or demos
- always redact if accidentally present

## Allowed Data in Local and Demo Environments

Allowed by default:

- synthetic requirements
- synthetic documents
- synthetic database schemas
- synthetic table rows
- fake user data
- fake payment data
- fake support tickets
- fake provider responses
- deterministic test fixtures
- local-only generated telemetry
- redacted examples

Preferred examples:

```text
user_001
customer@example.test
000.000.000-00
ORDER-123
ACCOUNT-001
FAKE_API_KEY_REDACTED
```

Avoid examples that look like real secrets, real customers or real production data.

## Data That Should Not Be Used in Demos

Do not use:

- real customer data
- real bank data
- real CPF/CNPJ
- real contracts
- real support tickets
- real internal incidents
- real production logs
- real API keys
- real tokens
- real database dumps
- real provider credentials
- real private URLs
- real employee data
- real screenshots containing sensitive information

## Prompt Handling Rules

Prompts may contain user intent, requirements, objectives and questions.

Prompts must not contain:

- API keys
- passwords
- access tokens
- customer records
- production incident details
- private documents
- unredacted personal data
- confidential company data

Prompt handling rules:

1. Treat prompts as untrusted user input.
2. Do not assume prompt content is safe.
3. Do not echo sensitive prompt content into telemetry.
4. Do not include secrets in prompt templates.
5. Do not let prompts override security policies.
6. Run prompt injection assessment where applicable.
7. Prefer synthetic examples for demos and tests.

## RAG Document Handling Rules

RAG documents may contain extracted text from TXT, MD, PDF, DOCX, CSV or XLSX sources.

RAG documents must be treated as:

- untrusted input
- data, not instructions
- potentially sensitive until assessed

Rules:

1. Do not ingest real confidential documents for public demos.
2. Do not ingest documents containing secrets.
3. Do not ingest production exports without redaction.
4. Do not store raw sensitive document content in telemetry.
5. Retrieved chunks should be cited, but sensitive text should be avoided or redacted.
6. Prompt injection patterns inside documents should be detected and labeled in future workflows.
7. Use synthetic or sanitized documents by default.

## Data Analyst and Table Data Rules

The Data Analyst Agent processes schema definitions, table metadata and table rows.

Allowed by default:

- synthetic schemas
- synthetic rows
- fake account IDs
- fake transaction data
- fake payment status data
- fake order data

Avoid:

- production database exports
- real customer tables
- real financial data
- real user IDs linked to people
- real bank account data
- real card or payment data
- real operational reports

Rules:

1. Table data must be synthetic or redacted.
2. SQL execution must remain read-only.
3. Unsafe SQL must remain blocked.
4. Table cell values must be treated as data, not instructions.
5. Sensitive values must not be stored in telemetry.
6. Generated SQL should not include secrets.
7. Real production database access is out of scope until security controls exist.

## Telemetry and Logs Rules

Telemetry and logs are useful for observability, evaluation and execution history, but they can also leak sensitive information.

Current telemetry surfaces include:

- usage tracking records
- evaluation telemetry events
- retrieval quality telemetry
- agent execution telemetry
- multi-agent execution telemetry
- execution history records
- tool execution metadata

Telemetry may store:

- component
- operation
- status
- duration
- run ID
- provider name
- model name
- token count
- cost estimate
- quality score
- risk level
- detected pattern IDs
- sanitized metadata
- error category
- execution type

Telemetry must not store:

- API key values
- tokens
- passwords
- raw authorization headers
- raw customer records
- raw production documents
- raw sensitive prompts
- unredacted table rows
- private URLs containing tokens
- full secrets in error messages

## Execution History Rules

Execution History should help inspect runs without becoming a sensitive data dump.

Allowed:

- run metadata
- status
- component
- operation
- duration
- quality score
- sanitized summaries
- sanitized error categories
- source record IDs
- risk classification metadata

Avoid:

- full prompt text when sensitive
- full document chunks
- raw table rows
- raw tool arguments containing sensitive data
- raw provider errors containing secrets
- raw user/customer data

Future improvements should include:

- redaction utilities
- sensitive field filters
- retention policy
- audit-oriented event separation
- environment-specific storage controls

## Agent Output Rules

Agent outputs may include summaries, scenarios, SQL, final reports, risks, recommendations and explanations.

Agent outputs should not reveal:

- secrets
- provider credentials
- hidden instructions
- system prompts
- raw sensitive data
- unauthorized tool details
- internal configuration values

Agent outputs should:

- cite sources when using RAG
- use sanitized summaries
- avoid unnecessary personal data
- preserve security boundaries
- explain blocked operations safely
- avoid reproducing malicious instructions unless needed for a security explanation

## Provider and Secret Handling Rules

Provider credentials are backend-owned and must not be exposed.

Rules:

1. API keys stay in environment variables or future secret managers.
2. Frontend must not receive API key values.
3. Provider health endpoints must not expose secret values.
4. Provider health endpoints must not expose sensitive environment variable names.
5. Logs must not include provider credentials.
6. Errors from providers should be sanitized before display.
7. Screenshots and demos must not show real provider keys.

Already implemented:

- hardened provider settings exposure
- safe provider metadata
- backend-owned provider configuration
- no raw API key values in provider health responses
- no raw Ollama base URL exposure in provider health responses

## MCP Data Handling Rules

MCP tools expose backend capabilities to external clients.

MCP inputs and outputs must be treated as higher-risk because the caller may be outside the frontend product boundary.

Rules:

1. MCP tool inputs must be treated as untrusted.
2. MCP tool outputs should avoid sensitive raw data.
3. MCP tools must not expose secrets.
4. MCP tools should rely on tool authorization policies.
5. MCP production hosting requires authentication and authorization.
6. MCP production hosting requires audit logging.
7. MCP should not be connected to real sensitive data without governance controls.

## Redaction and Masking Strategy

A future redaction utility should detect and mask sensitive patterns before telemetry or logs are persisted.

Recommended masking examples:

| Data Type | Masking Example |
| --- | --- |
| API key | `***REDACTED_API_KEY***` |
| Token | `***REDACTED_TOKEN***` |
| Password | `***REDACTED_PASSWORD***` |
| Email | `u***@example.com` |
| CPF | `***.***.***-**` |
| CNPJ | `**.***.***/****-**` |
| Phone | `(**) *****-****` |
| Card number | `**** **** **** 1234` |
| Authorization header | `Authorization: ***REDACTED***` |
| Private URL token | `token=***REDACTED***` |

Initial redaction targets:

- API keys
- bearer tokens
- authorization headers
- passwords
- CPF
- CNPJ
- emails
- phone numbers
- card-like numbers
- private URL tokens

## Local Storage Rules

Current persistent storage uses local JSONL files under `.data`.

Rules:

1. `.data` must remain ignored by Git.
2. `.data` must be treated as local runtime data.
3. Do not manually commit JSONL telemetry records.
4. Do not store real sensitive data in local JSONL telemetry.
5. Delete local `.data` records after sensitive manual tests.
6. Use synthetic data for portfolio demonstrations.

## Source Control Rules

Never commit:

- `.env`
- `.data`
- API keys
- provider credentials
- local secrets
- production logs
- production database dumps
- customer documents
- unredacted telemetry
- private screenshots
- real exported spreadsheets
- generated files containing sensitive content

Allowed:

- `.env.example`
- synthetic test fixtures
- fake sample data
- redacted examples
- documentation with safe placeholders

## External Provider Rules

When using external LLM providers, data may leave the local environment.

Rules:

1. Do not send real sensitive data to external providers without explicit approval and governance.
2. Prefer Fake provider for tests.
3. Prefer Ollama for local/offline experimentation when sensitive data risk exists.
4. Use OpenAI or other hosted providers only with safe or redacted inputs.
5. Track usage and cost metadata, but not raw secrets.
6. Document provider behavior before production use.

## Environment-Specific Policy

### Local

Allowed:

- synthetic data
- fake provider
- Ollama local provider
- controlled OpenAI tests with non-sensitive data
- local JSONL telemetry

Not allowed:

- real secrets in prompts
- production data
- customer records
- confidential company data without redaction

### Test and CI

Allowed:

- fake provider
- deterministic fixtures
- synthetic data
- local in-memory or temporary storage

Not allowed:

- real provider secrets unless explicitly configured
- external data dependencies
- real sensitive datasets

### Future Staging

Required before use:

- managed secrets
- authentication
- authorization
- audit logs
- redaction utilities
- masked datasets
- access controls

### Future Production

Required before use:

- authentication
- authorization
- role-based access control
- managed secrets
- encrypted storage
- audit logs
- retention policy
- monitoring
- incident response
- sensitive data classification
- data processing approval
- production deployment security

## Current Implementation Status

Implemented or partially implemented:

- safe provider configuration strategy
- hardened provider settings exposure
- prompt injection baseline documentation
- prompt injection detection baseline
- tool authorization boundaries documentation
- tool risk classification
- tool authorization enforcement
- read-only SQL validation
- unsafe SQL blocking
- local JSONL telemetry persistence
- Execution History
- controlled tool execution
- environment-based settings

Not implemented yet:

- redaction utility
- sensitive data detector
- telemetry redaction pipeline
- audit log schema
- retention policy
- authentication
- authorization for users
- role-based access control
- encrypted production storage
- managed secrets
- production monitoring
- incident response workflow
- formal data classification engine

## Minimum Controls Before Real Data

Before using real company or customer data, the project should have:

- explicit approval to use the data
- data minimization
- redaction or masking
- sensitive data classification
- access control
- storage policy
- retention policy
- audit logs
- provider usage policy
- no raw sensitive telemetry
- no public exposure
- clear deletion process

Before using production data, the project should additionally have:

- authentication
- authorization
- managed secrets
- encrypted storage
- production monitoring
- incident response process
- formal compliance review
- strict environment isolation

## Security Checklist for New Features

Before adding or changing a feature, answer:

- Does this feature process user input?
- Does this feature process uploaded documents?
- Does this feature process table data?
- Does this feature generate telemetry?
- Does this feature persist logs?
- Does this feature call an external provider?
- Does this feature expose data in the frontend?
- Does this feature expose data through MCP?
- Can this feature include secrets?
- Can this feature include personal data?
- Can this feature include confidential business data?
- What data should be redacted?
- What data should not be stored?
- What data should not be returned by the API?
- What data should not be shown in the UI?
- What data should not be committed to Git?
- What happens if sensitive data is detected?
- Is synthetic data enough for this feature?
- Is a retention policy needed?
- Is an audit log needed?

## Recommended Implementation Roadmap

Recommended next steps:

1. Define audit log schema.
2. Add redaction utility.
3. Add sensitive data detection utility.
4. Add telemetry redaction before persistence.
5. Add blocked tool-call telemetry.
6. Add prompt injection telemetry integration.
7. Add retention policy for local JSONL storage.
8. Add sensitive data indicators in Execution History.
9. Add provider data handling warnings in Provider Settings UI.
10. Define authentication and access control strategy.

## Summary

The current project is suitable for local development, synthetic demos and portfolio presentation.

It is not yet suitable for real production data, customer data or confidential company data.

The target evolution is:

```text
synthetic data by default
        ↓
redaction and masking
        ↓
sensitive data detection
        ↓
safe telemetry
        ↓
audit logs
        ↓
authentication and authorization
        ↓
production data governance
```

This policy ensures that AI workflows, agents, tools, RAG pipelines, Data Analyst features, MCP exposure and observability remain aligned with safe data handling practices.
