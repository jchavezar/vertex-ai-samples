import time
_date=time.strftime("%x").replace("/", "-")

# Init Values
project_id = "vtxdemos"
region = "us-central1"
staging_bucket = "gs://vtxdemos-staging/random"
display_name_job = "pytorch-random-customjob"

#Docker Images
custom_train_image_uri_cpu = "us-central1-docker.pkg.dev/vtxdemos/custom-trains/pytorch-random_cpu:1.0"
custom_train_image_uri_gpu = "us-central1-docker.pkg.dev/vtxdemos/custom-trains/pytorch-random_gpu:1.0"
prebuilt_train_image_uri_cpu_gpu = "us-docker.pkg.dev/vertex-ai/training/pytorch-gpu.1-13.py310:latest"
prebuilt_train_package_uri = "gs://vtxdemos-dist/ai-flex-train/trainer-pytorch.tar.gz"
custom_predict_image_uri_cpu = "us-central1-docker.pkg.dev/vtxdemos/custom-predictions/pytorch-random_cpu:1.0"
custom_predict_image_uri_gpu = "us-central1-docker.pkg.dev/vtxdemos/custom-predictions/pytorch-random_gpu:1.0"
prebuilt_preidct_image_uri_cpu = "us-docker.pkg.dev/vertex-ai/prediction/pytorch-cpu.2-0:latest"
prebuilt_predict_image_uri_gpu = "us-docker.pkg.dev/vertex-ai/prediction/pytorch-gpu.2-0:latest"

# Data source and storage
dataset_uri = "gs://vtx-datasets-public/pytorch_tabular/synthetic/train.csv"
model_uri = f"gs://vtxdemos-models/random/{_date}"

# Machine Types
machine_type_cpu = "n1-standard-4"
machine_type_gpu = "n1-standard-4"
accelerator_type = "NVIDIA_TESLA_P100"
accelerator_count = 1
replica_count = 1