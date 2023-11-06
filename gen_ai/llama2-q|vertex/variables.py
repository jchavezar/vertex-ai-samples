import time
_date=time.strftime("%x").replace("/", "-")

# Init Values
project_id = "vtxdemos"
region = "us-central1"
staging_bucket = "gs://vtxdemos-staging/llama2-gptq"
display_name_job = "llama2-gptq"

# Data source and storage
#dataset_uri = "gs://vtxdemos-datasets-public/ecommerce/train.csv"
#model_uri = f"gs://vtxdemos-models/ecommerce/{_date}"

# Machine Types
machine_type_gpu = "g2-standard-24"
accelerator_type = "NVIDIA_L4"
accelerator_count = 2
replica_count = 1