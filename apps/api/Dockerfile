FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/apps/api/src

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-dev

COPY apps/api/src ./apps/api/src

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "ai_api.main:app", "--host", "0.0.0.0", "--port", "8000", "--app-dir", "apps/api/src"]