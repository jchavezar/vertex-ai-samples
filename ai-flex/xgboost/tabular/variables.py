import time
_date=time.strftime("%x").replace("/", "-")

# Init Values
project_id = "vtxdemos"
region = "us-central1"
staging_bucket = "gs://vtxdemos-staging/wholesales"
display_name_job = "xg-wholesales-customjob"

#Docker Images
custom_train_image_uri_cpu = "us-central1-docker.pkg.dev/vtxdemos/custom-trains/xg-wholesales_cpu:1.0"
custom_train_image_uri_gpu = "us-central1-docker.pkg.dev/vtxdemos/custom-trains/xg-wholesales_gpu:1.0"
#prebuilt_train_image_uri_cpu = "us-docker.pkg.dev/vertex-ai/training/tf-cpu.2-12.py310:latest"
#prebuilt_train_image_uri_gpu = "us-docker.pkg.dev/vertex-ai/training/tf-gpu.2-12.py310:latest"
#prebuilt_train_package_uri = "gs://vtxdemos-dist/ai-flex-train/trainer-0.1.tar.gz"
custom_predict_image_uri_cpu = "us-central1-docker.pkg.dev/vtxdemos/custom-predictions/xg-wholesales_cpu:1.0"
custom_predict_image_uri_gpu = "us-central1-docker.pkg.dev/vtxdemos/custom-predictions/xg-wholesales_gpu:1.0"
#prebuilt_predict_image_uri_cpu = "us-docker.pkg.dev/vertex-ai/prediction/tf2-cpu.2-12:latest"
#prebuilt_predict_image_uri_gpu = "us-docker.pkg.dev/vertex-ai/prediction/tf2-gpu.2-12:latest"

# Data source and storage
dataset_dir = "vtxdemos.public.ctgan-synthetic"
model_dir = f"gs://vtxdemos-models/wholesales/{_date}/"
best_model_uri_after_ht = f"gs://vtxdemos-models/wholesales/{_date}/1/model"

# Machine Types
machine_type_cpu = "n1-standard-4"
machine_type_gpu = "n1-standard-4"
accelerator_type = "NVIDIA_TESLA_P100"
accelerator_count = 1
replica_count = 1