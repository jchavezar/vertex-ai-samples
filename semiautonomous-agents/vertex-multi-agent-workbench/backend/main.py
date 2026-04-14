"""Vertex Cowork - Enterprise Agent Platform API."""

import os

# Configure Google GenAI SDK to use Vertex AI
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "1"

from contextlib import asynccontextmanager
from typing import Any, AsyncIterator

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
import logging

from core.config import get_settings, Settings
from core.registry import AgentRegistry, ModelRegistry, MCPServerRegistry, AgentInfo
from models.factory import ModelFactory
from mcp_integration.manager import MCPManager
from agents.factory import AgentFrameworkFactory
from agents.base import AgentConfig, AgentType

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Global instances
settings: Settings = None
model_registry: ModelRegistry = None
mcp_registry: MCPServerRegistry = None
agent_registry: AgentRegistry = None
model_factory: ModelFactory = None
mcp_manager: MCPManager = None
framework_factory: AgentFrameworkFactory = None
quick_chat_session_service = None  # For maintaining conversation history


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan manager."""
    global settings, model_registry, mcp_registry, agent_registry
    global model_factory, mcp_manager, framework_factory

    # Initialize
    settings = get_settings()
    model_registry = ModelRegistry()
    mcp_registry = MCPServerRegistry()
    agent_registry = AgentRegistry()
    model_factory = ModelFactory(model_registry)
    mcp_manager = MCPManager(mcp_registry)
    framework_factory = AgentFrameworkFactory(model_factory, mcp_manager)

    logger.info(f"Vertex Cowork started - project: {settings.gcp_project_id}")

    yield

    # Cleanup
    await mcp_manager.disconnect_all()
    logger.info("Vertex Cowork stopped")


app = FastAPI(
    title="Vertex Cowork",
    description="Enterprise Agent Platform with Multi-Model and Multi-Framework Support",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============ Request/Response Models ============


class ModelResponse(BaseModel):
    """Model information response."""

    model_id: str
    provider: str
    display_name: str
    capabilities: list[str]
    supports_tools: bool
    supports_vision: bool


class MCPServerCreate(BaseModel):
    """Request to register an MCP server."""

    server_id: str
    name: str
    transport: str = Field(..., pattern="^(stdio|sse|http)$")
    command: str | None = None
    url: str | None = None
    config: dict[str, Any] = Field(default_factory=dict)


class MCPServerResponse(BaseModel):
    """MCP server information response."""

    server_id: str
    name: str
    transport: str
    tools: list[str]
    resources: list[str]
    connected: bool


class AgentCreate(BaseModel):
    """Request to create an agent."""

    agent_id: str
    name: str
    description: str = ""
    model_id: str
    framework: str = Field(default="adk", pattern="^(adk|langgraph)$")
    agent_type: str = Field(default="llm")
    system_prompt: str = ""
    tools: list[str] = Field(default_factory=list)
    mcp_servers: list[str] = Field(default_factory=list)
    subagents: list[str] = Field(default_factory=list)
    max_iterations: int = 10
    temperature: float = 0.7
    config: dict[str, Any] = Field(default_factory=dict)


class AgentResponse(BaseModel):
    """Agent information response."""

    agent_id: str
    name: str
    description: str
    model_id: str
    framework: str
    agent_type: str
    tools: list[str]
    mcp_servers: list[str]
    subagents: list[str]


class ChatRequest(BaseModel):
    """Chat request to an agent."""

    message: str
    session_id: str | None = None
    stream: bool = False


class ChatResponse(BaseModel):
    """Chat response from an agent."""

    content: str
    tool_calls: list[dict[str, Any]] = Field(default_factory=list)
    agent_id: str
    success: bool
    error: str | None = None


# ============ Health Check ============


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy", "service": "vertex_cowork"}


# ============ Models API ============


@app.get("/api/models", response_model=list[ModelResponse])
async def list_models(
    provider: str | None = Query(None, description="Filter by provider"),
) -> list[ModelResponse]:
    """List available models."""
    if provider:
        models = model_registry.list_by_provider(provider)
    else:
        models = model_registry.list_all()

    return [
        ModelResponse(
            model_id=m.model_id,
            provider=m.provider,
            display_name=m.display_name,
            capabilities=m.capabilities,
            supports_tools=m.supports_tools,
            supports_vision=m.supports_vision,
        )
        for m in models
    ]


@app.get("/api/models/{model_id}", response_model=ModelResponse)
async def get_model(model_id: str) -> ModelResponse:
    """Get a specific model."""
    model = model_registry.get(model_id)
    if not model:
        raise HTTPException(status_code=404, detail=f"Model '{model_id}' not found")

    return ModelResponse(
        model_id=model.model_id,
        provider=model.provider,
        display_name=model.display_name,
        capabilities=model.capabilities,
        supports_tools=model.supports_tools,
        supports_vision=model.supports_vision,
    )


# ============ MCP Servers API ============


@app.post("/api/mcp-servers", response_model=MCPServerResponse)
async def register_mcp_server(request: MCPServerCreate) -> MCPServerResponse:
    """Register a new MCP server."""
    server_info = mcp_manager.register_server(
        server_id=request.server_id,
        name=request.name,
        transport=request.transport,
        command=request.command,
        url=request.url,
        config=request.config,
    )

    return MCPServerResponse(
        server_id=server_info.server_id,
        name=server_info.name,
        transport=server_info.transport,
        tools=server_info.tools,
        resources=server_info.resources,
        connected=False,
    )


@app.get("/api/mcp-servers", response_model=list[MCPServerResponse])
async def list_mcp_servers() -> list[MCPServerResponse]:
    """List all registered MCP servers."""
    servers = mcp_registry.list_all()
    connected = mcp_manager.list_connected_servers()

    return [
        MCPServerResponse(
            server_id=s.server_id,
            name=s.name,
            transport=s.transport,
            tools=s.tools,
            resources=s.resources,
            connected=s.server_id in connected,
        )
        for s in servers
    ]


@app.post("/api/mcp-servers/{server_id}/connect")
async def connect_mcp_server(server_id: str) -> MCPServerResponse:
    """Connect to an MCP server."""
    try:
        client = await mcp_manager.connect_server(server_id)
        server_info = mcp_registry.get(server_id)

        return MCPServerResponse(
            server_id=server_info.server_id,
            name=server_info.name,
            transport=server_info.transport,
            tools=[t.name for t in client.get_tools()],
            resources=[r.uri for r in client.get_resources()],
            connected=True,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/mcp-servers/{server_id}/disconnect")
async def disconnect_mcp_server(server_id: str) -> dict[str, str]:
    """Disconnect from an MCP server."""
    await mcp_manager.disconnect_server(server_id)
    return {"status": "disconnected", "server_id": server_id}


@app.delete("/api/mcp-servers/{server_id}")
async def delete_mcp_server(server_id: str) -> dict[str, str]:
    """Delete an MCP server."""
    # Disconnect first if connected
    try:
        await mcp_manager.disconnect_server(server_id)
    except Exception:
        pass  # Server might not be connected

    if not mcp_registry.unregister(server_id):
        raise HTTPException(status_code=404, detail=f"MCP server '{server_id}' not found")

    return {"status": "deleted", "server_id": server_id}


@app.get("/api/mcp-servers/{server_id}/context")
async def get_mcp_context(server_id: str) -> dict[str, Any]:
    """Get context info from an MCP server (e.g., authenticated user and repos for GitHub)."""
    import httpx
    import json

    context = {"server_id": server_id}

    # For GitHub, use the token directly to get user info (like Claude Code does)
    if server_id == "github":
        server_info = mcp_registry.get(server_id)
        github_token = None
        if server_info and server_info.config:
            env = server_info.config.get("env", {})
            github_token = env.get("GITHUB_PERSONAL_ACCESS_TOKEN")

        if github_token:
            try:
                # Call GitHub API directly to get authenticated user
                async with httpx.AsyncClient() as client:
                    headers = {
                        "Authorization": f"Bearer {github_token}",
                        "Accept": "application/vnd.github+json",
                    }

                    # Get user info
                    user_resp = await client.get("https://api.github.com/user", headers=headers)
                    if user_resp.status_code == 200:
                        user_data = user_resp.json()
                        context["user"] = {
                            "login": user_data.get("login"),
                            "name": user_data.get("name") or user_data.get("login"),
                        }
                        logger.info(f"GitHub user from API: {context['user']['login']}")

                        # Get user's repos
                        repos_resp = await client.get(
                            "https://api.github.com/user/repos?sort=pushed&per_page=30",
                            headers=headers
                        )
                        if repos_resp.status_code == 200:
                            repos_data = repos_resp.json()
                            context["repos"] = [
                                {
                                    "name": r.get("name"),
                                    "full_name": r.get("full_name"),
                                    "description": (r.get("description") or "")[:100],
                                    "language": r.get("language"),
                                    "stars": r.get("stargazers_count", 0),
                                }
                                for r in repos_data[:30]
                            ]
                            logger.info(f"Fetched {len(context['repos'])} repos for {context['user']['login']}")
                    else:
                        logger.warning(f"GitHub API returned {user_resp.status_code}")
            except Exception as e:
                logger.warning(f"Could not fetch GitHub user: {e}")
        else:
            logger.warning("No GITHUB_PERSONAL_ACCESS_TOKEN in config")

    return context


@app.get("/api/mcp-servers/{server_id}/tools")
async def list_mcp_tools(server_id: str) -> list[dict[str, Any]]:
    """List tools from a connected MCP server."""
    client = mcp_manager.get_client(server_id)
    if not client:
        raise HTTPException(status_code=404, detail=f"MCP server '{server_id}' not connected")

    return [
        {
            "name": t.name,
            "description": t.description,
            "input_schema": t.input_schema,
        }
        for t in client.get_tools()
    ]


class MCPToolCallRequest(BaseModel):
    """Request to call an MCP tool."""
    arguments: dict[str, Any] = Field(default_factory=dict)


@app.post("/api/mcp-servers/{server_id}/tools/{tool_name}")
async def call_mcp_tool(server_id: str, tool_name: str, request: MCPToolCallRequest) -> dict[str, Any]:
    """Call a tool on an MCP server."""
    try:
        result = await mcp_manager.call_tool(server_id, tool_name, request.arguments)
        # Extract text content from result
        content = []
        if hasattr(result, 'content'):
            for item in result.content:
                if hasattr(item, 'text'):
                    content.append(item.text)
        return {
            "success": True,
            "tool": tool_name,
            "result": content[0] if len(content) == 1 else content,
        }
    except Exception as e:
        logger.error(f"MCP tool call failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============ Agents API ============


@app.post("/api/agents", response_model=AgentResponse)
async def create_agent(request: AgentCreate) -> AgentResponse:
    """Create a new agent."""
    # Get the appropriate framework
    framework = framework_factory.get_framework(request.framework)

    # Create agent config
    config = AgentConfig(
        agent_id=request.agent_id,
        name=request.name,
        description=request.description,
        model_id=request.model_id,
        agent_type=AgentType(request.agent_type),
        system_prompt=request.system_prompt,
        tools=request.tools,
        mcp_servers=request.mcp_servers,
        subagents=request.subagents,
        max_iterations=request.max_iterations,
        temperature=request.temperature,
        config=request.config,
    )

    # Create the agent
    await framework.create_agent(config)

    # Register in agent registry
    agent_info = AgentInfo(
        agent_id=request.agent_id,
        name=request.name,
        framework=request.framework,
        model_id=request.model_id,
        description=request.description,
        tools=request.tools,
        mcp_servers=request.mcp_servers,
        subagents=request.subagents,
        config=request.config,
    )
    agent_registry.register(agent_info)

    return AgentResponse(
        agent_id=request.agent_id,
        name=request.name,
        description=request.description,
        model_id=request.model_id,
        framework=request.framework,
        agent_type=request.agent_type,
        tools=request.tools,
        mcp_servers=request.mcp_servers,
        subagents=request.subagents,
    )


@app.get("/api/agents", response_model=list[AgentResponse])
async def list_agents(
    framework: str | None = Query(None, description="Filter by framework"),
) -> list[AgentResponse]:
    """List all agents."""
    if framework:
        agents = agent_registry.list_by_framework(framework)
    else:
        agents = agent_registry.list_all()

    return [
        AgentResponse(
            agent_id=a.agent_id,
            name=a.name,
            description=a.description,
            model_id=a.model_id,
            framework=a.framework,
            agent_type=a.config.get("agent_type", "llm"),
            tools=a.tools,
            mcp_servers=a.mcp_servers,
            subagents=a.subagents,
        )
        for a in agents
    ]


@app.get("/api/agents/{agent_id}", response_model=AgentResponse)
async def get_agent(agent_id: str) -> AgentResponse:
    """Get a specific agent."""
    agent = agent_registry.get(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")

    return AgentResponse(
        agent_id=agent.agent_id,
        name=agent.name,
        description=agent.description,
        model_id=agent.model_id,
        framework=agent.framework,
        agent_type=agent.config.get("agent_type", "llm"),
        tools=agent.tools,
        mcp_servers=agent.mcp_servers,
        subagents=agent.subagents,
    )


@app.delete("/api/agents/{agent_id}")
async def delete_agent(agent_id: str) -> dict[str, str]:
    """Delete an agent."""
    if not agent_registry.unregister(agent_id):
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")

    return {"status": "deleted", "agent_id": agent_id}


# ============ Chat API ============


@app.post("/api/agents/{agent_id}/chat", response_model=ChatResponse)
async def chat_with_agent(agent_id: str, request: ChatRequest) -> ChatResponse:
    """Chat with an agent."""
    agent_info = agent_registry.get(agent_id)
    if not agent_info:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")

    framework = framework_factory.get_framework(agent_info.framework)

    if request.stream:
        # Return streaming response
        async def generate():
            async for chunk in framework.stream(
                agent_id,
                request.message,
                request.session_id,
            ):
                yield f"data: {chunk}\n\n"
            yield "data: [DONE]\n\n"

        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
        )

    # Non-streaming response
    result = await framework.run(
        agent_id,
        request.message,
        request.session_id,
    )

    return ChatResponse(
        content=result.content,
        tool_calls=result.tool_calls,
        agent_id=result.agent_id,
        success=result.success,
        error=result.error,
    )


# ============ Quick Chat API (No Agent Required) ============


async def quick_chat_with_mcp(request: "QuickChatRequest") -> ChatResponse:
    """Quick chat with MCP tools using ADK - with conversation history support."""
    import os
    from google.adk.agents import LlmAgent
    from google.adk.runners import Runner
    from google.adk.sessions import InMemorySessionService
    from google.adk.tools import McpToolset
    from google.genai.types import Content, Part
    from mcp import StdioServerParameters

    global quick_chat_session_service

    try:
        # Build MCP toolsets and gather context
        tools = []
        mcp_context_parts = []

        for server_id in request.mcp_servers:
            server_info = mcp_registry.get(server_id)
            if not server_info or not server_info.command:
                logger.warning(f"MCP server '{server_id}' not found or has no command")
                continue

            cmd_parts = server_info.command.split()
            env = os.environ.copy()
            if server_info.config and "env" in server_info.config:
                env.update(server_info.config["env"])

            server_params = StdioServerParameters(
                command=cmd_parts[0],
                args=cmd_parts[1:] if len(cmd_parts) > 1 else [],
                env=env,
            )

            mcp_toolset = McpToolset(
                connection_params=server_params,
                tool_name_prefix=f"{server_id}_",
            )
            tools.append(mcp_toolset)
            mcp_context_parts.append(f"- {server_info.name} ({server_id})")
            logger.info(f"Quick chat: Added MCP toolset for {server_id}")

        # Build conversation history context
        history_context = ""
        if request.history:
            history_lines = []
            for msg in request.history[-10:]:  # Last 10 messages for context
                role = "User" if msg.role == "user" else "Assistant"
                history_lines.append(f"{role}: {msg.content[:500]}")  # Truncate long messages
            history_context = "\n\n**Recent conversation:**\n" + "\n".join(history_lines)

        # Build enhanced system prompt with MCP context
        mcp_context = "\n".join(mcp_context_parts)
        enhanced_prompt = f"""{request.system_prompt}

**Connected MCP Servers:**
{mcp_context}
{history_context}

**CRITICAL INSTRUCTIONS:**
1. ALWAYS use tools to get real data - never make things up
2. You have CONVERSATION CONTEXT above - use it! If user said a repo name before, REMEMBER it
3. When user says "yes" or follows up, use the context from previous messages
4. When results include repos/issues owned by the authenticated user, HIGHLIGHT them
5. Be CONCISE and SMART - don't ask for info the user already provided"""

        # Use global session service for persistence
        if quick_chat_session_service is None:
            quick_chat_session_service = InMemorySessionService()

        session_id = request.session_id or "default_quick_chat"
        app_name = "vertex_cowork_quick_mcp"

        agent = LlmAgent(
            name="quick_mcp_assistant",
            model=request.model_id,
            instruction=enhanced_prompt,
            tools=tools,
        )

        runner = Runner(
            agent=agent,
            session_service=quick_chat_session_service,
            app_name=app_name,
        )

        # Check if session exists, create if not
        existing = await quick_chat_session_service.get_session(
            app_name=app_name, user_id="default_user", session_id=session_id
        )
        if not existing:
            await quick_chat_session_service.create_session(
                app_name=app_name,
                user_id="default_user",
                session_id=session_id,
            )

        user_message = Content(parts=[Part(text=request.message)], role="user")
        result = runner.run_async(
            user_id="default_user",
            session_id=session_id,
            new_message=user_message,
        )

        content_parts = []
        tool_calls = []
        async for event in result:
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if hasattr(part, 'text') and part.text:
                        content_parts.append(part.text)
                    if hasattr(part, 'function_call') and part.function_call:
                        tool_calls.append({
                            "name": part.function_call.name,
                            "arguments": dict(part.function_call.args) if part.function_call.args else {},
                        })

        # Cleanup toolsets
        for toolset in tools:
            try:
                await toolset.close()
            except Exception:
                pass

        return ChatResponse(
            content="".join(content_parts),
            tool_calls=tool_calls,
            agent_id="quick_chat_mcp",
            success=True,
        )

    except Exception as e:
        logger.error(f"Quick chat with MCP error: {e}")
        return ChatResponse(
            content="",
            tool_calls=[],
            agent_id="quick_chat_mcp",
            success=False,
            error=str(e),
        )


class ChatMessage(BaseModel):
    """A single chat message."""
    role: str  # "user" or "assistant"
    content: str


class QuickChatRequest(BaseModel):
    """Quick chat request without agent."""
    message: str
    model_id: str = "gemini-2.5-flash"
    system_prompt: str = "You are a helpful AI assistant."
    session_id: str | None = None
    mcp_servers: list[str] = Field(default_factory=list)
    history: list[ChatMessage] = Field(default_factory=list)  # Conversation history


@app.post("/api/chat", response_model=ChatResponse)
async def quick_chat(request: QuickChatRequest) -> ChatResponse:
    """Quick chat with optional MCP tools - supports Gemini, Claude, and Llama models."""
    try:
        # If MCP servers are specified and using Gemini, use ADK with tools
        if request.mcp_servers and not ("claude" in request.model_id.lower() or "llama" in request.model_id.lower()):
            return await quick_chat_with_mcp(request)

        # Check if it's a Claude model
            from models.provider import ClaudeVertexProvider

            provider = ClaudeVertexProvider(
                model_id=request.model_id,
                project_id=settings.gcp_project_id,
                location="global",
            )

            messages = [{"role": "user", "content": request.message}]
            result = await provider.generate(
                messages=messages,
                system=request.system_prompt,
                max_tokens=4096,
            )

            return ChatResponse(
                content=result["content"],
                tool_calls=[],
                agent_id="quick_chat",
                success=True,
            )
        # Check if it's a Llama model
        elif "llama" in request.model_id.lower():
            from models.provider import LlamaVertexProvider

            provider = LlamaVertexProvider(
                model_id=request.model_id,
                project_id=settings.gcp_project_id,
                location="us-central1",
            )

            messages = [{"role": "user", "content": request.message}]
            result = await provider.generate(
                messages=messages,
                max_tokens=4096,
            )

            return ChatResponse(
                content=result["content"],
                tool_calls=[],
                agent_id="quick_chat",
                success=True,
            )
        else:
            # Use ADK for Gemini models
            from google.adk.agents import LlmAgent
            from google.adk.runners import Runner
            from google.adk.sessions import InMemorySessionService
            from google.genai.types import Content, Part

            session_service = InMemorySessionService()
            session_id = request.session_id or f"quick_{id(request)}"
            app_name = "vertex_cowork_quick"

            agent = LlmAgent(
                name="quick_assistant",
                model=request.model_id,
                instruction=request.system_prompt,
                tools=[],
            )

            runner = Runner(
                agent=agent,
                session_service=session_service,
                app_name=app_name,
            )

            await session_service.create_session(
                app_name=app_name,
                user_id="default_user",
                session_id=session_id,
            )

            user_message = Content(parts=[Part(text=request.message)], role="user")
            result = runner.run_async(
                user_id="default_user",
                session_id=session_id,
                new_message=user_message,
            )

            content_parts = []
            async for event in result:
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if hasattr(part, 'text') and part.text:
                            content_parts.append(part.text)

            return ChatResponse(
                content="".join(content_parts),
                tool_calls=[],
                agent_id="quick_chat",
                success=True,
            )
    except Exception as e:
        logger.error(f"Quick chat error: {e}")
        return ChatResponse(
            content="",
            tool_calls=[],
            agent_id="quick_chat",
            success=False,
            error=str(e),
        )


# ============ Frameworks API ============


@app.get("/api/frameworks")
async def list_frameworks() -> list[dict[str, Any]]:
    """List available agent frameworks."""
    frameworks = []
    for fw_type in framework_factory.list_frameworks():
        info = framework_factory.get_framework_info(fw_type)
        frameworks.append({"type": fw_type, **info})
    return frameworks


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
