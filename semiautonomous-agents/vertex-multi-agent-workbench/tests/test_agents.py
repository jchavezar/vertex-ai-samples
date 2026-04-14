"""Tests for agent framework functionality."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

import sys
sys.path.insert(0, "../backend")

from backend.agents.base import AgentConfig, AgentType, AgentResponse
from backend.agents.factory import AgentFrameworkFactory
from backend.core.registry import ModelRegistry, MCPServerRegistry
from backend.models.factory import ModelFactory
from backend.mcp.manager import MCPManager


@pytest.fixture
def model_registry():
    """Create a model registry with test models."""
    registry = ModelRegistry()
    return registry


@pytest.fixture
def mcp_registry():
    """Create an MCP server registry."""
    return MCPServerRegistry()


@pytest.fixture
def model_factory(model_registry):
    """Create a model factory."""
    with patch("backend.models.factory.get_settings") as mock_settings:
        mock_settings.return_value = MagicMock(
            gcp_project_id="test-project",
            gcp_location="us-central1",
        )
        return ModelFactory(model_registry)


@pytest.fixture
def mcp_manager(mcp_registry):
    """Create an MCP manager."""
    return MCPManager(mcp_registry)


@pytest.fixture
def framework_factory(model_factory, mcp_manager):
    """Create an agent framework factory."""
    with patch("backend.agents.factory.get_settings") as mock_settings:
        mock_settings.return_value = MagicMock(default_framework="adk")
        return AgentFrameworkFactory(model_factory, mcp_manager)


class TestAgentConfig:
    """Tests for AgentConfig dataclass."""

    def test_create_llm_config(self):
        """Test creating an LLM agent config."""
        config = AgentConfig(
            agent_id="test-agent",
            name="Test Agent",
            description="A test agent",
            model_id="gemini-2.0-flash",
            agent_type=AgentType.LLM,
            system_prompt="You are a helpful assistant.",
        )

        assert config.agent_id == "test-agent"
        assert config.agent_type == AgentType.LLM
        assert config.model_id == "gemini-2.0-flash"

    def test_create_supervisor_config(self):
        """Test creating a supervisor agent config."""
        config = AgentConfig(
            agent_id="supervisor",
            name="Supervisor Agent",
            description="Orchestrates other agents",
            model_id="gemini-2.0-flash",
            agent_type=AgentType.SUPERVISOR,
            subagents=["worker-1", "worker-2"],
        )

        assert config.agent_type == AgentType.SUPERVISOR
        assert len(config.subagents) == 2

    def test_create_sequential_config(self):
        """Test creating a sequential agent config."""
        config = AgentConfig(
            agent_id="sequential",
            name="Sequential Agent",
            description="Runs agents in sequence",
            model_id="gemini-2.0-flash",
            agent_type=AgentType.SEQUENTIAL,
            subagents=["step-1", "step-2", "step-3"],
        )

        assert config.agent_type == AgentType.SEQUENTIAL
        assert len(config.subagents) == 3


class TestAgentResponse:
    """Tests for AgentResponse dataclass."""

    def test_successful_response(self):
        """Test creating a successful response."""
        response = AgentResponse(
            content="Hello, world!",
            tool_calls=[{"name": "search", "arguments": {"query": "test"}}],
            agent_id="test-agent",
            success=True,
        )

        assert response.success
        assert response.content == "Hello, world!"
        assert len(response.tool_calls) == 1

    def test_error_response(self):
        """Test creating an error response."""
        response = AgentResponse(
            content="",
            agent_id="test-agent",
            success=False,
            error="Model invocation failed",
        )

        assert not response.success
        assert response.error == "Model invocation failed"


class TestAgentFrameworkFactory:
    """Tests for AgentFrameworkFactory."""

    def test_list_frameworks(self, framework_factory):
        """Test listing available frameworks."""
        frameworks = framework_factory.list_frameworks()
        assert "adk" in frameworks
        assert "langgraph" in frameworks

    def test_get_framework_info(self, framework_factory):
        """Test getting framework information."""
        adk_info = framework_factory.get_framework_info("adk")
        assert adk_info["name"] == "Google ADK"
        assert "features" in adk_info

        langgraph_info = framework_factory.get_framework_info("langgraph")
        assert langgraph_info["name"] == "LangGraph"


class TestModelRegistry:
    """Tests for ModelRegistry."""

    def test_default_models_registered(self, model_registry):
        """Test that default models are registered."""
        models = model_registry.list_all()
        assert len(models) > 0

        # Check for Gemini models
        gemini_models = model_registry.list_by_provider("vertex")
        assert len(gemini_models) > 0

    def test_get_model(self, model_registry):
        """Test getting a specific model."""
        model = model_registry.get("gemini-2.0-flash")
        assert model is not None
        assert model.provider == "vertex"

    def test_list_by_provider(self, model_registry):
        """Test filtering models by provider."""
        vertex_models = model_registry.list_by_provider("vertex")
        model_garden_models = model_registry.list_by_provider("model_garden")

        for model in vertex_models:
            assert model.provider == "vertex"

        for model in model_garden_models:
            assert model.provider == "model_garden"


class TestMCPServerRegistry:
    """Tests for MCPServerRegistry."""

    def test_register_server(self, mcp_registry):
        """Test registering an MCP server."""
        from backend.core.registry import MCPServerInfo

        server_info = MCPServerInfo(
            server_id="test-server",
            name="Test Server",
            transport="stdio",
            command="npx test-server",
        )

        mcp_registry.register(server_info)
        retrieved = mcp_registry.get("test-server")

        assert retrieved is not None
        assert retrieved.name == "Test Server"

    def test_unregister_server(self, mcp_registry):
        """Test unregistering an MCP server."""
        from backend.core.registry import MCPServerInfo

        server_info = MCPServerInfo(
            server_id="to-remove",
            name="To Remove",
            transport="http",
            url="http://localhost:3000",
        )

        mcp_registry.register(server_info)
        assert mcp_registry.get("to-remove") is not None

        result = mcp_registry.unregister("to-remove")
        assert result is True
        assert mcp_registry.get("to-remove") is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
