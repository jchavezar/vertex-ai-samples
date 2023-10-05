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
custom_train_image_uri_cpu = "us-central1-docker.pkg.dev/vtxdemos/custom-trains/xg-wholesales_cpu:1.0"
model_uri = "gs://vtxdemos-models/wholesales/pipe/{_date}/model"
dataset_uri = "vtxdemos.public.ctgan-synthetic"
package_path = "pipeline.yaml"
pipeline_root = "gs://vtxdemos-staging"
experiment_name = "xgboost--synthetic-flex"
prebuilt_predict_image_uri_cpu = "us-docker.pkg.dev/vertex-ai/prediction/xgboost-cpu.1-7:latest"
prebuilt_predict_image_uri_gpu = "us-docker.pkg.dev/vertex-ai/prediction/xgboost-gpu.1-7:latest"