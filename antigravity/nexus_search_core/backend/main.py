from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from dotenv import load_dotenv
from evaluator_agent import evaluate_answer # Corrected local import

# Load environment variables
load_dotenv(dotenv_path="../.env")

app = FastAPI(title="Nexus Search Core API")

# Classes for the new endpoint
class EvalRequest(BaseModel):
    answer: str
    sources: str

# Enable CORS for the frontend
# ... existing CORS middle ware ...
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "nexus_search_core"}

@app.post("/search")
async def search(query: str):
    return {"query": query, "results": []}

@app.post("/evaluate")
async def evaluate(req: EvalRequest):
    """
    Parallel Evaluation Endpoint.
    Invokes the ADK Evaluator Agent to perform fact-attribution analysis.
    """
    try:
        result = await evaluate_answer(req.answer, req.sources)
        if not result:
            raise HTTPException(status_code=500, detail="Evaluation failed to produce results")
        return result
    except Exception as e:
        print(f"Error in evaluate: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
