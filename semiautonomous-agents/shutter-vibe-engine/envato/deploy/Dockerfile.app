FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg ca-certificates && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY envato/app/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# `_client.py` lives outside `envato/` (shared across demos in this repo).
# main.py picks it up via the /app/demos fallback.
COPY demos/_client.py /app/demos/_client.py

COPY envato/app/main.py        /app/envato/app/main.py
COPY envato/app/templates      /app/envato/app/templates
COPY envato/app/static         /app/envato/app/static

ENV PYTHONUNBUFFERED=1 \
    GOOGLE_GENAI_USE_VERTEXAI=True \
    GOOGLE_CLOUD_PROJECT=vtxdemos \
    GOOGLE_CLOUD_LOCATION=us-central1 \
    ENVATO_GCS_BUCKET=envato-vibe-demo \
    PORT=8080

EXPOSE 8080
WORKDIR /app/envato/app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
