# GCP Project Setup

> **Version**: 1.0.0 | **Last Updated**: 2026-04-03

**Navigation**: [README](../README.md) | **GCP Setup** | [Entra ID](02-SETUP-ENTRA.md) | [WIF](03-SETUP-WIF.md) | [Discovery](04-SETUP-DISCOVERY.md) | [Local Dev](05-LOCAL-DEV.md) | [Agent Engine](06-AGENT-ENGINE.md)

---

## Overview

This guide covers creating and configuring the GCP project for SharePoint WIF Portal.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           GCP COMPONENTS                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   Project: sharepoint-wif-agent                                             │
│   ├── Discovery Engine API      → SharePoint search                         │
│   ├── Vertex AI API             → Agent Engine (optional)                   │
│   ├── IAM API                   → Workforce Identity Federation             │
│   ├── STS API                   → Token exchange                            │
│   └── Cloud Resource Manager    → Project management                        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Step 1: Create Project

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Click **Select Project** → **New Project**
3. Enter project name (e.g., `sharepoint-wif-agent`)
4. Click **Create**

**Save these values:**

| Setting | Value |
|---------|-------|
| Project ID | `sharepoint-wif-agent` |
| Project Number | `545964020693` |

---

## Step 2: Enable APIs

Run in Cloud Shell or terminal:

```bash
gcloud config set project sharepoint-wif-agent

gcloud services enable \
  aiplatform.googleapis.com \
  discoveryengine.googleapis.com \
  iam.googleapis.com \
  sts.googleapis.com \
  cloudresourcemanager.googleapis.com
```

**Verify:**

```bash
gcloud services list --enabled --filter="NAME:(aiplatform OR discoveryengine OR iam OR sts)"
```

---

## Step 3: Create Staging Bucket (Optional)

Required only if deploying to Agent Engine:

```bash
export PROJECT_ID=sharepoint-wif-agent
export LOCATION=us-central1

gcloud storage buckets create gs://${PROJECT_ID}-staging \
  --location=${LOCATION} \
  --uniform-bucket-level-access
```

---

## Verification Checklist

| Item | Command | Expected |
|------|---------|----------|
| Project set | `gcloud config get project` | `sharepoint-wif-agent` |
| APIs enabled | `gcloud services list --enabled` | 5 APIs listed |
| Bucket created | `gcloud storage ls` | `gs://sharepoint-wif-agent-staging/` |

---

## Next Step

→ [02-SETUP-ENTRA.md](02-SETUP-ENTRA.md) - Configure Microsoft Entra ID
