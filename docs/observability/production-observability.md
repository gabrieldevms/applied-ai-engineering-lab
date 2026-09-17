# Production Observability Runbook

Pack 2 adds a local, production-like monitoring path to the AI Quality Command Center. It does not deploy the application publicly. Run commands from the repository root in PowerShell. Docker Engine with Compose v2 is required for the container stack; Python 3.12+, `uv`, Node.js and npm are needed for source-level validation.

## Architecture and boundaries

| Plane | Source | Purpose |
| --- | --- | --- |
| Operational observability | FastAPI `/metrics` scraped by Prometheus on the internal Compose network | Request volume, latency, HTTP status classes and last observed readiness. |
| AI quality observability | Existing JSONL telemetry, sanitized evaluation artifacts and deterministic API read models | Evaluation, retrieval, agent, multi-agent, usage/cost and execution-history evidence. |

The browser uses the built React application at `http://127.0.0.1:8080/`. Nginx proxies ordinary `/api/*` requests to FastAPI. Prometheus scrapes `http://api:8000/metrics` directly; the API container has no host port. Nginx returns 404 for `/api/metrics` and its subpaths. The Prometheus UI binds to `127.0.0.1:9090` only when the `observability` profile is enabled. The frontend does not query Prometheus.

The `prom/prometheus:v3.14.0` image uses the checked-in [configuration](../../ops/prometheus/prometheus.yml), a 15-second scrape interval and 15-day local retention. This setting is a local storage limit, not a production retention or backup policy.

## Start and stop

The default Fake provider needs no key or paid service. The application can run without Prometheus:

```powershell
docker compose --env-file .env.example -f docker-compose.production-like.yml config --quiet
docker compose --env-file .env.example -f docker-compose.production-like.yml up -d --build --wait
Invoke-RestMethod http://127.0.0.1:8080/api/ready
docker compose --env-file .env.example -f docker-compose.production-like.yml down
```

Enable local monitoring explicitly:

```powershell
docker compose --env-file .env.example -f docker-compose.production-like.yml --profile observability config --quiet
docker compose --env-file .env.example -f docker-compose.production-like.yml --profile observability up -d --build --wait
Invoke-RestMethod http://127.0.0.1:8080/api/health
Invoke-RestMethod http://127.0.0.1:8080/api/ready
Invoke-RestMethod http://127.0.0.1:9090/api/v1/targets
python scripts/validate_observability_stack.py
docker compose --env-file .env.example -f docker-compose.production-like.yml --profile observability down
```

The validation script checks frontend/API routing, readiness, six quality-scorecard sections, Prometheus health and scraping, a recorded request metric, and the public 404 boundary for `/api/metrics`. Prometheus may take one scrape interval to show new samples; the script waits up to 90 seconds. Open `http://127.0.0.1:9090/` for the local Prometheus UI. A query such as `ai_quality_http_requests_total` displays bounded operational labels. Use `docker compose --env-file .env.example -f docker-compose.production-like.yml --profile observability logs --tail 100` when startup fails.

Normal `down` and container recreation preserve the named `app_data` and `prometheus_data` volumes. Do not use `down -v` for routine shutdown; it removes those volumes. The host `.data` directory used by local scripts and the API container's `app_data` volume are separate storage locations.

## Operational metric contract

| Metric | Type | Labels |
| --- | --- | --- |
| `ai_quality_http_requests_total` | Counter | Bounded method, registered route template, status class. |
| `ai_quality_http_request_duration_seconds` | Histogram | Bounded method and route template; fixed latency buckets. |
| `ai_quality_readiness` | Gauge | No labels; 1 for the last ready result, 0 otherwise. |

Metrics scraping does not count as an application request. Raw URLs, query strings, run IDs, artifact IDs, user input, prompts, document content, credentials, provider URLs and exception messages are excluded from labels. These metrics describe HTTP operations; rich AI quality records remain in application telemetry.

## Evaluation artifacts and quality scorecards

Running `uv run python scripts/run_ai_evaluation_pipeline.py --fail-on-warning` writes the existing full local report to `.data/ai-evaluation-pipeline-report.json` and a separate sanitized JSON artifact under `STORAGE_BASE_DIR/evaluation-artifacts/<artifact-id>.json`. Calling `POST /evals/ci/pipeline/run` also persists a sanitized artifact. In the production-like API container, that directory is `/app/.data/evaluation-artifacts/` on `app_data`. The GitHub Actions report upload remains attached to the workflow run and is independent of the local persistent artifact.

The artifact contract includes an opaque generated ID, timestamp, source, status, numeric score and counts, stage names/statuses/scores, and derived safe risks/recommendations. It omits raw stage output, prompts, request metadata and provider payloads. Writes are atomic. IDs must match 32 lowercase hexadecimal characters; malformed IDs are rejected, and missing valid IDs return 404. The API offers:

| API route | Result |
| --- | --- |
| `GET /evals/artifacts?limit=20` | Newest summaries and total count; limit 1–100. |
| `GET /evals/artifacts/latest` | Most recent artifact or 404. |
| `GET /evals/artifacts/{artifact_id}` | One safe artifact or 404. |
| `GET /observability/quality-scorecards` | Six deterministic quality sections and latest artifact summary. |

Under the Nginx web origin, prefix these paths with `/api`. For example, `Invoke-RestMethod http://127.0.0.1:8080/api/evals/artifacts` lists artifacts created inside the API container. A local script artifact in host `.data` is not automatically visible to the container because the two storage roots differ.

Scorecard sections cover evaluation quality, retrieval quality, agent reliability, multi-agent reliability, usage/cost and operational readiness. A quality section's status reflects the latest meaningful observation within the last seven days; no recent evidence yields `no_data`. Quality trends compare the warning/failed rate in the most recent seven days with the previous seven days and need at least one observation in both windows. Usage/cost reports a warning when a recent cost estimate is missing; readiness uses the existing local readiness checks. Those two sections report `insufficient_data` for quality trend rather than presenting cost movement or a single readiness snapshot as a comparable quality score. The endpoint does not call an LLM or Prometheus.

The existing Observability Center shows section states, trends, freshness and the latest artifact summary. The Evaluation Center shows its scorecard plus selectable recent artifact summaries, stage details and sanitized risks/recommendations. The existing dashboard refresh controls trigger new reads; Execution History remains its own view.

## Validation and troubleshooting

The main CI workflow runs `API tests`, `Web lint and build`, `Production-like stack` and `Observability stack`; the separate workflow runs `Deterministic AI evaluation pipeline`. The observability job checks Compose/Prometheus configuration, starts the optional profile with the Fake provider, and runs `scripts/validate_observability_stack.py`. No OpenAI key, Ollama service or paid API is required.

For local source validation, run `uv run pytest` from the repository root. Then use `Push-Location apps/web`, run `npm run lint` and `npm run build`, and `Pop-Location`. Run the pipeline command above to confirm local artifact creation; list the resulting `.data/evaluation-artifacts/*.json` files. Use the API artifact endpoints when validating artifacts in the container volume.

If Prometheus is healthy but its target is down, inspect `docker compose --env-file .env.example -f docker-compose.production-like.yml --profile observability logs --tail 100 prometheus api` and confirm API readiness. A newly started target may need a scrape interval. If the browser receives metrics at `/api/metrics`, the Nginx boundary is broken and the stack should not be exposed. If scorecards show `no_data` or `insufficient_data`, inspect the latest-observation time and collect representative telemetry before using trends for release decisions.

This pack does not add external log aggregation, alert delivery, distributed tracing, a cloud monitoring service, production data backups, authentication, multi-user isolation, production database storage, persistent agent state or public hosting. The local JSONL/artifact stores and Prometheus volume are single-instance demonstration facilities, not a production recovery strategy. See the [strategy](../architecture/production-observability-strategy.md) for design constraints and the [deployment runbook](../deployment/runbook.md) for the application-only deployment boundary.
