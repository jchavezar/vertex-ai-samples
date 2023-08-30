#%%
#region Libraries
from kfp import dsl
from google.cloud import aiplatform
from kfp.registry import RegistryClient
from google_cloud_pipeline_components.types import artifact_types
from google_cloud_pipeline_components.v1.model import ModelUploadOp
from google_cloud_pipeline_components.v1.custom_job import CustomTrainingJobOp
from google_cloud_pipeline_components.v1.endpoint import EndpointCreateOp, ModelDeployOp
#endregion

#region Variables
project_id="vtxdemos"
region="us-central1"
dist_uri="gs://vtxdemos-distfiles/trainer-0.1.tar.gz"
model_uri="gs://vtxdemos-models/kfpv2/tensorflow"
prebuilt_image_train="us-docker.pkg.dev/vertex-ai/training/tf-cpu.2-12.py310:latest"
prebuilt_image_inference="us-docker.pkg.dev/vertex-ai/prediction/tf2-cpu.2-12:latest"
staging_folder="gs://vtxdemos-staging"
kfp_repo_name="kfp-repo"
template_name="kfpv2-tensorflow"
#endregion

worker_pool_specs=[{
  "machineSpec": {
  "machineType": "n1-standard-4",
  },
  "replicaCount": "1",
  "pythonPackageSpec":{
      "executorImageUri": prebuilt_image_train,
      "packageUris": [dist_uri],
      "pythonModule": "trainer.task",
      }
}]


@dsl.pipeline(name=template_name)
def pipeline(
    train_display_name: str,
    inference_display_name: str,
    model_uri: str,
    prebuilt_image_inference: str = prebuilt_image_inference,
    worker_pool_specs: list = worker_pool_specs
):
    train_job_op = CustomTrainingJobOp(
        display_name=train_display_name,
        worker_pool_specs=worker_pool_specs,
        base_output_directory=model_uri
    )
    importer_spec = dsl.importer(
        artifact_uri="/model".format(model_uri),
        artifact_class=artifact_types.UnmanagedContainerModel,
        metadata={
          'containerSpec': { 'imageUri':
            prebuilt_image_inference
            }
          }
        )
    upload_job_op = ModelUploadOp(
        display_name=inference_display_name,
        unmanaged_container_model=importer_spec.outputs["artifact"]
    )
    upload_job_op.after(train_job_op)
    create_ep_job_op = EndpointCreateOp(
        display_name="kfpv2-tf"
    )
    deploy_ep_job_op = ModelDeployOp(
        model=upload_job_op.outputs["model"],
        endpoint=create_ep_job_op.outputs["endpoint"]
    )
    deploy_ep_job_op.after(upload_job_op)


if __name__ == "__main__":
    import kfp.compiler as compiler
    compiler.Compiler().compile(pipeline, "kfpv2-custom-tf-reg-pipeline" + ".yaml")
    
    #region Template
    client = RegistryClient(host=f"https://us-central1-kfp.pkg.dev/vtxdemos/kfp-repo")
    
    templateName, versionName = client.upload_pipeline(
        file_name="kfpv2-custom-tf-reg-pipeline.yaml",
    tags=["v2", "latest"])
    
    aiplatform.init(
        project=project_id,
        location=region,
        staging_bucket=staging_folder)
    
    job = aiplatform.PipelineJob(
        display_name="kfpv2-custom-tf-reg-pipeline",
        template_path=f"https://us-central1-kfp.pkg.dev/{project_id}/{kfp_repo_name}/{template_name}/" + \
            versionName,
        parameter_values={
            "train_display_name": "kfpv2-custom-tf-reg-train",
            "inference_display_name": "kfpv2-custom-tf-reg-inference",
            "model_uri": model_uri,
            "prebuilt_image_inference": prebuilt_image_inference
            }
        )
    
    job.submit()
    
# %%
