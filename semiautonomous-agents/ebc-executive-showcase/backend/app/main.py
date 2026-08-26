import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import PROJECT_ID, REGION, MODEL_NAME, PORT, HOST
from app.routes import health, voice, creative, swarm

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("ebc_backend")

app = FastAPI(
    title="EBC Executive AI Transformation Showcase API",
    description="High performance executive backend for boardroom 100-inch display",
    version="1.0.0"
)

# Enable CORS for local and cross-origin access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(health.router)
app.include_router(voice.router)
app.include_router(creative.router)
app.include_router(swarm.router)

@app.on_event("startup")
async def startup_event():
    logger.info("==================================================================")
    logger.info("  EBC Executive AI Transformation Showcase - Backend Started")
    logger.info(f"  GCP Project: {PROJECT_ID} | Region: {REGION}")
    logger.info(f"  Gemini Model: {MODEL_NAME}")
    logger.info(f"  Server Listening: http://{HOST}:{PORT}")
    logger.info("==================================================================")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=HOST, port=PORT, reload=True)
