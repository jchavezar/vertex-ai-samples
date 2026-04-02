"""
Answer Evaluator using Gemini 3.1 Flash Lite

Compares answers from both frameworks for correctness.
"""

import time
from dataclasses import dataclass
from google import genai
from google.genai import types


@dataclass
class EvaluationResult:
    """Evaluation result for an answer."""
    framework: str
    score: float  # 0-100
    is_correct: bool
    feedback: str
    latency_ms: float


@dataclass
class ComparisonResult:
    """Comparison between two framework answers."""
    adk_evaluation: EvaluationResult
    langgraph_evaluation: EvaluationResult
    winner: str  # "ADK", "LangGraph", "Tie"
    explanation: str
    evaluation_latency_ms: float


class AnswerEvaluator:
    """Evaluates and compares answers using Gemini 3.1 Flash Lite."""

    def __init__(self, project_id: str, location: str = "us-central1"):
        self.project_id = project_id
        self.location = location
        # Using gemini-2.0-flash-lite as the fast evaluation model
        self.model = "gemini-2.0-flash-lite-001"

        self.client = genai.Client(
            vertexai=True,
            project=project_id,
            location=location
        )

    async def evaluate_answer(
        self,
        query: str,
        answer: str,
        framework: str
    ) -> EvaluationResult:
        """Evaluate a single answer."""
        start_time = time.perf_counter()

        prompt = f"""You are an expert evaluator. Score this answer on correctness.

Question: {query}

Answer from {framework}:
{answer}

Evaluate:
1. Is the final answer correct? (true/false)
2. Score from 0-100 based on accuracy, completeness, and clarity
3. Brief feedback (1-2 sentences)

Respond in this exact format:
CORRECT: true/false
SCORE: [number]
FEEDBACK: [your feedback]"""

        try:
            response = await self.client.aio.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.0,
                    max_output_tokens=256,
                )
            )

            latency_ms = (time.perf_counter() - start_time) * 1000
            text = response.text if response.text else ""

            # Parse response
            text_lower = text.lower()
            is_correct = "correct: true" in text_lower or "correct:true" in text_lower
            score = 50.0  # default
            feedback = "Unable to parse feedback"

            for line in text.split("\n"):
                line_upper = line.upper().strip()
                if line_upper.startswith("SCORE:"):
                    try:
                        score = float(line.split(":", 1)[1].strip())
                    except (ValueError, IndexError):
                        pass
                elif line_upper.startswith("FEEDBACK:"):
                    feedback = line.split(":", 1)[1].strip() if ":" in line else line
                elif line_upper.startswith("CORRECT:"):
                    val = line.split(":", 1)[1].strip().lower() if ":" in line else ""
                    is_correct = val in ("true", "yes", "1", "correct")

            return EvaluationResult(
                framework=framework,
                score=score,
                is_correct=is_correct,
                feedback=feedback,
                latency_ms=latency_ms
            )

        except Exception as e:
            latency_ms = (time.perf_counter() - start_time) * 1000
            return EvaluationResult(
                framework=framework,
                score=0.0,
                is_correct=False,
                feedback=f"Evaluation error: {str(e)}",
                latency_ms=latency_ms
            )

    async def compare_answers(
        self,
        query: str,
        adk_answer: str,
        langgraph_answer: str
    ) -> ComparisonResult:
        """Compare answers from both frameworks."""
        import asyncio

        start_time = time.perf_counter()

        # Evaluate both in parallel
        adk_eval, langgraph_eval = await asyncio.gather(
            self.evaluate_answer(query, adk_answer, "Google ADK 2.0"),
            self.evaluate_answer(query, langgraph_answer, "LangGraph")
        )

        # Determine winner
        if adk_eval.score > langgraph_eval.score + 5:
            winner = "ADK"
            explanation = f"ADK scored {adk_eval.score:.0f} vs LangGraph's {langgraph_eval.score:.0f}"
        elif langgraph_eval.score > adk_eval.score + 5:
            winner = "LangGraph"
            explanation = f"LangGraph scored {langgraph_eval.score:.0f} vs ADK's {adk_eval.score:.0f}"
        else:
            winner = "Tie"
            explanation = f"Both scored similarly: ADK {adk_eval.score:.0f}, LangGraph {langgraph_eval.score:.0f}"

        total_latency = (time.perf_counter() - start_time) * 1000

        return ComparisonResult(
            adk_evaluation=adk_eval,
            langgraph_evaluation=langgraph_eval,
            winner=winner,
            explanation=explanation,
            evaluation_latency_ms=total_latency
        )
