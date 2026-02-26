---
description: Replicate the Verity Nexus Forensic Swarm Architecture
---

# Replicate Verity Nexus: Forensic Swarm Architecture

This workflow guides you through replicating the "Verity Nexus" architecture, a multi-agent forensic audit swarm built using Google ADK, Gemini 2.5/3, and Next.js.

## 1. Engine Setup (Backend)

1. **Initialize Project**:
   ```bash
   mkdir verity-nexus-engine && cd verity-nexus-engine
   uv init
   uv add google-adk google-genai fastapi uvicorn python-dotenv pydantic
   ```

2. **Configure Environment (.env)**:
   ```env
   GOOGLE_API_KEY=your_key
   GOOGLE_CLOUD_PROJECT=your_project
   GOOGLE_GENAI_USE_VERTEXAI=True
   GOOGLE_CLOUD_LOCATION=us-central1
   PORT=8005
   ```

3. **Define Agent Hierarchy**:
   - **Orchestrator**: Use `gemini-3-pro-preview`. Instructions MUST include delegation logic to sub-agents.
   - **Audit Agent**: Use `gemini-2.5-flash`. Attach the `TransactionScorer` tool.
   - **Tax Agent**: (Optional) Secondary agent for specialized reviews.

4. **Implement Data Tools**:
   - Create a `TransactionScorer` function that reads `ledger.csv` and applies logic from `materiality_policy.yaml`.
   - Wrap in `google.adk.tools.FunctionTool`.

5. **Build the Server (server.py)**:
   - Use `google.adk.Runner` with `auto_create_session=True`.
   - **CRITICAL**: Use `InMemorySessionService` with *keyword arguments* for `get_session` and `create_session`.
   - Implement a stream generator that yields `AIStreamProtocol` messages.

## 2. Frontend Setup (Next.js)

1. **Initialize UI**:
   ```bash
   npx create-next-app@latest verity-nexus-ui --ts --tailwind --eslint
   npm install ai @ai-sdk/react lucide-react framer-motion @xyflow/react
   ```

2. **Design System**: Use the "Modern Cave" or "UX Modern Cave" skill for a premium neofuturistic aesthetic.
3. **Agent Graph**: Implement a `LiveGraph` component using `React Flow` (xyflow) that listens for `agent_transition` packets from the stream data.
4. **Reasoning Stream**: Add a side panel that displays the `content` of `reasoning_stream` data events (tool calls and agent thoughts).

## 3. The "Pulse" Protocol (Integration)

1. **Streaming Transitions**: Ensure the backend yields `agent_transition` events whenever an agent handoff occurs.
   ```python
   # in server.py
   if event.author != current_agent:
       yield AIStreamProtocol.data({"type": "agent_transition", "agent": event.author})
   ```
2. **Standardized Tool Output**: Ensure tool results are rendered as structured "Audit Cards" on the frontend using the `workflow_complete` event.

// turbo
## 4. Launch
1. Start Engine: `uv run python server.py`
2. Start UI: `npm run dev -- -p 5174`
