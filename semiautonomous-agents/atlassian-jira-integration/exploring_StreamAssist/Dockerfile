FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8080

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY main.py .
COPY static ./static

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT}"]
