#%%
from vertexai.preview.language_models import TextGenerationModel
import vertexai

vertexai.init(project="cloud-llm-preview1")

# %%
model = TextGenerationModel.from_pretrained("text-bison@001")
model.tune_model(
        training_data="gs://vtxdemos-datasets-public/found_fine_tuning_data.jsonl/",
        # Optional:
        train_steps=4,
        tuning_job_location="europe-west4",  # Only supported in europe-west4 for Public Preview
        tuned_model_location="us-central1",
    )
# %%
