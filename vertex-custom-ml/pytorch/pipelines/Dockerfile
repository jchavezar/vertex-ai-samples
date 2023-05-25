#FROM nvidia/cuda:11.8.0-devel-ubuntu22.04
FROM pytorch/pytorch:1.12.1-cuda11.3-cudnn8-devel

RUN pip install ipykernel
RUN pip install --pre torch torchvision --index-url https://download.pytorch.org/whl/nightly/cu118
RUN pip install fsspec gcsfs
RUN pip install torchdata