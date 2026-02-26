import os
import hashlib
from typing import List, Optional, Literal
from pydantic import BaseModel, Field
from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.artifacts import InMemoryArtifactService
from google.genai import types

# Force Vertex AI configuration if missing from environment
# These are essential for the google-genai SDK used by ADK
if not os.environ.get("GOOGLE_CLOUD_PROJECT"):
    os.environ["GOOGLE_CLOUD_PROJECT"] = "deloitte-plantas"
if not os.environ.get("GOOGLE_CLOUD_LOCATION"):
    os.environ["GOOGLE_CLOUD_LOCATION"] = "us-central1"
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "true"

# 1. Define the Output Schema
class FactSegment(BaseModel):
    text: str = Field(description="A segment of the response text")
    attribution: Literal["grounded", "knowledge"] = Field(
        description="Whether this segment is explicitly found in the sources or is general LLM knowledge"
    )
    source_ref: Optional[str] = Field(
        None, description="Reference to the source document if grounded (e.g., 'DOC 1')"
    )

class EvaluationResult(BaseModel):
    segments: List[FactSegment] = Field(description="The full response decomposed into attributed segments")

# 2. Define the Evaluator Agent
evaluator_agent = LlmAgent(
    name="fact_evaluator",
    model="gemini-2.5-flash", 
    instruction="""
    You are a Fact-Attribution Specialist. Your goal is to analyze a generated answer and its source documents.
    
    TASK:
    1. Read the provided 'Answer' and the list of 'Sources'.
    2. Decompose the 'Answer' into segments (sentences or logical phrases).
    3. For EACH segment, compare it against the 'Sources'.
    4. If the segment contains specific data, numbers, or unique facts present in the sources, mark it as 'grounded'.
    5. If the segment is conversational filler, general introductory text, or general common knowledge not specifically mentioned in the sources, mark it as 'knowledge'.
    6. Ensure the sequence of 'text' in your segments, when concatenated, reconstructs the original 'Answer' exactly. DO NOT skip any words or punctuation.
    
    IMPORTANT: Be strict. If a fact is even slightly missing from the sources, mark it as 'knowledge'.
    The attribution must be exactly one of: "grounded" or "knowledge".
    """,
    output_schema=EvaluationResult,
    output_key="evaluation"
)

# 3. Setup Runner
runner = Runner(
    app_name="fact_evaluator_app",
    agent=evaluator_agent,
    session_service=InMemorySessionService(),
    artifact_service=InMemoryArtifactService(),
    auto_create_session=True
)

async def evaluate_answer(answer: str, sources: str):
    """
    Parallel Evaluation logic.
    """
    print(f"[DEBUG_EVAL] Starting evaluation for answer: {answer[:50]}...")
    prompt = f"ANSWER TO EVALUATE:\n{answer}\n\nSOURCES PROVIDED:\n{sources}"
    new_message = types.Content(role="user", parts=[types.Part(text=prompt)])
    
    session_id = f"eval_{hashlib.md5(answer.encode()).hexdigest()[:10]}"
    
    try:
        async for event in runner.run_async(
            user_id="system_eval",
            session_id=session_id,
            new_message=new_message
        ):
            # Print events for debugging
            if hasattr(event, 'content'):
                print(f"[DEBUG_EVAL] Event: {event.content}")
        
        # Retrieve the structured result from the session state
        session = await runner.session_service.get_session(
            app_name="fact_evaluator_app", 
            user_id="system_eval", 
            session_id=session_id
        )
        
        result = session.state.get("evaluation")
        if result:
            print(f"[DEBUG_EVAL] Evaluation completed with {len(result.get('segments', []))} segments")
        else:
            print(f"[DEBUG_EVAL] Evaluation result is EMPTY in session state")
            
        return result
    except Exception as e:
        print(f"[DEBUG_EVAL] ERROR in evaluator: {str(e)}")
        raise e
