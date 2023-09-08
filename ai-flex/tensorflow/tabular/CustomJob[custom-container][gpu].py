#%%
from variables import *
from google.cloud import aiplatform

aiplatform.init(project=project_id, location=region, staging_bucket=staging_bucket)

#region vertexai CustomJob
model = aiplatform.CustomJob(
    display_name=display_name_job+"-gpu",
    worker_pool_specs=[
        {
            "machine_spec": {
                "machine_type": machine_type_gpu,
                "accelerator_type": accelerator_type,
                "accelerator_count": accelerator_count,
            },
            "replica_count": replica_count,
            "container_spec": {
                "image_uri": custom_train_image_uri_gpu,
                "args": ["python", "train.py", "--dataset", dataset_uri]            
            },
        }
    ],
    labels= {
        "ai-flex": "custom-train-gpu"
        }
)
#endregion

model=model.run()
# %%
