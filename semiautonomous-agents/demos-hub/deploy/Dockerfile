FROM python:3.12-slim

WORKDIR /app

COPY app/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY app/         /app/app/
COPY static/      /app/static/

ENV PYTHONUNBUFFERED=1 \
    PORT=8080

EXPOSE 8080
WORKDIR /app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
