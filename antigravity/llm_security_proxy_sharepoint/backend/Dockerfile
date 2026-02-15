FROM python:3.12-slim

# Install uv (using pip to keep it simple and independent)
RUN pip install uv

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml ./

# Install dependencies using public PyPI to avoid corp airlock registry issues
RUN uv pip install --system -r pyproject.toml --index-url https://pypi.org/simple

# Copy application code
COPY . .

# Expose the port (Cloud Run sets PORT env var)
EXPOSE 8080

# Run the MCP server
CMD ["python", "mcp_server.py"]
