# Simple deployment container - Python + deployment deps
FROM python:3.12-slim

# Install deployment dependencies
RUN pip install --no-cache-dir \
    google-cloud-aiplatform[adk,agent_engines] \
    google-cloud-firestore \
    google-cloud-storage \
    google-genai \
    requests

WORKDIR /workspace

CMD ["/bin/bash"]
