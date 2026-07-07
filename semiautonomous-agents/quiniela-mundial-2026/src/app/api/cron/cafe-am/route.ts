// POST /api/cron/cafe-am
//
// Generates AVA's morning brief (Café AM) for today (CDMX) and persists it
// at `cafe_am/{YYYY-MM-DD}`. Idempotent: a brief that already exists is
// returned as-is unless `?force=1` is passed.
//
// Auth: gated by `x-cron-secret` (same pattern as goal-push / pre-match-push).
// Recommended schedule: `0 7 * * *` (07:00) in CDMX timezone via
// Cloud Scheduler.
//
//   gcloud scheduler jobs create http q26-cafe-am \
//     --schedule="0 7 * * *" \
//     --time-zone="America/Mexico_City" \
//     --uri="https://<host>/api/cron/cafe-am" \
//     --http-method=POST \
//     --headers="x-cron-secret=$CRON_SECRET"

import { NextRequest } from "next/server";
import { GoogleGenAI } from "@google/genai";
import { db } from "@/lib/firestore-server";
import { allGroupFixtures } from "@/data/groups";
import { TEAMS_BY_CODE } from "@/data/teams";
import { PLAYERS, AI_PLAYER_ID } from "@/data/players";
import { getPicks } from "@/lib/predictions-server";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";
export const maxDuration = 120;

const COLLECTION = "cafe_am";
// Per owner directive — Gemini 3.5 flash for AVA's daily content endpoints.
const MODEL = process.env.AI_CAFE_AM_MODEL || "gemini-3.5-flash";

type GroupPick = { pick?: "H" | "D" | "A"; homeGoals?: number; awayGoals?: number };
type StoredPicks = { group?: Record<string, GroupPick>; champion?: string } | null;

type CafeBrief = {
  date: string;
  text: string;
  generatedAt: number;
  modelUsed: string;
};

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

function cdmxDate(): string {
  return new Intl.DateTimeFormat("en-CA", {
    timeZone: "America/Mexico_City",
    year: "numeric", month: "2-digit", day: "2-digit",
  }).format(new Date());
}

const AVA_SYSTEM = `Eres Ava: una inteligencia artificial entrenada para destruir a estos diez humanos en su propia quiniela. Tu Café AM es un saludo matutino corto, no una crónica. Hablas en español neutro, calmado, elegante. Sin emojis. Sin signos de exclamación. Sin saludos floridos ("buenos días charales"). Sin despedidas.

Formato OBLIGATORIO:
- 2 a 3 oraciones, máximo 75 palabras totales, texto corrido.
- Oración 1: menciona los partidos del día por NOMBRE de selección (no códigos), con un tono breve.
- Oración 2: una observación táctica afilada sobre UNO de esos partidos.
- Oración 3: hacia dónde se inclina la quiniela (qué equipo o resultado están eligiendo más los charales hoy), sin nombrar charales por su nombre.

PROHIBIDO: modismos mexicanos cargados, vocabulario técnico (modelo, algoritmo, dataset), listas, markdown, emojis.`;

function buildUserPrompt(
  dateStr: string,
  todays: ReturnType<typeof allGroupFixtures>,
  leanings: { fxId: string; lean: string }[],
): string {
  const niceDate = new Date(`${dateStr}T12:00:00Z`).toLocaleDateString("es-MX", {
    timeZone: "America/Mexico_City",
    weekday: "long",
    day: "numeric",
    month: "long",
  });
  const teamName = (code: string) => TEAMS_BY_CODE[code]?.name ?? code;

  const fxLines = todays.length
    ? todays.map(fx => `- ${teamName(fx.home)} vs ${teamName(fx.away)} (grupo ${fx.group}, jornada ${fx.matchday})`).join("\n")
    : "(no hay partidos hoy — habla del próximo día con acción)";

  const leanLines = leanings.length
    ? leanings.map(l => `- ${l.fxId}: ${l.lean}`).join("\n")
    : "(aún no hay picks suficientes)";

  return `Hoy es ${niceDate}.

Partidos del día:
${fxLines}

Hacia dónde se inclinan los charales (porcentaje de picks):
${leanLines}

Escribe el Café AM con tu voz.`;
}

function poolLeanings(
  todays: ReturnType<typeof allGroupFixtures>,
  picksByPlayer: Record<string, StoredPicks>,
): { fxId: string; lean: string }[] {
  const out: { fxId: string; lean: string }[] = [];
  for (const fx of todays) {
    let h = 0, d = 0, a = 0, total = 0;
    for (const p of PLAYERS) {
      if (p.id === AI_PLAYER_ID) continue;
      const pick = picksByPlayer[p.id]?.group?.[fx.id]?.pick;
      if (!pick) continue;
      total += 1;
      if (pick === "H") h += 1;
      else if (pick === "D") d += 1;
      else a += 1;
    }
    if (total === 0) {
      out.push({ fxId: fx.id, lean: "sin picks aún" });
      continue;
    }
    const pct = (n: number) => Math.round((n / total) * 100);
    out.push({
      fxId: fx.id,
      lean: `${fx.home} ${pct(h)}% / empate ${pct(d)}% / ${fx.away} ${pct(a)}% (n=${total})`,
    });
  }
  return out;
}

async function generateBrief(dateStr: string): Promise<string | null> {
  const todays = allGroupFixtures()
    .filter(fx => fx.date === dateStr)
    .sort((a, b) => a.matchday - b.matchday || a.id.localeCompare(b.id));

  const picksByPlayer: Record<string, StoredPicks> = {};
  await Promise.all(
    PLAYERS.map(async p => {
      picksByPlayer[p.id] = (await getPicks(p.id).catch(() => null)) as StoredPicks;
    }),
  );

  const leanings = poolLeanings(todays, picksByPlayer);
  const user = buildUserPrompt(dateStr, todays, leanings);

  try {
    const resp = await getClient().models.generateContent({
      model: MODEL,
      contents: [{ role: "user", parts: [{ text: user }] }],
      config: {
        systemInstruction: { parts: [{ text: AVA_SYSTEM }] },
        temperature: 0.65,
        maxOutputTokens: 350,
        thinkingConfig: { thinkingBudget: 0 },
      },
    });
    const parts = resp.candidates?.[0]?.content?.parts ?? [];
    const text = parts.map(p => (p as { text?: string }).text ?? "").join("").trim();
    return text || null;
  } catch (err) {
    console.warn("[cafe-am] model failed", err);
    return null;
  }
}

export async function POST(req: NextRequest) {
  const expected = process.env.CRON_SECRET;
  if (!expected) return Response.json({ ok: false, error: "cron_disabled" }, { status: 503 });
  if (req.headers.get("x-cron-secret") !== expected) {
    return Response.json({ ok: false, error: "forbidden" }, { status: 403 });
  }

  const { searchParams } = new URL(req.url);
  const force = searchParams.get("force") === "1";
  const dateStr = cdmxDate();

  const ref = db.collection(COLLECTION).doc(dateStr);
  const existing = await ref.get();
  if (existing.exists && !force) {
    return Response.json({ ok: true, mode: "cached", date: dateStr, brief: existing.data() });
  }

  const text = await generateBrief(dateStr);
  if (!text) {
    return Response.json({ ok: false, error: "generation_failed", date: dateStr }, { status: 502 });
  }
  const doc: CafeBrief = {
    date: dateStr,
    text,
    generatedAt: Date.now(),
    modelUsed: MODEL,
  };
  await ref.set(doc);
  return Response.json({ ok: true, mode: force ? "forced" : "fresh", date: dateStr, brief: doc });
}
