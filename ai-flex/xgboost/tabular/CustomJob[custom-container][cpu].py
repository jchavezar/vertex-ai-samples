#%%
from variables import *
from google.cloud import aiplatform

aiplatform.init(project=project_id, location=region, staging_bucket=staging_bucket)

#region vertexai CustomJob
model = aiplatform.CustomJob(
    display_name=display_name_job+"-cpu",
    worker_pool_specs=[
        {
            "machine_spec": {
                "machine_type": machine_type_cpu,
                #"accelerator_type": accelerator_type,
                #"accelerator_count": accelerator_count,
            },
            "replica_count": replica_count,
            "container_spec": {
                "image_uri": custom_train_image_uri_cpu,
                "args": [
                    "python", 
                    "-m", 
                    "trainer.train", 
                    "--dataset_dir", 
                    dataset_dir,
                    ]
            },
        },
    ],
    labels= {
        "ai-flex": "custom-train-wholesale-cpu"
        },
    base_output_dir=model_dir
)
#endregion

model=model.run()
# %%
