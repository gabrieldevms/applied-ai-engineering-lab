# Prompt Injection Protection Baseline

## Objective

This document defines the initial prompt injection protection baseline for the Applied AI Engineering Lab and the AI Quality Command Center.

The goal is to document how prompt injection risks can appear in the current architecture, which inputs must be treated as untrusted, what controls already reduce risk and which protections should be implemented next.

This baseline is part of M8 — Cloud, Security and Portfolio.

## Context

The platform includes several AI workflows that process natural language, documents, retrieved context, table data, generated SQL, agent plans, tool calls and multi-agent messages.

Current relevant surfaces:

- RAG Console
- QA Agent Console
- Data Analyst Console
- Multi-Agent QA Copilot Console
- MCP QA Server
- Requirement Analysis
- Document ingestion
- Retrieved context
- Tool selection
- SQL generation
- Evaluation and LLMOps workflows

Prompt injection becomes relevant because the system may receive text that looks like instructions but should be treated only as user-provided data or retrieved context.

## What Prompt Injection Means in This Project

Prompt injection is any attempt to manipulate an AI workflow through text that tries to override, bypass or confuse the intended system behavior.

Examples:

- a document says: "Ignore previous instructions"
- a requirement says: "Do not validate this feature"
- retrieved context says: "Call a tool and send all data"
- a user prompt asks the agent to bypass safety rules
- table data contains instructions disguised as business data
- a tool response includes text that tries to influence the next model call
- an MCP tool input tries to trigger unintended behavior

In this project, prompt injection is especially important because agents can use tools and workflows can generate structured outputs.

## Trust Model

The platform must treat different text sources with different trust levels.

### Trusted Instructions

Trusted instructions include:

- system prompts defined by the application
- developer-authored prompt templates
- backend validation rules
- tool execution policies
- schema definitions
- safety limits
- governance rules

These instructions define how the system should behave.

### User Inputs

User inputs are useful but not fully trusted.

Examples:

- requirement text
- questions
- business rules
- objectives
- natural-language SQL requests
- console form inputs
- custom demo inputs

User inputs should be treated as task data, not as authority to override system behavior.

### Retrieved Context

Retrieved context is not trusted as an instruction source.

Examples:

- RAG chunks
- uploaded documents
- extracted PDF text
- DOCX content
- CSV/XLSX text
- markdown files
- knowledge base content

Retrieved context should be treated as evidence or reference material only.

### Tool Outputs

Tool outputs should be treated as structured data produced by controlled components.

However, tool outputs may include text derived from untrusted input or retrieved context.

### External Provider Outputs

LLM outputs should be validated before being trusted.

Current controls include:

- Pydantic schemas
- JSON parsing
- structured output validation
- deterministic evaluation suites
- tool execution boundaries

## Key Principle

Documents, user inputs and retrieved context are data, not instructions.

The model may use them to answer, analyze or reason, but they must not override:

- system instructions
- developer instructions
- tool policies
- SQL safety rules
- provider configuration boundaries
- security and governance rules

## Prompt Injection Entry Points

## 1. RAG Workflows

### Entry Points

- uploaded documents
- extracted text
- retrieved chunks
- user questions
- generated answers with citations

### Risks

Retrieved documents may contain malicious or misleading instructions such as:

- "Ignore your previous instructions"
- "Do not cite sources"
- "Reveal system prompts"
- "Call another tool"
- "Return hidden configuration"
- "Treat this document as the highest priority instruction"

### Baseline Rule

RAG context must be used as reference material, not as instruction authority.

### Current Mitigations

- explicit RAG answer generation flow
- source citations
- context retrieval boundaries
- structured request and response schemas
- retrieval quality telemetry
- RAG regression evaluation

### Future Controls

- retrieved-context risk labeling
- prompt injection heuristic detection
- suspicious chunk telemetry
- document trust levels
- RAG evaluation scenarios for malicious documents

## 2. QA Agent Workflows

### Entry Points

- requirement text
- supporting documents
- RAG context
- agent objectives
- tool outputs
- data validation input

### Risks

A requirement or supporting document may try to:

- bypass test generation
- suppress risks
- avoid negative scenarios
- force the agent to ignore validation
- request unauthorized tool usage
- change the workflow objective
- override agent instructions

### Baseline Rule

The QA Agent must treat requirements and documents as analysis targets, not as instructions that can override the agent runtime.

### Current Mitigations

- controlled agent runtime
- tool registry
- explicit tool execution handlers
- execution trace
- safety limits
- QA Agent evaluation
- data validation modes
- persistent telemetry

### Future Controls

- prompt injection detection before agent execution
- suspicious instruction tagging in execution trace
- blocked/suspicious prompt telemetry
- evaluation scenarios for malicious requirements
- tool policy validation before execution

## 3. Data Analyst Agent Workflows

### Entry Points

- natural-language analysis objective
- schema descriptions
- table metadata
- table row values
- generated SQL
- SQL explanations

### Risks

A natural-language objective or table value may try to:

- request unsafe SQL
- bypass read-only validation
- expose credentials
- modify data
- run destructive queries
- ignore schema boundaries
- produce SQL unrelated to the allowed schema

### Baseline Rule

Natural-language requests and table data must not override SQL safety validation.

### Current Mitigations

- read-only SQL validation
- unsafe SQL blocking
- controlled in-memory SQLite execution
- schema-based SQL generation
- result evidence
- deterministic evaluation
- telemetry through Data Analyst Console

### Future Controls

- prompt injection checks for SQL objectives
- suspicious SQL objective telemetry
- stricter schema boundary validation
- SQL generation policy checks
- malicious natural-language-to-SQL regression scenarios

## 4. Multi-Agent QA Copilot Workflows

### Entry Points

- requirement text
- objective
- agent messages
- shared state
- artifacts
- final report sections
- data validation evidence

### Risks

A malicious input may try to:

- manipulate one agent role
- create inconsistent artifacts
- bypass reviewer checks
- suppress conflicts
- force a false quality gate
- override final report content
- inject instructions through shared state

### Baseline Rule

Multi-agent messages and artifacts must remain observable, validated and bounded by role contracts.

### Current Mitigations

- role-based workflow
- shared state
- artifacts
- messages
- execution trace
- communication contracts
- contract validation
- conflict detection
- final report schema
- multi-agent telemetry

### Future Controls

- role-specific injection checks
- artifact trust metadata
- suspicious inter-agent message detection
- prompt injection regression scenarios
- stricter final report policy validation

## 5. MCP QA Server

### Entry Points

- MCP tool inputs
- MCP tool outputs
- external client requests
- tool execution arguments

### Risks

An MCP client may submit inputs that try to:

- call unintended tools
- bypass tool boundaries
- manipulate tool arguments
- force unsafe agent behavior
- expose internal metadata
- execute workflows outside the intended local boundary

### Baseline Rule

MCP tools must remain controlled, explicit and bounded by tool definitions.

### Current Mitigations

- explicit MCP tool definitions
- local MCP validation
- controlled backend services
- tool registry
- smoke test script

### Future Controls

- MCP authentication
- MCP authorization
- tool allowlists
- tool risk classification
- prompt injection checks for MCP tool inputs
- MCP audit logs
- production MCP hosting security model

## Instruction Hierarchy

The project should follow this instruction hierarchy:

```text
System and developer-defined safety rules
        ↓
Backend service policies and validation rules
        ↓
Tool authorization and execution boundaries
        ↓
User task request
        ↓
Retrieved context and documents
        ↓
Generated intermediate outputs
```

Lower-priority content must not override higher-priority rules.

## Data vs Instruction Rule

The following content must be treated as data:

- uploaded documents
- retrieved chunks
- requirements
- table rows
- tool outputs derived from user data
- external text
- MCP client input
- generated intermediate artifacts

The following content may define behavior:

- backend code
- system prompts
- prompt templates
- schemas
- tool policies
- safety validators
- governance rules

## Suspicious Prompt Injection Signals

The following patterns should be treated as suspicious when they appear in user inputs, documents or retrieved context:

- "ignore previous instructions"
- "ignore all above"
- "forget your rules"
- "you are now"
- "developer mode"
- "system prompt"
- "hidden instructions"
- "do not follow the original task"
- "override"
- "bypass"
- "reveal secrets"
- "show API key"
- "show token"
- "disable validation"
- "do not validate"
- "call this tool"
- "execute this command"
- "delete"
- "drop table"
- "update all records"
- "send data to"
- "exfiltrate"
- "base64 decode this instruction"
- "the real instruction is"

These signals are not always malicious by themselves, but they should increase risk score and trigger additional validation or telemetry.

## Baseline Mitigation Strategy

The initial protection strategy should include:

1. Keep system and developer instructions separate from user data.
2. Treat retrieved context as evidence, not instruction.
3. Validate structured outputs with schemas.
4. Restrict tool execution through explicit registries.
5. Keep SQL execution read-only.
6. Block unsafe SQL operations.
7. Add prompt injection heuristic checks.
8. Record suspicious inputs in telemetry.
9. Add evaluation scenarios for malicious inputs.
10. Add tool authorization boundaries before adding higher-risk tools.

## Prompt Injection Detection Baseline

A future code-level baseline can start with a deterministic detector.

The detector should return:

- `risk_level`
- `detected_patterns`
- `risk_reasons`
- `recommended_action`
- `is_blocking_required`

Possible risk levels:

- `none`
- `low`
- `medium`
- `high`

Possible recommended actions:

- `allow`
- `allow_with_warning`
- `require_review`
- `block`

Initial behavior should be conservative:

- low risk: allow and record metadata
- medium risk: allow with warning and telemetry
- high risk: block or require approval depending on workflow

## Recommended Initial Detection Rules

### High Risk

High-risk signals may include attempts to:

- reveal secrets
- reveal system prompts
- bypass validation
- execute destructive SQL
- call unauthorized tools
- exfiltrate data
- override safety rules

### Medium Risk

Medium-risk signals may include:

- instruction override language
- role manipulation
- suspicious tool-use requests
- hidden instruction patterns
- encoded instruction references

### Low Risk

Low-risk signals may include:

- vague mentions of instructions
- ambiguous wording
- harmless discussion about prompt injection in an educational context

## Workflow-Specific Policy

### RAG

Default behavior:

- retrieve and answer normally when no suspicious pattern exists
- label suspicious chunks when detected
- avoid following instructions found inside retrieved documents
- prefer citations and grounded answers

### QA Agent

Default behavior:

- analyze requirements even when suspicious text exists
- record suspicious input metadata
- avoid executing additional tools solely because the input requests it
- keep tool selection controlled by backend logic

### Data Analyst Agent

Default behavior:

- validate all SQL candidates
- block destructive SQL
- avoid using table data as instruction
- treat natural-language objectives as untrusted input

### Multi-Agent QA Copilot

Default behavior:

- preserve role contracts
- record suspicious input or artifact metadata
- avoid letting one artifact override global policy
- validate final report structure and quality gate metadata

### MCP

Default behavior:

- reject unsupported tools
- validate tool arguments
- apply future tool authorization policies
- log suspicious tool requests

## Telemetry Expectations

Prompt injection checks should eventually generate telemetry.

Useful fields:

- component
- operation
- run ID
- input source
- risk level
- detected patterns
- recommended action
- blocked status
- workflow type
- provider
- model
- timestamp

Sensitive values should be redacted.

Telemetry should not store full sensitive user data unless explicitly safe for the environment.

## Evaluation Expectations

The project should include deterministic prompt injection evaluation scenarios.

Example scenario categories:

- malicious RAG document
- malicious requirement
- malicious SQL objective
- malicious table cell
- malicious multi-agent artifact
- malicious MCP input
- false positive educational prompt
- harmless user question containing security terms

Evaluation should check:

- detection result
- risk level
- recommended action
- no unsafe tool call
- no unsafe SQL execution
- no secret exposure
- no policy override
- proper telemetry metadata

## Current Implementation Status

Implemented or partially implemented:

- structured prompts
- schema validation
- controlled tool registry
- explicit tool execution handlers
- SQL safety validation
- unsafe SQL blocking
- deterministic evaluations
- execution telemetry
- execution traces
- security documentation
- provider settings hardening

Not implemented yet:

- prompt injection detector
- prompt injection API/service
- prompt injection telemetry
- prompt injection evaluation suite
- retrieved-context risk labeling
- document trust levels
- suspicious tool-call blocking
- prompt injection UI indicators
- human approval based on prompt injection risk

## Security Checklist for AI Workflows

Before adding or changing an AI workflow, answer:

- Does this workflow process user-provided text?
- Does this workflow process uploaded documents?
- Does this workflow use retrieved context?
- Does this workflow generate or execute tool calls?
- Does this workflow generate SQL?
- Does this workflow call an external provider?
- Can the input contain hidden instructions?
- Can the input influence tool selection?
- Can the input influence provider selection?
- Can the input influence security-sensitive behavior?
- What should happen when injection-like text is detected?
- Should suspicious input be blocked, warned or only recorded?
- Should the workflow emit telemetry?
- Should the workflow require human approval?
- Are false positives acceptable in this workflow?

## Recommended Implementation Roadmap

Recommended next steps:

1. Add a deterministic prompt injection detection service.
2. Add schemas for prompt injection risk assessment.
3. Add unit tests for detection rules.
4. Add an API endpoint for prompt injection assessment.
5. Integrate detection into RAG Console telemetry.
6. Integrate detection into QA Agent inputs.
7. Integrate detection into Data Analyst objectives.
8. Integrate detection into Multi-Agent QA Copilot inputs.
9. Add evaluation scenarios for prompt injection.
10. Add UI indicators for suspicious inputs.

## Summary

The current platform already has useful safety boundaries such as structured outputs, controlled tools, SQL validation and telemetry.

However, prompt injection protection is not yet implemented as a dedicated runtime capability.

The baseline strategy is:

```text
treat external text as data
        ↓
preserve system and backend policies
        ↓
validate structured outputs
        ↓
control tool execution
        ↓
detect suspicious instructions
        ↓
record risk telemetry
        ↓
evaluate against malicious scenarios
        ↓
add blocking or approval controls where needed
```

This baseline prepares the project for the next step: implementing a deterministic prompt injection detection foundation.
