FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
COPY main.py .

RUN pip install -r requirements.txt

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]