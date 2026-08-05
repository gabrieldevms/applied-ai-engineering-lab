# Changelog

All notable changes to this project will be documented in this file.

## M8 — Cloud, Security and Portfolio

### Added

- Added current capabilities reference documentation preserving the detailed technical inventory previously maintained in the README.
- Added AI Quality Command Center technical case study for portfolio presentation.
- Added launch demo script for presenting the AI Quality Command Center as a local-first AI Quality Engineering platform.
- Added security and governance baseline documentation.
- Added updated security/governance status documentation for provider configuration, prompt injection, tool authorization, sensitive data handling and audit logs.
- Added post-launch implementation packs to the roadmap for cloud deployment, production observability, persistent agent state, enterprise security, MCP production hosting, data integrations and multi-provider AI evaluation.
- Started M8 product experience work.
- Rebuilt the frontend from scratch using Vite, React and TypeScript.
- Added the AI Quality Command Center foundation.
- Added backend observability dashboard integration through the frontend.
- Added Observability Center UI.
- Added Evaluation Center UI.
- Added QA Agent Console integrated with `POST /agents/qa/run`.
- Added Multi-Agent QA Copilot Console integrated with `POST /multi-agent/qa-copilot/run`.
- Added RAG Console integrated with `POST /rag/retrieve` and `POST /rag/answer`.
- Added Data Analyst Console integrated with `POST /data-analysis/agent/run`.
- Added Provider and Model Settings UI integrated with `GET /llm/providers` and `GET /llm/health`.
- Added Usage & Cost visualization integrated with usage tracking observability endpoints.
- Added demo usage record action for local LLMOps demonstration.
- Added Central de Riscos for risk and recommendation panels.
- Added consolidated section-level risk, recommendation and status views using `GET /observability/dashboard`.
- Added Persistent Storage Foundation with reusable local JSONL storage primitives.
- Added storage configuration settings for `STORAGE_BACKEND` and `STORAGE_BASE_DIR`.
- Added generic JSONL store support for append, list, recent listing, field lookup, count, clear and metadata operations.
- Added persistent local JSONL storage support for AI usage tracking records.
- Added `AI_USAGE_RECORDS_PATH` setting for configurable usage tracking persistence.
- Added persistent local JSONL storage support for evaluation telemetry events.
- Added `EVALUATION_TELEMETRY_EVENTS_PATH` setting for configurable evaluation telemetry persistence.
- Added persistent local JSONL storage support for retrieval quality telemetry records.
- Added `RETRIEVAL_QUALITY_RECORDS_PATH` setting for configurable retrieval quality persistence.
- Added persistent local JSONL storage support for agent execution telemetry records.
- Added `AGENT_EXECUTION_RECORDS_PATH` setting for configurable agent execution persistence.
- Added persistent local JSONL storage support for multi-agent execution telemetry records.
- Added `MULTI_AGENT_EXECUTION_RECORDS_PATH` setting for configurable multi-agent execution persistence.
- Added Execution History backend read model for consolidating persisted observability records.
- Added `GET /observability/execution-history` to list unified AI execution history records across evaluation, usage, retrieval, agent and multi-agent telemetry.
- Added Execution History UI to the AI Quality Command Center.
- Added frontend API client, hook and types for `GET /observability/execution-history`.
- Added filters for execution type, status, component, run ID and limit in the Execution History page.
- Added QA Agent Console telemetry integration with agent execution observability.
- Added frontend API client and types for `POST /observability/agent-execution/records`.
- Added Multi-Agent Copilot Console telemetry integration with multi-agent execution observability.
- Added frontend API client and types for `POST /observability/multi-agent-execution/records`.
- Added RAG Console telemetry integration with retrieval quality observability.
- Added frontend API client and types for `POST /observability/retrieval-quality/records`.
- Added Data Analyst Console telemetry integration with agent execution observability.
- Added live Observability Dashboard behavior with manual refresh, last updated timestamp and auto-refresh toggle.
- Added Execution History run details panel with selected execution drill-down.
- Added safe LLM provider configuration fields to provider health responses.
- Added deterministic prompt injection detection baseline.
- Added `POST /security/prompt-injection/assess` endpoint.
- Added prompt injection detection and API tests.
- Added tool authorization boundaries documentation covering tool risk levels, caller types, environment boundaries and future authorization controls.
- Added tool risk classification metadata to registered agent tools.
- Added tool security metadata to `/agents/tools` responses.
- Added tests for default tool risk classification and API exposure.
- Added tool authorization service for registered agent tools.
- Added caller and environment checks during tool execution.
- Added tests for allowed and blocked tool execution authorization decisions.
- Added sensitive data handling policy covering prompts, RAG documents, table data, telemetry, logs, Execution History, MCP inputs and provider usage.
- Added audit log schema documentation covering security-relevant events, tool authorization, prompt injection, human approval, sensitive data, provider configuration and MCP audit events.
- Added blocked tool-call telemetry service.
- Added safe telemetry recording when tool authorization blocks execution.
- Added `GET /security/blocked-tool-calls` endpoint.
- Added blocked tool-call telemetry tests.
- Added prompt injection telemetry service.
- Added safe telemetry recording for medium and high prompt injection assessments.
- Added `GET /security/prompt-injection/records` endpoint.
- Added prompt injection telemetry tests.
- Added security audit log service foundation.
- Added audit event schemas for authorization, prompt injection, human approval, sensitive data, provider configuration and MCP events.
- Added in-memory and JSONL audit event stores.
- Added `GET /security/audit/events` endpoint.
- Added audit log service and API tests.
- Added audit event recording for blocked tool-call authorization decisions.
- Added tests covering blocked tool-call audit events.
- Added audit event recording for high-risk prompt injection assessments.
- Added API tests covering prompt injection audit events.

### Changed

- Updated README into a portfolio-oriented launch landing page.
- Moved detailed capability inventory from the README into a dedicated technical reference document.
- Updated README security and governance status to reflect the current implemented controls.
- Updated ROADMAP M8 security and governance checklist to reflect implemented prompt injection, tool authorization, telemetry and audit log capabilities.
- Updated M8 next focus from implementation expansion to launch documentation, case study and portfolio presentation.
- Replaced the old frontend prototype with a clean product-oriented frontend foundation.
- Organized frontend navigation around product areas and AI engineering workflows.
- Introduced reusable frontend structures for API clients, typed responses, JSON viewers, metric cards and console pages.
- Completed the first local AI Quality Command Center frontend/product experience.
- Updated the frontend navigation to include provider settings, Usage & Cost and Central de Riscos.
- Updated AI usage tracking to support persistent storage through the storage foundation.
- Updated Usage & Cost backend data flow to survive API restarts when `STORAGE_BACKEND=local_jsonl`.
- Updated evaluation telemetry to support persistent storage through the storage foundation.
- Updated Evaluation Center and observability dashboard backend data flow to survive API restarts for evaluation telemetry when `STORAGE_BACKEND=local_jsonl`.
- Updated retrieval quality telemetry to support persistent storage through the storage foundation.
- Updated RAG quality and observability dashboard backend data flow to survive API restarts for retrieval quality records when `STORAGE_BACKEND=local_jsonl`.
- Updated agent execution telemetry to support persistent storage through the storage foundation.
- Updated agent execution observability backend data flow to survive API restarts when `STORAGE_BACKEND=local_jsonl`.
- Updated multi-agent execution telemetry to support persistent storage through the storage foundation.
- Updated multi-agent execution observability backend data flow to survive API restarts when `STORAGE_BACKEND=local_jsonl`.
- Updated QA Agent Console to automatically register agent execution telemetry after successful or failed backend executions.
- Updated Multi-Agent Copilot Console to automatically register multi-agent execution telemetry after successful or failed backend executions.
- Updated RAG Console to automatically register retrieval quality telemetry after retrieve and answer executions.
- Updated Data Analyst Console to automatically register agent execution telemetry after successful, blocked or failed backend executions.
- Updated Observability Center to refresh dashboard data without clearing the currently displayed dashboard.
- Updated Execution History timeline to support selecting records and inspecting execution metadata.
- Hardened provider health responses to avoid exposing sensitive environment variable names, API key values or internal provider URLs.
- Updated the Provider Settings UI to display only sanitized provider metadata and logical configuration fields.
- Tool execution metadata now includes tool risk classification fields.
- Tool execution now enforces authorization checks before running handlers.
- Tool Registry metadata now reports authorization enforcement as enabled.
- Tool execution now records sanitized blocked tool-call telemetry before raising authorization errors.
- Prompt injection assessment endpoint now records sanitized telemetry for relevant security assessments without storing the original input text.
- Tool execution now records both blocked tool-call telemetry and audit log events when authorization blocks execution.
- Prompt injection assessment now records both telemetry and audit log events for high-risk/blocking assessments.

### Notes

- M8 is still in progress.
- The first AI Quality Command Center frontend/product experience is completed for local demonstrations and portfolio presentation.
- Console execution results are currently kept in local React state.
- M8 remains in progress, but the local AI Quality Command Center, persistent local observability foundation, execution history and security/governance baseline are now implemented for portfolio demonstration.
- Production cloud deployment, authentication, multi-user isolation, persistent vector storage, persistent agent state, production monitoring and production MCP hosting remain post-launch work.
- The next M8 focus is launch documentation, final case study, roadmap synchronization and portfolio presentation.
- Usage tracking is the first observability service migrated from in-memory-only storage to the persistent storage foundation.
- Evaluation telemetry is now the second observability capability migrated to the persistent storage foundation, after usage tracking.
- Retrieval quality telemetry is now the third observability capability migrated to the persistent storage foundation.
- Agent execution telemetry is now the fourth observability capability migrated to the persistent storage foundation.
- Multi-agent execution telemetry completes the first persistent storage pass for the core observability telemetry services.
- Execution History currently works as a backend read model over persisted observability telemetry. It does not create a separate execution-history store yet.
- Execution History UI currently consumes the backend read model and does not persist frontend console state yet.
- QA Agent Console executions can now appear in Execution History through the persisted agent execution telemetry read model.
- Multi-Agent Copilot Console executions can now appear in Execution History through the persisted multi-agent execution telemetry read model.
- RAG Console executions can now appear in Execution History through the persisted retrieval quality telemetry read model.
- Data Analyst Console executions can now appear in Execution History through the persisted agent execution telemetry read model.
- Observability Center can now behave as a live operational dashboard for persisted console telemetry signals.
- Execution History now supports operational drill-down for individual telemetry records.

---

## M7 — Evaluation and LLMOps

### Added

- Added Golden Evaluation Dataset foundation.
- Added Golden Evaluation Dataset validation.
- Added Golden Evaluation Dataset Runner.
- Added support for scenario-level golden evaluation results.
- Added support for dataset-level evaluation status.
- Added filtering by scenario ID and scenario type.
- Added dry-run support for golden evaluation execution.
- Added prompt regression evaluation foundation.
- Added prompt regression suite definition.
- Added prompt regression execution service.
- Added prompt regression API endpoints.
- Added AI Evaluation Report Aggregation.
- Added aggregated AI quality report response.
- Added report sections, highlights, risks, metrics and recommendations.
- Added Evaluation Telemetry foundation.
- Added structured evaluation telemetry events.
- Added telemetry event listing.
- Added telemetry summary generation.
- Added latency tracking for evaluation workflows.
- Added error tracking for evaluation workflows.
- Added fallback and warning telemetry signals.
- Added LLM Output Evaluation Suite.
- Added RAG Regression Evaluation Suite.
- Added Agent Regression Evaluation Suite.
- Added Tool-calling Evaluation Suite.
- Added Multi-Agent QA Copilot Regression Evaluation Suite.
- Added controlled LLM-as-judge Evaluation Prototype.
- Added LLM-as-judge rubric items.
- Added structured judge output validation.
- Added CI Evaluation Pipeline service.
- Added CI Evaluation Pipeline API endpoint.
- Added AI evaluation pipeline script.
- Added GitHub Actions workflow for deterministic AI evaluation.
- Added AI evaluation pipeline report output.
- Added token usage tracking.
- Added cost usage tracking.
- Added usage record schemas.
- Added usage summary schemas.
- Added usage tracking service.
- Added usage records API endpoints.
- Added usage summary API endpoints.
- Added caller-provided pricing support for cost estimation.
- Added provider, model, component and operation usage coverage.
- Added Retrieval Quality Telemetry Metrics.
- Added retrieval quality record schemas.
- Added retrieval quality summary schemas.
- Added retrieval quality telemetry service.
- Added precision-at-k calculation.
- Added source coverage score calculation.
- Added retrieval quality score calculation.
- Added retrieval risk detection.
- Added retrieval quality records API endpoints.
- Added retrieval quality summary API endpoints.
- Added Agent Execution Telemetry Metrics.
- Added agent execution record schemas.
- Added agent execution summary schemas.
- Added agent execution telemetry service.
- Added step success rate calculation.
- Added tool success rate calculation.
- Added human approval rate calculation.
- Added agent execution quality score calculation.
- Added agent execution risk detection.
- Added retry, fallback, error and duration signals for agent execution.
- Added agent execution records API endpoints.
- Added agent execution summary API endpoints.
- Added Multi-Agent Execution Telemetry Metrics.
- Added multi-agent execution record schemas.
- Added multi-agent execution summary schemas.
- Added multi-agent execution telemetry service.
- Added agent success rate calculation for multi-agent workflows.
- Added task success rate calculation for multi-agent workflows.
- Added handoff success rate calculation.
- Added contract success rate calculation.
- Added artifact coverage score calculation.
- Added final report coverage score calculation.
- Added data validation evidence score calculation.
- Added multi-agent execution quality score calculation.
- Added multi-agent execution risk detection.
- Added conflict, critical conflict, failure, error, retry and fallback signals.
- Added multi-agent execution records API endpoints.
- Added multi-agent execution summary API endpoints.
- Added backend AI Observability Dashboard.
- Added observability dashboard schemas.
- Added observability dashboard service.
- Added section-level dashboard status aggregation.
- Added global risk aggregation.
- Added dashboard recommendation generation.
- Added `GET /observability/dashboard`.
- Added M7 Evaluation and LLMOps study note.
- Added documentation for the future AI Quality Command Center direction.

### Changed

- Updated AI evaluation pipeline naming to avoid milestone-specific runtime names.
- Renamed the deterministic evaluation script to `scripts/run_ai_evaluation_pipeline.py`.
- Renamed the evaluation workflow to `.github/workflows/ai-evaluation-pipeline.yml`.
- Updated the workflow display name to `AI Evaluation Pipeline`.
- Updated the pipeline report output to `.data/ai-evaluation-pipeline-report.json`.
- Updated project documentation to mark M7 as completed.
- Updated project documentation to set M8 as the next milestone.
- Updated README with evaluation, telemetry, observability and dashboard capabilities.
- Updated ROADMAP with completed M7 evaluation and observability scope.
- Updated documentation to position the future frontend as the AI Quality Command Center.

### Notes

- M7 introduces evaluation and observability as first-class product capabilities.
- Most evaluation logic remains deterministic and testable.
- LLM-as-judge exists as a controlled prototype, not as the only quality signal.
- The observability dashboard is backend-only in M7.
- The dashboard response contract is intended to support the future AI Quality Command Center frontend.
- Most telemetry and observability records are currently stored in memory.
- Token and cost tracking depends on caller-provided pricing data.
- Cost calculation is an estimate and not provider billing reconciliation.

---

## M6 — Multi-Agent QA Copilot

### Added

- Added Multi-Agent QA Copilot foundation.
- Added Multi-Agent QA Copilot API endpoint through `POST /multi-agent/qa-copilot/run`.
- Added multi-agent role descriptors for Orchestrator, Requirement Analyst, Functional QA, Test Automation, Reviewer and Report agents.
- Added shared multi-agent execution state.
- Added multi-agent artifacts.
- Added multi-agent messages.
- Added multi-agent task results.
- Added multi-agent execution trace.
- Added inter-agent communication contracts.
- Added contract validation.
- Added multi-agent failure handling with `stop_on_failure` and `continue_on_failure` strategies.
- Added skipped agent handling after blocking failures.
- Added multi-agent shared-state conflict detection.
- Added dedicated Multi-Agent Final QA Report Generator.
- Added quality gate metadata for multi-agent final reports.
- Added Requirement Analysis service integration in the Requirement Analyst Agent.
- Added Data Analyst Agent integration in the Functional QA Agent.
- Added data validation evidence in Multi-Agent QA final reports.
- Added `run_multi_agent_qa_copilot` MCP tool.
- Added deterministic Multi-Agent QA Copilot evaluation.
- Added Multi-Agent QA Copilot evaluation endpoint through `POST /multi-agent/qa-copilot/evaluate`.
- Added evaluation metrics for status alignment, role coverage, trace integrity, contract validation, failure control, conflict control, final report completeness and data validation evidence.
- Added M6 Multi-Agent QA Copilot final review study note.

### Changed

- Marked M6 Multi-Agent QA Copilot as completed.
- Added M7 Evaluation and LLMOps as the next planned milestone.

---

## M5 — MCP QA Server

### Added

- Added MCP QA Server foundation using FastMCP.
- Added MCP discovery tools:
  - `get_project_status`
  - `list_agent_tools`
  - `list_specialized_agents`
- Added Requirement Analysis MCP tool through `analyze_requirement`.
- Added RAG MCP tools through `retrieve_rag_context` and `answer_with_rag`.
- Added QA Agent MCP tool through `run_qa_agent`.
- Added Data Analyst Agent MCP tool through `run_data_analyst_agent`.
- Added SQL Workflow Regression MCP tool through `run_sql_regression_suite`.
- Added MCP client integration validation using FastMCP in-memory client.
- Added MCP smoke test script for local validation.
- Added FastMCP CLI wrapper for local tool inspection.
- Added MCP security boundaries documentation.
- Added MCP usage documentation.
- Added M5 MCP QA Server final review study note.

### Changed

- Marked M5 MCP QA Server as completed.

---

## Pre-M5 — Data Analyst Agent and QA/Data Integration

### Added

- Added Data Analyst Agent foundation.
- Added database schema representation for data analysis workflows.
- Added table and column metadata schemas.
- Added natural-language-to-SQL request schemas.
- Added structured SQL generation workflow.
- Added SQL explanation and assumptions in generated SQL responses.
- Added read-only SQL validation for generated and submitted queries.
- Added unsafe SQL blocking for write, destructive and administrative commands.
- Added controlled in-memory SQLite query execution.
- Added SQL query result evidence schemas.
- Added SQL generate, validate and execute workflow.
- Added Data Analyst Agent runtime wrapper.
- Added Data Analyst Agent API endpoint.
- Added Data Analyst Agent deterministic evaluation.
- Added Data Analyst Agent evaluation API endpoint.
- Added Specialized Agent Registry.
- Added specialized agent descriptors for QA Agent and Data Analyst Agent.
- Added Data Analyst Agent tool adapter as `data_analysis.agent.run`.
- Added Tool Registry support for `data_analysis.agent.run`.
- Added Generic Agent Runtime support for executing the Data Analyst Agent through tool calls.
- Added QA Agent data validation capability.
- Added optional QA Agent data validation through the Data Analyst Agent.
- Added automatic QA Agent data validation selection.
- Added QA Agent data validation modes: `auto`, `required` and `disabled`.
- Added QA Agent data validation selection metadata.
- Added QA Agent response support for data validation evidence.
- Added QA Agent deterministic evaluation with data evidence.
- Added QA Agent evaluation API endpoint.
- Added SQL workflow regression dataset runner.
- Added SQL regression scenario schemas.
- Added SQL regression suite request and response schemas.
- Added SQL workflow regression API endpoint.
- Added regression checks for workflow status, row count, expected columns and expected rows.

### Changed

- Updated README project status before M5.
- Updated ROADMAP status before M5.
- Marked Pre-M5 Data Analyst Agent and QA/Data Agent integration work as completed.
- Updated the next milestone to M5 — MCP QA Server.

---

## Pre-M5 — File Ingestion Expansion

### Added

- Added File Ingestion Expansion review documentation.
- Added multi-format file ingestion documentation for TXT, Markdown, PDF, DOCX, CSV and XLSX.
- Added structured table extraction documentation for CSV, XLSX and DOCX tables.
- Added PDF text extraction.
- Added DOCX text extraction.
- Added CSV ingestion.
- Added Excel and spreadsheet ingestion.
- Added structured table extraction.
- Added file metadata normalization.
- Added extraction and ingestion tests.
- Added RAG integration validation.

### Changed

- Marked File Ingestion Expansion as completed.
- Updated the next milestone to Data Analyst Agent foundation.
- Updated README supported file ingestion capabilities and limitations.

---

## M4 — AI Agents

### Added

- Added Agent runtime foundation.
- Added Agent request and response schemas.
- Added Agent execution trace.
- Added Agent run API endpoint.
- Added unit and API tests for agent runtime.
- Added Agent tool registry.
- Added default tool definitions for RAG retrieval, RAG answer generation and requirement analysis.
- Added Agent tools listing endpoint.
- Added unit and API tests for tool registry.
- Added Agent tool execution service.
- Added RAG retrieval tool handler for agents.
- Added Agent tool execution API endpoint.
- Added structured tool execution response.
- Added error handling for unknown or unsupported tools.
- Added unit and API tests for tool execution.
- Added Agent tool calling support.
- Added tool calls in agent run requests.
- Added tool execution results in agent traces.
- Added failed tool call handling in agent runtime.
- Added unit and API tests for agent tool calling.
- Added Requirement Analysis tool handler for agents.
- Added support for executing `requirements.analyze` through the tool execution service.
- Added Requirement Analysis tool calls in agent runtime.
- Added unit and API tests for requirement analysis tool execution.
- Added initial QA Agent service.
- Added QA Agent API endpoint.
- Added QA Agent orchestration using RAG retrieval and requirement analysis tools.
- Added structured QA Agent response with requirement analysis and retrieved context.
- Added unit and API tests for QA Agent.
- Added RAG answer tool handler for agents.
- Added support for executing `rag.answer` through the tool execution service.
- Added RAG answer tool calls in agent runtime.
- Added unit and API tests for RAG answer tool execution.
- Added LLM-based agent planning service.
- Added Agent planning prompt builder.
- Added Agent planning response parser.
- Added Agent planning API endpoint.
- Added structured agent plan schemas.
- Added unit and API tests for agent planning.
- Added Agent automatic tool selection service.
- Added Tool selection API endpoint.
- Added selection of executable tools from structured agent plans.
- Added skipped-step reporting for non-tool or invalid tool plan steps.
- Added unit and API tests for automatic tool selection.
- Added exposed tool execution handler availability for agent tool selection.
- Added multi-step agent execution service.
- Added Agent execution endpoint for planning, tool selection and execution.
- Added structured response combining plan, selected tools and runtime trace.
- Added unit and API tests for multi-step agent execution.
- Added Agent execution state schema.
- Added in-memory agent state store.
- Added Agent state service.
- Added execution state snapshots for multi-step agent workflows.
- Added unit tests for agent execution state.
- Added Agent approval policy schema.
- Added Agent tool approval decision schema.
- Added Human approval service for selected tool calls.
- Added approval-aware multi-step agent execution.
- Added unit and API tests for approval-controlled execution.
- Added file-based persistent agent execution logs.
- Added Agent execution log service.
- Added Agent execution log stores for memory and JSONL files.
- Added execution log events for planning, tool selection, approval, runtime and state recording.
- Added log retrieval endpoints for all events and by run ID.
- Added unit and API tests for execution logs.
- Added Agent safety policy schema.
- Added Agent safety violation schema.
- Added Agent safety check response schema.
- Added Agent safety service for tool execution boundaries.
- Added safety-aware multi-step agent execution.
- Added safety evaluation events in agent execution logs.
- Added unit and API tests for agent safety limits.
- Added deterministic agent evaluation service.
- Added Agent evaluation schemas and metrics.
- Added Agent execution evaluation endpoint.
- Added evaluation metrics for traceability, completion, safety, approval control and objective alignment.
- Added evaluation events in agent execution logs.
- Added unit and API tests for agent evaluation.
- Added M4 AI Agents module review documentation.
- Added consolidated documentation for agent runtime, planning, tools, approval, safety, logs and evaluation.
- Added Pre-M5 roadmap for file ingestion expansion and the Data Analyst Agent foundation.

### Changed

- Multi-step agent execution now records execution log events.
- Multi-step agent execution now filters executable tool calls through safety limits.
- Multi-step agent execution now returns evaluation results.
- Agent execution logs now include safety evaluation events.
- Agent execution logs now include evaluation completion events.
- Marked M4 — AI Agents as completed.
- Updated the project status and next milestone to File Ingestion Expansion.
- Consolidated README agent capabilities, endpoints and current limitations.

---

## M3 — RAG Knowledge Assistant

### Added

- Added RAG document chunking service.
- Added Document chunking API endpoint.
- Added Document chunking schemas and metadata.
- Added unit and API tests for document chunking.
- Added RAG document ingestion service.
- Added Document ingestion API endpoint.
- Added stable document identifiers based on content hash.
- Added metadata support for ingested documents and chunks.
- Added unit and API tests for document ingestion.
- Added RAG text extraction service.
- Added Text extraction API endpoint for uploaded files.
- Added support for `.txt`, `.md` and `.markdown` files.
- Added unit and API tests for text extraction.
- Added RAG file ingestion pipeline.
- Added File ingestion API endpoint.
- Added metadata parsing for multipart form requests.
- Added combined text extraction, document ingestion and chunking flow.
- Added unit and API tests for file ingestion.
- Added RAG embedding provider abstraction.
- Added fake deterministic embedding provider.
- Added Embedding service.
- Added Embedding API endpoint.
- Added settings for embedding provider and dimensions.
- Added unit and API tests for embeddings.
- Added Vector store abstraction for RAG.
- Added in-memory vector store implementation.
- Added cosine similarity search for vector records.
- Added unit tests for vector store behavior.
- Added Semantic Search Service for RAG.
- Added Semantic search API endpoint.
- Added query embedding and document chunk indexing flow.
- Added ranked vector search results with metadata.
- Added unit and API tests for semantic search.
- Added RAG answer generation service.
- Added RAG answer prompt builder.
- Added RAG answer API endpoint.
- Added shared LLM provider factory.
- Added RAG answer generation tests.
- Added Source citation builder for RAG context chunks.
- Added citations in RAG answer responses.
- Added citation-aware RAG answer prompt instructions.
- Added unit tests for source citations.
- Added deterministic RAG evaluation service.
- Added RAG evaluation API endpoint.
- Added context relevance metric.
- Added answer groundedness metric.
- Added query alignment metric.
- Added citation coverage metric.
- Added unit and API tests for RAG evaluation.
- Added dedicated RAG retrieval service.
- Added Retrieval API endpoint.
- Added reusable retrieval layer for semantic search and future agent workflows.
- Added unit and API tests for retrieval.

---

## M2 — LLM Engineering

### Added

- Added LLM provider abstraction.
- Added Fake LLM provider for local tests.
- Added LLM message, response and usage models.
- Added Requirement analysis prompt template.
- Added unit tests for requirement analysis prompt generation.
- Added structured requirement analysis schemas.
- Added requirement risk schema with severity validation.
- Added unit tests for requirement analysis schemas.
- Added Portuguese-first requirement analysis defaults.
- Added Requirement analyzer service.
- Added requirement analysis error handling.
- Added unit tests for requirement analyzer service.
- Added LLM response parser for requirement analysis.
- Added LLM response validation tests.
- Added strict schema validation for requirement analysis responses.
- Added retry configuration for requirement analysis.
- Added retry strategy for invalid LLM responses.
- Added Fake LLM provider support for sequential responses.
- Added unit tests for requirement analysis retry behavior.
- Added fallback provider support for requirement analysis.
- Added fallback strategy for failed LLM responses.
- Added unit tests for requirement analysis fallback behavior.
- Added Requirement analysis API endpoint.
- Added dependency provider for requirement analyzer service.
- Added fake structured response for local requirement analysis.
- Added API tests for requirement analysis endpoint.
- Added environment-based settings for LLM provider selection.
- Added `.env.example` file.
- Added settings tests for provider and retry configuration.
- Added OpenAI LLM provider implementation.
- Added LLM provider error handling.
- Added Requirement analyzer support for provider-level failures.
- Added unit tests for OpenAI provider behavior.
- Added unit tests for provider error retry and fallback handling.
- Added Ollama LLM provider implementation.
- Added environment settings for Ollama provider configuration.
- Added unit tests for Ollama provider behavior.
- Added documentation for local Ollama usage.
- Added LLM provider diagnostics endpoints.
- Added LLM provider configuration health status.
- Added unit and API tests for provider diagnostics.
- Added LLM output normalization for JSON responses.
- Added JSON object extraction from Markdown or mixed text responses.
- Added unit tests for normalized LLM outputs.

---

## M1 — AI API Base

### Added

- Added Docker support for the API.
- Added Docker Compose configuration for local API execution.
- Added Docker ignore file.
- Added GitHub Actions CI pipeline for API tests.
- Added basic API request logging.
- Added basic API error handling.
- Added README updates for M1 completion and M2 start.

---

## M0 — Foundation

### Added

- Added initial repository structure.
- Added initial documentation structure.
- Added initial roadmap.
- Added initial architecture vision.
- Added ADR template.
- Added first architectural decision record.
- Added GitHub Project board.
- Added initial issues for M0 Foundation.
- Added local development environment validation document.