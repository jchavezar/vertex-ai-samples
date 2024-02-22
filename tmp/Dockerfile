FROM pytorch/pytorch:1.12.1-cuda11.3-cudnn8-devel

WORKDIR /app
COPY inference/ .

RUN pip install pytorch_tabular[extra]
RUN pip install uvicorn fastapi
RUN pip install gcsfs

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]