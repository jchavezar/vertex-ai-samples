#%%
FROM pytorch/pytorch:2.0.1-cuda11.7-cudnn8-devel

RUN pip install ipykernel
RUN pip install uvicorn fastapi
RUN pip install "torch>=2.0" --extra-index-url https://download.pytorch.org/whl/cu117 --upgrade --quiet
RUN pip install "transformers==4.27.1" "datasets==2.9.0" "accelerate==0.17.1" "evaluate==0.4.0" tensorboard scikit-learn

COPY main.py main.py

EXPOSE 8080

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]