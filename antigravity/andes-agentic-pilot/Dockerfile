# syntax=docker/dockerfile:1.7
# ---- Stage 1: build the Vite SPA -------------------------------------------
FROM node:22-alpine AS web
WORKDIR /web
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci --no-audit --no-fund
COPY frontend/ ./
# Empty VITE_API_BASE => same-origin /api calls in production.
ENV VITE_API_BASE=""
RUN npm run build

# ---- Stage 2: FastAPI runtime ----------------------------------------------
FROM python:3.12-slim AS api
WORKDIR /app

# uv for fast, reproducible installs from the existing uv.lock.
RUN pip install --no-cache-dir uv==0.5.20

COPY backend/pyproject.toml backend/uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY backend/main.py ./main.py
COPY --from=web /web/dist ./static

ENV SPA_DIR=/app/static \
    PORT=8080 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

EXPOSE 8080
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
