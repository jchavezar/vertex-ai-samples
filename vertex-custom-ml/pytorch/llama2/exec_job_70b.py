#%%
from google.cloud.aiplatform import Model, Endpoint

project="vtxdemos"
deploy_image_uri="us-central1-docker.pkg.dev/vtxdemos/prediction/llama-2-70b-chat-gptq:v1.0"
artifact_uri="gs://vtxdemos-models/llama-2-70B-chat-gptq"

!docker build -t $deploy_image_uri -f Dockerfile70b .
!docker push $deploy_image_uri

#%%
model = Model.upload(
    display_name="llama2.1-70B", 
    serving_container_image_uri=deploy_image_uri,
    artifact_uri=artifact_uri,
    )

endpoint = Endpoint.create(
    display_name="llama2.1-70B-endpoint")
#%%
endpoint.deploy(
    machine_type="g2-standard-24",
    accelerator_type="NVIDIA_L4",
    accelerator_count=2,
    min_replica_count=1,
    max_replica_count=1,
    sync=True,
    model=model
    )
# %%
