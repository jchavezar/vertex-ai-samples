#%%
import os
import logging
from flask import Flask, request, Response, jsonify
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

# Model Download from huggingface
model = AutoModelForCausalLM.from_pretrained("facebook/opt-66b", torch_dtype=torch.float16).cuda()
tokenizer = AutoTokenizer.from_pretrained("facebook/opt-66b", use_fast=False)

# Creation of the Flask app
app = Flask(__name__)

# Flask route for Liveness checks
@app.route(os.environ['AIP_HEALTH_ROUTE'])
def isalive():
    status_code = Response(status=200)
    return status_code

# Flask route for predictions
@app.route(os.environ['AIP_PREDICT_ROUTE'],methods=['GET','POST'])
def prediction():
    data = request.get_json(silent=True, force=True)
    prompt = data
    input_ids = tokenizer(prompt, return_tensors="pt").input_ids.cuda()
    generated_ids = model.generate(input_ids)
    res = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)
    return jsonify({"Prediction": res[0]})

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8080)
# %%
