"""Base classes for agent framework abstraction."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, AsyncIterator
from enum import Enum


class AgentType(Enum):
    """Types of agents."""

    LLM = "llm"  # LLM-based reasoning agent
    SEQUENTIAL = "sequential"  # Sequential workflow agent
    PARALLEL = "parallel"  # Parallel execution agent
    LOOP = "loop"  # Loop/iteration agent
    SUPERVISOR = "supervisor"  # Supervisor/coordinator agent


@dataclass
class AgentConfig:
    """Configuration for creating an agent."""

    agent_id: str
    name: str
    description: str
    model_id: str
    agent_type: AgentType = AgentType.LLM
    system_prompt: str = ""
    tools: list[str] = field(default_factory=list)
    mcp_servers: list[str] = field(default_factory=list)
    subagents: list[str] = field(default_factory=list)
    max_iterations: int = 10
    temperature: float = 0.7
    config: dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentResponse:
    """Response from an agent execution."""

    content: str
    tool_calls: list[dict[str, Any]] = field(default_factory=list)
    intermediate_steps: list[dict[str, Any]] = field(default_factory=list)
    usage: dict[str, Any] = field(default_factory=dict)
    agent_id: str = ""
    success: bool = True
    error: str | None = None


class AgentFramework(ABC):
    """Abstract base class for agent frameworks."""

    framework_name: str = "base"

    @abstractmethod
    async def create_agent(self, config: AgentConfig) -> Any:
        """Create an agent with the given configuration."""
        pass

    @abstractmethod
    async def run(
        self,
        agent_id: str,
        input_message: str,
        session_id: str | None = None,
    ) -> AgentResponse:
        """Run the agent with the given input."""
        pass

    @abstractmethod
    async def stream(
        self,
        agent_id: str,
        input_message: str,
        session_id: str | None = None,
    ) -> AsyncIterator[str]:
        """Stream the agent's response."""
        pass

    @abstractmethod
    async def add_tool(self, agent_id: str, tool: Any) -> None:
        """Add a tool to an existing agent."""
        pass

    @abstractmethod
    async def add_mcp_server(self, agent_id: str, server_id: str) -> None:
        """Add MCP server tools to an agent."""
        pass

    @abstractmethod
    async def add_subagent(self, parent_id: str, child_id: str) -> None:
        """Add a subagent to a parent agent."""
        pass

    @abstractmethod
    def get_agent(self, agent_id: str) -> Any | None:
        """Get an agent by ID."""
        pass

    @abstractmethod
    def list_agents(self) -> list[str]:
        """List all agent IDs managed by this framework."""
        pass
