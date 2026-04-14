"""Registry classes for managing agents, models, and MCP servers."""

from dataclasses import dataclass, field
from typing import Any

import logging

logger = logging.getLogger(__name__)


@dataclass
class ModelInfo:
    """Information about a registered model."""

    model_id: str
    provider: str  # "vertex", "model_garden", "anthropic", "openai"
    display_name: str
    capabilities: list[str] = field(default_factory=list)
    max_tokens: int = 8192
    supports_tools: bool = True
    supports_vision: bool = False
    config: dict[str, Any] = field(default_factory=dict)


@dataclass
class MCPServerInfo:
    """Information about a registered MCP server."""

    server_id: str
    name: str
    transport: str  # "stdio", "sse", "http"
    command: str | None = None
    url: str | None = None
    tools: list[str] = field(default_factory=list)
    resources: list[str] = field(default_factory=list)
    config: dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentInfo:
    """Information about a registered agent."""

    agent_id: str
    name: str
    framework: str  # "adk", "langgraph"
    model_id: str
    description: str = ""
    tools: list[str] = field(default_factory=list)
    mcp_servers: list[str] = field(default_factory=list)
    subagents: list[str] = field(default_factory=list)
    config: dict[str, Any] = field(default_factory=dict)


class ModelRegistry:
    """Registry for available AI models."""

    def __init__(self) -> None:
        self._models: dict[str, ModelInfo] = {}
        self._initialize_default_models()

    def _initialize_default_models(self) -> None:
        """Initialize with default Vertex AI models."""
        default_models = [
            # Latest Gemini 3.x models
            ModelInfo(
                model_id="gemini-3-flash-preview",
                provider="vertex",
                display_name="Gemini 3 Flash Preview",
                capabilities=["text", "code", "reasoning", "tools", "thinking"],
                max_tokens=65536,
                supports_tools=True,
                supports_vision=True,
            ),
            ModelInfo(
                model_id="gemini-3.1-pro-preview",
                provider="vertex",
                display_name="Gemini 3.1 Pro Preview",
                capabilities=["text", "code", "reasoning", "tools", "long_context", "thinking"],
                max_tokens=131072,
                supports_tools=True,
                supports_vision=True,
            ),
            ModelInfo(
                model_id="gemini-3.1-flash-lite-preview",
                provider="vertex",
                display_name="Gemini 3.1 Flash Lite Preview",
                capabilities=["text", "code", "reasoning", "tools"],
                max_tokens=32768,
                supports_tools=True,
                supports_vision=True,
            ),
            # Gemini 2.5 models
            ModelInfo(
                model_id="gemini-2.5-flash",
                provider="vertex",
                display_name="Gemini 2.5 Flash",
                capabilities=["text", "code", "reasoning", "tools", "thinking"],
                max_tokens=65536,
                supports_tools=True,
                supports_vision=True,
            ),
            ModelInfo(
                model_id="gemini-2.5-pro",
                provider="vertex",
                display_name="Gemini 2.5 Pro",
                capabilities=["text", "code", "reasoning", "tools", "long_context", "thinking"],
                max_tokens=131072,
                supports_tools=True,
                supports_vision=True,
            ),
            # Claude models via Vertex AI (AnthropicVertex SDK, global region)
            ModelInfo(
                model_id="claude-sonnet-4-6",
                provider="claude_vertex",
                display_name="Claude Sonnet 4.6",
                capabilities=["text", "code", "reasoning", "tools"],
                max_tokens=8192,
                supports_tools=True,
                supports_vision=True,
            ),
            ModelInfo(
                model_id="claude-opus-4-6",
                provider="claude_vertex",
                display_name="Claude Opus 4.6",
                capabilities=["text", "code", "reasoning", "tools", "long_context"],
                max_tokens=32768,
                supports_tools=True,
                supports_vision=True,
            ),
            ModelInfo(
                model_id="claude-sonnet-4-5",
                provider="claude_vertex",
                display_name="Claude Sonnet 4.5",
                capabilities=["text", "code", "reasoning", "tools"],
                max_tokens=8192,
                supports_tools=True,
                supports_vision=True,
            ),
            ModelInfo(
                model_id="claude-opus-4-5",
                provider="claude_vertex",
                display_name="Claude Opus 4.5",
                capabilities=["text", "code", "reasoning", "tools", "long_context"],
                max_tokens=32768,
                supports_tools=True,
                supports_vision=True,
            ),
            ModelInfo(
                model_id="claude-haiku-4-5",
                provider="claude_vertex",
                display_name="Claude Haiku 4.5",
                capabilities=["text", "code", "reasoning"],
                max_tokens=8192,
                supports_tools=True,
                supports_vision=True,
            ),
            # Llama models via Vertex AI MaaS
            ModelInfo(
                model_id="llama-3.3-70b-instruct-maas",
                provider="llama_vertex",
                display_name="Llama 3.3 70B Instruct",
                capabilities=["text", "code", "reasoning"],
                max_tokens=8192,
                supports_tools=False,
                supports_vision=False,
            ),
        ]

        for model in default_models:
            self.register(model)

    def register(self, model: ModelInfo) -> None:
        """Register a model."""
        self._models[model.model_id] = model
        logger.info(f"Model registered: {model.model_id}")

    def get(self, model_id: str) -> ModelInfo | None:
        """Get a model by ID."""
        return self._models.get(model_id)

    def list_all(self) -> list[ModelInfo]:
        """List all registered models."""
        return list(self._models.values())

    def list_by_provider(self, provider: str) -> list[ModelInfo]:
        """List models by provider."""
        return [m for m in self._models.values() if m.provider == provider]


class MCPServerRegistry:
    """Registry for MCP servers."""

    def __init__(self) -> None:
        self._servers: dict[str, MCPServerInfo] = {}

    def register(self, server: MCPServerInfo) -> None:
        """Register an MCP server."""
        self._servers[server.server_id] = server
        logger.info(f"MCP server registered: {server.server_id}")

    def unregister(self, server_id: str) -> bool:
        """Unregister an MCP server."""
        if server_id in self._servers:
            del self._servers[server_id]
            logger.info(f"MCP server unregistered: {server_id}")
            return True
        return False

    def get(self, server_id: str) -> MCPServerInfo | None:
        """Get an MCP server by ID."""
        return self._servers.get(server_id)

    def list_all(self) -> list[MCPServerInfo]:
        """List all registered MCP servers."""
        return list(self._servers.values())


class AgentRegistry:
    """Registry for agents."""

    def __init__(self) -> None:
        self._agents: dict[str, AgentInfo] = {}

    def register(self, agent: AgentInfo) -> None:
        """Register an agent."""
        self._agents[agent.agent_id] = agent
        logger.info(f"Agent registered: {agent.agent_id}")

    def unregister(self, agent_id: str) -> bool:
        """Unregister an agent."""
        if agent_id in self._agents:
            del self._agents[agent_id]
            logger.info(f"Agent unregistered: {agent_id}")
            return True
        return False

    def get(self, agent_id: str) -> AgentInfo | None:
        """Get an agent by ID."""
        return self._agents.get(agent_id)

    def list_all(self) -> list[AgentInfo]:
        """List all registered agents."""
        return list(self._agents.values())

    def list_by_framework(self, framework: str) -> list[AgentInfo]:
        """List agents by framework."""
        return [a for a in self._agents.values() if a.framework == framework]
