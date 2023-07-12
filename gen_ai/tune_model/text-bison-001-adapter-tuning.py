#%%
import json
import pandas as pd
from google.cloud import storage
from google.cloud import aiplatform
from google.cloud.aiplatform.private_preview.language_models import TextGenerationModel

project_id="cloud-llm-preview1"

df = pd.read_csv("mtsamples.csv")
df = df[["description", "medical_specialty"]].sample(n=10)

with open("train.jsonl", "w") as f:
    for index, row in df.iterrows():
        f.write(json.dumps({"input_text": row["description"], "output_text": row["medical_specialty"]}) + '\n'
        )

#!gsutil cp train.jsonl gs://jesusarguelles-datasets/clinical-llm/train.jsonl

client_storage = storage.Client(project="jchavezar-demo")
bucket = client_storage.bucket("jesusarguelles-datasets")
for blob in bucket.list_blobs():
    bucket.blob(blob.name).download_to_filename("train.jsonl")
    
# %%

aiplatform.init(project=project_id)
model = TextGenerationModel("text-bison-001")
#%%
model = model.tune_model(
    training_data="gs://jesusarguelles-datasets/clinical-llm/train.jsonl",
    train_steps=10,
    tuning_job_location="europe-west4",
    tuned_model_location="us-central1",
)
#%%
model = TextGenerationModel.get_tuned_model(TextGenerationModel.list_tuned_model_names()[0])

#%%
prediction = model.predict('''Transurethral electrosurgical resection of the prostate for benign prostatic hyperplasia.

Suction-assisted lipectomy - lipodystrophy of the abdomen and thighs.
Bariatrics

 Cerebral Angiogram - moyamoya disease.
Neurology

 Vasectomy 10 years ago, failed.  Azoospermic.  Reversal two years ago.  Interested in sperm harvesting and cryopreservation
Urology

Left testicular swelling for one day.  Testicular Ultrasound.  Hypervascularity of the left epididymis compatible with left epididymitis.  Bilateral hydroceles.
''')
# %%
