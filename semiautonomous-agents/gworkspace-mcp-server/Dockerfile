FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir fastmcp requests uvicorn google-cloud-storage

# Copy application code
COPY . .

# Set environment variables
ENV PORT=8080
ENV MCP_TRANSPORT=streamable-http

EXPOSE 8080

CMD ["python", "server.py"]
