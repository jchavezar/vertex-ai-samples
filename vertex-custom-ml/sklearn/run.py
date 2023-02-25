# %%

# Libraries
from google.cloud import aiplatform as aip

# Variables

IMAGE_TRAIN_URI = "gcr.io/jchavezar-demo/sklearn-train:latest"
IMAGE_PREDICTION_URI = "gcr.io/jchavezar-demo/ecommerce:fast-onnx"
MODEL_URI = "gs://vtx-models/ecommerce/sklearn"

aip.init(project='jchavezar-demo', staging_bucket='gs://vtx-staging')
# %%

# Model Training on Vertex

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

model = aip.Model.upload(
    display_name='sklearn-ecommerce-1',
    artifact_uri=f'{MODEL_URI}/model',
    serving_container_image_uri=IMAGE_PREDICTION_URI,
    serving_container_predict_route='/predict',
    serving_container_health_route='/health'
)

# %%

endpoint = model.deploy(
    deployed_model_display_name='sklearn-ecommerce',
    machine_type='n1-standard-2',
    min_replica_count=1,
    max_replica_count=1
)
# %%
## Test
data_dict = {
    "latest_ecommerce_progress": [0],
	"bounces": [1],
	"time_on_site": [0],
	"pageviews": [1],
	"source": ["google"],
	"medium": ["organic"],
	"channel_grouping": ["Organic Search"],
	"device_category": ["desktop"],
	"country": ["India"]
}

data_dict = {
	"instances": [{
		"latest_ecommerce_progress": 0,
		"bounces": 1,
		"time_on_site": 0,
		"pageviews": 1,
		"source": "google",
		"medium": "organic",
		"channel_grouping": "Organic Search",
		"device_category": "desktop",
		"country": "India"
	}]
}

endpoint.predict(data_dict)

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

## Undeploy and Delete Components

# %%
endpoint.undeploy()

# %%
model.delete
