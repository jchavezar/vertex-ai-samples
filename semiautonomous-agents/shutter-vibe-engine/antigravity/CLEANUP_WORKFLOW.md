# Teardown Workflow: Shutter Vibe Engine Cleanup

This workflow outlines the steps to completely tear down all Google Cloud resources and clean up all local bootstrapped folders created during the Shutter Vibe Engine replication.

---

## 🚀 Interactive Cleanup Step

The agent or user can run the pre-packaged cleanup script in the workspace root to automate the deletion of all resources:

```bash
bash antigravity/cleanup.sh
```

### What this workflow removes:

1. **Eventarc trigger**: `envato-vibe-ingest-trigger`
2. **Cloud Run services**: `envato-vibe-app` and `envato-vibe-ingest`
3. **Cloud Storage bucket**: `gs://${ENVATO_GCS_BUCKET}` (and all ingested objects/segments recursively)
4. **IAM bindings**: Removes all permissions associated with the runner service account.
5. **Service Account**: `envato-vibe-runner@${GOOGLE_CLOUD_PROJECT}.iam.gserviceaccount.com`
6. **Local files**: Deletes the `multimodal-search/`, `demos/`, `.env`, and `.gitignore` paths.
