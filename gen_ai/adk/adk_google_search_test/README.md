# Google ADK Grounding Metadata Lab

This project provides a series of experiments to understand and solve the challenge of retrieving **Grounding Metadata** (search chunks and links) in complex multi-agent architectures using the **Google Agent Development Kit (ADK)**.

## 🚀 Overview

When building sophisticated AI agents, you often nest them using `AgentTool` or delegation. A common issue is the loss of "Grounding Metadata" when an agent is called as a tool. This lab reproduces that failure and provides two distinct architectural solutions.

## 📁 Project Structure

- **[01_basic_google_search.py](./01_basic_google_search.py)**: Baseline test. Shows how a single agent natively returns grounding links.
- **[02_failure_agent_as_tool.py](./02_failure_agent_as_tool.py)**: **Reproduction of the issue.** Shows how wrapping an agent in an `AgentTool` discards metadata.
- **[03_fix_custom_tool_class.py](./03_fix_custom_tool_class.py)**: **Solution A.** Uses a custom `GroundingAwareAgentTool` to manually propagate metadata via state.
- **[04_fix_agent_delegation.py](./04_fix_agent_delegation.py)**: **Solution B (Recommended).** Switches to native Agent Delegation, allowing metadata to flow freely through the event stream.
- **[EXPLANATION.md](./EXPLANATION.md)**: Detailed technical breakdown of the "Metadata Barrier" and why different architectures behave differently.

## 🛠 Setup

1. **Prerequisites**: 
   - Python 3.12+
   - `uv` (recommended for dependency management)
   - Google Cloud Project with Vertex AI enabled.

2. **Environment Variables**:
   Create a `.env` file in this directory:
   ```env
   GOOGLE_CLOUD_PROJECT=your-project-id
   GOOGLE_CLOUD_LOCATION=us-central1
   GOOGLE_GENAI_USE_VERTEXAI=true
   ```

3. **Install Dependencies**:
   ```bash
   uv sync
   ```

## 🏃 Running the Lab

To see the recommended "Clean" fix in action:
```bash
uv run python 04_fix_agent_delegation.py
```

## 📖 Learn More
Read the [EXPLANATION.md](./EXPLANATION.md) for a deep dive into ADK internal event handling and how to choose the right architecture for your needs.
