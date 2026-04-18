/* =============================================================================
 * mocks/sucursales.ts — Red de sucursales Caja Los Andes
 *
 * Cobertura: 24 sucursales seleccionadas del total de 139 puntos de atención.
 * Direcciones reales basadas en cobertura conocida CCLA (Memoria 2024 §A.4)
 * y direcciones de calles existentes. Coordenadas aproximadas (centroides
 * comunales o intersecciones cercanas — no están georreferenciadas a la
 * sucursal exacta).
 *
 * Casa matriz oficial: General Calderón Nº 121, Providencia, Santiago
 * (research doc §B.5).
 * ============================================================================= */

export type RegionChile =
  | 'Región de Arica y Parinacota'
  | 'Región de Tarapacá'
  | 'Región de Antofagasta'
  | 'Región de Atacama'
  | 'Región de Coquimbo'
  | 'Región de Valparaíso'
  | 'Región Metropolitana'
  | 'Región del Libertador General Bernardo O\'Higgins'
  | 'Región del Maule'
  | 'Región de Ñuble'
  | 'Región del Biobío'
  | 'Región de La Araucanía'
  | 'Región de Los Ríos'
  | 'Región de Los Lagos'
  | 'Región de Aysén del General Carlos Ibáñez del Campo'
  | 'Región de Magallanes y de la Antártica Chilena';

export interface HorarioSemana {
  lunes_a_viernes: string;
  sabado?: string;
  domingo?: string;
  feriados?: string;
}

export interface Sucursal {
  id: string;
  nombre: string;
  direccion: string;
  comuna: string;
  region: RegionChile;
  codigo_region: string; // ISO 3166-2:CL
  telefono?: string;
  horario: HorarioSemana;
  servicios: ('Crédito Social' | 'Beneficios' | 'Salud' | 'Tapp' | 'Pensionados' | 'Empresas' | 'Tótem Autoatención')[];
  totem_autoatencion: boolean;
  estacionamiento: boolean;
  accesibilidad_pmr: boolean;
  lat: number;
  lng: number;
  es_casa_matriz?: boolean;
}

const HORARIO_ESTANDAR: HorarioSemana = {
  lunes_a_viernes: '09:00 a 14:00 y 15:00 a 18:00',
  sabado: 'Cerrado',
  domingo: 'Cerrado',
};

const HORARIO_EXT: HorarioSemana = {
  lunes_a_viernes: '09:00 a 18:00 (jornada continua)',
  sabado: '10:00 a 13:00',
  domingo: 'Cerrado',
};

export const SUCURSALES: Sucursal[] = [
  /* ===== Región Metropolitana ===== */
  {
    id: 'suc-providencia-matriz',
    nombre: 'Casa Matriz Providencia',
    direccion: 'General Calderón 121',
    comuna: 'Providencia',
    region: 'Región Metropolitana',
    codigo_region: 'CL-RM',
    telefono: '600 510 0000',
    horario: HORARIO_EXT,
    servicios: ['Crédito Social', 'Beneficios', 'Salud', 'Tapp', 'Pensionados', 'Empresas', 'Tótem Autoatención'],
    totem_autoatencion: true,
    estacionamiento: true,
    accesibilidad_pmr: true,
    lat: -33.4225,
    lng: -70.6066,
    es_casa_matriz: true,
  },
  {
    id: 'suc-santiago-centro',
    nombre: 'Sucursal Santiago Centro',
    direccion: 'Bandera 220',
    comuna: 'Santiago',
    region: 'Región Metropolitana',
    codigo_region: 'CL-RM',
    telefono: '600 510 0000',
    horario: HORARIO_ESTANDAR,
    servicios: ['Crédito Social', 'Beneficios', 'Pensionados', 'Tótem Autoatención'],
    totem_autoatencion: true,
    estacionamiento: false,
    accesibilidad_pmr: true,
    lat: -33.4380,
    lng: -70.6500,
  },
  {
    id: 'suc-las-condes',
    nombre: 'Sucursal Las Condes — Apoquindo',
    direccion: 'Avenida Apoquindo 4775, Local 142',
    comuna: 'Las Condes',
    region: 'Región Metropolitana',
    codigo_region: 'CL-RM',
    telefono: '600 510 0000',
    horario: HORARIO_EXT,
    servicios: ['Crédito Social', 'Beneficios', 'Tapp', 'Empresas', 'Tótem Autoatención'],
    totem_autoatencion: true,
    estacionamiento: true,
    accesibilidad_pmr: true,
    lat: -33.4106,
    lng: -70.5797,
  },
  {
    id: 'suc-maipu',
    nombre: 'Sucursal Maipú',
    direccion: 'Av. Pajaritos 2742, Local 18',
    comuna: 'Maipú',
    region: 'Región Metropolitana',
    codigo_region: 'CL-RM',
    horario: HORARIO_EXT,
    servicios: ['Crédito Social', 'Beneficios', 'Pensionados', 'Tótem Autoatención'],
    totem_autoatencion: true,
    estacionamiento: true,
    accesibilidad_pmr: true,
    lat: -33.5104,
    lng: -70.7574,
  },
  {
    id: 'suc-puente-alto',
    nombre: 'Sucursal Puente Alto',
    direccion: 'Avenida Concha y Toro 2510',
    comuna: 'Puente Alto',
    region: 'Región Metropolitana',
    codigo_region: 'CL-RM',
    horario: HORARIO_ESTANDAR,
    servicios: ['Crédito Social', 'Beneficios', 'Tótem Autoatención'],
    totem_autoatencion: true,
    estacionamiento: false,
    accesibilidad_pmr: true,
    lat: -33.6111,
    lng: -70.5764,
  },
  {
    id: 'suc-la-florida',
    nombre: 'Sucursal La Florida',
    direccion: 'Av. Vicuña Mackenna Oriente 7080',
    comuna: 'La Florida',
    region: 'Región Metropolitana',
    codigo_region: 'CL-RM',
    horario: HORARIO_ESTANDAR,
    servicios: ['Crédito Social', 'Beneficios', 'Pensionados', 'Tótem Autoatención'],
    totem_autoatencion: true,
    estacionamiento: true,
    accesibilidad_pmr: true,
    lat: -33.5236,
    lng: -70.5993,
  },
  {
    id: 'suc-nunoa',
    nombre: 'Sucursal Ñuñoa',
    direccion: 'Avenida Irarrázaval 3275',
    comuna: 'Ñuñoa',
    region: 'Región Metropolitana',
    codigo_region: 'CL-RM',
    horario: HORARIO_ESTANDAR,
    servicios: ['Crédito Social', 'Beneficios', 'Pensionados'],
    totem_autoatencion: false,
    estacionamiento: false,
    accesibilidad_pmr: true,
    lat: -33.4569,
    lng: -70.6024,
  },
  {
    id: 'suc-san-bernardo',
    nombre: 'Sucursal San Bernardo',
    direccion: 'Avenida San Bernardo 1430',
    comuna: 'San Bernardo',
    region: 'Región Metropolitana',
    codigo_region: 'CL-RM',
    horario: HORARIO_ESTANDAR,
    servicios: ['Crédito Social', 'Beneficios', 'Tótem Autoatención'],
    totem_autoatencion: true,
    estacionamiento: true,
    accesibilidad_pmr: true,
    lat: -33.5921,
    lng: -70.7077,
  },
  /* ===== Norte Grande ===== */
  {
    id: 'suc-arica',
    nombre: 'Sucursal Arica',
    direccion: 'Calle 21 de Mayo 247',
    comuna: 'Arica',
    region: 'Región de Arica y Parinacota',
    codigo_region: 'CL-AP',
    horario: HORARIO_ESTANDAR,
    servicios: ['Crédito Social', 'Beneficios', 'Pensionados', 'Empresas'],
    totem_autoatencion: true,
    estacionamiento: false,
    accesibilidad_pmr: true,
    lat: -18.4783,
    lng: -70.3126,
  },
  {
    id: 'suc-iquique',
    nombre: 'Sucursal Iquique',
    direccion: 'Calle Tarapacá 458',
    comuna: 'Iquique',
    region: 'Región de Tarapacá',
    codigo_region: 'CL-TA',
    horario: HORARIO_ESTANDAR,
    servicios: ['Crédito Social', 'Beneficios', 'Tapp', 'Empresas'],
    totem_autoatencion: true,
    estacionamiento: false,
    accesibilidad_pmr: true,
    lat: -20.2208,
    lng: -70.1431,
  },
  {
    id: 'suc-antofagasta',
    nombre: 'Sucursal Antofagasta',
    direccion: 'Avenida Argentina 1934',
    comuna: 'Antofagasta',
    region: 'Región de Antofagasta',
    codigo_region: 'CL-AN',
    horario: HORARIO_EXT,
    servicios: ['Crédito Social', 'Beneficios', 'Pensionados', 'Empresas', 'Tótem Autoatención'],
    totem_autoatencion: true,
    estacionamiento: true,
    accesibilidad_pmr: true,
    lat: -23.6500,
    lng: -70.4000,
  },
  {
    id: 'suc-calama',
    nombre: 'Sucursal Calama',
    direccion: 'Calle Vivar 1820',
    comuna: 'Calama',
    region: 'Región de Antofagasta',
    codigo_region: 'CL-AN',
    horario: HORARIO_ESTANDAR,
    servicios: ['Crédito Social', 'Beneficios', 'Empresas'],
    totem_autoatencion: true,
    estacionamiento: false,
    accesibilidad_pmr: true,
    lat: -22.4569,
    lng: -68.9293,
  },
  {
    id: 'suc-copiapo',
    nombre: 'Sucursal Copiapó',
    direccion: 'Calle Atacama 538',
    comuna: 'Copiapó',
    region: 'Región de Atacama',
    codigo_region: 'CL-AT',
    horario: HORARIO_ESTANDAR,
    servicios: ['Crédito Social', 'Beneficios', 'Pensionados'],
    totem_autoatencion: false,
    estacionamiento: true,
    accesibilidad_pmr: true,
    lat: -27.3668,
    lng: -70.3325,
  },
  {
    id: 'suc-la-serena',
    nombre: 'Sucursal La Serena',
    direccion: 'Avenida Francisco de Aguirre 285',
    comuna: 'La Serena',
    region: 'Región de Coquimbo',
    codigo_region: 'CL-CO',
    horario: HORARIO_ESTANDAR,
    servicios: ['Crédito Social', 'Beneficios', 'Pensionados', 'Empresas'],
    totem_autoatencion: true,
    estacionamiento: true,
    accesibilidad_pmr: true,
    lat: -29.9027,
    lng: -71.2519,
  },
  /* ===== Centro ===== */
  {
    id: 'suc-valparaiso',
    nombre: 'Sucursal Valparaíso',
    direccion: 'Calle Esmeralda 940',
    comuna: 'Valparaíso',
    region: 'Región de Valparaíso',
    codigo_region: 'CL-VS',
    telefono: '600 510 0000',
    horario: HORARIO_EXT,
    servicios: ['Crédito Social', 'Beneficios', 'Pensionados', 'Empresas', 'Tótem Autoatención'],
    totem_autoatencion: true,
    estacionamiento: false,
    accesibilidad_pmr: true,
    lat: -33.0458,
    lng: -71.6197,
  },
  {
    id: 'suc-vina-del-mar',
    nombre: 'Sucursal Viña del Mar',
    direccion: 'Avenida Libertad 250',
    comuna: 'Viña del Mar',
    region: 'Región de Valparaíso',
    codigo_region: 'CL-VS',
    horario: HORARIO_EXT,
    servicios: ['Crédito Social', 'Beneficios', 'Tapp', 'Pensionados'],
    totem_autoatencion: true,
    estacionamiento: true,
    accesibilidad_pmr: true,
    lat: -33.0246,
    lng: -71.5518,
  },
  {
    id: 'suc-rancagua',
    nombre: 'Sucursal Rancagua',
    direccion: 'Calle Independencia 575',
    comuna: 'Rancagua',
    region: 'Región del Libertador General Bernardo O\'Higgins',
    codigo_region: 'CL-LI',
    horario: HORARIO_ESTANDAR,
    servicios: ['Crédito Social', 'Beneficios', 'Pensionados', 'Empresas'],
    totem_autoatencion: true,
    estacionamiento: true,
    accesibilidad_pmr: true,
    lat: -34.1701,
    lng: -70.7406,
  },
  {
    id: 'suc-talca',
    nombre: 'Sucursal Talca',
    direccion: 'Calle 1 Sur 1156',
    comuna: 'Talca',
    region: 'Región del Maule',
    codigo_region: 'CL-ML',
    horario: HORARIO_ESTANDAR,
    servicios: ['Crédito Social', 'Beneficios', 'Pensionados'],
    totem_autoatencion: true,
    estacionamiento: false,
    accesibilidad_pmr: true,
    lat: -35.4264,
    lng: -71.6553,
  },
  /* ===== Sur ===== */
  {
    id: 'suc-chillan',
    nombre: 'Sucursal Chillán',
    direccion: 'Calle Constitución 685',
    comuna: 'Chillán',
    region: 'Región de Ñuble',
    codigo_region: 'CL-NB',
    horario: HORARIO_ESTANDAR,
    servicios: ['Crédito Social', 'Beneficios', 'Pensionados', 'Empresas'],
    totem_autoatencion: true,
    estacionamiento: true,
    accesibilidad_pmr: true,
    lat: -36.6066,
    lng: -72.1034,
  },
  {
    id: 'suc-concepcion',
    nombre: 'Sucursal Concepción',
    direccion: 'Calle Aníbal Pinto 442',
    comuna: 'Concepción',
    region: 'Región del Biobío',
    codigo_region: 'CL-BI',
    telefono: '600 510 0000',
    horario: HORARIO_EXT,
    servicios: ['Crédito Social', 'Beneficios', 'Salud', 'Pensionados', 'Empresas', 'Tótem Autoatención'],
    totem_autoatencion: true,
    estacionamiento: true,
    accesibilidad_pmr: true,
    lat: -36.8270,
    lng: -73.0498,
  },
  {
    id: 'suc-temuco',
    nombre: 'Sucursal Temuco',
    direccion: 'Avenida Alemania 0671',
    comuna: 'Temuco',
    region: 'Región de La Araucanía',
    codigo_region: 'CL-AR',
    horario: HORARIO_EXT,
    servicios: ['Crédito Social', 'Beneficios', 'Pensionados', 'Empresas', 'Tótem Autoatención'],
    totem_autoatencion: true,
    estacionamiento: true,
    accesibilidad_pmr: true,
    lat: -38.7359,
    lng: -72.5904,
  },
  {
    id: 'suc-valdivia',
    nombre: 'Sucursal Valdivia',
    direccion: 'Calle Independencia 521',
    comuna: 'Valdivia',
    region: 'Región de Los Ríos',
    codigo_region: 'CL-LR',
    horario: HORARIO_ESTANDAR,
    servicios: ['Crédito Social', 'Beneficios', 'Pensionados'],
    totem_autoatencion: false,
    estacionamiento: false,
    accesibilidad_pmr: true,
    lat: -39.8142,
    lng: -73.2459,
  },
  {
    id: 'suc-osorno',
    nombre: 'Sucursal Osorno',
    direccion: 'Calle Mackenna 920',
    comuna: 'Osorno',
    region: 'Región de Los Lagos',
    codigo_region: 'CL-LL',
    horario: HORARIO_ESTANDAR,
    servicios: ['Crédito Social', 'Beneficios', 'Pensionados'],
    totem_autoatencion: true,
    estacionamiento: true,
    accesibilidad_pmr: true,
    lat: -40.5743,
    lng: -73.1330,
  },
  {
    id: 'suc-puerto-montt',
    nombre: 'Sucursal Puerto Montt',
    direccion: 'Calle Antonio Varas 595',
    comuna: 'Puerto Montt',
    region: 'Región de Los Lagos',
    codigo_region: 'CL-LL',
    horario: HORARIO_EXT,
    servicios: ['Crédito Social', 'Beneficios', 'Pensionados', 'Empresas'],
    totem_autoatencion: true,
    estacionamiento: true,
    accesibilidad_pmr: true,
    lat: -41.4717,
    lng: -72.9360,
  },
  /* ===== Austral ===== */
  {
    id: 'suc-coyhaique',
    nombre: 'Sucursal Coyhaique',
    direccion: 'Calle Condell 137',
    comuna: 'Coyhaique',
    region: 'Región de Aysén del General Carlos Ibáñez del Campo',
    codigo_region: 'CL-AI',
    horario: HORARIO_ESTANDAR,
    servicios: ['Crédito Social', 'Beneficios', 'Pensionados'],
    totem_autoatencion: false,
    estacionamiento: false,
    accesibilidad_pmr: true,
    lat: -45.5712,
    lng: -72.0685,
  },
  {
    id: 'suc-punta-arenas',
    nombre: 'Sucursal Punta Arenas',
    direccion: 'Calle Roca 826',
    comuna: 'Punta Arenas',
    region: 'Región de Magallanes y de la Antártica Chilena',
    codigo_region: 'CL-MA',
    horario: HORARIO_ESTANDAR,
    servicios: ['Crédito Social', 'Beneficios', 'Pensionados', 'Empresas'],
    totem_autoatencion: true,
    estacionamiento: true,
    accesibilidad_pmr: true,
    lat: -53.1638,
    lng: -70.9171,
  },
];

export function getSucursalById(id: string): Sucursal | undefined {
  return SUCURSALES.find((s) => s.id === id);
}

export function getSucursalesByRegion(region: RegionChile): Sucursal[] {
  return SUCURSALES.filter((s) => s.region === region);
}

export function getSucursalesByComuna(comuna: string): Sucursal[] {
  return SUCURSALES.filter((s) => s.comuna.toLowerCase() === comuna.toLowerCase());
}
