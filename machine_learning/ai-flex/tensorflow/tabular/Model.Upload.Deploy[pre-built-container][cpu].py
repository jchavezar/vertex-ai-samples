#%%
from variables import *
from google.cloud import aiplatform

#region Upload Model to Model Registry
model = aiplatform.Model.upload(
    display_name=display_name_job, 
    artifact_uri=model_uri+"/model", 
    serving_container_image_uri=prebuilt_preidct_image_uri_cpu
)

endpoint = aiplatform.Endpoint.create(
    display_name=display_name_job+"-cpu", 
)

model.deploy(
    endpoint=endpoint, 
    traffic_split={"0": 100},
    machine_type=machine_type_gpu,
    accelerator_type=accelerator_type,
    accelerator_count=accelerator_count,
    min_replica_count=1, 
    max_replica_count=1, 
    sync=True
)
#endregion

# %%
