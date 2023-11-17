```bash
docker build -t [gcr.io/vtxdemos/events-pubsub] -f Dockerfile_preprocess .
docker push gcr.io/[vtxdemos]/events-pubsub
```

```bash
gcloud run deploy [preprocess-video] --cpu 8 --memory 32Gi --image [gcr.io/vtxdemos/events-pubsub] --allow-unauthenticated
```

```bash
gcloud eventarc triggers create [preprocess-video-trigger] \
--location=[us-central1] \
--service-account=[254356041555-compute@developer.gserviceaccount.com] \
--destination-run-service=[preprocess-video] \
--destination-run-region=[us-central1] \
--destination-run-path="/" \
--event-filters="bucket=[vtxdemos-videos]" \
--event-filters="type=google.cloud.storage.object.v1.finalized"
```