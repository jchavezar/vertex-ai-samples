---
description: Tear down the Shutter Vibe Engine frontend, serverless ingestion pipeline, and GCS buckets on GCP
---
# Cleaning up the Multimodal Vibe Search Application

This workflow outlines the automated steps to delete all Cloud Run services, Eventarc triggers, GCS storage buckets, Service Accounts, and local folders.

---

## 1. Execute Automatic Teardown Script

Run the automated script to clean up both local and remote assets:

// turbo
```bash
bash antigravity/cleanup.sh
```
