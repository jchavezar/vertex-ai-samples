FROM python:3.12-slim

# Install uv (using pip to keep it simple and independent)
RUN pip install uv

# Install system dependencies for WeasyPrint and pydub
RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libffi-dev \
    libcairo2 \
    shared-mime-info \
    libglib2.0-0 \
    libgdk-pixbuf-2.0-0 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

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

# Run the Security Proxy server
CMD ["python", "main.py"]
