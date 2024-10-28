#%%
import kfp
from google.cloud import aiplatform
from kfp.registry import RegistryClient
from kfp.dsl import component, pipeline


@component
def summ(sum_a: int, sum_b: int) -> float:
    return float(sum_a + sum_b)


@component
def mul(mult_a: float, mult_b: float) -> str:
    return str(mult_a * mult_b)


@pipeline(name="single_pipe_kfp")
def pipeline(
        sum_a: int,
        sum_b: int,
        mult_b: float,
):
    sum_job = summ(sum_a=sum_a, sum_b=sum_b)
    mul_job = mul(mult_a=sum_job.output, mult_b=mult_b)


kfp.compiler.Compiler().compile(pipeline_func=pipeline,
                                package_path="/tmp/single_pipe_kfp.yaml")

client = RegistryClient(host=f"https://us-central1-kfp.pkg.dev/vtxdemos/kfp-repo")
templateName, versionName = client.upload_pipeline(
    file_name="/tmp/single_pipe_kfp.yaml",
    tags=["v1", "latest"],
    extra_headers={"description": "This is an example pipeline template."})

aiplatform.init(project="vtxdemos")

pipeline_job = aiplatform.PipelineJob(
    display_name="single_pipe_kfp",
    template_path="/tmp/single_pipe_kfp.yaml",
    pipeline_root="gs://vtxdemos-staging",
    enable_caching=False,
    parameter_values={
        "sum_a": 2343454,
        "sum_b": 2389934,
        "mult_b": 23478.12567
    }
)

pipeline_job.submit()
