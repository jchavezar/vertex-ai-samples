"""
LangGraph Multi-Step Workflow

This workflow uses LangGraph features:
- StateGraph with typed state
- Node-based execution
- Tools with bind_tools
"""

import time
from typing import TypedDict
from dataclasses import dataclass, field

from langchain_google_vertexai import ChatVertexAI
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode


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


# Define tools
@tool
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


@tool
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


class GraphState(TypedDict):
    """State passed between nodes."""
    query: str
    analysis: str
    reasoning: str
    final_answer: str
    steps: list[StepResult]


class LangGraphWorkflow:
    """
    3-Step LangGraph Workflow with Tools:
    1. Analyzer: Understand and break down the problem
    2. Reasoner: Apply logic and calculations (with tools)
    3. Synthesizer: Compile final answer
    """

    def __init__(self, project_id: str, location: str = "us-central1"):
        self.project_id = project_id
        self.location = location

        # Tools for the reasoner
        self.tools = [calculate, extract_numbers]

        # Initialize LLMs
        self.llm = ChatVertexAI(
            model="gemini-2.0-flash-001",
            project=project_id,
            location=location,
            temperature=0.1,
            max_output_tokens=1024,
        )

        # LLM with tools bound
        self.llm_with_tools = self.llm.bind_tools(self.tools)

        # Build the graph
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow."""

        async def analyze_node(state: GraphState) -> GraphState:
            """Step 1: Analyze the problem."""
            start_time = time.perf_counter()

            messages = [
                SystemMessage(content="""You are an expert problem analyzer. Your job is to:
1. Identify the type of problem (math, logic, code, etc.)
2. Extract key information and constraints
3. List the steps needed to solve it

Be concise and structured. Use plain text only - no LaTeX, no markdown formatting."""),
                HumanMessage(content=state["query"])
            ]

            response = await self.llm.ainvoke(messages)
            latency_ms = (time.perf_counter() - start_time) * 1000

            state["analysis"] = response.content
            state["steps"].append(StepResult(
                step_name="Analyzer",
                output=response.content,
                latency_ms=latency_ms
            ))

            return state

        async def reason_node(state: GraphState) -> GraphState:
            """Step 2: Apply reasoning with tools."""
            start_time = time.perf_counter()

            messages = [
                SystemMessage(content="""You are a logical reasoner. Given a problem and its analysis:
1. Apply the appropriate reasoning method
2. Use the calculate tool for any math operations
3. Show your work step by step
4. Arrive at intermediate conclusions

Be precise with calculations. Use plain text only - no LaTeX. Write equations as: sqrt(x), x^2, etc."""),
                HumanMessage(content=f"""Original Problem: {state["query"]}

Analysis:
{state["analysis"]}

Now solve this problem step by step. Use the calculate tool for math.""")
            ]

            # Call LLM with tools
            response = await self.llm_with_tools.ainvoke(messages)

            # Check if tool calls were made
            if response.tool_calls:
                # Execute tools
                tool_results = []
                for tool_call in response.tool_calls:
                    tool_name = tool_call["name"]
                    tool_args = tool_call["args"]

                    if tool_name == "calculate":
                        result = calculate.invoke(tool_args)
                    elif tool_name == "extract_numbers":
                        result = extract_numbers.invoke(tool_args)
                    else:
                        result = "Unknown tool"

                    tool_results.append(f"{tool_name}({tool_args}): {result}")

                # Make follow-up call with tool results
                follow_up = [
                    SystemMessage(content="Provide the final reasoning based on the tool results."),
                    HumanMessage(content=f"Tool results:\n" + "\n".join(tool_results) + "\n\nNow provide your reasoning.")
                ]
                final_response = await self.llm.ainvoke(follow_up)
                reasoning = final_response.content
            else:
                reasoning = response.content

            latency_ms = (time.perf_counter() - start_time) * 1000

            state["reasoning"] = reasoning
            state["steps"].append(StepResult(
                step_name="Reasoner",
                output=reasoning,
                latency_ms=latency_ms
            ))

            return state

        async def synthesize_node(state: GraphState) -> GraphState:
            """Step 3: Synthesize final answer."""
            start_time = time.perf_counter()

            messages = [
                SystemMessage(content="""You are a final answer synthesizer. Your job is to:
1. Review the reasoning provided
2. Verify the logic is sound
3. Provide a clear, concise final answer

Format: Start with the direct answer, then brief explanation. Use plain text only - no LaTeX. Write equations as: sqrt(x), x^2, etc."""),
                HumanMessage(content=f"""Original Question: {state["query"]}

Reasoning:
{state["reasoning"]}

Provide the final answer.""")
            ]

            response = await self.llm.ainvoke(messages)
            latency_ms = (time.perf_counter() - start_time) * 1000

            state["final_answer"] = response.content
            state["steps"].append(StepResult(
                step_name="Synthesizer",
                output=response.content,
                latency_ms=latency_ms
            ))

            return state

        # Build the graph
        builder = StateGraph(GraphState)

        # Add nodes
        builder.add_node("analyzer", analyze_node)
        builder.add_node("reasoner", reason_node)
        builder.add_node("synthesizer", synthesize_node)

        # Add edges
        builder.add_edge(START, "analyzer")
        builder.add_edge("analyzer", "reasoner")
        builder.add_edge("reasoner", "synthesizer")
        builder.add_edge("synthesizer", END)

        return builder.compile()

    async def run(self, query: str) -> WorkflowResult:
        """Execute the full 3-step workflow."""
        start_time = time.perf_counter()

        try:
            initial_state: GraphState = {
                "query": query,
                "analysis": "",
                "reasoning": "",
                "final_answer": "",
                "steps": [],
            }

            # Run the graph
            final_state = await self.graph.ainvoke(initial_state)

            total_latency = (time.perf_counter() - start_time) * 1000

            return WorkflowResult(
                framework="LangGraph",
                final_answer=final_state["final_answer"],
                total_latency_ms=total_latency,
                steps=final_state["steps"],
                success=True
            )

        except Exception as e:
            total_latency = (time.perf_counter() - start_time) * 1000
            return WorkflowResult(
                framework="LangGraph",
                final_answer="",
                total_latency_ms=total_latency,
                steps=[],
                success=False,
                error=str(e)
            )
