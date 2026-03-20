import asyncio
import logging
from typing import Any, Dict, List
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json

app = FastAPI(title="Observability Nexus Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("observability_nexus")

# Maintain active websocket connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"Client connected. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"Client disconnected. Total: {len(self.active_connections)}")

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Error sending message to client: {e}")

manager = ConnectionManager()

@app.post("/ingest")
async def ingest_telemetry(request: Request):
    """
    Ingests arbitrary telemetry (JSON) and broadcasts it immediately to all connected UI clients.
    """
    try:
        data = await request.json()
    except Exception:
        body = await request.body()
        data = {"raw": body.decode("utf-8")}
        
    logger.info(f"Ingested telemetry: {list(data.keys()) if isinstance(data, dict) else 'raw'}")
    
    # Broadcast to all UI connections
    payload = json.dumps(data)
    await manager.broadcast(payload)
    return {"status": "ok"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # We don't expect much *from* the UI right now, just keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.get("/health")
def health():
    return {"status": "ok", "app": "observability_nexus"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8145, reload=False)
