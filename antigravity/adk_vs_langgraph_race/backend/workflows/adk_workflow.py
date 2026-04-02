"""
Google ADK 2.0 Multi-Step Workflow

Uses actual ADK 2.0 features:
- Agent class with instructions
- Tools for computation
- InMemoryRunner for execution
- Proper Vertex AI configuration
"""

import os
import time
from dataclasses import dataclass, field

from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from google.genai import types


@dataclass
class StepResult:
    """Result from a workflow step."""
    step_name: str
    output: str
    latency_ms: float
    timestamp: float = field(default_factory=time.time)


@dataclass
class WorkflowResult:
    """Complete workflow result."""
    framework: str
    final_answer: str
    total_latency_ms: float
    steps: list[StepResult]
    success: bool = True
    error: str | None = None


# Define tools for ADK agents
def calculate(expression: str) -> str:
    """Evaluate a mathematical expression.

    Args:
        expression: A math expression like "2 + 2" or "15 * 7"

    Returns:
        The result as a string
    """
    try:
        allowed = set("0123456789+-*/.() ")
        if all(c in allowed for c in expression):
            return str(eval(expression))
        return f"Cannot evaluate: {expression}"
    except Exception as e:
        return f"Error: {str(e)}"


def extract_numbers(text: str) -> str:
    """Extract all numbers from text.

    Args:
        text: Text containing numbers

    Returns:
        Comma-separated list of numbers
    """
    import re
    numbers = re.findall(r'-?\d+\.?\d*', text)
    return ", ".join(numbers) if numbers else "No numbers found"


class ADKWorkflow:
    """
    3-Step ADK 2.0 Workflow with Tools:
    1. Analyzer: Understand and break down the problem
    2. Reasoner: Apply logic and calculations (with tools)
    3. Synthesizer: Compile final answer
    """

    def __init__(self, project_id: str, location: str = "us-central1"):
        self.project_id = project_id
        self.location = location
        self.model = "gemini-2.0-flash-001"

        # Set Vertex AI environment variables for ADK
        os.environ['GOOGLE_GENAI_USE_VERTEXAI'] = 'true'
        os.environ['GOOGLE_CLOUD_PROJECT'] = project_id
        os.environ['GOOGLE_CLOUD_LOCATION'] = location

    async def _run_agent(
        self,
        agent: Agent,
        message: str,
    ) -> str:
        """Run a single agent and collect its response."""
        runner = InMemoryRunner(agent=agent, app_name=f"race_{agent.name}")

        session = await runner.session_service.create_session(
            app_name=f"race_{agent.name}",
            user_id="race_user",
        )

        # Create proper Content message
        content_message = types.Content(
            role='user',
            parts=[types.Part(text=message)]
        )

        response_parts = []

        async for event in runner.run_async(
            user_id="race_user",
            session_id=session.id,
            new_message=content_message,
        ):
            # Collect text from model responses
            if hasattr(event, 'content') and event.content:
                c = event.content
                if hasattr(c, 'parts'):
                    for part in c.parts:
                        if hasattr(part, 'text') and part.text:
                            response_parts.append(part.text)

        return "".join(response_parts) if response_parts else ""

    async def run(self, query: str) -> WorkflowResult:
        """Execute the full 3-step ADK workflow."""
        start_time = time.perf_counter()
        steps: list[StepResult] = []

        try:
            # Step 1: Analyzer Agent
            step1_start = time.perf_counter()

            analyzer = Agent(
                name="analyzer",
                model=self.model,
                instruction="""You are an expert problem analyzer. Your job is to:
1. Identify the type of problem (math, logic, code, etc.)
2. Extract key information and constraints
3. List the steps needed to solve it

Be concise and structured. Use plain text only - no LaTeX, no markdown formatting.""",
            )

            analysis = await self._run_agent(analyzer, query)

            step1_latency = (time.perf_counter() - step1_start) * 1000
            steps.append(StepResult(
                step_name="Analyzer",
                output=analysis or "Analysis completed",
                latency_ms=step1_latency
            ))

            # Step 2: Reasoner Agent (with calculate tool)
            step2_start = time.perf_counter()

            reasoner = Agent(
                name="reasoner",
                model=self.model,
                instruction="""You are a logical reasoner. Given a problem and its analysis:
1. Apply the appropriate reasoning method
2. Use the calculate tool for any math operations
3. Show your work step by step
4. Arrive at intermediate conclusions

Be precise with calculations. Use plain text only - no LaTeX. Write equations as: sqrt(x), x^2, etc.""",
                tools=[calculate],
            )

            reasoning_prompt = f"""Original Problem: {query}

Analysis:
{analysis}

Now solve this problem step by step. Use the calculate tool for math."""

            reasoning = await self._run_agent(reasoner, reasoning_prompt)

            step2_latency = (time.perf_counter() - step2_start) * 1000
            steps.append(StepResult(
                step_name="Reasoner",
                output=reasoning or "Reasoning completed",
                latency_ms=step2_latency
            ))

            # Step 3: Synthesizer Agent
            step3_start = time.perf_counter()

            synthesizer = Agent(
                name="synthesizer",
                model=self.model,
                instruction="""You are a final answer synthesizer. Your job is to:
1. Review the reasoning provided
2. Verify the logic is sound
3. Provide a clear, concise final answer

Format: Start with the direct answer, then brief explanation. Use plain text only - no LaTeX. Write equations as: sqrt(x), x^2, etc.""",
            )

            synthesis_prompt = f"""Original Question: {query}

Reasoning:
{reasoning}

Provide the final answer."""

            final_answer = await self._run_agent(synthesizer, synthesis_prompt)

            step3_latency = (time.perf_counter() - step3_start) * 1000
            steps.append(StepResult(
                step_name="Synthesizer",
                output=final_answer or "Synthesis completed",
                latency_ms=step3_latency
            ))

            total_latency = (time.perf_counter() - start_time) * 1000

            return WorkflowResult(
                framework="Google ADK 2.0",
                final_answer=final_answer or "No answer generated",
                total_latency_ms=total_latency,
                steps=steps,
                success=True
            )

        except Exception as e:
            total_latency = (time.perf_counter() - start_time) * 1000

            # Fill in missing steps
            while len(steps) < 3:
                step_names = ["Analyzer", "Reasoner", "Synthesizer"]
                steps.append(StepResult(
                    step_name=step_names[len(steps)],
                    output=f"Error: {str(e)}",
                    latency_ms=0
                ))

            return WorkflowResult(
                framework="Google ADK 2.0",
                final_answer="",
                total_latency_ms=total_latency,
                steps=steps,
                success=False,
                error=str(e)
            )
