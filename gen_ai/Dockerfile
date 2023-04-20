FROM nvidia/cuda:11.8.0-devel-ubuntu22.04

# Install base utilities
RUN apt update && apt upgrade -y && \
    apt install build-essential manpages-dev -y  && \
    apt-get install -y wget && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install miniconda
ENV CONDA_DIR /opt/conda
RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh && \
     /bin/bash ~/miniconda.sh -b -p /opt/conda

# Put conda in path so we can use conda activate
ENV PATH=$CONDA_DIR/bin:$PATH

RUN pip install google-cloud-language --upgrade && pip install google-cloud-aiplatform --pre && pip install ipykernel && \
    pip install pandas --upgrade && pip install gcsfs
