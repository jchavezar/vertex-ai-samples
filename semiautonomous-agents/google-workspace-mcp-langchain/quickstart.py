"""
LangChain + LangGraph + Google Workspace Remote MCP: Minimal Standalone Quickstart
Demonstrates how LangChain (ChatGoogleGenerativeAI) and LangGraph (create_react_agent)
directly connect to Google Workspace Remote MCP using LangChain StructuredTools.

Usage:
    export GOOGLE_WORKSPACE_TOKEN="ya29.a0A..."   # OAuth token with Workspace scopes
    export GOOGLE_CLOUD_PROJECT="vtxdemos"
    python3 quickstart.py
"""

import asyncio
import os
import certifi
import httpx
from langchain_core.messages import HumanMessage
from langchain_core.tools import StructuredTool
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent

os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "true")
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "global")


async def main():
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT", "vtxdemos")
    token = os.environ.get("GOOGLE_WORKSPACE_TOKEN", "")
    endpoint_url = "https://gmailmcp.googleapis.com/mcp/v1"
    headers = {"x-goog-user-project": project_id}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    if not token:
        print("⚠️  Warning: Set GOOGLE_WORKSPACE_TOKEN with your Workspace OAuth token to execute tools.")

    # 1. Discover tools from Google Workspace Remote MCP (Streamable HTTP)
    async with httpx.AsyncClient(headers=headers, timeout=10.0) as client:
        await client.post(
            endpoint_url,
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "langchain-quickstart", "version": "1.0"}},
            },
        )
        res = await client.post(endpoint_url, json={"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
        mcp_tools = res.json().get("result", {}).get("tools", [])

    print(f"✅ Discovered {len(mcp_tools)} tools from Gmail Remote MCP.")

    # 2. Convert MCP tools into LangChain StructuredTool instances
    async def exec_mcp(tool_name: str, args: dict):
        async with httpx.AsyncClient(headers=headers, timeout=30.0) as client:
            resp = await client.post(
                endpoint_url,
                json={
                    "jsonrpc": "2.0",
                    "id": 100,
                    "method": "tools/call",
                    "params": {"name": tool_name, "arguments": args},
                },
            )
            return resp.json().get("result", {})

    langchain_tools = [
        StructuredTool(
            name=t["name"],
            description=t.get("description", "") or f"Executes {t['name']}",
            args_schema=t.get("inputSchema", {}) or {"type": "object", "properties": {}},
            coroutine=lambda _t=t["name"], **kw: exec_mcp(_t, kw),
        )
        for t in mcp_tools
    ]

    # 3. Initialize LangChain's ChatGoogleGenerativeAI with Gemini 3.7 Flash
    llm = ChatGoogleGenerativeAI(
        model="gemini-3.7-flash",
        project=project_id,
        location="global",
        temperature=0.2,
    )

    # 4. Compile the LangGraph ReAct Agent
    agent = create_react_agent(llm, langchain_tools)

    # 5. Invoke the Agent
    query = "What Gmail tools are available to help me manage drafts?"
    print(f"\n--- Query: '{query}' ---\n")

    response = await agent.ainvoke({"messages": [HumanMessage(content=query)]})
    for msg in response["messages"]:
        if msg.__class__.__name__ == "AIMessage" and msg.content:
            text = msg.content if isinstance(msg.content, str) else "".join(
                b.get("text", "") for b in msg.content if isinstance(b, dict) and "text" in b
            )
            if text:
                print(text)


if __name__ == "__main__":
    asyncio.run(main())
