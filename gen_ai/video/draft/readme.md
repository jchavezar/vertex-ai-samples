# Steps:

# Prerequisites

Cloud SDK installed: information [here](https://cloud.google.com/sdk/docs/install).

## Create Google Cloud Storage Buckets:

Create 4 buckets: video_gcs_uri, video_transcript_annotations_gcs, fps_gcs_uri, snippets_gcs_uri)*: 

```bash 
gsutil mb {video_gcs_uri_unique_name}
gsutil mb {video_transcript_annotations_gcs_unique_name}
gsutil mb {fps_gcs_uri_unique_name}
gsutil mb {snippets_gcs_uri_unique_name}
```

## Create a cloud sql database instance in Google Cloud.

```bash

gcloud sql instances create {instance_name} --database-version=POSTGRES_15 \
    --region={region} --cpu=1 --memory=4GB --root-password={database_password}
```

## Create a table database

```bash
gcloud sql databases create {database_name} --instance={instance_name}

```

## Create Container with Code for Preprocessing

Do not forget to change your variables.

```bash
gcloud builds submit --pack ^--^image=gcr.io/[vtxdemos]/preprocess--env=GOOGLE_PYTHON_VERSION="3.10.0"
```

```bash
gcloud run jobs create ${JOB_NAME} --execute-now \
    --image $IMAGE_NAME \
    --command python \
    --args process.py \
    --tasks $NUM_TASKS \
    --set-env-vars=INPUT_BUCKET=$INPUT_BUCKET,INPUT_FILE=$INPUT_FILE
```


gcloud run jobs create test --execute-now \
    --image gcr.io/vtxdemos/preprocess \
    --command python \
    --args process.py \
    --tasks $NUM_TASKS \
    --set-env-vars=INPUT_BUCKET=$INPUT_BUCKET,INPUT_FILE=$INPUT_FILE