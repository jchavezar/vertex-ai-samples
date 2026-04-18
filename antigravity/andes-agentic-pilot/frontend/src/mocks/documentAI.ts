/* =============================================================================
 * mocks/documentAI.ts — Drop-zone "Sube tu liquidación" + visual highlight
 *
 * Dos documentos:
 *   1. Liquidación de pensión IPS — Marzo 2026, María González
 *   2. Licencia médica electrónica — Tipo 1 (enfermedad común), Diego Riquelme
 *
 * Cada documento incluye:
 *   - PDF metadata
 *   - Entidades extraídas con bounding boxes (x, y, w, h en pixeles sobre
 *     la imagen renderizada de la primera página, asumiendo render @150 dpi)
 *   - Confidence scores
 *   - Auto-fill del formulario de solicitud destino
 *
 * Procesador modelado: Document AI Custom Extractor (es) entrenado sobre
 * 1.200 muestras de liquidaciones IPS y 800 licencias médicas COMPIN.
 * ============================================================================= */

export interface BoundingBox {
  page: number;
  x: number;
  y: number;
  width: number;
  height: number;
  /** Color hex para overlay visual */
  color?: string;
}

export interface ExtractedEntity {
  type: string;
  display_label: string;
  value: string | number;
  raw_text: string;
  confidence: number;
  bbox: BoundingBox;
  validated: boolean;
  validation_source?: string;
}

export interface DocumentMetadata {
  filename: string;
  size_bytes: number;
  mime: string;
  page_count: number;
  uploaded_at: string;
  uploaded_by: string;
  channel: 'sucursal_virtual' | 'app_movil' | 'tapp' | 'whatsapp';
  preview_image_url: string;
  original_pdf_url: string;
}

export interface DocumentAIProcessing {
  processor_id: string;
  processor_display_name: string;
  processor_version: string;
  language: 'es-CL' | 'es' | 'en';
  processed_at: string;
  processing_time_ms: number;
  page_count: number;
  total_entities_detected: number;
  avg_confidence: number;
}

export interface FormAutoFillField {
  campo_id: string;
  campo_label: string;
  valor: string | number;
  source_entity: string;
  confidence: number;
  pre_validated: boolean;
}

export interface ProcessedDocument {
  id: string;
  metadata: DocumentMetadata;
  processing: DocumentAIProcessing;
  entities: ExtractedEntity[];
  destino_formulario: string;
  autofill: FormAutoFillField[];
  warnings: string[];
}

/* ─────────────────────────────────────────────────────────────────────────── */
/* === Doc 1 — Liquidación de pensión IPS (María González) ================  */
/* ─────────────────────────────────────────────────────────────────────────── */

export const LIQUIDACION_PENSION_MARIA: ProcessedDocument = {
  id: 'doc-001',
  metadata: {
    filename: 'liquidacion_pension_marzo_2026.pdf',
    size_bytes: 184_502,
    mime: 'application/pdf',
    page_count: 1,
    uploaded_at: '2026-04-20T10:30:48.000-04:00',
    uploaded_by: 'persona-001',
    channel: 'sucursal_virtual',
    preview_image_url: '/mocks/img/liquidacion_maria_p1.png',
    original_pdf_url: '/mocks/pdf/liquidacion_pension_marzo_2026.pdf',
  },
  processing: {
    processor_id: 'projects/vtxdemos/locations/us/processors/ccla-liquidacion-pension-extractor',
    processor_display_name: 'CCLA · Liquidación Pensión Custom Extractor',
    processor_version: 'pretrained-v1.4',
    language: 'es-CL',
    processed_at: '2026-04-20T10:30:49.940-04:00',
    processing_time_ms: 1_940,
    page_count: 1,
    total_entities_detected: 9,
    avg_confidence: 0.965,
  },
  entities: [
    {
      type: 'rut_titular',
      display_label: 'RUT del titular',
      value: '12.345.678-5',
      raw_text: '12.345.678-5',
      confidence: 0.99,
      bbox: { page: 1, x: 120, y: 145, width: 165, height: 23, color: '#003DA5' },
      validated: true,
      validation_source: 'cross-check con perfil persona-001',
    },
    {
      type: 'nombre_titular',
      display_label: 'Nombre completo',
      value: 'GONZALEZ PEREIRA MARIA CECILIA',
      raw_text: 'GONZALEZ PEREIRA MARIA CECILIA',
      confidence: 0.98,
      bbox: { page: 1, x: 120, y: 175, width: 420, height: 23, color: '#003DA5' },
      validated: true,
      validation_source: 'cross-check con perfil persona-001',
    },
    {
      type: 'pagador',
      display_label: 'Pagador / Entidad previsional',
      value: 'INSTITUTO DE PREVISION SOCIAL (IPS)',
      raw_text: 'I.P.S. — INSTITUTO DE PREVISION SOCIAL',
      confidence: 0.97,
      bbox: { page: 1, x: 120, y: 210, width: 340, height: 23, color: '#FFC72C' },
      validated: true,
      validation_source: 'whitelist entidades previsionales SUSESO',
    },
    {
      type: 'periodo',
      display_label: 'Periodo de la liquidación',
      value: 'MARZO 2026',
      raw_text: 'MARZO 2026',
      confidence: 0.99,
      bbox: { page: 1, x: 430, y: 145, width: 110, height: 23, color: '#FFC72C' },
      validated: true,
    },
    {
      type: 'monto_pension_bruta_clp',
      display_label: 'Pensión bruta',
      value: 542_800,
      raw_text: '$ 542.800',
      confidence: 0.96,
      bbox: { page: 1, x: 420, y: 320, width: 130, height: 23, color: '#10B981' },
      validated: true,
    },
    {
      type: 'descuento_salud_clp',
      display_label: 'Descuento salud (FONASA)',
      value: 38_660,
      raw_text: '$ 38.660',
      confidence: 0.95,
      bbox: { page: 1, x: 420, y: 345, width: 130, height: 23, color: '#10B981' },
      validated: true,
    },
    {
      type: 'descuento_credito_ccla_clp',
      display_label: 'Descuento Crédito Caja Los Andes',
      value: 16_820,
      raw_text: '$ 16.820',
      confidence: 0.93,
      bbox: { page: 1, x: 420, y: 370, width: 130, height: 23, color: '#10B981' },
      validated: true,
      validation_source: 'cross-check con producto persona-001.cred-universal',
    },
    {
      type: 'monto_liquido_clp',
      display_label: 'Líquido a pagar',
      value: 487_320,
      raw_text: '$ 487.320',
      confidence: 0.99,
      bbox: { page: 1, x: 420, y: 420, width: 130, height: 23, color: '#EF4444' },
      validated: true,
      validation_source: 'cross-check con persona-001.pension_liquida_clp',
    },
    {
      type: 'banco_deposito',
      display_label: 'Banco de depósito',
      value: 'BANCO ESTADO — Cuenta RUT',
      raw_text: 'BANCO ESTADO CTA RUT',
      confidence: 0.91,
      bbox: { page: 1, x: 120, y: 480, width: 220, height: 23, color: '#6B7280' },
      validated: true,
    },
  ],
  destino_formulario: 'Solicitud Crédito Consolidación de Deuda',
  autofill: [
    { campo_id: 'rut', campo_label: 'RUT', valor: '12.345.678-5', source_entity: 'rut_titular', confidence: 0.99, pre_validated: true },
    { campo_id: 'nombre', campo_label: 'Nombre completo', valor: 'María Cecilia González Pereira', source_entity: 'nombre_titular', confidence: 0.98, pre_validated: true },
    { campo_id: 'pagador', campo_label: 'Pagador (descuento por planilla)', valor: 'IPS', source_entity: 'pagador', confidence: 0.97, pre_validated: true },
    { campo_id: 'pension_liquida', campo_label: 'Pensión líquida mensual', valor: 487_320, source_entity: 'monto_liquido_clp', confidence: 0.99, pre_validated: true },
    { campo_id: 'cuenta_deposito', campo_label: 'Cuenta de depósito', valor: 'BANCO ESTADO Cta RUT', source_entity: 'banco_deposito', confidence: 0.91, pre_validated: false },
  ],
  warnings: [],
};

/* ─────────────────────────────────────────────────────────────────────────── */
/* === Doc 2 — Licencia médica electrónica (Diego Riquelme) ================  */
/* ─────────────────────────────────────────────────────────────────────────── */

export const LICENCIA_MEDICA_DIEGO: ProcessedDocument = {
  id: 'doc-002',
  metadata: {
    filename: 'licencia_medica_LME_45821934.pdf',
    size_bytes: 92_318,
    mime: 'application/pdf',
    page_count: 1,
    uploaded_at: '2026-04-15T08:14:22.000-04:00',
    uploaded_by: 'persona-006',
    channel: 'app_movil',
    preview_image_url: '/mocks/img/licencia_diego_p1.png',
    original_pdf_url: '/mocks/pdf/licencia_medica_LME_45821934.pdf',
  },
  processing: {
    processor_id: 'projects/vtxdemos/locations/us/processors/ccla-licencia-medica-extractor',
    processor_display_name: 'CCLA · Licencia Médica Electrónica Extractor',
    processor_version: 'pretrained-v2.1',
    language: 'es-CL',
    processed_at: '2026-04-15T08:14:25.108-04:00',
    processing_time_ms: 3_108,
    page_count: 1,
    total_entities_detected: 11,
    avg_confidence: 0.943,
  },
  entities: [
    {
      type: 'numero_licencia',
      display_label: 'N° Licencia (LME)',
      value: 'LME-45821934',
      raw_text: 'N° LME 45-82-1934',
      confidence: 0.98,
      bbox: { page: 1, x: 380, y: 90, width: 180, height: 22, color: '#003DA5' },
      validated: true,
      validation_source: 'consulta API COMPIN — número activo',
    },
    {
      type: 'rut_trabajador',
      display_label: 'RUT trabajador',
      value: '13.987.654-3',
      raw_text: '13.987.654-3',
      confidence: 0.99,
      bbox: { page: 1, x: 130, y: 165, width: 145, height: 22, color: '#003DA5' },
      validated: true,
      validation_source: 'cross-check con persona-006',
    },
    {
      type: 'nombre_trabajador',
      display_label: 'Nombre trabajador',
      value: 'DIEGO ESTEBAN RIQUELME BUSTAMANTE',
      raw_text: 'RIQUELME BUSTAMANTE DIEGO ESTEBAN',
      confidence: 0.97,
      bbox: { page: 1, x: 130, y: 195, width: 410, height: 22, color: '#003DA5' },
      validated: true,
    },
    {
      type: 'rut_medico',
      display_label: 'RUT del profesional',
      value: '14.582.901-K',
      raw_text: '14.582.901-K',
      confidence: 0.97,
      bbox: { page: 1, x: 130, y: 270, width: 145, height: 22, color: '#FFC72C' },
      validated: true,
      validation_source: 'consulta Registro Nacional Prestadores SIS',
    },
    {
      type: 'nombre_medico',
      display_label: 'Profesional emisor',
      value: 'DRA. CONSTANZA MOLINA TAPIA',
      raw_text: 'MOLINA TAPIA CONSTANZA',
      confidence: 0.94,
      bbox: { page: 1, x: 130, y: 295, width: 320, height: 22, color: '#FFC72C' },
      validated: true,
    },
    {
      type: 'especialidad',
      display_label: 'Especialidad',
      value: 'MEDICINA GENERAL',
      raw_text: 'MEDICINA GENERAL',
      confidence: 0.92,
      bbox: { page: 1, x: 130, y: 320, width: 200, height: 22, color: '#FFC72C' },
      validated: true,
    },
    {
      type: 'tipo_licencia',
      display_label: 'Tipo de licencia',
      value: 'TIPO 1 — Enfermedad o accidente común',
      raw_text: 'TIPO 1 — ENF/ACC COMUN',
      confidence: 0.96,
      bbox: { page: 1, x: 130, y: 380, width: 380, height: 22, color: '#10B981' },
      validated: true,
    },
    {
      type: 'fecha_inicio',
      display_label: 'Inicio de reposo',
      value: '2026-04-14',
      raw_text: '14-04-2026',
      confidence: 0.98,
      bbox: { page: 1, x: 130, y: 410, width: 130, height: 22, color: '#10B981' },
      validated: true,
    },
    {
      type: 'dias_reposo',
      display_label: 'Días de reposo',
      value: 7,
      raw_text: '7 (SIETE) DIAS',
      confidence: 0.97,
      bbox: { page: 1, x: 320, y: 410, width: 130, height: 22, color: '#10B981' },
      validated: true,
    },
    {
      type: 'diagnostico_cie10',
      display_label: 'Diagnóstico CIE-10',
      value: 'J11.1',
      raw_text: 'J11.1 — INFLUENZA, OTRAS MANIFESTACIONES RESP.',
      confidence: 0.91,
      bbox: { page: 1, x: 130, y: 465, width: 410, height: 22, color: '#EF4444' },
      validated: true,
      validation_source: 'whitelist CIE-10 OPS',
    },
    {
      type: 'firma_electronica_valida',
      display_label: 'Firma electrónica válida',
      value: 'SI — emitida por COMPIN-MR el 14-04-2026 08:09:12',
      raw_text: 'FIRMA ELECTRONICA AVANZADA — VALIDADA',
      confidence: 0.86,
      bbox: { page: 1, x: 100, y: 700, width: 460, height: 50, color: '#6B7280' },
      validated: true,
      validation_source: 'API SUSESO firma electrónica avanzada (Ley 19.799)',
    },
  ],
  destino_formulario: 'Trámite Licencia Médica',
  autofill: [
    { campo_id: 'numero_lme', campo_label: 'N° LME', valor: 'LME-45821934', source_entity: 'numero_licencia', confidence: 0.98, pre_validated: true },
    { campo_id: 'tipo', campo_label: 'Tipo de licencia', valor: 'Tipo 1', source_entity: 'tipo_licencia', confidence: 0.96, pre_validated: true },
    { campo_id: 'fecha_inicio', campo_label: 'Inicio reposo', valor: '2026-04-14', source_entity: 'fecha_inicio', confidence: 0.98, pre_validated: true },
    { campo_id: 'dias', campo_label: 'Días', valor: 7, source_entity: 'dias_reposo', confidence: 0.97, pre_validated: true },
    { campo_id: 'diagnostico', campo_label: 'Diagnóstico CIE-10', valor: 'J11.1', source_entity: 'diagnostico_cie10', confidence: 0.91, pre_validated: true },
  ],
  warnings: [
    'Diagnóstico J11.1 (Influenza) — sistema sugiere requerir test de laboratorio adjunto si > 5 días reposo. Pendiente validación con COMPIN.',
  ],
};

/* ─────────────────────────────────────────────────────────────────────────── */
/* === Doc 3 — Cédula de identidad (Valentina, beca) ======================  */
/* ─────────────────────────────────────────────────────────────────────────── */

export const CEDULA_VALENTINA: ProcessedDocument = {
  id: 'doc-003',
  metadata: {
    filename: 'cedula_frente_back.jpg',
    size_bytes: 312_458,
    mime: 'image/jpeg',
    page_count: 2,
    uploaded_at: '2026-04-12T19:42:11.000-04:00',
    uploaded_by: 'persona-005',
    channel: 'app_movil',
    preview_image_url: '/mocks/img/cedula_valentina.jpg',
    original_pdf_url: '/mocks/pdf/cedula_valentina.pdf',
  },
  processing: {
    processor_id: 'projects/vtxdemos/locations/us/processors/identity-id-proofing',
    processor_display_name: 'Identity Document Proofing (CL)',
    processor_version: 'GA-v3.2',
    language: 'es-CL',
    processed_at: '2026-04-12T19:42:13.880-04:00',
    processing_time_ms: 2_880,
    page_count: 2,
    total_entities_detected: 7,
    avg_confidence: 0.972,
  },
  entities: [
    { type: 'rut', display_label: 'RUT', value: '21.567.890-4', raw_text: '21.567.890-4', confidence: 0.99, bbox: { page: 1, x: 250, y: 165, width: 145, height: 22, color: '#003DA5' }, validated: true },
    { type: 'nombres', display_label: 'Nombres', value: 'VALENTINA BELEN', raw_text: 'VALENTINA BELEN', confidence: 0.98, bbox: { page: 1, x: 250, y: 200, width: 200, height: 22, color: '#003DA5' }, validated: true },
    { type: 'apellidos', display_label: 'Apellidos', value: 'AGUILERA TAPIA', raw_text: 'AGUILERA TAPIA', confidence: 0.98, bbox: { page: 1, x: 250, y: 230, width: 200, height: 22, color: '#003DA5' }, validated: true },
    { type: 'fecha_nacimiento', display_label: 'Nacimiento', value: '2006-09-18', raw_text: '18 SEP 2006', confidence: 0.97, bbox: { page: 1, x: 250, y: 260, width: 130, height: 22, color: '#FFC72C' }, validated: true },
    { type: 'nacionalidad', display_label: 'Nacionalidad', value: 'CHILENA', raw_text: 'CHILENA', confidence: 0.99, bbox: { page: 1, x: 250, y: 290, width: 100, height: 22, color: '#FFC72C' }, validated: true },
    { type: 'fecha_emision', display_label: 'Emisión', value: '2024-11-03', raw_text: '03-11-2024', confidence: 0.96, bbox: { page: 2, x: 80, y: 120, width: 130, height: 22, color: '#10B981' }, validated: true },
    { type: 'fecha_vencimiento', display_label: 'Vencimiento', value: '2034-11-03', raw_text: '03-11-2034', confidence: 0.97, bbox: { page: 2, x: 80, y: 150, width: 130, height: 22, color: '#10B981' }, validated: true },
  ],
  destino_formulario: 'Postulación Beca de Estudios CCLA 2026',
  autofill: [
    { campo_id: 'rut', campo_label: 'RUT', valor: '21.567.890-4', source_entity: 'rut', confidence: 0.99, pre_validated: true },
    { campo_id: 'nombre', campo_label: 'Nombre completo', valor: 'Valentina Belén Aguilera Tapia', source_entity: 'nombres', confidence: 0.98, pre_validated: true },
    { campo_id: 'fecha_nac', campo_label: 'Fecha de nacimiento', valor: '2006-09-18', source_entity: 'fecha_nacimiento', confidence: 0.97, pre_validated: true },
  ],
  warnings: [],
};

export const ALL_PROCESSED_DOCUMENTS = [
  LIQUIDACION_PENSION_MARIA,
  LICENCIA_MEDICA_DIEGO,
  CEDULA_VALENTINA,
];
