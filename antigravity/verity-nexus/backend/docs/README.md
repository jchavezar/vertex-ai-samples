# Verity Nexus Engine

The Verity Nexus Engine is a high-performance forensic and regulatory audit platform powered by Google ADK and multi-agent orchestration.

## Architecture

- **Audit Agent**: Specialized in forensic analysis of financial transactions. Uses `gemini-2.5-flash` for high-throughput scanning.
- **Tax Agent**: Expert in regulatory compliance and tax law.
- **Orchestrator**: The central bridge that coordinates between agents to provide a unified synthesis of findings.

## Tech Stack

- **Backend**: Python 3.13, Google ADK, FastAPI.
- **Frontend**: Next.js 15 (App Router), TypeScript, Vanilla CSS.
- **Agent Framework**: Google ADK (Agent Development Kit).
- **Deployment**: Docker Compose.

## Getting Started

1. Set up your Google Cloud credentials in `credentials.json`.
2. Run `docker-compose up`.
3. Access the UI at `http://localhost:3000`.
