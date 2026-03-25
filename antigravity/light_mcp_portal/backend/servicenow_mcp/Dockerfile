# Use the official Python image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# Set working directory
WORKDIR /app

# Copy requirement files (if any) or install dependencies directly
# ServiceNow MCP depends on FastMCP and requests
RUN pip install --no-cache-dir fastmcp requests pyjwt

# Copy the server files
COPY . .

# Expose the port
EXPOSE 8080

# Command to run the SSE server
CMD ["python", "mcp_server_servicenow_sse.py"]
