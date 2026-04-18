/* =============================================================================
 * mocks/searchSuggestions.ts — Autocomplete + intent detection
 *
 * 35+ queries reales de afiliados CCLA (basadas en patrones de search analytics
 * documentados en investigación + términos extraídos del scraped HTML).
 *
 * Cada sugerencia incluye:
 *   - intent (que mapea a un módulo del producto)
 *   - popularidad (1000s últimos 30 días)
 *   - es_pregunta_natural (vs keyword)
 *   - sugerencia_de_completion (lo que el modelo agrega cuando el usuario tipea)
 *   - tags semánticos
 *
 * Las top queries reales que se ven en buscadores CCLA según investigación:
 *   1. "bodas de oro"
 *   2. "credito social"
 *   3. "pago cuota"
 *   4. "asignacion familiar tramo"
 *   5. "sucursal cerca"
 *
 * Las queries naturales largas (40%+) son evidencia de que el chat conversacional
 * es lo que la audiencia ya está pidiendo en buscador.
 * ============================================================================= */

export type SearchIntent =
  | 'producto_credito'
  | 'beneficio_social'
  | 'pago_cuota'
  | 'sucursal_horario'
  | 'simulador'
  | 'documento_certificado'
  | 'reclamo_consulta'
  | 'turismo_recreacion'
  | 'seguros'
  | 'convenios_descuentos'
  | 'estado_solicitud'
  | 'educacion_becas'
  | 'pyme'
  | 'voz_natural_conversacional';

export interface SearchSuggestion {
  id: string;
  query: string;
  intent: SearchIntent;
  popularidad_30d: number; // miles
  es_pregunta_natural: boolean; // vs keyword
  completion_predicted: string | null; // lo que el modelo sugiere agregar
  tags: string[];
  ruta_destino: string;
  /** ¿Esta query debería disparar el chat agéntico en lugar del search clásico? */
  trigger_chat_agentic: boolean;
  /** Confidence con la que el modelo identifica el intent */
  intent_confidence: number;
}

export const SEARCH_SUGGESTIONS: SearchSuggestion[] = [
  /* === Top queries (alto volumen) === */
  {
    id: 'sug-001',
    query: 'bodas de oro',
    intent: 'beneficio_social',
    popularidad_30d: 58.4,
    es_pregunta_natural: false,
    completion_predicted: 'bodas de oro como solicitar',
    tags: ['bono', 'pareja', 'aniversario', 'pensionado'],
    ruta_destino: '/beneficios/bodas-de-oro',
    trigger_chat_agentic: false,
    intent_confidence: 0.99,
  },
  {
    id: 'sug-002',
    query: 'crédito social',
    intent: 'producto_credito',
    popularidad_30d: 51.2,
    es_pregunta_natural: false,
    completion_predicted: 'crédito social pensionados simulador',
    tags: ['credito', 'universal', 'consumo'],
    ruta_destino: '/credito-social',
    trigger_chat_agentic: false,
    intent_confidence: 0.97,
  },
  {
    id: 'sug-003',
    query: 'pagar cuota',
    intent: 'pago_cuota',
    popularidad_30d: 47.9,
    es_pregunta_natural: false,
    completion_predicted: 'pagar cuota online crédito social',
    tags: ['pago', 'webpay', 'cuota'],
    ruta_destino: '/pagos',
    trigger_chat_agentic: false,
    intent_confidence: 0.98,
  },
  {
    id: 'sug-004',
    query: 'asignación familiar',
    intent: 'beneficio_social',
    popularidad_30d: 42.1,
    es_pregunta_natural: false,
    completion_predicted: 'asignación familiar tramo b 2026',
    tags: ['asignacion', 'tramo', 'sue'],
    ruta_destino: '/beneficios/asignacion-familiar',
    trigger_chat_agentic: false,
    intent_confidence: 0.99,
  },
  {
    id: 'sug-005',
    query: 'sucursal más cercana',
    intent: 'sucursal_horario',
    popularidad_30d: 38.6,
    es_pregunta_natural: false,
    completion_predicted: 'sucursal más cercana a mi ubicación',
    tags: ['sucursal', 'mapa', 'horario'],
    ruta_destino: '/sucursales',
    trigger_chat_agentic: true,
    intent_confidence: 0.94,
  },

  /* === Long-tail conversacionales — disparan chat agéntico === */
  {
    id: 'sug-006',
    query: '¿puedo juntar todas mis deudas en una sola?',
    intent: 'voz_natural_conversacional',
    popularidad_30d: 12.4,
    es_pregunta_natural: true,
    completion_predicted: null,
    tags: ['consolidacion', 'deudas', 'asesoria'],
    ruta_destino: '/andesia?intent=consolidacion',
    trigger_chat_agentic: true,
    intent_confidence: 0.91,
  },
  {
    id: 'sug-007',
    query: 'cómo le pido el bono a mis papás por sus 50 años',
    intent: 'voz_natural_conversacional',
    popularidad_30d: 8.7,
    es_pregunta_natural: true,
    completion_predicted: null,
    tags: ['bodas-oro', 'cargas-indirectas', 'familia'],
    ruta_destino: '/andesia?intent=bodas_oro_terceros',
    trigger_chat_agentic: true,
    intent_confidence: 0.89,
  },
  {
    id: 'sug-008',
    query: 'me quedé sin pega que beneficios tengo',
    intent: 'voz_natural_conversacional',
    popularidad_30d: 14.8,
    es_pregunta_natural: true,
    completion_predicted: null,
    tags: ['cesantia', 'seguro', 'chileno-coloquial'],
    ruta_destino: '/andesia?intent=cesantia',
    trigger_chat_agentic: true,
    intent_confidence: 0.93,
  },
  {
    id: 'sug-009',
    query: 'cuanto me prestan si gano 850 mil',
    intent: 'voz_natural_conversacional',
    popularidad_30d: 18.2,
    es_pregunta_natural: true,
    completion_predicted: null,
    tags: ['simulador', 'monto-maximo', 'renta'],
    ruta_destino: '/andesia?intent=simulacion_credito',
    trigger_chat_agentic: true,
    intent_confidence: 0.88,
  },
  {
    id: 'sug-010',
    query: 'mi mamá necesita pagar un funeral',
    intent: 'voz_natural_conversacional',
    popularidad_30d: 4.8,
    es_pregunta_natural: true,
    completion_predicted: null,
    tags: ['defuncion', 'urgencia', 'familia'],
    ruta_destino: '/andesia?intent=defuncion',
    trigger_chat_agentic: true,
    intent_confidence: 0.95,
  },

  /* === Pago y trámites === */
  {
    id: 'sug-011',
    query: 'estado de mi solicitud',
    intent: 'estado_solicitud',
    popularidad_30d: 33.7,
    es_pregunta_natural: false,
    completion_predicted: 'estado de mi solicitud crédito',
    tags: ['solicitud', 'trazabilidad'],
    ruta_destino: '/mis-solicitudes',
    trigger_chat_agentic: false,
    intent_confidence: 0.96,
  },
  {
    id: 'sug-012',
    query: 'certificado de afiliación',
    intent: 'documento_certificado',
    popularidad_30d: 21.3,
    es_pregunta_natural: false,
    completion_predicted: 'certificado de afiliación pdf descargar',
    tags: ['certificado', 'pdf', 'tramite'],
    ruta_destino: '/documentos/certificados',
    trigger_chat_agentic: false,
    intent_confidence: 0.99,
  },
  {
    id: 'sug-013',
    query: 'certificado de deuda',
    intent: 'documento_certificado',
    popularidad_30d: 16.9,
    es_pregunta_natural: false,
    completion_predicted: 'certificado de deuda crédito social',
    tags: ['deuda', 'certificado'],
    ruta_destino: '/documentos/certificados/deuda',
    trigger_chat_agentic: false,
    intent_confidence: 0.99,
  },
  {
    id: 'sug-014',
    query: 'cómo hacer una reprogramación',
    intent: 'reclamo_consulta',
    popularidad_30d: 9.2,
    es_pregunta_natural: true,
    completion_predicted: 'cómo hacer una reprogramación de cuotas',
    tags: ['reprogramacion', 'cuota', 'mora'],
    ruta_destino: '/andesia?intent=reprogramacion',
    trigger_chat_agentic: true,
    intent_confidence: 0.87,
  },

  /* === Beneficios sociales === */
  {
    id: 'sug-015',
    query: 'bono escolar 2026',
    intent: 'beneficio_social',
    popularidad_30d: 27.4,
    es_pregunta_natural: false,
    completion_predicted: 'bono escolar 2026 monto y fecha pago',
    tags: ['bono-escolar', 'marzo', 'cargas'],
    ruta_destino: '/beneficios/bono-escolar',
    trigger_chat_agentic: false,
    intent_confidence: 0.98,
  },
  {
    id: 'sug-016',
    query: 'beca caja los andes',
    intent: 'educacion_becas',
    popularidad_30d: 19.8,
    es_pregunta_natural: false,
    completion_predicted: 'beca caja los andes universidad postular',
    tags: ['beca', 'educacion-superior', 'jovenes'],
    ruta_destino: '/educacion/becas',
    trigger_chat_agentic: false,
    intent_confidence: 0.97,
  },
  {
    id: 'sug-017',
    query: 'bono nacimiento',
    intent: 'beneficio_social',
    popularidad_30d: 11.3,
    es_pregunta_natural: false,
    completion_predicted: 'bono nacimiento monto requisitos',
    tags: ['bono', 'nacimiento', 'parto'],
    ruta_destino: '/beneficios/bono-nacimiento',
    trigger_chat_agentic: false,
    intent_confidence: 0.99,
  },
  {
    id: 'sug-018',
    query: 'bono defunción',
    intent: 'beneficio_social',
    popularidad_30d: 8.6,
    es_pregunta_natural: false,
    completion_predicted: 'bono defunción cómo cobrar',
    tags: ['bono', 'defuncion', 'sepelio'],
    ruta_destino: '/beneficios/bono-defuncion',
    trigger_chat_agentic: false,
    intent_confidence: 0.99,
  },
  {
    id: 'sug-019',
    query: 'subsidio cuidadores',
    intent: 'beneficio_social',
    popularidad_30d: 6.4,
    es_pregunta_natural: false,
    completion_predicted: 'subsidio cuidadores ley 21632',
    tags: ['cuidadores', 'subsidio', 'ley-21632'],
    ruta_destino: '/beneficios/cuidadores',
    trigger_chat_agentic: false,
    intent_confidence: 0.96,
  },
  {
    id: 'sug-020',
    query: 'bono marzo',
    intent: 'beneficio_social',
    popularidad_30d: 22.1,
    es_pregunta_natural: false,
    completion_predicted: 'bono marzo 2026 quien lo recibe',
    tags: ['bono-marzo', 'estado'],
    ruta_destino: '/beneficios/bono-marzo',
    trigger_chat_agentic: false,
    intent_confidence: 0.98,
  },

  /* === Productos crédito === */
  {
    id: 'sug-021',
    query: 'crédito de salud',
    intent: 'producto_credito',
    popularidad_30d: 18.4,
    es_pregunta_natural: false,
    completion_predicted: 'crédito de salud cae 2026',
    tags: ['credito-salud', 'tratamiento'],
    ruta_destino: '/credito/salud',
    trigger_chat_agentic: false,
    intent_confidence: 0.98,
  },
  {
    id: 'sug-022',
    query: 'crédito consolidación',
    intent: 'producto_credito',
    popularidad_30d: 16.7,
    es_pregunta_natural: false,
    completion_predicted: 'crédito consolidación deudas portabilidad',
    tags: ['consolidacion', 'portabilidad'],
    ruta_destino: '/credito/consolidacion',
    trigger_chat_agentic: false,
    intent_confidence: 0.97,
  },
  {
    id: 'sug-023',
    query: 'crédito para estudiar',
    intent: 'voz_natural_conversacional',
    popularidad_30d: 7.8,
    es_pregunta_natural: true,
    completion_predicted: 'crédito para estudiar universidad',
    tags: ['credito-educacion', 'arancel'],
    ruta_destino: '/credito/educacion-superior',
    trigger_chat_agentic: false,
    intent_confidence: 0.91,
  },
  {
    id: 'sug-024',
    query: 'tapp crédito',
    intent: 'producto_credito',
    popularidad_30d: 13.2,
    es_pregunta_natural: false,
    completion_predicted: 'tapp crédito jóvenes app',
    tags: ['tapp', 'microcredito', 'jovenes'],
    ruta_destino: '/tapp/credito',
    trigger_chat_agentic: false,
    intent_confidence: 0.98,
  },
  {
    id: 'sug-025',
    query: 'simular crédito',
    intent: 'simulador',
    popularidad_30d: 24.6,
    es_pregunta_natural: false,
    completion_predicted: 'simular crédito cuota mensual',
    tags: ['simulador', 'cuota'],
    ruta_destino: '/simulador',
    trigger_chat_agentic: false,
    intent_confidence: 0.99,
  },

  /* === Sucursales === */
  {
    id: 'sug-026',
    query: 'sucursal providencia',
    intent: 'sucursal_horario',
    popularidad_30d: 14.2,
    es_pregunta_natural: false,
    completion_predicted: 'sucursal providencia horario sábado',
    tags: ['sucursal', 'rm', 'horario'],
    ruta_destino: '/sucursales/providencia',
    trigger_chat_agentic: false,
    intent_confidence: 0.97,
  },
  {
    id: 'sug-027',
    query: 'sucursal maipú horario',
    intent: 'sucursal_horario',
    popularidad_30d: 9.8,
    es_pregunta_natural: false,
    completion_predicted: null,
    tags: ['sucursal', 'maipu', 'horario'],
    ruta_destino: '/sucursales/maipu',
    trigger_chat_agentic: false,
    intent_confidence: 0.98,
  },
  {
    id: 'sug-028',
    query: 'atención sábado',
    intent: 'sucursal_horario',
    popularidad_30d: 11.4,
    es_pregunta_natural: false,
    completion_predicted: 'atención sábado sucursal santiago',
    tags: ['horario', 'fin-semana'],
    ruta_destino: '/sucursales?filtro=sabado',
    trigger_chat_agentic: true,
    intent_confidence: 0.92,
  },

  /* === Convenios === */
  {
    id: 'sug-029',
    query: 'convenios farmacia',
    intent: 'convenios_descuentos',
    popularidad_30d: 8.9,
    es_pregunta_natural: false,
    completion_predicted: 'convenios farmacia ahumada cruz verde',
    tags: ['convenio', 'farmacia', 'salud'],
    ruta_destino: '/convenios/farmacias',
    trigger_chat_agentic: false,
    intent_confidence: 0.96,
  },
  {
    id: 'sug-030',
    query: 'convenios cine',
    intent: 'convenios_descuentos',
    popularidad_30d: 6.7,
    es_pregunta_natural: false,
    completion_predicted: 'convenios cine cinemark hoyts',
    tags: ['convenio', 'cine', 'recreacion'],
    ruta_destino: '/convenios/cine',
    trigger_chat_agentic: false,
    intent_confidence: 0.97,
  },
  {
    id: 'sug-031',
    query: 'descuento farmacias ahumada',
    intent: 'convenios_descuentos',
    popularidad_30d: 5.3,
    es_pregunta_natural: false,
    completion_predicted: null,
    tags: ['ahumada', 'farmacia'],
    ruta_destino: '/convenios/farmacias/ahumada',
    trigger_chat_agentic: false,
    intent_confidence: 0.98,
  },

  /* === Turismo === */
  {
    id: 'sug-032',
    query: 'hotel pucón',
    intent: 'turismo_recreacion',
    popularidad_30d: 17.8,
    es_pregunta_natural: false,
    completion_predicted: 'hotel pucón caja los andes precios',
    tags: ['hotel', 'pucon', 'turismo'],
    ruta_destino: '/turismo/hoteles/pucon',
    trigger_chat_agentic: false,
    intent_confidence: 0.99,
  },
  {
    id: 'sug-033',
    query: 'vacaciones invierno',
    intent: 'turismo_recreacion',
    popularidad_30d: 14.1,
    es_pregunta_natural: false,
    completion_predicted: 'vacaciones invierno familia 2026',
    tags: ['vacaciones', 'invierno', 'familia'],
    ruta_destino: '/turismo/vacaciones-invierno',
    trigger_chat_agentic: false,
    intent_confidence: 0.94,
  },
  {
    id: 'sug-034',
    query: 'paquetes turismo',
    intent: 'turismo_recreacion',
    popularidad_30d: 10.6,
    es_pregunta_natural: false,
    completion_predicted: 'paquetes turismo nacional afiliados',
    tags: ['paquete', 'turismo'],
    ruta_destino: '/turismo/paquetes',
    trigger_chat_agentic: false,
    intent_confidence: 0.96,
  },

  /* === Seguros === */
  {
    id: 'sug-035',
    query: 'seguro de vida familiar',
    intent: 'seguros',
    popularidad_30d: 9.4,
    es_pregunta_natural: false,
    completion_predicted: 'seguro de vida familiar 9990',
    tags: ['seguro', 'vida', 'familia'],
    ruta_destino: '/seguros/vida-familiar',
    trigger_chat_agentic: false,
    intent_confidence: 0.98,
  },
  {
    id: 'sug-036',
    query: 'seguro cesantía',
    intent: 'seguros',
    popularidad_30d: 7.2,
    es_pregunta_natural: false,
    completion_predicted: 'seguro cesantía crédito social',
    tags: ['seguro', 'cesantia', 'credito'],
    ruta_destino: '/seguros/cesantia',
    trigger_chat_agentic: false,
    intent_confidence: 0.97,
  },

  /* === PYME === */
  {
    id: 'sug-037',
    query: 'crédito pyme',
    intent: 'pyme',
    popularidad_30d: 8.4,
    es_pregunta_natural: false,
    completion_predicted: 'crédito pyme empresa pequeña',
    tags: ['pyme', 'empresa'],
    ruta_destino: '/empresas/credito-pyme',
    trigger_chat_agentic: false,
    intent_confidence: 0.97,
  },
  {
    id: 'sug-038',
    query: 'cómo afiliar mis trabajadores',
    intent: 'pyme',
    popularidad_30d: 6.1,
    es_pregunta_natural: true,
    completion_predicted: 'cómo afiliar mis trabajadores empresa',
    tags: ['empresa', 'afiliacion'],
    ruta_destino: '/empresas/afiliacion',
    trigger_chat_agentic: true,
    intent_confidence: 0.89,
  },

  /* === Conversacionales adicionales (María-style) === */
  {
    id: 'sug-039',
    query: 'me quiero arreglar la dentadura',
    intent: 'voz_natural_conversacional',
    popularidad_30d: 5.7,
    es_pregunta_natural: true,
    completion_predicted: null,
    tags: ['dental', 'salud', 'credito-salud'],
    ruta_destino: '/andesia?intent=salud_dental',
    trigger_chat_agentic: true,
    intent_confidence: 0.86,
  },
  {
    id: 'sug-040',
    query: 'que hago si no puedo pagar mi cuota este mes',
    intent: 'voz_natural_conversacional',
    popularidad_30d: 11.8,
    es_pregunta_natural: true,
    completion_predicted: null,
    tags: ['mora', 'reprogramacion', 'urgencia'],
    ruta_destino: '/andesia?intent=mora',
    trigger_chat_agentic: true,
    intent_confidence: 0.93,
  },
  {
    id: 'sug-041',
    query: 'cuanta plata tengo en la caja',
    intent: 'voz_natural_conversacional',
    popularidad_30d: 16.2,
    es_pregunta_natural: true,
    completion_predicted: null,
    tags: ['saldo', 'cuenta', 'consulta'],
    ruta_destino: '/andesia?intent=saldo',
    trigger_chat_agentic: true,
    intent_confidence: 0.92,
  },
  {
    id: 'sug-042',
    query: 'mi licencia médica está pagada',
    intent: 'voz_natural_conversacional',
    popularidad_30d: 13.4,
    es_pregunta_natural: true,
    completion_predicted: null,
    tags: ['licencia-medica', 'subsidio', 'sil'],
    ruta_destino: '/andesia?intent=licencia_medica_estado',
    trigger_chat_agentic: true,
    intent_confidence: 0.94,
  },
];

/* ───────────────────────────────────────────────────────────────────────────
 * AUTOCOMPLETE: simulación del comportamiento "Apple-style"
 * ─────────────────────────────────────────────────────────────────────────── */

export interface AutocompleteResult {
  partial_input: string;
  suggestions: SearchSuggestion[];
  ai_response_inline: string | null; // respuesta resumida sin abandonar el search bar
  show_chat_cta: boolean;
}

export const AUTOCOMPLETE_DEMOS: AutocompleteResult[] = [
  {
    partial_input: 'bod',
    suggestions: [
      SEARCH_SUGGESTIONS.find((s) => s.id === 'sug-001')!,
      SEARCH_SUGGESTIONS.find((s) => s.id === 'sug-007')!,
    ],
    ai_response_inline:
      'Bono Bodas de Oro: $300.000 que CCLA paga por aniversario de 50 años de matrimonio. Aplicas tú, tus padres o suegros si están afiliados.',
    show_chat_cta: true,
  },
  {
    partial_input: 'me que',
    suggestions: [
      SEARCH_SUGGESTIONS.find((s) => s.id === 'sug-008')!,
      SEARCH_SUGGESTIONS.find((s) => s.id === 'sug-039')!,
    ],
    ai_response_inline: null,
    show_chat_cta: true,
  },
  {
    partial_input: 'cuanto',
    suggestions: [
      SEARCH_SUGGESTIONS.find((s) => s.id === 'sug-009')!,
      SEARCH_SUGGESTIONS.find((s) => s.id === 'sug-041')!,
    ],
    ai_response_inline:
      'Puedo calcular cuánto te prestamos en segundos. Escribe tu sueldo aproximado o pídele una simulación personalizada a Andesia.',
    show_chat_cta: true,
  },
  {
    partial_input: 'crédito',
    suggestions: [
      SEARCH_SUGGESTIONS.find((s) => s.id === 'sug-002')!,
      SEARCH_SUGGESTIONS.find((s) => s.id === 'sug-021')!,
      SEARCH_SUGGESTIONS.find((s) => s.id === 'sug-022')!,
      SEARCH_SUGGESTIONS.find((s) => s.id === 'sug-024')!,
    ],
    ai_response_inline: null,
    show_chat_cta: false,
  },
];

/* ───────────────────────────────────────────────────────────────────────────
 * Helpers
 * ─────────────────────────────────────────────────────────────────────────── */

export function getTopSuggestions(n = 10): SearchSuggestion[] {
  return [...SEARCH_SUGGESTIONS].sort((a, b) => b.popularidad_30d - a.popularidad_30d).slice(0, n);
}

export function getSuggestionsByIntent(intent: SearchIntent): SearchSuggestion[] {
  return SEARCH_SUGGESTIONS.filter((s) => s.intent === intent);
}

export function getConversationalSuggestions(): SearchSuggestion[] {
  return SEARCH_SUGGESTIONS.filter((s) => s.es_pregunta_natural);
}
