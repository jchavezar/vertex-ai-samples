---
description: Destroy GCS datastore and clean up all resources in vtxdemos
---

A recipe to detach the GCS Data Store from the Gemini Enterprise engine, delete the Data Store, and delete the GCS bucket to avoid any costs.

### Step 1: Execute Teardown Script
Execute the Python teardown script to destroy all resources:

```bash
uv run agy-recipes/ge_api_wif_gcs/scripts/teardown.py
```

This will automatically load `last_setup_resources.json` to find the exact resources created and delete them.
