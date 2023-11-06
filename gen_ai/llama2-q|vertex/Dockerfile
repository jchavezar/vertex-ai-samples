FROM nvidia/cuda:11.8.0-cudnn8-devel-ubuntu22.04

COPY requirements.txt requirements.txt
COPY main.py main/py
COPY utils utils

RUN apt-get update -y && \
     apt install python3 python3-pip -y

RUN pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118 && \
     GITHUB_ACTIONS=true pip install auto-gptq

RUN pip install -r requirements.txt

ENTRYPOINT ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]