from fastapi import FastAPI
from pydantic import BaseModel
from main import run_verity_engine

app = FastAPI(title="Verity Nexus Engine API")

class QueryRequest(BaseModel):
    query: str
    user_id: str = "default_user"

@app.post("/run")
async def run_engine(request: QueryRequest):
    results = await run_verity_engine(request.query, request.user_id)
    # Filter for text responses to keep it simple for the UI
    response_text = ""
    for event in results:
        if hasattr(event, "text") and event.text:
            response_text = event.text
            
    return {"response": response_text, "events": [str(e) for e in results]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
