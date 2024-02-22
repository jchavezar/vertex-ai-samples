FROM python:3.10-slim

WORKDIR /app

RUN mkdir .streamlit
COPY requirements.txt requirements.txt
COPY config.toml .streamlit/config.toml
COPY utils/crewai/requirements.txt utils/crewai/requirements.txt
RUN apt-get update
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install -r utils/crewai/requirements.txt
RUN pip install crewai --upgrade
RUN pip install -U google-cloud-aiplatform "shapely < 2.0.0"
RUN pip install -U crewai
COPY . .
COPY libraries/crewai/utilities/logger.py /usr/local/lib/python3.10/site-packages/crewai/utilities/logger.py
COPY google_analytics.html /usr/local/lib/python3.10/site-packages/streamlit/static/index.html

EXPOSE 8080

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

CMD ["streamlit", "run", "main.py", "--server.port=8080", "--server.address=0.0.0.0", "--server.enableCORS=false"]