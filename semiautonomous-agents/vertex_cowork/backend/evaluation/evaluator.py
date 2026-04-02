"""Agent evaluation framework for testing agent behavior."""

from dataclasses import dataclass, field
from typing import Any
import json

import logging

from agents.base import AgentFramework, AgentResponse

logger = logging.getLogger(__name__)


@dataclass
class EvaluationCase:
    """A single evaluation test case."""

    case_id: str
    description: str
    input_message: str
    expected_tools: list[str] = field(default_factory=list)
    expected_tool_order: str = "any"  # "exact", "in_order", "any"
    expected_content_contains: list[str] = field(default_factory=list)
    expected_content_not_contains: list[str] = field(default_factory=list)
    max_iterations: int = 10
    timeout_seconds: float = 60.0


@dataclass
class EvaluationResult:
    """Result of evaluating a single test case."""

    case_id: str
    passed: bool
    score: float  # 0.0 to 1.0
    actual_response: str
    actual_tools: list[str]
    errors: list[str] = field(default_factory=list)
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class EvaluationReport:
    """Full evaluation report for an agent."""

    agent_id: str
    total_cases: int
    passed_cases: int
    failed_cases: int
    overall_score: float
    results: list[EvaluationResult] = field(default_factory=list)


class AgentEvaluator:
    """Evaluator for testing agent behavior."""

    def __init__(self, framework: AgentFramework) -> None:
        self.framework = framework

    async def evaluate_case(
        self,
        agent_id: str,
        case: EvaluationCase,
    ) -> EvaluationResult:
        """Evaluate a single test case."""
        errors = []
        score = 0.0

        try:
            # Run the agent
            response = await self.framework.run(
                agent_id=agent_id,
                input_message=case.input_message,
                session_id=f"eval_{case.case_id}",
            )

            if not response.success:
                return EvaluationResult(
                    case_id=case.case_id,
                    passed=False,
                    score=0.0,
                    actual_response=response.error or "Unknown error",
                    actual_tools=[],
                    errors=[f"Agent execution failed: {response.error}"],
                )

            # Extract tool calls
            actual_tools = [tc.get("name", "") for tc in response.tool_calls]

            # Check tool usage
            tool_score = self._evaluate_tools(
                expected=case.expected_tools,
                actual=actual_tools,
                order=case.expected_tool_order,
            )

            # Check content
            content_score, content_errors = self._evaluate_content(
                response.content,
                case.expected_content_contains,
                case.expected_content_not_contains,
            )
            errors.extend(content_errors)

            # Calculate overall score
            if case.expected_tools:
                score = (tool_score + content_score) / 2
            else:
                score = content_score

            passed = score >= 0.8 and len(errors) == 0

            return EvaluationResult(
                case_id=case.case_id,
                passed=passed,
                score=score,
                actual_response=response.content,
                actual_tools=actual_tools,
                errors=errors,
                details={
                    "tool_score": tool_score,
                    "content_score": content_score,
                },
            )

        except Exception as e:
            logger.error(f"Evaluation error for case {case.case_id}: {e}")
            return EvaluationResult(
                case_id=case.case_id,
                passed=False,
                score=0.0,
                actual_response="",
                actual_tools=[],
                errors=[f"Evaluation error: {str(e)}"],
            )

    def _evaluate_tools(
        self,
        expected: list[str],
        actual: list[str],
        order: str,
    ) -> float:
        """Evaluate tool usage."""
        if not expected:
            return 1.0

        if order == "exact":
            return 1.0 if expected == actual else 0.0

        elif order == "in_order":
            # Check if expected tools appear in order (but not necessarily consecutive)
            actual_iter = iter(actual)
            try:
                for exp_tool in expected:
                    while True:
                        act_tool = next(actual_iter)
                        if act_tool == exp_tool:
                            break
                return 1.0
            except StopIteration:
                return 0.0

        else:  # "any"
            # Check if all expected tools were called (in any order)
            expected_set = set(expected)
            actual_set = set(actual)
            matched = expected_set & actual_set
            return len(matched) / len(expected_set) if expected_set else 1.0

    def _evaluate_content(
        self,
        content: str,
        contains: list[str],
        not_contains: list[str],
    ) -> tuple[float, list[str]]:
        """Evaluate response content."""
        errors = []
        total_checks = len(contains) + len(not_contains)

        if total_checks == 0:
            return 1.0, []

        passed_checks = 0
        content_lower = content.lower()

        for phrase in contains:
            if phrase.lower() in content_lower:
                passed_checks += 1
            else:
                errors.append(f"Expected content to contain: '{phrase}'")

        for phrase in not_contains:
            if phrase.lower() not in content_lower:
                passed_checks += 1
            else:
                errors.append(f"Expected content NOT to contain: '{phrase}'")

        return passed_checks / total_checks, errors

    async def evaluate_agent(
        self,
        agent_id: str,
        cases: list[EvaluationCase],
    ) -> EvaluationReport:
        """Evaluate an agent against multiple test cases."""
        results = []

        for case in cases:
            logger.info(f"Evaluating case {case.case_id} for agent {agent_id}")
            result = await self.evaluate_case(agent_id, case)
            results.append(result)

        passed = sum(1 for r in results if r.passed)
        failed = len(results) - passed
        overall_score = sum(r.score for r in results) / len(results) if results else 0.0

        report = EvaluationReport(
            agent_id=agent_id,
            total_cases=len(results),
            passed_cases=passed,
            failed_cases=failed,
            overall_score=overall_score,
            results=results,
        )

        logger.info(
            "evaluation_complete",
            agent_id=agent_id,
            passed=passed,
            failed=failed,
            score=overall_score,
        )

        return report

    def load_cases_from_json(self, json_path: str) -> list[EvaluationCase]:
        """Load evaluation cases from a JSON file."""
        with open(json_path) as f:
            data = json.load(f)

        return [
            EvaluationCase(
                case_id=case["case_id"],
                description=case.get("description", ""),
                input_message=case["input_message"],
                expected_tools=case.get("expected_tools", []),
                expected_tool_order=case.get("expected_tool_order", "any"),
                expected_content_contains=case.get("expected_content_contains", []),
                expected_content_not_contains=case.get("expected_content_not_contains", []),
                max_iterations=case.get("max_iterations", 10),
                timeout_seconds=case.get("timeout_seconds", 60.0),
            )
            for case in data.get("cases", [])
        ]
