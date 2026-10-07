FROM python:3.11-slim

WORKDIR /app

COPY requirements.cloud.txt .
RUN pip install --no-cache-dir -r requirements.cloud.txt

COPY cloud_gateway.py .

ENV PORT=8080
ENV MOUNTED_DB_PATH=/mnt/memory/ground_truth.db
ENV GCP_PROJECT=vtxdemos
ENV GEMINI_MODEL=gemini-3.8-flash

CMD ["uvicorn", "cloud_gateway:app", "--host", "0.0.0.0", "--port", "8080"]
