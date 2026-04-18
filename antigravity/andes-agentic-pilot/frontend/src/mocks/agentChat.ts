/* =============================================================================
 * mocks/agentChat.ts — Andesia floating chat (multi-agent transcript)
 *
 * Pre-recorded conversation que sigue exactamente el storyline de
 * docs/demo_strategy.md §4 (Beats 1–6):
 *
 *   Beat 1 — Concierge greets, classifies intent (consolidación + bono mamá)
 *   Beat 2 — CreditoAgent simula y razona
 *   Beat 3 — BeneficiosAgent ground en Ley 18.833 / reglamento
 *   Beat 4 — Document AI auto-fill liquidación
 *   Beat 5 — Memory Bank → nudge proactivo turismo Pucón
 *   Beat 6 — Live API voice close (María confirma cuota)
 *
 * Cada turno incluye: agent name, message, reasoning steps, tool calls
 * (con args + result), citaciones a reglamento.
 *
 * Estructura inspirada en:
 *  - ADK event schema (event: agent_start | thinking | tool_call | tool_result | handoff | message | done)
 *  - LangSmith run trees / Anthropic console tool-use viewer
 * ============================================================================= */

export type TurnRole = 'user' | 'concierge' | 'credito_agent' | 'beneficios_agent' | 'document_ai_agent' | 'memory_bank' | 'voice_agent' | 'system';

export type AgentColor = 'azul' | 'amarillo' | 'verde' | 'gris' | 'rojo' | 'morado';

export interface ReasoningStep {
  step_index: number;
  text: string; // chain-of-thought visible cuando user expande "Razonando…"
  duration_ms: number;
}

export interface ToolCall {
  id: string;
  name: string;
  args: Record<string, unknown>;
  result: Record<string, unknown> | string;
  status: 'success' | 'error' | 'running';
  latency_ms: number;
}

export interface Citation {
  id: string;
  source_type: 'ley' | 'reglamento_ccla' | 'circular_suseso' | 'cdn_pdf';
  source_title: string;
  source_url: string;
  paragraph_excerpt: string;
  similarity_score: number; // 0–1
  chunk_id: string;
}

export interface Handoff {
  from: TurnRole;
  to: TurnRole;
  reason: string;
}

export type Turn =
  | {
      kind: 'user_message';
      turn_index: number;
      role: 'user';
      timestamp_iso: string;
      text: string;
      audio_url?: string;
    }
  | {
      kind: 'agent_message';
      turn_index: number;
      role: Exclude<TurnRole, 'user'>;
      agent_label: string;
      agent_color: AgentColor;
      timestamp_iso: string;
      reasoning?: ReasoningStep[];
      tool_calls?: ToolCall[];
      handoffs?: Handoff[];
      text: string;
      citations?: Citation[];
      ui_card?: {
        type: 'producto_credito' | 'beneficio' | 'comparativa' | 'formulario' | 'video' | 'imagen';
        payload: Record<string, unknown>;
      };
    }
  | {
      kind: 'system_event';
      turn_index: number;
      role: 'system';
      timestamp_iso: string;
      event:
        | 'session_start'
        | 'memory_loaded'
        | 'document_uploaded'
        | 'voice_session_open'
        | 'session_close';
      payload: Record<string, unknown>;
    };

/* ─────────────────────────────────────────────────────────────────────────── */
/* === Andesia main demo conversation =====================================  */
/* ─────────────────────────────────────────────────────────────────────────── */

export const ANDESIA_DEMO_CONVERSATION: Turn[] = [
  /* === Sistema: arranca sesión ===========================================  */
  {
    kind: 'system_event',
    turn_index: 0,
    role: 'system',
    timestamp_iso: '2026-04-20T10:30:00.000-04:00',
    event: 'session_start',
    payload: {
      session_id: 'sess_2026_04_20_andesia_demo',
      user_id: 'persona-001',
      channel: 'sucursal-virtual-web',
      authenticated: true,
      auth_provider: 'keycloak:afiliados-ccla-prd',
    },
  },
  {
    kind: 'system_event',
    turn_index: 1,
    role: 'system',
    timestamp_iso: '2026-04-20T10:30:00.420-04:00',
    event: 'memory_loaded',
    payload: {
      memory_bank_user: 'persona-001',
      facts: [
        'Pensionada hace 22 años',
        'Comuna: Maipú',
        'Canal preferido: WhatsApp',
        'Interés activo (mar-2026): turismo Pucón',
        'Última visita: 2026-03-12 — consultó dental urgencia',
      ],
    },
  },

  /* === Turn 1 — usuario pregunta ========================================  */
  {
    kind: 'user_message',
    turn_index: 2,
    role: 'user',
    timestamp_iso: '2026-04-20T10:30:08.110-04:00',
    text: 'Hola, quiero ver si puedo juntar mis deudas en un solo crédito y también escuché algo de un bono para mi mamá que cumple 50 años de matrimonio.',
  },

  /* === Turn 2 — Concierge clasifica + handoff paralelo ==================  */
  {
    kind: 'agent_message',
    turn_index: 3,
    role: 'concierge',
    agent_label: 'Andesia · Concierge',
    agent_color: 'gris',
    timestamp_iso: '2026-04-20T10:30:09.940-04:00',
    reasoning: [
      {
        step_index: 1,
        text: 'Identifico al usuario por SSO Keycloak: persona-001 — María González, pensionada hace 22 años, Maipú.',
        duration_ms: 180,
      },
      {
        step_index: 2,
        text: 'Detecto dos intenciones distintas en el mismo mensaje: (1) consolidación de crédito personal; (2) consulta de beneficio Bono Bodas de Oro para tercero (madre).',
        duration_ms: 320,
      },
      {
        step_index: 3,
        text: 'Voy a delegar en paralelo a CreditoAgent y BeneficiosAgent. Cada uno trabaja sobre su dominio sin bloquear al otro. Reuno respuestas en 2-3s.',
        duration_ms: 240,
      },
    ],
    tool_calls: [
      {
        id: 't_001',
        name: 'getAfiliadoProfile',
        args: { rut: '12.345.678-5' },
        result: {
          nombre: 'María Cecilia González Pereira',
          segmento: 'Pensionado',
          antiguedad_anos: 22,
          comuna: 'Maipú',
          pension_liquida_clp: 487_320,
        },
        status: 'success',
        latency_ms: 142,
      },
    ],
    handoffs: [
      { from: 'concierge', to: 'credito_agent', reason: 'Intención #1: consolidación de deuda' },
      { from: 'concierge', to: 'beneficios_agent', reason: 'Intención #2: Bono Bodas de Oro (tercero)' },
    ],
    text:
      'Hola María, qué gusto saludarte. Veo dos cosas en lo que me dices: una consulta de crédito y una de beneficios. Las voy a revisar en paralelo y te respondo en un toque. Eso sí — antes de seguir, ¿me confirmas que quieres consolidar tus deudas externas (banco + retail) en un crédito social Caja Los Andes? Procedo bajo ese supuesto.',
  },

  /* === Turn 3 — CreditoAgent simula =====================================  */
  {
    kind: 'agent_message',
    turn_index: 4,
    role: 'credito_agent',
    agent_label: 'CreditoAgent',
    agent_color: 'azul',
    timestamp_iso: '2026-04-20T10:30:13.220-04:00',
    reasoning: [
      {
        step_index: 1,
        text: 'Consulto REDEC (con consentimiento previo de María firmado el 2025-09-12) para obtener deudas vigentes externas.',
        duration_ms: 520,
      },
      {
        step_index: 2,
        text: 'REDEC devuelve: BancoEstado consumo $3.200.000 cuota $98.400 CAE 27.4%; Falabella tarjeta $1.300.000 cuota $48.900 CAE 41.2%. Total deuda: $4.500.000, cuota total $147.300.',
        duration_ms: 380,
      },
      {
        step_index: 3,
        text: 'Simulo Crédito Consolidación CCLA: monto $4.500.000 a 36 meses, tasa preferencial pensionados CAE 18.9%. Cuota mensual proyectada: $142.300.',
        duration_ms: 240,
      },
      {
        step_index: 4,
        text: 'Validación capacidad de pago: cuota nueva $142.300 / pensión líquida $487.320 = 29.2%. Por encima del tope estándar 25% pero dentro del tope pensionados 30% (Reglamento Crédito Social art. 12). Aprobable con observación.',
        duration_ms: 310,
      },
      {
        step_index: 5,
        text: 'Beneficio neto: ahorro mensual $5.000 + reducción de obligaciones de 2 a 1 + tasa promedio bajó de 31.7% (ponderado) a 18.9%. Recomiendo aprobación.',
        duration_ms: 180,
      },
    ],
    tool_calls: [
      {
        id: 't_002',
        name: 'consultarREDEC',
        args: { rut: '12.345.678-5', consentimiento_firmado: '2025-09-12' },
        result: {
          ley: 'Ley 21.680',
          deudas: [
            { acreedor: 'BancoEstado', tipo: 'Consumo', saldo_clp: 3_200_000, cuota_clp: 98_400, cae_anual_pct: 27.4 },
            { acreedor: 'Falabella', tipo: 'Tarjeta retail', saldo_clp: 1_300_000, cuota_clp: 48_900, cae_anual_pct: 41.2 },
          ],
          total_deuda_clp: 4_500_000,
          total_cuota_clp: 147_300,
          fecha_consulta: '2026-04-20',
        },
        status: 'success',
        latency_ms: 893,
      },
      {
        id: 't_003',
        name: 'simulateCredito',
        args: { producto: 'Crédito Consolidación de Deuda', monto_clp: 4_500_000, plazo_meses: 36, segmento: 'Pensionado' },
        result: {
          cuota_mensual_clp: 142_300,
          cae_anual_pct: 18.9,
          tasa_mensual_pct: 1.43,
          costo_total_clp: 5_122_800,
          intereses_total_clp: 622_800,
          ahorro_vs_actual_mes_clp: 5_000,
          ahorro_total_proyecto_clp: 180_000,
          fecha_primera_cuota: '2026-05-15',
        },
        status: 'success',
        latency_ms: 412,
      },
    ],
    text:
      'Listo María. Revisé tus deudas en REDEC (con tu consentimiento del 2025-09-12) y simulé la consolidación. El resumen: en lugar de pagar $147.300 al mes en dos productos, pagarías una sola cuota de **$142.300** por 36 meses, con CAE preferencial pensionados de 18,9%. Es un ahorro de $5.000 al mes y, sobre todo, te baja la tasa promedio de 31,7% a 18,9%. ¿Quieres que avance con la solicitud?',
    citations: [
      {
        id: 'cit_001',
        source_type: 'ley',
        source_title: 'Ley 21.680 — Registro de Deuda Consolidada (REDEC)',
        source_url: 'https://www.bcn.cl/leychile/navegar?idNorma=1212014',
        paragraph_excerpt:
          'Artículo 4°.- El Registro de Deuda Consolidada contendrá la información sobre las obligaciones crediticias de las personas naturales… La consulta requerirá el consentimiento expreso del titular, otorgado de forma específica e informada.',
        similarity_score: 0.94,
        chunk_id: 'redec_art_4_p1',
      },
      {
        id: 'cit_002',
        source_type: 'reglamento_ccla',
        source_title: 'Reglamento Crédito Social Caja Los Andes — art. 12',
        source_url: 'https://www.cajalosandes.cl/static/reglamento-credito-social.pdf',
        paragraph_excerpt:
          'Artículo 12.- Para los pensionados afiliados, el descuento mensual por concepto de cuotas de Crédito Social no podrá exceder el treinta por ciento (30%) de la pensión líquida mensual…',
        similarity_score: 0.89,
        chunk_id: 'reg_credsoc_art_12_p1',
      },
    ],
    ui_card: {
      type: 'producto_credito',
      payload: {
        producto: 'Crédito Consolidación de Deuda',
        monto_clp: 4_500_000,
        cuota_mensual_clp: 142_300,
        cae_anual_pct: 18.9,
        plazo_meses: 36,
        ahorro_mensual_clp: 5_000,
        disclaimer: 'Simulación · no constituye oferta vinculante. Sujeta a validación documental y firma electrónica.',
      },
    },
  },

  /* === Turn 4 — BeneficiosAgent responde Bono Bodas de Oro ===============  */
  {
    kind: 'agent_message',
    turn_index: 5,
    role: 'beneficios_agent',
    agent_label: 'BeneficiosAgent',
    agent_color: 'amarillo',
    timestamp_iso: '2026-04-20T10:30:14.610-04:00',
    reasoning: [
      {
        step_index: 1,
        text: 'Pregunta es sobre tercero (madre del afiliado). Verifico si Bono Bodas de Oro es transferible / si la madre es elegible directa.',
        duration_ms: 200,
      },
      {
        step_index: 2,
        text: 'RAG sobre corpus Ley 20.595 + reglamento DS 32/2012 MDS + manual beneficios CCLA. Top-3 chunks recuperados con score >0.85.',
        duration_ms: 410,
      },
      {
        step_index: 3,
        text: 'Conclusión: Bono Bodas de Oro es del Estado (no de CCLA), pero CCLA tramita la solicitud para sus afiliados y cargas. La madre de María (Carmen, 79 años) puede solicitar directamente si cumple condiciones de Registro Social de Hogares.',
        duration_ms: 280,
      },
    ],
    tool_calls: [
      {
        id: 't_004',
        name: 'queryReglamentos',
        args: { query: 'Bono Bodas de Oro requisitos solicitud familiares afiliado', top_k: 3 },
        result: {
          chunks: [
            { id: 'ley_20595_art1', score: 0.96, source: 'Ley 20.595 art. 1' },
            { id: 'reg_bonobodas_p3', score: 0.91, source: 'Reglamento DS 32/2012 MDS' },
            { id: 'manual_ccla_bono_p2', score: 0.87, source: 'Manual Beneficios CCLA 2026' },
          ],
        },
        status: 'success',
        latency_ms: 612,
      },
      {
        id: 't_005',
        name: 'checkElegibilidadBeneficio',
        args: { beneficio_id: 'ben-bodas-oro', persona_rut: '4.123.987-2' },
        result: {
          elegible: true,
          monto_clp: 300_000,
          condiciones_cumplidas: ['50 años de matrimonio cumplidos en 2026-07-12', 'tramo RSH 60%'],
          condiciones_pendientes: [],
          documentos_requeridos: ['Certificado matrimonio Registro Civil', 'Cédulas ambos cónyuges'],
          monto_estimado_pago_clp: 300_000,
          fecha_pago_estimada: '2026-08-30',
        },
        status: 'success',
        latency_ms: 287,
      },
    ],
    text:
      'En paralelo revisé lo de tu mamá. **Sí**, Carmen califica para el Bono Bodas de Oro. Es un beneficio del Estado (Ley 20.595), bono único de **$300.000**, no imponible y no tributable. Como cumple 50 años de matrimonio en julio 2026 y está en el tramo 60% del Registro Social de Hogares, es elegible. Yo desde acá puedo iniciar la solicitud — solo necesitamos el certificado de matrimonio y las cédulas. ¿Te acompaño?',
    citations: [
      {
        id: 'cit_003',
        source_type: 'ley',
        source_title: 'Ley 20.595 — Bono Bodas de Oro',
        source_url: 'https://www.bcn.cl/leychile/navegar?idNorma=1040112',
        paragraph_excerpt:
          'Artículo 1°.- Establécese, en favor de las personas que cumplan cincuenta años de matrimonio, un bono especial denominado "Bono Bodas de Oro"…',
        similarity_score: 0.96,
        chunk_id: 'ley_20595_art_1',
      },
      {
        id: 'cit_004',
        source_type: 'reglamento_ccla',
        source_title: 'Manual de Beneficios CCLA 2026 — sección 4.2',
        source_url: 'https://cla.cdn.modyo.com/uploads/manual-beneficios-2026.pdf',
        paragraph_excerpt:
          '4.2 Bono Bodas de Oro. La Caja realiza la tramitación gratuita ante el IPS para sus afiliados y para los padres y madres de sus afiliados que cumplan los requisitos…',
        similarity_score: 0.87,
        chunk_id: 'manual_ccla_bono_p2',
      },
    ],
    ui_card: {
      type: 'beneficio',
      payload: {
        beneficio: 'Bono Bodas de Oro',
        beneficiario: 'Carmen Pereira Olivares (madre)',
        monto_clp: 300_000,
        ley: 'Ley 20.595',
        fecha_pago_estimada: '2026-08-30',
        documentos_pendientes: ['Certificado matrimonio', 'Cédula cónyuge madre'],
      },
    },
  },

  /* === Turn 5 — Usuario acepta + sube doc ================================  */
  {
    kind: 'user_message',
    turn_index: 6,
    role: 'user',
    timestamp_iso: '2026-04-20T10:30:42.180-04:00',
    text: 'Sí, dale a las dos. Te subo la liquidación de pensión de marzo.',
  },
  {
    kind: 'system_event',
    turn_index: 7,
    role: 'system',
    timestamp_iso: '2026-04-20T10:30:48.000-04:00',
    event: 'document_uploaded',
    payload: {
      filename: 'liquidacion_pension_marzo_2026.pdf',
      size_bytes: 184_502,
      pages: 1,
      mime: 'application/pdf',
    },
  },

  /* === Turn 6 — DocumentAI extrae y autorrellena ========================  */
  {
    kind: 'agent_message',
    turn_index: 8,
    role: 'document_ai_agent',
    agent_label: 'DocumentAI · CustomExtractor (es)',
    agent_color: 'morado',
    timestamp_iso: '2026-04-20T10:30:50.940-04:00',
    reasoning: [
      {
        step_index: 1,
        text: 'Recibo PDF 1 página, formato liquidación IPS. Aplico procesador Custom Extractor (es) entrenado sobre 1.200 liquidaciones de pensión chilenas.',
        duration_ms: 920,
      },
      {
        step_index: 2,
        text: 'Extraigo 8 entidades con confidence ≥ 0.91: RUT, nombre, AFP/IPS, monto pensión bruta, descuentos previsionales, monto líquido, periodo, banco depósito.',
        duration_ms: 540,
      },
      {
        step_index: 3,
        text: 'Cross-check con perfil persona-001: RUT y nombre coinciden exactamente. Monto líquido $487.320 coincide con dato registrado. Documento validado.',
        duration_ms: 180,
      },
    ],
    tool_calls: [
      {
        id: 't_006',
        name: 'documentAI.extract',
        args: {
          processor: 'projects/vtxdemos/locations/us/processors/ccla-liquidacion-pension-extractor',
          file: 'liquidacion_pension_marzo_2026.pdf',
        },
        result: {
          entities: [
            { type: 'rut_titular', value: '12.345.678-5', confidence: 0.99, bbox: [120, 145, 285, 168] },
            { type: 'nombre_titular', value: 'GONZALEZ PEREIRA MARIA CECILIA', confidence: 0.98, bbox: [120, 175, 540, 198] },
            { type: 'pagador', value: 'INSTITUTO DE PREVISION SOCIAL (IPS)', confidence: 0.97, bbox: [120, 210, 460, 233] },
            { type: 'periodo', value: 'MARZO 2026', confidence: 0.99, bbox: [430, 145, 540, 168] },
            { type: 'monto_pension_bruta_clp', value: 542_800, confidence: 0.96, bbox: [420, 320, 550, 343] },
            { type: 'descuento_salud_clp', value: 38_660, confidence: 0.95, bbox: [420, 345, 550, 368] },
            { type: 'descuento_credito_ccla_clp', value: 16_820, confidence: 0.93, bbox: [420, 370, 550, 393] },
            { type: 'monto_liquido_clp', value: 487_320, confidence: 0.99, bbox: [420, 420, 550, 443] },
          ],
          processing_time_ms: 920,
          page_count: 1,
        },
        status: 'success',
        latency_ms: 940,
      },
      {
        id: 't_007',
        name: 'submitSolicitudCredito',
        args: {
          producto_id: 'cred-consolidacion',
          monto_clp: 4_500_000,
          plazo_meses: 36,
          rut_solicitante: '12.345.678-5',
          consentimiento_redec: true,
          documento_acreditacion: 'liquidacion_pension_marzo_2026.pdf',
        },
        result: {
          numero_solicitud: 'SOL-2026-04-1182937',
          estado: 'aprobada_pendiente_firma',
          firma_electronica_url: 'https://miportal.cajalosandes.cl/firma/SOL-2026-04-1182937',
          fecha_desembolso_estimada: '2026-04-23',
        },
        status: 'success',
        latency_ms: 612,
      },
    ],
    text:
      'Listo, leí tu liquidación. Confirmo: pensión líquida marzo $487.320, IPS, descuento salud $38.660. Con esos datos creé la solicitud **SOL-2026-04-1182937** para tu Crédito Consolidación. Está aprobada y solo requiere tu firma electrónica. El desembolso a tus acreedores se haría el 23 de abril.',
    ui_card: {
      type: 'formulario',
      payload: {
        numero_solicitud: 'SOL-2026-04-1182937',
        campos_autollenados: [
          { campo: 'RUT', valor: '12.345.678-5', confidence: 0.99 },
          { campo: 'Nombre', valor: 'María Cecilia González Pereira', confidence: 0.98 },
          { campo: 'Pagador', valor: 'IPS', confidence: 0.97 },
          { campo: 'Pensión líquida', valor: '$487.320', confidence: 0.99 },
        ],
        estado: 'aprobada_pendiente_firma',
        cta: 'Firmar electrónicamente',
        cta_url: 'https://miportal.cajalosandes.cl/firma/SOL-2026-04-1182937',
      },
    },
  },

  /* === Turn 7 — Concierge nudge proactivo turismo (Memory Bank) =========  */
  {
    kind: 'agent_message',
    turn_index: 9,
    role: 'concierge',
    agent_label: 'Andesia · Concierge',
    agent_color: 'gris',
    timestamp_iso: '2026-04-20T10:30:58.110-04:00',
    reasoning: [
      {
        step_index: 1,
        text: 'Memory Bank devuelve interés activo: turismo Pucón consultado en mar-2026 sin conversión. Cuota nueva libera $5.000/mes vs status quo + 1 producto menos = mejor liquidez.',
        duration_ms: 220,
      },
      {
        step_index: 2,
        text: 'Disponibilidad turismo Pucón abr-jun 2026: 12 cupos disponibles tarifa afiliado $79.000/noche. Match con preferencia "viaje en familia con nieta".',
        duration_ms: 310,
      },
    ],
    tool_calls: [
      {
        id: 't_008',
        name: 'memoryBank.retrieve',
        args: { user_id: 'persona-001', topic: 'turismo' },
        result: {
          fact: 'Consultó Hotel Pucón el 2026-03-12, no concretó reserva. Acompañante mencionado: nieta Sofía (8 años).',
          last_interaction: '2026-03-12T16:42:11-03:00',
          confidence: 0.92,
        },
        status: 'success',
        latency_ms: 145,
      },
      {
        id: 't_009',
        name: 'getDisponibilidadTurismo',
        args: { hotel_id: 'hotel-pucon', desde: '2026-05-01', hasta: '2026-06-30' },
        result: {
          cupos_disponibles: 12,
          tarifa_afiliado_clp_noche: 79_000,
          tarifa_publico_clp_noche: 138_000,
          ahorro_pct: 42.8,
        },
        status: 'success',
        latency_ms: 187,
      },
    ],
    text:
      'Antes de cerrar — recuerdo que en marzo me consultaste por viajar a Pucón con la Sofi. Con la cuota nueva tu flujo libre sube ~$5.000 al mes; tengo cupo en el Hotel Caja Los Andes Pucón a $79.000/noche (tarifa afiliada, 43% bajo público) entre mayo y junio. ¿Te lo dejo apartado por 24 horas mientras decides?',
    ui_card: {
      type: 'comparativa',
      payload: {
        tipo: 'turismo_nudge',
        hotel: 'Hotel & Spa Caja Los Andes Pucón',
        precio_publico_clp: 138_000,
        precio_afiliada_clp: 79_000,
        cupos: 12,
        ventana: 'May–Jun 2026',
      },
    },
  },

  /* === Turn 8 — Usuario acepta y pasa a voz =============================  */
  {
    kind: 'user_message',
    turn_index: 10,
    role: 'user',
    timestamp_iso: '2026-04-20T10:31:18.220-04:00',
    text: '[Activa modo voz] Sí, apártamelo. Y confírmame en voz que la cuota es bajo $150 mil.',
  },
  {
    kind: 'system_event',
    turn_index: 11,
    role: 'system',
    timestamp_iso: '2026-04-20T10:31:18.610-04:00',
    event: 'voice_session_open',
    payload: {
      model: 'gemini-live-2.5-flash-native-audio',
      language: 'es-CL',
      voice: 'Aoede',
      vad_enabled: true,
      affective_dialog: true,
    },
  },

  /* === Turn 9 — Voice agent confirma ====================================  */
  {
    kind: 'agent_message',
    turn_index: 12,
    role: 'voice_agent',
    agent_label: 'Andesia · Voz',
    agent_color: 'rojo',
    timestamp_iso: '2026-04-20T10:31:19.940-04:00',
    reasoning: [
      {
        step_index: 1,
        text: 'Recupero contexto sesión: cuota aprobada $142.300. Ejecuto verificación literal contra umbral $150.000.',
        duration_ms: 90,
      },
    ],
    tool_calls: [
      {
        id: 't_010',
        name: 'getSimulacion',
        args: { numero_solicitud: 'SOL-2026-04-1182937' },
        result: { cuota_mensual_clp: 142_300 },
        status: 'success',
        latency_ms: 78,
      },
    ],
    text:
      'Sí María, confirmado. Tu cuota mensual es de **ciento cuarenta y dos mil trescientos pesos**, claramente bajo tus ciento cincuenta mil. Y ya te aparté el cupo del Hotel Pucón hasta mañana al mediodía. Cuando firmes electrónicamente, te aviso por WhatsApp. ¿Algo más?',
  },

  /* === Cierre =============================================================  */
  {
    kind: 'system_event',
    turn_index: 13,
    role: 'system',
    timestamp_iso: '2026-04-20T10:31:24.000-04:00',
    event: 'session_close',
    payload: {
      session_id: 'sess_2026_04_20_andesia_demo',
      duration_seconds: 84,
      tool_calls_total: 10,
      handoffs: 3,
      groundedness_score: 0.94,
      helpfulness_score: 0.91,
      memory_writes: 2,
      cost_usd: 0.041,
      trace_url: 'https://console.cloud.google.com/traces/details/sess_2026_04_20_andesia_demo?project=vtxdemos',
    },
  },
];

/* ─────────────────────────────────────────────────────────────────────────── */
/* === Conversación corta: Rodrigo (afiliación + crédito de salud) =========  */
/* ─────────────────────────────────────────────────────────────────────────── */

export const RODRIGO_PARTO_CONVERSATION: Turn[] = [
  {
    kind: 'user_message',
    turn_index: 0,
    role: 'user',
    timestamp_iso: '2026-04-19T14:22:00-04:00',
    text: 'Mi señora va a tener parto programado en julio, cesárea. ¿Qué me cubre Caja Los Andes?',
  },
  {
    kind: 'agent_message',
    turn_index: 1,
    role: 'concierge',
    agent_label: 'Andesia · Concierge',
    agent_color: 'gris',
    timestamp_iso: '2026-04-19T14:22:02-04:00',
    handoffs: [
      { from: 'concierge', to: 'beneficios_agent', reason: 'Subsidio nacimiento + crédito salud parto' },
    ],
    text: 'Felicitaciones Rodrigo. Te paso a Beneficios para que te arme el paquete completo.',
  },
  {
    kind: 'agent_message',
    turn_index: 2,
    role: 'beneficios_agent',
    agent_label: 'BeneficiosAgent',
    agent_color: 'amarillo',
    timestamp_iso: '2026-04-19T14:22:04-04:00',
    text:
      'Te explico lo que aplica en tu caso (Tramo C asignación familiar, parto julio 2026):\n\n1. **Bono Profamilia Nacimiento** — $80.000 únicos, dentro de 60 días post-parto.\n2. **Asignación Familiar tramo C** — $4.459 mensuales por la nueva carga.\n3. **Crédito de Salud** preferente para copago cesárea — CAE 19,5%, hasta $15M, pago directo a clínica.\n4. **Convenio RedSalud** — 30% descuento exámenes prenatales y postnatales.\n\n¿Quieres que te simule el Crédito de Salud o que te agende un control con prestador en convenio?',
    citations: [
      {
        id: 'cit_r01',
        source_type: 'reglamento_ccla',
        source_title: 'Manual Beneficios CCLA — Bono Profamilia Nacimiento',
        source_url: 'https://cla.cdn.modyo.com/uploads/manual-beneficios-2026.pdf',
        paragraph_excerpt:
          'Bono único de $80.000 al afiliado/a por el nacimiento de hijo/a, pagadero hasta 60 días después del nacimiento.',
        similarity_score: 0.93,
        chunk_id: 'manual_ccla_nacimiento_p1',
      },
    ],
  },
];

/* ─────────────────────────────────────────────────────────────────────────── */
/* === Conversación: Patricia (subsidio defunción) =========================  */
/* ─────────────────────────────────────────────────────────────────────────── */

export const PATRICIA_DEFUNCION_CONVERSATION: Turn[] = [
  {
    kind: 'user_message',
    turn_index: 0,
    role: 'user',
    timestamp_iso: '2026-04-15T10:08:00-04:00',
    text: 'Falleció mi esposo en febrero. ¿Hay algún apoyo de la Caja?',
  },
  {
    kind: 'agent_message',
    turn_index: 1,
    role: 'concierge',
    agent_label: 'Andesia · Concierge',
    agent_color: 'gris',
    timestamp_iso: '2026-04-15T10:08:02-04:00',
    text:
      'Patricia, lamento mucho su pérdida. Sí, hay un Bono Profamilia Defunción de $250.000 que le corresponde como cónyuge sobreviviente. La ventana de solicitud son 6 meses desde el deceso, así que estamos a tiempo. ¿Tiene a mano el certificado de defunción? Puedo iniciar la solicitud ahora mismo, o si prefiere, le agendo cita con un ejecutivo en su sucursal de Concepción.',
  },
];

export const ALL_CONVERSATIONS = {
  andesia_demo: ANDESIA_DEMO_CONVERSATION,
  rodrigo_parto: RODRIGO_PARTO_CONVERSATION,
  patricia_defuncion: PATRICIA_DEFUNCION_CONVERSATION,
};
