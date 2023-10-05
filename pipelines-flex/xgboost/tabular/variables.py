import time
_date=time.strftime("%x").replace("/", "-")

pipeline_name = "xgboost-classification-mlops1"
project_id = "vtxdemos"
region = "us-central1"
prefix = "xgboost-synthetic"
training_machine_type = "n1-standard-4"
accelerator_type = "NVIDIA_TESLA_T4"
accelerator_count = 1
replica_count = 1
custom_train_image_uri_cpu = "us-central1-docker.pkg.dev/vtxdemos/custom-trains/xg-synthetic_cpu:1.0"
model_uri = f"gs://vtxdemos-models/synthetic/pipe/{_date}"
dataset_uri = "vtxdemos.public.ctgan-synthetic"
package_path = "pipeline.yaml"
pipeline_root = "gs://vtxdemos-staging"
experiment_name = "xgboost--synthetic-flex"
custom_predict_image_uri_cpu = "us-central1-docker.pkg.dev/vtxdemos/custom-predictions/xg-pipe-synthetic_cpu:1.0"
custom_predict_image_uri_gpu = "us-central1-docker.pkg.dev/vtxdemos/custom-predictions/xg-pipe-synthetic_gpu:1.0"