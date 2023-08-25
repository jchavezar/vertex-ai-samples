FROM python:3.10

WORKDIR /app

COPY style.css .
COPY ai /app/ai
COPY credentials.py .
COPY google_database.py .
COPY front_search_engine_embeddings.py .
COPY requirements.txt .

RUN pip install -r requirements.txt

EXPOSE 8080

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "search_engine_embeddings.py", "--server.port=8080", "--server.address=0.0.0.0"]