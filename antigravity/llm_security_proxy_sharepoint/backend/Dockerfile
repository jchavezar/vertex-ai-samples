FROM python:3.12-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Copy dependency files
copy pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-cache

# Copy application code
copy . .

# Expose the port (Cloud Run sets PORT env var)
EXPOSE 8080

# Run the MCP server
# We use uv run to ensure the environment is correctly activated
CMD ["uv", "run", "python", "mcp_server.py"]
