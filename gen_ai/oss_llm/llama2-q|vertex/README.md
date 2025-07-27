# Getting Started
These are the steps to deploy GPTQ (quantized models / 4bits) with L4 GPUs using Vertex Endpoints.

## Config
ExLlama has been used which is a method designed to be fast and memory-efficient on modern GPUs.

This is onlt for prototyping and testing models I do not encourage to use these models in production because of the quality loss.

References:

- GPTQ-for-Llama: [link](https://github.com/qwopqwop200/GPTQ-for-LLaMa)
- ExLlama: [link](https://github.com/turboderp/exllama)

## List of Models working with GPTQ and ExLlama

- iambestfeed/open_llama_3b_4bit_128g
- Neko-Institute-of-Science/LLaMA-7B-4bit-128g
- Neko-Institute-of-Science/LLaMA-13B-4bit-128g
- Neko-Institute-of-Science/LLaMA-30B-4bit-32g
- Neko-Institute-of-Science/LLaMA-30B-4bit-128g
- Neko-Institute-of-Science/LLaMA-65B-4bit-32g
- Neko-Institute-of-Science/LLaMA-65B-4bit-128g
- Panchovix/LLaMA-2-70B-GPTQ-transformers4.32.0.dev0
- reeducator/bluemoonrp-13b
- reeducator/bluemoonrp-30b
- TehVenom/Metharme-13b-4bit-GPTQ
- TheBloke/airoboros-13B-GPTQ
- TheBloke/gpt4-x-vicuna-13B-GPTQ
- TheBloke/GPT4All-13B-snoozy-GPTQ
- TheBloke/guanaco-33B-GPTQ
- TheBloke/guanaco-65B-GPTQ
- TheBloke/h2ogpt-oasst1-512-30B-GPTQ
- TheBloke/koala-13B-GPTQ-4bit-128g
- TheBloke/Llama-2-13B-chat-GPTQ (128g)
- TheBloke/Llama-2-13B-GPTQ (32g, 64g, 128g)
- TheBloke/Llama-2-70B-GPTQ (32g, 128g)
- TheBloke/Manticore-13B-GPTQ
- TheBloke/medalpaca-13B-GPTQ-4bit
- TheBloke/medalpaca-13B-GPTQ-4bit (compat version)
- TheBloke/Nous-Hermes-13B-GPTQ
- TheBloke/robin-65B-v2-GPTQ
- TheBloke/tulu-7B-GPTQ
- TheBloke/Tulu-13B-SuperHOT-8K-GPTQ
- TheBloke/tulu-30B-GPTQ
- TheBloke/vicuna-13B-1.1-GPTQ-4bit-128g
- TheBloke/VicUnlocked-30B-LoRA-GPTQ
- TheBloke/wizard-mega-13B-GPTQ
- TheBloke/Wizard-Vicuna-7B-Uncensored-GPTQ
- TheBloke/Wizard-Vicuna-13B-Uncensored-GPTQ
- TheBloke/WizardLM-7B-uncensored-GPTQ
- TheBloke/WizardLM-30B-Uncensored-GPTQ
- TheBloke/WizardLM-33B-V1.0-Uncensored-SuperHOT-8K-GPTQ
- tmpupload/superhot-30b-8k-no-rlhf-test-128g-GPTQ
- Yhyu13/chimera-inst-chat-13b-gptq-4bit
- Yhyu13/oasst-rlhf-2-llama-30b-7k-steps-gptq-4bit

## Files

API Gateway is defined [here / main.py](https://github.com/jchavezar/vertex-ai-samples/blob/main/gen_ai/llama2-q%7Cvertex/main.py)

Vertex Deploy Job is define [here / Model.Upload.Deploy[custom-container][gpu].py](https://github.com/jchavezar/vertex-ai-samples/blob/main/gen_ai/llama2-q%7Cvertex/Model.Upload.Deploy%5Bcustom-container%5D%5Bgpu%5D.py)

Dockerfile [here](https://github.com/jchavezar/vertex-ai-samples/blob/main/gen_ai/llama2-q%7Cvertex/Dockerfile)

## Instructions

I have some models in my public Google Cloud Storage: *"gs://vtxdemos-models-public/llama2-q/llama-2-13b-gptq/"*
But you can download them from HuggingFace and Store it in GCS. [reference | TheBloke/Llama-2-13B-GPTQ](https://huggingface.co/TheBloke/Llama-2-13B-GPTQ)

1. Create Cloud Storage and Store Model Artifacts.
```
gsutil mb gs://[YOUR_UNIQUE_BUCKET_NAME]
```

2. Create Artifact Container Repository, [Instructions](https://cloud.google.com/artifact-registry/docs/repositories/create-repos#create-gcloud)
```
gcloud artifacts repositories create REPOSITORY \
    --repository-format=docker \
    --location=LOCATION \
    --description="DESCRIPTION" \
    --kms-key=KMS-KEY \
    --immutable-tags \
    --async
```

3. Change [variables.py file](https://github.com/jchavezar/vertex-ai-samples/blob/main/gen_ai/llama2-q%7Cvertex/variables.py) with your own variables.

4. Change [Model.Upload.Deploy[custom-container][gpu].py](https://github.com/jchavezar/vertex-ai-samples/blob/main/gen_ai/llama2-q%7Cvertex/Model.Upload.Deploy%5Bcustom-container%5D%5Bgpu%5D.py) variables like:

```
artifact_uri = "gs://vtxdemos-models-public/llama2-q/llama-2-13b-gptq/"
custom_predict_image_uri_gpu = f"us-central1-docker.pkg.dev/vtxdemos/custom-predictions/llama2:v1"
```

5. Build Container and Push

example:
```
docker build -t us-central1-docker.pkg.dev/vtxdemos/custom-predictions/llama-2-13B-chat-gptq:v1 .
docker push us-central1-docker.pkg.dev/vtxdemos/custom-predictions/llama-2-13B-chat-gptq:v1
```

6. Deploy

```
python Model.Upload.Deploy[custom-container][gpu].py
```

![Vertex Llama2 Q](images/llama2-13b-vertex.png)