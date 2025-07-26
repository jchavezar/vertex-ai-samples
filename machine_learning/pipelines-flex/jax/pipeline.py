from kfp import compiler
from google.cloud import aiplatform
from kfp.dsl import pipeline, importer
from google_cloud_pipeline_components.types import artifact_types
from google_cloud_pipeline_components.v1.model import ModelUploadOp
from google_cloud_pipeline_components.v1.custom_job import CustomTrainingJobOp
from google_cloud_pipeline_components.v1.endpoint import EndpointCreateOp, ModelDeployOp

train_image_uri_generated_prev = "us-central1-docker.pkg.dev/vtxdemos/custom-trains/jax-train:1.0"
prediction_image_uri_generated_prev = "us-central1-docker.pkg.dev/vtxdemos/custom-predictions/jax-prediction:1.0"

worker_pool_specs = [
    {
        "machine_spec": {
            "machine_type": "n1-standard-4",
        },
        "replica_count": 1,
        "container_spec": {
            "image_uri": train_image_uri_generated_prev,
            "env": [
                {
                    "name": "SECRET_ID",
                    "value": "projects/254356041555/secrets/snow_pass/versions/1"
                }
            ],
        },
    }
]

@pipeline(name="jax-training")
def pipeline():
  training_job = CustomTrainingJobOp(
      display_name="jax-pipe-training-job",
      worker_pool_specs=worker_pool_specs,
      base_output_directory="gs://vtxdemos-models/tmp",
      service_account="vtxdemos@vtxdemos.iam.gserviceaccount.com"
  )
  importer_spec = importer(
      artifact_uri="gs://vtxdemos-models/tmp/model",
      artifact_class=artifact_types.UnmanagedContainerModel,
      metadata={"containerSpec": {"imageUri": "us-central1-docker.pkg.dev/vtxdemos/custom-predictions/jax-prediction:1.0"}}
  ).after(training_job)
  create_endpoint_job = EndpointCreateOp(
      display_name="jax-pipe-endpoint-v1"
  )
  model_upload_job = ModelUploadOp(
      display_name="jax-pipe-model",
      unmanaged_container_model=importer_spec.outputs["artifact"],
      labels={"model": "jax_model"},
      version_aliases=["version1"]
  )
  ModelDeployOp(
      endpoint=create_endpoint_job.outputs["endpoint"],
      model=model_upload_job.outputs["model"],
      dedicated_resources_machine_type="n1-standard-4",
      dedicated_resources_min_replica_count=1,
      dedicated_resources_max_replica_count=1
  )

compiler.Compiler().compile(pipeline_func=pipeline, package_path="jax-pipeline.json")

pipeline_job = aiplatform.PipelineJob(
    display_name="jax-pipeline-job",
    template_path="jax-pipeline.json",
    pipeline_root="gs://vtxdemos-staging/",
    parameter_values={},
    enable_caching=False
)

pipeline_job.submit()
