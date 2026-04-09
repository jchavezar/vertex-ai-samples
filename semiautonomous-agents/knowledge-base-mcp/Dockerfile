FROM python:3.12-slim

WORKDIR /app

# Install uv for fast dependency management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy project files
COPY pyproject.toml .
COPY server.py .
COPY firestore_client.py .
COPY embeddings.py .
COPY tools/ tools/
COPY pipeline/ pipeline/

# Install dependencies
RUN uv pip install --system --no-cache .

# Run as non-root user
RUN useradd -m -u 1001 appuser
USER appuser

EXPOSE 8080

CMD ["python", "server.py"]
