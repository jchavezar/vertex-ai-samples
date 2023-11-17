![Alt text](images/video_architecture.png)

# Steps:

## Create Google Cloud Storage Buckets:

- *create 4 buckets: video_gcs_uri, video_transcript_annotations_gcs, fps_gcs_uri, snippets_gcs_uri)*: 
    ```bash 
    gsutil mb {video_gcs_uri_unique_name}
    gsutil mb {video_transcript_annotations_gcs_unique_name}
    gsutil mb {fps_gcs_uri_unique_name}
    gsutil mb {snippets_gcs_uri_unique_name}
    ```

## Create a Cloud SQL Database Instance in Google Cloud.

```bash
gcloud sql instances create {instance_name} --database-version=POSTGRES_15 \
    --region={region} --cpu=1 --memory=4GB --root-password={database_password}
```

## Create a table database

```bash
gcloud sql databases create {database_name} --instance={instance_name}

```

## Trigger Cloud Functions for Preprocessing

I create a function capable of react when a video is added, so it cat call 3 APIs; Video Intelligence, Gecko Embeddings and Text Bison to create a Vector Database with enough information for the query.








- 3 main documents: *_preprocess_embeddings, front_search_engine (web server), credentials.py

*I'll clean variables settings but for now you will have to change credentials and #_preprocess_embeddings variables like project_id, region, video_gcs_uri etc*

## Execution Instructions:
- Run what's inside of video_preprocess_embeddings for videos
- [OPTIONAL] if you want to run documents as well run document_preprocess_embeddings

After building the Vector Database you can deploy the front with the following command (service account is optional):
```bash
gcloud run deploy search --source=. --region=us-central1 --service-account=cloud-run@vtxdemos.iam.gserviceaccount.com
``````