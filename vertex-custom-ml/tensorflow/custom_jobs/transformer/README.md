## Description

Sentiment analysis detection using a corpus of 25k rows and BERT pre-trained model frozen at the embeddings layer: https://tfhub.dev/google/nnlm-en-dim50/2.

1. (container-nlp.ipynb)[https://github.com/jchavezar/vertex-ai-samples/blob/main/vertex-custom-ml/tensorflow/custom_jobs/transformer/container-nlp.ipynb] use aiplatform for an e2e workflow without using pipelines.
2. pipe-container-nlp.ipynb was created under Vertex AI Pipelines to facilitate the orchestration of each component.