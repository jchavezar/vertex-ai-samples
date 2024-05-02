FROM python:3.10

COPY requirements.txt .

RUN apt-get update
RUN apt-get install poppler-utils -y
RUN pip install -r requirements.txt

COPY utils utils
COPY tmp/ask_your_doc.py .

EXPOSE 8080

CMD ["python", "./ask_your_doc.py"]