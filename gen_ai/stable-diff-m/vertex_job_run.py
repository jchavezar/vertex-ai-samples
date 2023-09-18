#%%
from google.cloud.aiplatform import Model, Endpoint

project="vtxdemos"
deploy_image_uri="us-central1-docker.pkg.dev/vtxdemos/prediction/sd-diff-h:v2.0"
aip_storage_uri="gs://vtxdemos-models/sd-burger/"
model_file_name="BKWhopperSDXLv4-step00020000.safetensors"

#%%
#!docker build -t $deploy_image_uri .
#!docker push $deploy_image_uri
!gcloud builds submit -t $deploy_image_uri .

#%%
model = Model.upload(
    display_name="sd-diff-model-2", 
    serving_container_image_uri=deploy_image_uri,
    artifact_uri=aip_storage_uri,
    serving_container_environment_variables={"MODEL_FILE_NAME": model_file_name}
    )

#%%
model=Model(model_name=Model.list(filter="display_name=sd-diff-model")[0].resource_name)

endpoint = Endpoint.create(
    display_name="sd-diff-endpoint-2")

endpoint.deploy(
    machine_type="g2-standard-24",
    accelerator_type="NVIDIA_L4",
    accelerator_count=2,
    min_replica_count=1,
    max_replica_count=1,
    sync=True,
    model=model,
    )
# %%

endpoint.deploy(
    machine_type="n1-standard-8",
    accelerator_type="NVIDIA_TESLA_V100",
    accelerator_count=1,
    min_replica_count=1,
    max_replica_count=1,
    sync=True,
    model=model,
    )