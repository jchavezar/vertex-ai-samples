FROM python:3.10-slim

WORKDIR /app

RUN mkdir .streamlit
COPY Main.py Main.py
COPY utils/ utils
COPY pages/ pages
COPY images/ images
COPY files/ files
COPY requirements.txt .
COPY .streamlit/config.toml .streamlit/config.toml
COPY k.py k.py

RUN apt-get update
RUN pip install --upgrade pip
RUN pip install pandas --upgrade
RUN pip install -r requirements.txt

EXPOSE 8080

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "Main.py", "--server.port=8080", "--server.address=0.0.0.0"]