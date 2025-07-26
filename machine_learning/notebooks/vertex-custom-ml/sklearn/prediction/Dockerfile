FROM python:3.7

COPY requirements.txt .

RUN pip3 install --upgrade pip && \
   pip3 install -r requirements.txt

COPY api.py api.py

EXPOSE 8080

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8080"]