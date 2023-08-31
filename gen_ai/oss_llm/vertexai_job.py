#%%
#region Libraries
from google.cloud import aiplatform as aip 
#endregion

#region Variables
project_id="vtxdemos"
pred_image="oss_llama-base:v4"
#endregion

#%%
!docker build -t gcr.io/$project_id/$pred_image .
!docker push gcr.io/$project_id/$pred_image

#%%
#region Vertex AI Uploading and Deploying Model
aip.init(project=project_id)

model=aip.Model.list(filter='labels.model_hg="model_hg_llama"')
if not model:
    print("Uploading Model")
    model=aip.Model.upload(
        display_name="hg_llama",
        serving_container_image_uri=f"gcr.io/{project_id}/{pred_image}",
        serving_container_predict_route="/",
        serving_container_health_route="/health",
        serving_container_environment_variables={"BUCKET": "vtxdemos-models"},
        serving_container_ports=[8080],
        labels={"model_hg":"model_hg_llama"},
    )
else: model=aip.Model(model_name=model[0].resource_name)

#%%
endpoint=aip.Endpoint.list(filter='labels.hg="llama"')
if not endpoint:
    endpoint=aip.Endpoint.create(
        display_name="llama",
        labels={"hg":"llama"}
    )
else: endpoint=aip.Endpoint(endpoint_name=endpoint[0].resource_name)
# %%

end=endpoint.deploy(
    machine_type="g2-standard-24",
    #accelerator_type="NVIDIA_TESLA_K80",
    #accelerator_count=1,
    min_replica_count=1,
    max_replica_count=1,
    sync=True,
    model=model
)
#endregion
# %%
