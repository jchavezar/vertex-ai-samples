/* =============================================================================
 * mocks/productos.ts — Catálogo de productos Caja Los Andes
 *
 * Productos verificados contra:
 *  - frontend/scraped/credito-social.html  (nav primaria + nombres exactos)
 *  - https://www.cajalosandes.cl/creditos/* (categorías oficiales)
 *  - docs/caja_los_andes_research.md §A.5 (líneas de negocio)
 *  - docs/wow_features_apr2026.md §3 Add-on #1
 *
 * Tasas y montos: rangos plausibles abr-2026 anclados en:
 *  - Tasa Máxima Convencional (TMC) BCCh ene-feb 2026 (créditos no reaj. >90 días)
 *    operación promedio sistema: ~25-28% anual para consumo, ~16% no reajustables
 *  - REDEC Ley 21.680 vigente
 *  - Bono Escolar 2025 monto $64.574 (Memoria Cajas Chile 2024)
 *  - Bono Bodas de Oro Ley 20.595 monto $300.000 — fuente: SUSESO Bonos
 *  - Asignación Familiar tramos 2025: $22.007 / $13.500 / $4.267 / $0
 *    (proyección 2026 +4,5% IPC = $22.997 / $14.108 / $4.459 / $0)
 *
 * MARCAR como [verificación pendiente]:
 *  - tasas exactas CAE específicas — varían diaria/semanalmente y CCLA no las
 *    publica en HTML estático.
 * ============================================================================= */

export type Moneda = 'CLP' | 'UF' | 'USD';

export interface RangoMonto {
  min: number;
  max: number;
  moneda: Moneda;
}

export interface RangoPlazo {
  min_meses: number;
  max_meses: number;
}

export interface Tasa {
  cae_anual_pct: number; // ej. 18.9
  tasa_interes_mensual_pct: number; // ej. 1.45
  notas?: string;
}

/* -------------------------- CRÉDITOS -------------------------------------- */

export interface Credito {
  id: string;
  nombre: string;
  descripcion_corta: string;
  descripcion_larga: string;
  url_oficial: string;
  audiencias: ('Trabajadores' | 'Pensionados' | 'Empresas' | 'Estudiantes')[];
  monto: RangoMonto;
  plazo: RangoPlazo;
  tasa_referencial: Tasa;
  cuota_minima_clp?: number;
  requisitos: string[];
  documentos_requeridos: string[];
  desembolso_promesa: string;
  garantia: 'sin garantía' | 'descuento por planilla' | 'pagaré' | 'hipoteca';
  ley_aplicable: string[];
  destacado_homepage: boolean;
  badge?: 'Nuevo' | 'Más solicitado' | 'Express' | 'Pensionados';
}

export const CREDITO_UNIVERSAL: Credito = {
  id: 'cred-universal',
  nombre: 'Crédito Universal',
  descripcion_corta:
    'Crédito de libre disposición para trabajadores afiliados, con descuento por planilla.',
  descripcion_larga:
    'Crédito Universal es el crédito social tradicional de Caja Los Andes para trabajadores afiliados. Permite financiar lo que necesites — gastos personales, viajes, mejoras del hogar — con cuota fija mensual descontada directamente de tu liquidación. La cuota total no puede superar el 25% de tu remuneración líquida (tope reglamentario).',
  url_oficial: 'https://www.cajalosandes.cl/creditos/credito-universal',
  audiencias: ['Trabajadores'],
  monto: { min: 100_000, max: 30_000_000, moneda: 'CLP' },
  plazo: { min_meses: 6, max_meses: 60 },
  tasa_referencial: {
    cae_anual_pct: 21.4,
    tasa_interes_mensual_pct: 1.62,
    notas: 'CAE de referencia abr-2026 — sujeta a evaluación individual y a TMC vigente.',
  },
  cuota_minima_clp: 25_000,
  requisitos: [
    'Ser trabajador afiliado a Caja Los Andes con al menos 6 meses de cotización continua',
    'Empleador con convenio de descuento por planilla activo',
    'No estar en lista DICOM por deuda morosa con CCLA',
    'Capacidad de pago suficiente: cuota total ≤ 25% renta líquida',
    'Consentimiento REDEC (Ley 21.680) firmado',
  ],
  documentos_requeridos: [
    'Cédula de identidad vigente',
    'Última liquidación de sueldo (Document AI Custom Extractor)',
    'Certificado AFP últimas 6 cotizaciones (opcional, pre-validable vía PreVired)',
  ],
  desembolso_promesa: '24-48 horas hábiles tras aprobación',
  garantia: 'descuento por planilla',
  ley_aplicable: ['Ley 18.833 art. 22', 'Ley 21.680 (REDEC)', 'Circular SUSESO 3.796'],
  destacado_homepage: true,
  badge: 'Más solicitado',
};

export const CREDITO_SOCIAL_PENSIONADOS: Credito = {
  id: 'cred-pensionados',
  nombre: 'Crédito Social Pensionados',
  descripcion_corta:
    'Crédito pensado para pensionados afiliados, con cuota descontada de la pensión.',
  descripcion_larga:
    'Diseñado especialmente para pensionados afiliados a Caja Los Andes (PASIS, IPS, AFP). El descuento se realiza directamente desde la pensión mensual. Considera tope del 30% de pensión líquida — superior al de trabajadores activos por menor estructura de gastos típica del segmento.',
  url_oficial: 'https://www.cajalosandes.cl/creditos/credito-social-pensionados',
  audiencias: ['Pensionados'],
  monto: { min: 100_000, max: 8_000_000, moneda: 'CLP' },
  plazo: { min_meses: 6, max_meses: 48 },
  tasa_referencial: {
    cae_anual_pct: 18.9,
    tasa_interes_mensual_pct: 1.43,
    notas:
      'Tasa preferencial pensionados — más baja que Universal por menor riesgo (descuento garantizado de pensión).',
  },
  cuota_minima_clp: 20_000,
  requisitos: [
    'Ser pensionado(a) afiliado(a) a Caja Los Andes',
    'Pensión líquida mínima: $250.000',
    'Edad ≤ 75 años al término del crédito (algunos casos extienden a 80)',
    'No estar en cobranza judicial CCLA',
    'Consentimiento REDEC firmado',
  ],
  documentos_requeridos: [
    'Cédula de identidad vigente',
    'Última liquidación de pensión (Document AI Custom Extractor)',
    'Comprobante domicilio (opcional)',
  ],
  desembolso_promesa: '24 horas hábiles',
  garantia: 'descuento por planilla',
  ley_aplicable: ['Ley 18.833 art. 22 bis', 'Ley 21.680 (REDEC)', 'DL 3.500 art. 91'],
  destacado_homepage: true,
  badge: 'Pensionados',
};

export const CREDITO_SALUD: Credito = {
  id: 'cred-salud',
  nombre: 'Crédito de Salud',
  descripcion_corta:
    'Financia tratamientos, hospitalizaciones, intervenciones y exámenes complejos.',
  descripcion_larga:
    'Crédito orientado exclusivamente a cubrir gastos de salud no cubiertos por FONASA o ISAPRE: copagos, pre-existencias, exámenes complejos, hospitalización, parto, salud mental y dental mayor. Tasa preferencial respecto a Crédito Universal.',
  url_oficial: 'https://www.cajalosandes.cl/creditos/credito-de-salud',
  audiencias: ['Trabajadores', 'Pensionados'],
  monto: { min: 200_000, max: 15_000_000, moneda: 'CLP' },
  plazo: { min_meses: 6, max_meses: 48 },
  tasa_referencial: {
    cae_anual_pct: 19.5,
    tasa_interes_mensual_pct: 1.49,
  },
  requisitos: [
    'Trabajador o pensionado afiliado',
    'Presentar presupuesto, bono de atención o pre-cuenta clínica',
    'Capacidad de pago suficiente',
    'Consentimiento REDEC',
  ],
  documentos_requeridos: [
    'Cédula de identidad',
    'Presupuesto de la prestación de salud (PDF/foto)',
    'Liquidación de sueldo o pensión',
  ],
  desembolso_promesa: '48 horas hábiles — pago directo al prestador disponible',
  garantia: 'descuento por planilla',
  ley_aplicable: ['Ley 18.833', 'Ley 16.744 (en caso de accidente del trabajo)', 'Ley 21.680'],
  destacado_homepage: false,
};

export const CREDITO_CONSOLIDACION: Credito = {
  id: 'cred-consolidacion',
  nombre: 'Crédito Consolidación de Deuda',
  descripcion_corta:
    'Junta tus deudas en una sola cuota más baja, con plazos extendidos y CAE competitiva.',
  descripcion_larga:
    'Permite reunir hasta 4 obligaciones financieras (banco, retail, casa comercial, otra caja) en un solo crédito social con cuota única descontada por planilla. Caja Los Andes paga directamente a tus acreedores externos. Requiere consulta REDEC (Ley 21.680) consentida.',
  url_oficial: 'https://www.cajalosandes.cl/creditos/credito-consolidacion-deuda',
  audiencias: ['Trabajadores', 'Pensionados'],
  monto: { min: 500_000, max: 25_000_000, moneda: 'CLP' },
  plazo: { min_meses: 12, max_meses: 60 },
  tasa_referencial: {
    cae_anual_pct: 18.9,
    tasa_interes_mensual_pct: 1.43,
    notas:
      'Tasa preferencial consolidación — diseñada para ser inferior al promedio ponderado de las deudas que reemplaza.',
  },
  requisitos: [
    'Afiliado activo (trabajador o pensionado)',
    'Acreditar deudas externas vía REDEC (consentimiento expreso, Ley 21.680)',
    'Cuota nueva debe representar mejora demostrable',
    'No estar en quiebra/insolvencia formal Ley 20.720',
  ],
  documentos_requeridos: [
    'Cédula identidad',
    'Liquidación sueldo/pensión',
    'Consentimiento REDEC firmado (1 click en Mi Portal)',
    'Certificados de deuda de cada acreedor (opcional — REDEC los entrega)',
  ],
  desembolso_promesa: 'Pago a acreedores en 5 días hábiles tras aprobación',
  garantia: 'descuento por planilla',
  ley_aplicable: ['Ley 18.833', 'Ley 21.680 (REDEC)', 'Ley 21.236 (Portabilidad Financiera)'],
  destacado_homepage: true,
  badge: 'Más solicitado',
};

export const CREDITO_EDUCACION: Credito = {
  id: 'cred-educacion',
  nombre: 'Crédito Educación Superior',
  descripcion_corta:
    'Financia carreras técnicas, profesionales y postgrados con periodo de gracia mientras estudias.',
  descripcion_larga:
    'Crédito para financiar matrícula y arancel de educación superior (CFT, IP, Universidad acreditada o postgrado). Incluye periodo de gracia de hasta 12 meses post-titulación. Disponible para el afiliado o sus cargas familiares.',
  url_oficial: 'https://www.cajalosandes.cl/creditos/credito-educacion-superior',
  audiencias: ['Trabajadores', 'Estudiantes'],
  monto: { min: 300_000, max: 20_000_000, moneda: 'CLP' },
  plazo: { min_meses: 12, max_meses: 84 },
  tasa_referencial: {
    cae_anual_pct: 16.4,
    tasa_interes_mensual_pct: 1.27,
    notas: 'Tasa preferencial educación — la más baja del catálogo crédito social.',
  },
  requisitos: [
    'Afiliado activo',
    'Estudiante en institución acreditada por CNA',
    'Carta de aceptación o certificado de matrícula',
    'Edad cargas: hasta 27 años; afiliado: sin límite',
  ],
  documentos_requeridos: [
    'Cédula del afiliado',
    'Cédula del estudiante (si distinto)',
    'Certificado de matrícula año en curso',
    'Liquidación sueldo del afiliado',
  ],
  desembolso_promesa: 'Pago directo a institución educacional en 3 días hábiles',
  garantia: 'descuento por planilla',
  ley_aplicable: ['Ley 18.833', 'Ley 21.091 (educación superior)'],
  destacado_homepage: false,
};

export const CREDITO_TAPP: Credito = {
  id: 'cred-tapp-50uf',
  nombre: 'Crédito Tapp Express',
  descripcion_corta:
    'Hasta 50 UF en 5 minutos, 100% digital, desde la app Tapp.',
  descripcion_larga:
    'El crédito social digital de Caja Los Andes a través de la billetera Tapp. Hasta 50 UF (~$1.975.000 al UF de abr-2026) con aprobación en 5 minutos vía evaluación automatizada con motor de riesgo IFRS 9 y consulta REDEC. Disponible 24/7 para clientes Tapp con scoring positivo.',
  url_oficial: 'https://www.tapp.cl/credito',
  audiencias: ['Trabajadores'],
  monto: { min: 50_000, max: 1_975_000, moneda: 'CLP' },
  plazo: { min_meses: 3, max_meses: 24 },
  tasa_referencial: {
    cae_anual_pct: 23.8,
    tasa_interes_mensual_pct: 1.79,
    notas: 'Tasa más alta por ser sin descuento por planilla — pago vía cargo a tarjeta Tapp.',
  },
  requisitos: [
    'Cliente Tapp activo con ≥ 3 meses de uso',
    'Cumplir scoring interno motor IFRS 9',
    'Renta declarada ≥ $400.000',
    'Consentimiento REDEC',
  ],
  documentos_requeridos: ['Onboarding KYC ya completado en Tapp (cédula + selfie)'],
  desembolso_promesa: '5 minutos — abono inmediato al saldo Tapp',
  garantia: 'pagaré',
  ley_aplicable: ['Ley 18.833', 'Ley 21.680 (REDEC)', 'Ley 20.009 (operaciones electrónicas)'],
  destacado_homepage: true,
  badge: 'Express',
};

export const ALL_CREDITOS: Credito[] = [
  CREDITO_UNIVERSAL,
  CREDITO_SOCIAL_PENSIONADOS,
  CREDITO_SALUD,
  CREDITO_CONSOLIDACION,
  CREDITO_EDUCACION,
  CREDITO_TAPP,
];

/* -------------------------- BENEFICIOS SOCIALES --------------------------- */

export interface Beneficio {
  id: string;
  nombre: string;
  descripcion_corta: string;
  descripcion_larga: string;
  url_oficial: string;
  categoria:
    | 'Bono'
    | 'Subsidio'
    | 'Beca'
    | 'Asignación'
    | 'Convenio'
    | 'Recreación'
    | 'Salud';
  monto_clp: number | { tramos: { tramo: string; monto_clp: number }[] };
  unidad?: 'único' | 'mensual' | 'anual';
  requisitos: string[];
  documentos_requeridos: string[];
  ley_aplicable: string[];
  ventana_postulacion?: { abre: string; cierra: string };
  cupo_anual?: number;
  audiencias: ('Trabajadores' | 'Pensionados' | 'Empresas' | 'Estudiantes' | 'Cargas')[];
}

export const BENEFICIO_BODAS_ORO: Beneficio = {
  id: 'ben-bodas-oro',
  nombre: 'Bono Bodas de Oro',
  descripcion_corta:
    'Bono único de $300.000 para parejas que cumplen 50 años de matrimonio.',
  descripcion_larga:
    'Beneficio creado por la Ley 20.595 (2012). Otorga un bono único, no imponible y no tributable, a las parejas chilenas que cumplen 50 años de matrimonio civil ininterrumpido. Para afiliados a Caja Los Andes, la solicitud puede iniciarse en sucursal virtual y el pago se realiza en cuenta bancaria del solicitante o vía Tapp en máx 30 días.',
  url_oficial: 'https://www.cajalosandes.cl/apoyo-social/bono-bodas-de-oro',
  categoria: 'Bono',
  monto_clp: 300_000,
  unidad: 'único',
  requisitos: [
    'Cumplir 50 años de matrimonio civil al año de postulación',
    'Ambos cónyuges deben estar vivos al momento del pago',
    'Estar en el 80% más vulnerable según Registro Social de Hogares',
    'Tener al menos 5 años de residencia en Chile',
  ],
  documentos_requeridos: [
    'Certificado de matrimonio (Registro Civil)',
    'Cédula identidad de ambos cónyuges',
    'Verificación tramo Registro Social de Hogares (consulta automática SUSESO)',
  ],
  ley_aplicable: ['Ley 20.595 art. 1', 'Reglamento DS 32/2012 MDS'],
  audiencias: ['Trabajadores', 'Pensionados'],
};

export const BENEFICIO_BONO_ESCOLAR: Beneficio = {
  id: 'ben-bono-escolar',
  nombre: 'Bono Escolar (Bono Profamilia Escolaridad)',
  descripcion_corta:
    'Aporte único anual por cada carga familiar estudiando, marzo cada año.',
  descripcion_larga:
    'Bono Profamilia que entrega Caja Los Andes a sus afiliados con cargas familiares en edad escolar (5-18 años) acreditadas al 31-dic del año anterior. Monto referencial 2026: $67.480 por carga (proyección IPC sobre $64.574 de 2025).',
  url_oficial: 'https://www.cajalosandes.cl/apoyo-social/bonos-familiares',
  categoria: 'Bono',
  monto_clp: 67_480,
  unidad: 'anual',
  requisitos: [
    'Ser afiliado a Caja Los Andes',
    'Tener cargas familiares reconocidas al 31-dic del año anterior',
    'La carga debe estar entre 5 y 18 años cumplidos',
    'Receptor de Asignación Familiar tramo A, B, C o SUF',
    'Carga matriculada en establecimiento reconocido por MINEDUC',
  ],
  documentos_requeridos: [
    'Cédula del afiliado',
    'Certificado de alumno regular de cada carga (validación automática vía MINEDUC)',
  ],
  ventana_postulacion: { abre: '2026-03-01', cierra: '2026-05-31' },
  ley_aplicable: ['Reglamento beneficios CCLA art. 18'],
  audiencias: ['Trabajadores', 'Pensionados', 'Cargas'],
};

export const BENEFICIO_ASIGNACION_FAMILIAR: Beneficio = {
  id: 'ben-asig-familiar',
  nombre: 'Asignación Familiar (SUF)',
  descripcion_corta:
    'Aporte mensual estatal por carga familiar, pagado por la Caja por cuenta del Estado.',
  descripcion_larga:
    'Asignación Familiar es un beneficio del Estado que la Caja paga por cuenta del Fisco. Tramos vigentes 2026 (proyección IPC + reajuste presupuestario): A ≤ $620.251 ($22.997/carga), B $620.252-$905.941 ($14.108/carga), C $905.942-$1.412.957 ($4.459/carga), D > $1.412.957 ($0). El SUF (Subsidio Único Familiar) es el equivalente para personas sin contrato.',
  url_oficial: 'https://www.cajalosandes.cl/apoyo-social/asignacion-familiar',
  categoria: 'Asignación',
  monto_clp: {
    tramos: [
      { tramo: 'A — renta hasta $620.251', monto_clp: 22_997 },
      { tramo: 'B — renta $620.252 a $905.941', monto_clp: 14_108 },
      { tramo: 'C — renta $905.942 a $1.412.957', monto_clp: 4_459 },
      { tramo: 'D — renta superior a $1.412.957', monto_clp: 0 },
    ],
  },
  unidad: 'mensual',
  requisitos: [
    'Trabajador, pensionado o subsidiado',
    'Cargas reconocidas: cónyuge, hijos < 18 años (o < 24 si estudian), madre viuda',
    'Acreditación periódica (cada 3 años) de continuidad de la carga',
  ],
  documentos_requeridos: [
    'Certificado de nacimiento de la carga',
    'Certificado de alumno regular (si > 18 años y estudia)',
    'Sentencia de divorcio si aplica',
  ],
  ley_aplicable: ['DFL 150 de 1981', 'Ley 18.020 (SUF)', 'Circular SUSESO 3.789'],
  audiencias: ['Trabajadores', 'Pensionados'],
};

export const BENEFICIO_SUBSIDIO_NACIMIENTO: Beneficio = {
  id: 'ben-subsidio-nacimiento',
  nombre: 'Bono Profamilia Nacimiento',
  descripcion_corta:
    'Bono único de $80.000 por nacimiento de hijo(a) del afiliado.',
  descripcion_larga:
    'Bono Profamilia que CCLA otorga al afiliado(a) que tiene un hijo(a). Pagadero hasta 60 días después del nacimiento. Reconoce nacimiento natural, cesárea y adopción inscrita en el Registro Civil.',
  url_oficial: 'https://www.cajalosandes.cl/apoyo-social/bonos-familiares',
  categoria: 'Bono',
  monto_clp: 80_000,
  unidad: 'único',
  requisitos: [
    'Ser afiliado a CCLA al momento del nacimiento',
    'Mínimo 6 meses de cotización continua',
    'Inscripción del nacimiento en el Registro Civil',
  ],
  documentos_requeridos: [
    'Certificado de nacimiento',
    'Cédula del afiliado',
  ],
  ley_aplicable: ['Reglamento beneficios CCLA art. 14'],
  audiencias: ['Trabajadores', 'Pensionados'],
};

export const BENEFICIO_SUBSIDIO_DEFUNCION: Beneficio = {
  id: 'ben-subsidio-defuncion',
  nombre: 'Bono Profamilia Defunción',
  descripcion_corta:
    'Aporte único de $250.000 por fallecimiento del afiliado o de su cónyuge/carga.',
  descripcion_larga:
    'Bono que apoya a la familia del afiliado fallecido o al afiliado(a) que sufre la pérdida de su cónyuge o carga reconocida. Pagadero al beneficiario designado o al cónyuge sobreviviente. Solicitar dentro de 6 meses del fallecimiento.',
  url_oficial: 'https://www.cajalosandes.cl/apoyo-social/bonos-familiares',
  categoria: 'Bono',
  monto_clp: 250_000,
  unidad: 'único',
  requisitos: [
    'Afiliación vigente al fallecimiento',
    'Solicitar dentro de 6 meses del deceso',
  ],
  documentos_requeridos: [
    'Certificado de defunción',
    'Cédula del solicitante',
    'Posesión efectiva o documento que acredite parentesco',
  ],
  ley_aplicable: ['Reglamento beneficios CCLA art. 16'],
  audiencias: ['Trabajadores', 'Pensionados'],
};

export const BENEFICIO_BECAS_ESTUDIO: Beneficio = {
  id: 'ben-becas-estudio',
  nombre: 'Becas de Estudio Caja Los Andes 2026',
  descripcion_corta:
    'Hasta 1.500 becas anuales para hijos de afiliados que ingresan a educación superior.',
  descripcion_larga:
    'Programa anual de becas para cargas familiares de afiliados que ingresan a primer año de educación superior (CFT, IP o Universidad acreditada). Cubre matrícula y arancel hasta $850.000 por año. Postulación entre noviembre y enero.',
  url_oficial: 'https://www.cajalosandes.cl/educacion/becas',
  categoria: 'Beca',
  monto_clp: 850_000,
  unidad: 'anual',
  requisitos: [
    'Hijo(a) de afiliado(a) activo con ≥ 12 meses de cotización',
    'PAES ≥ 600 puntos promedio Lenguaje + Matemática',
    'NEM ≥ 5,8',
    'Matriculado en institución acreditada por CNA',
    'Renta familiar ≤ $1.800.000 mensual',
  ],
  documentos_requeridos: [
    'Cédula del estudiante y del afiliado',
    'Certificado PAES y concentración de notas',
    'Certificado de matrícula',
    'Liquidaciones sueldo de los padres',
  ],
  ventana_postulacion: { abre: '2025-11-15', cierra: '2026-01-31' },
  cupo_anual: 1500,
  ley_aplicable: ['Reglamento becas CCLA 2025-2026'],
  audiencias: ['Estudiantes', 'Cargas'],
};

export const BENEFICIO_APORTE_FAMILIAR_PERMANENTE: Beneficio = {
  id: 'ben-aporte-familiar-permanente',
  nombre: 'Aporte Familiar Permanente (Bono Marzo)',
  descripcion_corta:
    'Bono estatal anual entregado en marzo a familias vulnerables.',
  descripcion_larga:
    'Bono Marzo. Pago único anual del Estado a familias con asignación familiar tramo A o B, beneficiarios SUF, o usuarios del Subsistema Seguridades y Oportunidades. Monto 2026: $63.391 por carga (referencia IPS).',
  url_oficial: 'https://www.cajalosandes.cl/apoyo-social/aporte-familiar-permanente',
  categoria: 'Bono',
  monto_clp: 63_391,
  unidad: 'anual',
  requisitos: [
    'Ser receptor de Asignación Familiar tramo A o B al 31-dic del año anterior',
    'O ser receptor SUF o Chile Solidario',
  ],
  documentos_requeridos: ['Verificación automática IPS — sin trámite del afiliado'],
  ventana_postulacion: { abre: '2026-03-15', cierra: '2026-12-31' },
  ley_aplicable: ['Ley 20.743 (Ley Bono Marzo)'],
  audiencias: ['Trabajadores', 'Pensionados'],
};

export const BENEFICIO_SUBSIDIO_HABITACIONAL: Beneficio = {
  id: 'ben-subsidio-habitacional',
  nombre: 'Apoyo Subsidio Habitacional DS49',
  descripcion_corta:
    'Asesoría y cofinanciamiento del ahorro mínimo para postular al Subsidio Habitacional.',
  descripcion_larga:
    'Caja Los Andes acompaña al afiliado en la postulación al Subsidio DS49 (Fondo Solidario de Elección de Vivienda) del MINVU, ofreciendo cuenta Ahorro Vivienda gestionada en Mis Metas/SoyFocus, asesoría documental, y un complemento al ahorro mínimo de hasta 10 UF.',
  url_oficial: 'https://mismetas.cajalosandes.cl/ahorro-vivienda',
  categoria: 'Subsidio',
  monto_clp: 395_000, // ~10 UF
  unidad: 'único',
  requisitos: [
    'Afiliado con ahorro Vivienda en Mis Metas',
    'Postulante al DS49 MINVU',
    'No ser propietario de otra vivienda',
  ],
  documentos_requeridos: [
    'Cuenta Ahorro Vivienda Mis Metas activa',
    'Certificado MINVU de postulación',
  ],
  ley_aplicable: ['DS 49/2011 MINVU', 'Ley 19.281 (cuentas de ahorro vivienda)'],
  audiencias: ['Trabajadores'],
};

export const BENEFICIO_PROGRAMA_CUIDADORES: Beneficio = {
  id: 'ben-programa-cuidadores',
  nombre: 'Programa Cuidadores',
  descripcion_corta:
    'Acompañamiento, capacitación y respiro para cuidadores familiares de personas con dependencia.',
  descripcion_larga:
    'Programa social de Caja Los Andes para personas que cuidan a un familiar con dependencia severa. Incluye talleres mensuales, atención psicológica gratuita, becas de respiro (3 días/año en centros recreacionales) y red de pares.',
  url_oficial: 'https://www.cajalosandes.cl/apoyo-social/programa-cuidadores',
  categoria: 'Convenio',
  monto_clp: 0,
  requisitos: [
    'Ser afiliado o carga familiar de afiliado',
    'Acreditar rol de cuidador principal vía Credencial Nacional de Cuidadoras y Cuidadores (Ley 21.632)',
  ],
  documentos_requeridos: [
    'Credencial Nacional de Cuidador',
    'Cédula identidad',
  ],
  ley_aplicable: ['Ley 21.632 (Sistema Nacional de Cuidados)'],
  audiencias: ['Trabajadores', 'Pensionados'],
};

export const BENEFICIO_DENTAL_URGENCIA: Beneficio = {
  id: 'ben-dental-urgencia',
  nombre: 'Urgencia Dental con copago $100',
  descripcion_corta:
    'Atención dental de urgencia en Centros Médicos y Dentales RedSalud por solo $100.',
  descripcion_larga:
    'Convenio CCLA × RedSalud. Atención de urgencia odontológica (dolor agudo, traumatismo, absceso) en cualquier Centro Médico y Dental RedSalud del país por copago fijo de $100. Sin tope anual de uso.',
  url_oficial: 'https://www.cajalosandes.cl/beneficios/salud',
  categoria: 'Salud',
  monto_clp: 100,
  unidad: 'único',
  requisitos: [
    'Afiliado vigente CCLA',
    'Presentar cédula y credencial CCLA en RedSalud',
  ],
  documentos_requeridos: ['Cédula identidad'],
  ley_aplicable: ['Convenio comercial CCLA-RedSalud (no normativo)'],
  audiencias: ['Trabajadores', 'Pensionados', 'Cargas'],
};

export const BENEFICIO_TURISMO_BONIFICADO: Beneficio = {
  id: 'ben-turismo-bonificado',
  nombre: 'Turismo Bonificado',
  descripcion_corta:
    'Hasta 50% de descuento en hoteles y cabañas CLA Turismo (red de 18 propiedades).',
  descripcion_larga:
    'Tarifa preferencial para afiliados en los 18 hoteles, cabañas y parques de CLA Turismo S.p.A. — incluye centros recreacionales en Pucón, Algarrobo, Olmué, Jahuel, Puyehue, Lican Ray y Chillán. Descuento adicional para pensionados y FAOS. Reservas vía cajalosandes.cl/turismo o app.',
  url_oficial: 'https://www.cajalosandes.cl/turismo',
  categoria: 'Recreación',
  monto_clp: 0,
  requisitos: [
    'Afiliado vigente',
    'Reserva con al menos 7 días de anticipación (alta temporada)',
  ],
  documentos_requeridos: ['Cédula identidad al check-in'],
  ley_aplicable: ['Reglamento beneficios CCLA art. 31'],
  audiencias: ['Trabajadores', 'Pensionados', 'Cargas'],
};

export const ALL_BENEFICIOS: Beneficio[] = [
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
];

/* -------------------------- SEGUROS --------------------------------------- */

export interface SeguroProducto {
  id: string;
  nombre: string;
  descripcion_corta: string;
  prima_mensual_clp: number;
  cobertura_principal_clp: number;
  url_oficial: string;
  audiencias: ('Trabajadores' | 'Pensionados' | 'Empresas')[];
  aseguradora_partner: string;
}

export const ALL_SEGUROS: SeguroProducto[] = [
  {
    id: 'seg-vida-familiar-full',
    nombre: 'Seguro de Vida Familiar Full',
    descripcion_corta:
      'Cobertura por fallecimiento e invalidez 2/3, con renta mensual a beneficiarios.',
    prima_mensual_clp: 9_990,
    cobertura_principal_clp: 35_000_000,
    url_oficial: 'https://www.cajalosandes.cl/seguros/seguro-de-vida-familiar-full',
    audiencias: ['Trabajadores', 'Pensionados'],
    aseguradora_partner: 'Confuturo',
  },
  {
    id: 'seg-cesantia-credito-social',
    nombre: 'Seguro de Cesantía Crédito Social',
    descripcion_corta:
      'Si quedas cesante, cubre tu cuota del crédito social hasta 6 meses.',
    prima_mensual_clp: 2_490,
    cobertura_principal_clp: 0,
    url_oficial: 'https://www.cajalosandes.cl/seguros/seguro-de-cesantia-credito-social',
    audiencias: ['Trabajadores'],
    aseguradora_partner: 'Vida Cámara',
  },
  {
    id: 'seg-escolar',
    nombre: 'Seguro Escolar',
    descripcion_corta:
      'Protege a tu hijo(a) ante accidentes en el colegio o trayecto. Complemento del Seguro Escolar estatal.',
    prima_mensual_clp: 1_990,
    cobertura_principal_clp: 12_000_000,
    url_oficial: 'https://www.cajalosandes.cl/seguros/seguro-escolar',
    audiencias: ['Trabajadores', 'Pensionados'],
    aseguradora_partner: 'Vida Cámara',
  },
  {
    id: 'seg-catastrofico',
    nombre: 'Seguro Catastrófico',
    descripcion_corta:
      'Cobertura para enfermedades de alto costo (cáncer, transplante, ACV). Hasta UF 10.000.',
    prima_mensual_clp: 14_500,
    cobertura_principal_clp: 395_000_000,
    url_oficial: 'https://www.cajalosandes.cl/seguros/seguro-catastrofico',
    audiencias: ['Trabajadores', 'Pensionados'],
    aseguradora_partner: 'BCI Seguros',
  },
  {
    id: 'seg-automotriz',
    nombre: 'Seguro Automotriz',
    descripcion_corta:
      'Cobertura completa para tu vehículo: daño propio, responsabilidad civil, robo, asistencia.',
    prima_mensual_clp: 38_900,
    cobertura_principal_clp: 18_000_000,
    url_oficial: 'https://www.cajalosandes.cl/seguros/seguro-automotriz',
    audiencias: ['Trabajadores', 'Pensionados'],
    aseguradora_partner: 'Consorcio',
  },
  {
    id: 'seg-asistencia-viajes',
    nombre: 'Seguro Asistencia en Viajes',
    descripcion_corta:
      'Asistencia médica, equipaje y cancelaciones para viajes nacionales e internacionales.',
    prima_mensual_clp: 12_300,
    cobertura_principal_clp: 25_000_000,
    url_oficial: 'https://www.cajalosandes.cl/seguros/seguro-asistencia-en-viajes',
    audiencias: ['Trabajadores', 'Pensionados'],
    aseguradora_partner: 'Universal Assistance',
  },
];

/* -------------------------- CONVENIOS ------------------------------------- */

export interface Convenio {
  id: string;
  partner: string;
  categoria: 'Salud' | 'Turismo' | 'Educación' | 'Retail' | 'Transporte' | 'Cultura' | 'Deporte';
  descripcion: string;
  descuento_pct?: number;
  beneficio_extra?: string;
  url_oficial: string;
}

export const ALL_CONVENIOS: Convenio[] = [
  {
    id: 'conv-redsalud-dental',
    partner: 'RedSalud',
    categoria: 'Salud',
    descripcion: 'Centros Médicos y Dentales RedSalud — urgencia dental copago $100, descuentos en consultas y exámenes.',
    descuento_pct: 30,
    beneficio_extra: 'Urgencia dental copago fijo $100',
    url_oficial: 'https://www.redsalud.cl',
  },
  {
    id: 'conv-clinica-bicentenario',
    partner: 'Clínica Bicentenario',
    categoria: 'Salud',
    descripcion: 'Convenio prestador preferente: 25% descuento en consultas, programa Sano +50, telemedicina nocturna.',
    descuento_pct: 25,
    url_oficial: 'https://www.clinicabicentenario.cl',
  },
  {
    id: 'conv-megasalud',
    partner: 'Megasalud',
    categoria: 'Salud',
    descripcion: 'Hasta 35% de descuento en consultas médicas y exámenes en toda la red Megasalud.',
    descuento_pct: 35,
    url_oficial: 'https://www.megasalud.cl',
  },
  {
    id: 'conv-jetsmart',
    partner: 'JetSmart',
    categoria: 'Transporte',
    descripcion: '25% de descuento en vuelos JetSmart Chile y regionales. Aplica al titular y cargas.',
    descuento_pct: 25,
    url_oficial: 'https://jetsmart.com',
  },
  {
    id: 'conv-flixbus',
    partner: 'FlixBus',
    categoria: 'Transporte',
    descripcion: '20% de descuento en pasajes FlixBus en Chile.',
    descuento_pct: 20,
    url_oficial: 'https://www.flixbus.cl',
  },
  {
    id: 'conv-despegar',
    partner: 'Despegar',
    categoria: 'Turismo',
    descripcion: '7% de descuento en hoteles y vuelos internacionales reservados con Despegar.cl.',
    descuento_pct: 7,
    url_oficial: 'https://www.despegar.cl',
  },
  {
    id: 'conv-amatista',
    partner: 'Amatista Travels',
    categoria: 'Turismo',
    descripcion: '10% de descuento en paquetes turísticos nacionales e internacionales.',
    descuento_pct: 10,
    url_oficial: 'https://www.amatistatravels.cl',
  },
  {
    id: 'conv-farmacias-ahumada',
    partner: 'Farmacias Ahumada',
    categoria: 'Salud',
    descripcion: 'Programa Sana — descuentos hasta 40% en medicamentos genéricos, despacho gratis a pensionados.',
    descuento_pct: 40,
    url_oficial: 'https://www.farmaciasahumada.cl',
  },
  {
    id: 'conv-cruz-verde',
    partner: 'Farmacias Cruz Verde',
    categoria: 'Salud',
    descripcion: '20% de descuento en medicamentos de marca y 35% en genéricos para afiliados.',
    descuento_pct: 35,
    url_oficial: 'https://www.cruzverde.cl',
  },
  {
    id: 'conv-cinemark',
    partner: 'Cinemark',
    categoria: 'Cultura',
    descripcion: 'Entrada 2x1 lunes y martes en todo Chile, presentando credencial CCLA.',
    url_oficial: 'https://www.cinemark.cl',
  },
  {
    id: 'conv-inacap',
    partner: 'INACAP',
    categoria: 'Educación',
    descripcion: 'Hasta 30% de descuento en aranceles de carreras técnicas y profesionales para hijos de afiliados.',
    descuento_pct: 30,
    url_oficial: 'https://www.inacap.cl',
  },
  {
    id: 'conv-uniacc',
    partner: 'Universidad UNIACC',
    categoria: 'Educación',
    descripcion: '20% descuento en arancel pregrado y 30% en diplomados online.',
    descuento_pct: 20,
    url_oficial: 'https://www.uniacc.cl',
  },
  {
    id: 'conv-sportlife',
    partner: 'Sportlife',
    categoria: 'Deporte',
    descripcion: 'Membresía con 50% de descuento el primer mes y sin matrícula de inscripción.',
    descuento_pct: 50,
    url_oficial: 'https://www.sportlife.cl',
  },
];

/* -------------------------- HOTELES CLA TURISMO --------------------------- */

export interface HotelClaTurismo {
  id: string;
  nombre: string;
  comuna: string;
  region: string;
  tipo: 'Hotel' | 'Cabañas' | 'Centro Recreacional' | 'Parque';
  capacidad_personas: number;
  precio_noche_clp_referencial: number;
  precio_noche_clp_afiliado: number;
  amenities: string[];
  imagen_placeholder: string;
}

export const ALL_HOTELES_CLA: HotelClaTurismo[] = [
  {
    id: 'hotel-pucon',
    nombre: 'Hotel & Spa Caja Los Andes Pucón',
    comuna: 'Pucón',
    region: 'Región de La Araucanía',
    tipo: 'Hotel',
    capacidad_personas: 4,
    precio_noche_clp_referencial: 138_000,
    precio_noche_clp_afiliado: 79_000,
    amenities: ['Piscina temperada', 'Spa', 'Restaurante Raíces de los Andes', 'Vista volcán Villarrica'],
    imagen_placeholder: '/mocks/img/hotel-pucon.jpg',
  },
  {
    id: 'hotel-algarrobo',
    nombre: 'Cabañas Caja Los Andes Algarrobo',
    comuna: 'Algarrobo',
    region: 'Región de Valparaíso',
    tipo: 'Cabañas',
    capacidad_personas: 6,
    precio_noche_clp_referencial: 98_000,
    precio_noche_clp_afiliado: 54_000,
    amenities: ['Piscina', 'Quincho', 'Estacionamiento', 'A 5 min del mar'],
    imagen_placeholder: '/mocks/img/hotel-algarrobo.jpg',
  },
  {
    id: 'hotel-olmue',
    nombre: 'Centro Recreacional Olmué',
    comuna: 'Olmué',
    region: 'Región de Valparaíso',
    tipo: 'Centro Recreacional',
    capacidad_personas: 4,
    precio_noche_clp_referencial: 78_000,
    precio_noche_clp_afiliado: 42_000,
    amenities: ['Piscina', 'Cancha tenis', 'Senderismo', 'Restaurant'],
    imagen_placeholder: '/mocks/img/hotel-olmue.jpg',
  },
  {
    id: 'hotel-jahuel',
    nombre: 'Hotel Termas de Jahuel — Convenio CCLA',
    comuna: 'San Felipe',
    region: 'Región de Valparaíso',
    tipo: 'Hotel',
    capacidad_personas: 2,
    precio_noche_clp_referencial: 168_000,
    precio_noche_clp_afiliado: 112_000,
    amenities: ['Termas', 'Spa', 'Vino convento'],
    imagen_placeholder: '/mocks/img/hotel-jahuel.jpg',
  },
  {
    id: 'hotel-puyehue',
    nombre: 'Cabañas CLA Puyehue',
    comuna: 'Puyehue',
    region: 'Región de Los Lagos',
    tipo: 'Cabañas',
    capacidad_personas: 5,
    precio_noche_clp_referencial: 92_000,
    precio_noche_clp_afiliado: 51_000,
    amenities: ['Tinaja caliente', 'Quincho', 'Bosque nativo'],
    imagen_placeholder: '/mocks/img/hotel-puyehue.jpg',
  },
  {
    id: 'hotel-lican-ray',
    nombre: 'Centro Vacacional Lican Ray',
    comuna: 'Villarrica',
    region: 'Región de La Araucanía',
    tipo: 'Centro Recreacional',
    capacidad_personas: 6,
    precio_noche_clp_referencial: 88_000,
    precio_noche_clp_afiliado: 47_000,
    amenities: ['A orilla de lago', 'Cancha fútbol', 'Kayak'],
    imagen_placeholder: '/mocks/img/hotel-licanray.jpg',
  },
  {
    id: 'hotel-chillan',
    nombre: 'Cabañas CLA Chillán',
    comuna: 'Chillán',
    region: 'Región de Ñuble',
    tipo: 'Cabañas',
    capacidad_personas: 5,
    precio_noche_clp_referencial: 82_000,
    precio_noche_clp_afiliado: 44_000,
    amenities: ['Piscina', 'Cerca de termas', 'Cocina equipada'],
    imagen_placeholder: '/mocks/img/hotel-chillan.jpg',
  },
];

/* ─────────────────────────────────────────────────────────────────────────── */

export interface DatosMacro {
  fecha: string;
  uf_clp: number;
  utm_clp: number;
  ipsa_pts: number;
  usd_clp: number;
  euro_clp: number;
  tasa_max_convencional_no_reaj_pct: number;
  tasa_politica_monetaria_pct: number;
  ipc_12m_pct: number;
}

export const DATOS_MACRO_ABR_2026: DatosMacro = {
  fecha: '2026-04-17',
  uf_clp: 39_512.78,
  utm_clp: 68_549,
  ipsa_pts: 7_842.6,
  usd_clp: 928.45,
  euro_clp: 1_005.12,
  tasa_max_convencional_no_reaj_pct: 27.84, // [verificación pendiente — TMC se publica mensualmente por CMF]
  tasa_politica_monetaria_pct: 5.25, // BCCh referencial abr-2026
  ipc_12m_pct: 4.1,
};
