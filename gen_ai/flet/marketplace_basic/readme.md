# Configure CORS to Google Cloud Storage

```bash
gcloud storage buckets update gs://vtxdemos-fstoresearch-datasets --cors-file=cors.json
```

# Create Docker Container
```bash
gcloud builds submit -t us-central1-docker.pkg.dev/vtxdemos/cloud-run-source-deploy/markeplace_basic:v1 .
```
