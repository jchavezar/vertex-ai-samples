#%%
import os
import yaml
from kfp import compiler
from kfp.dsl import pipeline
from kfp.components import importer_node
from evaluation_component import evaluation
from google_cloud_pipeline_components.types import artifact_types
from google_cloud_pipeline_components.v1 import custom_job, model, endpoint


CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
config = yaml.safe_load(open(f"{CURRENT_DIR}/config.yaml"))

@pipeline(name=config["pipeline_name"])
def pipeline(
    project_id : str,
    prefix_name: str,
):
    custom_train_job = custom_job.component.custom_training_job(
        display_name=f"{prefix_name}-train",
        project=project_id,
        worker_pool_specs=config["worker_pool_specs"],
        base_output_directory=config["model_path"]
    )

    evaluation_job = evaluation(
        project_id=project_id,
        model_uri=config["model_path"],
    ).after(custom_train_job)

    importer_spec = importer_node.importer(
        artifact_uri="{}/model".format(config["model_path"]),
        artifact_class=artifact_types.UnmanagedContainerModel,
        metadata={
            "containerSpec": {
                "imageUri": config["pred_image_uri"]
            },
        }).after(custom_train_job)
    
    model_upload_job = model.ModelUploadOp(
        display_name=f"{prefix_name}-model",
        project=project_id,
        unmanaged_container_model=importer_spec.outputs["artifact"])
    
    endpoint_create_job = endpoint.EndpointCreateOp(
        display_name=f"{prefix_name}-endpoint",
        project=project_id,
    )
    
    endpoint_deploy_job = endpoint.ModelDeployOp(
        deployed_model_display_name=f"{prefix_name}-model-deployed",
        endpoint=endpoint_create_job.outputs["endpoint"],
        model=model_upload_job.outputs["model"],
        dedicated_resources_machine_type="n1-standard-4",
        dedicated_resources_min_replica_count=1,
        dedicated_resources_max_replica_count=1,
    )
#%%
if __name__ == '__main__':
    compiler.Compiler().compile(pipeline_func=pipeline, package_path="../pipeline.yaml")