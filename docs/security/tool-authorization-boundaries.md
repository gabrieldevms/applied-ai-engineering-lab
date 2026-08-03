# Tool Authorization Boundaries

## Objective

This document defines the initial tool authorization boundaries for the Applied AI Engineering Lab and the AI Quality Command Center.

The goal is to document how tools should be classified, who or what can execute them, which risks they introduce and which controls are required before adding higher-risk tool execution capabilities.

This baseline is part of M8 — Cloud, Security and Portfolio.

## Context

The platform currently includes controlled AI workflows that can use tools through backend services, agents and MCP exposure.

Current tool-related components:

- Tool Registry
- Tool Execution Service
- QA Agent
- Data Analyst Agent
- Multi-Agent QA Copilot
- MCP QA Server
- Prompt injection detection baseline
- Agent execution traces
- Observability telemetry
- Execution History

Tool authorization matters because agents and external clients may request tool execution, and future tools may access external systems, databases, repositories, files, CI/CD platforms or production-like environments.

## Core Principle

Tools are capability boundaries.

Every tool must have an explicit purpose, input schema, execution handler, risk level and authorization expectation.

No tool should be executable only because a model or user requested it.

## Current Tool Architecture

Current agent tools:

| Tool | Purpose | Current Risk |
| --- | --- | --- |
| `rag.retrieve` | Retrieve relevant document chunks | Low |
| `requirements.analyze` | Analyze software requirements | Low |
| `rag.answer` | Generate a grounded answer from retrieved context | Low |
| `data_analysis.agent.run` | Run controlled Data Analyst workflow | Medium |

Current MCP tools:

| MCP Tool | Purpose | Current Risk |
| --- | --- | --- |
| `get_project_status` | Return project status metadata | Low |
| `list_agent_tools` | List registered tools | Low |
| `list_specialized_agents` | List specialized agents | Low |
| `analyze_requirement` | Analyze requirement text | Low |
| `retrieve_rag_context` | Retrieve RAG context | Low |
| `answer_with_rag` | Generate grounded answer | Low |
| `run_qa_agent` | Run QA Agent workflow | Medium |
| `run_data_analyst_agent` | Run Data Analyst Agent workflow | Medium |
| `run_sql_regression_suite` | Run deterministic SQL regression suite | Low |
| `run_multi_agent_qa_copilot` | Run Multi-Agent QA Copilot workflow | Medium |

## Tool Registry as a Security Boundary

The Tool Registry is the first boundary for tool execution.

It should define:

- tool name
- tool description
- input schema
- output schema
- whether the tool is executable
- expected handler
- risk classification
- authorization policy
- telemetry expectations
- human approval requirements when applicable

A tool that is not registered must not be executable.

A tool that is registered but has no execution handler must not be executable.

## Tool Execution Service as a Control Point

The Tool Execution Service is the runtime enforcement point.

It should be responsible for:

- validating tool existence
- validating tool inputs
- checking whether the tool is executable
- applying future authorization checks
- applying future risk classification checks
- recording execution metadata
- rejecting unsupported tools
- rejecting unsafe or unauthorized tool calls

Future tool execution should not bypass this service.

## Tool Risk Classification

Tools should be classified by the impact they can have.

### Low Risk

Low-risk tools are read-only, analytical or local-only tools that do not change external state and do not access sensitive systems.

Examples:

- retrieve local context
- analyze a requirement
- generate a grounded answer
- list available tools
- run deterministic local evaluations

Expected controls:

- schema validation
- telemetry when relevant
- no human approval required by default
- no external state change

### Medium Risk

Medium-risk tools may perform more complex workflows, generate executable artifacts, run controlled queries or combine multiple internal capabilities.

Examples:

- run QA Agent
- run Data Analyst Agent
- run Multi-Agent QA Copilot
- generate SQL candidates
- execute read-only SQL in controlled local SQLite

Expected controls:

- schema validation
- execution trace
- telemetry
- read-only constraints when data access exists
- prompt injection assessment for user-provided text
- human approval optional depending on environment

### High Risk

High-risk tools may access external systems, secrets, production data, repositories, CI/CD pipelines, file systems, write APIs or state-changing operations.

Examples of future high-risk tools:

- create or update GitHub issues
- open or update pull requests
- write files
- execute shell commands
- call external business APIs
- access production databases
- send emails or messages
- deploy applications
- modify CI/CD configuration
- update provider settings
- manage secrets

Expected controls:

- authentication
- authorization
- audit logs
- explicit allowlists
- human approval
- environment restrictions
- sensitive data handling
- prompt injection checks
- rollback or recovery strategy when applicable

### Critical Risk

Critical-risk tools may alter production systems, secrets, billing, access control, infrastructure or customer-impacting data.

Examples of future critical tools:

- rotate or expose secrets
- change authentication settings
- deploy to production
- delete production data
- update billing configuration
- modify user permissions
- execute arbitrary commands in production

Expected controls:

- strong authentication
- role-based authorization
- mandatory human approval
- audit logs
- environment lock
- least privilege
- emergency stop strategy
- production change management

## Tool Categories

### Read-Only Analytical Tools

Tools that only read or analyze data.

Examples:

- `requirements.analyze`
- `rag.retrieve`
- `rag.answer`
- `get_project_status`
- `list_agent_tools`
- `list_specialized_agents`

Baseline rule:

- allowed in local and test environments
- no state change
- no approval required by default

### Controlled Execution Tools

Tools that execute internal workflows but remain bounded.

Examples:

- `run_qa_agent`
- `run_data_analyst_agent`
- `run_multi_agent_qa_copilot`
- `data_analysis.agent.run`

Baseline rule:

- allowed locally
- telemetry required
- execution trace required
- prompt injection assessment recommended
- human approval may be required in shared or production-like environments

### Data Access Tools

Tools that query structured or unstructured data.

Examples:

- RAG retrieval
- Data Analyst Agent
- SQL regression suite

Baseline rule:

- read-only by default
- schema validation required
- unsafe SQL must be blocked
- sensitive data policy required before real production data

### External Action Tools

Tools that call external APIs or trigger side effects.

Examples of future tools:

- GitHub issue creation
- Slack notification
- email sending
- CI/CD trigger
- cloud deployment action

Baseline rule:

- not allowed without explicit authorization design
- human approval required at first
- audit logs required
- environment allowlist required

### State-Changing Tools

Tools that modify data, files, repositories, workflows or configuration.

Examples of future tools:

- update database records
- write files
- update provider configuration
- change project settings
- create commits
- modify PRs

Baseline rule:

- blocked by default until authorization policies exist
- must require audit logs
- must define rollback expectations
- must define actor identity

## Authorization Model

The project should evolve toward a policy-based authorization model.

A future tool policy may include:

```text
tool_name
risk_level
allowed_environments
allowed_callers
requires_authentication
requires_human_approval
requires_audit_log
allows_external_network
allows_state_change
allows_sensitive_data
```

## Caller Types

Possible caller types:

- frontend console
- backend internal service
- QA Agent
- Data Analyst Agent
- Multi-Agent QA Copilot
- MCP client
- evaluation runner
- CI pipeline
- future authenticated user
- future admin user

Different callers may have different permissions.

For example:

| Caller | Default Permission |
| --- | --- |
| Frontend console | Execute approved local workflows |
| Backend service | Execute internal tools |
| QA Agent | Execute QA-approved tools |
| Data Analyst Agent | Execute controlled data tools |
| Multi-Agent QA Copilot | Execute bounded workflow tools |
| MCP client | Execute explicitly exposed MCP tools |
| CI pipeline | Execute deterministic evaluations |
| Future admin | Manage sensitive settings only with audit |

## Environment Boundaries

### Local

Local environment may allow low and medium-risk tools for development and portfolio demonstration.

Recommended local policy:

- allow read-only analytical tools
- allow controlled workflow tools
- allow controlled local SQLite execution
- block high-risk external action tools by default
- avoid sensitive real data

### Test and CI

Test and CI should only run deterministic and safe tools.

Recommended CI policy:

- allow Fake provider
- allow deterministic evaluation tools
- allow local-only tests
- block external provider dependencies by default
- block external action tools
- block tools that require secrets unless explicitly configured

### Future Staging

Future staging may allow selected external tools with authentication and audit logs.

Recommended staging policy:

- allow low and medium-risk tools
- allow selected high-risk tools with approval
- require managed secrets
- require audit logs
- require non-sensitive datasets or masked data

### Future Production

Future production should use strict authorization.

Recommended production policy:

- allow only explicitly approved tools
- require authentication
- require authorization
- require audit logs
- require human approval for high-risk and critical tools
- require sensitive data handling
- require production monitoring

## Human Approval

Human approval should be required when a tool can:

- change external state
- access sensitive data
- trigger cost-heavy operations
- call external systems
- affect users or customers
- modify files, repositories or deployments
- update provider settings
- execute high-risk or critical actions

Current status:

- human approval flow exists as a foundation
- tool-level approval policy is not fully implemented yet

Future implementation should support:

- approval reason
- approver identity
- tool name
- tool arguments summary
- risk level
- timestamp
- run ID
- approval decision
- audit log record

## Audit Logging Expectations

Tool execution should eventually produce audit logs when tools are medium, high or critical risk.

Audit fields may include:

- actor identity
- caller type
- tool name
- risk level
- environment
- run ID
- request ID
- timestamp
- action result
- approval status
- blocked status
- sanitized arguments summary
- error category

Audit logs should avoid storing secrets or sensitive raw payloads.

## Prompt Injection Interaction

Prompt injection protection and tool authorization are related.

A suspicious prompt must not be able to force tool execution.

Baseline rule:

- user input may request a tool
- the agent may consider a tool
- backend policy decides whether the tool is allowed
- tool registry validates existence
- tool authorization validates permission
- tool execution service controls execution

Prompt injection detection should influence:

- risk metadata
- warnings
- approval requirements
- blocking for high-risk tool requests
- telemetry records

## MCP Tool Boundaries

MCP tools expose backend capabilities to external clients.

MCP must be treated as a higher-risk boundary than internal backend calls because the caller may be outside the frontend product experience.

Current MCP status:

- local validation only
- no production hosting
- no authentication
- no authorization

Future MCP deployment should require:

- MCP authentication
- MCP authorization
- per-tool allowlist
- tool risk classification
- audit logs
- environment-specific exposure
- network boundary definition
- prompt injection checks for text inputs

## Current Implementation Status

Implemented:

- Tool Registry
- Tool Execution Service
- explicit execution handlers
- QA Agent tool usage
- Data Analyst Agent tool adapter
- MCP QA Server
- local MCP smoke test
- agent execution traces
- agent safety limits
- human approval flow foundation
- read-only SQL validation
- unsafe SQL blocking
- prompt injection detection baseline
- observability telemetry
- Execution History

Partially implemented:

- tool execution governance through explicit registry and handlers
- tool traceability through agent execution traces
- workflow-level safety through deterministic evaluations
- local-only MCP boundary

Not implemented yet:

- formal tool risk classification in code
- tool authorization policy engine
- per-tool environment allowlist
- per-tool caller permissions
- tool-level audit logs
- mandatory approval for high-risk tools
- MCP authentication
- MCP authorization
- production MCP hosting security
- sensitive data policy for tool inputs
- blocked tool-call telemetry

## Governance Rules

The following rules apply to current and future tool development:

1. A tool must be registered before execution.
2. A tool must have an explicit execution handler before execution.
3. A tool must define input and output schemas.
4. A tool must define its risk level.
5. A tool must define whether it can change state.
6. A tool must define whether it can access external systems.
7. A tool must define whether it can access sensitive data.
8. A tool must define whether human approval is required.
9. A tool must define telemetry expectations.
10. High-risk tools must not be introduced without audit log planning.
11. Critical-risk tools must not be introduced without authentication and authorization.
12. MCP-exposed tools must define an explicit external boundary.
13. Prompt injection must not be allowed to override tool policy.
14. User requests alone do not authorize tool execution.
15. Model outputs alone do not authorize tool execution.

## Security Checklist for New Tools

Before adding a new tool, answer:

- What is the tool name?
- What does it do?
- Who or what can call it?
- Can it change state?
- Can it access external systems?
- Can it access sensitive data?
- Can it generate cost?
- Can it modify files, repositories, databases or deployments?
- Does it need authentication?
- Does it need authorization?
- Does it need human approval?
- Does it need audit logs?
- Does it need telemetry?
- Can it be safely tested locally?
- Can it run in CI?
- Can it run with Fake provider?
- Can prompt injection influence it?
- What should happen if the tool is blocked?
- What should be redacted from logs?
- What is the rollback strategy if it changes state?

## Recommended Implementation Roadmap

Recommended next steps:

1. Add tool risk classification to tool schemas.
2. Add allowed caller metadata to tool definitions.
3. Add environment allowlist metadata to tool definitions.
4. Add authorization metadata to the Tool Registry.
5. Add tool authorization checks to the Tool Execution Service.
6. Add blocked tool-call telemetry.
7. Add audit log schema for tool execution.
8. Add MCP tool authorization policy.
9. Add human approval requirements for high-risk tools.
10. Add tests for tool authorization boundaries.

## Summary

The current project already has an important tool safety foundation: explicit registry, explicit handlers, controlled execution, SQL safety and execution traces.

The next step is to formalize tool risk classification and authorization checks.

The target evolution is:

```text
registered tools
  ↓
explicit execution handlers
  ↓
risk classification
  ↓
caller and environment policy
  ↓
authorization checks
  ↓
human approval for risky tools
  ↓
audit logs
  ↓
production-safe tool execution
```

This ensures that agents, MCP clients and future external integrations can use tools safely without allowing user prompts or model outputs to bypass backend policies.
