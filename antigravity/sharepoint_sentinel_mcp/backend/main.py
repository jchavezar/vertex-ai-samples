import os
import json
import logging
import asyncio
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from classifier_agent import main as run_classifier

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SharePointSentinelAPI")

app = FastAPI(title="SharePoint Sentinel API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

REPORT_FILE = "classification_report.json"
STATE_FILE = "sync_state.json"

class SyncStatus:
    is_running = False
    last_run = None
    error = None

status = SyncStatus()

@app.get("/api/health")
def health_check():
    return {"status": "ok", "app": "sharepoint_sentinel_mcp"}

@app.get("/api/results")
def get_results():
    if not os.path.exists(REPORT_FILE):
        return []
    try:
        with open(REPORT_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error reading report: {e}")
        return []

@app.get("/api/status")
def get_status():
    return {
        "is_running": status.is_running,
        "last_run": status.last_run,
        "error": status.error
    }

async def run_sync_task():
    status.is_running = True
    status.error = None
    try:
        await run_classifier()
        status.last_run = "Success"
    except Exception as e:
        logger.error(f"Sync task failed: {e}")
        status.error = str(e)
        status.last_run = "Failed"
    finally:
        status.is_running = False

@app.post("/api/sync")
async def trigger_sync(background_tasks: BackgroundTasks):
    if status.is_running:
        return {"message": "Sync already in progress"}
    
    background_tasks.add_task(run_sync_task)
    return {"message": "Sync started in background"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
