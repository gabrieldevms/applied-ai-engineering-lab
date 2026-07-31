# M7 — Evaluation and LLMOps Review

## Overview

M7 introduced the evaluation and observability foundation for the Applied AI Engineering Lab.

Until the previous modules, the project had already evolved from a basic AI API into a system with LLM provider abstraction, RAG capabilities, controlled agents, a Data Analyst Agent, an MCP QA Server and a Multi-Agent QA Copilot.

M7 changed the nature of the project again.

The system is no longer only capable of executing AI workflows. It can now evaluate, monitor, summarize and reason about the quality, reliability and operational behavior of those workflows.

This milestone adds the foundation for AI Quality Engineering and LLMOps.

## Goal

The goal of M7 is to continuously evaluate, observe and improve the behavior of LLM, RAG, agent and multi-agent components.

The milestone focuses on:

- golden evaluation datasets;
- deterministic regression evaluation;
- prompt regression testing;
- LLM output evaluation;
- RAG regression evaluation;
- agent regression evaluation;
- tool-calling evaluation;
- multi-agent regression evaluation;
- controlled LLM-as-judge evaluation;
- CI evaluation pipeline;
- structured telemetry;
- token usage tracking;
- cost tracking;
- latency tracking;
- error and fallback tracking;
- retrieval quality metrics;
- agent execution metrics;
- multi-agent execution metrics;
- backend observability dashboard.

## Why This Module Matters

Many AI applications can produce impressive outputs in isolated demos.

However, production-oriented AI systems require more than model calls. They need repeatable evaluation, regression safety, visibility into failures, measurable quality signals and a way to decide whether a workflow is reliable enough to be used.

M7 addresses this problem by introducing engineering mechanisms to answer questions such as:

- Are AI outputs still matching expected quality criteria?
- Did a prompt change break an expected behavior?
- Is the RAG workflow retrieving enough useful context?
- Are citations and sources being produced as expected?
- Are agents completing their tasks reliably?
- Are tools being selected and called correctly?
- Are multi-agent workflows producing complete artifacts and reports?
- Are failures, warnings and fallbacks visible?
- How many tokens are being used?
- What is the estimated cost of AI execution?
- Which areas of the system are healthy, warning or critical?

This is the point where the project starts to behave like an AI engineering platform rather than a collection of AI features.

## Main Capabilities Delivered

M7 delivered a complete evaluation and observability foundation.

Implemented capabilities include:

- Golden Evaluation Dataset;
- Golden Evaluation Dataset Runner;
- Prompt Regression Evaluation;
- AI Evaluation Report Aggregation;
- Evaluation Telemetry Foundation;
- Latency and Error Telemetry Instrumentation;
- LLM Output Evaluation Suite;
- RAG Regression Evaluation Suite;
- Agent Regression Evaluation Suite;
- Tool-calling Evaluation Suite;
- Multi-Agent QA Copilot Regression Evaluation;
- LLM-as-judge Evaluation Prototype;
- CI Evaluation Pipeline;
- Token and Cost Usage Tracking;
- Retrieval Quality Telemetry Metrics;
- Agent Execution Telemetry Metrics;
- Multi-Agent Execution Telemetry Metrics;
- AI Observability Dashboard.

## Evaluation Architecture

M7 organizes evaluation around deterministic and repeatable checks.

The evaluation architecture is based on:

```text
Golden scenarios
      ↓
Evaluation runners
      ↓
Deterministic checks
      ↓
Evaluation results
      ↓
Report aggregation
      ↓
CI evaluation pipeline
      ↓
Telemetry and observability
```

This design keeps evaluation explicit, testable and easy to extend.

The project avoids relying only on subjective model judgment. Instead, most evaluations are based on structured expectations, metadata, trace integrity, output markers, tool usage and quality gates.

The LLM-as-judge capability exists as a controlled prototype, not as the only source of truth.

## Golden Evaluation Dataset

The Golden Evaluation Dataset defines representative scenarios used to evaluate AI workflows.

It provides a controlled foundation for checking whether the system still behaves as expected across multiple AI capabilities.

The dataset includes scenarios for:

- requirement analysis;
- RAG answer generation;
- QA Agent execution;
- Data Analyst Agent execution;
- Multi-Agent QA Copilot execution;
- MCP project status discovery.

The dataset includes scenario metadata, expected outputs and validation rules.

This makes it possible to evaluate important AI behaviors without manually inspecting every response.

## Golden Evaluation Dataset Runner

The dataset runner executes golden scenarios and validates their outputs against defined expectations.

It supports:

- running all scenarios;
- filtering by scenario ID;
- filtering by scenario type;
- dry-run execution;
- status checks;
- quality gate checks;
- output marker checks;
- metadata key checks;
- scenario-level results;
- dataset-level status.

The runner creates a repeatable evaluation mechanism that can be used locally or inside CI.

## Prompt Regression Evaluation

Prompt regression evaluation checks whether prompt-driven workflows continue to produce expected structured behavior.

This is important because prompt changes can silently break output format, tone, completeness or schema alignment.

The prompt regression foundation includes:

- prompt regression suite definition;
- deterministic prompt output checks;
- suite execution;
- API endpoints for retrieving and running the suite.

This creates a safety net for prompt evolution.

## AI Evaluation Report Aggregation

The AI Evaluation Report Aggregation capability consolidates multiple evaluation results into a unified AI quality report.

It aggregates signals from:

- Golden Evaluation Dataset Runner;
- Prompt Regression Evaluation;
- Multi-Agent QA Copilot Evaluation.

The aggregated report includes:

- report status;
- score;
- sections;
- highlights;
- risks;
- metrics;
- recommendations.

This provides a higher-level view of AI quality instead of requiring each evaluation result to be interpreted in isolation.

## LLM Output Evaluation Suite

The LLM Output Evaluation Suite validates structured model outputs.

It focuses on whether LLM responses satisfy expected quality and formatting requirements.

The suite includes checks for:

- structured output presence;
- required sections;
- metadata;
- expected markers;
- quality status;
- deterministic validation rules.

This helps protect the project against regressions in model output behavior.

## RAG Regression Evaluation Suite

The RAG Regression Evaluation Suite validates retrieval and grounded-answer behavior.

It focuses on whether RAG workflows continue to retrieve useful context and produce grounded responses.

The suite includes checks for:

- retrieved chunks;
- grounded answer structure;
- citations;
- metadata;
- expected answer markers;
- retrieval-related quality expectations.

This is important because RAG systems can fail silently when retrieval quality decreases, documents change or citation behavior breaks.

## Agent Regression Evaluation Suite

The Agent Regression Evaluation Suite validates controlled agent behavior.

It focuses on whether agents produce expected outputs, traces and metadata.

The suite includes checks for:

- agent artifacts;
- execution traces;
- step integrity;
- metadata;
- quality gates;
- expected output markers.

This supports regression testing for agentic workflows.

## Tool-calling Evaluation Suite

The Tool-calling Evaluation Suite validates tool selection and tool-use behavior.

It focuses on whether agents are selecting appropriate tools and avoiding forbidden tools.

The suite includes checks for:

- selected tools;
- expected tools;
- forbidden tools;
- tool arguments;
- tool call metadata;
- deterministic validation.

This is especially important because tool use introduces operational risk. A model may produce plausible reasoning while selecting the wrong tool or using incorrect arguments.

## Multi-Agent QA Copilot Regression Evaluation

The Multi-Agent QA Copilot Regression Evaluation validates the complete multi-agent workflow.

It checks whether the copilot produces the expected structure, trace, contracts, artifacts and report output.

The suite validates:

- role coverage;
- artifacts;
- trace integrity;
- task results;
- communication contracts;
- conflicts;
- final report sections;
- data validation evidence.

This ensures that the Multi-Agent QA Copilot remains reliable as orchestration evolves.

## LLM-as-judge Evaluation Prototype

The LLM-as-judge prototype introduces controlled model-based evaluation.

It is intentionally treated as a prototype and not as the only evaluation mechanism.

The implementation includes:

- judge suite definition;
- rubric items;
- structured judge outputs;
- judge expectations;
- deterministic validation checks;
- telemetry instrumentation.

The main design principle is that LLM-as-judge should be used as an additional quality signal, not as an uncontrolled replacement for deterministic validation.

## CI Evaluation Pipeline

The CI Evaluation Pipeline runs a deterministic AI evaluation workflow as part of engineering quality control.

The pipeline includes stages for:

- golden dataset smoke validation;
- prompt regression;
- LLM output evaluation;
- RAG regression;
- agent regression;
- tool-calling evaluation;
- Multi-Agent QA Copilot regression;
- controlled LLM-as-judge evaluation.

The pipeline calculates an overall status and determines whether the CI should fail.

This brings AI evaluation closer to standard software engineering practices.

The pipeline naming intentionally avoids internal milestone-specific naming. Runtime-facing scripts and GitHub Actions labels use generic AI Evaluation Pipeline naming instead of M7-specific names.

## Structured AI Execution Telemetry

M7 introduced structured telemetry for AI execution events.

Telemetry records provide a normalized way to track execution behavior across evaluation and AI workflows.

The telemetry foundation supports:

- event recording;
- event listing;
- summary generation;
- status tracking;
- score metadata;
- duration metadata;
- error metadata.

This creates the basis for observing AI behavior over time.

## Latency and Error Telemetry Instrumentation

Evaluation flows were instrumented with latency and error tracking.

Instrumentation captures:

- start time;
- finish time;
- duration in milliseconds;
- success status;
- warning status;
- failure status;
- score extraction;
- error type;
- error message.

Instrumented flows include:

- Golden Evaluation Dataset Runner;
- Prompt Regression Evaluation;
- AI Evaluation Report Aggregation;
- Multi-Agent QA Copilot Evaluation;
- LLM Output Evaluation;
- RAG Regression Evaluation;
- Agent Regression Evaluation;
- Tool-calling Evaluation;
- Multi-Agent QA Copilot Regression;
- LLM-as-judge Evaluation;
- CI Evaluation Pipeline.

This allows evaluation workflows to be monitored as executable system behaviors, not just as isolated test results.

## Token and Cost Usage Tracking

M7 introduced token usage and cost tracking for AI observability.

Usage records include:

- provider;
- model name;
- component;
- operation;
- prompt tokens;
- completion tokens;
- embedding tokens;
- total tokens;
- input token cost;
- output token cost;
- embedding token cost;
- total estimated cost;
- currency;
- run ID;
- trace ID;
- metadata.

The implementation intentionally does not hardcode provider pricing.

Pricing is caller-provided because provider prices can change over time. This avoids stale assumptions and keeps cost estimation explicit.

The usage summary aggregates:

- total prompt tokens;
- total completion tokens;
- total embedding tokens;
- total tokens;
- total estimated cost;
- average cost;
- provider coverage;
- model coverage;
- component coverage;
- operation coverage;
- risks.

This provides the foundation for cost visibility across AI workflows.

## Retrieval Quality Telemetry Metrics

M7 introduced retrieval quality metrics for RAG and context retrieval workflows.

Retrieval quality records include:

- query;
- requested top-k;
- retrieved chunks count;
- relevant chunks count;
- citation count;
- unique source count;
- required source count;
- matched required source count;
- similarity scores;
- precision at k;
- source coverage score;
- quality score;
- risks.

The service calculates:

- precision at k;
- source coverage score;
- retrieval quality score;
- section status;
- quality risks.

This makes it possible to detect weak retrieval behavior before it becomes a user-facing hallucination or incomplete answer.

## Agent Execution Telemetry Metrics

M7 introduced agent execution metrics for single-agent workflows.

Agent execution records include:

- agent name;
- operation;
- run status;
- duration;
- step counts;
- successful and failed steps;
- tool call counts;
- successful and failed tool calls;
- retries;
- fallbacks;
- errors;
- human approval requests;
- human approvals granted;
- step success rate;
- tool success rate;
- human approval rate;
- quality score;
- risks.

The service calculates execution quality from available signals.

Human approval rate is only included when approval was actually requested. This avoids penalizing agents for workflows that did not require human approval.

This telemetry helps identify whether agent workflows are stable, failing, retrying too often, depending on fallback behavior or requiring unexpected human intervention.

## Multi-Agent Execution Telemetry Metrics

M7 introduced multi-agent execution metrics for orchestrated workflows.

Multi-agent execution records include:

- workflow name;
- run status;
- duration;
- agent counts;
- completed agents;
- failed agents;
- skipped agents;
- task counts;
- successful and failed tasks;
- artifact counts;
- handoff counts;
- failed handoffs;
- contract checks;
- passed and failed contract checks;
- conflicts;
- critical conflicts;
- failures;
- errors;
- final report sections;
- data validation evidence;
- retries;
- fallbacks;
- quality score;
- risks.

The service calculates:

- agent success rate;
- task success rate;
- handoff success rate;
- contract success rate;
- artifact coverage score;
- final report coverage score;
- data validation evidence score;
- overall quality score.

This provides visibility into the reliability of the Multi-Agent QA Copilot and future orchestrated AI workflows.

## AI Observability Dashboard

M7 introduced a backend AI Observability Dashboard.

The dashboard is a consolidated read model for observability data.

It summarizes:

- structured AI execution telemetry;
- token and cost usage;
- retrieval quality metrics;
- agent execution metrics;
- multi-agent execution metrics.

The dashboard returns:

- global status;
- generated timestamp;
- section-level statuses;
- section metrics;
- section risks;
- section recommendations;
- global risks;
- global recommendations;
- dashboard metadata.

Dashboard statuses include:

- `healthy`;
- `warning`;
- `critical`;
- `empty`.

The dashboard intentionally does not implement a full frontend UI in M7.

Instead, it creates the backend response contract that can later support a portfolio-grade frontend experience.

## Future Frontend Direction

The planned frontend direction is the AI Quality Command Center.

The M7 dashboard is the backend foundation for that future interface.

A future frontend may include:

- AI Quality overview;
- Evaluation Center;
- Observability Center;
- QA Agent Console;
- Multi-Agent QA Copilot Console;
- RAG Console;
- Data Analyst Agent Console;
- Provider and model configuration;
- cost and usage views;
- quality gate visualization;
- risk and recommendation panels.

This frontend direction is intentionally deferred to the next milestone so that the UI can be built on top of real backend capabilities instead of becoming a decorative interface.

The current architectural decision is:

```text
M7:
Backend observability dashboard contract

M8:
Frontend AI Quality Command Center
```

## Main API Endpoints Added

### Golden Dataset

```text
GET  /evals/golden-dataset
GET  /evals/golden-dataset/validation
POST /evals/golden-dataset/validate
POST /evals/golden-dataset/run
```

### Prompt Regression

```text
GET  /evals/prompt-regression/suite
POST /evals/prompt-regression/run
```

### Evaluation Reports

```text
POST /evals/reports/aggregate
```

### Evaluation Telemetry

```text
POST /evals/telemetry/events
GET  /evals/telemetry/events
POST /evals/telemetry/summary
GET  /evals/telemetry/summary
```

### LLM Output Evaluation

```text
GET  /evals/llm-output/suite
POST /evals/llm-output/run
```

### RAG Regression Evaluation

```text
GET  /evals/rag-regression/suite
POST /evals/rag-regression/run
```

### Agent Regression Evaluation

```text
GET  /evals/agent-regression/suite
POST /evals/agent-regression/run
```

### Tool-calling Evaluation

```text
GET  /evals/tool-calling/suite
POST /evals/tool-calling/run
```

### Multi-Agent QA Copilot Regression

```text
GET  /evals/multi-agent-copilot-regression/suite
POST /evals/multi-agent-copilot-regression/run
```

### LLM-as-judge Evaluation

```text
GET  /evals/llm-as-judge/suite
POST /evals/llm-as-judge/run
```

### CI Evaluation Pipeline

```text
POST /evals/ci/pipeline/run
```

### Usage Tracking

```text
POST /observability/usage/records
GET  /observability/usage/records
POST /observability/usage/summary
GET  /observability/usage/summary
```

### Retrieval Quality

```text
POST /observability/retrieval-quality/records
GET  /observability/retrieval-quality/records
POST /observability/retrieval-quality/summary
GET  /observability/retrieval-quality/summary
```

### Agent Execution Metrics

```text
POST /observability/agent-execution/records
GET  /observability/agent-execution/records
POST /observability/agent-execution/summary
GET  /observability/agent-execution/summary
```

### Multi-Agent Execution Metrics

```text
POST /observability/multi-agent-execution/records
GET  /observability/multi-agent-execution/records
POST /observability/multi-agent-execution/summary
GET  /observability/multi-agent-execution/summary
```

### Observability Dashboard

```text
GET /observability/dashboard
```

## Validation Strategy

M7 continued the same development style used throughout the project:

```text
Define schemas
      ↓
Create services
      ↓
Add deterministic tests
      ↓
Expose API endpoints
      ↓
Validate with Swagger
      ↓
Update documentation
```

The tests cover:

- schema validation;
- service behavior;
- summary aggregation;
- risk detection;
- API responses;
- dependency injection;
- endpoint validation;
- deterministic evaluation behavior;
- telemetry instrumentation;
- dashboard aggregation.

## Design Principles

M7 follows the same architectural principles established in earlier modules.

### Explicit Contracts

Every evaluation and telemetry capability is represented through explicit Pydantic schemas.

This keeps data contracts visible and testable.

### Deterministic First

Most evaluation logic is deterministic.

This avoids depending on subjective model output for every quality decision.

### LLM-as-judge as a Controlled Signal

LLM-as-judge is included as a prototype, but it is not the only source of quality validation.

Its output is structured and validated.

### Observability as a Product Capability

Telemetry, usage tracking, quality metrics and dashboard summaries are treated as first-class product capabilities.

They are not just logs.

### No Hidden Provider Coupling

Cost tracking does not hardcode provider prices.

LLM providers remain behind the existing abstraction.

### Backend Before Frontend

The observability dashboard is implemented first as a backend read model.

This creates a reliable contract for the future AI Quality Command Center frontend.

## What This Module Proves

M7 demonstrates that the project can support AI quality and LLMOps concerns such as:

- regression testing for AI behavior;
- repeatable evaluation scenarios;
- prompt regression safety;
- RAG quality checks;
- agent quality checks;
- tool-call validation;
- multi-agent workflow evaluation;
- controlled LLM-as-judge evaluation;
- CI-based AI quality gates;
- structured execution telemetry;
- token and cost tracking;
- latency and error tracking;
- retrieval quality metrics;
- agent execution metrics;
- multi-agent execution metrics;
- consolidated observability dashboard.

This is a major step toward building reliable AI systems rather than only AI demos.

## Current Limitations

The M7 implementation is still intentionally lightweight and local-first.

Current limitations include:

- evaluation datasets are still small and deterministic;
- telemetry storage is currently in-memory for most observability records;
- execution logs are still local JSONL files in some agent flows;
- token and cost tracking depends on caller-provided pricing data;
- cost calculation is an estimate, not provider billing reconciliation;
- retrieval quality metrics depend on caller-provided relevance and similarity signals;
- observability dashboard is backend-only;
- dashboard output is not yet connected to a persistent database;
- there is not yet a dedicated frontend;
- OpenTelemetry, Grafana and external monitoring integrations are not implemented yet;
- production authentication and authorization are not implemented yet;
- multi-user isolation is not implemented yet.

These limitations are acceptable for this stage and define the boundary between the current engineering foundation and future production hardening.

## Next Direction

After M7, the next milestone can focus on cloud, security, portfolio presentation and frontend experience.

A natural next direction is to evolve the project into an AI Quality Command Center.

Potential next steps include:

- frontend architecture;
- dashboard UI;
- evaluation run visualization;
- observability charts;
- agent console;
- Multi-Agent QA Copilot console;
- RAG console;
- Data Analyst Agent console;
- provider settings;
- authentication and authorization;
- deployment strategy;
- cloud-ready configuration;
- persistent observability storage;
- production monitoring integrations.

## Final Assessment

M7 is one of the most important milestones in the project so far.

It transforms the lab from an AI execution system into an AI quality and observability platform foundation.

The project now has enough structure to support serious discussions around:

- AI Engineering;
- Quality Engineering for AI systems;
- LLMOps;
- agent observability;
- RAG evaluation;
- prompt regression;
- AI CI/CD;
- multi-agent reliability;
- portfolio-grade AI platform architecture.

The key architectural achievement is that quality is no longer only something tested manually after execution.

Quality is now represented as data, contracts, metrics, summaries, risks, recommendations and CI gates.

That is the foundation for building reliable AI systems.
