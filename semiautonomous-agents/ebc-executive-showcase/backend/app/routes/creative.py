from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.services.creative_service import generate_campaign, ExecutiveCampaign

router = APIRouter(prefix="/api/creative", tags=["Creative Studio"])

class CampaignRequest(BaseModel):
    topic: str = Field(..., description="Tema o iniciativa empresarial para la campaña")

CREATIVE_TEMPLATES = [
    {
        "id": "black-quantum",
        "title": "Tarjeta Black Quantum & Private Wealth",
        "topic": "Lanzamiento exclusivo de la Tarjeta Black Quantum con concierge autónomo impulsado por Gemini 3.7 y beneficios exclusivos para banca privada.",
        "industry": "Banca Privada & Wealth",
        "impact": "Captación HNWI"
    },
    {
        "id": "cloud-enterprise",
        "title": "Expansión Cloud Soberana LATAM",
        "topic": "Campaña B2B dirigida a directores de tecnología para migrar infraestructuras core a centros de datos sostenibles y soberanos de Google Cloud.",
        "industry": "Cloud & Enterprise Tech",
        "impact": "+$12M Pipeline"
    },
    {
        "id": "ai-loyalty",
        "title": "Programa de Lealtad Hiper-Personalizado",
        "topic": "Ecosistema de recompensas dinámicas en tiempo real con IA multimodal para más de 10 millones de usuarios de retail y servicios.",
        "industry": "Retail & Consumo Masivo",
        "impact": "+45% Retención"
    },
    {
        "id": "sustainable-invest",
        "title": "Fondo de Inversión Sostenible ESG 2026",
        "topic": "Iniciativa de inversión verde auditada en blockchain y analizada con modelos de inteligencia artificial para energías limpias en América Latina.",
        "industry": "Finanzas Verdes / ESG",
        "impact": "Triple Impacto"
    }
]

@router.get("/templates")
def get_campaign_templates():
    return {"templates": CREATIVE_TEMPLATES}

@router.post("/generate", response_model=ExecutiveCampaign)
def handle_generate_campaign(request: CampaignRequest):
    if not request.topic.strip():
        raise HTTPException(status_code=400, detail="El tema de campaña no puede estar vacío.")
    return generate_campaign(request.topic)
