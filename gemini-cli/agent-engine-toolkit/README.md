# Vertex AI Agent Engine Toolkit 🚀

This toolkit provides a streamlined way to define, deploy, and manage Google ADK agents on Vertex AI Agent Engine using the latest `google.genai` SDK.

## Features
- **Modern Deployment**: Uses `genai.Client().agent_engines.create()` for full lifecycle control.
- **ADK Integration**: Easily deploy `LlmAgent` and other ADK constructs.
- **Lifecycle Management**: Scripts for listing and managing your deployed engines.

## Structure
- `src/agent_definition.py`: Where your ADK `root_agent` is defined.
- `deploy.py`: The main script to push your agent to the cloud.
- `manage.py`: Utility script to list and interact with deployed engines.

## Quick Start
1. Initialize dependencies: `uv sync`
2. Deploy: `uv run deploy.py`
3. List: `uv run manage.py`
