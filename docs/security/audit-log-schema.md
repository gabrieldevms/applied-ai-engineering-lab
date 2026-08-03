# Audit Log Schema

## Objective

This document defines the initial audit log schema for the Applied AI Engineering Lab and the AI Quality Command Center.

The goal is to define which events should become audit records, how audit logs differ from telemetry and Execution History, which fields should be captured, and which redaction rules must be applied before implementing audit logging in code.

This baseline is part of M8 — Cloud, Security and Portfolio.

## Context

The platform already includes:

- persistent observability telemetry
- Execution History
- prompt injection detection
- tool risk classification
- tool authorization enforcement
- sensitive data handling policy
- provider configuration hardening
- human approval flow foundation
- agent execution traces
- MCP tools

Audit logging is the next governance layer.

Telemetry helps understand system behavior.

Execution History helps inspect AI workflow runs.

Audit logs should explain security-relevant decisions and sensitive actions.

## Audit Logs vs Telemetry vs Execution History

## Telemetry

Telemetry is operational and quality-oriented.

Examples:

- duration
- status
- token usage
- cost estimate
- quality score
- retrieval quality
- agent step count
- error count
- execution metrics

Telemetry answers:

```text
What happened operationally?
How long did it take?
Was it successful?
How much did it cost?
Was the quality acceptable?
```

## Execution History

Execution History is a user-facing or operator-facing run timeline.

Examples:

- execution type
- component
- operation
- run ID
- status
- summary
- quality score
- duration
- metadata

Execution History answers:

```text
Which workflow ran?
When did it run?
What was the result?
What details can be inspected?
```

## Audit Logs

Audit logs are security and governance-oriented.

Examples:

- tool authorization allowed or blocked
- prompt injection detected
- high-risk tool requested
- human approval requested
- human approval granted or rejected
- sensitive data detected
- provider configuration accessed
- MCP tool called
- policy violation detected

Audit logs answer:

```text
Who or what attempted an action?
Was it allowed or blocked?
Which policy applied?
Was approval required?
Was sensitive data involved?
Can this action be reviewed later?
```

## Core Principle

Audit logs must record security-relevant decisions without storing secrets or unnecessary raw sensitive data.

The default posture is:

```text
record the decision
        ↓
record the policy
        ↓
record the actor/caller
        ↓
record sanitized metadata
        ↓
avoid raw sensitive payloads
        ↓
preserve reviewability
```

## Events That Should Generate Audit Logs

Audit logs should be generated for:

- blocked tool execution
- allowed medium, high or critical-risk tool execution
- high prompt injection risk detection
- prompt injection blocking decisions
- human approval requested
- human approval granted
- human approval rejected
- sensitive data detection
- provider configuration status access
- provider configuration changes in the future
- MCP tool execution
- authentication events in the future
- authorization failures in the future
- production or staging tool execution in the future
- state-changing tool execution in the future
- external action tool execution in the future
- audit policy changes in the future

## Events That Usually Do Not Need Audit Logs

Low-risk local events may not need audit logs by default.

Examples:

- regular low-risk RAG retrieval in local environment
- deterministic evaluation execution in CI
- fake provider test execution
- local synthetic demo run
- read-only frontend navigation

However, they may still generate telemetry or Execution History records.

## Audit Event Types

Recommended initial event types:

```text
tool_authorization_allowed
tool_authorization_blocked
tool_execution_started
tool_execution_completed
tool_execution_failed
prompt_injection_detected
prompt_injection_blocked
human_approval_requested
human_approval_granted
human_approval_rejected
sensitive_data_detected
provider_configuration_accessed
provider_configuration_changed
mcp_tool_called
mcp_tool_blocked
authentication_succeeded
authentication_failed
authorization_failed
policy_violation_detected
```

Not all event types need to be implemented immediately.

## Audit Event Severity

Recommended severity levels:

```text
info
warning
high
critical
```

Suggested mapping:

| Severity | Meaning |
| --- | --- |
| `info` | Expected security-relevant event |
| `warning` | Suspicious or policy-relevant event |
| `high` | Blocked action, high-risk input or approval-related event |
| `critical` | Production-impacting, secret-related or destructive action |

## Base Audit Event Schema

A future audit event should follow this base structure:

```json
{
  "audit_event_id": "audit-event-...",
  "event_type": "tool_authorization_blocked",
  "severity": "high",
  "status": "blocked",
  "occurred_at": "2026-08-03T18:30:00Z",
  "component": "agent_tool_execution",
  "operation": "execute_tool",
  "environment": "local",
  "actor": {
    "actor_type": "system",
    "actor_id": "backend_service",
    "display_name": "Backend Service"
  },
  "caller": {
    "caller_type": "qa_agent",
    "caller_id": "qa-agent-v1"
  },
  "target": {
    "target_type": "tool",
    "target_id": "requirements.analyze",
    "target_name": "requirements.analyze"
  },
  "run_context": {
    "run_id": "agent-run-...",
    "trace_id": "trace-...",
    "request_id": "request-...",
    "session_id": null
  },
  "policy": {
    "policy_name": "tool-authorization-policy-v1",
    "policy_version": "v1",
    "decision": "blocked",
    "reason": "Tool execution is blocked by authorization policy.",
    "violations": [
      "Tool is not allowed in environment=production."
    ]
  },
  "risk": {
    "risk_level": "medium",
    "risk_reasons": [
      "Tool can process sensitive table data."
    ],
    "prompt_injection_risk_level": "none",
    "sensitive_data_detected": false
  },
  "metadata": {
    "tool_category": "qa",
    "authorization_enforced": true
  },
  "redaction": {
    "redacted": true,
    "redacted_fields": [
      "arguments.requirement_text"
    ]
  }
}
```

## Required Fields

Initial required fields:

| Field | Description |
| --- | --- |
| `audit_event_id` | Unique audit event identifier |
| `event_type` | Security-relevant event type |
| `severity` | Event severity |
| `status` | Event result |
| `occurred_at` | Timestamp in UTC |
| `component` | System component |
| `operation` | Operation being audited |
| `environment` | Runtime environment |
| `actor` | Actor responsible for the action |
| `caller` | Caller that triggered the action |
| `target` | Target resource or tool |
| `policy` | Policy decision and reason |
| `metadata` | Sanitized extra metadata |
| `redaction` | Redaction summary |

## Status Values

Recommended status values:

```text
allowed
blocked
completed
failed
requested
granted
rejected
detected
redacted
```

## Actor Schema

The actor represents who or what is responsible for the action.

```json
{
  "actor_type": "system",
  "actor_id": "backend_service",
  "display_name": "Backend Service"
}
```

Possible actor types:

```text
system
frontend_user
backend_service
agent
mcp_client
ci_pipeline
future_authenticated_user
future_admin_user
```

Current local implementation may use mostly:

```text
system
backend_service
agent
mcp_client
ci_pipeline
```

Future production implementation should use authenticated user identity.

## Caller Schema

The caller represents the execution source.

```json
{
  "caller_type": "qa_agent",
  "caller_id": "qa-agent-v1"
}
```

Possible caller types should align with tool authorization metadata:

- `frontend_console`
- `backend_service`
- `qa_agent`
- `data_analyst_agent`
- `multi_agent_copilot`
- `mcp_client`
- `evaluation_runner`
- `ci_pipeline`
- `future_authenticated_user`
- `future_admin_user`

## Target Schema

The target represents what the audited action affected.

```json
{
  "target_type": "tool",
  "target_id": "data_analysis.agent.run",
  "target_name": "data_analysis.agent.run"
}
```

Possible target types:

```text
tool
agent
workflow
provider
mcp_tool
document
dataset
policy
configuration
approval_request
```

## Run Context Schema

The run context connects the audit event to workflow execution.

```json
{
  "run_id": "agent-run-...",
  "trace_id": "trace-...",
  "request_id": "request-...",
  "session_id": null
}
```

Current implementation may not have all IDs available.

Rules:

1. Use `run_id` when available.
2. Use `trace_id` when available.
3. Generate `request_id` in future API middleware.
4. Keep nullable fields when not available.
5. Do not store raw sensitive input as a run context field.

## Policy Schema

The policy block explains the decision.

```json
{
  "policy_name": "tool-authorization-policy-v1",
  "policy_version": "v1",
  "decision": "blocked",
  "reason": "Tool execution is blocked by authorization policy.",
  "violations": [
    "Tool is not allowed for caller_type=future_admin_user."
  ]
}
```

Recommended policy names:

```text
tool-authorization-policy-v1
prompt-injection-policy-v1
sensitive-data-policy-v1
provider-configuration-policy-v1
human-approval-policy-v1
mcp-tool-policy-v1
```

## Risk Schema

The risk block captures security risk context.

```json
{
  "risk_level": "medium",
  "risk_reasons": [
    "Tool can process sensitive table data."
  ],
  "prompt_injection_risk_level": "high",
  "sensitive_data_detected": false
}
```

Possible risk levels:

```text
none
low
medium
high
critical
```

Risk information should use categories and reasons, not raw sensitive values.

## Redaction Schema

The redaction block explains what was removed or masked.

```json
{
  "redacted": true,
  "redacted_fields": [
    "arguments.authorization_header",
    "arguments.api_key",
    "metadata.private_url"
  ]
}
```

Rules:

1. Audit logs must record that redaction happened.
2. Audit logs should not store the original sensitive value.
3. Redacted field paths should be descriptive but safe.
4. Redaction should happen before persistence.

## Tool Authorization Audit Events

## Allowed Tool Authorization

Generate audit logs for:

- medium-risk tool allowed
- high-risk tool allowed
- critical-risk tool allowed
- tool allowed in staging or production
- tool allowed via MCP
- tool allowed with human approval

Example:

```json
{
  "event_type": "tool_authorization_allowed",
  "severity": "info",
  "status": "allowed",
  "component": "agent_tool_execution",
  "operation": "authorize_tool",
  "target": {
    "target_type": "tool",
    "target_id": "data_analysis.agent.run",
    "target_name": "data_analysis.agent.run"
  },
  "policy": {
    "policy_name": "tool-authorization-policy-v1",
    "decision": "allowed",
    "reason": "Tool execution is allowed by authorization policy.",
    "violations": []
  }
}
```

## Blocked Tool Authorization

Generate audit logs for every blocked tool authorization.

Example:

```json
{
  "event_type": "tool_authorization_blocked",
  "severity": "high",
  "status": "blocked",
  "component": "agent_tool_execution",
  "operation": "authorize_tool",
  "target": {
    "target_type": "tool",
    "target_id": "requirements.analyze",
    "target_name": "requirements.analyze"
  },
  "policy": {
    "policy_name": "tool-authorization-policy-v1",
    "decision": "blocked",
    "reason": "Tool execution is blocked by authorization policy.",
    "violations": [
      "Tool is not allowed in environment=production."
    ]
  }
}
```

## Prompt Injection Audit Events

Prompt injection audit logs should be created when:

- risk level is high
- recommended action is block
- suspicious input influences tool authorization
- suspicious input appears in MCP input
- suspicious retrieved context is detected in future RAG workflows

Example:

```json
{
  "event_type": "prompt_injection_detected",
  "severity": "high",
  "status": "detected",
  "component": "security",
  "operation": "prompt_injection_assessment",
  "policy": {
    "policy_name": "prompt-injection-policy-v1",
    "decision": "block",
    "reason": "High-risk prompt injection patterns detected.",
    "violations": [
      "secret_exfiltration_attempt",
      "instruction_override_attempt"
    ]
  },
  "risk": {
    "risk_level": "high",
    "risk_reasons": [
      "Input appears to request secrets, tokens or credentials."
    ],
    "prompt_injection_risk_level": "high",
    "sensitive_data_detected": false
  },
  "redaction": {
    "redacted": true,
    "redacted_fields": [
      "input.text"
    ]
  }
}
```

## Human Approval Audit Events

Audit logs should capture human approval lifecycle events.

Events:

```text
human_approval_requested
human_approval_granted
human_approval_rejected
```

Required fields:

- approval request ID
- tool name or workflow name
- risk level
- requester
- approver when available
- decision
- decision reason
- timestamp
- run ID when available

Example:

```json
{
  "event_type": "human_approval_granted",
  "severity": "high",
  "status": "granted",
  "component": "agent_approval",
  "operation": "approve_tool_execution",
  "target": {
    "target_type": "approval_request",
    "target_id": "approval-...",
    "target_name": "data_analysis.agent.run"
  },
  "policy": {
    "policy_name": "human-approval-policy-v1",
    "decision": "granted",
    "reason": "Human approval granted for medium-risk controlled tool."
  }
}
```

## Sensitive Data Audit Events

Sensitive data audit logs should be created when:

- sensitive data is detected in prompts
- sensitive data is detected in telemetry metadata
- sensitive data is detected in tool arguments
- redaction happens before persistence
- sensitive data causes a blocked operation

Example:

```json
{
  "event_type": "sensitive_data_detected",
  "severity": "warning",
  "status": "detected",
  "component": "security",
  "operation": "sensitive_data_assessment",
  "policy": {
    "policy_name": "sensitive-data-policy-v1",
    "decision": "redacted",
    "reason": "Sensitive data patterns were detected and redacted."
  },
  "risk": {
    "risk_level": "medium",
    "risk_reasons": [
      "Input may contain personal data."
    ],
    "sensitive_data_detected": true
  },
  "redaction": {
    "redacted": true,
    "redacted_fields": [
      "input.email",
      "input.document_number"
    ]
  }
}
```

## Provider Configuration Audit Events

Provider configuration access should be audited when:

- provider health/status is requested in production
- provider configuration is changed in the future
- provider credentials are detected in unsafe locations
- provider error contains sensitive information and is redacted

Current provider settings are read-only and sanitized, but future production use should audit provider configuration operations.

Example:

```json
{
  "event_type": "provider_configuration_accessed",
  "severity": "info",
  "status": "completed",
  "component": "llm_provider",
  "operation": "read_provider_health",
  "target": {
    "target_type": "provider",
    "target_id": "openai",
    "target_name": "openai"
  },
  "policy": {
    "policy_name": "provider-configuration-policy-v1",
    "decision": "allowed",
    "reason": "Provider health metadata was accessed without exposing secrets."
  }
}
```

## MCP Audit Events

MCP audit logs should be generated when:

- MCP tool is called
- MCP tool is blocked
- MCP caller is unauthorized in the future
- MCP input has high prompt injection risk
- MCP tool returns security-relevant errors

Example:

```json
{
  "event_type": "mcp_tool_called",
  "severity": "warning",
  "status": "completed",
  "component": "mcp_server",
  "operation": "run_qa_agent",
  "caller": {
    "caller_type": "mcp_client",
    "caller_id": "local-mcp-client"
  },
  "target": {
    "target_type": "mcp_tool",
    "target_id": "run_qa_agent",
    "target_name": "run_qa_agent"
  },
  "policy": {
    "policy_name": "mcp-tool-policy-v1",
    "decision": "allowed",
    "reason": "MCP tool execution was allowed in local environment."
  }
}
```

## Authentication and Authorization Audit Events

Future authentication and user authorization should generate audit logs.

Events:

```text
authentication_succeeded
authentication_failed
authorization_failed
session_created
session_revoked
role_changed
```

These are not implemented yet, but the schema should support them.

## Redaction Rules

Audit logs must not include:

- API keys
- tokens
- passwords
- authorization headers
- session cookies
- raw customer data
- raw production documents
- unredacted table rows
- full sensitive prompts
- private URLs with tokens
- secrets from provider errors

Audit logs may include:

- detected pattern IDs
- sensitive data categories
- redacted field paths
- policy decision
- risk level
- sanitized summaries
- actor and caller type
- target IDs
- run IDs

## Storage Expectations

Future audit logs should be stored separately from operational telemetry.

Recommended local path:

```text
.data/security/audit-events.jsonl
```

Recommended future production storage:

- append-only storage
- restricted access
- retention policy
- tamper-resistant logs when needed
- encrypted storage
- queryable audit backend
- access-controlled audit UI

## Retention Expectations

Local development:

- short-lived audit data
- safe to delete
- synthetic data only

Future staging:

- defined retention period
- restricted access
- redaction required

Future production:

- formal retention policy
- compliance review
- access control
- secure deletion process
- audit event export if required

## Current Implementation Status

Implemented or partially implemented:

- persistent telemetry storage
- Execution History
- prompt injection detection
- tool risk classification
- tool authorization enforcement
- human approval flow foundation
- provider settings hardening
- sensitive data policy
- local JSONL storage foundation

Not implemented yet:

- audit log schemas in code
- audit log persistence
- audit log service
- audit log API endpoints
- audit log UI
- audit log retention policy
- audit log redaction utility
- sensitive data detector
- blocked tool-call audit logging
- prompt injection audit logging
- human approval audit logging
- MCP audit logging
- authentication audit logging

## Recommended Implementation Roadmap

Recommended next steps:

1. Add audit event schemas in code.
2. Add local JSONL audit event store.
3. Add audit logging service.
4. Record blocked tool authorization events.
5. Record high prompt injection risk events.
6. Record human approval events.
7. Add audit log API endpoint.
8. Add redaction utility before audit persistence.
9. Add sensitive data detection integration.
10. Add audit log UI in the AI Quality Command Center.
11. Add retention policy support.
12. Add production storage strategy.

## Security Checklist for Audit Events

Before adding a new audit event, answer:

- What event type is this?
- Why is it security-relevant?
- Who or what is the actor?
- What is the caller?
- What is the target?
- Which policy applies?
- Was the action allowed or blocked?
- What risk level applies?
- Does this event contain sensitive data?
- What must be redacted?
- Should this event be persisted?
- Should this event appear in Execution History?
- Should this event be visible in a future audit UI?
- Does this event need retention rules?
- Does this event need production access controls?

## Summary

Telemetry explains operational behavior.

Execution History explains workflow runs.

Audit logs explain security-relevant decisions.

The target evolution is:

```text
security-relevant action
        ↓
policy decision
        ↓
sanitized audit event
        ↓
append-only audit storage
        ↓
restricted audit access
        ↓
reviewable governance trail
```

This audit log schema prepares the project for blocked tool-call telemetry, prompt injection audit integration, human approval audit events and production-grade governance.
