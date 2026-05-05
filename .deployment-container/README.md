# Deployment Container

Solves the 2-account credential split for deployments.

## The Problem

- **Claude Code** needs: jesusarguelles@google.com → cloud-llm-preview1
- **Deployments** need: admin@jesusarguelles.altostrat.com → sharepoint-wif/vtxdemos

ADC auto-discovery picks the wrong one, causing permission errors.

## The Solution

Run all deployments in a Docker container with **explicit service account credentials**.

## Usage

```bash
# Build the container
gcloud builds submit --tag us-central1-docker.pkg.dev/sharepoint-wif/docparse/deployer:latest .

# Deploy something (e.g., Firestore agent)
gcloud builds submit \
  --config=deploy_firestore.yaml \
  --project=sharepoint-wif \
  /path/to/docparse-firestore-grounding/
```

The Cloud Build config mounts the service account automatically.
