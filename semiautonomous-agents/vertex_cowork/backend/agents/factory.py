"""Factory for creating agent frameworks."""

from typing import Literal

import logging

from agents.base import AgentFramework
from agents.adk_framework import ADKFramework
from agents.langgraph_framework import LangGraphFramework
from models.factory import ModelFactory
from mcp_integration.manager import MCPManager
from core.config import get_settings

logger = logging.getLogger(__name__)


class AgentFrameworkFactory:
    """Factory for creating and managing agent frameworks."""

    def __init__(
        self,
        model_factory: ModelFactory,
        mcp_manager: MCPManager,
    ) -> None:
        self.model_factory = model_factory
        self.mcp_manager = mcp_manager
        self._frameworks: dict[str, AgentFramework] = {}
        self._settings = get_settings()

    def get_framework(
        self,
        framework_type: Literal["adk", "langgraph"] | None = None,
    ) -> AgentFramework:
        """Get or create an agent framework instance."""
        framework_type = framework_type or self._settings.default_framework

        if framework_type in self._frameworks:
            return self._frameworks[framework_type]

        if framework_type == "adk":
            framework = ADKFramework(
                model_factory=self.model_factory,
                mcp_manager=self.mcp_manager,
            )
        elif framework_type == "langgraph":
            framework = LangGraphFramework(
                model_factory=self.model_factory,
                mcp_manager=self.mcp_manager,
            )
        else:
            raise ValueError(f"Unsupported framework: {framework_type}")

        self._frameworks[framework_type] = framework
        logger.info(f"Framework created: {framework_type}")

        return framework

    def list_frameworks(self) -> list[str]:
        """List available framework types."""
        return ["adk", "langgraph"]

    def get_framework_info(self, framework_type: str) -> dict:
        """Get information about a framework."""
        info = {
            "adk": {
                "name": "Google ADK",
                "description": "Google's Agent Development Kit - native Vertex AI integration",
                "features": [
                    "Native MCP support via McpToolset",
                    "SequentialAgent, ParallelAgent, LoopAgent",
                    "Built-in evaluation framework",
                    "Vertex AI Agent Engine deployment",
                    "Multi-language support (Python, TypeScript, Go, Java)",
                ],
                "best_for": [
                    "Google Cloud native deployments",
                    "Gemini-optimized agents",
                    "Enterprise governance requirements",
                ],
            },
            "langgraph": {
                "name": "LangGraph",
                "description": "LangChain's graph-based agent framework",
                "features": [
                    "Flexible graph-based workflows",
                    "StateGraph for complex state management",
                    "Supervisor and hierarchical patterns",
                    "Strong LangChain ecosystem integration",
                    "Memory and checkpointing",
                ],
                "best_for": [
                    "Complex multi-agent orchestration",
                    "Custom workflow patterns",
                    "LangChain ecosystem users",
                ],
            },
        }
        return info.get(framework_type, {})
