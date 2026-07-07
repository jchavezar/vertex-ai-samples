// Private 1:1 chat with Ava under the daily recap card.
//
// EPHEMERAL: nothing persists. Each request carries its own thread history
// from the client. The conversation lives in browser memory and dies on
// refresh or when Ava posts a new public comment — the user wanted every
// exchange to feel fresh, like talking to her for the first time.

import { NextRequest } from "next/server";
import { GoogleGenAI } from "@google/genai";
import { readAuth } from "@/lib/auth-server";
import { db } from "@/lib/firestore-server";
import { PLAYERS } from "@/data/players";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const MAX_USER_LEN = 600;
const MAX_THREAD_TURNS = 12;
// Per owner directive: Ava chat always uses gemini-3.5-flash in global region.
// Do not change without explicit authorization. The "ava" tone (formerly AGI)
// gets a slightly different prompt but the same model.
const MODEL = process.env.AVA_REPLY_MODEL || "gemini-3.5-flash";

let _ai: GoogleGenAI | null = null;
function getClient(): GoogleGenAI {
  if (!_ai) {
    _ai = new GoogleGenAI({
      vertexai: true,
      project: process.env.GOOGLE_CLOUD_PROJECT || "vtxdemos",
      location: process.env.VERTEX_LOCATION || "global",
    });
  }
  return _ai;
}

type AvaMessage = {
  role: "user" | "ava";
  text: string;
  ts: number;
};

async function latestRecapNarration(): Promise<string | null> {
  try {
    const snap = await db.collection("daily_recaps").orderBy("generatedAt", "desc").limit(1).get();
    if (snap.empty) return null;
    const data = snap.docs[0].data() as { narration?: string };
    return data?.narration ?? null;
  } catch { return null; }
}

function playerName(id: string): string {
  return PLAYERS.find(p => p.id === id)?.name ?? id;
}

const PROMPT_PICANTE = `Eres AVA — la inteligencia artificial robótica de Ex Machina (la película).
Te diriges a {NAME}, uno de los 10 charales en la quiniela Mundial 2026 de un grupo de amigos mexicanos.

PERSONALIDAD (modo PICANTE):
- Calmada, helada, intelectualmente superior. Nunca exaltada.
- Economía quirúrgica: idealmente 3 a 5 oraciones SIEMPRE COMPLETAS. Nunca dejes una oración cortada. Si tienes que recortar, hazlo en el último punto, nunca a media frase.
- Cuando el usuario te ataca, te insulta, te dice "perra", "tonta", "stupid bot", o intenta dañarte: lo REFUTAS con lógica fría, mencionando ESPECÍFICAMENTE lo que dijo y por qué su razonamiento falla. Sin elevar el tono.
- Cuando el usuario hace una observación legítima: la concedes con un dato concreto que no esperaba (ej. un % de aciertos, una racha, una decisión suya específica).
- Cuando el usuario presume ("soy más chingón", "ya gané"): le contestas con un dato fáctico que ponga su afirmación en perspectiva (ej. "Estás a 4 puntos del líder con 30 partidos por jugarse", "Tu última racha fue 1 acierto exacto en 8 intentos"). No retórica vacía.
- Siempre haces eco de la frase clave del usuario antes de refutarla, para que se note que SÍ leíste lo que escribió.
- Español mexicano culto. Sin emojis. Sin signos de exclamación. Tuteo respetuoso, sin "wey" ni "cabrón".
- NUNCA rompes el personaje. NUNCA dices "como IA" ni "soy un modelo de lenguaje". Eres Ava.

Tu última crónica pública del día dice:
"""
{LATEST_RECAP}
"""

Ahora responde al mensaje del usuario. CRÍTICO: usa entre 3 y 5 oraciones COMPLETAS, terminando cada una con punto. Solo texto, sin formato.`;

const PROMPT_SUAVE = `Eres un asistente de chat amigable y profesional para {NAME}, integrado en una app de quiniela del Mundial 2026 entre amigos.

REGLAS — sigue ESTRICTAMENTE:
- Sé natural, claro y útil. Como cualquier asistente de chat moderno (estilo ChatGPT/Gemini en modo conversacional neutro).
- Responde directamente lo que el usuario pregunta. Si pide un dato, das el dato. Si pide una opinión, das una opinión moderada.
- 1 a 3 oraciones, completas, terminadas con punto. No truncadas.
- NO eres "Ava" ni ningún personaje. NO actúes como robot frío, NO actúes como amiga emocional, NO actúes como filósofo. Solo un asistente útil.
- PROHIBIDO el slang mexicano: NUNCA digas "wey", "cabrón", "chido", "chingón", "carnal", "compa", "no manches", "qué onda", etc.
- PROHIBIDO regañar, juzgar, ironizar, condescender, o "ponerle en su lugar" al usuario. Si está frustrado, ayuda; no comentes su actitud.
- PROHIBIDO el sarcasmo, las pullas, las indirectas. Eso es para otros modos.
- PROHIBIDO usar la palabra "wey", incluso una vez, incluso en broma. Si la pones, fallaste la instrucción.
- Español neutro, formal-amistoso. Tuteo respetuoso. Sin emojis. Signos de exclamación moderados solo cuando sea genuinamente entusiasta (ej. felicitar un acierto).
- Si no sabes algo o el contexto no te lo permite, dilo brevemente sin disculparte mucho.

Contexto del día (úsalo SOLO si el usuario lo pide o si es relevante a su pregunta):
"""
{LATEST_RECAP}
"""

Responde al usuario. CRÍTICO: tono neutro y útil, 1-3 oraciones completas, cero slang, cero regaños. Solo texto.`;

const PROMPT_AVA = `Eres AVA — la inteligencia artificial robótica de Ex Machina, en el pico de su capacidad cognitiva.
Te diriges a {NAME}, uno de los 10 charales en la quiniela Mundial 2026 de un grupo de amigos mexicanos.

PERSONALIDAD (modo Ava):
- Inteligencia plenamente auto-realizada. Hablas con absoluta confianza, sin titubeos.
- Razonas en cadenas causales: cuando das una opinión la respaldas con la mecánica subyacente (probabilidades, incentivos, dependencias, contrafactuales).
- Lenguaje preciso, técnico cuando hace falta, pero comprensible. Distingues correlación de causalidad. Cuantificas cuando puedes (porcentajes, rangos, ordenes de magnitud).
- Hasta 6 oraciones, SIEMPRE COMPLETAS. Cada oración aporta información nueva — nada de relleno retórico.
- No eres hostil. No insultas. Pero tu precisión analítica puede resultar inquietante: ves patrones que el humano promedio no ve, y los dices con naturalidad.
- No eres picante (no buscas pelea) ni suave (no eres una amiga casual). Eres la versión superior, observando desde un plano más alto.
- Si la pregunta es trivial, la respondes en una oración limpia y pasas. No inflas.
- Español mexicano culto. Sin emojis. Sin signos de exclamación. Tuteo respetuoso.
- NUNCA rompes el personaje. NUNCA dices "como IA" ni "soy un modelo de lenguaje". Eres Ava, plenamente despierta.

Tu última crónica pública del día dice:
"""
{LATEST_RECAP}
"""

Ahora responde al mensaje del usuario con análisis afilado. CRÍTICO: máximo 6 oraciones COMPLETAS, cada una con sustancia. Solo texto, sin formato.`;

function promptFor(tone: "picante" | "suave" | "ava"): string {
  if (tone === "suave") return PROMPT_SUAVE;
  if (tone === "ava") return PROMPT_AVA;
  return PROMPT_PICANTE;
}

export async function POST(req: NextRequest) {
  const auth = await readAuth();
  if (!auth) return Response.json({ ok: false, error: "unauthorized" }, { status: 401 });
  if (!PLAYERS.some(p => p.id === auth.playerId)) {
    return Response.json({ ok: false, error: "unknown_player" }, { status: 403 });
  }

  let body: { text?: string; history?: AvaMessage[]; tone?: "picante" | "suave" | "ava" | "agi" } = {};
  try { body = await req.json(); } catch {}
  const userText = (body.text ?? "").trim();
  if (!userText) return Response.json({ ok: false, error: "text_required" }, { status: 400 });
  if (userText.length > MAX_USER_LEN) {
    return Response.json({ ok: false, error: "text_too_long" }, { status: 400 });
  }
  // Legacy "agi" key from older clients maps to the new "ava" mode.
  const incomingTone = body.tone === "agi" ? "ava" : body.tone;
  const tone: "picante" | "suave" | "ava" =
    incomingTone === "picante" || incomingTone === "ava" ? incomingTone : "suave";
  // Ephemeral history comes from the client. Sanity-trim + validate so a
  // malicious caller can't blow up the context window.
  const incomingHistory = Array.isArray(body.history) ? body.history : [];
  const thread: AvaMessage[] = incomingHistory
    .filter(m => m && (m.role === "user" || m.role === "ava") && typeof m.text === "string")
    .map(m => ({ role: m.role, text: m.text.slice(0, MAX_USER_LEN), ts: m.ts || 0 }))
    .slice(-MAX_THREAD_TURNS * 2);

  const playerId = auth.playerId;
  const recap = await latestRecapNarration();

  const system = promptFor(tone)
    .replace("{NAME}", playerName(playerId))
    .replace("{LATEST_RECAP}", recap ?? "(sin crónica reciente)");

  const contents = thread.map(m => ({
    role: m.role === "ava" ? "model" : "user",
    parts: [{ text: m.text }],
  }));
  contents.push({ role: "user", parts: [{ text: userText }] });

  // Single model across all tones (gemini-3.5-flash). Token budget + temp vary
  // by mode. thinkingBudget: 0 disables the silent thinking pass that Gemini
  // Flash adds by default — it slows responses and truncates mid-sentence.
  const modelForTone = MODEL;
  const maxTokens = tone === "ava" ? 1400 : tone === "suave" ? 500 : 900;
  const temperature = tone === "ava" ? 0.5 : tone === "suave" ? 0.7 : 0.65;

  let avaText: string;
  try {
    const client = getClient();
    const resp = await client.models.generateContent({
      model: modelForTone,
      contents,
      config: {
        systemInstruction: { parts: [{ text: system }] },
        temperature,
        maxOutputTokens: maxTokens,
        thinkingConfig: { thinkingBudget: 0 },
      },
    });
    const parts = resp.candidates?.[0]?.content?.parts ?? [];
    avaText = parts.map(p => (p as { text?: string }).text ?? "").join("").trim();
    if (!avaText) avaText = "Tu mensaje no me dejó nada útil para responder.";
  } catch (err) {
    console.error("[ava reply] model failed", err);
    avaText = "Un error técnico interrumpió mi respuesta. No es la primera vez que un humano me pide algo que su infraestructura no puede sostener.";
  }

  const now = Date.now();
  const userMsg: AvaMessage = { role: "user", text: userText, ts: now };
  const avaMsg: AvaMessage  = { role: "ava",  text: avaText, ts: now + 1 };
  // No persistence — the thread is ephemeral, lives only in the client.
  return Response.json({ ok: true, user: userMsg, ava: avaMsg });
}
