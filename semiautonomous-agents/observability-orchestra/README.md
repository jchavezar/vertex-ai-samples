# Observability Orchestra

Multi-model Agent Engine for testing observability features with Cloud Trace and Cloud Logging.

## Architecture

| Agent | Model | Region | Purpose |
|-------|-------|--------|---------|
| Orchestrator | gemini-2.5-flash | us-central1 | Routes requests to sub-agents |
| Claude Analyst | claude-sonnet-4-6 | us-east5 | Deep analysis, reasoning, code review |
| Flash-Lite Creator | gemini-3.1-flash-lite-preview | global | Creative content, fast responses |

## Region Hacks

Agent Engine only supports `us-central1`, but:
- **Claude** models are only available in `us-east5`, `europe-west1`, or `global`
- **Gemini 3.1 Flash-Lite Preview** is only available on `global` endpoint

This project demonstrates how to use custom model wrappers (`ClaudeUsEast5`, `GeminiGlobal`) to override the region per-model while keeping Agent Engine in `us-central1`.

## Setup

```bash
cd agent
uv sync
cp .env.example .env  # Edit with your project settings
```

## Local Testing

```bash
uv run python test_local.py
```

## Deploy to Agent Engine

```bash
uv run python deploy.py
```

## Test Remote Agent

```bash
uv run python test_remote.py
```

## Observability

After deployment, view traces and logs:
- Cloud Trace: https://console.cloud.google.com/traces/list
- Cloud Logging: https://console.cloud.google.com/logs/query
