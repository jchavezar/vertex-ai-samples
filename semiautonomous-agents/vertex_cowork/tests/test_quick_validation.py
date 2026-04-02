#!/usr/bin/env python3
"""Quick validation test for Vertex Cowork core components."""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

def test_imports():
    """Test that all core modules can be imported."""
    print("Testing imports...")

    # Core
    from core.config import Settings
    from core.registry import AgentRegistry, ModelRegistry, MCPServerRegistry
    print("  - core: OK")

    # Models
    from models.provider import ModelProvider, VertexProvider, ModelGardenProvider
    from models.factory import ModelFactory
    print("  - models: OK")

    # MCP
    from mcp.client import MCPClient, MCPTool, MCPResource
    from mcp.manager import MCPManager
    print("  - mcp: OK")

    # Agents
    from agents.base import AgentFramework, AgentConfig, AgentResponse, AgentType
    from agents.factory import AgentFrameworkFactory
    print("  - agents: OK")

    # Evaluation
    from evaluation.evaluator import AgentEvaluator, EvaluationCase, EvaluationResult
    print("  - evaluation: OK")

    print("\nAll imports successful!")


def test_model_registry():
    """Test model registry functionality."""
    print("\nTesting ModelRegistry...")

    from core.registry import ModelRegistry

    registry = ModelRegistry()
    models = registry.list_all()

    print(f"  - Registered models: {len(models)}")

    vertex_models = registry.list_by_provider("vertex")
    print(f"  - Vertex AI models: {len(vertex_models)}")

    garden_models = registry.list_by_provider("model_garden")
    print(f"  - Model Garden models: {len(garden_models)}")

    # Test getting specific model
    gemini = registry.get("gemini-2.0-flash")
    assert gemini is not None, "Gemini 2.0 Flash should be registered"
    print(f"  - Gemini 2.0 Flash: {gemini.display_name}")

    print("\nModelRegistry tests passed!")


def test_agent_config():
    """Test agent configuration."""
    print("\nTesting AgentConfig...")

    from agents.base import AgentConfig, AgentType

    # Create LLM agent config
    config = AgentConfig(
        agent_id="test-agent",
        name="Test Agent",
        description="A test agent",
        model_id="gemini-2.0-flash",
        agent_type=AgentType.LLM,
        system_prompt="You are a helpful assistant.",
        mcp_servers=["filesystem"],
    )

    assert config.agent_id == "test-agent"
    assert config.agent_type == AgentType.LLM
    assert len(config.mcp_servers) == 1
    print("  - LLM agent config: OK")

    # Create supervisor config
    supervisor = AgentConfig(
        agent_id="supervisor",
        name="Supervisor",
        description="Orchestrates agents",
        model_id="gemini-2.0-pro",
        agent_type=AgentType.SUPERVISOR,
        subagents=["worker-1", "worker-2"],
    )

    assert supervisor.agent_type == AgentType.SUPERVISOR
    assert len(supervisor.subagents) == 2
    print("  - Supervisor config: OK")

    print("\nAgentConfig tests passed!")


def test_framework_factory():
    """Test framework factory."""
    print("\nTesting AgentFrameworkFactory...")

    from agents.factory import AgentFrameworkFactory

    # Mock dependencies (without actual GCP connection)
    class MockModelFactory:
        pass

    class MockMCPManager:
        pass

    from unittest.mock import patch, MagicMock

    with patch("agents.factory.get_settings") as mock_settings:
        mock_settings.return_value = MagicMock(default_framework="adk")

        factory = AgentFrameworkFactory(MockModelFactory(), MockMCPManager())

        frameworks = factory.list_frameworks()
        assert "adk" in frameworks
        assert "langgraph" in frameworks
        print(f"  - Available frameworks: {frameworks}")

        adk_info = factory.get_framework_info("adk")
        assert adk_info["name"] == "Google ADK"
        print(f"  - ADK features: {len(adk_info['features'])}")

        lg_info = factory.get_framework_info("langgraph")
        assert lg_info["name"] == "LangGraph"
        print(f"  - LangGraph features: {len(lg_info['features'])}")

    print("\nAgentFrameworkFactory tests passed!")


def test_evaluation():
    """Test evaluation components."""
    print("\nTesting Evaluation...")

    from evaluation.evaluator import EvaluationCase, EvaluationResult

    case = EvaluationCase(
        case_id="test-1",
        description="Test case",
        input_message="Hello",
        expected_tools=["search"],
        expected_content_contains=["hello"],
    )

    assert case.case_id == "test-1"
    assert case.expected_tool_order == "any"
    print("  - EvaluationCase: OK")

    result = EvaluationResult(
        case_id="test-1",
        passed=True,
        score=0.95,
        actual_response="Hello, how can I help?",
        actual_tools=["search"],
    )

    assert result.passed
    assert result.score > 0.9
    print("  - EvaluationResult: OK")

    print("\nEvaluation tests passed!")


def main():
    """Run all validation tests."""
    print("=" * 60)
    print("Vertex Cowork - Quick Validation")
    print("=" * 60)

    try:
        test_imports()
        test_model_registry()
        test_agent_config()
        test_framework_factory()
        test_evaluation()

        print("\n" + "=" * 60)
        print("ALL VALIDATION TESTS PASSED!")
        print("=" * 60)
        return 0

    except Exception as e:
        print(f"\nVALIDATION FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
