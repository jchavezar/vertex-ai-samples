FROM python:3.10.10-slim-bullseye

COPY . .

RUN pip install torch==1.12.1+cu113 torchvision==0.13.1+cu113 torchaudio==0.12.1 --extra-index-url https://download.pytorch.org/whl/cu113 
RUN pip install pytorch_tabular[extra]
RUN pip install flask
RUN pip install transformers


# Flask Env Variable
ENV FLASK_APP=pred

# Expose port 8080
EXPOSE 8080

CMD flask run --host=0.0.0.0 --port=8080