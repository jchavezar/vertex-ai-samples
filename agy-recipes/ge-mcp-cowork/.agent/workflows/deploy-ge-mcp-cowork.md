---
description: Replicate, configure, and spin up the Gemini Enterprise MCP Co-work Portal web application locally
---
# Replicating and Deploying the GE MCP Co-work Portal

This workflow outlines the automated steps to replicate the Co-work Portal application code, configure local environment variables interactively, install node modules, and start the local servers.

To start this deployment, follow the phases below.

---

## 1. Interactive Parameter Configuration

> [!IMPORTANT]
> **Agent Instruction**: Do NOT propose or write the `.env` file directly. You must first stop and explicitly prompt the user in the chat for each of the variables below, presenting the detected default values (run `gcloud config get-value project` to find the active project). Only after the user confirms or provides custom overrides in the chat, execute the replication script passing those parameters.

The agent will ask you for:
*   **Target Destination**: The local folder where the app should be copied (default: `./ge-mcp-cowork-portal`).
*   **GOOGLE_CLOUD_PROJECT**: Your target Google Cloud Project ID.
*   **GOOGLE_CLOUD_LOCATION**: The target region (default: `us-central1`).
*   **REASONING_ENGINE_ID**: The target Vertex AI Reasoning Engine ID (default: `jira-testing_1778158449701`).
*   **JIRA_DEFAULT_SITE**: The default Jira domain site (default: `sockcop.atlassian.net`).
*   **SHAREPOINT_DEFAULT_SITE**: The default SharePoint domain URL.

---

## 2. Execute Setup and Replication
Once the variables are aligned, run the replication script using `uv` with non-interactive CLI parameters to clone the portal and configure it:

// turbo
```bash
uv run agy-recipes/ge-mcp-cowork/scripts/setup.py \
  --destination "<TARGET_DESTINATION>" \
  --project-id "<PROJECT_ID>" \
  --engine-id "<ENGINE_ID>" \
  --jira-url "<JIRA_URL>" \
  --sharepoint-url "<SHAREPOINT_URL>" \
  --non-interactive
```

---

## 3. Run and Monitor
To run the replicated portal:
1. Navigate to the destination directory:
   ```bash
   cd <TARGET_DESTINATION>
   ```
2. Launch the server script:
   ```bash
   ./start.sh
   ```
3. Open **`http://localhost:5173/`** in your browser.
