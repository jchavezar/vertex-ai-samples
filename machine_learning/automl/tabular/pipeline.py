#%%
import os
import time
from kfp import dsl
from kfp.dsl import pipeline
from kfp import compiler
from kfp.registry import RegistryClient
from typing import NamedTuple
from google.cloud import aiplatform
from google_cloud_pipeline_components.v1 import dataset, endpoint
from google_cloud_pipeline_components.v1.automl import training_job
from kfp.dsl import component, Input, Output, Artifact, Metrics, ClassificationMetrics
print(os.getcwd())
# os.chdir("automl/tabular/")
os.listdir("")

# Constants
project_id = "vtxdemos"
region = "us-central1"
pipeline_root = "gs://vtxdemos-pipelines"
prefix = "sockcop-experiment"
bq_source = "bq://aju-dev-demos.beans.beans1"
staging_bucket = pipeline_root
display_name = 'automl-beans{}'.format(str(int(time.time())))
api_endpoint  = f"{region}-aiplatform.googleapis.com"
thresholds_dict_str: str = '{"auRoc": 0.95}'
#%%
# Create Evaluation Component
@component(
    base_image="gcr.io/deeplearning-platform-release/tf2-cpu.2-3:latest",
    output_component_file="tabular_eval_component.yaml",
    packages_to_install=["google-cloud-aiplatform"],
)
def classification_model_eval_metrics(
        project: str,
        location: str,  # "us-central1",
        api_endpoint: str,  # "us-central1-aiplatform.googleapis.com",
        thresholds_dict_str: str,
        model: Input[Artifact],
        metrics: Output[Metrics],
        metricsc: Output[ClassificationMetrics],
) -> NamedTuple("Outputs", [("dep_decision", str)]):  # Return parameter.

    import json
    import logging

    from google.cloud import aiplatform as aip

    # Fetch model eval info
    def get_eval_info(client, model_name):
        from google.protobuf.json_format import MessageToDict

        response = client.list_model_evaluations(parent=model_name)
        metrics_list = []
        metrics_string_list = []
        for evaluation in response:
            print("model_evaluation")
            print(" name:", evaluation.name)
            print(" metrics_schema_uri:", evaluation.metrics_schema_uri)
            metrics = MessageToDict(evaluation._pb.metrics)
            for metric in metrics.keys():
                logging.info("metric: %s, value: %s", metric, metrics[metric])
            metrics_str = json.dumps(metrics)
            metrics_list.append(metrics)
            metrics_string_list.append(metrics_str)

        return (
            evaluation.name,
            metrics_list,
            metrics_string_list,
        )

    # Use the given metrics threshold(s) to determine whether the model is
    # accurate enough to deploy.
    def classification_thresholds_check(metrics_dict, thresholds_dict):
        for k, v in thresholds_dict.items():
            logging.info("k {}, v {}".format(k, v))
            if k in ["auRoc", "auPrc"]:  # higher is better
                if metrics_dict[k] < v:  # if under threshold, don't deploy
                    logging.info("{} < {}; returning False".format(metrics_dict[k], v))
                    return False
        logging.info("threshold checks passed.")
        return True

    def log_metrics(metrics_list, metricsc):
        test_confusion_matrix = metrics_list[0]["confusionMatrix"]
        logging.info("rows: %s", test_confusion_matrix["rows"])

        # log the ROC curve
        fpr = []
        tpr = []
        thresholds = []
        for item in metrics_list[0]["confidenceMetrics"]:
            fpr.append(item.get("falsePositiveRate", 0.0))
            tpr.append(item.get("recall", 0.0))
            thresholds.append(item.get("confidenceThreshold", 0.0))
        print(f"fpr: {fpr}")
        print(f"tpr: {tpr}")
        print(f"thresholds: {thresholds}")
        metricsc.log_roc_curve(fpr, tpr, thresholds)

        # log the confusion matrix
        annotations = []
        for item in test_confusion_matrix["annotationSpecs"]:
            annotations.append(item["displayName"])
        logging.info("confusion matrix annotations: %s", annotations)
        metricsc.log_confusion_matrix(
            annotations,
            test_confusion_matrix["rows"],
        )

        # log textual metrics info as well
        for metric in metrics_list[0].keys():
            if metric != "confidenceMetrics":
                val_string = json.dumps(metrics_list[0][metric])
                metrics.log_metric(metric, val_string)
        # metrics.metadata["model_type"] = "AutoML Tabular classification"

    logging.getLogger().setLevel(logging.INFO)
    aip.init(project=project)
    # extract the model resource name from the input Model Artifact
    model_resource_path = model.metadata["resourceName"]
    logging.info("model path: %s", model_resource_path)

    client_options = {"api_endpoint": api_endpoint}
    # Initialize client that will be used to create and send requests.
    client = aip.gapic.ModelServiceClient(client_options=client_options)
    eval_name, metrics_list, metrics_str_list = get_eval_info(
        client, model_resource_path
    )
    logging.info("got evaluation name: %s", eval_name)
    logging.info("got metrics list: %s", metrics_list)
    log_metrics(metrics_list, metricsc)

    thresholds_dict = json.loads(thresholds_dict_str)
    deploy = classification_thresholds_check(metrics_list[0], thresholds_dict)
    if deploy:
        dep_decision = "true"
    else:
        dep_decision = "false"
    logging.info("deployment decision is %s", dep_decision)

    return (dep_decision,)


#%%
# Define Pipeline
@dsl.pipeline(name="automl-beans-v1")
def pipeline(
        project_id: str,
        region: str,
        prefix: str,
        bq_source: str,
        thresholds_dict_str: str,
):
    ds = dataset.TabularDatasetCreateOp(
            project=project_id,
            display_name=f"{prefix}-dataset",
            bq_source=bq_source
    )

    tf = training_job.AutoMLTabularTrainingJobRunOp(
        project=project_id,
        display_name=f"{prefix}-transform",
        dataset=ds.outputs["dataset"],
        optimization_prediction_type="classification",
        column_transformations=[
            {"numeric": {"column_name": "Area"}},
            {"numeric": {"column_name": "Perimeter"}},
            {"numeric": {"column_name": "MajorAxisLength"}},
            {"numeric": {"column_name": "MinorAxisLength"}},
            {"numeric": {"column_name": "AspectRation"}},
            {"numeric": {"column_name": "Eccentricity"}},
            {"numeric": {"column_name": "ConvexArea"}},
            {"numeric": {"column_name": "EquivDiameter"}},
            {"numeric": {"column_name": "Extent"}},
            {"numeric": {"column_name": "Solidity"}},
            {"numeric": {"column_name": "roundness"}},
            {"numeric": {"column_name": "Compactness"}},
            {"numeric": {"column_name": "ShapeFactor1"}},
            {"numeric": {"column_name": "ShapeFactor2"}},
            {"numeric": {"column_name": "ShapeFactor3"}},
            {"numeric": {"column_name": "ShapeFactor4"}},
            {"categorical": {"column_name": "Class"}},
        ],
        target_column="Class",
    )

    model_eval_task = classification_model_eval_metrics(
        project=project_id,
        location=region,
        api_endpoint=api_endpoint,
        thresholds_dict_str=thresholds_dict_str,
        model=tf.outputs["model"],
    )

    with dsl.If(
            model_eval_task.outputs["dep_decision"] == "true",
            name="deploy_decision",
    ):
        endpoint_op = endpoint.EndpointCreateOp(
            project=project_id,
            location=region,
            display_name="train-automl-beans",
        )

        endpoint.ModelDeployOp(
            model=tf.outputs["model"],
            endpoint=endpoint_op.outputs["endpoint"],
            dedicated_resources_min_replica_count=1,
            dedicated_resources_max_replica_count=1,
            dedicated_resources_machine_type="n1-standard-4",
        )


# Compile the Pipeline (Download the config file)
compiler.Compiler().compile(
    pipeline_func=pipeline,
    package_path='beans_class_pipelines.yaml')

# Upload the Template
client = RegistryClient(host=f"https://us-central1-kfp.pkg.dev/{project_id}/vtxdemos")

templateName, versionName = client.upload_pipeline(
    file_name="beans_class_pipelines.yaml",
    tags=["v1", "latest"],
    extra_headers={"description":"This is an example pipeline template."})

#%%
aiplatform.init(
    #experiment="automl-tab-beans-training-v1",
    #experiment_description="tabular automl classification",
    project=project_id,
    location=region,
    staging_bucket=staging_bucket,
)

#%%
job = aiplatform.PipelineJob(
    display_name="automl-image-training-v2",
    template_path="beans_class_pipelines.yaml",
    pipeline_root=pipeline_root,
    parameter_values={
        "project_id": project_id,
        "region": region,
        "prefix": prefix,
        "bq_source": bq_source,
        "thresholds_dict_str": thresholds_dict_str
    }
)

job.submit(experiment="automl-tab-beans-training-v1")
