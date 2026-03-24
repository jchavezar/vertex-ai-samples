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
# We copy everything so `uv sync` has access to the full application code if needed.
COPY . .

# Copy built frontend step
COPY --from=build-frontend /app/dist ./dist

# Install uv and sync pyproject.toml
RUN pip install uv && cd backend && uv pip install --system -r pyproject.toml

# Create a local env for Vertex AI if it exists
ENV PORT=8080
EXPOSE 8080

# Start server
WORKDIR /app/backend
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
