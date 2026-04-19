FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg ca-certificates && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY multimodal-search/app/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# `_client.py` lives outside this folder (shared across demos in this repo).
# main.py picks it up via the /app/demos fallback.
COPY demos/_client.py /app/demos/_client.py

COPY multimodal-search/app/main.py        /app/multimodal-search/app/main.py
COPY multimodal-search/app/templates      /app/multimodal-search/app/templates
COPY multimodal-search/app/static         /app/multimodal-search/app/static

ENV PYTHONUNBUFFERED=1 \
    GOOGLE_GENAI_USE_VERTEXAI=True \
    GOOGLE_CLOUD_PROJECT=vtxdemos \
    GOOGLE_CLOUD_LOCATION=us-central1 \
    ENVATO_GCS_BUCKET=envato-vibe-demo \
    PORT=8080

EXPOSE 8080
WORKDIR /app/multimodal-search/app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
