# Recipe Title: [Short Description of what this replicates]

Provide a 1-2 sentence summary of what infrastructure, API, or integration this recipe sets up.

## Prerequisites

### Required APIs
Ensure the following Google Cloud APIs are enabled in the target project:
- `example.googleapis.com`

### Required IAM Roles
The identity executing this recipe (either ADC or service account) requires the following roles:
- `roles/example.admin`

### Required Environment Variables
Specify any local or runtime environment variables that must be configured:
- `GCP_PROJECT`: The target GCP project ID.
- `GCP_PROJECT_NUMBER`: The target GCP project number (needed for some Discovery Engine or WIF calls).
- `GCP_LOCATION`: Location for resources (e.g., `us-central1` or `global`).

---

## How to Run

### 1. Setup
To provision all resources and configure the recipe:
```bash
uv run scripts/setup.py
```
This script will save the names of all provisioned resources to `last_setup_resources.json`.

### 2. Verify
To run test assertions or query the provisioned resources:
```bash
uv run scripts/test_recipe.py
```

### 3. Teardown
To destroy all provisioned resources and clean up the workspace:
```bash
uv run scripts/teardown.py
```
*(This will automatically clean up the `last_setup_resources.json` file).*
