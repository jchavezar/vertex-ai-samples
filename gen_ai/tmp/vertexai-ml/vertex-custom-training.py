#%%
from google.cloud import aiplatform

aiplatform.init(project="vtxdemos", location="us-central1", staging_bucket="gs://vtxdemos-tmp")

#region vertexai CustomJob
model = aiplatform.CustomJob(
    display_name="pytorch2.2",
    worker_pool_specs=[
        {
            "machine_spec": {
                "machine_type": "g2-standard-4",
                "accelerator_type": "NVIDIA_L4",
                "accelerator_count": 1,
            },
            "replica_count": 1,
            "container_spec": {
                "image_uri": "us-central1-docker.pkg.dev/vtxdemos/custom-trains/pytorch-2.2_gpu:1.0",
                "args": ["python3", "main.py"]            
            },
        }
    ],
    base_output_dir = "gs://vtxdemos-models",
    labels= {
        "ai-flex": "custom-train-gpu"
        }
)
#endregion

model=model.run()
# %%