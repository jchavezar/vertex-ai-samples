FROM python:3.10

WORKDIR /app

COPY bq_llm.py .
COPY . .

RUN pip install -r requirements.txt

EXPOSE 8080

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "bq_llm.py", "--server.port=8080", "--server.address=0.0.0.0"]