# Loading jsonl from Google Cloud Storage
#%%
from google.cloud import storage
import json
import pandas as pd

client = storage.Client(project='cloud-llm-preview4')
blob = client.bucket('asu_demo').blob('asu-test-working.jsonl')

blob.download_to_filename('asu-test-working.jsonl')
# %%
with open('asu-test-working.jsonl', 'r') as f:
    input_text = []
    output_text = []
    for line in f:
        input_text.append(json.loads(line)['input_text'])
        output_text.append(json.loads(line)['output_text'])
        

df = pd.DataFrame({'input_text':input_text, 'output_text':output_text})

# From Pandas to JSONL
# %%
with open('asu-test-working2.jsonl', 'w') as f:
    for index, row in df.iterrows():
        json.dump({'input_text': row['input_text'], 'output_text': row['output_text']}, f)
        f.write('\n')

## Upload to GCS
# %%
blob = client.bucket('sockcop-datasets-public4').blob('asu-test-working2.jsonl')
blob.upload_from_filename('asu-test-working2.jsonl')

######################## Tune Model #######################
#%%
from typing import Union
import vertexai
import pandas as pd
from vertexai.preview.language_models import TextGenerationModel, TextEmbeddingModel

def tuning(
    project_id: str,
    location: str,
    training_data: Union[pd.DataFrame, str]
):
    vertexai.init(project=project_id, location=location)
    model = TextEmbeddingModel('text-bison@001')
    
    model.tune_model(
        training_data=training_data,
        train_steps=1,
        tuning_job_location="europe-west4",
        tuned_model_location=location
    )
    
    return model

model = tuning(
    project_id = 'cloud-llm-preview4',
    location='us-central1',
    training_data='gs://sockcop-datasets-public4/asu-test-working2.jsonl'
)

#%%
model.predict("what's the dog name?")

# %%
