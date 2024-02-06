FROM python:3.10-slim

WORKDIR /app

RUN mkdir .streamlit
COPY . .
#COPY Main.py Main.py
#COPY utils/ utils
#COPY pages/ pages
#COPY images/ images
#COPY files/ files
COPY requirements.txt .
COPY config.toml .streamlit/config.toml
#COPY k.py k.py
#COPY passcode.py passcode.py
RUN apt-get update
RUN pip install --upgrade pip
RUN pip install pandas --upgrade
RUN pip install -r requirements.txt
RUN pip install -r utils/crewai/requirements.txt
RUN pip install -U google-cloud-aiplatform "shapely<2"
COPY libraries/crewai/crew.py /usr/local/lib/python3.10/site-packages/crewai/crew.py
COPY libraries/crewai/agent.py /usr/local/lib/python3.10/site-packages/crewai/agent.py

COPY google_analytics.html /usr/local/lib/python3.10/site-packages/streamlit/static/index.html

EXPOSE 8080

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

CMD ["streamlit", "run", "main.py", "--server.port=8080", "--server.address=0.0.0.0"]