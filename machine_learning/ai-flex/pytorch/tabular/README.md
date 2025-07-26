![](../../images/ai-flex-customjob.png)

# Getting Started
All the steps are modular/flexible therefore the order is not important, variables.py is the file for setting the values [change this file].

Dataset is not real is synthethic, created from [CreateSyntheticDataset.py](https://github.com/jchavezar/vertex-ai-samples/blob/main/ai-flex/pytorch/tabular/CreateSyntheticDataset.py)

## Training

Training code is under the folder */trainer*, this folder has 1 file only: [train.py](https://github.com/jchavezar/vertex-ai-samples/blob/main/ai-flex/pytorch/tabular/trainer/train.py) *"for training"*.

```mermaid
graph TB
        A[Google Cloud Storage] ---> |train.csv| X[train:pd.DataFrame]
    subgraph  ""
        direction TB
        X(random split) --> Y
        X(random split) --> Z
        Y[train:pd.DataFrame] --> |dataset| F
        Z[val:pd.DataFrame] --> |dataset| F
        D[CategoryEmbeddingModelConfig] --> E[Model]
        C[LinearHeadConfig] --> E[Model]
        E --> |training: model.fit| F(Training)
        id1{{aiplatform.CustomJob}}
    end
        F --> |model save| G[Google Cloud Storage]
```

### For custom containers
#### Build & Push Images

Container Images Sizes:
- cpu = 6.69GB
- gpu = 18.9GB

```sh
docker build -t us-central1-docker.pkg.dev/vtxdemos/custom-trains/pytorch-random_cpu:1.0 -f Dockerfile_train_[cpu] .
docker push us-central1-docker.pkg.dev/vtxdemos/custom-trains/pytorch-random_cpu:1.0

docker build -t us-central1-docker.pkg.dev/vtxdemos/custom-trains/pytorch-random_gpu:1.0 -f Dockerfile_train_[gpu] .
docker push us-central1-docker.pkg.dev/vtxdemos/custom-trains/pytorch-random_gpu:1.0
```

### For pre-built containers
#### Build Eggs or Python Distribution Packages and Copy to GCS
```sh
python setup.py sdist --formats=gztar
gsutil cp dist/trainer-0.1.tar.gz gs://vtxdemos-dist/ai-flex-train/trainer-pytorch.tar.gz
```
### Run jobs

```sh
python CustomJob[*][*].py
```
*\*\* are file types: custom-container/prebuilt, cp/gpu*

## Prediction

Prediction code is under /inference which has 1 file "main.py", we ise fastapi + uvicorn as a web server to serve tensorflow model.

```mermaid
graph TB
        A[Google Cloud Storage] ---> |gs://vtxdemos-models/ecommerce/09-08-23/model/*| B(Model Registry)
    subgraph  Models
        direction TB
        B -- "model version" --> C(Deploy)
        id1([aiplatform.Model.upload])
    end
    subgraph "Endpoints"
        direction TB
        E(Endpoint Create)
        C --> |machine type, accelerator| D(Public Endpoint)
        E --> |machine type, accelerator| D(Public Endpoint)
        id2([aiplatform.Endpoint.create])
    end
```

### For custom containers
#### Build & Push Images

Container Images Sizes:
- cpu = 2.45GB

```sh
docker build -t us-central1-docker.pkg.dev/vtxdemos/custom-predictions/pytorch-random_cpu:1.0 -f Dockerfile_prediction_[cpu] .
docker push us-central1-docker.pkg.dev/vtxdemos/custom-predictions/pytorch-random_cpu:1.0
```

## Run Upload Jobs
```sh
python CustomJob[*][*].py
```
*\*\* are file types: custom-container/prebuilt, cp/gpu*

## Request Format

Format is correlated to upload component type: **custom-container** or **pre-built-container**

### For Custom Container:

As we can see in the *main.py* file, the code is expecting the following format:

```
{
    "instances": [
        {
            "feature_column_name_1": ["value_row1", "value_row2"],
            "feature_column_name_2": ["value_row1", "value_row2"]
        }
    ]
}
```

### For Pre-built Container:

REST accepts json files in the following format:

```
{
    "instances": [
        {
            "feature_column_name_1": ["value_row1"],
        },
        {
            "feature_column_name_2": ["value_row2"],
        }
    ]
}
```

## Comments

We can also chain the calls/components like this and have them in 1 file:

```python

from variables import *
from google.cloud import aiplatform

aiplatform.init(project=project_id, location=region, staging_bucket=staging_bucket)

#region vertexai CustomJob
model = aiplatform.CustomJob(
    display_name=display_name_job+"-cpu",
    worker_pool_specs=[
        {
            "machine_spec": {
                "machine_type": machine_type_cpu,
                #"accelerator_type": accelerator_type,
                #"accelerator_count": accelerator_count,
            },
            "replica_count": replica_count,
            "container_spec": {
                "image_uri": custom_train_image_uri_cpu,
                "args": ["python", "-m", "trainer.train", "--dataset", dataset_uri]
            },
        },
    ],
    base_output_dir = model_uri,
    labels= {
        "ai-flex": "custom-train-cpu"
        }
)
model=model.run()
#endregion


#region vertexai Import to Model Registry and Deploy
model = aiplatform.Model.upload(
    display_name=display_name_job, 
    artifact_uri=model_uri, 
    serving_container_image_uri=custom_predict_image_uri_cpu
)

endpoint = aiplatform.Endpoint.create(
    display_name=display_name_job+"cpu", 
)

model.deploy(
    endpoint=endpoint, 
    traffic_split={"0": 100},
    machine_type=machine_type_cpu, 
    min_replica_count=1, 
    max_replica_count=1, 
    sync=True
)
```