from fastapi import FastAPI, HTTPException, Request
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
async def evaluate(request: Request):
    data = await request.json()
    answer = data.get("answer")
    sources = data.get("sources")
    citations = data.get("citations", [])
    
    if not answer or not sources:
        return {"error": "Missing answer or sources"}
    
    try:
        result = await evaluate_answer(answer, sources, citations)
        return result
    except Exception as e:
        print(f"Evaluation Error: {str(e)}")
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
