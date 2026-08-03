# Demonstration Scenarios

## Objective

This document describes practical demonstration scenarios for the Applied AI Engineering Lab and the AI Quality Command Center.

The goal is to show how the platform can execute AI-powered quality workflows, collect telemetry, persist observability signals, expose execution history and support operational inspection through a frontend product experience.

## Demonstration Scope

The current demo is designed for local execution.

It demonstrates:

- AI Quality Command Center frontend
- FastAPI backend
- QA Agent Console
- Multi-Agent QA Copilot Console
- RAG Console
- Data Analyst Console
- Usage and cost visualization
- Risk and recommendation panels
- Execution History
- Execution run details
- Live Observability Dashboard behavior

## Prerequisites

Start the backend API:

```powershell
uv run uvicorn ai_api.main:app --reload --app-dir apps/api/src
```

Start the frontend:

```powershell
cd apps\web
npm run dev
```

Open the frontend in the browser using the local Vite URL.

## Recommended Demo Flow

The recommended end-to-end demonstration flow is:

```text
Open AI Quality Command Center
  ↓
Run one or more AI consoles
  ↓
Inspect the generated result
  ↓
Confirm telemetry registration
  ↓
Open Execution History
  ↓
Inspect run details
  ↓
Open Observability Center
  ↓
Refresh or enable auto-refresh
  ↓
Show updated risks, recommendations and observability signals
```

## Scenario 1 — RAG Grounded Answer With Citations

### Goal

Demonstrate document-based retrieval, grounded answer generation and retrieval quality telemetry.

### Steps

1. Open **RAG Console**.
2. Keep the default banking/debt renegotiation documents or provide custom documents.
3. Click **Retrieve context**.
4. Inspect retrieved chunks and similarity scores.
5. Click **Generate answer**.
6. Inspect the grounded answer, citations and context chunks.
7. Confirm the telemetry status message is displayed.
8. Open **Execution History**.
9. Filter by `retrieval_quality`.
10. Select the RAG execution and inspect run details.

### What to Highlight

- Temporary document indexing
- Context retrieval
- Source citations
- Retrieval quality signals
- Persisted telemetry
- Execution History drill-down

### Expected Outcome

The demo should show that a RAG execution can produce a grounded answer with citations and generate retrieval quality telemetry that appears in Execution History.

---

## Scenario 2 — QA Agent Requirement Analysis

### Goal

Demonstrate how the QA Agent supports quality analysis from a requirement-like input.

### Steps

1. Open **QA Agent Console**.
2. Use the default requirement or provide a custom requirement.
3. Run the QA Agent.
4. Inspect the final answer.
5. Inspect requirement analysis, retrieved context, data validation selection and execution steps.
6. Confirm the telemetry status message is displayed.
7. Open **Execution History**.
8. Filter by `agent_execution`.
9. Select the QA Agent execution and inspect run details.

### What to Highlight

- Agent execution trace
- Tool usage
- Requirement analysis
- QA-oriented reasoning
- Agent execution telemetry
- Operational run details

### Expected Outcome

The demo should show that the QA Agent can execute a controlled workflow and register agent execution telemetry for later inspection.

---

## Scenario 3 — Data Analyst Agent SQL Validation

### Goal

Demonstrate controlled natural-language-to-SQL analysis with read-only safety validation and result evidence.

### Steps

1. Open **Data Analyst Console**.
2. Use the default database schema and table data.
3. Run the Data Analyst Agent.
4. Inspect the generated SQL.
5. Inspect SQL safety validation.
6. Inspect returned rows and evidence.
7. Confirm the telemetry status message is displayed.
8. Open **Execution History**.
9. Filter by `agent_execution`.
10. Select the Data Analyst execution and inspect run details.

### What to Highlight

- Natural-language analytics workflow
- SQL generation
- Read-only SQL validation
- Controlled in-memory SQLite execution
- Result evidence
- Agent telemetry integration

### Expected Outcome

The demo should show that the Data Analyst Agent can transform a natural-language objective into a safe SQL workflow and produce inspectable execution evidence.

---

## Scenario 4 — Multi-Agent QA Copilot Report

### Goal

Demonstrate a multi-agent quality workflow that coordinates multiple roles and produces a final QA report.

### Steps

1. Open **Multi-Agent QA Copilot Console**.
2. Use the default requirement or provide a custom requirement.
3. Run the Multi-Agent QA Copilot.
4. Inspect the final report.
5. Inspect roles, task results, artifacts, trace and contract validation.
6. Confirm the telemetry status message is displayed.
7. Open **Execution History**.
8. Filter by `multi_agent_execution`.
9. Select the multi-agent execution and inspect run details.

### What to Highlight

- Multi-agent orchestration
- Role-based task execution
- Shared artifacts
- Execution trace
- Contract validation
- Multi-agent telemetry
- Quality gate metadata

### Expected Outcome

The demo should show how specialized agents can collaborate around a QA workflow and produce an observable multi-agent execution.

---

## Scenario 5 — Execution History and Run Details

### Goal

Demonstrate the operational timeline and drill-down experience for persisted telemetry records.

### Steps

1. Open **Execution History**.
2. Review the unified execution timeline.
3. Filter by execution type:
   - `retrieval_quality`
   - `agent_execution`
   - `multi_agent_execution`
   - `usage`
   - `evaluation_telemetry`
4. Select an execution.
5. Inspect:
   - status
   - execution type
   - component
   - operation
   - duration
   - quality score
   - run ID
   - source record ID
   - metadata
6. Clear the selected execution.
7. Change filters and confirm the selection is reset.

### What to Highlight

- Unified read model
- Persisted local telemetry records
- Operational inspection
- Traceability through run IDs and source record IDs
- Metadata visibility

### Expected Outcome

The demo should show that executions are no longer isolated frontend results. They become inspectable operational records.

---

## Scenario 6 — Live Observability Dashboard

### Goal

Demonstrate the Observability Center as a live operational dashboard for AI workflow signals.

### Steps

1. Open **Observability Center**.
2. Review global status, risks and recommendations.
3. Click **Atualizar dashboard**.
4. Confirm the last updated timestamp changes.
5. Enable auto-refresh.
6. Run one of the consoles in another tab or by navigating through the app.
7. Return to Observability Center.
8. Wait for auto-refresh or manually refresh.
9. Confirm updated observability signals.

### What to Highlight

- Dashboard refresh behavior
- Auto-refresh toggle
- Last updated timestamp
- Aggregated risks
- Aggregated recommendations
- Observability from persisted telemetry

### Expected Outcome

The demo should show that the Command Center behaves like a live operational interface instead of a static frontend.

---

## Suggested Presentation Narrative

A concise presentation narrative:

```text
This project started as a FastAPI foundation and evolved into an Applied AI Engineering platform for software quality.

The AI Quality Command Center demonstrates how QA-oriented AI workflows can be executed through a frontend product experience.

Each console runs a specific AI workflow: RAG, QA Agent, Data Analyst Agent or Multi-Agent QA Copilot.

After execution, the frontend registers telemetry into backend observability endpoints.

Telemetry is persisted locally through JSONL storage and then exposed through Execution History and the Observability Dashboard.

This creates an end-to-end loop: execute, observe, inspect, evaluate and improve.
```

## What This Demonstrates Technically

The demo highlights:

- Modular backend architecture
- Provider-independent LLM engineering
- RAG with citations
- Controlled agent workflows
- Multi-agent orchestration
- SQL safety validation
- Evaluation and LLMOps foundation
- Telemetry instrumentation
- Local persistent observability
- Execution history read model
- Frontend product experience for AI quality engineering

## Current Limitations

The current demo is local and portfolio-oriented.

Known limitations:

- No production cloud deployment yet
- No authentication or multi-user isolation yet
- No production database storage yet
- No persistent vector database yet
- No persistent agent state yet
- No external SQL database connectors yet
- No OpenTelemetry, Prometheus or Grafana integration yet
- Provider settings are local/demo-oriented
- Some evaluation datasets are still small and deterministic

## Recommended Demo Order for Interviews or Portfolio Review

For a short demo:

```text
1. Open Overview
2. Run RAG Console
3. Show Execution History
4. Show Run Details
5. Show Observability Center
```

For a complete demo:

```text
1. Open Overview
2. Run RAG Console
3. Run QA Agent Console
4. Run Data Analyst Console
5. Run Multi-Agent QA Copilot Console
6. Show Execution History filters
7. Show Run Details
8. Show Observability Center auto-refresh
9. Show Usage and Cost
10. Show Risk Center
11. Explain roadmap and current limitations
```

## Next Demonstration Improvements

Future improvements may include:

- Demo screenshots
- Demo video script
- Seed script for sample telemetry
- One-command demo setup
- Portfolio README section
- Architecture diagram image exports
- Public technical case study