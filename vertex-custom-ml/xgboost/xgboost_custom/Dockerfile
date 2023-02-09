FROM rapidsai/rapidsai-nightly:22.12-cuda11.2-base-ubuntu20.04-py3.8

RUN pip install google-cloud-storage \
  && pip install gcsfs \
  && pip install pandas \
  && pip install dask-bigquery

COPY trainer trainer/

ENTRYPOINT ["python", "trainer/train.py"]
