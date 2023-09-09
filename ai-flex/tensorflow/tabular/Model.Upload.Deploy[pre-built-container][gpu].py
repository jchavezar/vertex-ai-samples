#%%
from variables import *
from google.cloud import aiplatform

#region Upload Model to Model Registry
model = aiplatform.Model.upload(
    display_name=display_name_job, 
    artifact_uri=model_uri+"/model", 
    serving_container_image_uri=prebuilt_preidct_image_uri_gpu
)

endpoint = aiplatform.Endpoint.create(
    display_name=display_name_job+"-gpu", 
)

model.deploy(
    endpoint=endpoint, 
    traffic_split={"0": 100},
    machine_type=machine_type_gpu, 
    min_replica_count=1, 
    max_replica_count=1, 
    sync=True
)
#endregion

# %%
