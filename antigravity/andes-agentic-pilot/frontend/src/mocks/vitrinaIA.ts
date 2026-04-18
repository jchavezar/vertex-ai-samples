/* =============================================================================
 * mocks/vitrinaIA.ts — Vitrina IA generativa (Nano Banana Pro = Gemini 3 Pro Image)
 *
 * Tarjetas personalizadas generadas para cada afiliado. Cada card es
 * una imagen + copy + CTA producida por:
 *   - Gemini 3 Pro (texto + razonamiento sobre perfil)
 *   - Nano Banana Pro (imagen, brand-aligned)
 *   - Veo 3.1 (en algunos casos, video corto 8s)
 *
 * Cada card incluye:
 *   - prompt_imagen (lo que se le pidió a Nano Banana Pro)
 *   - prompt_copy (lo que se le pidió a Gemini para texto)
 *   - elementos_marca CCLA aplicados (color, tipografía, logo lockup)
 *   - generation_metadata (modelo, tokens, latencia)
 *   - share_assets (caption WhatsApp, alt-text accesibilidad)
 *
 * Las imágenes referenciadas son URLs ficticias del bucket interno
 * gs://andesia-vitrina-prod/cards/{id}.webp
 * ============================================================================= */

export type CardSize = 'square_1080' | 'story_1080x1920' | 'banner_1200x628' | 'video_short_9x16';

export type GenModel =
  | 'nano-banana-pro' // Gemini 3 Pro Image (gemini-3-pro-image-preview)
  | 'veo-3.1-fast'
  | 'imagen-4-fast'
  | 'gemini-3-pro-multimodal';

export interface BrandElements {
  primary_color: string; // CCLA azul corporativo
  accent_color: string;
  logo_position: 'top-left' | 'top-right' | 'bottom-left' | 'bottom-right' | 'centered';
  typography: string;
  cta_button_color: string;
  watermark_visible: boolean;
}

export interface GenerationMetadata {
  model: GenModel;
  prompt_tokens: number;
  output_tokens?: number;
  generation_time_seconds: number;
  cost_usd_estimated: number;
  seed?: number;
  safety_filters_passed: boolean;
  groundedness_check_passed: boolean;
  guardrails_applied: string[];
}

export interface ShareAssets {
  caption_whatsapp: string;
  caption_instagram?: string;
  alt_text_accessibility: string;
  hashtags: string[];
}

export interface VitrinaCard {
  id: string;
  persona_id: string; // referencia a personas.ts
  generated_at: string;
  card_size: CardSize;
  asset_url: string; // gs:// o https:// CDN
  asset_url_thumbnail: string;
  variant_count: number; // cuántas variantes generó el modelo antes de elegir
  selected_variant_index: number;

  /** Razón estratégica de por qué esta tarjeta para esta persona */
  trigger: {
    tipo: 'fecha_clave' | 'cross_sell' | 'reactivacion' | 'evento_vida' | 'estacional' | 'campana_corporativa';
    descripcion: string;
    senales_input: string[]; // qué datos del perfil dispararon la card
  };

  /** Prompts originales (transparencia) */
  prompt_imagen: string;
  prompt_copy: string;

  /** Output final */
  titulo: string;
  subtitulo: string;
  cuerpo: string;
  cta_label: string;
  cta_deep_link: string;

  brand_elements: BrandElements;
  share_assets: ShareAssets;
  generation_metadata: GenerationMetadata;

  /** Métricas predichas por el modelo de relevancia */
  ctr_predicho_pct: number;
  conversion_predicha_pct: number;
}

const CCLA_BRAND: BrandElements = {
  primary_color: '#003C84', // azul CCLA
  accent_color: '#FFD400', // amarillo
  logo_position: 'top-left',
  typography: 'Inter / Caja Sans (custom CCLA)',
  cta_button_color: '#003C84',
  watermark_visible: true,
};

/* ───────────────────────────────────────────────────────────────────────────
 * CARDS PRE-GENERADAS
 * ─────────────────────────────────────────────────────────────────────────── */

export const VITRINA_CARDS: VitrinaCard[] = [
  /* === Card 1 — María: Bono Bodas de Oro para sus padres === */
  {
    id: 'vit-001',
    persona_id: 'persona-001',
    generated_at: '2026-04-17T07:42:18-04:00',
    card_size: 'square_1080',
    asset_url: 'https://cdn.andesia.cajalosandes.cl/vitrina/vit-001.webp',
    asset_url_thumbnail: 'https://cdn.andesia.cajalosandes.cl/vitrina/vit-001_thumb.webp',
    variant_count: 4,
    selected_variant_index: 2,
    trigger: {
      tipo: 'fecha_clave',
      descripcion: 'Aniversario 50 años de matrimonio de los padres de María registrado en su perfil familiar (carga indirecta).',
      senales_input: [
        'persona.cargas_indirectas[0].relacion = madre, fecha_matrimonio = 1976-05-12',
        'persona.intereses_declarados incluye "familia"',
        'historia_busquedas: "bono bodas oro padres" hace 11 días',
      ],
    },
    prompt_imagen:
      'Pareja de adultos mayores chilenos (75 años aprox), abuelos cariñosos, sentados en living iluminado de casa modesta de Maipú, sosteniendo una foto antigua de su matrimonio. Estilo fotográfico cálido, luz dorada de tarde, paleta cálida con acentos azul CCLA. NO usar caras de stock genéricas — diversidad real Chile. Composición cuadrada 1080x1080, espacio negativo en esquina superior derecha para overlay de copy. Aspect ratio 1:1.',
    prompt_copy:
      'Genera un titular emotivo en español chileno de máximo 8 palabras y un subtitular descriptivo de máximo 12 palabras. El producto es Bono Bodas de Oro $300.000 que CCLA paga por aniversario de 50 años de matrimonio. Tono cariñoso, no comercial. La afiliada es María, de 58 años, pensionada, y el bono es para sus padres. Cierra con CTA clara de un click.',
    titulo: 'Tus papás merecen celebrar sus 50',
    subtitulo: 'Solicita por ellos el Bono Bodas de Oro: $300.000',
    cuerpo:
      'Detectamos en tu perfil que tu mamá Berta y tu papá José cumplen 50 años de casados este 12 de mayo. Como afiliada Caja Los Andes puedes solicitar el bono de $300.000 en su nombre, sin trámite presencial. Te dejamos el formulario pre-llenado.',
    cta_label: 'Solicitar el bono ahora',
    cta_deep_link: '/beneficios/bodas-de-oro/solicitar?prefill=carga-001&token=mAr1A_pre_filled',
    brand_elements: CCLA_BRAND,
    share_assets: {
      caption_whatsapp:
        'Mira lo que encontré para los papás. Caja Los Andes paga $300.000 por las bodas de oro y se hace todo en línea, mira:',
      alt_text_accessibility:
        'Pareja de adultos mayores en su living mirando una foto de su boda. Texto: "Tus papás merecen celebrar sus 50. Solicita el Bono Bodas de Oro $300.000". Botón azul "Solicitar el bono ahora". Logo Caja Los Andes esquina superior izquierda.',
      hashtags: ['#CajaLosAndes', '#BodasDeOro', '#FamiliaChilena'],
    },
    generation_metadata: {
      model: 'nano-banana-pro',
      prompt_tokens: 124,
      output_tokens: 78,
      generation_time_seconds: 11.4,
      cost_usd_estimated: 0.014,
      seed: 482910,
      safety_filters_passed: true,
      groundedness_check_passed: true,
      guardrails_applied: ['ccla_brand_guidelines_v3', 'family_inclusive_imagery', 'no_fake_celebrities', 'no_perfect_teeth'],
    },
    ctr_predicho_pct: 14.8,
    conversion_predicha_pct: 31.2,
  },

  /* === Card 2 — María: Crédito Consolidación === */
  {
    id: 'vit-002',
    persona_id: 'persona-001',
    generated_at: '2026-04-17T07:43:02-04:00',
    card_size: 'banner_1200x628',
    asset_url: 'https://cdn.andesia.cajalosandes.cl/vitrina/vit-002.webp',
    asset_url_thumbnail: 'https://cdn.andesia.cajalosandes.cl/vitrina/vit-002_thumb.webp',
    variant_count: 6,
    selected_variant_index: 4,
    trigger: {
      tipo: 'cross_sell',
      descripcion: 'María tiene 3 deudas activas (CCLA + Banco Estado + Falabella). DTI = 46.3%. Consolidar bajaría DTI a 29.2% y ahorraría $2.127.200 en intereses.',
      senales_input: [
        'persona.productos_contratados.cuotas_pendientes_total = $4.580.000',
        'externo.deudas_otros_actores: BancoEstado $2.840.000, CMR Falabella $1.120.000',
        'simulacion_engine.ahorro_consolidacion = $2.127.200',
        'dti_actual = 46.3 (alta)',
      ],
    },
    prompt_imagen:
      'Visualización abstracta de tres flujos de dinero (representados como líneas de luz cálidas) que convergen en una sola línea limpia y azul CCLA. Estilo 3D suave, gradientes sutiles, fondo blanco con sutil textura papel. Iconografía financiera, ningún rostro. Banner horizontal 1200x628, espacio para texto en lado izquierdo. Estilo: Stripe homepage meets Apple infographic. Aspect ratio 1.91:1.',
    prompt_copy:
      'María tiene tres deudas activas que suman $7.5 MM y paga $189.500 al mes en cuotas. Consolidar a un solo crédito CCLA bajaría a $135.300 mensuales y ahorraría $2.127.200 en intereses. Genera titular financiero claro y honesto (no clickbait), subtitular con cifra concreta, y CTA accionable. Tono: una asesora de confianza, no vendedora.',
    titulo: 'Una sola cuota. Más liviana.',
    subtitulo: 'Consolidando podrías ahorrar $2.127.200 y bajar tu cuota mensual en $54.200',
    cuerpo:
      'Vimos que tienes deudas en CCLA, BancoEstado y CMR Falabella. Si las juntas en un Crédito Consolidación CCLA a CAE 18,9%, pagas una sola cuota y te queda más oxígeno cada mes. Sin papeleo: usamos lo que ya sabemos de ti.',
    cta_label: 'Ver mi simulación personalizada',
    cta_deep_link: '/credito/consolidacion/simular?ref=vitrina-002&autofill=true',
    brand_elements: CCLA_BRAND,
    share_assets: {
      caption_whatsapp: '',
      alt_text_accessibility:
        'Banner azul con tres líneas convergentes que se transforman en una sola. Texto: "Una sola cuota. Más liviana. Ahorras $2.127.200 consolidando con CCLA". Botón "Ver mi simulación personalizada".',
      hashtags: ['#CréditoConsolidación', '#CajaLosAndes', '#FinanzasSaludables'],
    },
    generation_metadata: {
      model: 'nano-banana-pro',
      prompt_tokens: 142,
      output_tokens: 86,
      generation_time_seconds: 9.8,
      cost_usd_estimated: 0.012,
      seed: 718430,
      safety_filters_passed: true,
      groundedness_check_passed: true,
      guardrails_applied: ['cifras_validadas_motor_simulacion', 'cae_disclosure_required', 'no_promesas_aprobacion', 'sernac_compliance'],
    },
    ctr_predicho_pct: 8.4,
    conversion_predicha_pct: 19.7,
  },

  /* === Card 3 — María: Hotel Pucón nieta Sofía === */
  {
    id: 'vit-003',
    persona_id: 'persona-001',
    generated_at: '2026-04-17T07:43:45-04:00',
    card_size: 'story_1080x1920',
    asset_url: 'https://cdn.andesia.cajalosandes.cl/vitrina/vit-003.webp',
    asset_url_thumbnail: 'https://cdn.andesia.cajalosandes.cl/vitrina/vit-003_thumb.webp',
    variant_count: 5,
    selected_variant_index: 1,
    trigger: {
      tipo: 'estacional',
      descripcion: 'Vacaciones de invierno en julio. María tiene una nieta (Sofía, 8) declarada. Hotel Pucón CLA tiene cupos y precio afiliado $79.000/noche.',
      senales_input: [
        'persona.cargas_familiares[1] = nieta Sofía 8 años',
        'persona.intereses_declarados incluye "viajes" y "familia"',
        'calendario_chile.vacaciones_invierno = 2026-07-08 a 2026-07-26',
        'inventario_hoteles_cla.pucon.disponibilidad = 12 cupos',
      ],
    },
    prompt_imagen:
      'Vista de una abuela chilena (60 años, sonrisa cálida, no actriz famosa) jugando con su nieta de 8 años en la nieve frente al volcán Villarrica nevado al fondo. Día soleado, cielo azul limpio, paleta fría con acento amarillo cálido en sus parkas. Composición vertical 1080x1920 estilo Instagram Story, espacio negativo arriba para titular y abajo para CTA. Realismo fotográfico, sin filtros artificiales. Aspect ratio 9:16.',
    prompt_copy:
      'María podría llevar a su nieta Sofía (8 años) a Hotel Pucón CLA en vacaciones de invierno. Precio afiliado $79.000/noche habitación doble + niño gratis. Genera titular emotivo evocando memoria intergeneracional, subtitular con precio claro, CTA simple. Sin clichés, sin "Pucón te espera".',
    titulo: 'Las primeras nieves de Sofía',
    subtitulo: 'Hotel CLA Pucón desde $79.000 la noche, niño gratis',
    cuerpo:
      'Las vacaciones de invierno parten el 8 de julio. Hotel CLA Pucón tiene 12 cupos para afiliados con tarifa especial: $79.000 la noche, segundo niño gratis hasta los 12 años. Spa, juegos, comida 100% incluida.',
    cta_label: 'Reservar ahora',
    cta_deep_link: '/turismo/hoteles/pucon/reservar?fecha=2026-07-12&pax=2A1N&ref=vit-003',
    brand_elements: CCLA_BRAND,
    share_assets: {
      caption_whatsapp:
        'Pucón con la Sofi en julio. Caja Los Andes lo tiene a $79.000 la noche y los niños van gratis. ¿Te animas a venir tú también?',
      caption_instagram:
        'Las primeras nieves de los nietos no se olvidan. Hotel CLA Pucón, vacaciones de invierno 2026.',
      alt_text_accessibility:
        'Abuela y nieta jugando en la nieve frente al volcán Villarrica. Titular: "Las primeras nieves de Sofía". Precio destacado: $79.000 la noche.',
      hashtags: ['#PucónConCLA', '#VacacionesEnFamilia', '#CajaLosAndes', '#TurismoChile'],
    },
    generation_metadata: {
      model: 'nano-banana-pro',
      prompt_tokens: 138,
      output_tokens: 92,
      generation_time_seconds: 12.7,
      cost_usd_estimated: 0.016,
      seed: 391207,
      safety_filters_passed: true,
      groundedness_check_passed: true,
      guardrails_applied: ['child_safety_imagery', 'precio_validado_inventario', 'no_promesas_clima', 'turismo_responsable'],
    },
    ctr_predicho_pct: 11.2,
    conversion_predicha_pct: 6.8,
  },

  /* === Card 4 — Rodrigo: Bono Nacimiento + Crédito Salud === */
  {
    id: 'vit-004',
    persona_id: 'persona-002',
    generated_at: '2026-04-17T07:44:31-04:00',
    card_size: 'square_1080',
    asset_url: 'https://cdn.andesia.cajalosandes.cl/vitrina/vit-004.webp',
    asset_url_thumbnail: 'https://cdn.andesia.cajalosandes.cl/vitrina/vit-004_thumb.webp',
    variant_count: 4,
    selected_variant_index: 3,
    trigger: {
      tipo: 'evento_vida',
      descripcion: 'Rodrigo y su pareja Camila esperan su primer hijo en julio 2026 (registrado en encuesta de vida). Edad madre 28 años, primer parto.',
      senales_input: [
        'persona.evento_vida_proximo = parto, fecha_estimada 2026-07-15',
        'persona.cargas_familiares = 0 (será su primera carga)',
        'persona.intereses_declarados incluye "salud"',
        'persona.previsión = FONASA Tramo C',
      ],
    },
    prompt_imagen:
      'Pareja chilena joven (30 años aprox), de Estación Central — un hombre y una mujer embarazada de 7 meses, riendo en su cocina mientras pintan un mueblecito blanco para el bebé. Iluminación natural de ventana, paleta suave y cálida, tonos pastel. Composición cuadrada con espacio negativo arriba. Realismo cariñoso, sin perfección artificial. Aspect ratio 1:1.',
    prompt_copy:
      'Rodrigo y Camila esperan su primer hijo en julio. Necesitan saber sobre Bono Nacimiento $80.000 + posibilidad de Crédito Salud $1.5MM si surgen gastos no cubiertos por FONASA. Genera titular cariñoso, subtitular práctico con cifras, CTA que abre conversación con Andesia. Tono: te apoyamos, no vendemos.',
    titulo: 'Estamos contigo en este nuevo capítulo',
    subtitulo: '$80.000 Bono Nacimiento + Crédito Salud preferente, listo cuando lo necesites',
    cuerpo:
      'Sabemos que viene tu primer hijo en julio. Ya tienes el Bono Nacimiento de $80.000 garantizado al inscribirlo, y si surgen gastos médicos no cubiertos podemos preaprobarte un Crédito Salud por hasta $1.500.000 a CAE 19,5%. Habla con Andesia para armar tu plan.',
    cta_label: 'Hablar con Andesia',
    cta_deep_link: '/andesia/conversar?intent=parto_planificacion&persona=persona-002',
    brand_elements: CCLA_BRAND,
    share_assets: {
      caption_whatsapp: '',
      alt_text_accessibility:
        'Pareja joven pintando una cuna blanca, ella embarazada. Texto: "Estamos contigo en este nuevo capítulo. $80.000 Bono Nacimiento + Crédito Salud preferente". Botón "Hablar con Andesia".',
      hashtags: ['#BonoNacimiento', '#CajaLosAndes', '#PrimerHijo'],
    },
    generation_metadata: {
      model: 'nano-banana-pro',
      prompt_tokens: 152,
      output_tokens: 94,
      generation_time_seconds: 10.3,
      cost_usd_estimated: 0.013,
      seed: 564821,
      safety_filters_passed: true,
      groundedness_check_passed: true,
      guardrails_applied: ['ccla_brand_guidelines_v3', 'family_inclusive_imagery', 'no_predicciones_genero_bebe', 'pregnancy_safe_imagery'],
    },
    ctr_predicho_pct: 17.4,
    conversion_predicha_pct: 24.8,
  },

  /* === Card 5 — Valentina: Crédito Tapp + Beca === */
  {
    id: 'vit-005',
    persona_id: 'persona-005',
    generated_at: '2026-04-17T07:45:14-04:00',
    card_size: 'video_short_9x16',
    asset_url: 'https://cdn.andesia.cajalosandes.cl/vitrina/vit-005.mp4',
    asset_url_thumbnail: 'https://cdn.andesia.cajalosandes.cl/vitrina/vit-005_thumb.webp',
    variant_count: 3,
    selected_variant_index: 2,
    trigger: {
      tipo: 'cross_sell',
      descripcion: 'Valentina (19, INACAP Temuco, mapuche) postuló a Beca CCLA hace 12 días. Aprobada hoy por $850.000. Oportunidad: ofrecer Crédito Tapp 50 UF a CAE preferente para notebook estudio.',
      senales_input: [
        'persona.estudios.estado_beca = aprobada hoy 2026-04-17',
        'persona.intereses_declarados incluye "tecnologia"',
        'persona.notas_demo: "no tiene notebook propio, usa el laboratorio"',
        'inventario_partner.PCFactory_INACAP.notebook_lenovo_idea = $649.990',
      ],
    },
    prompt_imagen:
      'Joven mujer mapuche de 19 años, estudiante INACAP Temuco, sonriendo mientras abre la caja de su primer notebook personal en su pieza modesta pero ordenada. Detalles culturales sutiles (witral en la pared, sin estereotipos), buena luz natural. Vertical 1080x1920. La cámara captura el gesto de ilusión, no el producto. Estilo documental cariñoso. Sin filtros excesivos. Aspect ratio 9:16.',
    prompt_copy:
      'Valentina recién obtuvo su Beca CCLA $850.000. Si quiere notebook propio para estudiar, ofrecemos Crédito Tapp 50 UF (~$1.975.000) a CAE 23,8% en 24 cuotas de $98.500. Genera narración para video corto 12 segundos: 3 frases punch, copy directo, sin paternalismo. Cierre con CTA que la lleve directo al simulador Tapp.',
    titulo: 'La beca llegó. Falta tu notebook.',
    subtitulo: 'Crédito Tapp 50 UF en 24 cuotas, todo desde la app',
    cuerpo:
      '¡Felicitaciones! Tu Beca CCLA por $850.000 fue aprobada esta mañana. Si quieres complementar con un notebook tuyo, te tenemos un Crédito Tapp pre-evaluado por 50 UF (~$1.975.000) en 24 cuotas de $98.500. Convenio PC Factory te da 12% extra de descuento.',
    cta_label: 'Simular cuota Tapp',
    cta_deep_link: '/tapp/credito/simular?monto_uf=50&plazo_meses=24&ref=vit-005',
    brand_elements: CCLA_BRAND,
    share_assets: {
      caption_whatsapp:
        'Conseguí mi beca CCLA y me ofrecieron un crédito Tapp pa el notebook, todo desde la app. Si conoces a alguien estudiando, dile que se afilie po:',
      alt_text_accessibility:
        'Video corto vertical de 12 segundos: Valentina abriendo su primer notebook. Texto en pantalla: "La beca llegó. Falta tu notebook. Crédito Tapp 50 UF en 24 cuotas". CTA "Simular cuota Tapp".',
      hashtags: ['#CajaLosAndes', '#TappJovenes', '#BecaCCLA', '#Estudiantes'],
    },
    generation_metadata: {
      model: 'veo-3.1-fast',
      prompt_tokens: 184,
      output_tokens: 0,
      generation_time_seconds: 38.6,
      cost_usd_estimated: 0.087,
      seed: 920184,
      safety_filters_passed: true,
      groundedness_check_passed: true,
      guardrails_applied: [
        'representacion_cultural_pueblos_originarios_aprobada_consejo_indigena_ccla',
        'no_estereotipos',
        'cae_disclosure_required',
        'video_max_15s',
      ],
    },
    ctr_predicho_pct: 22.1,
    conversion_predicha_pct: 12.4,
  },

  /* === Card 6 — Patricia: Programa Universidad de la Experiencia === */
  {
    id: 'vit-006',
    persona_id: 'persona-003',
    generated_at: '2026-04-17T07:45:58-04:00',
    card_size: 'square_1080',
    asset_url: 'https://cdn.andesia.cajalosandes.cl/vitrina/vit-006.webp',
    asset_url_thumbnail: 'https://cdn.andesia.cajalosandes.cl/vitrina/vit-006_thumb.webp',
    variant_count: 3,
    selected_variant_index: 1,
    trigger: {
      tipo: 'reactivacion',
      descripcion: 'Patricia (67, Concepción, viuda hace 14 meses) no usa app desde hace 2 meses. Detección de patrón: aislamiento social. Programa Universidad Experiencia abre cohorte mayo en Concepción.',
      senales_input: [
        'persona.estado_civil = viuda (desde 2025-02)',
        'persona.frecuencia_uso_app = 0 sesiones últimos 60 días',
        'inventario_programa.universidad_experiencia.cohorte_mayo_concepcion = abierta',
        'memory_bank.preferencias = "le gustaba la jardinería antes"',
      ],
    },
    prompt_imagen:
      'Grupo diverso de adultos mayores chilenos (5-6 personas, 65-75 años) riendo y conversando en una mesa con plantas y materiales de jardinería en una sala iluminada estilo centro comunitario de Concepción. Inclusivo, sin estereotipos de "viejitos felices comerciales". Cuadrado 1080x1080, espacio negativo arriba. Aspect ratio 1:1.',
    prompt_copy:
      'Patricia tiene 67 años, vive en Concepción, enviudó hace 14 meses, le gustaba la jardinería antes. CCLA tiene Universidad de la Experiencia con cohorte mayo en Concepción, gratis para afiliados, talleres incluyen jardinería, fotografía con celular, y "café conversado" semanal. Genera invitación cariñosa, no condescendiente, que respete su duelo y abra una puerta.',
    titulo: 'Volver al jardín, entre amigas',
    subtitulo: 'Universidad de la Experiencia · Cohorte mayo Concepción · Gratis para afiliados',
    cuerpo:
      'Patricia, abrimos cupos para la nueva cohorte de la Universidad de la Experiencia en Concepción. Empezamos el 4 de mayo con taller de jardinería los lunes y "café conversado" los jueves. Todo presencial en nuestra sucursal Concepción Centro. No hay requisitos, no hay notas. Solo ganas de juntarse.',
    cta_label: 'Ver el programa',
    cta_deep_link: '/programas/universidad-experiencia/concepcion?ref=vit-006',
    brand_elements: CCLA_BRAND,
    share_assets: {
      caption_whatsapp: '',
      alt_text_accessibility:
        'Grupo de adultos mayores conversando alrededor de plantas en una mesa luminosa. Texto: "Volver al jardín, entre amigas. Universidad de la Experiencia, Concepción mayo". Botón "Ver el programa".',
      hashtags: ['#UniversidadExperiencia', '#CajaLosAndes', '#AdultoMayorActivo'],
    },
    generation_metadata: {
      model: 'nano-banana-pro',
      prompt_tokens: 168,
      output_tokens: 102,
      generation_time_seconds: 11.9,
      cost_usd_estimated: 0.015,
      seed: 738201,
      safety_filters_passed: true,
      groundedness_check_passed: true,
      guardrails_applied: ['adulto_mayor_inclusivo', 'no_paternalismo', 'duelo_respetuoso', 'no_promesas_emocionales'],
    },
    ctr_predicho_pct: 9.1,
    conversion_predicha_pct: 4.2,
  },
];

/* ───────────────────────────────────────────────────────────────────────────
 * Helpers
 * ─────────────────────────────────────────────────────────────────────────── */

export function getCardById(id: string): VitrinaCard | undefined {
  return VITRINA_CARDS.find((c) => c.id === id);
}

export function getCardsByPersona(persona_id: string): VitrinaCard[] {
  return VITRINA_CARDS.filter((c) => c.persona_id === persona_id);
}

export function getCardsByTriggerType(tipo: VitrinaCard['trigger']['tipo']): VitrinaCard[] {
  return VITRINA_CARDS.filter((c) => c.trigger.tipo === tipo);
}
