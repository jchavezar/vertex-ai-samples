#%%
#region Libraries
from google.cloud import aiplatform as aip 
#endregion

#region Variables
project_id="vtxdemos"
pred_image="bert-base:v2"
#endregion

!docker build -t gcr.io/vtxdemos/$pred_image .
!docker push gcr.io/vtxdemos/$pred_image

#%%
#region Vertex AI Uploading and Deploying Model
aip.init(project=project_id)

model=aip.Model.list(filter='labels.model_hg="model_hg_bert"')
if not model:
    print("Uploading Model")
    model=aip.Model.upload(
        display_name="hg_bert",
        serving_container_image_uri=f"gcr.io/{project_id}/{pred_image}",
        serving_container_predict_route="/predict",
        serving_container_health_route="/health",
        serving_container_ports=[8080],
        labels={"model_hg":"model_hg_bert"},
    )
else: model=aip.Model(model_name=model[0].resource_name)

#%%
endpoint=aip.Endpoint.list(filter='labels.hg="hg_bert"')
if not endpoint:
    endpoint=aip.Endpoint.create(
        display_name="hg_bert",
        labels={"hg":"hg_bert"}
    )
else: endpoint=aip.Endpoint(endpoint_name=endpoint[0].resource_name)
# %%

end=endpoint.deploy(
    machine_type="n1-standard-4",
    accelerator_type="NVIDIA_TESLA_K80",
    accelerator_count=1,
    min_replica_count=1,
    max_replica_count=1,
    sync=True,
    model=model
)
#endregion

# %%
