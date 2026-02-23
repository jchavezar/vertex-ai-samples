# Guide to Registering and Managing Agent Engines in Gemini Enterprise (Antigravity/Agentspace)

This guide outlines the steps to create, register, update, and deregister an Agent Engine using the Agent Development Kit (ADK) and the Agentspace API.

## Prerequisites

Ensure you have the following:
-   **Google Cloud Project ID** (e.g., `vtxdemos`)
-   **Python Environment** with `vertexai`, `google-cloud-aiplatform`, and `google-cloud-discoveryengine` installed.
-   **OAuth Client ID and Secret** (Web Application type) from Google Cloud Console > APIs & Services > Credentials.
-   **Antigravity/ADK** setup (if using the internal IDE extension).

---

## 1. Create and Deploy an ADK Agent

First, define your agent logic using the ADK and deploy it to Vertex AI Agent Engine.

### Python Script (`deploy_agent.py`)

```python
import vertexai
from vertexai.preview import reasoning_engines
from google.adk.agents import Agent

# Initialize Vertex AI
PROJECT_ID = "your-project-id"
STAGING_BUCKET = "gs://your-staging-bucket"
vertexai.init(project=PROJECT_ID, staging_bucket=STAGING_BUCKET)

# Define your agent
root_agent = Agent(
    name="root_agent",
    model="gemini-2.5-flash",
    description="You are an AI Assistant with access to tools.",
    instruction="Answer user questions using available tools."
    # Add tools and workflows here
)

# Create the App
app = reasoning_engines.AdkApp(
    agent=root_agent,
    enable_tracing=True,
)

# Deploy to Agent Engine
remote_app = reasoning_engines.ReasoningEngine.create(
    reasoning_engine=app,
    requirements=[
        "google-cloud-aiplatform[adk,reasoning_engines]",
        "google-cloud-discoveryengine"
    ],
    display_name="My Agent Engine",
)

print(f"Agent Engine Deployed: {remote_app.resource_name}")
# Save this resource name for later steps!
# Format: projects/{project}/locations/{location}/reasoningEngines/{id}
```

---

## 2. Create Authorization ID for Agentspace

To allow Agentspace to invoke your agent, you need to register an Authorization ID.

### Step 2.1: Generate OAuth Token (One-time setup)
You need an OAuth token with appropriate scopes (`drive.metadata.readonly`, `calendar.readonly`, etc., depending on your agent's needs).

### Step 2.2: Register Auth ID via API

```bash
export PROJECT_NUMBER="your-project-number"
export AUTH_ID="my-agent-auth"
export OAUTH_CLIENT_ID="your-client-id"
export OAUTH_CLIENT_SECRET="your-client-secret"
export OAUTH_TOKEN_URI="https://oauth2.googleapis.com/token"

# Retrieve a valid access token for the API call
ACCESS_TOKEN=$(gcloud auth print-access-token)

curl -X POST 
  -H "Authorization: Bearer $ACCESS_TOKEN" 
  -H "Content-Type: application/json" 
  -H "X-Goog-User-Project: $PROJECT_NUMBER" 
  "https://discoveryengine.googleapis.com/v1alpha/projects/$PROJECT_NUMBER/locations/global/authorizations?authorizationId=$AUTH_ID" 
  -d '{
  "name": "projects/'"$PROJECT_NUMBER"'/locations/global/authorizations/'"$AUTH_ID"'",
  "serverSideOauth2": {
    "clientId": "'"$OAUTH_CLIENT_ID"'",
    "clientSecret": "'"$OAUTH_CLIENT_SECRET"'",
    "authorizationUri": "https://accounts.google.com/o/oauth2/auth",
    "tokenUri": "'"$OAUTH_TOKEN_URI"'"
  }
}'
```

---

## 3. Register Agent in Agentspace

Once deployed and authorized, register the Agent Engine as a discoverable agent in Agentspace.

```bash
export PROJECT_ID="your-project-id"
export PROJECT_NUMBER="your-project-number"
export REASONING_ENGINE_RES="projects/..." # Resource name from Step 1
export AUTH_ID="my-agent-auth" # From Step 2
export AGENT_DISPLAY_NAME="My Agent Name"
export AGENT_DESCRIPTION="Description of what the agent does."
# The Agent Engine ID (last part of the resource name from Step 1)
export AS_APP="reasoning-engine-id" 

ACCESS_TOKEN=$(gcloud auth print-access-token)

curl -X POST -H "Authorization: Bearer $ACCESS_TOKEN" 
  -H "Content-Type: application/json" 
  -H "X-Goog-User-Project: $PROJECT_ID" 
  "https://discoveryengine.googleapis.com/v1alpha/projects/$PROJECT_NUMBER/locations/global/collections/default_collection/engines/$AS_APP/assistants/default_assistant/agents" 
  -d '{
  "displayName": "'"$AGENT_DISPLAY_NAME"'",
  "description": "'"$AGENT_DESCRIPTION"'",
  "icon": {
      "uri": "https://www.gstatic.com/images/branding/product/2x/googleg_48dp.png" 
  },
  "adk_agent_definition": {
    "tool_settings": {
      "tool_description": "Use this tool to answer user questions."
    },
    "provisioned_reasoning_engine": {
      "reasoning_engine": "'"$REASONING_ENGINE_RES"'"
    },
    "authorizations": [
      "projects/'"$PROJECT_NUMBER"'/locations/global/authorizations/'"$AUTH_ID"'"
    ]
  }
}'
```

---

## 4. Update an Existing Agent

To update the logic of an existing agent without changing its registration ID.

```python
import vertexai
from vertexai.preview import reasoning_engines

# Initialize
vertexai.init(project="your-project-id", staging_bucket="gs://your-bucket")

# Re-create the App with new logic/agent definition
app = reasoning_engines.AdkApp(agent=updated_agent, enable_tracing=True)

# Get reference to existing deployment
remote_app = reasoning_engines.ReasoningEngine("projects/.../reasoningEngines/existing-id")

# Update
remote_app.update(
    reasoning_engine=app,
    requirements=["google-cloud-aiplatform[adk,reasoning_engines]"],
)
print("Agent updated successfully.")
```

---

## 5. Deregister (Delete) an Agent

To remove an agent from Agentspace and/or delete the Agent Engine.

### 5.1 Delete from Agentspace (Deregister)

This removes the agent from the Agentspace UI/Listing.

```python
import requests

ACCESS_TOKEN = "your-access-token" # $(gcloud auth print-access-token)
PROJECT_ID = "your-project-id"
# The full resource name of the registered agent in Discovery Engine (NOT the Reasoning Engine ID)
# Format: projects/{number}/locations/global/collections/default_collection/engines/{engine_id}/assistants/default_assistant/agents/{agent_id}
AGENT_RESOURCE_NAME = "projects/..." 

url = f"https://discoveryengine.googleapis.com/v1alpha/{AGENT_RESOURCE_NAME}"
headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}", 
    "Content-Type": "application/json", 
    "X-Goog-User-Project": PROJECT_ID
}

response = requests.delete(url, headers=headers)

if response.status_code == 200:
    print("Agent successfully deregistered from Agentspace.")
else:
    print(f"Error deregistering agent: {response.status_code} - {response.text}")
```

### 5.2 Delete Agent Engine (Optional)

If you also want to delete the underlying compute resource in Vertex AI:

```python
from vertexai.preview import reasoning_engines

remote_app = reasoning_engines.ReasoningEngine("projects/.../reasoningEngines/id")
remote_app.delete()
print("Agent Engine deleted.")
```
