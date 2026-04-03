# Agent Engine Deployment

> **Navigation**: [README](../README.md) | [Overview](01-OVERVIEW.md) | [Entra ID](02-ENTRA-ID-SETUP.md) | [WIF](03-WIF-SETUP.md) | [Local Testing](04-LOCAL-TESTING.md) | **Agent Engine** | [GE Setup](06-GEMINI-ENTERPRISE.md)

This guide covers deploying the ADK agent to Vertex AI Agent Engine.

## Prerequisites

1. **Local testing passed** (see 04-LOCAL-TESTING.md)
2. **GCP permissions**:
   - `roles/aiplatform.admin` for deployment
   - `roles/storage.admin` on staging bucket
3. **Staging bucket** accessible by the Vertex AI service agent

## Step 1: Configure Deployment

Update `.env` with deployment settings:

```env
# GCP Configuration
PROJECT_ID=your-project-id
PROJECT_NUMBER=440133963879
LOCATION=us-central1
STAGING_BUCKET=gs://your-staging-bucket

# Discovery Engine
ENGINE_ID=your-engine-id
DATA_STORE_ID=your-datastore-id

# WIF Configuration
WIF_POOL_ID=entra-id-oidc-pool
WIF_PROVIDER_ID=entra-id-provider

# Authorization ID
AUTH_ID=sharepointauth
```

## Step 2: Grant Storage Permissions

The Vertex AI service agent needs access to the staging bucket:

```bash
export PROJECT_NUMBER=440133963879
export STAGING_BUCKET=your-staging-bucket

# Grant storage admin to Vertex AI service agent
gcloud storage buckets add-iam-policy-binding gs://$STAGING_BUCKET \
  --member="serviceAccount:service-${PROJECT_NUMBER}@gcp-sa-aiplatform.iam.gserviceaccount.com" \
  --role="roles/storage.admin"
```

## Step 3: Deploy Agent

```bash
uv run python deploy.py
```

Expected output:
```
=====================================
Deploying ADK Agent to Agent Engine
=====================================
Project:  your-project-id
Location: us-central1
Staging:  gs://your-staging-bucket
=====================================

Creating Agent Engine deployment...
Environment variables: {'PROJECT_NUMBER': '...', 'ENGINE_ID': '...', ...}
...
AgentEngine created. Resource name: projects/xxx/locations/us-central1/reasoningEngines/yyy

=====================================
Deployment Complete!
=====================================
Resource Name: projects/xxx/locations/us-central1/reasoningEngines/yyy
=====================================
```

**Save the Resource Name** - you'll need it for Gemini Enterprise registration.

## Step 4: Grant Discovery Engine Permissions

The Agent Engine service account needs Discovery Engine access:

```bash
export PROJECT_NUMBER=440133963879
export PROJECT_ID=your-project-id

# Grant to Reasoning Engine service agent
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:service-${PROJECT_NUMBER}@gcp-sa-aiplatform-re.iam.gserviceaccount.com" \
  --role="roles/discoveryengine.admin"

# Grant service usage consumer
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:service-${PROJECT_NUMBER}@gcp-sa-aiplatform-re.iam.gserviceaccount.com" \
  --role="roles/serviceusage.serviceUsageConsumer"
```

## Step 5: Test Deployed Agent

### Using test_agent.py

```bash
export REASONING_ENGINE_RES="projects/xxx/locations/us-central1/reasoningEngines/yyy"
uv run python test_agent.py deployed "what documents do you have?"
```

### Using Raw API

```bash
# Create session
curl -X POST \
  "https://us-central1-aiplatform.googleapis.com/v1/$REASONING_ENGINE_RES:createSession" \
  -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  -H "Content-Type: application/json" \
  -d '{"input": {"user_id": "test"}}'

# Query (replace SESSION_ID with actual ID)
curl -X POST \
  "https://us-central1-aiplatform.googleapis.com/v1/$REASONING_ENGINE_RES:streamQuery" \
  -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "message": "what documents do you have?",
      "user_id": "test",
      "session_id": "SESSION_ID"
    }
  }'
```

## Step 6: Update Deployed Agent

To update after code changes:

```bash
uv run python deploy.py update projects/xxx/locations/us-central1/reasoningEngines/yyy
```

## Environment Variables in Agent Engine

The `deploy.py` passes environment variables via `env_vars`:

```python
# deploy.py
env_vars = {
    "PROJECT_NUMBER": os.environ.get("PROJECT_NUMBER", ""),
    "ENGINE_ID": os.environ.get("ENGINE_ID", ""),
    "WIF_POOL_ID": os.environ.get("WIF_POOL_ID", ""),
    "WIF_PROVIDER_ID": os.environ.get("WIF_PROVIDER_ID", ""),
    "AUTH_ID": os.environ.get("AUTH_ID", "sharepointauth"),
}

app = reasoning_engines.AdkApp(
    agent=root_agent,
    enable_tracing=True,
    env_vars=env_vars,
)
```

## Viewing Logs

Check Agent Engine logs in Cloud Logging:

```bash
export REASONING_ENGINE_ID=yyy  # Last part of resource name

gcloud logging read \
  'resource.type="aiplatform.googleapis.com/ReasoningEngine" resource.labels.reasoning_engine_id="'$REASONING_ENGINE_ID'"' \
  --project=$PROJECT_ID \
  --limit=50 \
  --format='value(textPayload)'
```

### Debug Context Logging

The agent logs context details for troubleshooting:

```
[CONTEXT DEBUG] Tool Context Details:
  tool_context type: <class 'google.adk.agents.context.Context'>
  state keys: ['temp:sharepointauth']
  temp:sharepointauth: eyJ...
```

## Troubleshooting

### Deployment Errors

| Error | Solution |
|-------|----------|
| `storage.objects.get permission denied` | Grant storage.admin on staging bucket |
| `cloudpickle error` | Check dependencies match |
| `ModuleNotFoundError` | Add module to `extra_packages` |

### Runtime Errors

| Error | Solution |
|-------|----------|
| `Session not found` | Use session ID from create_session response |
| `env var not set` | Check env_vars passed in deploy.py |
| `Discovery Engine 403` | Grant discoveryengine.admin to RE service agent |

### SDK Parameter Mismatch

The SDK uses `message` but ADK expects different parameters. Use raw API for testing:

```python
# SDK calls with 'message' but backend expects specific format
payload = {
    'input': {
        'message': 'your query',
        'user_id': 'test',
        'session_id': session_id
    }
}
```

## Service Accounts

| Service Account | Purpose |
|-----------------|---------|
| `service-XXX@gcp-sa-aiplatform.iam.gserviceaccount.com` | Vertex AI Platform SA |
| `service-XXX@gcp-sa-aiplatform-re.iam.gserviceaccount.com` | Reasoning Engine SA |
| `XXX-compute@developer.gserviceaccount.com` | Compute Engine Default SA |

The **Reasoning Engine SA** (`@gcp-sa-aiplatform-re`) is used at runtime and needs Discovery Engine permissions.
