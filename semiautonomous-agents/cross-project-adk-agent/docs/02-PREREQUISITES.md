# Prerequisites

> **Navigation**: [README](../README.md) | [Overview](01-OVERVIEW.md) | **Prerequisites** | [Deploy](03-DEPLOY-AGENT-ENGINE.md) | [Register](04-REGISTER-GEMINI-ENTERPRISE.md) | [Testing](05-TESTING.md) | [Troubleshooting](06-TROUBLESHOOTING.md)

---

## GCP Projects

You need access to two GCP projects:

| Project | ID | Number | Purpose |
|---------|-----|--------|---------|
| Project A | `sharepoint-wif-agent` | REDACTED_PROJECT_NUMBER | Hosts Agent Engine |
| Project B | `vtxdemos` | REDACTED_PROJECT_NUMBER | Hosts Gemini Enterprise / Agentspace |

---

## Required APIs

### Project A (sharepoint-wif-agent)

```bash
gcloud services enable aiplatform.googleapis.com \
  --project=sharepoint-wif-agent
```

### Project B (vtxdemos)

```bash
gcloud services enable discoveryengine.googleapis.com \
  --project=vtxdemos
```

---

## Staging Bucket

Agent Engine requires a staging bucket in Project A for deployment artifacts:

```bash
# Check if it exists
gcloud storage ls gs://sharepoint-wif-agent-staging/ --project=sharepoint-wif-agent

# Create if needed
gcloud storage buckets create gs://sharepoint-wif-agent-staging \
  --project=sharepoint-wif-agent \
  --location=us-central1
```

Grant Vertex AI service agent access:

```bash
gcloud storage buckets add-iam-policy-binding gs://sharepoint-wif-agent-staging \
  --member="serviceAccount:service-REDACTED_PROJECT_NUMBER@gcp-sa-aiplatform.iam.gserviceaccount.com" \
  --role="roles/storage.admin"
```

---

## Agentspace App

You need an existing Agentspace (Gemini Enterprise) app in `vtxdemos`. The app ID is set as `AS_APP` in `.env`.

To find your Agentspace app ID:

```bash
curl -s -X GET \
  -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  -H "X-Goog-User-Project: vtxdemos" \
  "https://discoveryengine.googleapis.com/v1alpha/projects/REDACTED_PROJECT_NUMBER/locations/global/collections/default_collection/engines" \
  | jq '.engines[].name'
```

---

## IAM Roles

Your user account needs:

| Project | Role | Purpose |
|---------|------|---------|
| sharepoint-wif-agent | `roles/aiplatform.admin` | Deploy Agent Engine |
| sharepoint-wif-agent | `roles/storage.admin` | Upload to staging bucket |
| vtxdemos | `roles/discoveryengine.admin` | Register agents in Agentspace |

---

## Local Tools

| Tool | Version | Install |
|------|---------|---------|
| Python | 3.12+ | via pyenv or system |
| uv | latest | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| gcloud CLI | latest | `gcloud components update` |
| jq | any | `apt install jq` |

---

## Configuration

```bash
cd semiautonomous-agents/cross-project-adk-agent
cp .env.example .env
# Edit .env with your values
uv sync
```

---

**Next**: [Deploy Agent Engine →](03-DEPLOY-AGENT-ENGINE.md)
