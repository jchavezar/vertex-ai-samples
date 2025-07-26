#%%
from google.cloud import aiplatform
from kfp.dsl import component, pipeline
import kfp.compiler as compiler

aiplatform.init(project="vtxdemos", location="us-central1")

@component
def train(x: str) -> str:
    return x


@pipeline(name='a100-test')
def pipeline():
    train_job = train(x="hi").add_node_selector_constraint('NVIDIA_A100_80GB').set_gpu_limit("1")
    
compiler.Compiler().compile(pipeline, "a100-single" + ".yaml")

job = aiplatform.PipelineJob(
    display_name="kfpv2-custom-tf-reg-pipeline",
    template_path=f"a100-single.yaml",
    parameter_values={},
    )

job.submit()
# %%

from google.cloud import aiplatform
from kfp.dsl import component, pipeline
from google_cloud_pipeline_components.v1.custom_job import CustomTrainingJobOp
import kfp.compiler as compiler

aiplatform.init(project="vtxdemos", location="us-central1")

@pipeline(name='a100-test')
def pipeline():
    train_job = CustomTrainingJobOp(
        display_name="test",
        worker_pool_specs=[
            {
                "machine_spec": {
                    "machine_type": "a2-ultragpu-1g",
                    "accelerator_type": "NVIDIA_A100_80GB",
                    "accelerator_count": 1
                },
                "replica_count": 1,
                "container_spec": {
                    "image_uri": "us-central1-docker.pkg.dev/vtxdemos/custom-trains/tf-preprocess_gpu:1.0",
                    "args": ["python", "-m", "trainer.train", "--dataset", "gs://vtxdemos-datasets-public/ecommerce/train.csv"]
                }
            }
        ]
    )

compiler.Compiler().compile(pipeline, "a100-single" + ".yaml")

job = aiplatform.PipelineJob(
    display_name="kfpv2-custom-tf-reg-pipeline",
    template_path=f"a100-single.yaml",
    parameter_values={},
    )

job.submit()

# %%
