#%%
from kfp import compiler
from kfp.dsl import component, pipeline
from google.cloud import aiplatform as aip

aip.init(
    project="vtxdemos",
    location="us-central1",
)

@component(packages_to_install=["pandas"])
def component1(x:str) -> int:
    return int(x)

@component
def component2(x:int) -> int:
    print(2*x)
    return 2*x

@pipeline(name="pipe1")
def pipe():
    ob1 = component1(x="5")
    obj2 = component2(x=ob1.output)

compiler.Compiler().compile(
    pipeline_func=pipe,
    package_path='pipe.yaml')

job = aip.PipelineJob(
    display_name="sum-pipe",
    template_path="pipe.yaml",
    pipeline_root="gs://vtxdemos-tmp/pipe-artifacts",
    parameter_values={
    }
)

job.submit(service_account="vtxdemos@vtxdemos.iam.gserviceaccount.com")

# %%
