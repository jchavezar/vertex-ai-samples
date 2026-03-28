FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY mcp_server.py .

# Run as non-root user
RUN useradd -m -u 1001 appuser
USER appuser

EXPOSE 8080

CMD ["python", "mcp_server.py"]
