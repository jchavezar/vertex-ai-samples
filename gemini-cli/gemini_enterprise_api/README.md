# Gemini Enterprise Agent Invocation

This folder contains tools and scripts for interacting with Gemini Enterprise (Vertex AI Agent Builder) using the `v1alpha` and `v1beta` APIs.

## Contents

- `invoke_agent_eng_spa.py`: A Python script that invokes a specific Gemini Enterprise agent (e.g., "Eng-Spa") using the `streamAssist` API. It demonstrates how to send a query and process the streaming response, printing both the original request and the final answer.

## Prerequisites

- **Google Cloud Project**: A project with the Discovery Engine API enabled.
- **Project Number**: `254356041555`
- **Engine ID**: `agentspace-testing_1748446185255`
- **Authentication**: Ensure you have authenticated via Application Default Credentials:
  ```bash
  gcloud auth application-default login
  ```
- **Dependencies**:
  ```bash
  pip install google-auth requests
  ```

## Usage

Run the script directly using Python:

```bash
python invoke_agent_eng_spa.py
```

The script will output the request details, the query being sent, and the streaming answer received from the agent.
