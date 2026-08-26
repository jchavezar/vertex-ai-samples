from fastapi import APIRouter
from app.config import PROJECT_ID, REGION, MODEL_NAME

router = APIRouter(tags=["Health"])

@router.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "ebc-executive-showcase",
        "project": PROJECT_ID,
        "region": REGION,
        "model": MODEL_NAME
    }

@router.get("/api/health")
def api_health_check():
    return {
        "status": "ok",
        "service": "ebc-executive-showcase",
        "project": PROJECT_ID,
        "region": REGION,
        "model": MODEL_NAME
    }
