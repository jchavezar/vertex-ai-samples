FROM pytorch/pytorch:1.12.1-cuda11.3-cudnn8-devel

COPY . .
RUN pip install google-cloud-bigquery
RUN pip install db-dtypes
RUN pip install pandas
RUN pip install pytorch_tabular[extra]
RUN pip install gcsfs

ENTRYPOINT ["python", "train.py"]
