FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir \
    fastmcp>=2.0.0 \
    google-cloud-firestore>=2.19.0 \
    google-cloud-secret-manager>=2.21.0 \
    google-genai>=1.0.0 \
    requests>=2.32.0

# Copy application code
COPY amex_job/ amex_job/
COPY enrichment/ enrichment/
COPY mcp_server/ mcp_server/

# Set environment variables
ENV PORT=8080
ENV FASTMCP_PORT=8080
ENV FASTMCP_HOST=0.0.0.0
ENV FASTMCP_TRANSPORT=streamable-http
ENV GCP_PROJECT_ID=vtxdemos

EXPOSE 8080

CMD ["python", "mcp_server/server.py"]
