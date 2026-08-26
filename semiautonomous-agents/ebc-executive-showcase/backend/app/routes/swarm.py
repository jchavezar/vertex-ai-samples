from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from app.services.swarm_service import execute_swarm_stream, AGENTS_CONFIG

router = APIRouter(prefix="/api/swarm", tags=["Agent Swarm"])

class SwarmRequest(BaseModel):
    mandate: str = Field(..., description="Mandato de la junta directiva para el enjambre de agentes")

SWARM_MANDATES = [
    {
        "id": "mandate-1",
        "title": "Adquisición de Fintech Competidora",
        "mandate": "Evaluar la adquisición hostil o amistosa de una fintech de pagos transfronterizos en Sudamérica por $150M USD.",
        "complexity": "Nivel C-Suite",
        "lanes": 4
    },
    {
        "id": "mandate-2",
        "title": "Transformación Total a IA Operativa",
        "mandate": "Aprobar el plan maestro de migración de todas las operaciones de atención, análisis crediticio y marketing a agentes autónomos de Google Cloud en un horizonte de 18 meses.",
        "complexity": "Transformación Core",
        "lanes": 4
    },
    {
        "id": "mandate-3",
        "title": "Lanzamiento de Banco Digital 100% Autónomo",
        "mandate": "Diseñar la estrategia de entrada, presupuesto financiero, arquitectura de seguridad y campaña de lanzamiento de un nuevo neobanco para generación Z y PyMEs.",
        "complexity": "Nuevo Negocio",
        "lanes": 4
    },
    {
        "id": "mandate-4",
        "title": "Optimización Global de Costos con IA Soberana",
        "mandate": "Rediseñar la estructura de costes de la organización para reducir un 30% de OPEX protegiendo el 100% de la fuerza laboral mediante reentrenamiento con copilotos de IA.",
        "complexity": "Eficiencia & Talento",
        "lanes": 4
    }
]

@router.get("/agents")
def get_agents():
    return {"agents": AGENTS_CONFIG}

@router.get("/mandates")
def get_mandates():
    return {"mandates": SWARM_MANDATES}

@router.post("/stream")
async def stream_swarm_execution(request: SwarmRequest):
    if not request.mandate.strip():
        raise HTTPException(status_code=400, detail="El mandato no puede estar vacío.")
    
    return StreamingResponse(
        execute_swarm_stream(request.mandate),
        media_type="text/event-stream"
    )
