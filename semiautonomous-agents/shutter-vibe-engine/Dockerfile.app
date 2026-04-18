FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg ca-certificates && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY envato/requirements.app.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY demos/_client.py /app/demos/_client.py
COPY envato/app_v2.py /app/envato/app_v2.py
COPY envato/templates /app/envato/templates
COPY envato/static /app/envato/static

ENV PYTHONUNBUFFERED=1 \
    GOOGLE_GENAI_USE_VERTEXAI=True \
    GOOGLE_CLOUD_PROJECT=vtxdemos \
    GOOGLE_CLOUD_LOCATION=us-central1 \
    ENVATO_GCS_BUCKET=envato-vibe-demo \
    PORT=8080

EXPOSE 8080
CMD ["uvicorn", "envato.app_v2:app", "--host", "0.0.0.0", "--port", "8080"]
