FROM python:3.10-slim

WORKDIR /app
COPY inference/ .

RUN pip install --upgrade pip && \
    pip install catboost && \
    pip install google-cloud-storage && \
    pip install pandas && \
    pip install fastapi==0.75.0 uvicorn

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
