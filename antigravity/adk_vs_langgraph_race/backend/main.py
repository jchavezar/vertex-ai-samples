"""
AI Framework Race: ADK vs LangGraph

FastAPI backend that runs both workflows in parallel and streams results.
"""

import os
import json
import asyncio
from typing import AsyncGenerator
from contextlib import asynccontextmanager
from dataclasses import asdict

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel
from dotenv import load_dotenv

from workflows.adk_workflow import ADKWorkflow
from workflows.langgraph_workflow import LangGraphWorkflow
from workflows.evaluator import AnswerEvaluator

load_dotenv()

# Configuration
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", os.getenv("PROJECT_ID", ""))
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")

# Workflows (initialized on startup)
adk_workflow: ADKWorkflow | None = None
langgraph_workflow: LangGraphWorkflow | None = None
evaluator: AnswerEvaluator | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize workflows on startup."""
    global adk_workflow, langgraph_workflow, evaluator

    if not PROJECT_ID:
        raise RuntimeError("GOOGLE_CLOUD_PROJECT or PROJECT_ID must be set")

    print(f"Initializing workflows with project={PROJECT_ID}, location={LOCATION}")

    adk_workflow = ADKWorkflow(PROJECT_ID, LOCATION)
    langgraph_workflow = LangGraphWorkflow(PROJECT_ID, LOCATION)
    evaluator = AnswerEvaluator(PROJECT_ID, LOCATION)

    print("Workflows initialized successfully!")
    yield


app = FastAPI(
    title="AI Framework Race",
    description="Race between Google ADK 2.0 and LangGraph",
    lifespan=lifespan
)


class RaceRequest(BaseModel):
    """Request to start a race."""
    query: str


class StepUpdate(BaseModel):
    """Real-time update for a workflow step."""
    framework: str
    step_name: str
    output: str
    latency_ms: float
    is_final: bool = False


async def race_generator(query: str) -> AsyncGenerator[str, None]:
    """
    Run both workflows in parallel and stream results as SSE events.
    """
    if not adk_workflow or not langgraph_workflow or not evaluator:
        yield f"data: {json.dumps({'error': 'Workflows not initialized'})}\n\n"
        return

    # Track completion
    results = {"adk": None, "langgraph": None}

    async def run_adk():
        """Run ADK workflow and stream steps."""
        result = await adk_workflow.run(query)
        results["adk"] = result
        return result

    async def run_langgraph():
        """Run LangGraph workflow and stream steps."""
        result = await langgraph_workflow.run(query)
        results["langgraph"] = result
        return result

    # Send start event
    yield f"data: {json.dumps({'event': 'race_start', 'query': query})}\n\n"

    # Create tasks for parallel execution
    adk_task = asyncio.create_task(run_adk())
    langgraph_task = asyncio.create_task(run_langgraph())

    # Wait for both to complete
    done, pending = await asyncio.wait(
        [adk_task, langgraph_task],
        return_when=asyncio.ALL_COMPLETED
    )

    # Get results
    adk_result = await adk_task
    langgraph_result = await langgraph_task

    # Send ADK steps
    for step in adk_result.steps:
        yield f"data: {json.dumps({
            'event': 'step',
            'framework': 'ADK',
            'step_name': step.step_name,
            'output': step.output[:500] + '...' if len(step.output) > 500 else step.output,
            'latency_ms': round(step.latency_ms, 2)
        })}\n\n"

    # Send LangGraph steps
    for step in langgraph_result.steps:
        yield f"data: {json.dumps({
            'event': 'step',
            'framework': 'LangGraph',
            'step_name': step.step_name,
            'output': step.output[:500] + '...' if len(step.output) > 500 else step.output,
            'latency_ms': round(step.latency_ms, 2)
        })}\n\n"

    # Send final results
    yield f"data: {json.dumps({
        'event': 'result',
        'framework': 'ADK',
        'final_answer': adk_result.final_answer,
        'total_latency_ms': round(adk_result.total_latency_ms, 2),
        'success': adk_result.success,
        'error': adk_result.error
    })}\n\n"

    yield f"data: {json.dumps({
        'event': 'result',
        'framework': 'LangGraph',
        'final_answer': langgraph_result.final_answer,
        'total_latency_ms': round(langgraph_result.total_latency_ms, 2),
        'success': langgraph_result.success,
        'error': langgraph_result.error
    })}\n\n"

    # Run evaluation
    yield f"data: {json.dumps({'event': 'evaluating'})}\n\n"

    comparison = await evaluator.compare_answers(
        query,
        adk_result.final_answer,
        langgraph_result.final_answer
    )

    # Send evaluation results
    yield f"data: {json.dumps({
        'event': 'evaluation',
        'adk_score': comparison.adk_evaluation.score,
        'adk_correct': comparison.adk_evaluation.is_correct,
        'adk_feedback': comparison.adk_evaluation.feedback,
        'langgraph_score': comparison.langgraph_evaluation.score,
        'langgraph_correct': comparison.langgraph_evaluation.is_correct,
        'langgraph_feedback': comparison.langgraph_evaluation.feedback,
        'winner': comparison.winner,
        'explanation': comparison.explanation,
        'evaluation_latency_ms': round(comparison.evaluation_latency_ms, 2)
    })}\n\n"

    # Send race complete
    yield f"data: {json.dumps({
        'event': 'race_complete',
        'adk_total_ms': round(adk_result.total_latency_ms, 2),
        'langgraph_total_ms': round(langgraph_result.total_latency_ms, 2),
        'faster': 'ADK' if adk_result.total_latency_ms < langgraph_result.total_latency_ms else 'LangGraph',
        'time_diff_ms': round(abs(adk_result.total_latency_ms - langgraph_result.total_latency_ms), 2)
    })}\n\n"


@app.post("/api/race")
async def start_race(request: RaceRequest):
    """Start a race between ADK and LangGraph."""
    return StreamingResponse(
        race_generator(request.query),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


@app.get("/api/test-cases")
async def get_test_cases():
    """Return sample test cases for the race."""
    return {
        "test_cases": [
            {
                "id": 1,
                "name": "Multi-step Math",
                "query": "A train leaves Station A at 8:00 AM traveling at 60 mph. Another train leaves Station B (300 miles away) at 9:00 AM traveling toward Station A at 90 mph. At what time will they meet?"
            },
            {
                "id": 2,
                "name": "Logic Puzzle",
                "query": "There are 5 houses in a row. The red house is to the left of the blue house. The green house is in the middle. The yellow house is not next to the green house. The white house is at one end. What is the order of houses from left to right?"
            },
            {
                "id": 3,
                "name": "Code Analysis",
                "query": "Given this Python code: `result = [x**2 for x in range(10) if x % 2 == 0]`. What is the sum of all elements in result?"
            },
            {
                "id": 4,
                "name": "Science Reasoning",
                "query": "If I drop a ball from 80 meters on Earth (g=10 m/s^2) and another ball from 45 meters on a planet with g=20 m/s^2, which ball hits the ground first and by how many seconds?"
            },
            {
                "id": 5,
                "name": "Historical Analysis",
                "query": "If World War II ended in 1945, the Moon landing was in 1969, and the Berlin Wall fell in 1989, how many years passed between each event, and what's the total span?"
            },
            {
                "id": 6,
                "name": "Multi-hop Reasoning",
                "query": "Alice is twice as old as Bob. In 10 years, Alice will be 1.5 times Bob's age. How old is Charlie if Charlie is the average of their current ages?"
            },
            {
                "id": 7,
                "name": "Data Transformation",
                "query": "Convert the list [3, 1, 4, 1, 5, 9, 2, 6] to: 1) sorted ascending, 2) unique values only, 3) sum of unique values, 4) average of unique values."
            },
            {
                "id": 8,
                "name": "Business Calculation",
                "query": "A company has 3 products. Product A costs $50 with 30% margin, Product B costs $80 with 25% margin, Product C costs $120 with 40% margin. If they sell 100 of A, 75 of B, and 50 of C, what's the total profit?"
            }
        ]
    }


@app.get("/health")
async def health():
    """Health check."""
    return {"status": "healthy", "project": PROJECT_ID}


# Serve frontend
app.mount("/static", StaticFiles(directory="../frontend/static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the frontend."""
    with open("../frontend/index.html", "r") as f:
        return f.read()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
