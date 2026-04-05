# SharePoint WIF Portal - Combined Dockerfile
# Combines frontend (nginx) and backend (FastAPI) in a single container

# ============================================
# Stage 1: Build Frontend
# ============================================
FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend

# Copy package files
COPY frontend/package*.json ./

# Install dependencies
RUN npm ci

# Copy source
COPY frontend/ .

# Build production bundle
RUN npm run build

# ============================================
# Stage 2: Build Backend Dependencies
# ============================================
FROM python:3.12-slim AS backend-builder

WORKDIR /app/backend

# Install uv
RUN pip install uv

# Copy dependency files
COPY backend/pyproject.toml ./
COPY backend/uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-dev

# ============================================
# Stage 3: Production Image
# ============================================
FROM python:3.12-slim

# Install nginx and supervisor
RUN apt-get update && \
    apt-get install -y --no-install-recommends nginx supervisor && \
    rm -rf /var/lib/apt/lists/* && \
    rm /etc/nginx/sites-enabled/default

# Install uv
RUN pip install uv

# Copy backend with dependencies
WORKDIR /app/backend
COPY --from=backend-builder /app/backend/.venv /app/backend/.venv
COPY backend/ .

# Copy frontend build
COPY --from=frontend-builder /app/frontend/dist /usr/share/nginx/html

# Copy deployment configs
COPY deploy/nginx.conf /etc/nginx/sites-enabled/default
COPY deploy/supervisord.conf /etc/supervisor/conf.d/app.conf

# Create log directory
RUN mkdir -p /var/log/supervisor

# Expose Cloud Run port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Start supervisor (manages nginx + backend)
CMD ["supervisord", "-n", "-c", "/etc/supervisor/supervisord.conf"]
