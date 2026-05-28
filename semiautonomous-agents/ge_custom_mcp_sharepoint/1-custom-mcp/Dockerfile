FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY server.py auth.py graph_client.py doc_reader.py ./
COPY tools/ tools/

RUN useradd -m -u 1001 appuser
USER appuser

EXPOSE 8080
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8080"]
