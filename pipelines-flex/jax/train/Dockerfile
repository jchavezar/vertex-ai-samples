FROM python:3.10

RUN apt-get update -y
RUN pip install --upgrade pip
RUN pip install -U google-cloud-bigquery google-cloud-storage jax scikit-learn pandas db-dtypes
RUN pip install google-cloud-secret-manager==2.10.0 snowflake-connector-python snowflake-connector-python[pandas]

COPY main.py .
CMD ["python", "main.py"]