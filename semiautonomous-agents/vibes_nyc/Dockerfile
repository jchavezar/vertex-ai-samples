# Stage 1: Build the React frontend
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install && npm install --save-dev @types/google.maps
COPY frontend/ ./
# Production API URL is root (served by same process)
ENV VITE_API_BASE_URL=/
RUN npm run build

# Stage 2: Build the Python backend
FROM python:3.12-slim
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/cache/*

# Copy backend requirements and install
# We'll use a simple pip install for reliability in the container
COPY backend/pyproject.toml ./backend/
RUN pip install --no-cache-dir \
    fastapi[standard] \
    uvicorn \
    httpx \
    pydantic \
    python-dotenv \
    google-cloud-aiplatform[adk,agent_engines] \
    google-adk \
    sse-starlette \
    vertexai

# Copy source code
COPY .env .
COPY backend/ ./backend/
COPY agent/ ./agent/
# Copy the built frontend dist from stage 1
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Expose the port FastAPI will run on
EXPOSE 8080

# Run the application
# We set the working directory to backend to find main.py or use the module path
CMD ["python", "backend/main.py"]
