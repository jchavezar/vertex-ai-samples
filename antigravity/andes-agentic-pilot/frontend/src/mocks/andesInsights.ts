/* =============================================================================
 * mocks/andesInsights.ts — Conversational Analytics API (BigQuery + Looker)
 *
 * Dataset sintético de transacciones representando ~6 meses de operación CCLA
 * (oct-2025 → abr-2026), con foco en abril 2026 para el demo.
 *
 * Estructura realista anclada en:
 *   - 4.046.785 trabajadores afiliados (Memoria CCLA 2024)
 *   - 139 puntos de atención (~26 sucursales modeladas en sucursales.ts)
 *   - Mix de canales: web (45%), app Tapp (28%), sucursal (19%), CC voz (8%)
 *   - Productos top: Crédito Universal, Crédito Consolidación, Crédito Salud,
 *     Crédito Tapp, Bono Bodas de Oro, Asignación Familiar, Becas
 *
 * Las 6 NL queries pre-baked simulan el flujo "habla con tu data":
 *   usuario tipea pregunta en español → API devuelve chart spec + insight
 *
 * Fuente conceptual: Conversational Analytics API (Vertex AI) +
 * BigQuery ML.FORECAST para predicciones.
 * ============================================================================= */

export type ProductoTipo =
  | 'credito_universal'
  | 'credito_pensionados'
  | 'credito_salud'
  | 'credito_consolidacion'
  | 'credito_educacion'
  | 'credito_tapp'
  | 'bono_bodas_oro'
  | 'bono_escolar'
  | 'asignacion_familiar'
  | 'bono_nacimiento'
  | 'bono_defuncion'
  | 'beca_educacion'
  | 'turismo_hotel'
  | 'seguro_vida_familiar';

export type CanalAtencion = 'web' | 'app_tapp' | 'sucursal' | 'contact_center' | 'whatsapp_business';

export interface Transaction {
  id: string;
  fecha: string; // YYYY-MM-DD
  sucursal_id: string; // referencia a sucursales.ts
  region_codigo: string; // 'RM', 'V', 'VIII', etc
  producto: ProductoTipo;
  monto_clp: number;
  canal: CanalAtencion;
  estado: 'aprobado' | 'rechazado' | 'pendiente_doc' | 'desembolsado';
  segmento_afiliado: 'trabajador_activo' | 'pensionado' | 'pyme' | 'jovenes_18_29';
  is_first_time: boolean;
  tasa_aplicada_cae?: number;
}

export interface ChartSpec {
  chart_type: 'bar' | 'line' | 'pie' | 'area' | 'kpi_card' | 'heatmap';
  x_axis?: string;
  y_axis?: string;
  series?: string[];
  filters?: { field: string; op: string; value: string | number }[];
  data_points: Array<Record<string, string | number | null>>;
  unit?: 'clp' | 'pct' | 'count' | 'dias';
}

export interface InsightQuery {
  id: string;
  nl_query: string;
  user_role: 'gerente_general' | 'gerente_credito' | 'gerente_riesgo' | 'analista' | 'sucursal_mgr';
  generated_sql_preview: string;
  chart: ChartSpec;
  insight_summary_es: string;
  follow_up_suggestions: string[];
  generation_time_ms: number;
  data_freshness: string; // ISO timestamp
}

/* ───────────────────────────────────────────────────────────────────────────
 * TRANSACCIONES — 120 filas representativas
 * Distribución pensada para que las queries devuelvan números coherentes
 * ─────────────────────────────────────────────────────────────────────────── */

export const TRANSACTIONS: Transaction[] = [
  // === Crédito Universal (más vendido) — abril 2026 ===
  { id: 'tx-0001', fecha: '2026-04-01', sucursal_id: 'suc-providencia-cm', region_codigo: 'RM', producto: 'credito_universal', monto_clp: 2800000, canal: 'web', estado: 'desembolsado', segmento_afiliado: 'trabajador_activo', is_first_time: false, tasa_aplicada_cae: 21.4 },
  { id: 'tx-0002', fecha: '2026-04-01', sucursal_id: 'suc-maipu', region_codigo: 'RM', producto: 'credito_universal', monto_clp: 1500000, canal: 'app_tapp', estado: 'desembolsado', segmento_afiliado: 'trabajador_activo', is_first_time: true, tasa_aplicada_cae: 22.1 },
  { id: 'tx-0003', fecha: '2026-04-02', sucursal_id: 'suc-concepcion', region_codigo: 'VIII', producto: 'credito_universal', monto_clp: 4200000, canal: 'sucursal', estado: 'desembolsado', segmento_afiliado: 'trabajador_activo', is_first_time: false, tasa_aplicada_cae: 20.9 },
  { id: 'tx-0004', fecha: '2026-04-02', sucursal_id: 'suc-antofagasta', region_codigo: 'II', producto: 'credito_universal', monto_clp: 5800000, canal: 'sucursal', estado: 'aprobado', segmento_afiliado: 'trabajador_activo', is_first_time: false, tasa_aplicada_cae: 19.8 },
  { id: 'tx-0005', fecha: '2026-04-03', sucursal_id: 'suc-temuco', region_codigo: 'IX', producto: 'credito_universal', monto_clp: 1200000, canal: 'web', estado: 'desembolsado', segmento_afiliado: 'jovenes_18_29', is_first_time: true, tasa_aplicada_cae: 23.2 },
  { id: 'tx-0006', fecha: '2026-04-03', sucursal_id: 'suc-puente-alto', region_codigo: 'RM', producto: 'credito_universal', monto_clp: 3500000, canal: 'app_tapp', estado: 'desembolsado', segmento_afiliado: 'trabajador_activo', is_first_time: false, tasa_aplicada_cae: 20.4 },
  { id: 'tx-0007', fecha: '2026-04-04', sucursal_id: 'suc-vinadelmar', region_codigo: 'V', producto: 'credito_universal', monto_clp: 2100000, canal: 'sucursal', estado: 'desembolsado', segmento_afiliado: 'trabajador_activo', is_first_time: false, tasa_aplicada_cae: 21.0 },
  { id: 'tx-0008', fecha: '2026-04-05', sucursal_id: 'suc-iquique', region_codigo: 'I', producto: 'credito_universal', monto_clp: 1800000, canal: 'web', estado: 'rechazado', segmento_afiliado: 'trabajador_activo', is_first_time: true },
  { id: 'tx-0009', fecha: '2026-04-06', sucursal_id: 'suc-providencia-cm', region_codigo: 'RM', producto: 'credito_universal', monto_clp: 6500000, canal: 'web', estado: 'desembolsado', segmento_afiliado: 'trabajador_activo', is_first_time: false, tasa_aplicada_cae: 18.9 },
  { id: 'tx-0010', fecha: '2026-04-07', sucursal_id: 'suc-rancagua', region_codigo: 'VI', producto: 'credito_universal', monto_clp: 2900000, canal: 'app_tapp', estado: 'desembolsado', segmento_afiliado: 'trabajador_activo', is_first_time: false, tasa_aplicada_cae: 21.4 },
  { id: 'tx-0011', fecha: '2026-04-08', sucursal_id: 'suc-valdivia', region_codigo: 'XIV', producto: 'credito_universal', monto_clp: 1700000, canal: 'sucursal', estado: 'desembolsado', segmento_afiliado: 'trabajador_activo', is_first_time: false, tasa_aplicada_cae: 21.7 },
  { id: 'tx-0012', fecha: '2026-04-09', sucursal_id: 'suc-las-condes', region_codigo: 'RM', producto: 'credito_universal', monto_clp: 4800000, canal: 'web', estado: 'desembolsado', segmento_afiliado: 'trabajador_activo', is_first_time: false, tasa_aplicada_cae: 19.4 },
  { id: 'tx-0013', fecha: '2026-04-10', sucursal_id: 'suc-puerto-montt', region_codigo: 'X', producto: 'credito_universal', monto_clp: 2400000, canal: 'app_tapp', estado: 'desembolsado', segmento_afiliado: 'trabajador_activo', is_first_time: false, tasa_aplicada_cae: 21.2 },
  { id: 'tx-0014', fecha: '2026-04-11', sucursal_id: 'suc-talca', region_codigo: 'VII', producto: 'credito_universal', monto_clp: 1300000, canal: 'web', estado: 'desembolsado', segmento_afiliado: 'jovenes_18_29', is_first_time: true, tasa_aplicada_cae: 23.0 },
  { id: 'tx-0015', fecha: '2026-04-12', sucursal_id: 'suc-providencia-cm', region_codigo: 'RM', producto: 'credito_universal', monto_clp: 5200000, canal: 'web', estado: 'desembolsado', segmento_afiliado: 'trabajador_activo', is_first_time: false, tasa_aplicada_cae: 19.1 },

  // === Crédito Pensionados — segmento clave para María ===
  { id: 'tx-0016', fecha: '2026-04-01', sucursal_id: 'suc-providencia-cm', region_codigo: 'RM', producto: 'credito_pensionados', monto_clp: 1800000, canal: 'sucursal', estado: 'desembolsado', segmento_afiliado: 'pensionado', is_first_time: false, tasa_aplicada_cae: 18.9 },
  { id: 'tx-0017', fecha: '2026-04-03', sucursal_id: 'suc-maipu', region_codigo: 'RM', producto: 'credito_pensionados', monto_clp: 2200000, canal: 'sucursal', estado: 'desembolsado', segmento_afiliado: 'pensionado', is_first_time: false, tasa_aplicada_cae: 18.9 },
  { id: 'tx-0018', fecha: '2026-04-05', sucursal_id: 'suc-concepcion', region_codigo: 'VIII', producto: 'credito_pensionados', monto_clp: 1500000, canal: 'app_tapp', estado: 'desembolsado', segmento_afiliado: 'pensionado', is_first_time: false, tasa_aplicada_cae: 18.9 },
  { id: 'tx-0019', fecha: '2026-04-07', sucursal_id: 'suc-vinadelmar', region_codigo: 'V', producto: 'credito_pensionados', monto_clp: 1100000, canal: 'sucursal', estado: 'desembolsado', segmento_afiliado: 'pensionado', is_first_time: false, tasa_aplicada_cae: 18.9 },
  { id: 'tx-0020', fecha: '2026-04-09', sucursal_id: 'suc-temuco', region_codigo: 'IX', producto: 'credito_pensionados', monto_clp: 980000, canal: 'sucursal', estado: 'desembolsado', segmento_afiliado: 'pensionado', is_first_time: false, tasa_aplicada_cae: 18.9 },
  { id: 'tx-0021', fecha: '2026-04-11', sucursal_id: 'suc-osorno', region_codigo: 'X', producto: 'credito_pensionados', monto_clp: 1700000, canal: 'sucursal', estado: 'desembolsado', segmento_afiliado: 'pensionado', is_first_time: false, tasa_aplicada_cae: 18.9 },
  { id: 'tx-0022', fecha: '2026-04-13', sucursal_id: 'suc-la-serena', region_codigo: 'IV', producto: 'credito_pensionados', monto_clp: 2400000, canal: 'sucursal', estado: 'desembolsado', segmento_afiliado: 'pensionado', is_first_time: false, tasa_aplicada_cae: 18.9 },
  { id: 'tx-0023', fecha: '2026-04-15', sucursal_id: 'suc-providencia-cm', region_codigo: 'RM', producto: 'credito_pensionados', monto_clp: 3100000, canal: 'web', estado: 'desembolsado', segmento_afiliado: 'pensionado', is_first_time: false, tasa_aplicada_cae: 18.9 },

  // === Crédito Consolidación (la apuesta de María) ===
  { id: 'tx-0024', fecha: '2026-04-02', sucursal_id: 'suc-providencia-cm', region_codigo: 'RM', producto: 'credito_consolidacion', monto_clp: 8200000, canal: 'web', estado: 'desembolsado', segmento_afiliado: 'trabajador_activo', is_first_time: false, tasa_aplicada_cae: 18.9 },
  { id: 'tx-0025', fecha: '2026-04-05', sucursal_id: 'suc-maipu', region_codigo: 'RM', producto: 'credito_consolidacion', monto_clp: 5800000, canal: 'sucursal', estado: 'aprobado', segmento_afiliado: 'pensionado', is_first_time: false, tasa_aplicada_cae: 18.9 },
  { id: 'tx-0026', fecha: '2026-04-07', sucursal_id: 'suc-las-condes', region_codigo: 'RM', producto: 'credito_consolidacion', monto_clp: 12500000, canal: 'sucursal', estado: 'desembolsado', segmento_afiliado: 'trabajador_activo', is_first_time: false, tasa_aplicada_cae: 17.5 },
  { id: 'tx-0027', fecha: '2026-04-10', sucursal_id: 'suc-concepcion', region_codigo: 'VIII', producto: 'credito_consolidacion', monto_clp: 6700000, canal: 'web', estado: 'desembolsado', segmento_afiliado: 'trabajador_activo', is_first_time: false, tasa_aplicada_cae: 18.9 },
  { id: 'tx-0028', fecha: '2026-04-12', sucursal_id: 'suc-rancagua', region_codigo: 'VI', producto: 'credito_consolidacion', monto_clp: 4500000, canal: 'app_tapp', estado: 'desembolsado', segmento_afiliado: 'trabajador_activo', is_first_time: false, tasa_aplicada_cae: 19.1 },
  { id: 'tx-0029', fecha: '2026-04-14', sucursal_id: 'suc-temuco', region_codigo: 'IX', producto: 'credito_consolidacion', monto_clp: 7900000, canal: 'sucursal', estado: 'pendiente_doc', segmento_afiliado: 'trabajador_activo', is_first_time: false },

  // === Crédito Salud ===
  { id: 'tx-0030', fecha: '2026-04-03', sucursal_id: 'suc-providencia-cm', region_codigo: 'RM', producto: 'credito_salud', monto_clp: 1200000, canal: 'app_tapp', estado: 'desembolsado', segmento_afiliado: 'trabajador_activo', is_first_time: false, tasa_aplicada_cae: 19.5 },
  { id: 'tx-0031', fecha: '2026-04-05', sucursal_id: 'suc-puente-alto', region_codigo: 'RM', producto: 'credito_salud', monto_clp: 850000, canal: 'web', estado: 'desembolsado', segmento_afiliado: 'trabajador_activo', is_first_time: false, tasa_aplicada_cae: 19.5 },
  { id: 'tx-0032', fecha: '2026-04-08', sucursal_id: 'suc-vinadelmar', region_codigo: 'V', producto: 'credito_salud', monto_clp: 2400000, canal: 'sucursal', estado: 'desembolsado', segmento_afiliado: 'trabajador_activo', is_first_time: false, tasa_aplicada_cae: 19.5 },
  { id: 'tx-0033', fecha: '2026-04-11', sucursal_id: 'suc-antofagasta', region_codigo: 'II', producto: 'credito_salud', monto_clp: 3500000, canal: 'sucursal', estado: 'desembolsado', segmento_afiliado: 'trabajador_activo', is_first_time: false, tasa_aplicada_cae: 19.5 },
  { id: 'tx-0034', fecha: '2026-04-14', sucursal_id: 'suc-osorno', region_codigo: 'X', producto: 'credito_salud', monto_clp: 1700000, canal: 'app_tapp', estado: 'desembolsado', segmento_afiliado: 'pensionado', is_first_time: false, tasa_aplicada_cae: 19.5 },

  // === Crédito Educación ===
  { id: 'tx-0035', fecha: '2026-03-15', sucursal_id: 'suc-providencia-cm', region_codigo: 'RM', producto: 'credito_educacion', monto_clp: 1800000, canal: 'web', estado: 'desembolsado', segmento_afiliado: 'trabajador_activo', is_first_time: true, tasa_aplicada_cae: 16.4 },
  { id: 'tx-0036', fecha: '2026-03-18', sucursal_id: 'suc-temuco', region_codigo: 'IX', producto: 'credito_educacion', monto_clp: 1500000, canal: 'web', estado: 'desembolsado', segmento_afiliado: 'jovenes_18_29', is_first_time: true, tasa_aplicada_cae: 16.4 },
  { id: 'tx-0037', fecha: '2026-04-02', sucursal_id: 'suc-concepcion', region_codigo: 'VIII', producto: 'credito_educacion', monto_clp: 2100000, canal: 'sucursal', estado: 'desembolsado', segmento_afiliado: 'trabajador_activo', is_first_time: true, tasa_aplicada_cae: 16.4 },
  { id: 'tx-0038', fecha: '2026-04-09', sucursal_id: 'suc-las-condes', region_codigo: 'RM', producto: 'credito_educacion', monto_clp: 3500000, canal: 'web', estado: 'desembolsado', segmento_afiliado: 'trabajador_activo', is_first_time: false, tasa_aplicada_cae: 16.4 },

  // === Crédito Tapp (microcrédito jóvenes) ===
  { id: 'tx-0039', fecha: '2026-04-01', sucursal_id: 'suc-puente-alto', region_codigo: 'RM', producto: 'credito_tapp', monto_clp: 250000, canal: 'app_tapp', estado: 'desembolsado', segmento_afiliado: 'jovenes_18_29', is_first_time: true, tasa_aplicada_cae: 23.8 },
  { id: 'tx-0040', fecha: '2026-04-02', sucursal_id: 'suc-temuco', region_codigo: 'IX', producto: 'credito_tapp', monto_clp: 180000, canal: 'app_tapp', estado: 'desembolsado', segmento_afiliado: 'jovenes_18_29', is_first_time: true, tasa_aplicada_cae: 23.8 },
  { id: 'tx-0041', fecha: '2026-04-03', sucursal_id: 'suc-iquique', region_codigo: 'I', producto: 'credito_tapp', monto_clp: 320000, canal: 'app_tapp', estado: 'desembolsado', segmento_afiliado: 'jovenes_18_29', is_first_time: false, tasa_aplicada_cae: 23.8 },
  { id: 'tx-0042', fecha: '2026-04-04', sucursal_id: 'suc-maipu', region_codigo: 'RM', producto: 'credito_tapp', monto_clp: 420000, canal: 'app_tapp', estado: 'desembolsado', segmento_afiliado: 'trabajador_activo', is_first_time: false, tasa_aplicada_cae: 23.8 },
  { id: 'tx-0043', fecha: '2026-04-05', sucursal_id: 'suc-concepcion', region_codigo: 'VIII', producto: 'credito_tapp', monto_clp: 150000, canal: 'app_tapp', estado: 'desembolsado', segmento_afiliado: 'jovenes_18_29', is_first_time: true, tasa_aplicada_cae: 23.8 },
  { id: 'tx-0044', fecha: '2026-04-08', sucursal_id: 'suc-rancagua', region_codigo: 'VI', producto: 'credito_tapp', monto_clp: 280000, canal: 'app_tapp', estado: 'desembolsado', segmento_afiliado: 'jovenes_18_29', is_first_time: false, tasa_aplicada_cae: 23.8 },
  { id: 'tx-0045', fecha: '2026-04-10', sucursal_id: 'suc-puerto-montt', region_codigo: 'X', producto: 'credito_tapp', monto_clp: 350000, canal: 'app_tapp', estado: 'desembolsado', segmento_afiliado: 'jovenes_18_29', is_first_time: false, tasa_aplicada_cae: 23.8 },
  { id: 'tx-0046', fecha: '2026-04-13', sucursal_id: 'suc-arica', region_codigo: 'XV', producto: 'credito_tapp', monto_clp: 200000, canal: 'app_tapp', estado: 'desembolsado', segmento_afiliado: 'jovenes_18_29', is_first_time: true, tasa_aplicada_cae: 23.8 },

  // === Bono Bodas de Oro ===
  { id: 'tx-0047', fecha: '2026-04-04', sucursal_id: 'suc-maipu', region_codigo: 'RM', producto: 'bono_bodas_oro', monto_clp: 300000, canal: 'sucursal', estado: 'desembolsado', segmento_afiliado: 'pensionado', is_first_time: true },
  { id: 'tx-0048', fecha: '2026-04-08', sucursal_id: 'suc-vinadelmar', region_codigo: 'V', producto: 'bono_bodas_oro', monto_clp: 300000, canal: 'sucursal', estado: 'desembolsado', segmento_afiliado: 'pensionado', is_first_time: true },
  { id: 'tx-0049', fecha: '2026-04-12', sucursal_id: 'suc-concepcion', region_codigo: 'VIII', producto: 'bono_bodas_oro', monto_clp: 300000, canal: 'sucursal', estado: 'desembolsado', segmento_afiliado: 'pensionado', is_first_time: true },
  { id: 'tx-0050', fecha: '2026-04-15', sucursal_id: 'suc-providencia-cm', region_codigo: 'RM', producto: 'bono_bodas_oro', monto_clp: 300000, canal: 'app_tapp', estado: 'desembolsado', segmento_afiliado: 'pensionado', is_first_time: true },

  // === Bono Escolar (peak marzo) ===
  { id: 'tx-0051', fecha: '2026-03-04', sucursal_id: 'suc-puente-alto', region_codigo: 'RM', producto: 'bono_escolar', monto_clp: 67480, canal: 'app_tapp', estado: 'desembolsado', segmento_afiliado: 'trabajador_activo', is_first_time: false },
  { id: 'tx-0052', fecha: '2026-03-04', sucursal_id: 'suc-temuco', region_codigo: 'IX', producto: 'bono_escolar', monto_clp: 67480, canal: 'web', estado: 'desembolsado', segmento_afiliado: 'trabajador_activo', is_first_time: false },
  { id: 'tx-0053', fecha: '2026-03-05', sucursal_id: 'suc-maipu', region_codigo: 'RM', producto: 'bono_escolar', monto_clp: 67480, canal: 'app_tapp', estado: 'desembolsado', segmento_afiliado: 'trabajador_activo', is_first_time: false },
  { id: 'tx-0054', fecha: '2026-03-05', sucursal_id: 'suc-concepcion', region_codigo: 'VIII', producto: 'bono_escolar', monto_clp: 134960, canal: 'sucursal', estado: 'desembolsado', segmento_afiliado: 'trabajador_activo', is_first_time: false },
  { id: 'tx-0055', fecha: '2026-03-06', sucursal_id: 'suc-iquique', region_codigo: 'I', producto: 'bono_escolar', monto_clp: 67480, canal: 'web', estado: 'desembolsado', segmento_afiliado: 'trabajador_activo', is_first_time: false },
  { id: 'tx-0056', fecha: '2026-03-06', sucursal_id: 'suc-antofagasta', region_codigo: 'II', producto: 'bono_escolar', monto_clp: 202440, canal: 'app_tapp', estado: 'desembolsado', segmento_afiliado: 'trabajador_activo', is_first_time: false },
  { id: 'tx-0057', fecha: '2026-04-02', sucursal_id: 'suc-rancagua', region_codigo: 'VI', producto: 'bono_escolar', monto_clp: 67480, canal: 'web', estado: 'desembolsado', segmento_afiliado: 'trabajador_activo', is_first_time: false },

  // === Asignación Familiar (recurrente, abril 2026) ===
  { id: 'tx-0058', fecha: '2026-04-01', sucursal_id: 'suc-puente-alto', region_codigo: 'RM', producto: 'asignacion_familiar', monto_clp: 22007, canal: 'web', estado: 'desembolsado', segmento_afiliado: 'trabajador_activo', is_first_time: false },
  { id: 'tx-0059', fecha: '2026-04-01', sucursal_id: 'suc-maipu', region_codigo: 'RM', producto: 'asignacion_familiar', monto_clp: 13510, canal: 'app_tapp', estado: 'desembolsado', segmento_afiliado: 'trabajador_activo', is_first_time: false },
  { id: 'tx-0060', fecha: '2026-04-01', sucursal_id: 'suc-temuco', region_codigo: 'IX', producto: 'asignacion_familiar', monto_clp: 22007, canal: 'web', estado: 'desembolsado', segmento_afiliado: 'trabajador_activo', is_first_time: false },
  { id: 'tx-0061', fecha: '2026-04-01', sucursal_id: 'suc-concepcion', region_codigo: 'VIII', producto: 'asignacion_familiar', monto_clp: 4267, canal: 'web', estado: 'desembolsado', segmento_afiliado: 'trabajador_activo', is_first_time: false },
  { id: 'tx-0062', fecha: '2026-04-01', sucursal_id: 'suc-vinadelmar', region_codigo: 'V', producto: 'asignacion_familiar', monto_clp: 22007, canal: 'web', estado: 'desembolsado', segmento_afiliado: 'trabajador_activo', is_first_time: false },
  { id: 'tx-0063', fecha: '2026-04-01', sucursal_id: 'suc-iquique', region_codigo: 'I', producto: 'asignacion_familiar', monto_clp: 22007, canal: 'app_tapp', estado: 'desembolsado', segmento_afiliado: 'trabajador_activo', is_first_time: false },

  // === Bono Nacimiento ===
  { id: 'tx-0064', fecha: '2026-04-03', sucursal_id: 'suc-estacion-central', region_codigo: 'RM', producto: 'bono_nacimiento', monto_clp: 80000, canal: 'app_tapp', estado: 'desembolsado', segmento_afiliado: 'trabajador_activo', is_first_time: true },
  { id: 'tx-0065', fecha: '2026-04-08', sucursal_id: 'suc-temuco', region_codigo: 'IX', producto: 'bono_nacimiento', monto_clp: 80000, canal: 'sucursal', estado: 'desembolsado', segmento_afiliado: 'trabajador_activo', is_first_time: true },
  { id: 'tx-0066', fecha: '2026-04-12', sucursal_id: 'suc-puerto-montt', region_codigo: 'X', producto: 'bono_nacimiento', monto_clp: 80000, canal: 'app_tapp', estado: 'desembolsado', segmento_afiliado: 'trabajador_activo', is_first_time: true },

  // === Bono Defunción ===
  { id: 'tx-0067', fecha: '2026-04-05', sucursal_id: 'suc-concepcion', region_codigo: 'VIII', producto: 'bono_defuncion', monto_clp: 250000, canal: 'sucursal', estado: 'desembolsado', segmento_afiliado: 'pensionado', is_first_time: true },
  { id: 'tx-0068', fecha: '2026-04-09', sucursal_id: 'suc-providencia-cm', region_codigo: 'RM', producto: 'bono_defuncion', monto_clp: 250000, canal: 'sucursal', estado: 'desembolsado', segmento_afiliado: 'pensionado', is_first_time: true },

  // === Beca Educación ===
  { id: 'tx-0069', fecha: '2026-03-12', sucursal_id: 'suc-temuco', region_codigo: 'IX', producto: 'beca_educacion', monto_clp: 850000, canal: 'web', estado: 'aprobado', segmento_afiliado: 'jovenes_18_29', is_first_time: true },
  { id: 'tx-0070', fecha: '2026-03-15', sucursal_id: 'suc-concepcion', region_codigo: 'VIII', producto: 'beca_educacion', monto_clp: 850000, canal: 'web', estado: 'aprobado', segmento_afiliado: 'jovenes_18_29', is_first_time: true },
  { id: 'tx-0071', fecha: '2026-03-20', sucursal_id: 'suc-providencia-cm', region_codigo: 'RM', producto: 'beca_educacion', monto_clp: 850000, canal: 'web', estado: 'aprobado', segmento_afiliado: 'jovenes_18_29', is_first_time: true },

  // === Turismo ===
  { id: 'tx-0072', fecha: '2026-04-06', sucursal_id: 'suc-providencia-cm', region_codigo: 'RM', producto: 'turismo_hotel', monto_clp: 158000, canal: 'web', estado: 'desembolsado', segmento_afiliado: 'pensionado', is_first_time: false },
  { id: 'tx-0073', fecha: '2026-04-08', sucursal_id: 'suc-vinadelmar', region_codigo: 'V', producto: 'turismo_hotel', monto_clp: 89000, canal: 'app_tapp', estado: 'desembolsado', segmento_afiliado: 'trabajador_activo', is_first_time: false },
  { id: 'tx-0074', fecha: '2026-04-11', sucursal_id: 'suc-rancagua', region_codigo: 'VI', producto: 'turismo_hotel', monto_clp: 110000, canal: 'web', estado: 'desembolsado', segmento_afiliado: 'trabajador_activo', is_first_time: false },

  // === Seguro Vida Familiar ===
  { id: 'tx-0075', fecha: '2026-04-02', sucursal_id: 'suc-providencia-cm', region_codigo: 'RM', producto: 'seguro_vida_familiar', monto_clp: 9990, canal: 'web', estado: 'desembolsado', segmento_afiliado: 'trabajador_activo', is_first_time: true },
  { id: 'tx-0076', fecha: '2026-04-04', sucursal_id: 'suc-maipu', region_codigo: 'RM', producto: 'seguro_vida_familiar', monto_clp: 9990, canal: 'app_tapp', estado: 'desembolsado', segmento_afiliado: 'pensionado', is_first_time: true },
  { id: 'tx-0077', fecha: '2026-04-07', sucursal_id: 'suc-temuco', region_codigo: 'IX', producto: 'seguro_vida_familiar', monto_clp: 9990, canal: 'sucursal', estado: 'desembolsado', segmento_afiliado: 'trabajador_activo', is_first_time: true },
  { id: 'tx-0078', fecha: '2026-04-12', sucursal_id: 'suc-concepcion', region_codigo: 'VIII', producto: 'seguro_vida_familiar', monto_clp: 9990, canal: 'web', estado: 'desembolsado', segmento_afiliado: 'trabajador_activo', is_first_time: true },

  // === Histórico marzo 2026 (para comparativos YoY/MoM) ===
  { id: 'tx-0079', fecha: '2026-03-02', sucursal_id: 'suc-providencia-cm', region_codigo: 'RM', producto: 'credito_universal', monto_clp: 2500000, canal: 'web', estado: 'desembolsado', segmento_afiliado: 'trabajador_activo', is_first_time: false, tasa_aplicada_cae: 21.4 },
  { id: 'tx-0080', fecha: '2026-03-04', sucursal_id: 'suc-maipu', region_codigo: 'RM', producto: 'credito_universal', monto_clp: 1800000, canal: 'app_tapp', estado: 'desembolsado', segmento_afiliado: 'trabajador_activo', is_first_time: false, tasa_aplicada_cae: 21.4 },
  { id: 'tx-0081', fecha: '2026-03-08', sucursal_id: 'suc-concepcion', region_codigo: 'VIII', producto: 'credito_universal', monto_clp: 3200000, canal: 'sucursal', estado: 'desembolsado', segmento_afiliado: 'trabajador_activo', is_first_time: false, tasa_aplicada_cae: 21.4 },
  { id: 'tx-0082', fecha: '2026-03-11', sucursal_id: 'suc-temuco', region_codigo: 'IX', producto: 'credito_universal', monto_clp: 1400000, canal: 'web', estado: 'desembolsado', segmento_afiliado: 'jovenes_18_29', is_first_time: true, tasa_aplicada_cae: 23.2 },
  { id: 'tx-0083', fecha: '2026-03-15', sucursal_id: 'suc-vinadelmar', region_codigo: 'V', producto: 'credito_universal', monto_clp: 2100000, canal: 'sucursal', estado: 'desembolsado', segmento_afiliado: 'trabajador_activo', is_first_time: false, tasa_aplicada_cae: 21.0 },
  { id: 'tx-0084', fecha: '2026-03-19', sucursal_id: 'suc-las-condes', region_codigo: 'RM', producto: 'credito_universal', monto_clp: 5500000, canal: 'web', estado: 'desembolsado', segmento_afiliado: 'trabajador_activo', is_first_time: false, tasa_aplicada_cae: 19.4 },
  { id: 'tx-0085', fecha: '2026-03-22', sucursal_id: 'suc-puente-alto', region_codigo: 'RM', producto: 'credito_universal', monto_clp: 2700000, canal: 'app_tapp', estado: 'desembolsado', segmento_afiliado: 'trabajador_activo', is_first_time: false, tasa_aplicada_cae: 21.4 },
  { id: 'tx-0086', fecha: '2026-03-25', sucursal_id: 'suc-rancagua', region_codigo: 'VI', producto: 'credito_universal', monto_clp: 1900000, canal: 'web', estado: 'desembolsado', segmento_afiliado: 'trabajador_activo', is_first_time: false, tasa_aplicada_cae: 21.4 },

  // === Histórico abril 2025 (YoY) ===
  { id: 'tx-0087', fecha: '2025-04-02', sucursal_id: 'suc-providencia-cm', region_codigo: 'RM', producto: 'credito_universal', monto_clp: 2200000, canal: 'web', estado: 'desembolsado', segmento_afiliado: 'trabajador_activo', is_first_time: false, tasa_aplicada_cae: 23.1 },
  { id: 'tx-0088', fecha: '2025-04-05', sucursal_id: 'suc-maipu', region_codigo: 'RM', producto: 'credito_universal', monto_clp: 1300000, canal: 'sucursal', estado: 'desembolsado', segmento_afiliado: 'trabajador_activo', is_first_time: true, tasa_aplicada_cae: 24.0 },
  { id: 'tx-0089', fecha: '2025-04-09', sucursal_id: 'suc-concepcion', region_codigo: 'VIII', producto: 'credito_universal', monto_clp: 3800000, canal: 'sucursal', estado: 'desembolsado', segmento_afiliado: 'trabajador_activo', is_first_time: false, tasa_aplicada_cae: 22.9 },
  { id: 'tx-0090', fecha: '2025-04-12', sucursal_id: 'suc-temuco', region_codigo: 'IX', producto: 'credito_universal', monto_clp: 1100000, canal: 'web', estado: 'desembolsado', segmento_afiliado: 'jovenes_18_29', is_first_time: true, tasa_aplicada_cae: 24.5 },
  { id: 'tx-0091', fecha: '2025-04-16', sucursal_id: 'suc-las-condes', region_codigo: 'RM', producto: 'credito_universal', monto_clp: 4900000, canal: 'web', estado: 'desembolsado', segmento_afiliado: 'trabajador_activo', is_first_time: false, tasa_aplicada_cae: 21.2 },

  // === Casos rechazados / pendientes (para mora analytics) ===
  { id: 'tx-0092', fecha: '2026-04-02', sucursal_id: 'suc-arica', region_codigo: 'XV', producto: 'credito_universal', monto_clp: 2400000, canal: 'web', estado: 'rechazado', segmento_afiliado: 'trabajador_activo', is_first_time: true },
  { id: 'tx-0093', fecha: '2026-04-04', sucursal_id: 'suc-coyhaique', region_codigo: 'XI', producto: 'credito_universal', monto_clp: 1700000, canal: 'sucursal', estado: 'rechazado', segmento_afiliado: 'trabajador_activo', is_first_time: false },
  { id: 'tx-0094', fecha: '2026-04-06', sucursal_id: 'suc-iquique', region_codigo: 'I', producto: 'credito_consolidacion', monto_clp: 5200000, canal: 'web', estado: 'pendiente_doc', segmento_afiliado: 'trabajador_activo', is_first_time: false },
  { id: 'tx-0095', fecha: '2026-04-09', sucursal_id: 'suc-puerto-montt', region_codigo: 'X', producto: 'credito_salud', monto_clp: 1900000, canal: 'app_tapp', estado: 'pendiente_doc', segmento_afiliado: 'trabajador_activo', is_first_time: true },
  { id: 'tx-0096', fecha: '2026-04-11', sucursal_id: 'suc-punta-arenas', region_codigo: 'XII', producto: 'credito_universal', monto_clp: 1500000, canal: 'sucursal', estado: 'rechazado', segmento_afiliado: 'jovenes_18_29', is_first_time: true },

  // === Volumen extra abril 2026 (suba YoY) ===
  { id: 'tx-0097', fecha: '2026-04-13', sucursal_id: 'suc-providencia-cm', region_codigo: 'RM', producto: 'credito_universal', monto_clp: 3300000, canal: 'web', estado: 'desembolsado', segmento_afiliado: 'trabajador_activo', is_first_time: false, tasa_aplicada_cae: 20.8 },
  { id: 'tx-0098', fecha: '2026-04-14', sucursal_id: 'suc-maipu', region_codigo: 'RM', producto: 'credito_universal', monto_clp: 2200000, canal: 'app_tapp', estado: 'desembolsado', segmento_afiliado: 'trabajador_activo', is_first_time: false, tasa_aplicada_cae: 21.4 },
  { id: 'tx-0099', fecha: '2026-04-15', sucursal_id: 'suc-concepcion', region_codigo: 'VIII', producto: 'credito_universal', monto_clp: 4100000, canal: 'sucursal', estado: 'desembolsado', segmento_afiliado: 'trabajador_activo', is_first_time: false, tasa_aplicada_cae: 20.9 },
  { id: 'tx-0100', fecha: '2026-04-15', sucursal_id: 'suc-vinadelmar', region_codigo: 'V', producto: 'credito_universal', monto_clp: 1800000, canal: 'web', estado: 'desembolsado', segmento_afiliado: 'trabajador_activo', is_first_time: false, tasa_aplicada_cae: 21.0 },
  { id: 'tx-0101', fecha: '2026-04-15', sucursal_id: 'suc-temuco', region_codigo: 'IX', producto: 'credito_universal', monto_clp: 1600000, canal: 'app_tapp', estado: 'desembolsado', segmento_afiliado: 'jovenes_18_29', is_first_time: true, tasa_aplicada_cae: 23.2 },
  { id: 'tx-0102', fecha: '2026-04-16', sucursal_id: 'suc-providencia-cm', region_codigo: 'RM', producto: 'credito_pensionados', monto_clp: 1500000, canal: 'sucursal', estado: 'desembolsado', segmento_afiliado: 'pensionado', is_first_time: false, tasa_aplicada_cae: 18.9 },
  { id: 'tx-0103', fecha: '2026-04-16', sucursal_id: 'suc-osorno', region_codigo: 'X', producto: 'credito_pensionados', monto_clp: 2100000, canal: 'sucursal', estado: 'desembolsado', segmento_afiliado: 'pensionado', is_first_time: false, tasa_aplicada_cae: 18.9 },
  { id: 'tx-0104', fecha: '2026-04-16', sucursal_id: 'suc-rancagua', region_codigo: 'VI', producto: 'credito_consolidacion', monto_clp: 6800000, canal: 'sucursal', estado: 'desembolsado', segmento_afiliado: 'trabajador_activo', is_first_time: false, tasa_aplicada_cae: 18.9 },
  { id: 'tx-0105', fecha: '2026-04-17', sucursal_id: 'suc-las-condes', region_codigo: 'RM', producto: 'credito_consolidacion', monto_clp: 9400000, canal: 'web', estado: 'desembolsado', segmento_afiliado: 'trabajador_activo', is_first_time: false, tasa_aplicada_cae: 17.5 },

  // === WhatsApp Business como canal (lanzamiento abril) ===
  { id: 'tx-0106', fecha: '2026-04-10', sucursal_id: 'suc-providencia-cm', region_codigo: 'RM', producto: 'credito_tapp', monto_clp: 250000, canal: 'whatsapp_business', estado: 'desembolsado', segmento_afiliado: 'trabajador_activo', is_first_time: false, tasa_aplicada_cae: 23.8 },
  { id: 'tx-0107', fecha: '2026-04-11', sucursal_id: 'suc-maipu', region_codigo: 'RM', producto: 'credito_tapp', monto_clp: 180000, canal: 'whatsapp_business', estado: 'desembolsado', segmento_afiliado: 'jovenes_18_29', is_first_time: true, tasa_aplicada_cae: 23.8 },
  { id: 'tx-0108', fecha: '2026-04-13', sucursal_id: 'suc-concepcion', region_codigo: 'VIII', producto: 'credito_tapp', monto_clp: 320000, canal: 'whatsapp_business', estado: 'desembolsado', segmento_afiliado: 'jovenes_18_29', is_first_time: false, tasa_aplicada_cae: 23.8 },

  // === Más beneficios sociales abril 2026 ===
  { id: 'tx-0109', fecha: '2026-04-13', sucursal_id: 'suc-puente-alto', region_codigo: 'RM', producto: 'asignacion_familiar', monto_clp: 22007, canal: 'web', estado: 'desembolsado', segmento_afiliado: 'trabajador_activo', is_first_time: false },
  { id: 'tx-0110', fecha: '2026-04-13', sucursal_id: 'suc-osorno', region_codigo: 'X', producto: 'asignacion_familiar', monto_clp: 22007, canal: 'web', estado: 'desembolsado', segmento_afiliado: 'trabajador_activo', is_first_time: false },
  { id: 'tx-0111', fecha: '2026-04-14', sucursal_id: 'suc-arica', region_codigo: 'XV', producto: 'asignacion_familiar', monto_clp: 22007, canal: 'app_tapp', estado: 'desembolsado', segmento_afiliado: 'trabajador_activo', is_first_time: false },
  { id: 'tx-0112', fecha: '2026-04-15', sucursal_id: 'suc-coyhaique', region_codigo: 'XI', producto: 'asignacion_familiar', monto_clp: 22007, canal: 'web', estado: 'desembolsado', segmento_afiliado: 'trabajador_activo', is_first_time: false },
  { id: 'tx-0113', fecha: '2026-04-16', sucursal_id: 'suc-punta-arenas', region_codigo: 'XII', producto: 'asignacion_familiar', monto_clp: 13510, canal: 'sucursal', estado: 'desembolsado', segmento_afiliado: 'trabajador_activo', is_first_time: false },

  // === Otros segmentos ===
  { id: 'tx-0114', fecha: '2026-04-08', sucursal_id: 'suc-iquique', region_codigo: 'I', producto: 'credito_universal', monto_clp: 4200000, canal: 'sucursal', estado: 'desembolsado', segmento_afiliado: 'pyme', is_first_time: false, tasa_aplicada_cae: 18.4 },
  { id: 'tx-0115', fecha: '2026-04-10', sucursal_id: 'suc-antofagasta', region_codigo: 'II', producto: 'credito_universal', monto_clp: 3800000, canal: 'sucursal', estado: 'desembolsado', segmento_afiliado: 'pyme', is_first_time: false, tasa_aplicada_cae: 18.4 },
  { id: 'tx-0116', fecha: '2026-04-12', sucursal_id: 'suc-puerto-montt', region_codigo: 'X', producto: 'credito_universal', monto_clp: 2900000, canal: 'sucursal', estado: 'desembolsado', segmento_afiliado: 'pyme', is_first_time: false, tasa_aplicada_cae: 18.4 },
  { id: 'tx-0117', fecha: '2026-04-14', sucursal_id: 'suc-providencia-cm', region_codigo: 'RM', producto: 'turismo_hotel', monto_clp: 79000, canal: 'web', estado: 'desembolsado', segmento_afiliado: 'pensionado', is_first_time: false },
  { id: 'tx-0118', fecha: '2026-04-15', sucursal_id: 'suc-vinadelmar', region_codigo: 'V', producto: 'credito_salud', monto_clp: 1100000, canal: 'app_tapp', estado: 'desembolsado', segmento_afiliado: 'pensionado', is_first_time: false, tasa_aplicada_cae: 19.5 },
  { id: 'tx-0119', fecha: '2026-04-16', sucursal_id: 'suc-las-condes', region_codigo: 'RM', producto: 'seguro_vida_familiar', monto_clp: 9990, canal: 'web', estado: 'desembolsado', segmento_afiliado: 'trabajador_activo', is_first_time: true },
  { id: 'tx-0120', fecha: '2026-04-17', sucursal_id: 'suc-maipu', region_codigo: 'RM', producto: 'credito_consolidacion', monto_clp: 7200000, canal: 'app_tapp', estado: 'pendiente_doc', segmento_afiliado: 'pensionado', is_first_time: false },
];

/* ───────────────────────────────────────────────────────────────────────────
 * 6 PRE-BAKED NL QUERIES
 * ─────────────────────────────────────────────────────────────────────────── */

export const INSIGHT_QUERIES: InsightQuery[] = [
  {
    id: 'q-001',
    nl_query: '¿Cuánto colocamos en Crédito Universal esta semana versus la semana pasada?',
    user_role: 'gerente_credito',
    generated_sql_preview:
      "SELECT DATE_TRUNC(fecha, WEEK) AS semana, SUM(monto_clp) AS total_colocado\nFROM ccla_dwh.transactions\nWHERE producto = 'credito_universal'\n  AND estado = 'desembolsado'\n  AND fecha BETWEEN '2026-04-06' AND '2026-04-19'\nGROUP BY 1 ORDER BY 1;",
    chart: {
      chart_type: 'bar',
      x_axis: 'semana',
      y_axis: 'total_colocado_mm_clp',
      unit: 'clp',
      data_points: [
        { semana: '2026-W15 (06-12 abr)', total_colocado_mm_clp: 28.2 },
        { semana: '2026-W16 (13-19 abr)', total_colocado_mm_clp: 33.7 },
      ],
    },
    insight_summary_es:
      'Crédito Universal subió 19,5% semana sobre semana ($28,2 MM CLP → $33,7 MM CLP). El alza viene principalmente de Las Condes (+42%) y Concepción (+28%). Posible efecto del lanzamiento de la campaña "Otoño Tasa Fija" del 13 de abril.',
    follow_up_suggestions: [
      '¿En qué canal se concentra el alza?',
      'Compara este mes contra abril 2025',
      '¿Cuál fue la tasa CAE promedio aplicada esta semana?',
    ],
    generation_time_ms: 1840,
    data_freshness: '2026-04-17T08:30:00-04:00',
  },
  {
    id: 'q-002',
    nl_query: 'Muéstrame la mora regional de los últimos 30 días, peor a mejor',
    user_role: 'gerente_riesgo',
    generated_sql_preview:
      "SELECT region_codigo, SAFE_DIVIDE(SUM(IF(estado='rechazado',1,0)), COUNT(*))*100 AS pct_rechazo,\n  COUNT(*) AS solicitudes\nFROM ccla_dwh.transactions\nWHERE fecha >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)\nGROUP BY region_codigo\nORDER BY pct_rechazo DESC;",
    chart: {
      chart_type: 'bar',
      x_axis: 'region',
      y_axis: 'pct_rechazo',
      unit: 'pct',
      data_points: [
        { region: 'XII Magallanes', pct_rechazo: 14.3 },
        { region: 'XI Aysén', pct_rechazo: 12.5 },
        { region: 'XV Arica', pct_rechazo: 11.2 },
        { region: 'I Tarapacá', pct_rechazo: 9.8 },
        { region: 'IX La Araucanía', pct_rechazo: 7.4 },
        { region: 'X Los Lagos', pct_rechazo: 6.9 },
        { region: 'VIII Biobío', pct_rechazo: 5.1 },
        { region: 'VII Maule', pct_rechazo: 4.8 },
        { region: 'VI O\'Higgins', pct_rechazo: 4.2 },
        { region: 'V Valparaíso', pct_rechazo: 3.9 },
        { region: 'RM Metropolitana', pct_rechazo: 3.4 },
        { region: 'IV Coquimbo', pct_rechazo: 3.1 },
        { region: 'II Antofagasta', pct_rechazo: 2.8 },
      ],
    },
    insight_summary_es:
      'Las regiones extremas (XII Magallanes 14,3% y XI Aysén 12,5%) tienen tasas de rechazo 4× sobre el promedio nacional (3,8%). El driver principal es score crediticio bajo en primer-time applicants. Recomendación: revisar política de scoring para zonas con menor densidad de información comercial Equifax.',
    follow_up_suggestions: [
      '¿Qué % de los rechazados eran primera solicitud?',
      'Desglosa Magallanes por sucursal',
      '¿Cuántos de los rechazos podrían recuperarse con codeudor?',
    ],
    generation_time_ms: 2210,
    data_freshness: '2026-04-17T08:30:00-04:00',
  },
  {
    id: 'q-003',
    nl_query: 'Comparativo de desembolsos Q1 2025 vs Q1 2026 por canal',
    user_role: 'gerente_general',
    generated_sql_preview:
      "SELECT canal, EXTRACT(YEAR FROM fecha) AS year, SUM(monto_clp) AS total\nFROM ccla_dwh.transactions\nWHERE estado = 'desembolsado'\n  AND fecha BETWEEN '2025-01-01' AND '2026-03-31'\n  AND EXTRACT(QUARTER FROM fecha) = 1\nGROUP BY canal, year;",
    chart: {
      chart_type: 'bar',
      x_axis: 'canal',
      y_axis: 'total_mm_clp',
      series: ['Q1 2025', 'Q1 2026'],
      unit: 'clp',
      data_points: [
        { canal: 'Web', 'Q1 2025': 184500, 'Q1 2026': 198200 },
        { canal: 'App Tapp', 'Q1 2025': 92300, 'Q1 2026': 138400 },
        { canal: 'Sucursal', 'Q1 2025': 142800, 'Q1 2026': 128900 },
        { canal: 'Contact Center', 'Q1 2025': 38400, 'Q1 2026': 31200 },
        { canal: 'WhatsApp Business', 'Q1 2025': 0, 'Q1 2026': 12800 },
      ],
    },
    insight_summary_es:
      'App Tapp creció +50% YoY ($92,3 MM → $138,4 MM CLP), confirmando la tesis de migración a canales digitales. Sucursal cayó -9,7% pero sigue siendo crítico para crédito de altos montos. WhatsApp Business (lanzado en febrero 2026) ya representa $12,8 MM CLP en Q1, principalmente Crédito Tapp en jóvenes 18-29.',
    follow_up_suggestions: [
      '¿Cuál es el costo de adquisición por canal?',
      'Ticket promedio Tapp vs sucursal',
      '¿Cuántos clientes nuevos trajo WhatsApp Business?',
    ],
    generation_time_ms: 2640,
    data_freshness: '2026-04-17T08:30:00-04:00',
  },
  {
    id: 'q-004',
    nl_query: '¿Cuántos beneficios sociales pagamos este mes y a quiénes?',
    user_role: 'gerente_general',
    generated_sql_preview:
      "SELECT producto, COUNT(*) AS pagos, SUM(monto_clp) AS total_clp,\n  AVG(monto_clp) AS ticket_promedio\nFROM ccla_dwh.transactions\nWHERE producto IN ('bono_bodas_oro','bono_escolar','asignacion_familiar','bono_nacimiento','bono_defuncion','beca_educacion')\n  AND fecha >= '2026-04-01'\n  AND estado = 'desembolsado'\nGROUP BY producto ORDER BY total_clp DESC;",
    chart: {
      chart_type: 'pie',
      unit: 'clp',
      data_points: [
        { producto: 'Asignación Familiar', pagos: 412580, total_clp: 7842900000 },
        { producto: 'Bono Bodas de Oro', pagos: 2180, total_clp: 654000000 },
        { producto: 'Bono Defunción', pagos: 1890, total_clp: 472500000 },
        { producto: 'Bono Nacimiento', pagos: 4720, total_clp: 377600000 },
        { producto: 'Bono Escolar', pagos: 1284, total_clp: 86660320 },
        { producto: 'Beca Educación', pagos: 87, total_clp: 73950000 },
      ],
    },
    insight_summary_es:
      'En abril 2026 se pagaron $9.508 MM CLP en beneficios sociales a 422.741 afiliados. Asignación Familiar concentra el 82,5% del monto. Destaca el aumento de 23% en Bono Defunción versus marzo (efecto invierno temprano + temporada gripe). Bodas de Oro ya superó la meta mensual (1.800 → 2.180).',
    follow_up_suggestions: [
      '¿Qué comuna tiene más Bonos Bodas de Oro?',
      'Ticket promedio de Bono Defunción vs años anteriores',
      '¿Quiénes son afiliados elegibles que NO han cobrado?',
    ],
    generation_time_ms: 1950,
    data_freshness: '2026-04-17T08:30:00-04:00',
  },
  {
    id: 'q-005',
    nl_query: 'Predice los desembolsos de Crédito Consolidación para mayo y junio',
    user_role: 'gerente_credito',
    generated_sql_preview:
      "SELECT * FROM ML.FORECAST(\n  MODEL `ccla_ml.consolidacion_arima_plus_xreg`,\n  STRUCT(60 AS horizon, 0.95 AS confidence_level)\n) WHERE fecha BETWEEN '2026-05-01' AND '2026-06-30';",
    chart: {
      chart_type: 'line',
      x_axis: 'mes',
      y_axis: 'monto_predicho_mm_clp',
      series: ['Histórico', 'Pronóstico', 'Banda 95%'],
      unit: 'clp',
      data_points: [
        { mes: '2026-01', historico: 1840, pronostico: null, banda_inf: null, banda_sup: null },
        { mes: '2026-02', historico: 2120, pronostico: null, banda_inf: null, banda_sup: null },
        { mes: '2026-03', historico: 2580, pronostico: null, banda_inf: null, banda_sup: null },
        { mes: '2026-04', historico: 2890, pronostico: null, banda_inf: null, banda_sup: null },
        { mes: '2026-05', historico: null, pronostico: 3220, banda_inf: 2940, banda_sup: 3500 },
        { mes: '2026-06', historico: null, pronostico: 3480, banda_inf: 3140, banda_sup: 3820 },
      ],
    },
    insight_summary_es:
      'El modelo ARIMA+ proyecta $3.220 MM CLP en mayo (+11,4% MoM) y $3.480 MM CLP en junio (+8,1% MoM) en Crédito Consolidación. El driver principal es la desinflación del IPC (4,2% → 3,8% YoY), que reduce TMC y mejora la propuesta de portabilidad. Confianza 95%. Recomendación: aumentar provisiones IFRS 9 stage 1 en 12% para Q2.',
    follow_up_suggestions: [
      '¿Qué pasaría si la TPM sube 25 pb?',
      'Desglosa la predicción por región',
      '¿Cuánto del crecimiento es nuevo cliente vs portabilidad?',
    ],
    generation_time_ms: 4280,
    data_freshness: '2026-04-17T08:30:00-04:00',
  },
  {
    id: 'q-006',
    nl_query: '¿Qué sucursales tienen el mejor ticket promedio en Crédito Pensionados?',
    user_role: 'sucursal_mgr',
    generated_sql_preview:
      "SELECT s.nombre AS sucursal, s.region_codigo, COUNT(*) AS ops, AVG(t.monto_clp) AS ticket_promedio\nFROM ccla_dwh.transactions t JOIN ccla_dim.sucursales s USING(sucursal_id)\nWHERE t.producto = 'credito_pensionados' AND t.estado = 'desembolsado'\n  AND t.fecha >= DATE_SUB(CURRENT_DATE(), INTERVAL 90 DAY)\nGROUP BY 1,2\nHAVING ops >= 5\nORDER BY ticket_promedio DESC LIMIT 10;",
    chart: {
      chart_type: 'bar',
      x_axis: 'sucursal',
      y_axis: 'ticket_promedio_clp',
      unit: 'clp',
      data_points: [
        { sucursal: 'Providencia (CM)', region: 'RM', ops: 84, ticket_promedio_clp: 2950000 },
        { sucursal: 'La Serena', region: 'IV', ops: 21, ticket_promedio_clp: 2410000 },
        { sucursal: 'Las Condes', region: 'RM', ops: 32, ticket_promedio_clp: 2310000 },
        { sucursal: 'Maipú', region: 'RM', ops: 48, ticket_promedio_clp: 2150000 },
        { sucursal: 'Concepción', region: 'VIII', ops: 41, ticket_promedio_clp: 1890000 },
        { sucursal: 'Osorno', region: 'X', ops: 18, ticket_promedio_clp: 1710000 },
        { sucursal: 'Viña del Mar', region: 'V', ops: 27, ticket_promedio_clp: 1620000 },
        { sucursal: 'Antofagasta', region: 'II', ops: 15, ticket_promedio_clp: 1480000 },
        { sucursal: 'Temuco', region: 'IX', ops: 31, ticket_promedio_clp: 1340000 },
        { sucursal: 'Rancagua', region: 'VI', ops: 22, ticket_promedio_clp: 1220000 },
      ],
    },
    insight_summary_es:
      'Providencia Casa Matriz lidera ticket promedio con $2,95 MM CLP en Crédito Pensionados, 2,4× sobre Rancagua ($1,22 MM). El alto ticket correlaciona con pensiones más altas en RM oriente. Maipú destaca por volumen (48 ops en 90 días, top 4). Oportunidad: capacitar a Rancagua y Antofagasta en venta consultiva para subir ticket promedio.',
    follow_up_suggestions: [
      '¿Qué % de los créditos Pensionados se firman digital vs presencial?',
      'Cross-sell: ¿estos clientes tienen Bodas de Oro?',
      'Comparativo NPS de sucursales top vs bottom',
    ],
    generation_time_ms: 2090,
    data_freshness: '2026-04-17T08:30:00-04:00',
  },
];

/* ───────────────────────────────────────────────────────────────────────────
 * KPI CARDS PRE-AGGREGATED (header del dashboard)
 * ─────────────────────────────────────────────────────────────────────────── */

export interface KpiCard {
  id: string;
  label: string;
  value: string;
  delta_pct: number;
  delta_period: string;
  trend: 'up' | 'down' | 'flat';
  is_positive: boolean;
}

export const KPI_CARDS_ABRIL_2026: KpiCard[] = [
  { id: 'kpi-001', label: 'Colocaciones MTD', value: '$118.4 MM CLP', delta_pct: 12.7, delta_period: 'vs abril 2025 MTD', trend: 'up', is_positive: true },
  { id: 'kpi-002', label: 'Solicitudes recibidas', value: '38.420', delta_pct: 18.3, delta_period: 'vs marzo 2026', trend: 'up', is_positive: true },
  { id: 'kpi-003', label: 'Tasa aprobación', value: '94.6%', delta_pct: 0.4, delta_period: 'vs marzo 2026', trend: 'up', is_positive: true },
  { id: 'kpi-004', label: 'Ticket promedio', value: '$2.84 MM CLP', delta_pct: -3.1, delta_period: 'vs marzo 2026', trend: 'down', is_positive: false },
  { id: 'kpi-005', label: 'Beneficios sociales pagados', value: '$9.508 MM CLP', delta_pct: 8.9, delta_period: 'vs marzo 2026', trend: 'up', is_positive: true },
  { id: 'kpi-006', label: 'Mora 30+ días', value: '4.2%', delta_pct: -0.3, delta_period: 'vs marzo 2026', trend: 'down', is_positive: true },
  { id: 'kpi-007', label: 'NPS afiliados', value: '74', delta_pct: 3.0, delta_period: 'vs Q1 2026', trend: 'up', is_positive: true },
  { id: 'kpi-008', label: 'Atenciones canal digital', value: '76.4%', delta_pct: 5.2, delta_period: 'vs abril 2025', trend: 'up', is_positive: true },
];

/* ───────────────────────────────────────────────────────────────────────────
 * Helpers
 * ─────────────────────────────────────────────────────────────────────────── */

export function getInsightById(id: string): InsightQuery | undefined {
  return INSIGHT_QUERIES.find((q) => q.id === id);
}

export function getTransactionsByProducto(producto: ProductoTipo): Transaction[] {
  return TRANSACTIONS.filter((t) => t.producto === producto);
}

export function getTransactionsByRegion(region_codigo: string): Transaction[] {
  return TRANSACTIONS.filter((t) => t.region_codigo === region_codigo);
}

export function getTransactionsByDateRange(start: string, end: string): Transaction[] {
  return TRANSACTIONS.filter((t) => t.fecha >= start && t.fecha <= end);
}
