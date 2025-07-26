FROM nvidia/cuda:11.8.0-devel-ubuntu22.04

# Install base utilities
RUN apt update && apt upgrade -y && \
    apt install curl -y && \
    apt install build-essential manpages-dev -y  && \
    apt-get install -y wget && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install miniconda
ENV CONDA_DIR /opt/conda
RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh && \
     /bin/bash ~/miniconda.sh -b -p /opt/conda
RUN $CONDA_DIR/bin/conda create --name env311 python=3.11

# Put conda in path so we can use conda activate
ENV PATH=$CONDA_DIR/envs/env311/bin:$PATH

RUN pip install google-cloud-language --upgrade && pip install ipykernel && \
    pip install pandas --upgrade && pip install gcsfs && pip install gdown && \
    pip install db-dtypes --quiet
RUN $CONDA_DIR/envs/env311/bin/pip install db-dtypes --quiet
RUN $CONDA_DIR/envs/env311/bin/pip install matplotlib

## LangChain

RUN pip install google-cloud-aiplatform --pre && \
    pip install langchain && \
    pip install datasets && \
    pip install google-api-python-client && \
    pip install chromadb && \
    pip install pypdf && \
    pip install faiss-cpu && \
    pip install google-cloud-bigquery[all]

RUN apt-get install apt-transport-https ca-certificates gnupg --quiet
RUN echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list
RUN curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key --keyring /usr/share/keyrings/cloud.google.gpg add -
RUN apt-get update && apt-get install google-cloud-cli
RUN pip install boto3
RUN pip install pytorch_tabular[extra]

RUN $CONDA_DIR/bin/conda create --name env39 python=3.9
RUN $CONDA_DIR/bin/pip install scann