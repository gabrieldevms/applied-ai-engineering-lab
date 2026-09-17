# Production Observability Strategy

## Scope and decision

Pack 2 extends the local-first AI Quality Command Center with operational monitoring, persistent evaluation artifacts and clearer AI quality scorecards. Pack 1's application topology, API contracts, JSONL telemetry, Execution History and frontend remain the foundation. This is a production-like local observability path, not a public deployment or a complete production operations program.

Operational observability and AI quality observability serve different questions:

| Plane | Questions | Source of truth |
| --- | --- | --- |
| Operational | Is the application serving requests, how quickly, and with which HTTP failure rate? Is it ready? | Bounded Prometheus-compatible API metrics scraped by local Prometheus. |
| AI quality | Are evaluations, retrieval, agents and multi-agent workflows meeting their quality expectations? What did they cost, and which executions failed? | Existing application telemetry, JSONL stores, evaluation artifacts and backend read models. |

Prometheus must not replace rich AI telemetry. Domain records, run IDs, traces, quality evidence and artifact details remain in the application storage layer rather than becoming metric labels.

## Local monitoring topology

```text
Browser -> web / Nginx -> /api/* -> FastAPI -> existing AI telemetry
                                 |      |
                                 |      +-> internal GET /metrics
                                 |                ^
                                 |                |
                                 |           Prometheus
                                 +-> JSONL data and evaluation artifacts
```

The target design keeps the API and web services runnable without monitoring. An explicit Compose `observability` profile will add a version-pinned Prometheus service on the internal Docker network. Prometheus will scrape `http://api:8000/metrics`, store time-series data in its own named volume and bind its local UI only to loopback. It will not receive provider credentials or send metrics to an external service. The API remains unbound on the host.

Nginx must reject `/api/metrics` before its general `/api/` proxy rule. `/metrics` is an operator endpoint on the internal API workload, not part of the browser API contract. Existing frontend routes and all other `/api/*` requests retain the same-origin behavior introduced in Pack 1. A local development API may expose `/metrics` directly on port 8000; the production-like web boundary must not proxy it.

## Operational metric contract

A small Prometheus Python client is sufficient; no broad instrumentation framework is needed. The first metrics are:

| Metric | Type | Labels | Meaning |
| --- | --- | --- | --- |
| `ai_quality_http_requests_total` | Counter | `method`, `route`, `status_class` | Completed application requests. |
| `ai_quality_http_request_duration_seconds` | Histogram | `method`, `route` | Request duration in seconds with fixed buckets. |
| `ai_quality_readiness` | Gauge | None | Last observed local readiness result: 1 ready, 0 not ready. |

The route label uses the registered route template, never the raw request path or query. Unmatched routes use one fixed value. Method values are reduced to a fixed HTTP vocabulary, and status class is a bounded value such as `2xx` or `5xx`. The `/metrics` scrape itself is excluded from application traffic metrics. No metric labels may contain run or trace IDs, artifact IDs, prompts, filenames, SQL, user strings or exception messages. Metric names and labels are stable and project-scoped. Histogram buckets are fixed and suitable for local request latencies; they are not an SLO commitment.

Metrics must contain no prompt or document text, requirement text, user input, provider credentials, raw tool or database payloads, internal provider URLs or unbounded error strings. Instrumentation must not change the behavior of `/health`, `/ready` or any existing API route. Readiness stays deterministic and independent of Prometheus. Failure to scrape or start Prometheus must not prevent the API from serving requests.

## Persistence and evaluation artifacts

The existing named application volume remains mounted at `STORAGE_BASE_DIR`. Existing JSONL telemetry and security records keep their contracts. Evaluation artifacts will use a dedicated `evaluation-artifacts/` directory under that configured root, with safe generated IDs mapped to JSON files. IDs are opaque identifiers, never filesystem paths. Writes should be atomic; listing, retrieval and latest-artifact reads must reject traversal and report missing IDs predictably.

The persisted contract is a sanitized summary derived from deterministic evaluation results: artifact ID, timestamp, source, status, suite/stage summaries, numeric quality metrics and bounded safe CI metadata. Existing pipeline response metadata and free-form report content must be inspected before persistence and must not be copied wholesale. Secrets, prompts, user input and private document content must not be stored. The artifact created by an application or local pipeline run survives normal API container recreation through the application volume. The existing GitHub Actions artifact upload remains a separate CI-run attachment and must continue to work.

The JSONL and artifact stores are local, single-instance persistence. Neither Docker volume provides backup, retention guarantees or cross-instance coordination. No production database or vector store is introduced in this pack.

## AI quality scorecards and frontend

Scorecards will be deterministic read models over existing evaluation, retrieval, agent, multi-agent and usage services, persistent artifacts and the current dashboard. They will not create a second telemetry store or call an LLM or Prometheus. Each section will expose its evidence, status, freshness and available risks or recommendations. Missing evidence is explicit (`no_data` or an existing equivalent), rather than treated as healthy. Operational readiness may use the API's local readiness result; Prometheus is not queried from the application to score itself.

Avoid a single arbitrary cross-domain score. A trend is emitted only where timestamped history supports an explicit recent-versus-previous comparison; otherwise it is `insufficient_data`. Window sizes, comparison rules and status thresholds must be documented and tested alongside the read model. Existing dashboard and Execution History response contracts remain compatible.

The current Observability Center and Evaluation Center will consume the new read models through their existing typed API client pattern. They will show section-level quality state, trends, latest and prior evaluation artifacts, artifact details and refresh time without duplicating Execution History. Simple accessible cards and text indicators should fit the current visual language; a charting dependency is not warranted by this scope. Prometheus remains an operator interface, never a frontend data source.

## Validation and deferred work

Every Pack 2 PR must pass the backend, frontend, production-like stack and deterministic AI evaluation jobs when they run. Monitoring changes also need a focused CI check for Compose configuration, a healthy Prometheus target, a safe metric query, intact frontend/API routing and denial of `/api/metrics`. CI uses the Fake provider and no paid or external monitoring service.

Pack 2 does not add Grafana, external log aggregation, alert delivery, distributed tracing, a cloud monitoring service, authentication, production secrets management, production databases, persistent RAG vectors or agent state, or a public cloud deployment. Local metrics and artifacts must not be described as production retention, backup or unrestricted public readiness.
