##Install packages
#!gsutil cp gs://vertex_sdk_llm_private_releases/SDK/google_cloud_aiplatform-1.25.dev20230413+language.models-py2.py3-none-any.whl .
#!pip install google_cloud_aiplatform-1.25.dev20230413+language.models-py2.py3-none-any.whl "shapely<2.0.0"
#%%

import vertexai
from vertexai.preview.language_models import TextGenerationModel

vertexai.init(project="vtxdemos", location="us-central1")

model = TextGenerationModel.from_pretrained("text-bison@001")

print(model.predict(
    "what llm model are you using?",
    # Optional:
    max_output_tokens=256,
    temperature=0.3,
    top_p=0.8,
    top_k=40,
))

# %%
