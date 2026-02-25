from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import agent_adk_tool
import agent_custom_client
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Vertex AI Search Agent Comparison API")

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    query: str

class AgentResponse(BaseModel):
    response: str
    logs: str

class CompareResponse(BaseModel):
    adk: AgentResponse
    custom: AgentResponse

@app.post("/api/compare", response_model=CompareResponse)
async def compare_agents(request: QueryRequest):
    logger.info(f"Received query: {request.query}")
    
    # Run ADK Agent
    try:
        adk_result = await agent_adk_tool.run_query(request.query)
    except Exception as e:
        logger.error(f"Error running ADK agent: {e}")
        adk_result = {"response": "Error executing ADK agent", "logs": str(e)}

    # Run Custom Client Agent
    try:
        custom_result = await agent_custom_client.run_query(request.query)
    except Exception as e:
        logger.error(f"Error running Custom Client agent: {e}")
        custom_result = {"response": "Error executing Custom Client agent", "logs": str(e)}

    return {
        "adk": adk_result,
        "custom": custom_result
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
