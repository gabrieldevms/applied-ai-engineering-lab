# M4 — AI Agents Module Review

## Purpose

M4 introduces the AI Agents layer of the Applied AI Engineering Lab.

The goal of this module is to move beyond direct LLM calls and build controlled, observable and testable agent workflows.

This module focuses on agent execution for software quality scenarios, especially QA workflows involving requirement analysis, RAG-based answers, tool usage, approval, safety and evaluation.

## Current Status

Status: completed

The M4 module is now functionally complete and validated with automated tests and local API checks.

Validated locally:

```text
229 tests passed
GET  /health
GET  /agents/tools
POST /agents/execute
GET  /agents/logs
POST /agents/evaluate
POST /agents/qa/run
```

## What M4 Delivers

M4 delivers a complete agent execution foundation composed of the following capabilities:

```text
Agent Runtime
Agent Schemas
Agent Execution Trace
Tool Registry
Tool Execution Service
Tool Calling
RAG Retrieval Tool
Requirement Analysis Tool
RAG Answer Tool
QA Agent
Agent Planning with LLM
Automatic Tool Selection
Multi-step Agent Execution
Memory and Execution State
Human Approval Flow
Persistent Agent Execution Logs
Agent Safety Limits
Agent Evaluation
```

## High-level Workflow

The main multi-step execution flow is:

```text
User objective
  ↓
Agent planning
  ↓
Automatic tool selection
  ↓
Human approval policy
  ↓
Safety policy
  ↓
Controlled tool execution
  ↓
Agent runtime trace
  ↓
Execution state snapshot
  ↓
Persistent execution logs
  ↓
Deterministic agent evaluation
  ↓
Final agent response
```

## Architecture Overview

The M4 module is organized around small and explicit services.

```text
AgentPlanningService
  Generates a structured plan from an objective.

AgentToolSelectionService
  Converts plan steps into executable tool calls.

AgentApprovalService
  Applies approval rules before tools can run.

AgentSafetyService
  Applies execution boundaries and safety limits.

AgentRuntime
  Executes controlled workflow steps and tool calls.

ToolExecutionService
  Executes registered tools through explicit handlers.

AgentStateService
  Records execution state snapshots.

AgentExecutionLogService
  Records persistent execution events.

AgentEvaluationService
  Evaluates the quality of an agent execution.
```

## Main API Endpoints

### Agent execution

```http
POST /agents/execute
```

Runs the full multi-step agent workflow.

This endpoint coordinates planning, tool selection, approval, safety, runtime execution, state recording, execution logs and evaluation.

### QA Agent

```http
POST /agents/qa/run
```

Runs a specialized QA Agent workflow.

This is useful for software quality scenarios involving requirements, context documents and QA-oriented analysis.

### Tool registry

```http
GET /agents/tools
```

Lists registered tools available to agents.

### Tool execution

```http
POST /agents/tools/execute
```

Executes a registered tool directly.

### Execution logs

```http
GET /agents/logs
GET /agents/logs/{run_id}
```

Lists persisted agent execution log events.

### Agent evaluation

```http
POST /agents/evaluate
```

Evaluates an agent execution using deterministic quality checks.

## Registered Tools

The current registered tools are:

| Tool | Purpose |
| --- | --- |
| `rag.retrieve` | Retrieve relevant document chunks from a query |
| `requirements.analyze` | Analyze software requirements and generate QA outputs |
| `rag.answer` | Generate a grounded RAG answer from retrieved context |

## Agent Runtime

The Agent Runtime is responsible for executing the controlled workflow.

It records explicit execution steps, including:

```text
understand_objective
inspect_context
tool_call:<tool_name>
produce_final_answer
```

Each step has a status, input, output and metadata.

This makes the workflow traceable and testable.

## Tool Registry

The Tool Registry defines which tools are available to the agent.

Each tool includes:

```text
name
description
category
input schema
output schema
metadata
safety information
LLM requirement information
```

This prevents the agent from calling arbitrary tools.

Only registered tools can be selected and executed.

## Tool Execution Service

The Tool Execution Service executes registered tools through explicit handlers.

Current handlers include:

```text
RAGRetrieveTool
RequirementAnalysisTool
RAGAnswerTool
```

This keeps tool execution controlled and predictable.

## Agent Planning with LLM

The planning service uses an LLM provider to generate a structured plan.

The plan includes:

```text
summary
steps
step objective
tool name
tool arguments
rationale
```

The planner is guided by the registered tool schemas so it can produce arguments compatible with each tool.

The system supports multiple LLM providers through the existing LLM abstraction layer.

Current providers include:

```text
FakeLLMProvider
OllamaProvider
OpenAIProvider
```

## Automatic Tool Selection

The tool selection service converts plan steps into executable tool calls.

It validates:

```text
whether the tool exists
whether the tool has a handler
whether the selected step can be executed
```

Steps without executable tools are skipped with explicit reasons.

## Human Approval Flow

The approval layer applies a policy before execution.

The approval policy can:

```text
require approval for specific tools
reject specific tools
auto-approve safe tools
attach approval metadata
```

Approval decisions are returned in the response and are also included in execution metadata.

Possible approval statuses:

```text
approved
rejected
pending
not_required
```

Tools with pending or rejected approval are not executed.

## Safety Limits

The safety layer applies execution boundaries after approval and before runtime execution.

The safety policy can control:

```text
maximum selected tool calls
maximum executable tool calls
blocked tools
whether LLM-based tools are allowed
```

Safety violations are returned in the response.

Possible safety statuses:

```text
passed
blocked
```

Blocked tools are filtered out before runtime execution.

## Execution State

The execution state service records a snapshot of each agent run.

The state includes:

```text
state id
run id
objective
status
current step
total steps
completed steps
failed steps
skipped steps
tool calls
metadata
```

This provides a compact state representation for each workflow execution.

## Persistent Execution Logs

Execution logs are stored as JSONL events.

The current local path is:

```text
.data/agent-execution-logs.jsonl
```

The log store supports:

```text
append event
list events
list events by run id
count events
```

Current log events include:

```text
plan_generated
tools_selected
approval_evaluated
safety_evaluated
runtime_completed
runtime_failed
state_recorded
evaluation_completed
```

The current implementation stores logs locally as JSONL files.

This is useful for local auditability and future observability work.

## Agent Evaluation

The evaluation layer checks the quality of the execution using deterministic rules.

Current evaluation metrics:

| Metric | Purpose |
| --- | --- |
| `traceability` | Checks whether steps, state and logs exist |
| `completion` | Checks whether the agent run completed successfully |
| `safety` | Checks whether safety checks passed |
| `approval_control` | Checks whether selected tools have approval decisions |
| `objective_alignment` | Checks whether the run objective matches the requested objective |

Possible evaluation statuses:

```text
passed
warning
failed
```

The evaluation response includes:

```text
overall score
metric-level scores
metric statuses
messages
metadata
```

## QA Agent

The QA Agent is a specialized agent workflow focused on quality engineering scenarios.

It can coordinate existing capabilities such as:

```text
requirement analysis
RAG retrieval
RAG answer generation
structured QA output
```

This is the first domain-specific agent in the project.

## Why This Module Matters

M4 is important because it turns the project from a collection of AI endpoints into a controlled agent platform.

The project now has the foundations required for real agent engineering:

```text
explicit runtime
controlled tool use
schema-driven planning
approval gates
safety boundaries
execution state
persistent logs
deterministic evaluation
test coverage
```

This is directly connected to AI Quality Engineering because agent behavior can now be inspected, tested, constrained and evaluated.

## Current Limitations

The current implementation is still a technical prototype.

Known limitations:

```text
approval is policy-based and synchronous
there is no external approval UI yet
execution logs are stored locally as JSONL files
there is no production database for execution history yet
evaluation is deterministic and rule-based
tool execution is limited to the current registered tools
there is no authentication or user management yet
there is no deployed frontend yet
```

These limitations are expected at this stage.

The module is designed as a learning-focused and portfolio-ready foundation, not as a production SaaS product.

## Suggested Next Steps

After M4, the recommended roadmap is:

```text
M4 Final Review
  ↓
File ingestion expansion
  ↓
Data Analyst Agent foundation
  ↓
M5 MCP QA Server
```

## File Ingestion Expansion

The next practical improvement is to expand document ingestion.

Target file types:

```text
PDF
DOCX
Excel / spreadsheets
CSV
Markdown
Plain text
```

This will make RAG and agent workflows more useful with real-world documents.

## Data Analyst Agent Foundation

A future Data Analyst Agent can work with the QA Agent to support database-oriented validation.

Target capabilities:

```text
understand database schemas
generate SQL from natural language
explain generated SQL
execute read-only queries
validate business rules against data
support QA evidence generation
```

Example future workflow:

```text
QA Agent receives a test scenario
  ↓
QA Agent identifies a required database validation
  ↓
Data Analyst Agent receives the validation objective
  ↓
Data Analyst Agent generates a SQL query
  ↓
Query is reviewed and executed in read-only mode
  ↓
Results are returned as QA evidence
  ↓
QA Agent consolidates the validation output
```

## M4 Conclusion

M4 establishes the core agent engineering layer of the project.

The project now has a strong foundation for:

```text
AI agents
tool calling
controlled execution
human approval
safety
observability
evaluation
QA-oriented AI workflows
```

This module is a major milestone for the Applied AI Engineering Lab and provides the foundation for more advanced applied AI systems.