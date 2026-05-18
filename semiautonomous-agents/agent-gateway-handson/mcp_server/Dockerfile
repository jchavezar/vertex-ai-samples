FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN groupadd -g 65532 nonroot && \
    useradd -u 65532 -g 65532 -s /bin/false nonroot

WORKDIR /app

COPY pyproject.toml uv.lock* ./
RUN uv sync --frozen --no-dev || uv sync --no-dev

COPY . .

USER 65532:65532

EXPOSE 8080

CMD [".venv/bin/uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8080"]
