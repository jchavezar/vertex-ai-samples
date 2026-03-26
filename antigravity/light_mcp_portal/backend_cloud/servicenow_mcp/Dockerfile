# Use a lightweight Python base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies if required (uv uses them)
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Install uv for fast dependency resolution
RUN pip install uv

# Copy the requirements file
COPY requirements.txt .

# Install dependencies using uv
RUN uv pip install --system -r requirements.txt

# Copy the MCP server file
COPY mcp_server_servicenow.py .

# Ensure unbuffered output for standard logs
ENV PYTHONUNBUFFERED=1

# Expose default FastMCP port (Cloud Run sets PORT, usually 8080)
EXPOSE 8080

# Command to run FastMCP with SSE
CMD uv run fastmcp run mcp_server_servicenow.py:mcp --transport sse --host 0.0.0.0 --port ${PORT:-8080}
