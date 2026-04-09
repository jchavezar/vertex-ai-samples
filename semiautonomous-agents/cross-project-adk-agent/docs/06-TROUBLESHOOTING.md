# Troubleshooting

> **Navigation**: [README](../README.md) | [Overview](01-OVERVIEW.md) | [Prerequisites](02-PREREQUISITES.md) | [Deploy](03-DEPLOY-AGENT-ENGINE.md) | [Register](04-REGISTER-GEMINI-ENTERPRISE.md) | [Testing](05-TESTING.md) | **Troubleshooting**

---

## Deployment Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| `storage.objects.get permission denied` | Vertex AI SA can't access staging bucket | Grant `roles/storage.admin` on bucket to `service-REDACTED_PROJECT_NUMBER@gcp-sa-aiplatform.iam.gserviceaccount.com` |
| `ModuleNotFoundError: agent` | Agent package not included | Ensure `extra_packages=["agent"]` in deploy.py |
| `cloudpickle version mismatch` | SDK auto-pins wrong version | Let the SDK handle it (it auto-appends) |
| Staging bucket not found | Bucket doesn't exist | `gcloud storage buckets create gs://sharepoint-wif-agent-staging --project=sharepoint-wif-agent` |

---

## Registration Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| `PERMISSION_DENIED` on register API | No Discovery Engine access in vtxdemos | Grant `roles/discoveryengine.admin` to your user in vtxdemos |
| `AS_APP not set` | Missing Agentspace app ID in .env | Find it: list engines in vtxdemos Discovery Engine |
| Agent registered but not visible | Agent not shared | Run share command with `ALL_USERS` scope |

---

## Cross-Project Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Agent shows in GE but fails on query | Missing IAM cross-project binding | Grant vtxdemos DE SA `aiplatform.user` on sharepoint-wif-agent |
| `PERMISSION_DENIED` at runtime | DE SA can't call Agent Engine | `gcloud projects add-iam-policy-binding sharepoint-wif-agent --member="serviceAccount:service-REDACTED_PROJECT_NUMBER@gcp-sa-discoveryengine.iam.gserviceaccount.com" --role="roles/aiplatform.user"` |
| Timeout errors | Agent Engine cold start | Retry -- first call after deploy can be slow |

---

## Key Service Accounts

| Service Account | Project | Purpose |
|-----------------|---------|---------|
| `service-REDACTED_PROJECT_NUMBER@gcp-sa-aiplatform.iam.gserviceaccount.com` | sharepoint-wif-agent | Vertex AI Platform SA |
| `service-REDACTED_PROJECT_NUMBER@gcp-sa-aiplatform-re.iam.gserviceaccount.com` | sharepoint-wif-agent | Reasoning Engine runtime SA |
| `service-REDACTED_PROJECT_NUMBER@gcp-sa-discoveryengine.iam.gserviceaccount.com` | vtxdemos | Discovery Engine SA (makes cross-project calls) |
| `REDACTED_PROJECT_NUMBER-compute@developer.gserviceaccount.com` | sharepoint-wif-agent | Default compute SA |

---

## Useful Commands

### Check Agent Engine Status

```bash
gcloud ai reasoning-engines list \
  --project=sharepoint-wif-agent \
  --region=us-central1 \
  --format="table(name, displayName, createTime)"
```

### Check IAM Bindings

```bash
# What roles does vtxdemos DE SA have on sharepoint-wif-agent?
gcloud projects get-iam-policy sharepoint-wif-agent \
  --flatten="bindings[].members" \
  --filter="bindings.members:service-REDACTED_PROJECT_NUMBER@gcp-sa-discoveryengine" \
  --format="table(bindings.role)"
```

### Check Agent Engine Logs

```bash
gcloud logging read \
  'resource.type="aiplatform.googleapis.com/ReasoningEngine"' \
  --project=sharepoint-wif-agent \
  --limit=20 \
  --format='value(textPayload)'
```

### List All Agents in Agentspace

```bash
curl -s -X GET \
  -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  -H "X-Goog-User-Project: vtxdemos" \
  "https://discoveryengine.googleapis.com/v1alpha/projects/REDACTED_PROJECT_NUMBER/locations/global/collections/default_collection/engines/agentspace-testing_1748446185255/assistants/default_assistant/agents" \
  | jq '.agents[] | {name: .name, display: .displayName, engine: .adkAgentDefinition.provisionedReasoningEngine.reasoningEngine}'
```

---

## Full Reset

If you need to start over:

```bash
# 1. Delete agent from Agentspace
curl -X DELETE \
  -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  -H "X-Goog-User-Project: vtxdemos" \
  "https://discoveryengine.googleapis.com/v1alpha/projects/REDACTED_PROJECT_NUMBER/locations/global/collections/default_collection/engines/agentspace-testing_1748446185255/assistants/default_assistant/agents/410068398271859395"

# 2. Delete Agent Engine
gcloud ai reasoning-engines delete 7011410278222921728 \
  --project=sharepoint-wif-agent \
  --region=us-central1

# 3. Remove IAM binding
gcloud projects remove-iam-policy-binding sharepoint-wif-agent \
  --member="serviceAccount:service-REDACTED_PROJECT_NUMBER@gcp-sa-discoveryengine.iam.gserviceaccount.com" \
  --role="roles/aiplatform.user"

# 4. Redeploy
uv run python deploy.py new
# Update REASONING_ENGINE_RES in .env
uv run python register_agent.py
```
