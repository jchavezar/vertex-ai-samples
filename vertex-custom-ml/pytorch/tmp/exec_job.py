#%%
from google.cloud.aiplatform import Model, Endpoint

project="vtxdemos"
deploy_image_uri="us-central1-docker.pkg.dev/vtxdemos/prediction/llama-2-13b-chat-gptq:tmp1"
artifact_uri="gs://vtxdemos-models/llama-2-13B-chat-gptq"

!docker build -t $deploy_image_uri .
!docker push $deploy_image_uri

#%%
model = Model.upload(
    display_name="ttest2-13B", 
    serving_container_image_uri=deploy_image_uri,
    artifact_uri=artifact_uri,
    )

endpoint = Endpoint.create(
    display_name="ttest2-13B-endpoint")

endpoint.deploy(
    machine_type="g2-standard-24",
    min_replica_count=1,
    max_replica_count=1,
    sync=True,
    model=model
    )
# %%
