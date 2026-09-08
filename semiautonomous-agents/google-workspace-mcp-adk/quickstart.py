"""
Google ADK + Google Workspace Remote MCP: Minimal Standalone Quickstart
Demonstrates the most compact way to connect Gemini 3.7 Flash to Google Workspace via ADK McpToolset.

Usage:
    export GOOGLE_WORKSPACE_TOKEN="ya29.a0A..."   # OAuth token with Workspace scopes
    export GOOGLE_CLOUD_PROJECT="vtxdemos"
    python3 quickstart.py
"""

import asyncio
import os
from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams
from google.genai import types

os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "true")
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "global")


async def main():
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT", "vtxdemos")
    os.environ["GOOGLE_CLOUD_PROJECT"] = project_id
    token = os.environ.get("GOOGLE_WORKSPACE_TOKEN", "")

    if not token:
        print("⚠️  Warning: Set GOOGLE_WORKSPACE_TOKEN with your Workspace OAuth token to execute tools.")

    # 1. Connect ADK to Google Workspace Remote MCP (Gmail) in just 1 declaration:
    toolset = McpToolset(
        connection_params=StreamableHTTPConnectionParams(
            url="https://gmailmcp.googleapis.com/mcp/v1",
            headers={"Authorization": f"Bearer {token}", "x-goog-user-project": project_id},
        )
    )

    # 2. Declare the Agent with gemini-3.7-flash
    agent = Agent(
        name="gmail_assistant",
        model="gemini-3.7-flash",
        instruction="You are an enterprise AI assistant with direct access to Gmail MCP tools.",
        tools=[toolset],
    )

    # 3. Execute query with ADK Runner
    runner = InMemoryRunner(agent=agent)
    session = await runner.session_service.create_session(app_name=runner.app_name, user_id="user")

    query = "What Gmail tools are available to help me manage drafts?"
    print(f"\n--- Query: '{query}' ---\n")

    async for event in runner.run_async(
        session_id=session.id,
        user_id="user",
        new_message=types.Content(parts=[types.Part.from_text(text=query)]),
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    print(part.text, end="", flush=True)
    print("\n")


if __name__ == "__main__":
    asyncio.run(main())
