# Stage 1: Build the React frontend
FROM node:20 as build-frontend
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Stage 2: Serve with Fastapi
FROM python:3.11-slim
WORKDIR /app

# Install dependencies via uv
COPY backend/pyproject.toml backend/uv.lock* ./
RUN pip install uv && uv pip install --system fastapi uvicorn google-genai pydantic sse-starlette python-dotenv

# Copy everything else
COPY backend ./backend

# Copy built frontend step
COPY --from=build-frontend /app/dist ./dist

# Create a local env for Vertex AI if it exists
ENV PORT=8080

EXPOSE 8080

# Start server
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8080"]
