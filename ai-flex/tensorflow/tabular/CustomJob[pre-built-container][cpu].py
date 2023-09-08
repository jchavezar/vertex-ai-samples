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
            "python_package_spec": {
                "executor_image_uri": prebuilt_train_image_uri_cpu,
                "package_uris": [prebuilt_train_package_uri],
                "python_module": "trainer.train",
                "args": ["--dataset", dataset_uri]
            },
        }
    ],
    base_output_dir = model_uri,
    labels= {
        "ai-flex": "prebuilt-train-cpu"
        }
)
#endregion

model=model.run()
# %%
