# ==============================================================================
# Production Dockerfile for Mike-GCP Enterprise Legal AI Platform
# Multi-stage build with non-root security context (UID 10001) for Google Cloud Run
# ==============================================================================

# Stage 1: Build & Dependency Resolution
FROM python:3.12-slim AS builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install uv for deterministic high-speed package resolution
RUN pip install --no-cache-dir uv

# Copy package manifests and source files required by hatchling wheel build
COPY pyproject.toml README.md ./
COPY app.py telemetry.py spanner_engine.py agent_engine.py adk_agents.py demo_data.py ui_template.py generate_scaled_corpus.py generate_multimodal_corpus.py multimodal_extraction_pipeline.py ingest_and_benchmark.py ./

# Install dependencies into system site-packages
RUN uv pip install --system --no-cache .

# ------------------------------------------------------------------------------
# Stage 2: Hardened Runtime Container
# ------------------------------------------------------------------------------
FROM python:3.12-slim AS runner

WORKDIR /app

# Install runtime curl for health probes
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create dedicated non-root application user
RUN groupadd -g 10001 appgroup && \
    useradd -u 10001 -g appgroup -s /bin/bash -m appuser

# Copy installed site-packages from builder stage
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application source code with non-root ownership
COPY --chown=appuser:appgroup . .

# Set strict production environment defaults
ENV PORT=8080
ENV HOST=0.0.0.0
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV OTEL_TO_CLOUD=true
ENV VERTEX_LOCATION=global
ENV DEFAULT_CHAT_MODEL=gemini-3.8-flash
ENV REASONING_CHAT_MODEL=gemini-3.7-flash

# Cloud Run Container Port
EXPOSE 8080

# Switch to non-root user for principle of least privilege
USER appuser

# Health check using the production readiness probe
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8080/health/readiness || exit 1

# Production ASGI server with uvicorn workers
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "4", "--limit-concurrency", "100", "--timeout-keep-alive", "65"]
