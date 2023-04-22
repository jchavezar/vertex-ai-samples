#%%
import argparse
import os
import yaml

from google.cloud import aiplatform


def parse_args():
    parser = argparse.ArgumentParser(description="Utility tool to trigger vertex pipelines jobs")
    parser.add_argument("--config_path", help="Pipeline config file", required=True)
    parser.add_argument("--pipeline_path", help="Pipeline path", required=False, default='pipeline.yaml')
    parser.add_argument("--prefix_name", help="Prefix name", required=False, default='transformer-nlp-tf2')
    parser.add_argument("--project", help="Pipeline path", required=False, default=os.getenv("PROJECT_ID"))
    parser.add_argument("--region", help="Pipeline path", required=False, default="us-central1")
    parser.add_argument("--submit_pipeline_sync", help="Pipeline path", required=False, default="true")
    parser.add_argument("--enable_caching", help="Pipeline path", required=False, default="true")

    args = parser.parse_args()
    args.submit_pipeline_sync = str(args.submit_pipeline_sync).lower() in ('true', '1', 't')
    args.enable_caching = str(args.enable_caching).lower() in ('true', '1', 't')

    return args


def trigger_pipeline(
        project,
        region,
        pipeline_name,
        pipeline_path,
        pipeline_root,
        experiment_name,
        prefix_name,
        labels,
        submit_pipeline_sync,
        enable_caching
):
    aiplatform.init(project=project, location=region)
    job = aiplatform.PipelineJob(
        display_name=pipeline_name,
        template_path=pipeline_path,
        pipeline_root=pipeline_root,
        parameter_values={
            "project_id": project,
            "prefix_name": prefix_name
        },
        labels=labels,
        enable_caching=enable_caching
    )
    job.submit(experiment=experiment_name)

    if submit_pipeline_sync:
        job.wait()


if __name__ == "__main__":
    #args = parse_args()
    config = yaml.safe_load(open("../../training/config.yaml"))

    trigger_pipeline(
        project="vtxdemos",
        region="us-central1",
        pipeline_path="../../training/pipeline.yaml",
        pipeline_root=f"gs://vtxdemos-pipelines",
        pipeline_name=config['pipeline_name'],
        experiment_name=config.get('experiment_name', config['pipeline_name']),
        prefix_name="testingcharge",
        labels=config.get("labels", {}),
        submit_pipeline_sync=True,
        enable_caching=True
    )
    #%%
    !ls ../../training
# %%
