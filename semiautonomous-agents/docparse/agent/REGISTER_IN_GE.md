# Registering the agent in your Gemini Enterprise app

Skip this entire file if you don't have (or don't want) a Gemini Enterprise app — the docparse agent runs fine standalone on Vertex AI Agent Engine.

## What you need before you start

A Gemini Enterprise **app** and **assistant** already created in your GE-hosting project. If you don't have one yet: GCP Console → **Vertex AI Search and Conversation** → **Apps** → **+ New App** → pick "Search" or "Chat" → finish the wizard.

## 1. Find the 3 values you'll add to `.env`

```bash
# A. The project where your GE app lives (often different from your docparse project)
echo "GE_PROJECT_ID = the project ID shown on your GE app's overview page"

# B. The numeric project number for the same project
gcloud projects describe <GE_PROJECT_ID> --format='value(projectNumber)'
#   → use the value shown for GE_PROJECT_NUMBER

# C. The app (engine) ID — find in the URL of your GE app, after /engines/
#   e.g. .../collections/default_collection/engines/my-app_1776970890534
#                                                  ^^^^^^^^^^^^^^^^^^^^^
#   → use the value shown for AS_APP
```

`AS_ASSISTANT` defaults to `default_assistant`. Only change it if your app has multiple assistants.

## 2. Add them to `.env`

```bash
GE_PROJECT_ID=their-ge-project
GE_PROJECT_NUMBER=123456789012
AS_APP=my-app_1776970890534
# AS_ASSISTANT=default_assistant   ← only set if you renamed it
```

## 3. Grant cross-project IAM (one-time)

The GE service agent lives in the GE project. It needs permission to invoke the Agent Engine running in the docparse project:

```bash
gcloud projects add-iam-policy-binding ${PROJECT} \
  --member="serviceAccount:service-${GE_PROJECT_NUMBER}@gcp-sa-discoveryengine.iam.gserviceaccount.com" \
  --role="roles/aiplatform.user" --condition=None
```

`${PROJECT}` is your **docparse** project, `${GE_PROJECT_NUMBER}` is the **GE-hosting** project's number.

## 4. Register

```bash
./deploy.sh register
```

This shells into `agent/register_agent.py` which adds the agent to the assistant via Discovery Engine API and shares it with `ALL_USERS`.

## 5. Verify

Open your GE app in the browser. Click **Chat** (or your assistant's name) → the **+ Tools** menu should show "docparse RAG agent" available. Toggle it on and ask a question that requires your PDFs.

## Common errors

| Symptom | Fix |
|---|---|
| `403 PERMISSION_DENIED` on register | Re-check step 3 — the cross-project IAM grant. |
| Agent registers but answers with "no information" | The RAG corpus is empty. Verify `gcloud storage ls gs://${PROJECT}-docparse-out/` has your `.txt` files first. |
| ADC resolves to wrong identity | Run `gcloud auth login your-admin-account@your-domain.com` then re-run `./deploy.sh register`. |
| `403` on the agent's tool call | The `AS_APP` engine ID is wrong — re-check the URL in step 1.C. |
