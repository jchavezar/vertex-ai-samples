import os
import asyncio
import pandas as pd
import time
#from PIL import Image
from flask import Flask, request
from google.cloud import storage
from google.cloud import aiplatform
from utils import ai, database, variables, credentials
from vertexai.preview.vision_models import MultiModalEmbeddingModel, Image

app = Flask(__name__)

async def foo():
    time.sleep(100)
    return 'Asynchronicity!'

async def bar():
    return await foo()

@app.post("/")
async def index():
    data = request.get_json()
    return asyncio.run(bar())

if __name__ == "__main__":
    # Dev only: run "python main.py" and open http://localhost:8080
    app.run(host="localhost", port=8080, debug=True)
