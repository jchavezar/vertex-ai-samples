![Alt text](images/video_architecture.png)

# Steps:

## Requirements:
- CloudSQL Database: 
    
    ```bash 
    gcloud sql databases create $database_name --instance pg15-pgvector-demo```

- Google Cloud Storage Bucket *(create 4 buckets: video_gcs_uri, video_transcript_annotations_gcs, fps_gcs_uri, snippets_gcs_uri)*: 
```bash 
gsutil mb [YOUR_BUCKET_NAME]
```
- 3 main documents: *_preprocess_embeddings, front_search_engine (web server), credentials.py

*I'll clean variables settings but for now you will have to change credentials and *_preprocess_embeddings variables like project_id, region, video_gcs_uri etc*

## Execution Instructions:
- Run what's inside of video_preprocess_embeddings for videos
- [OPTIONAL] if you want to run documents as well run document_preprocess_embeddings

After building the Vector Database you can deploy the front with the following command (service account is optional):
```bash
gcloud run deploy search --source=. --region=us-central1 --service-account=cloud-run@vtxdemos.iam.gserviceaccount.com
``````