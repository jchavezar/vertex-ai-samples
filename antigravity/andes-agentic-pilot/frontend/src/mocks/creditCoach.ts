/* =============================================================================
 * mocks/creditCoach.ts — Crédito Coach interactivo
 *
 * Reasoning trace que sigue el patrón "ReAct" (Reason + Act):
 *   1. María pregunta "¿me conviene este crédito?"
 *   2. Agente recopila contexto (obligaciones actuales)
 *   3. Calcula DTI (Debt-to-Income)
 *   4. Compara escenarios (no hacer nada vs consolidar)
 *   5. Lista pros/contras
 *   6. Final recommendation card
 *
 * Modeled after: Klarna AI assistant transparency, Plaid debt waterfall analysis
 * ============================================================================= */

export interface ObligacionActual {
  acreedor: string;
  tipo: 'Crédito Universal CCLA' | 'Tarjeta Tapp' | 'Banco Consumo' | 'Tarjeta Retail' | 'Línea Crédito' | 'Crédito Hipotecario';
  saldo_clp: number;
  cuota_mensual_clp: number;
  cae_anual_pct: number;
  meses_restantes: number;
  notas?: string;
}

export interface DtiCalculation {
  ingreso_liquido_mensual_clp: number;
  total_cuotas_actuales_clp: number;
  dti_actual_pct: number;
  dti_post_consolidacion_pct: number;
  tope_reglamentario_pct: number;
  tope_aplicable_segmento: string;
  apto_post_consolidacion: boolean;
}

export interface EscenarioComparado {
  nombre: 'no_hacer_nada' | 'consolidar_ccla' | 'portabilidad_otra';
  display_name: string;
  cuota_mensual_clp: number;
  meses: number;
  costo_total_clp: number;
  intereses_total_clp: number;
  cae_promedio_pct: number;
  obligaciones_resultantes: number;
  pros: string[];
  contras: string[];
  diferencia_vs_status_quo_clp: number;
}

export interface CoachReasoningStep {
  step: number;
  titulo: string;
  texto: string;
  data_referenciada?: Record<string, unknown>;
}

export interface CreditCoachAnalysis {
  persona_id: string;
  pregunta_inicial: string;
  fecha_analisis: string;
  obligaciones_actuales: ObligacionActual[];
  dti: DtiCalculation;
  reasoning_steps: CoachReasoningStep[];
  escenarios: EscenarioComparado[];
  recomendacion_final: {
    accion_recomendada: string;
    racional_corto: string;
    nivel_confianza: 'baja' | 'media' | 'alta' | 'muy_alta';
    riesgo_principal: string;
    cae_recomendado_pct: number;
    cuota_recomendada_clp: number;
    plazo_recomendado_meses: number;
    monto_recomendado_clp: number;
    fecha_primera_cuota: string;
    disclaimers: string[];
    citations: { fuente: string; url: string }[];
  };
}

/* ─────────────────────────────────────────────────────────────────────────── */
/* === Análisis para María González — consolidación =======================  */
/* ─────────────────────────────────────────────────────────────────────────── */

export const COACH_ANALYSIS_MARIA: CreditCoachAnalysis = {
  persona_id: 'persona-001',
  pregunta_inicial: '¿Me conviene tomar este crédito de consolidación?',
  fecha_analisis: '2026-04-20T10:31:42-04:00',
  obligaciones_actuales: [
    {
      acreedor: 'Caja Los Andes',
      tipo: 'Crédito Universal CCLA',
      saldo_clp: 1_840_500,
      cuota_mensual_clp: 78_240,
      cae_anual_pct: 21.4,
      meses_restantes: 26,
      notas: 'Crédito vigente al día desde sept-2023.',
    },
    {
      acreedor: 'BancoEstado',
      tipo: 'Banco Consumo',
      saldo_clp: 3_200_000,
      cuota_mensual_clp: 98_400,
      cae_anual_pct: 27.4,
      meses_restantes: 36,
      notas: 'Detectado vía REDEC con consentimiento 2025-09-12.',
    },
    {
      acreedor: 'Falabella Servicios Financieros',
      tipo: 'Tarjeta Retail',
      saldo_clp: 1_300_000,
      cuota_mensual_clp: 48_900,
      cae_anual_pct: 41.2,
      meses_restantes: 30,
      notas: 'Tasa más alta del portafolio. Candidata #1 a consolidar.',
    },
  ],
  dti: {
    ingreso_liquido_mensual_clp: 487_320,
    total_cuotas_actuales_clp: 225_540,
    dti_actual_pct: 46.3,
    dti_post_consolidacion_pct: 29.2,
    tope_reglamentario_pct: 30,
    tope_aplicable_segmento: 'Pensionados — Reglamento Crédito Social art. 12',
    apto_post_consolidacion: true,
  },
  reasoning_steps: [
    {
      step: 1,
      titulo: 'Mapeo de obligaciones actuales',
      texto:
        'Tienes 3 obligaciones activas: un Crédito Universal con CCLA al 21,4%, un crédito de consumo BancoEstado al 27,4% y una tarjeta Falabella al 41,2%. Tu cuota mensual total son $225.540, equivalente al 46,3% de tu pensión líquida. Eso supera el tope reglamentario del 30% para pensionados — es decir, **estás financieramente sobreendeudada según el reglamento**.',
      data_referenciada: { dti_actual: 0.463, tope_reglamentario: 0.30 },
    },
    {
      step: 2,
      titulo: 'Validación legal y de elegibilidad',
      texto:
        'El Crédito Consolidación de Caja Los Andes (Ley 18.833 + Ley 21.236 portabilidad) te permite reunir hasta 4 obligaciones en una sola, pagada por descuento de pensión, con CAE preferente para pensionados de 18,9%.',
    },
    {
      step: 3,
      titulo: 'Simulación de la nueva cuota',
      texto:
        'Si consolidamos los $4.500.000 (suma de las 3 obligaciones) a 36 meses al 18,9% CAE, la cuota mensual queda en $142.300. Eso equivale al 29,2% de tu pensión líquida — justo bajo el tope reglamentario y aceptable.',
      data_referenciada: { monto_consolidado: 4_500_000, plazo_meses: 36, cae: 0.189, cuota: 142_300 },
    },
    {
      step: 4,
      titulo: 'Comparación de costos totales',
      texto:
        'Status quo: pagar las 3 deudas hasta sus términos respectivos te cuesta aproximadamente $7.250.000 totales (intereses incluidos). Con consolidación a 36 meses pagas $5.122.800. **Ahorro neto estimado: $2.127.200** durante la vida del crédito.',
      data_referenciada: { ahorro_total_clp: 2_127_200 },
    },
    {
      step: 5,
      titulo: 'Riesgos y consideraciones',
      texto:
        'Riesgo principal: alargar la vida del crédito CCLA actual (que terminaba en 26 meses) hasta 36 — son 10 meses más con CCLA. Pero el ahorro mensual y total compensa con holgura. Recomendación: consolidar.',
    },
  ],
  escenarios: [
    {
      nombre: 'no_hacer_nada',
      display_name: 'Mantener todo como está',
      cuota_mensual_clp: 225_540,
      meses: 36,
      costo_total_clp: 7_250_000,
      intereses_total_clp: 2_750_000,
      cae_promedio_pct: 31.7,
      obligaciones_resultantes: 3,
      pros: ['Sin cambios', 'Termina más pronto el crédito CCLA actual (26 meses vs 36)'],
      contras: [
        'DTI de 46,3% — sobre tope reglamentario',
        'CAE promedio ponderada 31,7%',
        'Riesgo de mora si baja la pensión',
        'Falabella al 41,2% es predatorio',
      ],
      diferencia_vs_status_quo_clp: 0,
    },
    {
      nombre: 'consolidar_ccla',
      display_name: 'Consolidar con Crédito CCLA',
      cuota_mensual_clp: 142_300,
      meses: 36,
      costo_total_clp: 5_122_800,
      intereses_total_clp: 622_800,
      cae_promedio_pct: 18.9,
      obligaciones_resultantes: 1,
      pros: [
        'Una sola cuota, fácil de gestionar',
        'CAE preferente pensionados 18,9%',
        'DTI baja al 29,2% — apto reglamentariamente',
        'Ahorro total estimado $2,1M',
        'Pago directo a acreedores en 5 días hábiles',
      ],
      contras: [
        'Alarga 10 meses el crédito CCLA actual',
        'Requiere firma electrónica + REDEC ya consentido',
      ],
      diferencia_vs_status_quo_clp: -2_127_200,
    },
    {
      nombre: 'portabilidad_otra',
      display_name: 'Portabilidad a otra entidad',
      cuota_mensual_clp: 158_900,
      meses: 36,
      costo_total_clp: 5_720_400,
      intereses_total_clp: 1_220_400,
      cae_promedio_pct: 22.5,
      obligaciones_resultantes: 1,
      pros: ['Una sola cuota', 'Comparable a consolidar'],
      contras: [
        'CAE más alta que CCLA (no eres cliente preferente allá)',
        'Trámite presencial probable',
        'Sin descuento por planilla — riesgo de mora',
      ],
      diferencia_vs_status_quo_clp: -1_529_600,
    },
  ],
  recomendacion_final: {
    accion_recomendada: 'Consolidar con Crédito Consolidación CCLA',
    racional_corto:
      'Reduces tu cuota mensual de $225.540 a $142.300, bajas el CAE promedio de 31,7% a 18,9% y ahorras ~$2,1M en la vida del crédito. Tu DTI vuelve al rango reglamentario.',
    nivel_confianza: 'muy_alta',
    riesgo_principal:
      'Si tu pensión bajara (ej. cambio régimen), una sola cuota mayor podría afectarte más que la suma actual. Sugerimos contratar Seguro Cesantía Crédito Social como complemento.',
    cae_recomendado_pct: 18.9,
    cuota_recomendada_clp: 142_300,
    plazo_recomendado_meses: 36,
    monto_recomendado_clp: 4_500_000,
    fecha_primera_cuota: '2026-05-15',
    disclaimers: [
      'Simulación · no constituye oferta vinculante.',
      'Sujeta a validación documental y firma electrónica.',
      'Las tasas pueden variar según evaluación final y vigencia de la TMC.',
      'Consulta REDEC con consentimiento expreso (Ley 21.680).',
    ],
    citations: [
      { fuente: 'Reglamento Crédito Social CCLA art. 12 (tope pensionados)', url: 'https://www.cajalosandes.cl/static/reglamento-credito-social.pdf' },
      { fuente: 'Ley 18.833 — Estatuto General CCAF', url: 'https://www.bcn.cl/leychile/navegar?idNorma=30153' },
      { fuente: 'Ley 21.680 — REDEC', url: 'https://www.bcn.cl/leychile/navegar?idNorma=1212014' },
      { fuente: 'Ley 21.236 — Portabilidad Financiera', url: 'https://www.bcn.cl/leychile/navegar?idNorma=1146386' },
    ],
  },
};

/* ─────────────────────────────────────────────────────────────────────────── */
/* === Análisis para Diego — sobre adelanto de cuota ======================  */
/* ─────────────────────────────────────────────────────────────────────────── */

export const COACH_ANALYSIS_DIEGO_ADELANTO: CreditCoachAnalysis = {
  persona_id: 'persona-006',
  pregunta_inicial: '¿Me conviene adelantar 1 cuota en mayo?',
  fecha_analisis: '2026-04-18T19:32:00-04:00',
  obligaciones_actuales: [
    {
      acreedor: 'Caja Los Andes',
      tipo: 'Crédito Universal CCLA',
      saldo_clp: 3_870_000,
      cuota_mensual_clp: 142_300,
      cae_anual_pct: 18.9,
      meses_restantes: 27,
    },
  ],
  dti: {
    ingreso_liquido_mensual_clp: 925_400,
    total_cuotas_actuales_clp: 142_300,
    dti_actual_pct: 15.4,
    dti_post_consolidacion_pct: 15.4,
    tope_reglamentario_pct: 25,
    tope_aplicable_segmento: 'Trabajadores activos — Reglamento art. 8',
    apto_post_consolidacion: true,
  },
  reasoning_steps: [
    {
      step: 1,
      titulo: 'Situación financiera holgada',
      texto:
        'Tu DTI actual es 15,4%, muy por debajo del tope 25%. Tienes capacidad para adelantar pagos sin riesgo de cashflow.',
    },
    {
      step: 2,
      titulo: 'Cálculo de ahorro por adelanto',
      texto:
        'Adelantar 1 cuota equivale a aplicar $142.300 al capital adeudado. Eso reduce los intereses futuros en aproximadamente $25.320 y termina el crédito 1 mes antes (mayo 2028 vs junio 2028).',
    },
    {
      step: 3,
      titulo: 'Comparación con uso alternativo del dinero',
      texto:
        'Si en lugar de adelantar inviertes los $142.300 en Mis Metas (rendimiento esperado 6%/año real), generarías $8.500 en 24 meses. Adelantar el crédito al 18,9% TIR equivalente es más rentable.',
    },
  ],
  escenarios: [
    {
      nombre: 'no_hacer_nada',
      display_name: 'Pagar normal',
      cuota_mensual_clp: 142_300,
      meses: 27,
      costo_total_clp: 3_842_100,
      intereses_total_clp: -27_900,
      cae_promedio_pct: 18.9,
      obligaciones_resultantes: 1,
      pros: ['Mantienes liquidez actual'],
      contras: ['Pagas $25.320 más en intereses vs adelantar 1 cuota'],
      diferencia_vs_status_quo_clp: 0,
    },
    {
      nombre: 'consolidar_ccla',
      display_name: 'Adelantar 1 cuota en mayo',
      cuota_mensual_clp: 142_300,
      meses: 26,
      costo_total_clp: 3_816_780,
      intereses_total_clp: -53_220,
      cae_promedio_pct: 18.9,
      obligaciones_resultantes: 1,
      pros: ['Ahorro $25.320 intereses', 'Termina 1 mes antes'],
      contras: ['Reduce liquidez del mes mayo en $142.300'],
      diferencia_vs_status_quo_clp: -25_320,
    },
  ],
  recomendacion_final: {
    accion_recomendada: 'Adelantar 1 cuota en mayo',
    racional_corto:
      'Ahorras $25.320 en intereses sin afectar tu DTI. Mejor uso del dinero que mantenerlo en cuenta corriente.',
    nivel_confianza: 'alta',
    riesgo_principal: 'Pérdida puntual de liquidez de mayo — manejable porque tu DTI es bajo.',
    cae_recomendado_pct: 18.9,
    cuota_recomendada_clp: 142_300,
    plazo_recomendado_meses: 26,
    monto_recomendado_clp: 142_300,
    fecha_primera_cuota: '2026-05-03',
    disclaimers: ['Simulación · estimaciones sujetas a tabla de amortización oficial.'],
    citations: [
      { fuente: 'Cláusula prepago Crédito Universal CCLA', url: 'https://www.cajalosandes.cl/static/contrato-credito-universal.pdf' },
    ],
  },
};

export const ALL_COACH_ANALYSES = [COACH_ANALYSIS_MARIA, COACH_ANALYSIS_DIEGO_ADELANTO];
