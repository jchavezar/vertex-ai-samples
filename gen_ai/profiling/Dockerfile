# app/Dockerfile

FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt ./requirements.txt
COPY profiling.py  ./profiling.py
COPY ai.py ./ai.py
COPY utils.py ./utils.py
COPY cred.yaml ./cred.yaml

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*


RUN pip3 install -r requirements.txt

EXPOSE 8080

HEALTHCHECK CMD curl --fail http://localhost:8080/_stcore/health

ENTRYPOINT ["streamlit", "run", "profiling.py", "--server.port=8080", "--server.address=0.0.0.0"]