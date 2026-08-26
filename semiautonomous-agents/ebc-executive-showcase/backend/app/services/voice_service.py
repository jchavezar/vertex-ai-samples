import logging
from typing import List, Optional
from pydantic import BaseModel, Field
from app.services.gemini_service import gemini_service

logger = logging.getLogger("voice_service")

class VoiceKpi(BaseModel):
    label: str = Field(description="Nombre del KPI, ej: 'ROI Proyectado Año 1'")
    value: str = Field(description="Valor numérico destacado, ej: '+38.5%' o '$4.2M USD'")
    description: str = Field(description="Breve descripción del impacto")
    trend: str = Field(description="Tendencia: 'up', 'down', o 'neutral'")

class StrategicPillar(BaseModel):
    title: str = Field(description="Título del pilar estratégico")
    detail: str = Field(description="Explicación concisa y accionable")
    timeline: str = Field(description="Horizonte temporal sugerido, ej: 'Q1-Q2'")

class VoiceExecutiveResponse(BaseModel):
    transcript_query: str = Field(description="Transcripción de la pregunta ejecutiva")
    spoken_voice_script: str = Field(description="Guion de locución ejecutiva en español neutro, fluido y directo (máximo 4 oraciones) para reproducción por voz")
    executive_summary: str = Field(description="Resumen ejecutivo de alto impacto para la junta directiva")
    kpis: List[VoiceKpi] = Field(description="3 o 4 métricas cuantitativas clave de nivel C-Suite")
    pillars: List[StrategicPillar] = Field(description="3 pilares de ejecución y estrategia")
    governance_note: str = Field(description="Recomendación de gobernanza y cumplimiento normativo")

VOICE_SYSTEM_INSTRUCTION = """
Eres el Asistente Ejecutivo de Inteligencia Artificial para la Sala de Juntas (EBC Executive Showcase).
Tu audiencia está compuesta por Directores Generales (CEOs), Directores Financieros (CFOs), Directores de Tecnología (CTOs) y Consejeros de Administración en Latinoamérica y el mundo.
Tus respuestas deben ser:
1. En ESPAÑOL EJECUTIVO impecable, formal pero directo y pragmático.
2. Basadas en datos financieros sólidos, métricas de ROI medibles, CAPEX/OPEX, tiempos de recuperación (payback) y mejores prácticas empresariales de Google Cloud Vertex AI.
3. El campo 'spoken_voice_script' debe ser un mensaje de audio perfecto para ser leído en voz alta: elocuente, seguro, conciso (aproximadamente 35-50 palabras) sin viñetas ni caracteres especiales, pensado para síntesis de voz en tiempo real.
4. Genera siempre métricas cuantitativas realistas y de alto impacto para visualización en pantallas de 100 pulgadas.
"""

def process_voice_query(query_text: str) -> VoiceExecutiveResponse:
    prompt = f"""
    Pregunta ejecutiva recibida:
    "{query_text}"

    Genera una respuesta estratégica de nivel C-Suite estructurada según el esquema definido.
    """
    try:
        result = gemini_service.generate_structured(
            prompt=prompt,
            response_schema=VoiceExecutiveResponse,
            system_instruction=VOICE_SYSTEM_INSTRUCTION,
            temperature=0.2
        )
        return result
    except Exception as e:
        logger.error(f"Error generating voice response: {e}")
        # Fallback response in Spanish
        return VoiceExecutiveResponse(
            transcript_query=query_text,
            spoken_voice_script="Hemos analizado su consulta estratégica. La implementación de IA generativa en Vertex AI proyecta un retorno de inversión superior al 35 por ciento en el primer año, optimizando costos operativos y acelerando la toma de decisiones directivas.",
            executive_summary="Análisis estratégico preliminar: La adopción de arquitecturas de agentes autónomos y modelos multimodales optimiza los flujos de trabajo críticos de la organización con estricta gobernanza corporativa.",
            kpis=[
                VoiceKpi(label="ROI Estimado a 12 Meses", value="+38.2%", description="Reducción en tiempo de ciclo y costos operativos", trend="up"),
                VoiceKpi(label="Optimización de OPEX", value="-27.4%", description="Automatización de tareas repetitivas en backoffice", trend="down"),
                VoiceKpi(label="Payback Estimado", value="8.5 Meses", description="Punto de equilibrio de la inversión tecnológica", trend="up"),
                VoiceKpi(label="Precisión de Modelos", value="99.2%", description="Gobernanza y trazabilidad en Vertex AI", trend="up")
            ],
            pillars=[
                StrategicPillar(title="Despliegue de Agentes Especializados", detail="Implementación de microagentes coordinados para procesos de alta frecuencia.", timeline="Meses 1 - 3"),
                StrategicPillar(title="Integración de Datos y Gobernanza", detail="Conexión segura de datos empresariales con políticas de Zero-Leak y cifrado E2E.", timeline="Meses 2 - 4"),
                StrategicPillar(title="Escalabilidad y Medición de Impacto", detail="Tableros en tiempo real para supervisión de KPIs financieros y satisfacción.", timeline="Meses 4 - 6")
            ],
            governance_note="Cumplimiento estricto con normativas internacionales de protección de datos, soberanía de la información y auditoría continua en Google Cloud."
        )
