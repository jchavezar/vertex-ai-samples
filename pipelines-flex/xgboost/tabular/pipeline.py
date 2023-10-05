#%%
from variables import *
from kfp import compiler
from google.cloud import aiplatform
from kfp.dsl import component, pipeline, importer
from google_cloud_pipeline_components.v1.custom_job import CustomTrainingJobOp
from google_cloud_pipeline_components.v1.model import ModelUploadOp
from google_cloud_pipeline_components.v1.endpoint import EndpointCreateOp
from google_cloud_pipeline_components.v1.endpoint import ModelDeployOp
from google_cloud_pipeline_components.types import artifact_types

@pipeline(name=pipeline_name)
def pipeline():
    training_job = CustomTrainingJobOp(
        display_name = prefix+"-pipe-trainingjob",
        project = project_id,
        worker_pool_specs = [
            {
                "machine_spec": {
                    "machine_type": training_machine_type,
                },
                "replica_count": replica_count,
                "container_spec": {
                    "image_uri": custom_train_image_uri_cpu,
                    "command": [
                        "python",
                        "-m",
                        "trainer.train",
                        "--dataset_dir",
                        dataset_uri,
                    ],
                },
            }
        ],
        base_output_directory = model_uri,
    )
    
    #Import GCS Model
    
    unmanaged_model_importer = importer(
        artifact_uri = model_uri,
        artifact_class = artifact_types.UnmanagedContainerModel,
        metadata = {
            "containerSpec": { "imageUri":
                prebuilt_predict_image_uri_cpu
                }
            }
        ).after(training_job)
        
    model_upload_op = ModelUploadOp(
        display_name = prefix+"-pipe-model",
        unmanaged_container_model = unmanaged_model_importer.outputs["artifact"],
    )
    
    endpoint_create_op = EndpointCreateOp(
        display_name=prefix+"-pipe-endpoint",
    )
    
    endpoint = ModelDeployOp(
        model = model_upload_op.outputs["model"],
        endpoint = endpoint_create_op.outputs["endpoint"],
        dedicated_resources_machine_type = training_machine_type,
        dedicated_resources_min_replica_count = 1,
        dedicated_resources_max_replica_count = 1
    )

if __name__ == '__main__':
    compiler.Compiler().compile(pipeline_func=pipeline, package_path=package_path)
    aiplatform.init(project=project_id, location=region)
    
    pipeline_job = aiplatform.PipelineJob(
        display_name=prefix+"-pipeline-job",
        template_path=package_path,
        pipeline_root=pipeline_root,
        parameter_values={},
        enable_caching=False
        )
    
    pipeline_job.submit(experiment=experiment_name)
    
# %%
