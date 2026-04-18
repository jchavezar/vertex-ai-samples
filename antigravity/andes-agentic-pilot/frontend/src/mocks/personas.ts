/* =============================================================================
 * mocks/personas.ts — Demo personas para Caja Los Andes
 *
 * Persona principal: María González (storyline en demo_strategy.md §4).
 * Todas las personas son sintéticas. RUTs marcados como [demo] no validan
 * con dígito verificador real — diseñados para que cualquier validador
 * automatizado los descarte en producción.
 *
 * Fuentes para perfilamiento:
 *  - docs/caja_los_andes_research.md §A.4 (segmentación), §A.6 (segmentos)
 *  - docs/demo_strategy.md §4 (persona María)
 *  - Estructura de afiliados CCAF: SUSESO Estadísticas 2024
 * ============================================================================= */

export type SegmentoCCLA =
  | 'Plata'
  | 'Oro'
  | 'Platino'
  | 'Pensionado'
  | 'Empresa PYME'
  | 'FAOS'
  | 'Estudiante';

export type CanalPreferido = 'sucursal' | 'app' | 'web' | 'whatsapp' | 'contact-center' | 'tapp';

export interface ProductoContratado {
  tipo:
    | 'Crédito Universal'
    | 'Crédito Social Pensionados'
    | 'Crédito de Salud'
    | 'Crédito Consolidación de Deuda'
    | 'Crédito Educación Superior'
    | 'Tarjeta Tapp'
    | 'Cuenta Mis Metas'
    | 'Seguro de Vida Familiar Full'
    | 'Seguro Cesantía Crédito Social'
    | 'Plan Salud Pensionados'
    | 'Asignación Familiar SUF';
  fecha_inicio: string; // ISO yyyy-mm-dd
  saldo_actual_clp?: number;
  cuota_mensual_clp?: number;
  estado: 'vigente' | 'al_dia' | 'atrasado_30' | 'atrasado_60' | 'cerrado';
}

export interface CargaFamiliar {
  nombre: string;
  edad: number;
  parentesco: 'hijo' | 'hija' | 'nieto' | 'nieta' | 'cónyuge' | 'madre' | 'padre';
  rut?: string; // demo
  estudia?: boolean;
  discapacidad?: boolean;
}

export interface Persona {
  id: string;
  rut: string; // [demo] – no válido para producción
  nombre_completo: string;
  primer_nombre: string;
  edad: number;
  fecha_nacimiento: string; // yyyy-mm-dd
  genero: 'F' | 'M' | 'X';
  comuna: string;
  region: string;
  direccion: string;
  telefono_movil: string;
  email: string;
  ocupacion: string;
  empleador?: string;
  renta_liquida_clp?: number;
  pension_liquida_clp?: number;
  afp?: 'Habitat' | 'Cuprum' | 'Provida' | 'PlanVital' | 'Capital' | 'Modelo' | 'Uno';
  isapre_o_fonasa: 'FONASA Tramo A' | 'FONASA Tramo B' | 'FONASA Tramo C' | 'FONASA Tramo D' | 'Banmédica' | 'Colmena' | 'Cruz Blanca' | 'Vida Tres' | 'Nueva Masvida';
  antiguedad_afiliacion_anos: number;
  segmento: SegmentoCCLA;
  canal_preferido: CanalPreferido;
  cargas_familiares: CargaFamiliar[];
  productos_contratados: ProductoContratado[];
  intereses_declarados: string[]; // para Memory Bank
  ultimas_consultas?: string[]; // últimas búsquedas en sucursal virtual
  notas_demo: string; // anclaje narrativo para el demo
  asignacion_familiar_tramo?: 'A' | 'B' | 'C' | 'D' | 'no_aplica';
}

/* ─────────────────────────────────────────────────────────────────────────── */

export const PERSONA_MARIA: Persona = {
  id: 'persona-001',
  rut: '12.345.678-5', // [demo]
  nombre_completo: 'María Cecilia González Pereira',
  primer_nombre: 'María',
  edad: 58,
  fecha_nacimiento: '1967-08-14',
  genero: 'F',
  comuna: 'Maipú',
  region: 'Región Metropolitana',
  direccion: 'Avenida Pajaritos 4521, depto 504, Maipú',
  telefono_movil: '+56 9 7654 3210',
  email: 'maria.gonzalez.demo@ejemplo.cl',
  ocupacion: 'Pensionada — ex Auxiliar de enfermería (sector salud)',
  empleador: 'Servicio de Salud Metropolitano Central (jubilada 2018)',
  pension_liquida_clp: 487_320,
  afp: 'Habitat',
  isapre_o_fonasa: 'FONASA Tramo B',
  antiguedad_afiliacion_anos: 22,
  segmento: 'Pensionado',
  canal_preferido: 'whatsapp',
  cargas_familiares: [
    {
      nombre: 'Sofía Ignacia Reyes González',
      edad: 8,
      parentesco: 'nieta',
      rut: '24.876.123-7',
      estudia: true,
    },
    {
      nombre: 'Carmen Pereira Olivares',
      edad: 79,
      parentesco: 'madre',
      rut: '4.123.987-2',
    },
  ],
  productos_contratados: [
    {
      tipo: 'Crédito Universal',
      fecha_inicio: '2023-09-12',
      saldo_actual_clp: 1_840_500,
      cuota_mensual_clp: 78_240,
      estado: 'al_dia',
    },
    {
      tipo: 'Plan Salud Pensionados',
      fecha_inicio: '2019-02-01',
      cuota_mensual_clp: 14_900,
      estado: 'vigente',
    },
    {
      tipo: 'Tarjeta Tapp',
      fecha_inicio: '2024-11-04',
      saldo_actual_clp: 32_400,
      estado: 'vigente',
    },
  ],
  intereses_declarados: [
    'Turismo Pucón en familia (consultado mar-2026)',
    'Becas escolares para nieta',
    'Bono Bodas de Oro para sus padres',
    'Telemedicina y dental urgencia',
  ],
  ultimas_consultas: [
    '¿cuánto me queda en mi crédito?',
    'turismo pucón con mi nieta',
    'bono bodas de oro',
    'dental urgencia copago 100',
  ],
  notas_demo:
    'Persona principal del demo. Quiere consolidar 2 deudas externas (banco + retail) en un crédito social y consultar Bono Bodas de Oro para sus padres (Carmen + cónyuge cumplen 50 años de matrimonio en jul-2026).',
  asignacion_familiar_tramo: 'no_aplica',
};

export const PERSONA_RODRIGO: Persona = {
  id: 'persona-002',
  rut: '17.452.901-K', // [demo]
  nombre_completo: 'Rodrigo Andrés Salinas Vergara',
  primer_nombre: 'Rodrigo',
  edad: 32,
  fecha_nacimiento: '1993-03-22',
  genero: 'M',
  comuna: 'Estación Central',
  region: 'Región Metropolitana',
  direccion: 'Calle Exposición 2210, depto 1206, Estación Central',
  telefono_movil: '+56 9 8821 4509',
  email: 'rodrigo.salinas.demo@ejemplo.cl',
  ocupacion: 'Bodeguero — Operador logístico',
  empleador: 'Walmart Chile S.A. (CD San Bernardo)',
  renta_liquida_clp: 712_500,
  afp: 'Modelo',
  isapre_o_fonasa: 'FONASA Tramo C',
  antiguedad_afiliacion_anos: 7,
  segmento: 'Plata',
  canal_preferido: 'app',
  cargas_familiares: [
    { nombre: 'Maite Salinas Quintero', edad: 4, parentesco: 'hija', estudia: true },
    { nombre: 'Catalina Quintero Reyes', edad: 30, parentesco: 'cónyuge' },
  ],
  productos_contratados: [
    {
      tipo: 'Crédito Universal',
      fecha_inicio: '2025-06-18',
      saldo_actual_clp: 2_650_000,
      cuota_mensual_clp: 112_300,
      estado: 'al_dia',
    },
    {
      tipo: 'Tarjeta Tapp',
      fecha_inicio: '2023-04-09',
      saldo_actual_clp: 18_750,
      estado: 'vigente',
    },
    {
      tipo: 'Asignación Familiar SUF',
      fecha_inicio: '2021-08-01',
      estado: 'vigente',
    },
  ],
  intereses_declarados: [
    'Crédito de salud (parto programado)',
    'Sala cuna convenios',
    'Seguro escolar para Maite el 2027',
  ],
  ultimas_consultas: [
    'asignación familiar tramo c monto',
    'crédito de salud parto',
    'cuenta tapp ahorro',
  ],
  notas_demo:
    'Trabajador joven afiliado vía empleador (Walmart). Útil para demos de afiliación digital y crédito de salud pre-parto.',
  asignacion_familiar_tramo: 'C',
};

export const PERSONA_PATRICIA: Persona = {
  id: 'persona-003',
  rut: '8.345.612-1', // [demo]
  nombre_completo: 'Patricia del Carmen Muñoz Soto',
  primer_nombre: 'Patricia',
  edad: 67,
  fecha_nacimiento: '1958-11-30',
  genero: 'F',
  comuna: 'Concepción',
  region: 'Región del Biobío',
  direccion: 'Calle Lincoyán 845, Concepción',
  telefono_movil: '+56 9 5544 7821',
  email: 'patricia.munoz.demo@ejemplo.cl',
  ocupacion: 'Pensionada — viuda — ex Profesora básica',
  empleador: 'Corporación Municipal de Educación Concepción (jubilada 2016)',
  pension_liquida_clp: 612_400,
  afp: 'Provida',
  isapre_o_fonasa: 'FONASA Tramo B',
  antiguedad_afiliacion_anos: 28,
  segmento: 'Pensionado',
  canal_preferido: 'sucursal',
  cargas_familiares: [],
  productos_contratados: [
    {
      tipo: 'Crédito Social Pensionados',
      fecha_inicio: '2024-08-15',
      saldo_actual_clp: 2_180_000,
      cuota_mensual_clp: 68_900,
      estado: 'al_dia',
    },
    {
      tipo: 'Plan Salud Pensionados',
      fecha_inicio: '2017-01-01',
      cuota_mensual_clp: 14_900,
      estado: 'vigente',
    },
    {
      tipo: 'Seguro de Vida Familiar Full',
      fecha_inicio: '2022-05-20',
      cuota_mensual_clp: 9_990,
      estado: 'vigente',
    },
  ],
  intereses_declarados: [
    'Universidad de la Experiencia (taller de pintura)',
    'Recreación 50+ Concepción',
    'Subsidio defunción cónyuge fallecido feb-2026',
  ],
  ultimas_consultas: [
    'subsidio defunción esposo',
    'club centro pensionados concepción',
    'reajuste pensión abril 2026',
  ],
  notas_demo:
    'Pensionada viuda en Concepción. Útil para demo "AbuelApp" voz multimodal + subsidio defunción.',
  asignacion_familiar_tramo: 'no_aplica',
};

export const PERSONA_JOSE_PYME: Persona = {
  id: 'persona-004',
  rut: '15.892.341-8', // [demo] — RUT del representante; empresa: 76.123.456-9
  nombre_completo: 'José Manuel Toro Cárcamo',
  primer_nombre: 'José',
  edad: 45,
  fecha_nacimiento: '1980-06-07',
  genero: 'M',
  comuna: 'Antofagasta',
  region: 'Región de Antofagasta',
  direccion: 'Avenida Argentina 1850, oficina 302, Antofagasta',
  telefono_movil: '+56 9 9087 6512',
  email: 'jose.toro.demo@panaderiacardenal.cl',
  ocupacion: 'Empresario PYME — dueño de Panadería El Cardenal Ltda.',
  empleador: 'Panadería El Cardenal Ltda. (RUT 76.123.456-9, 14 trabajadores)',
  renta_liquida_clp: 2_350_000,
  afp: 'Cuprum',
  isapre_o_fonasa: 'Banmédica',
  antiguedad_afiliacion_anos: 11,
  segmento: 'Empresa PYME',
  canal_preferido: 'web',
  cargas_familiares: [
    { nombre: 'Diego Toro Henríquez', edad: 16, parentesco: 'hijo', estudia: true },
    { nombre: 'Antonia Toro Henríquez', edad: 13, parentesco: 'hija', estudia: true },
    { nombre: 'Marcela Henríquez Vásquez', edad: 43, parentesco: 'cónyuge' },
  ],
  productos_contratados: [
    {
      tipo: 'Crédito Universal',
      fecha_inicio: '2024-12-01',
      saldo_actual_clp: 5_200_000,
      cuota_mensual_clp: 187_500,
      estado: 'al_dia',
    },
    {
      tipo: 'Seguro de Vida Familiar Full',
      fecha_inicio: '2023-03-10',
      cuota_mensual_clp: 12_800,
      estado: 'vigente',
    },
  ],
  intereses_declarados: [
    'Becas TECLA Talento Emprende para Diego',
    'Programa de bienestar trabajadores panadería',
    'Crédito Educación Superior 2027',
    'Convenios con FlixBus (camiones reparto)',
  ],
  ultimas_consultas: [
    'cómo afiliar mis trabajadores',
    'beca técnica diego 16 años',
    'crédito empresarial',
  ],
  notas_demo:
    'Dueño PYME afiliado y empleador. Útil para demos de Onboarding Conversacional Empresas + becas educación.',
  asignacion_familiar_tramo: 'D',
};

export const PERSONA_VALENTINA_BECA: Persona = {
  id: 'persona-005',
  rut: '21.567.890-4', // [demo]
  nombre_completo: 'Valentina Belén Aguilera Tapia',
  primer_nombre: 'Valentina',
  edad: 19,
  fecha_nacimiento: '2006-09-18',
  genero: 'F',
  comuna: 'Temuco',
  region: 'Región de La Araucanía',
  direccion: 'Calle Caupolicán 1290, Temuco',
  telefono_movil: '+56 9 6611 2098',
  email: 'valentina.aguilera.demo@ejemplo.cl',
  ocupacion: 'Estudiante 1er año — Técnico en Enfermería, INACAP Temuco',
  empleador: undefined,
  renta_liquida_clp: 0,
  afp: 'Modelo',
  isapre_o_fonasa: 'FONASA Tramo A',
  antiguedad_afiliacion_anos: 1,
  segmento: 'Estudiante',
  canal_preferido: 'app',
  cargas_familiares: [],
  productos_contratados: [
    {
      tipo: 'Crédito Educación Superior',
      fecha_inicio: '2026-03-12',
      saldo_actual_clp: 1_950_000,
      cuota_mensual_clp: 0, // periodo de gracia
      estado: 'vigente',
    },
    {
      tipo: 'Tarjeta Tapp',
      fecha_inicio: '2026-03-15',
      saldo_actual_clp: 4_200,
      estado: 'vigente',
    },
  ],
  intereses_declarados: [
    'Becas Caja Los Andes 2026',
    'Convenios con JetSmart Temuco-Santiago',
    'Cupo Colonia Universitaria de verano',
    'Plan Salud joven',
  ],
  ultimas_consultas: [
    'becas estudios técnico cuándo postular',
    'descuento jetsmart',
    'idioma mapudungun',
  ],
  notas_demo:
    'Estudiante mapuche en Temuco, hija de afiliado activo. Útil para demos de selector inclusivo (mapudungun) + becas + Crédito Educación Superior.',
  asignacion_familiar_tramo: 'no_aplica',
};

export const PERSONA_DIEGO_PADRE: Persona = {
  id: 'persona-006',
  rut: '13.987.654-3', // [demo]
  nombre_completo: 'Diego Esteban Riquelme Bustamante',
  primer_nombre: 'Diego',
  edad: 41,
  fecha_nacimiento: '1984-12-03',
  genero: 'M',
  comuna: 'Puente Alto',
  region: 'Región Metropolitana',
  direccion: 'Avenida Concha y Toro 8120, Puente Alto',
  telefono_movil: '+56 9 4422 9087',
  email: 'diego.riquelme.demo@ejemplo.cl',
  ocupacion: 'Conductor de bus — Red Metropolitana',
  empleador: 'STP Santiago S.A. (operador Red)',
  renta_liquida_clp: 925_400,
  afp: 'Habitat',
  isapre_o_fonasa: 'FONASA Tramo C',
  antiguedad_afiliacion_anos: 14,
  segmento: 'Plata',
  canal_preferido: 'whatsapp',
  cargas_familiares: [
    { nombre: 'Camila Riquelme Mora', edad: 11, parentesco: 'hija', estudia: true },
    { nombre: 'Tomás Riquelme Mora', edad: 8, parentesco: 'hijo', estudia: true },
    { nombre: 'Bastián Riquelme Mora', edad: 5, parentesco: 'hijo', estudia: true },
    { nombre: 'Karen Mora Pérez', edad: 38, parentesco: 'cónyuge' },
  ],
  productos_contratados: [
    {
      tipo: 'Crédito Consolidación de Deuda',
      fecha_inicio: '2025-11-08',
      saldo_actual_clp: 3_870_000,
      cuota_mensual_clp: 142_300,
      estado: 'al_dia',
    },
    {
      tipo: 'Asignación Familiar SUF',
      fecha_inicio: '2014-10-01',
      estado: 'vigente',
    },
    {
      tipo: 'Tarjeta Tapp',
      fecha_inicio: '2024-02-22',
      saldo_actual_clp: 67_800,
      estado: 'vigente',
    },
  ],
  intereses_declarados: [
    'Bono Escolar 2026 (3 hijos)',
    'Seguro Escolar para Camila',
    'Plan dental urgencia familia',
    'Cine al Aire Libre Puente Alto',
  ],
  ultimas_consultas: [
    'bono escolar marzo cuánto recibo',
    'seguro escolar caja los andes',
    'urgencia dental copago',
  ],
  notas_demo:
    'Padre con 3 hijos en edad escolar, conductor del Transantiago. Caso clásico de "discovery gap" — califica para múltiples beneficios y los desconoce.',
  asignacion_familiar_tramo: 'C',
};

/* ─────────────────────────────────────────────────────────────────────────── */

export const ALL_PERSONAS: Persona[] = [
  PERSONA_MARIA,
  PERSONA_RODRIGO,
  PERSONA_PATRICIA,
  PERSONA_JOSE_PYME,
  PERSONA_VALENTINA_BECA,
  PERSONA_DIEGO_PADRE,
];

export function getPersonaById(id: string): Persona | undefined {
  return ALL_PERSONAS.find((p) => p.id === id);
}

export function getPersonaByRut(rut: string): Persona | undefined {
  return ALL_PERSONAS.find((p) => p.rut === rut);
}
