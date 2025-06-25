# ADK Agent with File Upload Capability

This project demonstrates the end-to-end process of creating a simple AI agent using the Google Agent Development Kit (ADK), deploying it as a scalable Reasoning Engine on Vertex AI, and registering it with AgentSpace for discovery and use.

The core functionality of this agent is to receive and process files uploaded by a user.

## 🚀 Project Workflow

The process follows three main steps, each corresponding to a key file in this directory:

1.  **Define the Agent (`agent.py`)**: Create the agent's logic, including its instructions and tools.
2.  **Deploy the Agent (`agent_engine_deploy.py`)**: Package the agent and deploy it to Google Cloud as a managed Reasoning Engine.
3.  **Register the Agent (`register_to_agentspace.sh`)**: Make the deployed agent discoverable within a broader ecosystem like Vertex AI Agent Builder (AgentSpace).

---

## 📂 File Breakdown

Here is a detailed explanation of each file and its role in the project.

### 1. `agent.py`

This is the heart of the project where the AI agent's "brain" is defined.

```python
import logging
from google.adk.agents import LlmAgent
from google.adk.tools import load_artifacts

root_agent = LlmAgent(
    name="root_agent",
    model="gemini-2.5-flash",
    instruction="Answer any question, ALWAYS use your artifacts from load_artifacts tool",
    tools=[load_artifacts],
)
```

*   **`LlmAgent`**: This is the basic building block from the ADK for creating an agent powered by a Large Language Model.
*   **`model="gemini-2.5-flash"`**: It specifies that the agent will use Google's fast and efficient Gemini 2.5 Flash model for its reasoning.
*   **`instruction`**: This is the system prompt that dictates the agent's core behavior. Here, it's instructed to always use its `load_artifacts` tool to access file content when answering questions.
*   **`tools=[load_artifacts]`**: This is the most critical part for file handling. `load_artifacts` is a built-in ADK tool that gives the agent the ability to "see" and process the content of files that are uploaded during a conversation.

### 2. `agent_engine_deploy.py`

This script takes the locally defined `root_agent` and deploys it to Google Cloud, turning it into a scalable, serverless Reasoning Engine.

```python
#%%
import vertexai
from agent import root_agent
from vertexai import agent_engines
from vertexai.preview import reasoning_engines

vertexai.init(project="vtxdemos", staging_bucket="gs://vtxdemos-staging")

app = reasoning_engines.AdkApp(
    agent=root_agent,
    enable_tracing=True,
)

#%%
# Deploy Agent Engine
remote_app = agent_engines.create(
    agent_engine=app,
    requirements=[
        "google-cloud-aiplatform[adk,agent_engines]",
    ],
    extra_packages=["agent.py"]
)
```

*   **`reasoning_engines.AdkApp`**: This wraps our `root_agent` into an application package that Vertex AI can understand.
*   **`agent_engines.create(...)`**: This is the function that starts the deployment. It uploads the agent's code (`agent.py`), installs its dependencies (`requirements`), and provisions a managed endpoint for it on Vertex AI.
*   When this script is run, it will output a resource name for the newly created Reasoning Engine, which is needed for the next step.

### 3. `register_to_agentspace.sh`

After the agent is deployed, it exists as an endpoint but isn't necessarily discoverable by other tools or UIs. This shell script registers the deployed agent with a service like AgentSpace, making it available as a tool for other assistants or applications.

```bash
%%bash
export PROJECT_ID="vtxdemos"
export REASONING_ENGINE_RES="projects/..." # <-- From deployment step
export AGENT_DISPLAY_NAME_RES="Uploader load_tool"
...

curl -X POST -H "Authorization: Bearer $(gcloud auth print-access-token)" ...
```

*   This script uses `curl` to send a `POST` request to the `discoveryengine.googleapis.com` API.
*   It passes the `REASONING_ENGINE_RES` (the unique ID of the deployed agent) in the request body.
*   It also defines metadata like a `displayName` and `description` so the agent can be easily identified in a UI or list of available tools.

---

### Note on Other Files

The files located in the `/model_armor_gsearch_vais/` directory belong to a separate, more complex example. That project demonstrates how to build a chat UI with **Flet**, create a multi-agent system with security guardrails (**Model Armor**), and integrate **Google Search**. While not part of this file-upload workflow, it serves as an excellent reference for building a complete user-facing application with the ADK.