# Deployment container — handles all Agent Engine/RAG/Firestore deployments
# Uses explicit service account credentials to avoid ADC auto-discovery conflicts
FROM python:3.12-slim

# Install gcloud SDK
RUN apt-get update && apt-get install -y curl gnupg && \
    echo "deb https://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list && \
    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add - && \
    apt-get update && apt-get install -y google-cloud-sdk && \
    rm -rf /var/lib/apt/lists/*

# Install uv (fast Python package manager)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# Pre-install common deployment dependencies
RUN pip install --no-cache-dir \
    google-cloud-aiplatform[adk,agent_engines] \
    google-cloud-firestore \
    google-cloud-storage \
    google-genai \
    requests

WORKDIR /workspace

# Entrypoint expects service account key at /secrets/sa-key.json
# Set explicitly to avoid auto-discovery
ENV GOOGLE_APPLICATION_CREDENTIALS=/secrets/sa-key.json

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
