from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import uvicorn

# Set GCP parameters explicitly
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "TRUE"
os.environ["GOOGLE_CLOUD_PROJECT"] = "vtxdemos"
os.environ["GOOGLE_CLOUD_LOCATION"] = "us-central1"

from topology_1_single_agent import execute_query_t1
from topology_2_workflow_agents import execute_query_t2

app = FastAPI()

# Allow connections from Vite Dev Server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5199", "http://127.0.0.1:5199"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    query: str
    topology: str

@app.post("/chat")
async def chat(payload: ChatRequest):
    query = payload.query
    topology = payload.topology
    
    if topology == "t1":
        response, elapsed = execute_query_t1(query)
        router_decision = "N/A (Monolithic Agent has access to all tools)"
    else:
        response, elapsed, router_decision = execute_query_t2(query)
        
    return {
        "response": response,
        "latency": elapsed,
        "router_decision": router_decision
    }

if __name__ == "__main__":
    # Serve on port 8099
    uvicorn.run(app, host="0.0.0.0", port=8099)
