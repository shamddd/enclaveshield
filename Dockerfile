# Multi-stage Dockerfile for Confidential Computing Research Framework
FROM python:3.12-slim AS builder

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml .
COPY src /app/src

RUN uv venv /app/.venv && uv pip install --no-cache-dir .

FROM python:3.12-slim AS runner

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
COPY src /app/src
COPY scripts /app/scripts
COPY docs /app/docs

ENV PATH="/app/.venv/bin:${PATH}"
ENV PYTHONPATH="/app/src"

EXPOSE 8000

CMD ["uvicorn", "cc_framework.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
