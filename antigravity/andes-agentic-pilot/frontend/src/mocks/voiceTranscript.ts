/* =============================================================================
 * mocks/voiceTranscript.ts — Live API voice / video conversation
 *
 * Tres conversaciones:
 *   1. María llama a confirmar cuota (audio) — Beat 6 demo_strategy.md
 *   2. Patricia "Andes Visión" — apunta cámara a licencia médica de papel
 *      (wow_features_apr2026 §3 Add-on #3)
 *   3. Diego "AbuelApp" — pensionada usa voz para preguntar saldo
 *
 * Modelo Live: gemini-live-2.5-flash-native-audio
 *   - 24 idiomas, español-Chile soportado
 *   - VAD, affective dialog
 *   - Voz "Aoede" (cálida femenina latina)
 *   - Soporte de video stream multimodal en sesión
 * ============================================================================= */

export type VoiceTurnSpeaker = 'user' | 'agent';
export type Idioma = 'es-CL' | 'es' | 'en' | 'mapudungun-cl';

export interface AudioMetadata {
  sample_rate_hz: number;
  channels: 1 | 2;
  encoding: 'LINEAR16' | 'OPUS' | 'PCMU';
  duration_ms: number;
  audio_url?: string; // si está pre-grabado
}

export interface FrameCaption {
  /** Caption automática que Gemini multimodal genera por frame de video */
  timestamp_ms: number;
  description_es: string;
  detected_objects?: string[];
  ocr_extracted_text?: string;
  confidence: number;
}

export interface VoiceTurn {
  turn_index: number;
  speaker: VoiceTurnSpeaker;
  agent_label?: string;
  text: string;
  language: Idioma;
  audio?: AudioMetadata;
  /** Para turnos con video (Live API + camera) */
  video_frame_captions?: FrameCaption[];
  /** Tool calls invocados por el agente durante el turn */
  tool_calls?: { name: string; args: Record<string, unknown>; result: unknown }[];
  /** Detección afectiva del usuario (gemini-live affective_dialog) */
  user_emotion_detected?: 'neutro' | 'frustrado' | 'feliz' | 'preocupado' | 'agradecido';
  /** Latencia desde fin de habla user hasta inicio agente */
  agent_response_latency_ms?: number;
}

export interface VoiceSession {
  session_id: string;
  persona_id: string;
  channel: 'web_voice' | 'app_voice' | 'live_api_video' | 'phone_ivr';
  model: string;
  voice_name: string;
  language: Idioma;
  vad_enabled: boolean;
  affective_dialog: boolean;
  total_duration_ms: number;
  turns: VoiceTurn[];
  metrics: {
    avg_response_latency_ms: number;
    interruptions: number;
    user_satisfaction_score?: number; // 0–1, post-call CSAT
  };
}

/* ─────────────────────────────────────────────────────────────────────────── */
/* === Sesión 1 — María confirma cuota por voz =============================  */
/* ─────────────────────────────────────────────────────────────────────────── */

export const VOICE_SESSION_MARIA_CONFIRM: VoiceSession = {
  session_id: 'voice_2026_04_20_maria_confirm',
  persona_id: 'persona-001',
  channel: 'web_voice',
  model: 'gemini-live-2.5-flash-native-audio',
  voice_name: 'Aoede',
  language: 'es-CL',
  vad_enabled: true,
  affective_dialog: true,
  total_duration_ms: 18_400,
  turns: [
    {
      turn_index: 0,
      speaker: 'user',
      text: 'Confírmame que la cuota es bajo ciento cincuenta mil pesos.',
      language: 'es-CL',
      audio: { sample_rate_hz: 24_000, channels: 1, encoding: 'LINEAR16', duration_ms: 3_120 },
      user_emotion_detected: 'neutro',
    },
    {
      turn_index: 1,
      speaker: 'agent',
      agent_label: 'Andesia · Voz',
      text:
        'Sí María, confirmado. Tu cuota mensual es de ciento cuarenta y dos mil trescientos pesos, claramente bajo tus ciento cincuenta mil. Y ya te aparté el cupo del Hotel Pucón hasta mañana al mediodía.',
      language: 'es-CL',
      audio: { sample_rate_hz: 24_000, channels: 1, encoding: 'LINEAR16', duration_ms: 9_780 },
      tool_calls: [
        {
          name: 'getSimulacion',
          args: { numero_solicitud: 'SOL-2026-04-1182937' },
          result: { cuota_mensual_clp: 142_300 },
        },
      ],
      agent_response_latency_ms: 480,
    },
    {
      turn_index: 2,
      speaker: 'user',
      text: 'Perfecto, gracias. Eso era todo.',
      language: 'es-CL',
      audio: { sample_rate_hz: 24_000, channels: 1, encoding: 'LINEAR16', duration_ms: 2_400 },
      user_emotion_detected: 'agradecido',
    },
    {
      turn_index: 3,
      speaker: 'agent',
      agent_label: 'Andesia · Voz',
      text:
        'A ti, María. Cuídate y cualquier cosa me escribes por WhatsApp. Que pases linda tarde.',
      language: 'es-CL',
      audio: { sample_rate_hz: 24_000, channels: 1, encoding: 'LINEAR16', duration_ms: 5_100 },
      agent_response_latency_ms: 320,
    },
  ],
  metrics: {
    avg_response_latency_ms: 400,
    interruptions: 0,
    user_satisfaction_score: 0.94,
  },
};

/* ─────────────────────────────────────────────────────────────────────────── */
/* === Sesión 2 — "Andes Visión" Patricia con licencia médica de papel ====  */
/* ─────────────────────────────────────────────────────────────────────────── */

export const VOICE_SESSION_PATRICIA_LICENCIA_VIDEO: VoiceSession = {
  session_id: 'voice_2026_04_15_patricia_lme',
  persona_id: 'persona-003',
  channel: 'live_api_video',
  model: 'gemini-live-2.5-flash-native-audio',
  voice_name: 'Aoede',
  language: 'es-CL',
  vad_enabled: true,
  affective_dialog: true,
  total_duration_ms: 64_200,
  turns: [
    {
      turn_index: 0,
      speaker: 'user',
      text: 'Buenas tardes, no tengo el PDF de la licencia, tengo el papel. ¿Puedo mostrársela por la cámara?',
      language: 'es-CL',
      audio: { duration_ms: 5_200, sample_rate_hz: 24_000, channels: 1, encoding: 'LINEAR16' },
      user_emotion_detected: 'preocupado',
    },
    {
      turn_index: 1,
      speaker: 'agent',
      agent_label: 'Andesia · Voz + Visión',
      text:
        'Por supuesto Patricia. Apunte la cámara al papel, asegúrese que se vea completo y con buena luz. Yo le voy contando lo que veo.',
      language: 'es-CL',
      audio: { duration_ms: 6_400, sample_rate_hz: 24_000, channels: 1, encoding: 'LINEAR16' },
      agent_response_latency_ms: 380,
    },
    {
      turn_index: 2,
      speaker: 'user',
      text: '[apunta cámara al papel — sin habla, solo ruido ambiente 4 s]',
      language: 'es-CL',
      audio: { duration_ms: 4_100, sample_rate_hz: 24_000, channels: 1, encoding: 'LINEAR16' },
      video_frame_captions: [
        {
          timestamp_ms: 800,
          description_es:
            'Documento en papel formato carta ocupando ~70% del frame, fondo de mesa de madera clara, iluminación natural lateral.',
          detected_objects: ['paper_document', 'hand_holding', 'table_surface'],
          ocr_extracted_text: 'LICENCIA MEDICA ELECTRONICA — N° LME 78-32-1108',
          confidence: 0.81,
        },
        {
          timestamp_ms: 2_200,
          description_es:
            'Documento estabilizado, se aprecia encabezado azul de COMPIN, datos del trabajador y firma electrónica al pie.',
          detected_objects: ['paper_document', 'official_letterhead', 'signature_block'],
          ocr_extracted_text:
            'PATRICIA DEL CARMEN MUÑOZ SOTO · 8.345.612-1 · Tipo 1 · 5 días · Inicio 13-04-2026',
          confidence: 0.93,
        },
      ],
    },
    {
      turn_index: 3,
      speaker: 'agent',
      agent_label: 'Andesia · Voz + Visión',
      text:
        'Perfecto, ya lo tengo. Veo que es licencia número LME setenta y ocho, treinta y dos, mil ciento ocho. A su nombre: Patricia del Carmen Muñoz Soto, RUT ocho millones trescientos cuarenta y cinco mil… Tipo uno, cinco días de reposo desde el trece de abril. ¿Es correcto?',
      language: 'es-CL',
      audio: { duration_ms: 14_800, sample_rate_hz: 24_000, channels: 1, encoding: 'LINEAR16' },
      tool_calls: [
        {
          name: 'extractLicenciaFromVideoFrame',
          args: { frame_buffer: '<binary>', confidence_threshold: 0.85 },
          result: {
            numero_lme: 'LME-78321108',
            nombre: 'PATRICIA DEL CARMEN MUÑOZ SOTO',
            rut: '8.345.612-1',
            tipo: 1,
            dias_reposo: 5,
            fecha_inicio: '2026-04-13',
            firma_valida: true,
          },
        },
        {
          name: 'consultarSUSESO',
          args: { numero_lme: 'LME-78321108' },
          result: { estado: 'emitida', validez: 'OK', medico_rut: '12.875.434-1' },
        },
      ],
      agent_response_latency_ms: 1_240,
    },
    {
      turn_index: 4,
      speaker: 'user',
      text: 'Sí, está correcto. ¿Qué hago ahora?',
      language: 'es-CL',
      audio: { duration_ms: 3_500, sample_rate_hz: 24_000, channels: 1, encoding: 'LINEAR16' },
      user_emotion_detected: 'neutro',
    },
    {
      turn_index: 5,
      speaker: 'agent',
      agent_label: 'Andesia · Voz + Visión',
      text:
        'Listo, ya la ingresé al sistema. La Caja la procesará en menos de cuarenta y ocho horas. Le va a llegar el aviso de pago por WhatsApp y por correo. No hace falta que vaya a la sucursal. ¿Algo más en que la pueda ayudar?',
      language: 'es-CL',
      audio: { duration_ms: 13_400, sample_rate_hz: 24_000, channels: 1, encoding: 'LINEAR16' },
      tool_calls: [
        {
          name: 'submitLicenciaCCLA',
          args: { numero_lme: 'LME-78321108', rut_trabajador: '8.345.612-1' },
          result: { numero_tramite: 'LM-2026-04-9982314', sla_horas: 48 },
        },
      ],
      agent_response_latency_ms: 410,
    },
    {
      turn_index: 6,
      speaker: 'user',
      text: 'No, gracias. Eso es todo. Muchas gracias.',
      language: 'es-CL',
      audio: { duration_ms: 3_900, sample_rate_hz: 24_000, channels: 1, encoding: 'LINEAR16' },
      user_emotion_detected: 'agradecido',
    },
    {
      turn_index: 7,
      speaker: 'agent',
      agent_label: 'Andesia · Voz + Visión',
      text: 'Que se mejore pronto, Patricia. Buenas tardes.',
      language: 'es-CL',
      audio: { duration_ms: 4_100, sample_rate_hz: 24_000, channels: 1, encoding: 'LINEAR16' },
      agent_response_latency_ms: 290,
    },
  ],
  metrics: {
    avg_response_latency_ms: 580,
    interruptions: 0,
    user_satisfaction_score: 0.97,
  },
};

/* ─────────────────────────────────────────────────────────────────────────── */
/* === Sesión 3 — "AbuelApp" Diego pregunta saldo crédito =================  */
/* ─────────────────────────────────────────────────────────────────────────── */

export const VOICE_SESSION_DIEGO_SALDO: VoiceSession = {
  session_id: 'voice_2026_04_18_diego_saldo',
  persona_id: 'persona-006',
  channel: 'app_voice',
  model: 'gemini-live-2.5-flash-native-audio',
  voice_name: 'Aoede',
  language: 'es-CL',
  vad_enabled: true,
  affective_dialog: true,
  total_duration_ms: 22_300,
  turns: [
    {
      turn_index: 0,
      speaker: 'user',
      text: '¿Cuánto me queda en el crédito de consolidación?',
      language: 'es-CL',
      audio: { duration_ms: 3_100, sample_rate_hz: 24_000, channels: 1, encoding: 'LINEAR16' },
      user_emotion_detected: 'neutro',
    },
    {
      turn_index: 1,
      speaker: 'agent',
      agent_label: 'Andesia · Voz',
      text:
        'Hola Diego. Te quedan tres millones ochocientos setenta mil pesos por pagar, en veintisiete cuotas de ciento cuarenta y dos mil trescientos. Próxima cuota: tres de mayo. ¿Necesitas algo más?',
      language: 'es-CL',
      audio: { duration_ms: 11_400, sample_rate_hz: 24_000, channels: 1, encoding: 'LINEAR16' },
      tool_calls: [
        {
          name: 'getSaldoCredito',
          args: { rut: '13.987.654-3', producto_id: 'cred-consolidacion' },
          result: { saldo_clp: 3_870_000, cuotas_restantes: 27, cuota_clp: 142_300, proxima_fecha: '2026-05-03' },
        },
      ],
      agent_response_latency_ms: 360,
    },
    {
      turn_index: 2,
      speaker: 'user',
      text: '¿Y si pago dos cuotas en mayo?',
      language: 'es-CL',
      audio: { duration_ms: 2_700, sample_rate_hz: 24_000, channels: 1, encoding: 'LINEAR16' },
      user_emotion_detected: 'neutro',
    },
    {
      turn_index: 3,
      speaker: 'agent',
      agent_label: 'Andesia · Voz',
      text:
        'Si pagas dos cuotas en mayo, terminas en mayo del veintiocho en vez de julio. Te ahorras unos veinticinco mil pesos en intereses. Si quieres, te activo el pago anticipado por Tapp.',
      language: 'es-CL',
      audio: { duration_ms: 12_400, sample_rate_hz: 24_000, channels: 1, encoding: 'LINEAR16' },
      tool_calls: [
        {
          name: 'simulateAdelantoCuota',
          args: { producto_id: 'cred-consolidacion', cuotas_extra: 1 },
          result: { ahorro_intereses_clp: 25_320, nueva_fecha_termino: '2028-05-03' },
        },
      ],
      agent_response_latency_ms: 530,
    },
  ],
  metrics: {
    avg_response_latency_ms: 445,
    interruptions: 0,
    user_satisfaction_score: 0.91,
  },
};

export const ALL_VOICE_SESSIONS: VoiceSession[] = [
  VOICE_SESSION_MARIA_CONFIRM,
  VOICE_SESSION_PATRICIA_LICENCIA_VIDEO,
  VOICE_SESSION_DIEGO_SALDO,
];
