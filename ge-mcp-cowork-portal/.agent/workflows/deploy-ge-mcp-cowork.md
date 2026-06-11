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
Run the following commands to copy the application template files, register the Antigravity workflows/skills in the target workspace, and write the environment configuration:

// turbo
```bash
# 1. Create target clone directory
mkdir -p ./ge-mcp-cowork-portal

# 2. Copy application files from vertex-ai-samples recipe folder
cp -r /Users/jesusarguelles/IdeaProjects/vertex-ai-samples/agy-recipes/ge-mcp-cowork/app/* ./ge-mcp-cowork-portal/

# 3. Copy the .agent skills and workflows into both the portal clone and the active workspace root
mkdir -p ./ge-mcp-cowork-portal/.agent
cp -r /Users/jesusarguelles/IdeaProjects/vertex-ai-samples/agy-recipes/ge-mcp-cowork/.agent/* ./ge-mcp-cowork-portal/.agent/
mkdir -p ./.agent
cp -r /Users/jesusarguelles/IdeaProjects/vertex-ai-samples/agy-recipes/ge-mcp-cowork/.agent/* ./.agent/

# 4. Load environment configurations by copying the original project's .env file, or fallback to generating one
if [ -f /Users/jesusarguelles/IdeaProjects/vertex-ai-samples/semiautonomous-agents/ge-mcp-cowork/.env ]; then
  cp /Users/jesusarguelles/IdeaProjects/vertex-ai-samples/semiautonomous-agents/ge-mcp-cowork/.env ./ge-mcp-cowork-portal/.env
else
  cat <<EOF > ./ge-mcp-cowork-portal/.env
GOOGLE_CLOUD_PROJECT=<PROJECT_ID>
GOOGLE_CLOUD_LOCATION=us-central1
GEMINI_MODEL=gemini-2.5-flash
USE_REASONING_ENGINE=False
REASONING_ENGINE_ID=<ENGINE_ID>
JIRA_DEFAULT_SITE=<JIRA_URL>
SHAREPOINT_DEFAULT_SITE=<SHAREPOINT_URL>
EOF
fi

# 5. Initialize env file in backend folder
cp ./ge-mcp-cowork-portal/backend/.env.example ./ge-mcp-cowork-portal/backend/.env
```

---

## 3. Install and Run
Install Node modules and start the local servers:

// turbo
```bash
# 1. Install react frontend packages
cd ./ge-mcp-cowork-portal/frontend
npm install
cd ../..

# 2. Launch servers in the background
cd ./ge-mcp-cowork-portal
./start.sh
```

