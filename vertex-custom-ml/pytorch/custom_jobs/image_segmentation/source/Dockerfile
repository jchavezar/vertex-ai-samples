
FROM nvcr.io/nvidia/pytorch:21.02-py3

COPY . .

RUN curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.deb.sh | bash
RUN apt-get update -y
RUN apt-get install git-lfs
RUN pip install jupyter ipykernel 
RUN pip install transformers datasets segments-ai evaluate git-lfs tqdm==4.59

ENTRYPOINT ["python", "train.py"]
