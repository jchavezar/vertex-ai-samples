/* =============================================================================
 * mocks/phishingDetector.ts — Detector de phishing
 *
 * 4 mensajes reales chilenos típicos (WhatsApp + SMS + email) con clasificación:
 *   verdict (PHISHING / SOSPECHOSO / SEGURO)
 *   confidence %
 *   red flags detectados
 *   recommended action
 *
 * Basado en patrones reales reportados a Caja Los Andes vía contact center
 * (referencias en research doc D.1) + casos públicos del CSIRT Gobierno.
 *
 * URLs falsas inspiradas en patrones reales reportados a CSIRT-CL en 2025-2026:
 *   - typosquatting de subdominios (cajalosandes.cl-pagos.online)
 *   - URLs largas con parámetros oscurecedores
 *   - dominios .top, .xyz, .online de bajo costo
 *   - HTTPS válido pero certificado emitido hace <30 días
 * ============================================================================= */

export type PhishingVerdict = 'PHISHING' | 'SOSPECHOSO' | 'SEGURO';
export type PhishingChannel = 'whatsapp' | 'sms' | 'email' | 'llamada' | 'redes_sociales';

export interface RedFlag {
  type:
    | 'url_typosquatting'
    | 'sentido_urgencia'
    | 'amenaza'
    | 'remitente_no_oficial'
    | 'pide_credenciales'
    | 'pide_clave_dinamica'
    | 'enlace_acortado'
    | 'gramatica_sospechosa'
    | 'monto_demasiado_alto'
    | 'certificado_reciente'
    | 'subdomain_disfrazado'
    | 'pide_descarga_apk'
    | 'pide_transferencia_inmediata';
  description: string;
  severity: 'baja' | 'media' | 'alta' | 'critica';
}

export interface PhishingAnalysis {
  id: string;
  channel: PhishingChannel;
  received_at: string;
  raw_message: string;
  sender_visible: string;
  sender_real?: string;
  links_detected: { url: string; expanded_url?: string; is_safe: boolean; reputation_score: number }[];
  verdict: PhishingVerdict;
  confidence_pct: number;
  red_flags: RedFlag[];
  recommended_action: string;
  educational_note: string;
  cita_oficial: { fuente: string; url: string };
}

/* ─────────────────────────────────────────────────────────────────────────── */

export const PHISHING_CASES: PhishingAnalysis[] = [
  /* === CASO 1 — WhatsApp PHISHING === */
  {
    id: 'phish-001',
    channel: 'whatsapp',
    received_at: '2026-04-19T11:42:00-04:00',
    raw_message:
      '🚨 Caja Los Andes 🚨\nEstimado afiliado, su crédito social fue PRE-APROBADO por $4.500.000.\n\nPara recibir el dinero HOY, ingrese aquí y valide su cédula:\nhttps://cajalosandes.cl-pagos.online/aprob/?ref=4521\n\nVálido solo por las próximas 2 horas. ⏰',
    sender_visible: '+56 9 8821 4598 (sin verificación WhatsApp Business)',
    sender_real: 'Número de prepago Movistar — sin asociación con CCLA',
    links_detected: [
      {
        url: 'https://cajalosandes.cl-pagos.online/aprob/?ref=4521',
        is_safe: false,
        reputation_score: 0.04,
      },
    ],
    verdict: 'PHISHING',
    confidence_pct: 99,
    red_flags: [
      {
        type: 'url_typosquatting',
        description:
          'El dominio "cajalosandes.cl-pagos.online" NO es de Caja Los Andes. El dominio real termina en ".cl" (ej: cajalosandes.cl o miportal.cajalosandes.cl). Aquí "cl" es solo parte del nombre y el dominio real es "cl-pagos.online".',
        severity: 'critica',
      },
      {
        type: 'sentido_urgencia',
        description: 'Urgencia artificial: "HOY", "próximas 2 horas". Caja Los Andes nunca presiona para tomar decisiones financieras.',
        severity: 'alta',
      },
      {
        type: 'pide_credenciales',
        description: 'Solicita validar cédula vía un formulario web no oficial.',
        severity: 'critica',
      },
      {
        type: 'remitente_no_oficial',
        description: 'WhatsApp sin tilde de verificación Business. CCLA no envía pre-aprobaciones por WhatsApp sin afiliación previa al canal.',
        severity: 'alta',
      },
      {
        type: 'monto_demasiado_alto',
        description: 'Monto $4.500.000 sin evaluación previa. Las pre-aprobaciones requieren al menos consulta REDEC con consentimiento.',
        severity: 'media',
      },
    ],
    recommended_action:
      'NO hacer clic en el enlace. NO responder. Reportar al CSIRT-CL en csirt.gob.cl/reportar y bloquear el número. Si tienes dudas reales sobre tus créditos, ingresa siempre desde miportal.cajalosandes.cl o llama al 600 510 0000.',
    educational_note:
      'Las URLs oficiales de Caja Los Andes terminan en cajalosandes.cl o tapp.cl. Cualquier dominio extra (.online, .top, -pagos, -tramites) es siempre falso.',
    cita_oficial: {
      fuente: 'CSIRT Gobierno de Chile — Recomendaciones contra phishing financiero',
      url: 'https://www.csirt.gob.cl/recomendaciones',
    },
  },
  /* === CASO 2 — SMS SOSPECHOSO (genérico, podría ser legítimo o no) === */
  {
    id: 'phish-002',
    channel: 'sms',
    received_at: '2026-04-18T16:09:11-04:00',
    raw_message:
      'CCLA: Tu cuota de Crédito Social vence el 25-04. Paga en linea: bit.ly/clapagos26',
    sender_visible: 'CCLA-INFO',
    sender_real: 'SMS-Mass — agregador no certificado',
    links_detected: [
      {
        url: 'https://bit.ly/clapagos26',
        expanded_url: 'https://www.cajalosandes.cl/pagos?utm=sms',
        is_safe: true,
        reputation_score: 0.78,
      },
    ],
    verdict: 'SOSPECHOSO',
    confidence_pct: 64,
    red_flags: [
      {
        type: 'enlace_acortado',
        description:
          'El link es bit.ly — acortador de terceros que oculta el destino. Aunque al expandirse va al dominio real, CCLA en sus comunicaciones oficiales no usa bit.ly.',
        severity: 'media',
      },
      {
        type: 'remitente_no_oficial',
        description: 'Sender ID "CCLA-INFO" no figura en la lista de remitentes oficiales registrados (la lista oficial es CAJALOSANDES y MIPORTAL).',
        severity: 'media',
      },
      {
        type: 'sentido_urgencia',
        description: 'Insiste en fecha de vencimiento — patrón aceptable pero abusable. Verifica directamente en Mi Portal.',
        severity: 'baja',
      },
    ],
    recommended_action:
      'Verifica el monto y vencimiento directamente en miportal.cajalosandes.cl o app oficial. Si el dato coincide, paga desde la app. NO uses el enlace SMS.',
    educational_note:
      'Caja Los Andes envía SMS con sender ID "CAJALOSANDES" y siempre con URLs cortas internas (cla.cl/...) o a dominios oficiales completos. Nunca con bit.ly o tinyurl.',
    cita_oficial: {
      fuente: 'CCLA — Centro de ayuda · Comunicaciones oficiales',
      url: 'https://www.cajalosandes.cl/centro-de-ayuda/comunicaciones',
    },
  },
  /* === CASO 3 — EMAIL PHISHING === */
  {
    id: 'phish-003',
    channel: 'email',
    received_at: '2026-04-17T09:14:52-04:00',
    raw_message:
      'Asunto: ⚠️ Suspensión de su Asignación Familiar — Acción requerida\n\nEstimado(a) Sr./Sra.,\n\nDetectamos inconsistencias en su declaración de cargas familiares. Su Asignación Familiar quedará SUSPENDIDA en 48 horas si no actualiza sus datos.\n\nValide su información aquí:\nhttp://cajalosandes-suseso-validacion.top/login.php?u=usuario\n\nDeberá ingresar su clave única, fecha nacimiento, número de tarjeta para verificación.\n\nAtentamente,\nDepartamento de Asignación Familiar\nCaja Los Andes',
    sender_visible: 'asignacion@cajalosandes-suseso.com',
    sender_real:
      'Servidor SMTP en Lituania — sin SPF/DKIM válido para cajalosandes.cl',
    links_detected: [
      {
        url: 'http://cajalosandes-suseso-validacion.top/login.php?u=usuario',
        is_safe: false,
        reputation_score: 0.02,
      },
    ],
    verdict: 'PHISHING',
    confidence_pct: 99,
    red_flags: [
      {
        type: 'url_typosquatting',
        description: 'Dominio .top que combina "cajalosandes" + "suseso" + "validacion". Ningún subdominio oficial usa esa combinación.',
        severity: 'critica',
      },
      {
        type: 'pide_credenciales',
        description: 'Pide Clave Única (que es del Estado, NUNCA debe entregarse a privados), fecha nacimiento Y número de tarjeta. Ningún proceso real solicita esto junto.',
        severity: 'critica',
      },
      {
        type: 'amenaza',
        description: 'Amenaza con suspensión de Asignación Familiar — manipulación emocional clásica.',
        severity: 'alta',
      },
      {
        type: 'remitente_no_oficial',
        description: 'Email pretende ser de Caja Los Andes y SUSESO simultáneamente — son dos entidades distintas. CCLA jamás se firma con dominio @cajalosandes-suseso.com.',
        severity: 'critica',
      },
      {
        type: 'gramatica_sospechosa',
        description: 'Mezcla formal/informal, "Sr./Sra." sin nombre real, traducción imperfecta.',
        severity: 'media',
      },
    ],
    recommended_action:
      'NO hacer clic. NO responder. Reportar el correo a phishing@cajalosandes.cl y al CSIRT-CL. La actualización de tramos de Asignación Familiar se hace en MIPORTAL o en SUSESO directamente — nunca por correo.',
    educational_note:
      'Las trámites de Asignación Familiar en CCLA se gestionan en miportal.cajalosandes.cl o presencialmente. SUSESO es regulador público y NO comparte canales de notificación con CCLA.',
    cita_oficial: {
      fuente: 'SUSESO — Cómo actualizar tramos de Asignación Familiar',
      url: 'https://www.suseso.cl/612/w3-propertyvalue-141051.html',
    },
  },
  /* === CASO 4 — WhatsApp SEGURO (ejemplo legítimo para contraste) === */
  {
    id: 'phish-004',
    channel: 'whatsapp',
    received_at: '2026-04-20T08:30:00-04:00',
    raw_message:
      'Caja Los Andes ✓ Hola María, te confirmamos que tu solicitud SOL-2026-04-1182937 fue aprobada. El desembolso a tus acreedores se realizará el 23-04. Puedes ver el detalle en https://miportal.cajalosandes.cl/solicitudes/SOL-2026-04-1182937 — Equipo Andesia',
    sender_visible: 'Caja Los Andes Oficial · WhatsApp Business ✓',
    sender_real: 'WhatsApp Business API verificado — owner: Caja Compensación Los Andes RUT 81.826.800-9',
    links_detected: [
      {
        url: 'https://miportal.cajalosandes.cl/solicitudes/SOL-2026-04-1182937',
        is_safe: true,
        reputation_score: 0.99,
      },
    ],
    verdict: 'SEGURO',
    confidence_pct: 96,
    red_flags: [],
    recommended_action: 'Mensaje válido. Puedes ingresar a Mi Portal para revisar el estado de la solicitud.',
    educational_note:
      'Comunicación oficial CCLA por WhatsApp Business: aparece check verde de verificación (✓), incluye número de solicitud trazable, link a dominio oficial miportal.cajalosandes.cl y firma "Equipo Andesia" reconocible.',
    cita_oficial: {
      fuente: 'WhatsApp — Cómo identificar cuentas Business verificadas',
      url: 'https://faq.whatsapp.com/general/security-and-privacy/about-business-account-verification',
    },
  },
];

export function getPhishingCaseById(id: string): PhishingAnalysis | undefined {
  return PHISHING_CASES.find((p) => p.id === id);
}

export function getPhishingByChannel(channel: PhishingChannel): PhishingAnalysis[] {
  return PHISHING_CASES.filter((p) => p.channel === channel);
}
