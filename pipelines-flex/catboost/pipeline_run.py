# %%
import kfp
import datetime
from kfp import components
#from kfp.dsl import Artifact, Output
from google.cloud import aiplatform

now = datetime.datetime.now()
identifier = now.strftime("%Y%m%d-%H%M")

train = components.load_component_from_file(
  'components/train/train_component.yaml')

deploy = components.load_component_from_file(
    'components/inference/kubeflow_component/inference_component.yaml')


# Pipelines
@kfp.dsl.pipeline(name="catboost-ecommerce-pipeline")
def pipeline(
    bq_dataset: str,
    project_id: str,
    experiment_name: str,
    run_num: str,
):
  train_job = train(
      bq_dataset=bq_dataset,
      project_id=project_id,
      experiment_name=experiment_name,
      run_num=run_num
  )

  deploy(
      aip_storage_uri=train_job.output,
      project_id=project_id,
  )


kfp.compiler.Compiler().compile(pipeline_func=pipeline,
                                package_path="catboost.yaml")

aiplatform.init(project="vtxdemos", location="us-central1")

job = aiplatform.PipelineJob(
    display_name="catboost-ecommerce",
    template_path="catboost.yaml",
    pipeline_root="gs://vtxdemos-staging",
    parameter_values={
        "bq_dataset": "vtxdemos.demos_us.ecommerce_balanced",
        "project_id": "vtxdemos",
        "experiment_name": "catboost-ecommerce",
        "run_num": f"num-{identifier}",
    }
)

job.submit()
