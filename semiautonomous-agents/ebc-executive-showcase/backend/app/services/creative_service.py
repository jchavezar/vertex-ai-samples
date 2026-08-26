import logging
from typing import List, Optional
from pydantic import BaseModel, Field
from app.services.gemini_service import gemini_service

logger = logging.getLogger("creative_service")

class StoryboardPanel(BaseModel):
    panel_number: int = Field(description="Número de panel del 1 al 4")
    title: str = Field(description="Título conceptual del panel")
    visual_description: str = Field(description="Descripción visual cinematográfica de alta definición para el render/imagen")
    voiceover_script: str = Field(description="Guion de locución en español para este panel (5-8 segundos)")
    duration_seconds: int = Field(description="Duración en segundos del panel, ej: 6")
    on_screen_text: str = Field(description="Texto destacado en pantalla, conciso y de alto impacto")
    artwork_theme: str = Field(description="Tema visual: 'quantum-finance', 'global-network', 'ai-future', 'executive-growth'")
    visual_badge: str = Field(description="Categoría, ej: 'GANCHO', 'DISRUPCIÓN', 'ESCALA', 'ACCIÓN'")

class ChannelCopy(BaseModel):
    channel: str = Field(description="Canal, ej: 'LinkedIn C-Suite', 'Instagram/TikTok Reel', 'Nota de Prensa'")
    format_type: str = Field(description="Formato publicitario recomendado")
    content: str = Field(description="Texto o guion completo redactado para el canal")
    target_metric: str = Field(description="Métrica objetivo esperada, ej: '3.2M Impresiones B2B'")

class FinancialProjection(BaseModel):
    roi_porcentaje: str = Field(description="ROI proyectado, ej: '+320%'")
    cac_impact: str = Field(description="Impacto en Costo de Adquisición de Clientes, ej: '-44% CAC'")
    conversion_multiplier: str = Field(description="Multiplicador de conversión, ej: '3.8x'")
    recommended_budget: str = Field(description="Presupuesto sugerido de pauta y despliegue, ej: '$85,000 USD'")
    payback_period: str = Field(description="Periodo de retorno de inversión de la campaña, ej: '45 días'")

class ExecutiveCampaign(BaseModel):
    campaign_title: str = Field(description="Título ejecutivo de la campaña publicitaria")
    central_concept: str = Field(description="Concepto creativo central unificador")
    executive_slogan: str = Field(description="Slogan de alto impacto corporativo")
    target_audience: str = Field(description="Público objetivo y segmento de mercado")
    tone_of_voice: str = Field(description="Tono de comunicación (ej: 'Vanguardista, Autorizado y Dinámico')")
    storyboard: List[StoryboardPanel] = Field(description="Storyboard secuencial de 4 paneles cinemáticos")
    channels_copy: List[ChannelCopy] = Field(description="Copy adaptado para 3 canales directivos")
    financial_projection: FinancialProjection = Field(description="Proyección financiera y de impacto de la campaña")

CREATIVE_SYSTEM_INSTRUCTION = """
Eres el Director Creativo Ejecutivo y Estratega de Marketing Global de EBC Showcase.
Tu misión es transformar cualquier iniciativa, producto o visión empresarial en una campaña multimedia integral de clase mundial.
Reglas:
1. Idioma: Español ejecutivo elegante y persuasivo.
2. Genera exactamente 4 paneles de storyboard secuenciales con una narrativa ascendente:
   - Panel 1: Gancho & Desafío (El dolor del mercado o statu quo)
   - Panel 2: Innovación & Disrupción (El salto cuántico tecnológico o de producto)
   - Panel 3: Prueba Ejecutiva & Escalabilidad (Validación con datos y alcance global)
   - Panel 4: Cierre & Llamada a la Acción (La decisión transformadora)
3. Cada panel debe tener descripciones visuales ricas, cinemáticas y con estilo estético limpio, sofisticado y moderno.
4. Genera proyecciones financieras realistas y sólidas que justifiquen el presupuesto ante el CFO.
"""

def generate_campaign(prompt_topic: str) -> ExecutiveCampaign:
    user_prompt = f"""
    Iniciativa / Producto a promocionar:
    "{prompt_topic}"

    Desarrolla la campaña publicitaria multimedia completa con 4 paneles de storyboard, copys multicanal y proyecciones de ROI.
    """
    try:
        campaign = gemini_service.generate_structured(
            prompt=user_prompt,
            response_schema=ExecutiveCampaign,
            system_instruction=CREATIVE_SYSTEM_INSTRUCTION,
            temperature=0.3
        )
        return campaign
    except Exception as e:
        logger.error(f"Error in creative campaign generation: {e}")
        # Fallback curated campaign in Spanish
        return ExecutiveCampaign(
            campaign_title="Quantum Leap: La Nueva Era de la Banca Inteligente",
            central_concept="Autonomía, Precisión y Velocidad: Redefiniendo el estándar financiero con Inteligencia Artificial generativa de Vertex AI.",
            executive_slogan="El Futuro Financiero no se espera, se lidera.",
            target_audience="Directores Generales, Inversionistas Institucionales y Clientes de Alto Patrimonio (HNWI)",
            tone_of_voice="Vanguardista, Autorizado, Cinemático y Confiable",
            storyboard=[
                StoryboardPanel(
                    panel_number=1,
                    title="La Fricción de la Banca Tradicional",
                    visual_description="Plano general cenital de una metrópoli financiera al atardecer, rascacielos iluminados con estelas de datos rojos y ámbar que representan lentitud en procesos heredados.",
                    voiceover_script="En los negocios de alta velocidad, esperar días por una decisión financiera es cosa del pasado.",
                    duration_seconds=6,
                    on_screen_text="EL COSTO DE LA LENTITUD",
                    artwork_theme="quantum-finance",
                    visual_badge="GANCHO"
                ),
                StoryboardPanel(
                    panel_number=2,
                    title="La Inteligencia Predictiva en Acción",
                    visual_description="Transición fluida a una interfaz holográfica cristalina donde algoritmos de Vertex AI analizan millones de transacciones en microsegundos, emitiendo pulsos azul cobalto y esmeralda.",
                    voiceover_script="Presentamos Quantum AI: decisiones crediticias e inversiones optimizadas en tiempo real.",
                    duration_seconds=7,
                    on_screen_text="HIPER-VELOCIDAD PREDICTIVA",
                    artwork_theme="ai-future",
                    visual_badge="DISRUPCIÓN"
                ),
                StoryboardPanel(
                    panel_number=3,
                    title="Escala Global y Seguridad Blindada",
                    visual_description="Vista orbital de la Tierra con redes interconectadas protegidas por un escudo de seguridad criptográfica multicapa en tonos blanco ártico y platino.",
                    voiceover_script="Protección de nivel bancario con infraestructura soberana de Google Cloud.",
                    duration_seconds=6,
                    on_screen_text="SEGURIDAD Y ESCALA GLOBAL",
                    artwork_theme="global-network",
                    visual_badge="ESCALA"
                ),
                StoryboardPanel(
                    panel_number=4,
                    title="Liderazgo y Transformación Definitiva",
                    visual_description="Director ejecutivo en un centro de comando iluminado con luz natural, mirando un dashboard de crecimiento exponencial mientras el logotipo institucional se materializa con brillo metálico.",
                    voiceover_script="Transforme su institución hoy. El futuro financiero no se espera, se lidera.",
                    duration_seconds=7,
                    on_screen_text="ACTIVE EL FUTURO HOY",
                    artwork_theme="executive-growth",
                    visual_badge="ACCIÓN"
                )
            ],
            channels_copy=[
                ChannelCopy(
                    channel="LinkedIn C-Suite",
                    format_type="Artículo de Liderazgo de Pensamiento + Video Reel 16:9",
                    content="La ventaja competitiva ya no reside en acumular datos, sino en la velocidad para transformarlos en capital estratégico. En el EBC Showcase demostramos cómo la IA autónoma reduce el ciclo operativo en 68% garantizando gobernanza total. ¿Está su junta directiva lista para el siguiente salto? #LiderazgoIA #VertexAI #Fintech2026",
                    target_metric="2.4M Alcance Orgánico Directivo"
                ),
                ChannelCopy(
                    channel="Instagram / TikTok Reel",
                    format_type="Reel Vertical 9:16 de Alta Tensión con Subtítulos Dinámicos",
                    content="[Voz potente] '¿Y si tu banco pudiera predecir el mercado antes del cierre de campana?' 📊⚡ Mira cómo los agentes autónomos de Google Cloud revolucionan la toma de decisiones en 6 segundos. Link en bio para el informe ejecutivo.",
                    target_metric="850K Reproducciones / 14% CTR"
                ),
                ChannelCopy(
                    channel="Nota de Prensa Corporativa",
                    format_type="Comunicado Oficial para Medios Financieros (Bloomberg / Expansión)",
                    content="CIUDAD DE MÉXICO & NUEVA YORK — Anunciamos el despliegue del nuevo ecosistema de agentes autónomos EBC impulsado por Google Cloud Vertex AI, marcando un hito en eficiencia operativa, personalización y retorno financiero para el sector empresarial.",
                    target_metric="Top Tier Media Coverage"
                )
            ],
            financial_projection=FinancialProjection(
                roi_porcentaje="+345%",
                cac_impact="-38.5%",
                conversion_multiplier="4.2x",
                recommended_budget="$95,000 USD",
                payback_period="42 días"
            )
        )
