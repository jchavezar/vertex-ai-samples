FROM python:3.12-slim

WORKDIR /app

# Install uv package manager (pinned version)
COPY --from=ghcr.io/astral-sh/uv:0.5.11 /uv /uvx /bin/

# Copy requirements first (layer caching)
COPY requirements.txt .

# Install dependencies with uv
RUN uv pip install --system --no-cache -r requirements.txt

# Copy application code
COPY server.py auth.py graph_client.py ./
COPY tools/ tools/

# Run as non-root user
RUN useradd -m -u 1001 appuser
USER appuser

EXPOSE 8080

CMD ["python", "server.py"]
