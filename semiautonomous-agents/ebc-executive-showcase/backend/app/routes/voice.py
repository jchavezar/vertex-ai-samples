from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List
from app.services.voice_service import process_voice_query, VoiceExecutiveResponse

router = APIRouter(prefix="/api/voice", tags=["Voice Assistant"])

class VoiceQueryRequest(BaseModel):
    query: str = Field(..., description="Pregunta ejecutiva expresada por voz o texto")

EXECUTIVE_SCENARIOS = [
    {
        "id": "roi-automation",
        "title": "ROI de Automatización de Clientes",
        "query": "¿Cuál es el ROI estimado y el periodo de amortización al automatizar la atención a clientes con agentes multimodales en Vertex AI?",
        "category": "Financiero & Operaciones",
        "badge": "ROI +38%"
    },
    {
        "id": "premium-product",
        "title": "Estrategia para Producto Premium",
        "query": "Diseña una campaña y estrategia de posicionamiento para nuestro nuevo producto financiero de ultra alto patrimonio.",
        "category": "Estrategia & Producto",
        "badge": "C-Suite"
    },
    {
        "id": "brazil-expansion",
        "title": "Expansión al Mercado Brasileño",
        "query": "Evalúa el impacto financiero, regulatorio y operativo de expandir nuestras operaciones fintech hacia el mercado de Brasil en 2026.",
        "category": "Expansión Internacional",
        "badge": "M&A / Escala"
    },
    {
        "id": "supply-chain-ai",
        "title": "Transformación de Cadena de Suministro",
        "query": "¿Cómo impacta la adopción de modelos de razonamiento continuo en la optimización de inventarios y logística de retail?",
        "category": "Cadena de Suministro",
        "badge": "-28% Costo"
    },
    {
        "id": "governance-security",
        "title": "Gobernanza y Mitigación de Riesgos",
        "query": "¿Qué marco de gobernanza, soberanía de datos y ciberseguridad debemos implementar para cumplir con la regulación bancaria internacional?",
        "category": "Gobernanza & Riesgo",
        "badge": "Zero-Leak"
    }
]

@router.get("/scenarios")
def get_voice_scenarios():
    return {"scenarios": EXECUTIVE_SCENARIOS}

@router.post("/query", response_model=VoiceExecutiveResponse)
def handle_voice_query(request: VoiceQueryRequest):
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="La consulta no puede estar vacía.")
    return process_voice_query(request.query)
