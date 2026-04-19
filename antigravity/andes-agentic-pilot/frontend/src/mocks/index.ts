/* =============================================================================
 * mocks/index.ts — Master re-export for Andesia demo
 *
 * Single source of truth para que los componentes UI importen mocks así:
 *
 *   import { ALL_PERSONAS, PERSONA_MARIA, ANDESIA_DEMO_CONVERSATION } from '@/mocks';
 *
 * En vez de:
 *
 *   import { ALL_PERSONAS, PERSONA_MARIA } from '@/mocks/personas';
 *   import { ANDESIA_DEMO_CONVERSATION } from '@/mocks/agentChat';
 *
 * ----------------------------------------------------------------------------
 * Estructura del módulo:
 *   01. PERSONAS        — quiénes son los afiliados ficticios
 *   02. PRODUCTOS       — créditos, beneficios, seguros, convenios, hoteles, macro
 *   03. SUCURSALES      — geografía CCLA (26 puntos representativos)
 *   04. AGENT CHAT      — conversaciones multi-agente ADK con razonamiento expuesto
 *   05. RECOMMENDATIONS — feed de tarjetas Vitrina (lógica del recomendador)
 *   06. DOCUMENT AI     — extracción Document AI sobre liquidaciones, licencias, cédulas
 *   07. VOICE           — sesiones Live API (web/app/video) con OCR multimodal
 *   08. CREDIT COACH    — análisis financiero ReAct + DTI + escenarios
 *   09. PHISHING        — detector con 4 casos reales chilenos
 *   10. NOTEBOOKLM      — episodios AndesTV (cinemático + podcast 2 voces)
 *   11. ANDES INSIGHTS  — Conversational Analytics: 120 transactions + 6 NL queries
 *   12. VITRINA IA      — 6 cards Nano Banana Pro / Veo 3.1 con prompts y branding
 *   13. SEARCH          — 42 sugerencias autocomplete con intent + chat trigger
 *   14. IDIOMAS         — 6 idiomas (incl. mapudungun, aimara, creole), 18 keys
 * ============================================================================= */

/* === 01. PERSONAS ============================================================ */
export {
  ALL_PERSONAS,
  PERSONA_MARIA,
  PERSONA_RODRIGO,
  PERSONA_PATRICIA,
  PERSONA_JOSE_PYME,
  PERSONA_VALENTINA_BECA,
  PERSONA_DIEGO_PADRE,
  getPersonaById,
  getPersonaByRut,
} from './personas';
export type {
  Persona,
  CargaFamiliar,
  ProductoContratado,
  SegmentoCCLA,
  CanalPreferido,
} from './personas';

/* === 02. PRODUCTOS =========================================================== */
export {
  // créditos
  ALL_CREDITOS,
  CREDITO_UNIVERSAL,
  CREDITO_SOCIAL_PENSIONADOS,
  CREDITO_SALUD,
  CREDITO_CONSOLIDACION,
  CREDITO_EDUCACION,
  CREDITO_TAPP,
  // beneficios
  ALL_BENEFICIOS,
  BENEFICIO_BODAS_ORO,
  BENEFICIO_BONO_ESCOLAR,
  BENEFICIO_ASIGNACION_FAMILIAR,
  BENEFICIO_SUBSIDIO_NACIMIENTO,
  BENEFICIO_SUBSIDIO_DEFUNCION,
  BENEFICIO_BECAS_ESTUDIO,
  BENEFICIO_APORTE_FAMILIAR_PERMANENTE,
  BENEFICIO_SUBSIDIO_HABITACIONAL,
  BENEFICIO_PROGRAMA_CUIDADORES,
  BENEFICIO_DENTAL_URGENCIA,
  BENEFICIO_TURISMO_BONIFICADO,
  // seguros, convenios, hoteles
  ALL_SEGUROS,
  ALL_CONVENIOS,
  ALL_HOTELES_CLA,
  // macro
  DATOS_MACRO_ABR_2026,
} from './productos';
export type {
  Credito,
  Beneficio,
  SeguroProducto,
  Convenio,
  HotelClaTurismo,
  DatosMacro,
  Moneda,
  RangoMonto,
  RangoPlazo,
  Tasa,
} from './productos';

/* === 03. SUCURSALES ========================================================== */
export {
  SUCURSALES,
  getSucursalById,
  getSucursalesByRegion,
  getSucursalesByComuna,
} from './sucursales';
export type {
  Sucursal,
  HorarioSemana,
  RegionChile,
} from './sucursales';

/* === 04. AGENT CHAT (multi-agent ADK) ======================================== */
export {
  ANDESIA_DEMO_CONVERSATION,
  RODRIGO_PARTO_CONVERSATION,
  PATRICIA_DEFUNCION_CONVERSATION,
  ALL_CONVERSATIONS,
} from './agentChat';
export type {
  Turn,
  ReasoningStep,
  ToolCall,
  Citation,
  Handoff,
  TurnRole,
  AgentColor,
} from './agentChat';

/* === 05. RECOMMENDATIONS ===================================================== */
export {
  RECOMMENDATIONS_MARIA,
  RECOMMENDATIONS_RODRIGO,
  RECOMMENDATIONS_BY_PERSONA,
  getRecommendationsForPersona,
} from './recommendations';
export type {
  RecommendationCard,
  CategoriaRecomendacion,
  RelevanciaTier,
} from './recommendations';

/* === 06. DOCUMENT AI ========================================================= */
export {
  ALL_PROCESSED_DOCUMENTS,
  LIQUIDACION_PENSION_MARIA,
  LICENCIA_MEDICA_DIEGO,
  CEDULA_VALENTINA,
} from './documentAI';
export type {
  ProcessedDocument,
  ExtractedEntity,
  BoundingBox,
  DocumentMetadata,
  DocumentAIProcessing,
  FormAutoFillField,
} from './documentAI';

/* === 07. VOICE TRANSCRIPTS =================================================== */
export {
  ALL_VOICE_SESSIONS,
  VOICE_SESSION_MARIA_CONFIRM,
  VOICE_SESSION_PATRICIA_LICENCIA_VIDEO,
  VOICE_SESSION_DIEGO_SALDO,
} from './voiceTranscript';
export type {
  VoiceSession,
  VoiceTurn,
  VoiceTurnSpeaker,
  Idioma,
  AudioMetadata,
  FrameCaption,
} from './voiceTranscript';

/* === 08. CREDIT COACH (financial ReAct) ====================================== */
export {
  ALL_COACH_ANALYSES,
  COACH_ANALYSIS_MARIA,
  COACH_ANALYSIS_DIEGO_ADELANTO,
} from './creditCoach';
export type {
  CreditCoachAnalysis,
  ObligacionActual,
  DtiCalculation,
  EscenarioComparado,
  CoachReasoningStep,
} from './creditCoach';

/* === 09. PHISHING DETECTOR =================================================== */
export {
  PHISHING_CASES,
  getPhishingCaseById,
  getPhishingByChannel,
} from './phishingDetector';
export type {
  PhishingAnalysis,
  RedFlag,
  PhishingVerdict,
  PhishingChannel,
} from './phishingDetector';

/* === 10. NOTEBOOKLM (AndesTV) ================================================ */
export {
  ALL_ANDESTV_EPISODES,
  EPISODE_RESUMEN_SEMANAL_MARIA,
  EPISODE_PODCAST_CONSOLIDACION,
  EPISODE_BONO_BODAS_ORO_SHORT,
} from './notebookLM';
export type {
  AndesTVEpisode,
  EpisodeFormat,
  EpisodeAudience,
  PodcastSpeaker,
  TranscriptLine,
  SourceDocument,
} from './notebookLM';

/* === 11. ANDES INSIGHTS (Conversational Analytics) =========================== */
export {
  TRANSACTIONS,
  INSIGHT_QUERIES,
  KPI_CARDS_ABRIL_2026,
  getInsightById,
  getTransactionsByProducto,
  getTransactionsByRegion,
  getTransactionsByDateRange,
} from './andesInsights';
export type {
  Transaction,
  ProductoTipo,
  CanalAtencion,
  ChartSpec,
  InsightQuery,
  KpiCard,
} from './andesInsights';

/* === 13. SEARCH SUGGESTIONS ================================================== */
export {
  SEARCH_SUGGESTIONS,
  AUTOCOMPLETE_DEMOS,
  getTopSuggestions,
  getSuggestionsByIntent,
  getConversationalSuggestions,
} from './searchSuggestions';
export type {
  SearchSuggestion,
  SearchIntent,
  AutocompleteResult,
} from './searchSuggestions';

/* === 14. IDIOMAS ============================================================= */
export {
  LANGUAGES,
  TRANSLATIONS,
  GLOSARIO_CCLA,
  t,
  getLanguageByCode,
  getProductionLanguages,
} from './idiomas';
export type {
  Language,
  LanguageCode,
  TranslationKey,
  TranslationsMap,
  GlosarioTerm,
} from './idiomas';

/* =============================================================================
 * Convenience: storyline anchor (for the Monday April 20 keynote)
 * The "María González" thread connects: PERSONA → RECOMMENDATIONS →
 *   AGENT CHAT → DOCUMENT AI → VOICE → CREDIT COACH → VITRINA IA → NOTEBOOKLM
 *
 * NOTA: los IDs específicos referencian los registros principales del demo.
 * ============================================================================= */
export const KEYNOTE_STORYLINE = {
  persona_export: 'PERSONA_MARIA',
  conversation_export: 'ANDESIA_DEMO_CONVERSATION',
  vitrina_card_ids: ['vit-001', 'vit-002', 'vit-003'],
  episode_export: 'EPISODE_RESUMEN_SEMANAL_MARIA',
  document_export: 'LIQUIDACION_PENSION_MARIA',
  voice_session_export: 'VOICE_SESSION_MARIA_CONFIRM',
  coach_analysis_export: 'COACH_ANALYSIS_MARIA',
  recommendations_export: 'RECOMMENDATIONS_MARIA',
} as const;
