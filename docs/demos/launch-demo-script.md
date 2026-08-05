# AI Quality Command Center — Launch Demo Script

This document provides a guided launch demo script for presenting the AI Quality Command Center as a local-first AI Quality Engineering platform.

The goal of this demo is to show how the project connects LLM engineering, RAG, QA agents, data validation, multi-agent workflows, evaluation, observability and governance into a single product-oriented experience.

## Demo Positioning

The AI Quality Command Center is a local-first platform for applying AI Engineering practices to software quality workflows.

It demonstrates:

- LLM provider abstraction;
- structured requirement analysis;
- RAG-based knowledge retrieval;
- QA agent workflows;
- Data Analyst Agent workflows;
- Multi-Agent QA Copilot orchestration;
- AI evaluation and regression checks;
- observability and execution history;
- usage and cost tracking;
- prompt injection assessment;
- tool authorization;
- audit logging;
- security and governance documentation.

This is not presented as a complete production SaaS product.

It is presented as a production-oriented portfolio project that makes AI system architecture, quality controls, observability and governance explicit.

## Recommended Demo Length

Recommended duration:

- short version: 5 to 7 minutes;
- standard version: 10 to 15 minutes;
- technical deep dive: 25 to 40 minutes.

For LinkedIn or portfolio video, use the short or standard version.

For interviews, technical reviews or architecture discussions, use the technical deep dive.

## Demo Narrative

Use the following narrative:

~~~text
Most AI demos stop at a prompt or chatbot.

This project explores what happens after that:

How do we build AI systems that are structured, testable, observable, auditable and useful for real software quality workflows?
~~~

Then introduce the project:

~~~text
The AI Quality Command Center is a local-first AI Quality Engineering platform.

It combines LLM providers, RAG, QA agents, data validation agents, multi-agent workflows, evaluation, observability and governance in one product experience.
~~~

## Prerequisites

Before starting the demo, make sure the API and frontend are running.

### Start the API

~~~powershell
uv run uvicorn ai_api.main:app --reload --app-dir apps/api/src
~~~

Open:

~~~text
http://127.0.0.1:8000/health
http://127.0.0.1:8000/docs
~~~

### Start the frontend

~~~powershell
cd apps\web
npm run dev
~~~

Open the local Vite URL shown in the terminal.

## Recommended Demo Flow

The recommended flow is:

~~~text
1. Open the AI Quality Command Center
2. Show the product overview
3. Run a RAG workflow
4. Run a QA Agent workflow
5. Run a Data Analyst Agent workflow
6. Run the Multi-Agent QA Copilot
7. Show Execution History
8. Open Run Details
9. Show the Observability Center
10. Show Usage and Cost
11. Show Risk Center
12. Show Provider Settings
13. Show Security/Governance endpoints
14. Close with architecture and roadmap
~~~

## Demo Script

### 1. Open the AI Quality Command Center

Open the frontend.

Suggested explanation:

~~~text
This is the AI Quality Command Center.

It is the product layer of the project, built with React and TypeScript, consuming a FastAPI backend.

The goal is to provide a local interface for AI quality workflows: agents, RAG, evaluations, observability, usage tracking, risk signals and execution history.
~~~

Highlight:

- product-oriented frontend;
- local-first execution;
- backend integration;
- AI quality and observability focus.

### 2. Show the Overview

Open the main overview page.

Suggested explanation:

~~~text
The overview gives a high-level view of the system.

The project is not just a chatbot. It is composed of backend services, AI workflows, evaluation suites, telemetry, execution history and governance controls.
~~~

Mention:

- API foundation;
- LLM providers;
- RAG;
- agents;
- multi-agent workflows;
- evaluation;
- observability;
- governance.

### 3. Run a RAG Workflow

Open the RAG Console.

Suggested input:

~~~text
Question:
What are the main risks of releasing a payment feature without validating boleto generation?

Documents:
A payment feature allows customers to renegotiate debt and generate boletos for payment. The release depends on boleto registration, correct due date calculation, CNAB processing and reconciliation evidence.
~~~

Suggested explanation:

~~~text
This flow demonstrates a RAG-style workflow.

The system retrieves relevant context and generates an answer grounded in the provided documents.

The important point is not only the answer itself, but the structured workflow: extraction, retrieval, answer generation and source-aware reasoning.
~~~

Highlight:

- retrieval;
- grounded answer;
- citations/context;
- retrieval quality telemetry;
- RAG console telemetry integration.

### 4. Run a QA Agent Workflow

Open the QA Agent Console.

Suggested requirement:

~~~text
As a customer, I want to renegotiate an overdue debt and generate a boleto so that I can pay the agreement before the due date.
~~~

Suggested explanation:

~~~text
The QA Agent applies quality engineering reasoning to a software requirement.

It can identify business rules, acceptance criteria, risks, open questions, test scenarios and automation opportunities.
~~~

Highlight:

- requirement analysis;
- QA-focused structured output;
- tool execution;
- execution trace;
- telemetry registration;
- agent observability.

### 5. Run a Data Analyst Agent Workflow

Open the Data Analyst Console.

Suggested explanation:

~~~text
The Data Analyst Agent demonstrates how AI can support data validation workflows.

Instead of allowing arbitrary SQL execution, the project generates structured SQL candidates, validates read-only safety and executes only controlled queries against in-memory SQLite data.
~~~

Suggested natural-language question:

~~~text
Which customers have generated boletos with pending payment status?
~~~

Suggested schema/table idea, when needed:

~~~text
customers(id, name)
boletos(id, customer_id, status, amount)
~~~

Highlight:

- natural language to SQL;
- read-only SQL validation;
- unsafe query blocking;
- controlled execution;
- data evidence;
- QA/data validation integration.

### 6. Run the Multi-Agent QA Copilot

Open the Multi-Agent QA Copilot Console.

Suggested requirement:

~~~text
As an operations analyst, I want the system to generate a CNAB report after boleto processing so that finance can reconcile paid and pending agreements.
~~~

Suggested explanation:

~~~text
The Multi-Agent QA Copilot orchestrates specialized QA agents around a shared workflow.

Instead of one agent doing everything, the system separates responsibilities: requirement analysis, functional QA, test automation, review and reporting.
~~~

Highlight:

- orchestrator agent;
- specialized agents;
- shared state;
- artifacts;
- messages;
- execution trace;
- final QA report;
- quality gates;
- deterministic evaluation.

### 7. Show Execution History

Open Execution History.

Suggested explanation:

~~~text
After running workflows, the system records operational signals.

Execution History consolidates persisted telemetry into a timeline, making AI workflow execution inspectable.
~~~

Highlight:

- unified timeline;
- execution type;
- status;
- component;
- operation;
- run ID;
- quality score when available;
- persisted local JSONL telemetry.

### 8. Open Run Details

Select one execution record.

Suggested explanation:

~~~text
Run Details allow deeper inspection of each execution.

This is important because AI systems need traceability. When an agent fails, produces low-quality output or triggers a risk signal, we need to inspect what happened.
~~~

Highlight:

- selected execution;
- metadata;
- raw record view;
- debugging and operational review;
- AI observability.

### 9. Show Observability Center

Open Observability Center.

Suggested explanation:

~~~text
The Observability Center aggregates AI quality signals across usage, retrieval, agent execution, multi-agent execution and evaluation telemetry.
~~~

Highlight:

- backend dashboard integration;
- manual refresh;
- auto-refresh;
- last updated timestamp;
- risk and recommendation signals;
- local operational dashboard behavior.

### 10. Show Usage and Cost

Open Usage and Cost.

Suggested explanation:

~~~text
The project includes token and cost usage tracking.

The goal is not provider billing reconciliation yet. The goal is to show how AI systems can expose usage and estimated cost signals as part of LLMOps.
~~~

Highlight:

- token tracking;
- estimated cost;
- provider/component metadata;
- persistent local usage records.

### 11. Show Risk Center

Open Risk Center.

Suggested explanation:

~~~text
The Risk Center consolidates operational and quality risks detected by the observability layer.

This helps position the project as an AI Quality Engineering system, not only an execution interface.
~~~

Highlight:

- risks;
- recommendations;
- section-level status;
- quality-oriented product thinking.

### 12. Show Provider Settings

Open Provider Settings.

Suggested explanation:

~~~text
The provider settings screen shows the current LLM provider configuration safely.

The backend exposes only sanitized provider metadata. It does not expose API keys or sensitive provider configuration.
~~~

Highlight:

- Fake provider;
- Ollama provider;
- OpenAI provider;
- safe provider diagnostics;
- no frontend secret exposure.

### 13. Show Security and Governance

Open the API docs or call security endpoints.

Recommended endpoints:

~~~text
POST /security/prompt-injection/assess
GET /security/prompt-injection/records
GET /security/blocked-tool-calls
GET /security/audit/events
~~~

Suggested explanation:

~~~text
The project includes a security and governance baseline.

Prompt injection is assessed through a deterministic baseline. Tool execution is controlled through a registry, risk classification and authorization checks. Blocked tool calls and high-risk prompt injection assessments generate telemetry and audit events.
~~~

Highlight:

- prompt injection assessment;
- prompt injection telemetry;
- prompt injection audit events;
- tool authorization;
- blocked tool-call telemetry;
- blocked tool-call audit events;
- audit log service;
- sensitive data handling policy.

### 14. Close with Architecture

Show the README architecture diagram or architecture document.

Suggested explanation:

~~~text
The architecture intentionally separates frontend, API transport, domain services, LLM providers, RAG, agents, tools, evaluation, observability, storage and security controls.

This makes the system easier to test, evolve, observe and explain.
~~~

Highlight:

- explicit architecture;
- framework-light agent runtime;
- provider independence;
- local-first persistence;
- evaluation and observability;
- governance controls.

## Short Demo Version

For a 5 to 7 minute demo, use this flow:

~~~text
1. Overview
2. QA Agent Console
3. Multi-Agent QA Copilot
4. Execution History
5. Observability Center
6. Security/Audit endpoints
7. Architecture and roadmap
~~~

Suggested closing:

~~~text
This project started as an Applied AI Engineering lab and evolved into a local AI Quality Command Center.

It demonstrates how AI can be applied to software quality with architecture, evaluation, observability and governance from the beginning.
~~~

## Technical Deep Dive Version

For a technical interview or architecture review, expand the demo with:

- LLM provider abstraction;
- structured Pydantic outputs;
- RAG ingestion and retrieval services;
- Tool Registry;
- Tool Execution Service;
- Tool Authorization Service;
- Agent Runtime;
- Multi-Agent QA Copilot contracts;
- evaluation suites;
- telemetry services;
- local JSONL storage;
- audit log service;
- security documentation.

Suggested explanation:

~~~text
The project intentionally implements its own lightweight agent runtime, tool registry, RAG pipeline, evaluation layer and governance controls instead of relying on high-level orchestration frameworks.

This makes the architecture explicit, auditable and easier to study.
~~~

## Demo Boundaries

Be explicit about current limitations.

Current limitations:

- local-first demo environment;
- no production authentication yet;
- no multi-user isolation yet;
- no cloud deployment yet;
- no persistent vector database yet;
- no persistent agent memory/session resume yet;
- no production monitoring integration yet;
- no production MCP hosting yet.

Suggested wording:

~~~text
This is not positioned as a finished SaaS product.

It is a production-oriented AI Engineering portfolio project, built to demonstrate architecture, quality controls, observability and governance patterns.
~~~

## Post-launch Evolution

After the local portfolio launch, the project will continue through implementation packs:

1. Cloud & Deployment
2. Production Observability
3. Production Agent State
4. Security Enterprise Layer
5. MCP Production Layer
6. Data Integrations
7. Multi-provider AI Evaluation

Suggested wording:

~~~text
The launch version focuses on the local AI Quality Command Center.

The next evolution packs will move the project toward cloud deployment, production observability, persistent state, enterprise security, production MCP hosting, external data integrations and multi-provider evaluation.
~~~

## Suggested LinkedIn Launch Summary

~~~text
I built an AI Quality Command Center as part of my Applied AI Engineering Lab.

The project combines LLM provider abstraction, RAG, QA agents, a Data Analyst Agent, a Multi-Agent QA Copilot, evaluation pipelines, observability, execution history, usage tracking and security/governance controls.

The goal was to go beyond prompt demos and explore what it takes to build AI systems that are structured, testable, observable and auditable in a software quality context.
~~~

## Final Demo Checklist

Before recording or presenting:

- [ ] API starts successfully
- [ ] Frontend starts successfully
- [ ] Health endpoint returns success
- [ ] Provider settings load correctly
- [ ] RAG Console works
- [ ] QA Agent Console works
- [ ] Data Analyst Console works
- [ ] Multi-Agent QA Copilot Console works
- [ ] Execution History shows recent records
- [ ] Run Details opens correctly
- [ ] Observability Center refreshes correctly
- [ ] Usage and Cost view loads
- [ ] Risk Center loads
- [ ] Security endpoints are available
- [ ] README and roadmap are updated
- [ ] Limitations are clearly stated
