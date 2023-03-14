FROM python:3.10.10-slim-bullseye

COPY . .

RUN pip install torch==1.12.1+cu113 torchvision==0.13.1+cu113 torchaudio==0.12.1 --extra-index-url https://download.pytorch.org/whl/cu113 
RUN pip install pytorch_tabular[extra]

ENTRYPOINT ["python", "train.py"]
