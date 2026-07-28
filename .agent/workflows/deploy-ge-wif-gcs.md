---
description: Deploy GCS datastore and hook it up to Gemini Enterprise in vtxdemos
---

A recipe to create a GCS bucket, upload a sample PDF, create a Discovery Engine Data Store, and hook it up to the Gemini Enterprise engine (`sockcop_gemini_enterprise`) in project `vtxdemos`.

### Step 1: Execute Setup Script
Execute the Python setup script to create the resources and index the data:

```bash
uv run agy-recipes/ge_api_wif_gcs/scripts/setup.py
```

### Step 2: Validate Data Ingestion
Once the setup completes successfully, run the test script to verify that Gemini Enterprise can answer questions grounded in the GCS document:

```bash
uv run agy-recipes/ge_api_wif_gcs/scripts/test_search.py "What is the document about?"
```

If you have a Microsoft Entra ID token, you can place it in `/tmp/entra_token.txt` before running the test script to verify the WIF token exchange pipeline.
