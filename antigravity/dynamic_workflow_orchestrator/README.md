# Dynamic Workflow Orchestrator

<div align="center">
  <h3>Powered by Google ADK & FastAPI</h3>
</div>

## Overview

The Dynamic Workflow Orchestrator is a full-stack application within the Antigravity suite demonstrating real-time event streaming across sequential agentic steps using the Google Agent Development Kit (ADK).

It showcases how to orchestrate multiple agents (e.g., a `SummaryAgent` and a `BulletPointAgent`) to process text and yield responses immediately to the client via Server-Sent Events (SSE).

### Human-in-the-Loop Workflow
This project includes a fully interactive Human-in-the-Loop step. The ADK workflow stops exactly between the first sequence and the second, emits a `WAITING_FOR_USER_INPUT` status state, and awaits explicit action bounds mapping via standard FastAPI forms.

## Architecture

- **Backend**: FastAPI + Python 3.12 + Google ADK 
- **Frontend**: React 19 + TypeScript + Vite + TailwindCSS
- **Communication**: Server-Sent Events (SSE) stream on `/api/workflow`

## Zero-Leak Protocol

This project strictly adheres to the Zero-Leak security policy. All secrets (`GEMINI_API_KEY`) must reside in `.env` files which are globally git-ignored. The backend programmatically resolves the `.env` file via `python-dotenv`.

## Agent Engine & Gemini Enterprise Deployment

This agent is configured to be deployed to **Vertex AI Agent Engine** and exposed via **Gemini Enterprise**.

### 1. Deploying to Agent Engine
To deploy the backend orchestration logic to Google Cloud as a Reasoning Engine:
```bash
cd backend
uv run python deploy.py
```
This script will package the agent, upload it to the designated staging bucket, and provision a Vertex AI Reasoning Engine. It will output the unique Engine ID upon completion.

### 2. Registering with Gemini Enterprise
To expose your deployed Agent Engine app via the Gemini Enterprise interface:
1. Open the **Google Cloud Console**.
2. Navigate to **Vertex AI Search and Conversation** (or **Discovery Engine**).
3. Select your designated **Gemini Enterprise App**.
4. Navigate to the **Agents** tab and click **Add agent**.
5. Select **Custom agent via Agent Engine**.
6. Follow the UI prompts to configure the agent's display name and link it to the Reasoning Engine ID:
   - `projects/*/locations/us-central1/reasoningEngines/8966261138304008192` (dynamic_workflow_orchestrator)
   - `projects/*/locations/us-central1/reasoningEngines/7262493104274407424` (dynamic_workflow_orchestrator_v4)

## Ports

- **Frontend**: `5176`
- **Backend**: `8007`

## Quick Start
### 1. Start the Backend
```bash
cd backend
uv run uvicorn main:app --host 0.0.0.0 --port 8007 --reload
```

### 2. Start the Frontend
```bash
cd frontend
npm run dev
```

Navigate to `http://localhost:5176` to view the UI.

## Demo

**Real-time Streaming:**
![Dynamic Workflow Demo](/usr/local/google/home/jesusarguelles/.gemini/jetski/brain/4124182f-8406-4892-ab46-f8b02dd66414/streaming_result_1773172683582.png)

**Interactive Workflow (Awaiting User Review):**
![Awaiting Review](/usr/local/google/home/jesusarguelles/.gemini/jetski/brain/4124182f-8406-4892-ab46-f8b02dd66414/hitl_waiting_approval_1773196852013.png)

**Final Result (Workflow Completed):**
![Final Output](/usr/local/google/home/jesusarguelles/.gemini/jetski/brain/4124182f-8406-4892-ab46-f8b02dd66414/hitl_finished_final_1773197690663.png)
