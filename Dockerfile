FROM python:3.14-slim AS builder

WORKDIR /app

RUN pip install --no-cache-dir uv==0.13.5

COPY pyproject.toml uv.lock README.md ./
RUN uv sync --frozen --no-dev --no-install-project
COPY huerise/ ./huerise/
RUN uv sync --frozen --no-dev --no-editable


FROM python:3.14-slim

WORKDIR /app

COPY --from=builder /app/.venv .venv

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

CMD ["python", "-m", "uvicorn", "huerise.app:app", "--host", "0.0.0.0", "--port", "8000"]
