FROM python:3.10.13

WORKDIR /app

COPY Main.py Main.py
COPY utils/ utils
COPY pages/ pages
COPY images/ images
COPY requirements.txt .

RUN apt-get update
RUN pip install --upgrade pip

RUN pip install -r requirements.txt

EXPOSE 8080

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "Main.py", "--server.port=8080", "--server.address=0.0.0.0"]