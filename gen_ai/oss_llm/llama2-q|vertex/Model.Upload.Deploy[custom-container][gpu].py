#%%
from variables import * #change values
from google.cloud import aiplatform

artifact_uri = "gs://vtxdemos-models-public/llama2-q/llama-2-13b-gptq/"
display_name_job = artifact_uri.split("/")[4]
custom_predict_image_uri_gpu = f"us-central1-docker.pkg.dev/vtxdemos/custom-predictions/llama2:v1"

!docker build -t $custom_predict_image_uri_gpu .
!docker push $custom_predict_image_uri_gpu

#region Upload Model to Model Registry

aiplatform.init(project="vtxdemos")
model = aiplatform.Model.upload(
    display_name=display_name_job, 
    artifact_uri=artifact_uri, 
    serving_container_image_uri=custom_predict_image_uri_gpu,
    #serving_container_args= [
    #    "--model_base_path=$(AIP_STORAGE_DIR)"
    #    ]
)

endpoint = aiplatform.Endpoint.create(
    display_name=display_name_job+"-gpu", 
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

endpoint_resource_name = aiplatform.Endpoint.list(filter=f'display_name="{display_name_job+"-gpu"}"')[0].resource_name
endpoint = aiplatform.Endpoint(endpoint_name=endpoint_resource_name)

response = endpoint.predict({"instances": ["Do you have sentiments?"]})
response
# %%
