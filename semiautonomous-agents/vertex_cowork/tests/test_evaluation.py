"""Tests for the evaluation framework."""

import pytest
from unittest.mock import AsyncMock, MagicMock

import sys
sys.path.insert(0, "../backend")

from backend.evaluation.evaluator import (
    AgentEvaluator,
    EvaluationCase,
    EvaluationResult,
    EvaluationReport,
)
from backend.agents.base import AgentFramework, AgentResponse


@pytest.fixture
def mock_framework():
    """Create a mock agent framework."""
    framework = MagicMock(spec=AgentFramework)
    framework.run = AsyncMock()
    return framework


@pytest.fixture
def evaluator(mock_framework):
    """Create an evaluator with mock framework."""
    return AgentEvaluator(mock_framework)


class TestEvaluationCase:
    """Tests for EvaluationCase dataclass."""

    def test_basic_case(self):
        """Test creating a basic evaluation case."""
        case = EvaluationCase(
            case_id="test-1",
            description="Test case",
            input_message="Hello",
            expected_content_contains=["hello", "world"],
        )

        assert case.case_id == "test-1"
        assert len(case.expected_content_contains) == 2

    def test_tool_case(self):
        """Test creating an evaluation case with tool expectations."""
        case = EvaluationCase(
            case_id="tool-test",
            description="Test tool usage",
            input_message="Search for Python",
            expected_tools=["search", "summarize"],
            expected_tool_order="in_order",
        )

        assert len(case.expected_tools) == 2
        assert case.expected_tool_order == "in_order"


class TestAgentEvaluator:
    """Tests for AgentEvaluator."""

    @pytest.mark.asyncio
    async def test_evaluate_successful_case(self, evaluator, mock_framework):
        """Test evaluating a successful case."""
        mock_framework.run.return_value = AgentResponse(
            content="Hello, I can help you with that!",
            tool_calls=[],
            agent_id="test-agent",
            success=True,
        )

        case = EvaluationCase(
            case_id="test-success",
            description="Test success",
            input_message="Can you help me?",
            expected_content_contains=["help"],
        )

        result = await evaluator.evaluate_case("test-agent", case)

        assert result.passed
        assert result.score > 0.8
        assert "help" in result.actual_response.lower()

    @pytest.mark.asyncio
    async def test_evaluate_failed_case(self, evaluator, mock_framework):
        """Test evaluating a failed case."""
        mock_framework.run.return_value = AgentResponse(
            content="I don't understand.",
            tool_calls=[],
            agent_id="test-agent",
            success=True,
        )

        case = EvaluationCase(
            case_id="test-fail",
            description="Test failure",
            input_message="Calculate 2+2",
            expected_content_contains=["4", "four"],
        )

        result = await evaluator.evaluate_case("test-agent", case)

        assert not result.passed
        assert result.score < 0.8
        assert len(result.errors) > 0

    @pytest.mark.asyncio
    async def test_evaluate_tool_usage(self, evaluator, mock_framework):
        """Test evaluating tool usage."""
        mock_framework.run.return_value = AgentResponse(
            content="Here are the search results.",
            tool_calls=[
                {"name": "search", "arguments": {"query": "test"}},
                {"name": "format", "arguments": {}},
            ],
            agent_id="test-agent",
            success=True,
        )

        case = EvaluationCase(
            case_id="test-tools",
            description="Test tool usage",
            input_message="Search for test",
            expected_tools=["search"],
            expected_tool_order="any",
        )

        result = await evaluator.evaluate_case("test-agent", case)

        assert result.passed
        assert "search" in result.actual_tools

    @pytest.mark.asyncio
    async def test_evaluate_agent_report(self, evaluator, mock_framework):
        """Test generating a full evaluation report."""
        mock_framework.run.return_value = AgentResponse(
            content="Response content",
            tool_calls=[],
            agent_id="test-agent",
            success=True,
        )

        cases = [
            EvaluationCase(
                case_id=f"case-{i}",
                description=f"Test case {i}",
                input_message=f"Test {i}",
                expected_content_contains=["response"],
            )
            for i in range(3)
        ]

        report = await evaluator.evaluate_agent("test-agent", cases)

        assert report.total_cases == 3
        assert report.agent_id == "test-agent"
        assert len(report.results) == 3

    def test_evaluate_tools_exact_order(self, evaluator):
        """Test tool evaluation with exact order."""
        score = evaluator._evaluate_tools(
            expected=["a", "b", "c"],
            actual=["a", "b", "c"],
            order="exact",
        )
        assert score == 1.0

        score = evaluator._evaluate_tools(
            expected=["a", "b", "c"],
            actual=["a", "c", "b"],
            order="exact",
        )
        assert score == 0.0

    def test_evaluate_tools_in_order(self, evaluator):
        """Test tool evaluation with in_order."""
        score = evaluator._evaluate_tools(
            expected=["a", "c"],
            actual=["a", "b", "c", "d"],
            order="in_order",
        )
        assert score == 1.0

        score = evaluator._evaluate_tools(
            expected=["c", "a"],
            actual=["a", "b", "c"],
            order="in_order",
        )
        assert score == 0.0

    def test_evaluate_tools_any_order(self, evaluator):
        """Test tool evaluation with any order."""
        score = evaluator._evaluate_tools(
            expected=["a", "b"],
            actual=["b", "c", "a"],
            order="any",
        )
        assert score == 1.0

        score = evaluator._evaluate_tools(
            expected=["a", "b", "c"],
            actual=["a", "d"],
            order="any",
        )
        assert score == pytest.approx(1 / 3)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
