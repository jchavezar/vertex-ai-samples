#FROM nvidia/cuda:11.8.0-devel-ubuntu22.04
FROM pytorch/pytorch:1.12.1-cuda11.3-cudnn8-devel

# Install base utilities
RUN apt update && apt upgrade -y && \
    apt install curl -y && \
    apt install build-essential manpages-dev -y  && \
    apt-get install -y wget && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install miniconda
RUN pip install google-cloud-language --upgrade && pip install ipykernel && \
    pip install pandas --upgrade && pip install gcsfs && pip install gdown

RUN pip install tensorflow
RUN pip install tensorflow && pip install google-cloud-bigquery && \
     pip install google-cloud-pipeline-components==2.0.0b1 && \
     pip install kfp==2.0.0b14 && \
     pip install google-cloud-aiplatform --pre && \
     pip install ipykernel && \
     pip install pyarrow

RUN apt-get install apt-transport-https ca-certificates gnupg
RUN echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list
RUN curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key --keyring /usr/share/keyrings/cloud.google.gpg add -
RUN apt-get update && apt-get install google-cloud-cli
RUN pip install boto3
RUN pip install pytorch_tabular[extra]