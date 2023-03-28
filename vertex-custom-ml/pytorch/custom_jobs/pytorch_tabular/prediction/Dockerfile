FROM pytorch/pytorch:1.12.1-cuda11.3-cudnn8-devel

COPY . .
WORKDIR main/

#RUN pip install torch==1.12.1+cu113 torchvision==0.13.1+cu113 torchaudio==0.12.1 --extra-index-url https://download.pytorch.org/whl/cu113 
RUN pip install pytorch_tabular[extra]
RUN pip install uvicorn fastapi
RUN pip install gcsfs

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]