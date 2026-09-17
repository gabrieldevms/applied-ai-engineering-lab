# Production-like Deployment Runbook

This runbook starts the AI Quality Command Center as a local, production-like stack. It is a deployment rehearsal, not a public production deployment. See the [deployment strategy](../architecture/deployment-strategy.md) for the architecture and its boundaries.

## Prerequisites and topology

From a fresh clone, use a running Docker Engine with Docker Compose v2. Run the commands below from the repository root in PowerShell. The stack builds the frontend with Node 22, serves the assets from Nginx, and runs the FastAPI application with Uvicorn without reload. It does not require locally installed Python, Node.js, `uv`, OpenAI credentials or Ollama. Those tools are needed only for the separate source-level validation commands below.

```text
Browser at 127.0.0.1:8080
  -> web (Nginx)
       /       -> built React application
       /api/*  -> api (FastAPI), with /api removed
```

Only the web service binds a host port, at `127.0.0.1:8080`. The API listens on port 8000 inside the Compose network. The original `docker-compose.yml` remains a development API service with a source bind mount and `--reload`; it is not the production-like stack.

## Configuration

The checked-in `.env.example` selects the deterministic Fake LLM provider. Compose reads it for variable substitution in the commands below. Shell environment variables take precedence over values in the env file, so check provider-related variables in the current shell before starting if you use multiple providers. Do not commit a local `.env` file or an API key.

The production-like Compose file fixes `APP_ENV=local`, `STORAGE_BACKEND=local_jsonl` and `STORAGE_BASE_DIR=/app/.data` inside the API container. The default agent execution log path follows that storage root. It passes only the selected LLM provider, OpenAI key/model and Ollama URL/model from the environment. Other settings use backend defaults. `APP_ENV` is a label, not an authorization control.

| Provider | Configuration and behavior |
| --- | --- |
| Fake | Default. No credentials, external service or paid inference. Use for stack validation and CI. |
| OpenAI | Set `LLM_PROVIDER=openai`, `OPENAI_API_KEY` and `OPENAI_MODEL` in a local, untracked env file. Requests may transmit data and incur cost. Only the API container receives these values. |
| Ollama | Set `LLM_PROVIDER=ollama`, a reachable `OLLAMA_MODEL` and `OLLAMA_BASE_URL=http://host.docker.internal:11434` when Ollama runs on the Docker host. `localhost` inside the API container is the container itself. |

To use a local env file, copy `.env.example` to `.env`, edit it without committing it, and replace `--env-file .env.example` with `--env-file .env` in the commands. The frontend build has no provider key or backend host setting; browser requests remain relative to `/api`.

## Build, start and inspect

```powershell
docker compose --env-file .env.example -f docker-compose.production-like.yml config --quiet
docker compose --env-file .env.example -f docker-compose.production-like.yml build api web
docker compose --env-file .env.example -f docker-compose.production-like.yml up -d --wait
docker compose --env-file .env.example -f docker-compose.production-like.yml ps
```

`up --wait` succeeds after the API readiness check and the web health check pass. Open `http://127.0.0.1:8080/` in a browser. Nginx preserves React client-side routes and forwards `/api/*` to FastAPI after removing `/api`.

Check the local signals in PowerShell:

```powershell
(Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8080/).StatusCode
Invoke-RestMethod http://127.0.0.1:8080/health
Invoke-RestMethod http://127.0.0.1:8080/api/health
Invoke-RestMethod http://127.0.0.1:8080/api/ready
Invoke-RestMethod http://127.0.0.1:8080/api/observability/dashboard
```

`/health` at the web origin is the Nginx health signal. `/api/health` is the API liveness signal and returns `{"status":"ok"}`. `/api/ready` returns HTTP 200 with `status: ready` when settings load, the selected LLM provider has coherent local configuration, and the configured JSONL storage root and agent-log directory are writable. It returns HTTP 503 with `status: not_ready` and `ok`, `failed` or `skipped` check statuses when a requirement fails. With in-memory storage, the storage check is skipped. Readiness does not contact OpenAI or Ollama, run an agent, execute SQL, or test external network reachability. Responses do not include credentials or internal provider URLs.

The API's interactive `/docs` page is available directly in the development API workflow. The production-like proxy is designed around `/api` application calls; the docs UI is not part of the validated proxy route contract.

## Persistence and lifecycle

The named Docker volume `app_data` is mounted at `/app/.data`. Local JSONL observability and security records, along with the default agent execution log, survive normal container recreation and `docker compose down`. The volume does not make in-memory RAG vectors, transient agent state or browser page state durable. JSONL storage is intended for one local API instance; it has no cross-instance coordination, backup policy or production retention policy.

```powershell
docker compose --env-file .env.example -f docker-compose.production-like.yml logs --tail 100 api
docker compose --env-file .env.example -f docker-compose.production-like.yml logs --tail 100 web
docker compose --env-file .env.example -f docker-compose.production-like.yml restart
docker compose --env-file .env.example -f docker-compose.production-like.yml down
```

`restart` does not rebuild changed images. After changing code or configuration, use `up -d --build --wait`. Do not use `down -v` for routine shutdown: it deletes the named data volume. Keep secrets and real user data out of this local rehearsal.

## Validation and troubleshooting

For source-level validation, install Python 3.12+, `uv`, Node.js and npm. These commands run independently of the container stack:

```powershell
uv run pytest
Push-Location apps/web
npm ci
npm run lint
npm run build
Pop-Location
```

The main CI workflow runs backend tests, frontend lint/build, Compose validation, both image builds and a Fake-provider stack smoke test. The separate AI Evaluation Pipeline remains a deterministic quality gate.

If `up --wait` fails, inspect `docker compose ... ps` and `logs --tail 100 api` or `logs --tail 100 web` using the full command prefix above. A 503 from `/api/ready` identifies a failed check without exposing a path or secret. `provider: failed` means the selected provider lacks required local settings. `storage: failed` means the storage root or agent-log directory is unavailable or unwritable. For Ollama, a ready result only confirms local configuration; verify model/service reachability separately before running workflows. A busy host port 8080 also prevents the web container from starting.

## Cloud-readiness boundary

Pack 1 provides:

- [x] A provider-neutral, same-origin web/API boundary and production-like local images.
- [x] A persistent local volume for supported JSONL records.
- [x] Separate liveness and readiness signals.
- [x] CI coverage for backend, frontend and container builds with a local stack smoke test.

Before any restricted staging or public production hosting, evaluate the target platform and add the controls appropriate to its exposure:

- [ ] Choose a provider and validate its ingress, TLS, runtime secret injection and deployment process.
- [ ] Define authentication, access control and multi-user isolation before broad access.
- [ ] Replace or harden single-instance JSONL persistence with backup, retention and recovery appropriate to real data.
- [ ] Add production monitoring, alerting and operational response procedures.
- [ ] Review data handling, audit retention and security controls for the intended users and workloads.

Provider-specific infrastructure, PostgreSQL, production vector storage, persistent agent memory and session resume, a production secrets manager, OpenTelemetry/external monitoring, Kubernetes, Terraform, production MCP hosting, external SQL/NoSQL integrations and additional LLM providers are outside Pack 1. The current stack must not be exposed as an unrestricted public service or used for real customer data.
