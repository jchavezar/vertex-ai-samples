FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PORT=8080

# system deps for pypdfium2 (no native build needed -- wheel ships .so)
RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# install uv
COPY --from=ghcr.io/astral-sh/uv:0.11.2 /uv /uvx /bin/

WORKDIR /app

# install deps first (better layer caching)
COPY pyproject.toml uv.lock /app/
RUN uv sync --frozen --no-install-project --no-dev

# now install the project
COPY src /app/src
RUN uv sync --frozen --no-dev

EXPOSE 8080

# Cloud Run sends one request per container; concurrency=1 in service config.
# Keep workers=1 so all asyncio tasks share one event loop and one Gemini client.
CMD ["uv", "run", "--no-sync", "uvicorn", "docparse.service:app", \
     "--host", "0.0.0.0", "--port", "8080", \
     "--workers", "1", "--timeout-keep-alive", "75"]
