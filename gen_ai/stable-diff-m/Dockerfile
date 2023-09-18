FROM nvidia/cuda:11.8.0-cudnn8-devel-ubuntu22.04

RUN apt-get update -y && \
     apt install python3 python3-pip -y && \
     apt-get install -y nvidia-container-toolkit-base

RUN pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118 && \
     GITHUB_ACTIONS=true pip install auto-gptq && \
     pip install fastapi && pip install uvicorn && \
     pip install google-cloud-storage && \
     pip install google-cloud-storage diffusers["torch"]  && \
     pip install transformers && \ 
     pip install omegaconf && \
     pip install xformers

COPY main.py main.py

ENTRYPOINT ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]