#%%
#region Imports

from google.cloud import aiplatform

#endregion

#region Variables

PROJECT_ID="vtxdemos"
REGION="europe-west4"
BUCKET_NAME="vtxdemos-models"
BUCKET_URI=f"gs://{BUCKET_NAME}/"
FULL_GCS_PATH=f"{BUCKET_URI}model_artifacts"
PYTORCH_PREDICTION_IMAGE_URI = (
    "us-docker.pkg.dev/vertex-ai/prediction/pytorch-gpu.1-12:latest"
)
APP_NAME = "my-stable-diffusion"
VERSION = 1
MODEL_DISPLAY_NAME = "stable_diffusion_1_5-unique"
MODEL_DESCRIPTION = "stable_diffusion_1_5 container"
ENDPOINT_DISPLAY_NAME = f"{APP_NAME}-endpoint"

#endregion

#region Functions

!gsutil cp -r model_artifacts $BUCKET_URI

#endregion

#region Main

aiplatform.init(project=PROJECT_ID, location=REGION, staging_bucket=BUCKET_NAME)


model = aiplatform.Model.upload(
    display_name=MODEL_DISPLAY_NAME,
    description=MODEL_DESCRIPTION,
    serving_container_image_uri=PYTORCH_PREDICTION_IMAGE_URI,
    artifact_uri=FULL_GCS_PATH,
)

model.wait()

print(model.display_name)
print(model.resource_name)
#%%
#endregion

#region Endpoint
endpoint = aiplatform.Endpoint.create(display_name=ENDPOINT_DISPLAY_NAME)

model.deploy(
    endpoint=endpoint,
    deployed_model_display_name=MODEL_DISPLAY_NAME,
    machine_type="g2-standard-4",
    accelerator_type="NVIDIA_L4",
    accelerator_count=1,
    traffic_percentage=100,
    deploy_request_timeout=1200,
    sync=True,
)

#endregion
# %%
