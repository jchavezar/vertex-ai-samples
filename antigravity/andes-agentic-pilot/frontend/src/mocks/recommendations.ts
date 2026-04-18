/* =============================================================================
 * mocks/recommendations.ts — "Beneficios para ti" carrusel personalizado
 *
 * Recomendaciones generadas hipotéticamente por:
 *   Vector Search + Recommendations AI + segmentos BigQuery
 *
 * Para María González (persona-001) — mezcla de:
 *   - alta relevancia (Bono Bodas Oro madre, dental urgencia)
 *   - aspiracional (turismo Pucón, Universidad de la Experiencia)
 *   - financiera (crédito consolidación)
 *
 * Estructura inspirada en:
 *   - Spotify "Made for You" rationale strings
 *   - Netflix "Because you watched X" copy patterns
 *   - cajalosandes.cl Guía de Beneficios
 * ============================================================================= */

import type { Persona } from './personas';

export type CategoriaRecomendacion =
  | 'Crédito'
  | 'Beneficio'
  | 'Salud'
  | 'Recreación'
  | 'Educación'
  | 'Apoyo Social'
  | 'Tapp'
  | 'Seguro';

export type RelevanciaTier = 'critica' | 'alta' | 'media' | 'aspiracional';

export interface RecommendationCard {
  id: string;
  titulo: string;
  subtitulo: string;
  categoria: CategoriaRecomendacion;
  monto_estimado_clp?: number;
  monto_display?: string; // "$300.000" o "Hasta 50% dcto"
  porque_te_lo_recomendamos: string; // 1 line, debe citar dato del perfil
  cta_label: string;
  cta_destino: string;
  imagen: string;
  badge?: 'Para tu mamá' | 'Para tu nieta' | 'Para ti' | 'Tu sucursal' | 'Solo abril';
  tier: RelevanciaTier;
  fundamento_data: string[]; // explicación técnica para Inspector
  relevance_score: number; // 0–1
  generado_por: 'vector_search' | 'collaborative_filter' | 'rule_based' | 'memory_bank';
}

/* ─────────────────────────────────────────────────────────────────────────── */
/* === Recomendaciones para María González (persona-001) ===================  */
/* ─────────────────────────────────────────────────────────────────────────── */

export const RECOMMENDATIONS_MARIA: RecommendationCard[] = [
  {
    id: 'rec-maria-bodas-oro',
    titulo: 'Bono Bodas de Oro para tus padres',
    subtitulo: '50 años de matrimonio · julio 2026',
    categoria: 'Apoyo Social',
    monto_estimado_clp: 300_000,
    monto_display: '$300.000',
    porque_te_lo_recomendamos:
      'Tu mamá Carmen y tu papá cumplen 50 años de matrimonio el 12 de julio. Su tramo del Registro Social de Hogares los hace elegibles, y la Caja te ayuda a tramitarlo gratis.',
    cta_label: 'Iniciar trámite',
    cta_destino: '/beneficios/bono-bodas-de-oro/iniciar',
    imagen: '/mocks/img/rec-bodas-oro.jpg',
    badge: 'Para tu mamá',
    tier: 'critica',
    fundamento_data: [
      'persona-001.cargas_familiares.madre.fecha_matrimonio = 1976-07-12',
      'persona-001.cargas_familiares.madre.rsh_tramo = 60%',
      'beneficio:ben-bodas-oro elegibilidad calculada via Ley 20.595 art. 3',
    ],
    relevance_score: 0.97,
    generado_por: 'rule_based',
  },
  {
    id: 'rec-maria-consolidacion',
    titulo: 'Consolida tu deuda en una sola cuota',
    subtitulo: 'Bajaría tu tasa promedio de 31,7% a 18,9%',
    categoria: 'Crédito',
    monto_estimado_clp: 4_500_000,
    monto_display: 'Cuota desde $142.300',
    porque_te_lo_recomendamos:
      'Detectamos vía REDEC que tienes 2 deudas externas (BancoEstado + Falabella) sumando $4.5M con cuota total $147.300. Consolidando ahorras y simplificas.',
    cta_label: 'Simular consolidación',
    cta_destino: '/creditos/consolidacion/simular',
    imagen: '/mocks/img/rec-consolidacion.jpg',
    badge: 'Para ti',
    tier: 'critica',
    fundamento_data: [
      'REDEC.deudas_vigentes (Ley 21.680) consultadas con consentimiento 2025-09-12',
      'CAE preferente pensionados 18.9% < CAE ponderado actual 31.7%',
    ],
    relevance_score: 0.95,
    generado_por: 'rule_based',
  },
  {
    id: 'rec-maria-pucon-nieta',
    titulo: 'Hotel Caja Los Andes Pucón con tarifa afiliada',
    subtitulo: 'Plan abuela + nieta · 3 noches base',
    categoria: 'Recreación',
    monto_estimado_clp: 237_000,
    monto_display: '$79.000/noche (43% bajo público)',
    porque_te_lo_recomendamos:
      'Consultaste Pucón en marzo y mencionaste a tu nieta Sofía (8). Tenemos cupo entre mayo-junio con desayuno y entrada al spa incluidos.',
    cta_label: 'Ver disponibilidad',
    cta_destino: '/turismo/hotel-pucon',
    imagen: '/mocks/img/rec-pucon.jpg',
    badge: 'Solo abril',
    tier: 'aspiracional',
    fundamento_data: [
      'memory_bank.user=persona-001 fact: "Consultó Hotel Pucón el 2026-03-12, no concretó reserva"',
      'memory_bank.user=persona-001 fact: "acompañante mencionado nieta Sofía 8 años"',
    ],
    relevance_score: 0.88,
    generado_por: 'memory_bank',
  },
  {
    id: 'rec-maria-bono-escolar-sofia',
    titulo: 'Bono Escolar 2026 para Sofía',
    subtitulo: 'Aporte único anual · marzo cada año',
    categoria: 'Apoyo Social',
    monto_estimado_clp: 67_480,
    monto_display: '$67.480',
    porque_te_lo_recomendamos:
      'Sofía es tu carga familiar reconocida y está cursando 3° básico. El plazo de postulación 2026 cierra el 31 de mayo.',
    cta_label: 'Postular ahora',
    cta_destino: '/apoyo-social/bono-escolar/postular',
    imagen: '/mocks/img/rec-bono-escolar.jpg',
    badge: 'Para tu nieta',
    tier: 'alta',
    fundamento_data: [
      'persona-001.cargas_familiares incluye Sofía Reyes González edad 8',
      'beneficio:ben-bono-escolar requisitos cumplidos',
    ],
    relevance_score: 0.91,
    generado_por: 'rule_based',
  },
  {
    id: 'rec-maria-dental',
    titulo: 'Urgencia Dental en RedSalud por $100',
    subtitulo: 'Cobertura inmediata sin tope anual',
    categoria: 'Salud',
    monto_estimado_clp: 100,
    monto_display: '$100 copago',
    porque_te_lo_recomendamos:
      'Como pensionada FONASA Tramo B, este convenio te cubre dolor agudo, abscesos y traumatismos en cualquier RedSalud sin agendar. Útil tener en mente.',
    cta_label: 'Ver centros cercanos',
    cta_destino: '/beneficios/dental-urgencia',
    imagen: '/mocks/img/rec-dental.jpg',
    tier: 'media',
    fundamento_data: [
      'persona-001.isapre_o_fonasa = "FONASA Tramo B"',
      'persona-001.segmento = "Pensionado"',
      'convenio:conv-redsalud-dental aplica sin restricción etaria',
    ],
    relevance_score: 0.74,
    generado_por: 'collaborative_filter',
  },
  {
    id: 'rec-maria-universidad-experiencia',
    titulo: 'Universidad de la Experiencia — Maipú',
    subtitulo: 'Talleres de pintura y memoria · Inicio 5 mayo',
    categoria: 'Educación',
    monto_estimado_clp: 0,
    monto_display: 'Gratis para pensionados',
    porque_te_lo_recomendamos:
      'Programa exclusivo para pensionados afiliados con sede a 12 minutos de tu domicilio. Patricia Muñoz (otra afiliada de tu segmento) tomó pintura este verano.',
    cta_label: 'Conocer talleres',
    cta_destino: '/pensionados/universidad-experiencia',
    imagen: '/mocks/img/rec-universidad.jpg',
    badge: 'Tu sucursal',
    tier: 'aspiracional',
    fundamento_data: [
      'persona-001.segmento = "Pensionado"',
      'distancia_geo(persona-001.comuna, sede_maipu) = 4.2 km',
    ],
    relevance_score: 0.69,
    generado_por: 'collaborative_filter',
  },
  {
    id: 'rec-maria-seguro-vida-mama',
    titulo: 'Seguro de Sepelio para tu mamá',
    subtitulo: 'Tranquilidad anticipada · UF 50 cobertura',
    categoria: 'Seguro',
    monto_estimado_clp: 4_990,
    monto_display: 'Prima desde $4.990/mes',
    porque_te_lo_recomendamos:
      'Tu mamá Carmen (79) no tiene seguro funerario. Este convenio Confuturo cubre servicio completo con un copago mínimo y se contrata 100% online.',
    cta_label: 'Cotizar',
    cta_destino: '/seguros/sepelio-pensionados',
    imagen: '/mocks/img/rec-seguro-sepelio.jpg',
    tier: 'media',
    fundamento_data: [
      'persona-001.cargas_familiares.madre.edad = 79',
      'no_existe producto-seguro-vida en perfil para carga madre',
    ],
    relevance_score: 0.63,
    generado_por: 'rule_based',
  },
  {
    id: 'rec-maria-cine-pucon',
    titulo: 'Cinemark 2x1 lunes y martes',
    subtitulo: 'En todo Chile presentando credencial',
    categoria: 'Recreación',
    monto_display: '2x1',
    porque_te_lo_recomendamos:
      'Beneficio activo para llevar a Sofía al cine. El próximo estreno familiar es el jueves 24 de abril.',
    cta_label: 'Ver cartelera',
    cta_destino: '/beneficios/cinemark',
    imagen: '/mocks/img/rec-cinemark.jpg',
    tier: 'aspiracional',
    fundamento_data: ['carga_familiar.nieta.edad = 8', 'convenio:conv-cinemark vigente'],
    relevance_score: 0.55,
    generado_por: 'collaborative_filter',
  },
];

/* ─────────────────────────────────────────────────────────────────────────── */

export const RECOMMENDATIONS_RODRIGO: RecommendationCard[] = [
  {
    id: 'rec-rod-bono-nacimiento',
    titulo: 'Bono Nacimiento — anticipa tu trámite',
    subtitulo: 'Para tu hijo/a en julio 2026',
    categoria: 'Apoyo Social',
    monto_estimado_clp: 80_000,
    monto_display: '$80.000',
    porque_te_lo_recomendamos:
      'Mencionaste que tu pareja tiene parto programado. Puedes pre-armar el trámite ahora y solo activarlo con el certificado de nacimiento.',
    cta_label: 'Pre-cargar trámite',
    cta_destino: '/apoyo-social/bono-nacimiento',
    imagen: '/mocks/img/rec-nacimiento.jpg',
    tier: 'critica',
    fundamento_data: ['intereses_declarados incluye "parto programado"'],
    relevance_score: 0.95,
    generado_por: 'rule_based',
  },
  {
    id: 'rec-rod-credito-salud',
    titulo: 'Crédito de Salud — pago directo a clínica',
    subtitulo: 'Hasta $15M · CAE 19,5%',
    categoria: 'Crédito',
    monto_display: 'Cuota desde $89.000/mes',
    porque_te_lo_recomendamos:
      'Para cubrir copagos de cesárea programada. Pago directo al prestador en 48h.',
    cta_label: 'Simular',
    cta_destino: '/creditos/salud/simular',
    imagen: '/mocks/img/rec-cred-salud.jpg',
    tier: 'alta',
    fundamento_data: ['intereses_declarados incluye "cesárea"'],
    relevance_score: 0.86,
    generado_por: 'rule_based',
  },
  {
    id: 'rec-rod-asig-familiar',
    titulo: 'Aumenta tu Asignación Familiar al nacer',
    subtitulo: 'Tramo C: +$4.459/mes por carga',
    categoria: 'Apoyo Social',
    monto_estimado_clp: 4_459,
    monto_display: '+$4.459/mes',
    porque_te_lo_recomendamos:
      'Estás en tramo C. Cuando inscribas a tu nuevo hijo/a, tu asignación sube automáticamente.',
    cta_label: 'Ver detalle tramos',
    cta_destino: '/apoyo-social/asignacion-familiar',
    imagen: '/mocks/img/rec-asig-familiar.jpg',
    tier: 'media',
    fundamento_data: ['persona-002.asignacion_familiar_tramo = "C"'],
    relevance_score: 0.78,
    generado_por: 'rule_based',
  },
];

export const RECOMMENDATIONS_BY_PERSONA: Record<string, RecommendationCard[]> = {
  'persona-001': RECOMMENDATIONS_MARIA,
  'persona-002': RECOMMENDATIONS_RODRIGO,
};

export function getRecommendationsForPersona(persona: Persona): RecommendationCard[] {
  return RECOMMENDATIONS_BY_PERSONA[persona.id] ?? [];
}
