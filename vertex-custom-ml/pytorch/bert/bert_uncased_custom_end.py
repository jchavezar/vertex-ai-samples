#%%
from google.cloud import aiplatform as aip 

project_id="vtxdemos"

!gcloud builds submit -t gcr.io/vtxdemos/bert-base:v1 .

aip.init(project=project_id)

endpoint=aip.Endpoint().list(filter='labels.hg="hg_bert"')
if endpoint:
    print(enendpointd)

#%%
endpoint=aip.Endpoint().create(
    display_name="hg_bert",
    labels={"hg":"hg_bert"}
)
# %%

endpoint.deploy(
    machine_type="n1-standard-4",
    accelerator_type="NVIDIA_TESLA_K80",
    accelerator_count=1,
    min_replica_count=1,
    max_replica_count=1,
    sync=True
)