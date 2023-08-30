FROM python:3.10

WORKDIR /app

COPY style.css .
COPY utils/ /app/utils
COPY front_search_multimodal.py .
COPY requirements.txt .

RUN pip install -r requirements.txt

EXPOSE 8080

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "front_search_multimodal.py", "--server.port=8080", "--server.address=0.0.0.0"]