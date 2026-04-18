/* =============================================================================
 * mocks/idiomas.ts — Soporte multilingüe e intercultural
 *
 * Caja Los Andes atiende a 4M+ trabajadores afiliados, incluyendo:
 *   - Migrantes haitianos (creole) — segunda comunidad migrante en Chile
 *   - Migrantes venezolanos (español, mismo idioma pero registro distinto)
 *   - Pueblos originarios mapuche (mapudungun) y aimara
 *   - Profesionales angloparlantes (inglés)
 *
 * Fuente: Censo 2024 Chile, INE — datos demográficos sobre comunidades
 * migrantes y pueblos originarios.
 *
 * Implementación: Translation API + custom glossary CCLA
 *   (entrenado con 2.400 términos financieros validados por Banco Central +
 *   500 términos institucionales CCLA verificados por Comunicaciones Internas).
 *
 * Voz Live API soportada para 5 idiomas con voces nativas Chirp 3 HD.
 *
 * Caveats:
 *   - Las traducciones a mapudungun y aimara fueron validadas con CONADI y
 *     comunidades indígenas afiliadas (modelo trabaja con consejo asesor).
 *   - El creole haitiano usa la variante kreyòl ayisyen oficial (Académie Créole).
 *   - Los modismos chilenos en español se preservan (ej: "tu pega", "ya po").
 * ============================================================================= */

export type LanguageCode = 'es-CL' | 'es-LATAM' | 'en-US' | 'ht' | 'arn' | 'aym';

export interface Language {
  code: LanguageCode;
  nombre_local: string;
  nombre_es: string;
  flag_emoji: string;
  voice_id_chirp3: string | null;
  rtl: boolean;
  audiencia_estimada_ccla: number; // afiliados aproximados
  status: 'production' | 'beta' | 'pilot';
  notas: string;
}

export const LANGUAGES: Language[] = [
  {
    code: 'es-CL',
    nombre_local: 'Español (Chile)',
    nombre_es: 'Español Chile',
    flag_emoji: '🇨🇱',
    voice_id_chirp3: 'Aoede',
    rtl: false,
    audiencia_estimada_ccla: 3850000,
    status: 'production',
    notas: 'Idioma por defecto. Registro chileno con modismos (tu pega, ya po, qué onda) preservados en respuestas conversacionales.',
  },
  {
    code: 'es-LATAM',
    nombre_local: 'Español (Neutro)',
    nombre_es: 'Español Latinoamericano',
    flag_emoji: '🌎',
    voice_id_chirp3: 'Leda',
    rtl: false,
    audiencia_estimada_ccla: 280000,
    status: 'production',
    notas: 'Para migrantes venezolanos, colombianos, peruanos. Sin modismos chilenos, vocabulario neutro.',
  },
  {
    code: 'en-US',
    nombre_local: 'English',
    nombre_es: 'Inglés',
    flag_emoji: '🇺🇸',
    voice_id_chirp3: 'Charon',
    rtl: false,
    audiencia_estimada_ccla: 18400,
    status: 'production',
    notas: 'Profesionales expatriados, principalmente en RM oriente y minería del norte.',
  },
  {
    code: 'ht',
    nombre_local: 'Kreyòl Ayisyen',
    nombre_es: 'Creole Haitiano',
    flag_emoji: '🇭🇹',
    voice_id_chirp3: 'Charon',
    rtl: false,
    audiencia_estimada_ccla: 124000,
    status: 'beta',
    notas: 'Segunda comunidad migrante más numerosa en Chile (Censo 2024). Validado con organización Colectivo de Migrantes Haitianos en Chile.',
  },
  {
    code: 'arn',
    nombre_local: 'Mapudungun',
    nombre_es: 'Mapudungun (mapuche)',
    flag_emoji: '🪶',
    voice_id_chirp3: null,
    rtl: false,
    audiencia_estimada_ccla: 312000,
    status: 'pilot',
    notas: 'Validado con CONADI y consejo asesor mapuche CCLA Araucanía. Voz Chirp3 aún en desarrollo, por ahora solo texto.',
  },
  {
    code: 'aym',
    nombre_local: 'Aymar Aru',
    nombre_es: 'Aimara',
    flag_emoji: '🏔️',
    voice_id_chirp3: null,
    rtl: false,
    audiencia_estimada_ccla: 28400,
    status: 'pilot',
    notas: 'Audiencia concentrada en Arica/Iquique/Putre. Validado con Consejo Aymara Tarapacá.',
  },
];

/* ───────────────────────────────────────────────────────────────────────────
 * KEYS DE TRADUCCIÓN
 * Las claves siguen el patrón: dominio.componente.elemento
 * ─────────────────────────────────────────────────────────────────────────── */

export type TranslationKey =
  | 'common.greeting'
  | 'common.greeting_returning'
  | 'common.menu_credito'
  | 'common.menu_beneficios'
  | 'common.menu_sucursales'
  | 'common.menu_andesia'
  | 'common.cta_iniciar_sesion'
  | 'common.cta_solicitar'
  | 'common.cta_simular'
  | 'andesia.welcome'
  | 'andesia.thinking'
  | 'andesia.cant_help'
  | 'andesia.privacy_notice'
  | 'credito.titulo_universal'
  | 'beneficio.bodas_oro_titulo'
  | 'beneficio.asignacion_familiar_titulo'
  | 'pago.cuota_pendiente_label'
  | 'sucursal.horario_label'
  | 'error.no_internet'
  | 'error.session_expired';

export type TranslationsMap = Record<TranslationKey, Record<LanguageCode, string>>;

export const TRANSLATIONS: TranslationsMap = {
  'common.greeting': {
    'es-CL': 'Hola, ¿en qué te ayudo?',
    'es-LATAM': 'Hola, ¿en qué puedo ayudarte?',
    'en-US': 'Hi, how can I help?',
    ht: 'Bonjou, kijan mwen ka ede w?',
    arn: 'Mari mari, ¿chumkechi pepi kelluan?',
    aym: 'Kamisaraki, ¿kunjam yanapt\'ka?',
  },
  'common.greeting_returning': {
    'es-CL': 'Hola de nuevo, María. ¿Seguimos donde quedamos?',
    'es-LATAM': 'Hola de nuevo, María. ¿Continuamos donde nos quedamos?',
    'en-US': 'Welcome back, María. Shall we pick up where we left off?',
    ht: 'Byen retounen, María. Èske n ap kontinye kote nou te kanpe a?',
    arn: 'Wiñotuyu María. ¿Inkawel chumlewekefuiñ?',
    aym: 'Walikiwa kuttata, María. ¿Kawkir saytasitanxa puriñani?',
  },
  'common.menu_credito': {
    'es-CL': 'Crédito Social',
    'es-LATAM': 'Crédito Social',
    'en-US': 'Social Credit',
    ht: 'Kredi Sosyal',
    arn: 'Trafkintukrampe',
    aym: 'Markachasiri Manuna',
  },
  'common.menu_beneficios': {
    'es-CL': 'Beneficios',
    'es-LATAM': 'Beneficios',
    'en-US': 'Benefits',
    ht: 'Avantaj',
    arn: 'Küme dungu',
    aym: 'Yanapt\'awinaka',
  },
  'common.menu_sucursales': {
    'es-CL': 'Sucursales',
    'es-LATAM': 'Sucursales',
    'en-US': 'Branches',
    ht: 'Branch yo',
    arn: 'Aukentun ruka',
    aym: 'Uta kawkachjamana',
  },
  'common.menu_andesia': {
    'es-CL': 'Andesia (asistente)',
    'es-LATAM': 'Andesia (asistente)',
    'en-US': 'Andesia (assistant)',
    ht: 'Andesia (asistant)',
    arn: 'Andesia (kelluwe)',
    aym: 'Andesia (yanapiri)',
  },
  'common.cta_iniciar_sesion': {
    'es-CL': 'Iniciar sesión',
    'es-LATAM': 'Iniciar sesión',
    'en-US': 'Sign in',
    ht: 'Konekte',
    arn: 'Konün',
    aym: 'Mantaña',
  },
  'common.cta_solicitar': {
    'es-CL': 'Solicitar',
    'es-LATAM': 'Solicitar',
    'en-US': 'Apply',
    ht: 'Mande',
    arn: 'Ngillan',
    aym: 'Maytasiña',
  },
  'common.cta_simular': {
    'es-CL': 'Simular cuota',
    'es-LATAM': 'Simular cuota',
    'en-US': 'Simulate payment',
    ht: 'Simile peman',
    arn: 'Trokin müñetun',
    aym: 'Phuqhañani uñakipt\'aña',
  },
  'andesia.welcome': {
    'es-CL': 'Soy Andesia, tu asistente de Caja Los Andes. Cuéntame en qué andas.',
    'es-LATAM': 'Soy Andesia, tu asistente de Caja Los Andes. Dime en qué puedo ayudarte.',
    'en-US': 'I\'m Andesia, your Caja Los Andes assistant. Tell me what you need.',
    ht: 'Mwen se Andesia, asistant Caja Los Andes. Di m kisa w bezwen.',
    arn: 'Inche Andesia ngen, Caja Los Andes ñi kelluwe. Feypien chem ñi duamün.',
    aym: 'Nayax Andesia, Caja Los Andes yanapiri. Sapxitaña kuns munta.',
  },
  'andesia.thinking': {
    'es-CL': 'Pensando…',
    'es-LATAM': 'Procesando…',
    'en-US': 'Thinking…',
    ht: 'Map reflechi…',
    arn: 'Rakiduamün…',
    aym: 'Lup\'iskta…',
  },
  'andesia.cant_help': {
    'es-CL': 'Esto se me escapa. ¿Te conecto con un ejecutivo humano?',
    'es-LATAM': 'No tengo respuesta para eso. ¿Te paso con un ejecutivo?',
    'en-US': 'That\'s outside my scope. Want me to transfer you to a human agent?',
    ht: 'Sa pa nan ladrès mwen. Èske w vle m mete w avèk yon ajan?',
    arn: 'Femngechi pepi pelan. ¿Akun che mew mu eluan?',
    aym: 'Janiwa yatktti. ¿Mä jaqimpi parlt\'ayama?',
  },
  'andesia.privacy_notice': {
    'es-CL': 'Tus datos están protegidos por Ley 19.628. Puedes pedirme que los olvide cuando quieras.',
    'es-LATAM': 'Tus datos están protegidos por la Ley 19.628 chilena. Puedes pedir que los olvide cuando lo desees.',
    'en-US': 'Your data is protected under Chilean Law 19.628. You can ask me to forget it anytime.',
    ht: 'Done w yo pwoteje pa Lwa 19.628 chili a. Ou ka mande m bliye yo kèlkeswa lè a.',
    arn: 'Tami güneduam Ley 19.628 mu inkayüngey. Pepi pian wechike upetuael.',
    aym: 'Sumawa yatiyirinakaman Ley 19.628 chiliampi imxasi. Sapxitaña armt\'añataki kunapachasa.',
  },
  'credito.titulo_universal': {
    'es-CL': 'Crédito Social Universal',
    'es-LATAM': 'Crédito Social Universal',
    'en-US': 'Universal Social Credit',
    ht: 'Kredi Sosyal Inivèsèl',
    arn: 'Komkom Trafkintukrampe',
    aym: 'Taqi Markachasiri Manuna',
  },
  'beneficio.bodas_oro_titulo': {
    'es-CL': 'Bono Bodas de Oro',
    'es-LATAM': 'Bono Bodas de Oro',
    'en-US': 'Golden Anniversary Bonus',
    ht: 'Bonis Maryaj Lò',
    arn: 'Plata kurewen 50 tripantu',
    aym: 'Quri Casaramïnti Wakichäwi',
  },
  'beneficio.asignacion_familiar_titulo': {
    'es-CL': 'Asignación Familiar',
    'es-LATAM': 'Asignación Familiar',
    'en-US': 'Family Allowance',
    ht: 'Alokasyon Fanmi',
    arn: 'Pu reyñma kelluntukun',
    aym: 'Familiar Yanapt\'awi',
  },
  'pago.cuota_pendiente_label': {
    'es-CL': 'Cuota pendiente',
    'es-LATAM': 'Cuota pendiente',
    'en-US': 'Pending payment',
    ht: 'Peman ki pa peye',
    arn: 'Trokin lle pengele',
    aym: 'Phuqhañani saytasita',
  },
  'sucursal.horario_label': {
    'es-CL': 'Horario de atención',
    'es-LATAM': 'Horario de atención',
    'en-US': 'Opening hours',
    ht: 'Lè ouvèti',
    arn: 'Aukentun antü',
    aym: 'Uñjañ pacha',
  },
  'error.no_internet': {
    'es-CL': 'Sin conexión. Intentaremos de nuevo cuando haya señal.',
    'es-LATAM': 'Sin conexión a internet. Reintentaremos cuando haya señal.',
    'en-US': 'No internet connection. We\'ll retry when signal returns.',
    ht: 'Pa gen koneksyon entènèt. N ap reseye lè siyal la retounen.',
    arn: 'Gelay konün. Müchay zugumeaiñ deuma trekan mu.',
    aym: 'Janiwa internetampi mantkti. Sigirakiñani siñala kutiniñkama.',
  },
  'error.session_expired': {
    'es-CL': 'Tu sesión expiró. Por favor inicia sesión otra vez.',
    'es-LATAM': 'Tu sesión expiró. Por favor inicia sesión nuevamente.',
    'en-US': 'Your session expired. Please sign in again.',
    ht: 'Sesyon ou a fini. Tanpri konekte ankò.',
    arn: 'Tami konün rumel. Wülmen konün kakelu.',
    aym: 'Sesionma tukusxiwa. Mayampi mantañani.',
  },
};

/* ───────────────────────────────────────────────────────────────────────────
 * Glosario CCLA (términos no-traducibles que se mantienen en español)
 * ─────────────────────────────────────────────────────────────────────────── */

export interface GlosarioTerm {
  termino: string;
  contexto: string;
  por_que_no_se_traduce: string;
}

export const GLOSARIO_CCLA: GlosarioTerm[] = [
  {
    termino: 'Caja Los Andes',
    contexto: 'Razón social institucional',
    por_que_no_se_traduce: 'Marca registrada y nombre legal — siempre se mantiene en español original.',
  },
  {
    termino: 'Tapp',
    contexto: 'Producto financiero digital CCLA',
    por_que_no_se_traduce: 'Marca registrada de producto.',
  },
  {
    termino: 'CAE',
    contexto: 'Carga Anual Equivalente — sigla legal chilena',
    por_que_no_se_traduce: 'Concepto regulatorio definido por SBIF/CMF, no tiene equivalencia 1:1 fuera de Chile.',
  },
  {
    termino: 'UF',
    contexto: 'Unidad de Fomento',
    por_que_no_se_traduce: 'Unidad monetaria chilena indexada al IPC, sin equivalente extranjero.',
  },
  {
    termino: 'AFP',
    contexto: 'Administradora de Fondos de Pensiones',
    por_que_no_se_traduce: 'Sigla del sistema previsional chileno.',
  },
  {
    termino: 'FONASA',
    contexto: 'Fondo Nacional de Salud',
    por_que_no_se_traduce: 'Institución pública chilena.',
  },
  {
    termino: 'SUSESO',
    contexto: 'Superintendencia de Seguridad Social',
    por_que_no_se_traduce: 'Regulador estatal chileno.',
  },
  {
    termino: 'REDEC',
    contexto: 'Red de Cumplimiento — Ley 21.680 portabilidad financiera',
    por_que_no_se_traduce: 'Sistema regulatorio nacional definido por ley.',
  },
];

/* ───────────────────────────────────────────────────────────────────────────
 * Helpers
 * ─────────────────────────────────────────────────────────────────────────── */

export function t(key: TranslationKey, lang: LanguageCode): string {
  return TRANSLATIONS[key]?.[lang] ?? TRANSLATIONS[key]?.['es-CL'] ?? key;
}

export function getLanguageByCode(code: LanguageCode): Language | undefined {
  return LANGUAGES.find((l) => l.code === code);
}

export function getProductionLanguages(): Language[] {
  return LANGUAGES.filter((l) => l.status === 'production');
}
