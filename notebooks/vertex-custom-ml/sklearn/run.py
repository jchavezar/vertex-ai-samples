# %%

# Libraries
from google.cloud import aiplatform as aip

# Train Using custom containers
# -------------------------------------------------------------------------------------------------------------------------------------------------
## Variables (change these with your own values)

IMAGE_TRAIN_URI = "gcr.io/jchavezar-demo/sklearn-train:latest"
IMAGE_PREDICTION_URI = "gcr.io/jchavezar-demo/ecommerce:fast-onnx"
MODEL_URI = "gs://vtx-models/ecommerce/sklearn"

aip.init(project='jchavezar-demo', staging_bucket='gs://vtx-staging')
# %%

## Model Training on Vertex

worker_pool_specs=[
    {
        "machine_spec": {
            "machine_type": "n1-standard-4"
        },
        "replica_count" : 1,
        "container_spec": {
            "image_uri": IMAGE_TRAIN_URI
        }
    }
]

my_job = aip.CustomJob(
    display_name = "sklearn-customjob-train",
    worker_pool_specs = worker_pool_specs,
    base_output_dir = MODEL_URI,
)

my_job.run()
# checkpoint
#%%

## Upload Model

model = aip.Model.upload(
    display_name='sklearn-ecommerce-1',
    artifact_uri=f'{MODEL_URI}/model',
    serving_container_image_uri=IMAGE_PREDICTION_URI,
    serving_container_predict_route='/predict',
    serving_container_health_route='/health'
)

# %%

## Deploy Model for Online Predictions

endpoint = model.deploy(
    deployed_model_display_name='sklearn-ecommerce-1',
    machine_type='n1-standard-2',
    min_replica_count=1,
    max_replica_count=1
)
# %%
## Test
### Using Python SDK
import json

from google.api import httpbody_pb2
from google.cloud import aiplatform_v1

DATA = {
    "signature_name": "predict",
    "instances": [
        {
	        "latest_ecommerce_progress": 0,
            "bounces": 1,
            "time_on_site": 0,
            "pageviews": 1,
            "source": "google",
            "medium": "organic",
            "channel_grouping": "Organic Search",
            "device_category": "desktop",
            "country": "India"
        }
    ],
}

http_body = httpbody_pb2.HttpBody(
    data=json.dumps(DATA).encode("utf-8"),
    content_type="application/json",
)

req = aiplatform_v1.RawPredictRequest(
    http_body=http_body, endpoint=endpoint.resource_name
)

### Using Rest
#%%

!(curl \
-X POST \
-H "Authorization: Bearer $(gcloud auth print-access-token)" \
-H "Content-Type: application/json" \
https://us-central1-aiplatform.googleapis.com/v1/projects/jchavezar-demo/locations/us-central1/endpoints/5619353240912003072:predict \
-d '{"instances": [{ \
		"latest_ecommerce_progress": 0, \
		"bounces": 1, \
		"time_on_site": 0, \
		"pageviews": 1, \
		"source": "google", \
		"medium": "organic", \
		"channel_grouping": "Organic Search", \
		"device_category": "desktop", \
		"country": "India" \
	}] \
}')


# Train Using local.script and pre-built container images
# -------------------------------------------------------------------------------------------------------------------------------------------------

#%%

job = aip.CustomJob.from_local_script(
    display_name="customjob-from-pythonscript",
    script_path="./training/train.py",
    container_uri="us-docker.pkg.dev/vertex-ai/training/scikit-learn-cpu.0-23:latest",
    requirements=["protobuf==3.20.2","skl2onnx", "gcsfs"],
    replica_count=1,
    base_output_dir=MODEL_URI
)

job.run()
# %%

## Upload Model

model = aip.Model.upload(
    display_name='sklearn-ecommerce-2',
    artifact_uri=f'{MODEL_URI}/model',
    serving_container_image_uri=IMAGE_PREDICTION_URI,
    serving_container_predict_route='/predict',
    serving_container_health_route='/health'
)

## Deploy Model for Online Predictions

endpoint = model.deploy(
    deployed_model_display_name='sklearn-ecommerce-2',
    machine_type='n1-standard-2',
    min_replica_count=1,
    max_replica_count=1
)

# %%


# Train Using Python Distribution Package
# -------------------------------------------------------------------------------------------------------------------------------------------------

#%%
!rm -fr source
!mkdir source
!mkdir source/trainer/
!touch source/trainer/__init__.py
!cp training/train.py source/trainer/train.py

setup_py = "import setuptools\n\nsetuptools.setup(\n\n    install_requires=[\n\n        'skl2onnx',\n\n    ],\n\n    packages=setuptools.find_packages())"
! echo "$setup_py" > source/setup.py

!tar cvf source.tar source
!gzip source.tar -f
!gsutil cp ./source.tar.gz {MODEL_URI}/packages/source.tar.gz

# %%

worker_pool_specs=[
    {
        "machine_spec": {
            "machine_type": "n1-standard-4"
        },
        "replica_count" : 1,
        "python_package_spec": {
            "executor_image_uri": "us-docker.pkg.dev/vertex-ai/training/tf-cpu.2-4:latest",
            "package_uris": [MODEL_URI+'/packages/source.tar.gz'],
            "python_module": "trainer.train"
        }
    }
]

#%%
my_trainingjob = aip.CustomJob(
    display_name = "sklearn-customjob-train",
    worker_pool_specs = worker_pool_specs,
    base_output_dir = MODEL_URI,
)

my_trainingjob.run()

## Upload Model

model = aip.Model.upload(
    display_name='sklearn-ecommerce-3',
    artifact_uri=f'{MODEL_URI}/model',
    serving_container_image_uri=IMAGE_PREDICTION_URI,
    serving_container_predict_route='/predict',
    serving_container_health_route='/health'
)

## Deploy Model for Online Predictions

endpoint = model.deploy(
    deployed_model_display_name='sklearn-ecommerce-3',
    machine_type='n1-standard-2',
    min_replica_count=1,
    max_replica_count=1
)