#%%
import json
import vertexai
from google.cloud import storage
from datasets import load_dataset
from vertexai.preview.language_models import TextGenerationModel

## Variables
dataset_uri = "gs://vtxdemos-datasets-public/ga/tweet_sent.jsonl"

#%%
dataset_name = "twitter_complaints"
dataset = load_dataset("ought/raft", dataset_name)

classes = [k.replace("_", " ") for k in dataset["train"].features["Label"].names]
print(classes)
dataset = dataset.map(
    lambda x: {"text_label": [classes[label] for label in x["Label"]]},
    batched=True,
    num_proc=1,
)
print(dataset)
dataset["train"][0]
# %%

with open("dataset.jsonl", "w") as f:
    for i in dataset["train"]:
        line={"input_text": f'Classify the following text into one of the following classes: \n{classes} \nText:{i["Tweet text"]}', "output_text": i["text_label"]}
        f.write(json.dumps(line)+"\n")

# %%
## Uploading to GCS
client = storage.Client()
client.bucket(dataset_uri.split("/")[2]).blob("/".join(dataset_uri.split("/")[3:])).upload_from_filename("dataset.jsonl")

## Using vertexai library for tuning


# %%
##
vertexai.init(project="vtxdemos")

model = TextGenerationModel.from_pretrained("text-bison@001")
model.tune_model(
    training_data=dataset_uri,
    # Optional:
    train_steps=10,
    tuning_job_location="europe-west4",  # Only supported in europe-west4 for Public Preview
    tuned_model_location="us-central1",
    model_display_name="tweet_sent_py"
)
print(model._job.status)

# %%
tuned_model_names = TextGenerationModel.from_pretrained("text-bison@001").list_tuned_model_names()
print(tuned_model_names)

model = TextGenerationModel.get_tuned_model(tuned_model_names[0])
parameters = {
    "temperature": 0.2,
    "max_output_tokens": 256,
    "top_p": 0.8,
    "top_k": 40
}
model = TextGenerationModel.from_pretrained("text-bison@001")
model = model.get_tuned_model("projects/254356041555/locations/us-central1/models/4393993711244017664")
#%%
response = model.predict(
    """Classify the following text into one of the following classes: [\'Unlabeled\', \'complaint\', \'no complaint\'] 
Text:@BurberryService Thanks for sending my Christmas present with the security protection still on it!""",
    **parameters
    )
print(f"Response from Model: {response.text}")
