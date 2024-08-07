import argparse
from google.cloud import aiplatform

parser = argparse.ArgumentParser(description='Deploy Catboost Inference Webserver')
parser.add_argument("--project-id", type=str, default="vtxdemos")
parser.add_argument("--aip-storage-uri")
args = parser.parse_args()

aiplatform.init(project=args.project_id, location="us-central1")

model = aiplatform.Model.upload(
    display_name="catboost-inference",
    artifact_uri=args.aip_storage_uri,
    serving_container_image_uri="us-central1-docker.pkg.dev/vtxdemos/custom-predictions/catboost-predict:1.0"
)

endpoint = aiplatform.Endpoint.create(
    display_name="catboost-inference-ep",
)

model.deploy(
    endpoint=endpoint,
    traffic_split={"0": 100},
    machine_type="n1-standard-4",
    min_replica_count=1,
    max_replica_count=1,
    sync=True
)