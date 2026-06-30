FROM python:3.12-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY policy.py main.py ./

# Cloud Run injects PORT; default to 8080 locally.
ENV PORT=8080

CMD exec uvicorn main:app --host 0.0.0.0 --port ${PORT} --workers 1
