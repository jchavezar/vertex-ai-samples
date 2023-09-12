#%%
from variables import *
from kfp import compiler
from kfp.dsl import component, pipeline
from google_cloud_pipeline_components.v1.custom_job import CustomTrainingJobOp
from google_cloud_pipeline_components.v1.model import ModelUploadOp
from google_cloud_pipeline_components.v1.endpoint import EndpointCreateOp
from google_cloud_pipeline_components.v1.endpoint import EndpointConfigureOp
from google_cloud_pipeline_components.v1.endpoint import EndpointDeployModelOp

@pipeline(name=pipeline_name)
def pipeline(
    dataset_uri: str
):
    training_job = CustomTrainingJobOp(
        display_name=prefix+"-pipe-trainingjob",
        project=project_id,
        worker_pool_specs=[
            {
                "machine_spec": {
                    "machine_type": training_machine_type,
                    "accelerator_type": accelerator_type,
                    "accelerator_count": accelerator_count,
                },
                "replica_count": replica_count,
                "container_spec": {
                    "image_uri": custom_train_image_uri_cpu,
                    "command": [
                        "python",
                        "-m",
                        "trainer.train",
                        "--dataset",
                        f"{dataset_uri}",
                    ],
                },
            }
        ],
        base_output_directory=model_uri,
    ),
    model = ModelUploadOp(
        display_name=prefix+"-pipe-model",
        project=project_id,
        artifact_uri=training_job.outputs["model"],
    ),
    endpoint = EndpointCreateOp(
        display_name=prefix+"-pipe-endpoint",
        project=project_id, 
    ),
    endpoint = EndpointDeployModelOp(
        display_name=prefix+"-pipe-endpoint",
        project=project_id,
        model=model,
        endpoint=endpoint,
    )

if __name__ == '__main__':
    compiler.Compiler().compile(pipeline_func=pipeline, package_path=package_path)
# %%
