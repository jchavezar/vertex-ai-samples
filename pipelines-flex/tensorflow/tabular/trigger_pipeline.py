#%%
from variables import *
from google.cloud import aiplatform

def trigger_pipeline(
):
    aiplatform.init(project=project_id, location=region)
    
    pipeline_job = aiplatform.PipelineJob(
        display_name=prefix+"-pipeline-job",
        template_path=package_path,
        pipeline_root=pipeline_root,
        parameter_values={
            "dataset_uri": "gs://vxtdemos-datasets-public/ecommerce/train.csv"
            }
        )
        
    pipeline_job.submit(experiment=experiment_name)
    

if __name__ == "__main__":
    trigger_pipeline()
# %%
