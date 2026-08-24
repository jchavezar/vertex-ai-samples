---
name: replicating-managed-agent-sandbox-chat
description: Orchestrates setup, testing, and teardown of the Vertex AI Managed Agent Sandbox & A2A Wire-Tap platform. Use when deploying, testing, or troubleshooting the managed agent sandbox solution.
---

# Replicating Managed Agent Sandbox Chat & A2A Wire-Tap

This skill guides Antigravity agents in provisioning, verifying, running, and debugging the **Vertex AI Managed Agents Sandbox Chat & A2A Wire-Tap Console**.

## Architecture & Components
- **Agent Model**: `antigravity-preview-05-2026` hosted on Google Cloud GAOS.
- **MicroVM Sandboxes**: Isolated, dedicated Linux execution environments (`/workspace`).
- **A2A Protocol**: Inter-agent delegation, adversarial model risk interrogation (SR 11-7), and cryptographic consensus.
- **Zero-Parsing Console**: React 19 + FastAPI SSE streaming bridge.

## Quick Reproduction Steps

### 1. Verification & Setup
```bash
uv run agy-recipes/managed-agent-sandbox-chat/scripts/setup.py
```

### 2. Interaction Smoke Test
```bash
uv run agy-recipes/managed-agent-sandbox-chat/scripts/test_recipe.py
```

### 3. Launch UI Server & Frontend
```bash
cd antigravity-sandbox-chat
./start.sh
```

### 4. Teardown
```bash
uv run agy-recipes/managed-agent-sandbox-chat/scripts/teardown.py
```
