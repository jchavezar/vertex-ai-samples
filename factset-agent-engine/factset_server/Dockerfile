FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY server.py .
COPY factset_tools_schema.json .

ENV PORT 8080
EXPOSE 8080

CMD ["python", "server.py"]
