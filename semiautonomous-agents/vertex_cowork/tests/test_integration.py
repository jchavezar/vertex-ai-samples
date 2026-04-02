"""Integration tests for Vertex Cowork."""

import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch, MagicMock

import sys
sys.path.insert(0, "../backend")


@pytest.fixture
def mock_settings():
    """Mock settings for testing."""
    with patch("backend.core.config.get_settings") as mock:
        mock.return_value = MagicMock(
            gcp_project_id="test-project",
            gcp_location="us-central1",
            database_url="postgresql+asyncpg://localhost:5432/test",
            redis_url="redis://localhost:6379",
            default_framework="adk",
            default_model="gemini-2.0-flash",
            api_host="0.0.0.0",
            api_port=8080,
            enable_auth=False,
        )
        yield mock


@pytest.fixture
async def client(mock_settings):
    """Create test client."""
    # Import here to use mocked settings
    from backend.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac


class TestHealthEndpoint:
    """Tests for health check endpoint."""

    @pytest.mark.asyncio
    async def test_health_check(self, client):
        """Test health check returns healthy status."""
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "vertex_cowork"


class TestModelsAPI:
    """Tests for models API endpoints."""

    @pytest.mark.asyncio
    async def test_list_models(self, client):
        """Test listing all models."""
        response = await client.get("/api/models")
        assert response.status_code == 200
        models = response.json()
        assert isinstance(models, list)
        assert len(models) > 0

    @pytest.mark.asyncio
    async def test_list_models_by_provider(self, client):
        """Test listing models filtered by provider."""
        response = await client.get("/api/models?provider=vertex")
        assert response.status_code == 200
        models = response.json()
        for model in models:
            assert model["provider"] == "vertex"

    @pytest.mark.asyncio
    async def test_get_model(self, client):
        """Test getting a specific model."""
        response = await client.get("/api/models/gemini-2.0-flash")
        assert response.status_code == 200
        model = response.json()
        assert model["model_id"] == "gemini-2.0-flash"

    @pytest.mark.asyncio
    async def test_get_nonexistent_model(self, client):
        """Test getting a model that doesn't exist."""
        response = await client.get("/api/models/nonexistent-model")
        assert response.status_code == 404


class TestMCPServersAPI:
    """Tests for MCP servers API endpoints."""

    @pytest.mark.asyncio
    async def test_list_empty_servers(self, client):
        """Test listing servers when none are registered."""
        response = await client.get("/api/mcp-servers")
        assert response.status_code == 200
        servers = response.json()
        assert isinstance(servers, list)

    @pytest.mark.asyncio
    async def test_register_server(self, client):
        """Test registering a new MCP server."""
        server_data = {
            "server_id": "test-server",
            "name": "Test Server",
            "transport": "stdio",
            "command": "npx test-server",
        }

        response = await client.post("/api/mcp-servers", json=server_data)
        assert response.status_code == 200
        server = response.json()
        assert server["server_id"] == "test-server"
        assert server["connected"] is False


class TestAgentsAPI:
    """Tests for agents API endpoints."""

    @pytest.mark.asyncio
    async def test_list_empty_agents(self, client):
        """Test listing agents when none exist."""
        response = await client.get("/api/agents")
        assert response.status_code == 200
        agents = response.json()
        assert isinstance(agents, list)

    @pytest.mark.asyncio
    async def test_create_agent(self, client):
        """Test creating a new agent."""
        agent_data = {
            "agent_id": "test-agent",
            "name": "Test Agent",
            "description": "A test agent",
            "model_id": "gemini-2.0-flash",
            "framework": "adk",
            "agent_type": "llm",
            "system_prompt": "You are a helpful assistant.",
        }

        with patch("backend.agents.adk_framework.ADKFramework.create_agent") as mock:
            mock.return_value = MagicMock()
            response = await client.post("/api/agents", json=agent_data)

        assert response.status_code == 200
        agent = response.json()
        assert agent["agent_id"] == "test-agent"
        assert agent["framework"] == "adk"

    @pytest.mark.asyncio
    async def test_create_langgraph_agent(self, client):
        """Test creating a LangGraph agent."""
        agent_data = {
            "agent_id": "langgraph-agent",
            "name": "LangGraph Agent",
            "model_id": "gemini-2.0-flash",
            "framework": "langgraph",
            "agent_type": "llm",
        }

        with patch(
            "backend.agents.langgraph_framework.LangGraphFramework.create_agent"
        ) as mock:
            mock.return_value = MagicMock()
            response = await client.post("/api/agents", json=agent_data)

        assert response.status_code == 200
        agent = response.json()
        assert agent["framework"] == "langgraph"


class TestFrameworksAPI:
    """Tests for frameworks API endpoint."""

    @pytest.mark.asyncio
    async def test_list_frameworks(self, client):
        """Test listing available frameworks."""
        response = await client.get("/api/frameworks")
        assert response.status_code == 200
        frameworks = response.json()
        assert len(frameworks) == 2

        framework_types = [f["type"] for f in frameworks]
        assert "adk" in framework_types
        assert "langgraph" in framework_types


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
