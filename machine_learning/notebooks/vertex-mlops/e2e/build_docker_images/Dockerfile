FROM nvidia/cuda:11.8.0-cudnn8-devel-ubuntu22.04
ARG DEBIAN_FRONTEND=noninteractive

COPY training/train.py train.py
COPY requirements.txt requirements.txt
RUN apt update -y
RUN apt-get install -y python3.10 && \
     apt-get install -y python3-pip
RUN pip install -r requirements.txt

CMD ["python3", "train.py"]
