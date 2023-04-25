# Create Buckets
# Install gcsfs
#%%

import pandas as pd

df = pd.read_csv('gs://sockcop-datasets-public/mtsamples.csv', index_col=False)
df = df[df!=df.isnull()][['description', 'medical_specialty']]
df["medical_specialty"] = df["medical_specialty"].str.strip()
df["medical_specialty"].value_counts()


columns = ["Radiology", "Neurology", "Gastroenterology"]
df = df[df["medical_specialty"].isin(columns)]
train = df.sample(frac=0.5).sample(n=20)
test = df.drop(train.index).sample(n=20)

import json
with open("train.jsonl", "w") as f:
    for num,text in enumerate(train.values):
        if num < int(len(train)*.80):
            json.dump({"classificationAnnotation": {"displayName": text[1]}, "textContent": text[0], "dataItemResourceLabels": {"aiplatform.googleapis.com/ml_use": "training"}}, f)
        elif num >= int(len(train)*.80) < int(len(train)*.90):
            json.dump({"classificationAnnotation": {"displayName": text[1]}, "textContent": text[0], "dataItemResourceLabels": {"aiplatform.googleapis.com/ml_use": "test"}}, f)
        else : json.dump({"classificationAnnotation": {"displayName": text[1]}, "textContent": text[0], "dataItemResourceLabels": {"aiplatform.googleapis.com/ml_use": "validation"}}, f)
        f.write("\n")

with open("test.jsonl", "w") as f:
    for text in test.values:
        json.dump({"classificationAnnotation": {"displayName": text[1]}, "textContent": text[0], "dataItemResourceLabels": {"aiplatform.googleapis.com/ml_use": "test"}}, f)
        f.write("\n")

!gsutil cp train.jsonl gs://sockcop-datasets-public/train.jsonl
!gsutil cp test.jsonl gs://sockcop-datasets-public/test.jsonl

df['medical_specialty'].unique().tolist()