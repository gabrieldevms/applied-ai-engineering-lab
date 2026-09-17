# Cloud and Deployment Strategy

## Scope and decision

Pack 1 prepares the AI Quality Command Center for production-like local execution and future cloud deployment. It does not select a cloud provider or publish the application publicly. The existing FastAPI services, React application, provider abstractions and local-first storage model remain in place.

The deployment boundary is a same-origin web entry point. The browser continues to request relative `/api/...` URLs. A web server serves the built React application at `/` and forwards `/api/*` to the internal FastAPI workload after removing `/api`. The FastAPI routes keep their current paths, such as `/health` and `/observability/dashboard`.

```text
Browser
  |
  v
Web / reverse proxy (public entry point)
  |-- /       -> React static assets
  `-- /api/*  -> internal FastAPI service, with /api removed
```

The frontend and backend remain separate workloads internally. For the local production-like stack, the web workload uses Nginx for static serving and reverse proxying; the API uses Uvicorn without development reload. Nginx is an infrastructure choice for this stack, not an application framework dependency. A future hosting platform can replace the web server while preserving the external URL contract.

This topology keeps browser requests on one origin, avoids a frontend API host setting and avoids adding CORS solely for deployment. `VITE_API_BASE_URL` is not needed for the selected topology. The API is reachable from the web workload on a private container network; the browser does not connect to the API container directly.

## Execution environments

| Environment | Execution path | Exposure |
| --- | --- | --- |
| Local development | Vite on port 5173 proxies `/api` to locally running FastAPI on port 8000. The existing Docker Compose API service remains a development option. | Developer machine only. |
| Production-like local | Built React assets and FastAPI run in separate containers behind the web reverse proxy. Only the web entry point is published. | Local machine for validation and demonstrations. |
| Future staging or cloud | The same web/API boundary can run behind a platform ingress with TLS and environment-specific runtime configuration. | Private or restricted until authentication and operational controls are implemented. |

The production-like local stack is a deployment rehearsal, not a claim of production readiness. No provider-specific manifests or infrastructure are part of Pack 1.

## Configuration and secret boundaries

The backend owns provider and storage configuration through environment variables. The default Fake LLM and Fake embedding providers remain valid, deterministic, credential-free settings for local runs and CI. The production-like stack should configure `STORAGE_BACKEND=local_jsonl` and an explicit storage root within the mounted data volume. The legacy agent execution log path must also resolve inside that volume so all supported local JSONL records survive normal container recreation.

The React build must not contain provider credentials or internal backend addresses. Runtime secrets, including `OPENAI_API_KEY`, belong only in the API environment and must not be copied into images, committed, logged or exposed through API status responses. Local `.env` files remain untracked. Future staging or cloud execution must inject secrets through the chosen platform's backend secret mechanism; selecting that mechanism is deferred until a platform is chosen.

Provider selection stays explicit:

- `fake` needs no external service and is the default for validation.
- `openai` requires a server-side key and model; enabling it may transmit data and incur cost. CI and stack smoke tests must not require it.
- `ollama` requires a reachable Ollama service and model. `localhost` inside a container refers to that container, so a containerized deployment needs an explicitly reachable address. It is not required for CI.

Environment labels are descriptive deployment configuration, not a substitute for tool authorization. Pack 1 does not grant broader tool access based on `APP_ENV`.

## Storage and availability

The production-like stack must mount a persistent Docker volume at the configured JSONL storage root. Normal container replacement must retain observability, security and agent execution log records. Removing the volume still removes the data. In-memory RAG vectors, agent state and transient frontend page state do not become persistent through this volume.

JSONL storage is suitable for a single local API instance. It has no cross-instance coordination, database transactions, retention policy or backup strategy. Future cloud evaluation must account for these limits before scaling or accepting real user data. A production database, persistent vector store and durable agent state belong to later packs.

## Liveness and readiness

`GET /health` remains a lightweight liveness check: it indicates that the API process can serve an HTTP response and does not depend on optional LLM providers or storage.

Pack 1 adds a separate readiness check, expected at `GET /ready`, for the minimum local requirements to serve configured workloads. It should validate loaded settings, coherent selected-provider configuration and the configured storage path when local persistence is enabled. Readiness must be deterministic, inexpensive and free of paid inference, agent execution or external network calls. Responses must not disclose secrets or internal provider URLs.

The web entry point should expose a simple local health signal. Container or ingress health checks can use the API readiness signal when deciding whether the stack is ready to receive traffic. An optional provider being unavailable must not invalidate an otherwise valid Fake-provider configuration.

## Build and CI expectations

The existing backend tests and deterministic AI evaluation pipeline remain quality gates. Pack 1 extends the main CI workflow to run frontend lint and build with the committed npm lockfile, build both container images, validate the production-like Compose configuration and, if stable, smoke-test routing and readiness with Fake providers. CI must not depend on paid APIs, OpenAI credentials or Ollama.

The production-like images should use reproducible dependency installation, omit source bind mounts and development reload, and keep runtime contents minimal. The existing local development commands remain available.

## Public deployment boundary and deferred work

The application currently lacks user authentication, access control, multi-user isolation, production secrets management, production-grade persistent storage, audit retention and external monitoring. It must not be treated as safe for unrestricted public access or real customer data after Pack 1. Production MCP hosting is also deferred.

Pack 1 does not introduce a cloud provider, Kubernetes, Terraform, a production database, vector database, persistent agent memory, external SQL connectors or new LLM providers. A provider-specific deployment can be evaluated after the production-like stack, health checks, CI and runbook have been validated.
