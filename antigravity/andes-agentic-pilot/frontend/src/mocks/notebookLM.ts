/* =============================================================================
 * mocks/notebookLM.ts — AndesTV podcast/video overview
 *
 * Metadata para 3 episodios pre-renderizados estilo NotebookLM:
 *   1. "Tu Resumen Semanal — Abril 3era semana 2026" (audio + cinematic video)
 *   2. "Cómo aprovechar tu Crédito Consolidación" (audio podcast 2 voces)
 *   3. "Bono Bodas de Oro — Lo que tu familia debe saber" (cinematic video corto)
 *
 * Capability: NotebookLM Cinematic Video Overviews (lanzado 4-mar-2026)
 * que combina Gemini 3 + Nano Banana Pro + Veo 3.1.
 * Ref: docs/wow_features_apr2026.md Add-on #2
 *
 * Voces: Chirp 3 HD GA feb-2026 — voces "Aoede" (femenina cálida latina)
 * y "Charon" (masculina latina informal).
 * ============================================================================= */

export type EpisodeFormat = 'video_cinematic' | 'audio_podcast' | 'audio_overview' | 'video_short';
export type EpisodeAudience = 'maria' | 'pensionados' | 'trabajadores' | 'pyme' | 'general';

export interface PodcastSpeaker {
  id: string;
  display_name: string;
  voice_engine: 'chirp-3-hd' | 'wavenet' | 'studio';
  voice_id: string;
  language: 'es-CL' | 'es' | 'en';
  persona: 'host_curioso' | 'experto_caja' | 'narrador_calmado' | 'periodista';
  description: string;
}

export interface TranscriptLine {
  timestamp_seconds: number;
  speaker_id: string;
  text: string;
}

export interface SourceDocument {
  id: string;
  title: string;
  url: string;
  type: 'pdf' | 'web' | 'reglamento' | 'noticia' | 'memoria_anual';
  pages_or_section?: string;
}

export interface AndesTVEpisode {
  id: string;
  title: string;
  subtitle: string;
  format: EpisodeFormat;
  duration_seconds: number;
  generated_at: string;
  generation_model: string;
  language: 'es-CL';
  audience: EpisodeAudience;
  thumbnail_url: string;
  video_url?: string;
  audio_url?: string;
  speakers: PodcastSpeaker[];
  transcript: TranscriptLine[];
  sources: SourceDocument[];
  cta_after_play?: { label: string; destino: string };
  shareable: boolean;
  share_text?: string;
}

/* ─────────────────────────────────────────────────────────────────────────── */
/* === Voces estándar AndesTV ============================================  */
/* ─────────────────────────────────────────────────────────────────────────── */

const VOICE_AOEDE: PodcastSpeaker = {
  id: 'speaker-aoede',
  display_name: 'Catalina (host)',
  voice_engine: 'chirp-3-hd',
  voice_id: 'es-CL-Chirp3-HD-Aoede',
  language: 'es-CL',
  persona: 'host_curioso',
  description: 'Voz femenina chilena, cálida, registro coloquial-formal. Ritmo conversacional.',
};

const VOICE_CHARON: PodcastSpeaker = {
  id: 'speaker-charon',
  display_name: 'Tomás (experto)',
  voice_engine: 'chirp-3-hd',
  voice_id: 'es-CL-Chirp3-HD-Charon',
  language: 'es-CL',
  persona: 'experto_caja',
  description: 'Voz masculina chilena adulta, autoritativa pero accesible. Explica conceptos financieros.',
};

const VOICE_NARRATOR: PodcastSpeaker = {
  id: 'speaker-narrator',
  display_name: 'Narradora',
  voice_engine: 'chirp-3-hd',
  voice_id: 'es-CL-Chirp3-HD-Leda',
  language: 'es-CL',
  persona: 'narrador_calmado',
  description: 'Voz femenina chilena, registro neutro-formal. Para resúmenes personales.',
};

/* ─────────────────────────────────────────────────────────────────────────── */
/* === Episodio 1 — Resumen Semanal Personalizado para María ==============  */
/* ─────────────────────────────────────────────────────────────────────────── */

export const EPISODE_RESUMEN_SEMANAL_MARIA: AndesTVEpisode = {
  id: 'andestv-001',
  title: 'Tu Resumen — Abril 3era semana 2026',
  subtitle: 'María González · 28 segundos · Cinematic Overview',
  format: 'video_cinematic',
  duration_seconds: 28,
  generated_at: '2026-04-20T10:31:38-04:00',
  generation_model: 'NotebookLM Cinematic (Gemini 3 + Nano Banana Pro + Veo 3.1)',
  language: 'es-CL',
  audience: 'maria',
  thumbnail_url: '/mocks/img/andestv-resumen-maria-thumb.jpg',
  video_url: '/mocks/video/andestv-resumen-maria.mp4',
  speakers: [VOICE_NARRATOR],
  transcript: [
    { timestamp_seconds: 0, speaker_id: 'speaker-narrator', text: 'Hola María. Aquí va tu resumen de esta semana en Caja Los Andes.' },
    { timestamp_seconds: 5, speaker_id: 'speaker-narrator', text: 'Te aprobamos tu Crédito Consolidación de Deuda por cuatro millones quinientos mil pesos.' },
    { timestamp_seconds: 11, speaker_id: 'speaker-narrator', text: 'Cuota mensual: ciento cuarenta y dos mil trescientos. Plazo: treinta y seis meses. Primer pago: quince de mayo.' },
    { timestamp_seconds: 18, speaker_id: 'speaker-narrator', text: 'Iniciamos también la solicitud del Bono Bodas de Oro para tus padres. El pago se haría el treinta de agosto.' },
    { timestamp_seconds: 24, speaker_id: 'speaker-narrator', text: 'Y te dejamos apartado el cupo en Pucón para mayo. Que tengas linda semana.' },
  ],
  sources: [
    { id: 'src-001', title: 'Solicitud SOL-2026-04-1182937', url: 'https://miportal.cajalosandes.cl/solicitudes/SOL-2026-04-1182937', type: 'web' },
    { id: 'src-002', title: 'Trámite Bono Bodas de Oro #BBO-9821', url: 'https://miportal.cajalosandes.cl/beneficios/BBO-9821', type: 'web' },
    { id: 'src-003', title: 'Reserva turismo Pucón #TUR-44512', url: 'https://miportal.cajalosandes.cl/turismo/TUR-44512', type: 'web' },
  ],
  cta_after_play: { label: 'Compartir por WhatsApp', destino: 'whatsapp://send?text=' },
  shareable: true,
  share_text: 'Mira mi resumen Caja Los Andes 👆 — me aprobaron el crédito y el bono de mi mamá ❤️',
};

/* ─────────────────────────────────────────────────────────────────────────── */
/* === Episodio 2 — Podcast 2 voces sobre consolidación de deuda ==========  */
/* ─────────────────────────────────────────────────────────────────────────── */

export const EPISODE_PODCAST_CONSOLIDACION: AndesTVEpisode = {
  id: 'andestv-002',
  title: 'Cómo aprovechar tu Crédito Consolidación de Deuda',
  subtitle: 'Conversación con Tomás · 6 min 12 s · Audio Podcast',
  format: 'audio_podcast',
  duration_seconds: 372,
  generated_at: '2026-04-20T10:32:11-04:00',
  generation_model: 'NotebookLM Audio Overview (Gemini 3 + Chirp 3 HD)',
  language: 'es-CL',
  audience: 'general',
  thumbnail_url: '/mocks/img/andestv-podcast-consolidacion.jpg',
  audio_url: '/mocks/audio/andestv-podcast-consolidacion.mp3',
  speakers: [VOICE_AOEDE, VOICE_CHARON],
  transcript: [
    { timestamp_seconds: 0, speaker_id: 'speaker-aoede', text: 'Hola, bienvenidos a AndesTV. Hoy estamos con Tomás, asesor financiero de Caja Los Andes. Tomás, hablemos de algo que mucha gente no sabe que existe: el Crédito Consolidación de Deuda.' },
    { timestamp_seconds: 12, speaker_id: 'speaker-charon', text: 'Hola Catalina, encantado. Mira, este producto es básicamente lo siguiente: si tienes varias deudas en distintos lugares — un banco por acá, una tarjeta por allá, un crédito en otra caja — las juntas en una sola cuota acá.' },
    { timestamp_seconds: 28, speaker_id: 'speaker-aoede', text: '¿Y por qué me convendría hacer eso?' },
    { timestamp_seconds: 32, speaker_id: 'speaker-charon', text: 'Por dos razones principales. Una: bajas la tasa promedio. La gente no se da cuenta, pero las tarjetas de retail pueden estar al 41%, mientras nuestra tasa preferente es 18,9%. Y dos: ordenas tu vida financiera. Una sola cuota, una sola fecha, descontada por planilla.' },
    { timestamp_seconds: 52, speaker_id: 'speaker-aoede', text: 'Y eso del REDEC que está sonando harto, ¿qué tiene que ver?' },
    { timestamp_seconds: 58, speaker_id: 'speaker-charon', text: 'Buena pregunta. REDEC es el Registro de Deuda Consolidada, está en la Ley 21.680. Antes nosotros no podíamos saber cuántas deudas tenías en otros lados — adivinábamos. Ahora, con tu consentimiento, vemos el mapa completo y simulamos mucho mejor.' },
    { timestamp_seconds: 78, speaker_id: 'speaker-aoede', text: 'O sea, ¿les das permiso a la Caja para mirar?' },
    { timestamp_seconds: 82, speaker_id: 'speaker-charon', text: 'Exacto. Es opt-in, expreso, y se firma una sola vez en Mi Portal. Después podemos consultar cuando lo necesites para una solicitud.' },
    { timestamp_seconds: 95, speaker_id: 'speaker-aoede', text: 'Tomás, dame un ejemplo concreto.' },
    { timestamp_seconds: 99, speaker_id: 'speaker-charon', text: 'Te doy uno típico. María, pensionada, tiene un crédito BancoEstado al 27,4%, una tarjeta Falabella al 41,2%, y un crédito nuestro al 21,4%. Suma cuatro y medio millones, paga cuota total $225.000 al mes. Consolidando con nosotros: una sola cuota de $142.000, ahorro de $83.000 al mes y dos millones de pesos en intereses durante la vida del crédito.' },
    { timestamp_seconds: 132, speaker_id: 'speaker-aoede', text: 'Wow. ¿Y cuál es la letra chica?' },
    { timestamp_seconds: 136, speaker_id: 'speaker-charon', text: 'Que extiendes el plazo. Si la deuda original terminaba en 26 meses, ahora termina en 36. Pero ojo: muchas veces ya tenías plazos peores. Y siempre podés adelantar cuotas sin costo.' },
    { timestamp_seconds: 156, speaker_id: 'speaker-aoede', text: 'Tomás, en una frase: ¿quién NO debería consolidar?' },
    { timestamp_seconds: 162, speaker_id: 'speaker-charon', text: 'Quien tiene una sola deuda chica que va a terminar en pocos meses. Para todo lo demás, vale la pena al menos simular.' },
    { timestamp_seconds: 174, speaker_id: 'speaker-aoede', text: 'Eso, gente. Si quieren simular, vayan a cajalosandes.cl, sección Créditos. Tomás, gracias.' },
    { timestamp_seconds: 184, speaker_id: 'speaker-charon', text: 'A ti, Catalina. Y recuerden: ordenar tus deudas es ordenar tu cabeza.' },
  ],
  sources: [
    { id: 'src-101', title: 'Crédito Consolidación de Deuda — Ficha producto', url: 'https://www.cajalosandes.cl/creditos/credito-consolidacion-deuda', type: 'web' },
    { id: 'src-102', title: 'Ley 21.680 — REDEC', url: 'https://www.bcn.cl/leychile/navegar?idNorma=1212014', type: 'reglamento' },
    { id: 'src-103', title: 'Memoria Cajas de Chile 2024 — sección Caja Los Andes', url: 'https://www.cajasdechile.cl/wp-content/uploads/2025/04/Memoria-Cajas-de-Chile-2024.pdf', type: 'pdf', pages_or_section: 'pp. 30-32' },
  ],
  cta_after_play: { label: 'Simular mi consolidación', destino: '/creditos/consolidacion/simular' },
  shareable: true,
  share_text: 'Buenísimo este podcast sobre consolidar deudas en Caja Los Andes 🎧',
};

/* ─────────────────────────────────────────────────────────────────────────── */
/* === Episodio 3 — Cinematic short "Bono Bodas de Oro" ===================  */
/* ─────────────────────────────────────────────────────────────────────────── */

export const EPISODE_BONO_BODAS_ORO_SHORT: AndesTVEpisode = {
  id: 'andestv-003',
  title: 'Bono Bodas de Oro — Lo que tu familia debe saber',
  subtitle: '45 segundos · Cinematic Short',
  format: 'video_short',
  duration_seconds: 45,
  generated_at: '2026-04-20T10:33:02-04:00',
  generation_model: 'NotebookLM Cinematic (Gemini 3 + Nano Banana Pro + Veo 3.1)',
  language: 'es-CL',
  audience: 'general',
  thumbnail_url: '/mocks/img/andestv-bodas-oro-thumb.jpg',
  video_url: '/mocks/video/andestv-bodas-oro.mp4',
  speakers: [VOICE_NARRATOR],
  transcript: [
    { timestamp_seconds: 0, speaker_id: 'speaker-narrator', text: '¿Tus padres o abuelos cumplen cincuenta años de matrimonio?' },
    { timestamp_seconds: 4, speaker_id: 'speaker-narrator', text: 'El Estado de Chile entrega un Bono Bodas de Oro de trescientos mil pesos.' },
    { timestamp_seconds: 11, speaker_id: 'speaker-narrator', text: 'Es un bono único, no imponible y no tributable, creado por la Ley veinte mil quinientos noventa y cinco.' },
    { timestamp_seconds: 21, speaker_id: 'speaker-narrator', text: 'Para recibirlo, deben estar en el ochenta por ciento más vulnerable según el Registro Social de Hogares.' },
    { timestamp_seconds: 30, speaker_id: 'speaker-narrator', text: 'Caja Los Andes tramita el beneficio gratis en menos de treinta días.' },
    { timestamp_seconds: 38, speaker_id: 'speaker-narrator', text: 'Empieza el trámite en cajalosandes.cl o pregunta a Andesia.' },
  ],
  sources: [
    { id: 'src-201', title: 'Ley 20.595 — Bono Bodas de Oro', url: 'https://www.bcn.cl/leychile/navegar?idNorma=1040112', type: 'reglamento' },
    { id: 'src-202', title: 'IPS — Bono Bodas de Oro', url: 'https://www.chileatiende.gob.cl/fichas/41488-bono-bodas-de-oro', type: 'web' },
    { id: 'src-203', title: 'Registro Social de Hogares', url: 'https://www.registrosocial.gob.cl', type: 'web' },
  ],
  cta_after_play: { label: 'Iniciar trámite', destino: '/beneficios/bono-bodas-de-oro' },
  shareable: true,
  share_text: '¿Sabías que tus papás pueden recibir $300.000 si llevan 50 años casados? 💍',
};

export const ALL_ANDESTV_EPISODES = [
  EPISODE_RESUMEN_SEMANAL_MARIA,
  EPISODE_PODCAST_CONSOLIDACION,
  EPISODE_BONO_BODAS_ORO_SHORT,
];
