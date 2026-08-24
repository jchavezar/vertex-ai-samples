# Recipe: Vertex AI Managed Agent Sandbox Chat & A2A Wire-Tap

This recipe provisions, verifies, and runs the **Vertex AI Managed Agents Autonomous Sandbox & A2A Forensic Wire-Tap** solution.

## Architecture
- **Agent Model**: `antigravity-preview-05-2026` hosted on Google Cloud GAOS.
- **MicroVM Sandboxes**: Isolated, dedicated Linux execution environments (`/workspace`).
- **A2A Protocol**: Inter-agent delegation, adversarial model risk interrogation (SR 11-7), and cryptographic consensus.
- **Zero-Parsing Console**: React 19 + FastAPI SSE streaming bridge.

## Required Google Cloud APIs
- `aiplatform.googleapis.com` (Vertex AI API)
- `serviceusage.googleapis.com` (Service Usage API)

## IAM Roles Required
- `roles/aiplatform.user`
- `roles/serviceusage.serviceUsageConsumer`

## Scripts
- `scripts/setup.py`: Checks ADC, verifies project access (`vtxdemos`), and ensures required APIs are enabled.
- `scripts/test_recipe.py`: Runs an isolated multi-turn interaction test against the Vertex AI Managed Agent runtime.
- `scripts/teardown.py`: Idempotent cleanup script.

## Replication Commands
```bash
# Setup
uv run agy-recipes/managed-agent-sandbox-chat/scripts/setup.py

# Test Interaction
uv run agy-recipes/managed-agent-sandbox-chat/scripts/test_recipe.py

# Launch Full UI
cd antigravity-sandbox-chat && ./start.sh

# Teardown
uv run agy-recipes/managed-agent-sandbox-chat/scripts/teardown.py
```
