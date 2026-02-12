# Antigravity: ADK Agent Manual

**Status:** Draft / Verified  
**Last Updated:** February 11, 2026  
**Target System:** Antigravity / Agentspace (Gemini Enterprise)

---

## 1. Introduction

This manual provides a comprehensive guide to developing, registering, and using AI agents for the **Antigravity** project using Google's **Agent Development Kit (ADK)** and the **Agentspace** platform (integrated into Gemini Enterprise).

It consolidates instructions from internal documentation and recent external validation of libraries and APIs.

## 2. Prerequisites

Before you begin, ensure you have the following:

*   **Google Cloud Project (GCP):** An active GCP project.
*   **APIs Enabled:**
    *   `discoveryengine.googleapis.com` (Discovery Engine API)
    *   `aiplatform.googleapis.com` (Vertex AI API)
*   **IAM Roles:**
    *   `Discovery Engine Admin` (or `agents.manage` permission)
    *   `Vertex AI User`
    *   `Service Account User` (for the service account running the agent)
*   **Python Environment:** Python 3.9+ recommended.

## 3. Development Setup

The core library for developing agents is `google-adk`.

### Installation

```bash
pip install google-adk
```

*Note: Ensure you are using the latest version compatible with Gemini 2.5+ models.*

## 4. Developing an Agent

Agents are defined using the `LlmAgent` class. This allows you to define the agent's persona, tools, and behavior.

### Code Example (`agent.py`)

```python
from typing import Optional
from functools import partial
from google.adk.agents import LlmAgent
from google.adk.types import CallbackContext

def update_ui_status(
    callback_context: CallbackContext, status_msg: str
) -> Optional[dict]:
    """Updates the status of the execution on the Agentspace UI."""
    # This key is specific to Agentspace UI rendering
    callback_context.state["ui:status_update"] = status_msg
    return None

# Define the Agent
antigravity_agent = LlmAgent(
    name="AntigravityCore",
    model="gemini-2.0-flash-001",  # Use recent models like gemini-2.5 if available
    instruction="""
    You are the Antigravity Core Agent.
    Your goal is to assist users with system anomalies and data processing.
    Always be precise and cite your sources.
    """,
    description="Core assistant for the Antigravity system.",
    output_key="response",
    # Callbacks provide real-time feedback to the UI
    before_agent_callback=partial(
        update_ui_status, status_msg="Antigravity: Analyzing input..."
    ),
    after_agent_callback=partial(
        update_ui_status, status_msg="Antigravity: Response generated."
    ),
)
```

## 5. Deployment & Registration

Registration connects your code (Reasoning Engine) to the Agentspace UI.

**Important:** The API currently uses the `v1alpha` endpoint of `discoveryengine`.

### 5.1 Prepare Reasoning Engine
Ensure your agent code is deployed to a **Reasoning Engine** (e.g., via Vertex AI Reasoning Engine). You will need the `ADK_DEPLOYMENT_ID` from this step.

### 5.2 Register with Agentspace (API)

Use the following `curl` command to register the agent.

**Variables:**
*   `PROJECT_ID`: Your GCP Project ID.
*   `APP_ID`: Agentspace App ID (often default is `default_engine` or similar, check your URL).
*   `ADK_DEPLOYMENT_ID`: The ID from Step 5.1.
*   `REASONING_ENGINE_LOCATION`: e.g., `us-central1`.

```bash
curl -X POST 
-H "Authorization: Bearer $(gcloud auth print-access-token)" 
-H "Content-Type: application/json" 
-H "X-Goog-User-Project: YOUR_PROJECT_ID" 
"https://discoveryengine.googleapis.com/v1alpha/projects/YOUR_PROJECT_ID/locations/global/collections/default_collection/engines/YOUR_APP_ID/assistants/default_assistant/agents" 
-d '{
  "displayName": "Antigravity Core",
  "description": "Primary interface for system queries.",
  "icon": {
    "uri": "https://example.com/antigravity_icon.png"
  },
  "adk_agent_definition": {
    "tool_settings": {
      "tool_description": "You are an expert on the Antigravity system."
    },
    "provisioned_reasoning_engine": {
      "reasoning_engine": "projects/YOUR_PROJECT_ID/locations/us-central1/reasoningEngines/ADK_DEPLOYMENT_ID"
    }
  }
}'
```

### 5.3 Managing Agents

*   **List Agents:** GET request to the registration endpoint.
*   **Update Agent:** PATCH request to `https://discoveryengine.googleapis.com/v1alpha/AGENT_RESOURCE_NAME`.
*   **Delete Agent:** DELETE request to `https://discoveryengine.googleapis.com/v1alpha/AGENT_RESOURCE_NAME`.

## 6. Authorization (Optional)

If your agent needs to access user data (e.g., Drive, Gmail) on behalf of the user, you must configure OAuth 2.0.

1.  **Create OAuth Credentials:** In GCP Console (APIs & Services > Credentials), create an OAuth 2.0 Client ID (Web Application).
2.  **Register Authorization Resource:**

```bash
curl -X POST 
-H "Authorization: Bearer $(gcloud auth print-access-token)" 
-H "Content-Type: application/json" 
"https://discoveryengine.googleapis.com/v1alpha/projects/YOUR_PROJECT_ID/locations/global/authorizations?authorizationId=antigravity-auth" 
-d '{
  "name": "projects/YOUR_PROJECT_ID/locations/global/authorizations/antigravity-auth",
  "serverSideOauth2": {
    "clientId": "YOUR_OAUTH_CLIENT_ID",
    "clientSecret": "YOUR_OAUTH_CLIENT_SECRET",
    "authorizationUri": "https://accounts.google.com/o/oauth2/v2/auth",
    "tokenUri": "https://oauth2.googleapis.com/token"
  }
}'
```

3.  **Link to Agent:** Add the authorization resource name to the `authorizations` array in the `adk_agent_definition` when registering/updating the agent.

## 7. Intelligence & Validation Notes

*   **API Stability:** The `v1alpha` API is stable for Agentspace but subject to change. Always check the [Discovery Engine API release notes](https://cloud.google.com/discovery-engine/docs/release-notes) for breaking changes.
*   **Naming:** "Agentspace" is increasingly integrated into "Gemini Enterprise" and "Vertex AI Agents". Documentation may refer to these terms interchangeably.
*   **Community:** The `google-adk` python package is active on GitHub. Check `waytlion/google-adk-python` or official Google samples for advanced patterns like Multi-Agent orchestration.

## 8. Usage

Once registered, the agent will appear in the **Agentspace UI**. Users can select "Antigravity Core" and interact.

*   **Status Updates:** The `ui:status_update` state key is the standard way to push "Thinking..." or "Processing..." messages to the frontend.
*   **Access Tokens:** If authorized, access tokens are available in `tool_context.state[f"temp:{AUTH_ID}"]`.

## 9. Deploying to Vertex AI Agent Engine

This section details how to deploy your ADK agent to **Vertex AI Agent Engine** (also known as Reasoning Engine). This allows your agent to run as a scalable, managed service.

### 9.1 Prerequisites

Ensure your environment is set up with the necessary extras.

```bash
pip install "google-cloud-aiplatform[adk,agent_engines]"
```

### 9.2 Agent Definition (`agent.py`)

Your agent logic should be encapsulated in a Python file (e.g., `agent.py`). The entry point must be an instance of `google.adk.agents.Agent`, conventionally named `root_agent`.

```python
# agent.py
from google.adk.agents import Agent
from google.adk.tools import VertexAiSearchTool, AgentTool

# Example: Define tools or sub-agents
# vertex_search_tool = VertexAiSearchTool(data_store_id="...")

# Define the Root Agent
root_agent = Agent(
    name='antigravity_root_agent',
    model='gemini-2.5-flash', # Use the latest available model
    instruction="You are the Antigravity system orchestrator. Answer queries using your tools.",
    description="Orchestrates system queries and tool usage.",
    tools=[], # Add tools here
)
```

### 9.3 Deployment Script (`deploy.py`)

As of the recent SDK update, use the `vertexai.Client` to deploy agents to the Agent Engine. This is the recommended approach.

```python
# deploy.py
import os
import vertexai
from vertexai.agent_engines import AdkApp
from agent import root_agent  # Import your agent

# Configuration
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
STAGING_BUCKET = "gs://your-staging-bucket"
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
DISPLAY_NAME = "antigravity-core-agent"

# 1. Initialize the Client
client = vertexai.Client(
    project=PROJECT_ID,
    location=LOCATION,
)

# 2. Wrap the agent in an AdkApp
local_agent = AdkApp(
    agent=root_agent,
    enable_tracing=True
)

# 3. Deploy to Agent Engine
print(f"Deploying agent: {DISPLAY_NAME}...")
remote_agent = client.agent_engines.create(
    agent=local_agent,
    config={
        "display_name": DISPLAY_NAME,
        "requirements": [
            "google-cloud-aiplatform[adk,agent_engines]",
            "google-genai",
            "python-dotenv",
        ],
        # Important: Include your agent file so it's uploaded
        "extra_packages": ["agent.py"],
        "env_vars": {
            "ENABLE_TELEMETRY": "False" # Required to prevent telemetry crashes if SSL fails
        }
    }
)

print(f"Agent deployed! Resource Name: {remote_agent.resource_name}")
```

### 9.4 Managing Agents

#### Listing Agents (with Filters)
You can find existing agents using filters, which is useful for CI/CD pipelines to avoid duplicate deployments.

```python
# List agents with a specific display name
existing_agents = agent_engines.list(filter=f'display_name="{DISPLAY_NAME}"')

for agent in existing_agents:
    print(f"Found agent: {agent.resource_name} ({agent.display_name})")
```

#### Updating an Agent
If an agent already exists, you can update it instead of creating a new one.

```python
if existing_agents:
    remote_agent = existing_agents[0] # Get the first match
    print(f"Updating agent: {remote_agent.resource_name}")
    
    remote_agent.update(
        agent_engine=local_agent,
        requirements=[
            "google-cloud-aiplatform[adk,agent_engines]"
        ],
        extra_packages=["agent.py"]
    )
```

#### Deleting an Agent
To clean up resources:

```python
# Delete by resource name
agent_engines.delete(
    resource_name="projects/YOUR_PROJECT/locations/us-central1/reasoningEngines/1234567890",
    force=True
)
```

### 9.5 Testing (Remote)

Once deployed, you can interact with the remote agent similarly to the local one.

```python
# Get the remote agent instance
remote_agent = agent_engines.get("projects/YOUR_PROJECT/locations/us-central1/reasoningEngines/YOUR_AGENT_ID")

# Query the agent
response = remote_agent.query(
    message="Report on the latest system anomalies.",
    session_id="test-session-01"
)
print(response)

# Or stream the response
# for event in remote_agent.stream_query(message="..."):
#     print(event)
```

---
*Generated by Gemini CLI for Project Antigravity.*
