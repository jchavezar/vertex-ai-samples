// POST { slots: [{slot, teamA, teamB, hPct, aPct}] }
// Auth required. Returns Gemini-picked R32 winners with brief Spanish reasoning.
import { readAuth } from "@/lib/auth-server";
import { GoogleGenAI } from "@google/genai";
import { TEAMS_BY_CODE } from "@/data/teams";
import { TEAM_STRENGTH } from "@/data/team-strength";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

type Slot = { slot: string; teamA: string; teamB: string; hPct: number; aPct: number };
type PickResult = { slot: string; pick: string; reason: string };

let _ai: GoogleGenAI | null = null;
function getClient(): GoogleGenAI {
  if (!_ai) {
    _ai = new GoogleGenAI({
      vertexai: true,
      project: process.env.GOOGLE_CLOUD_PROJECT || "vtxdemos",
      location: process.env.AI_REASONER_LOCATION || "global",
    });
  }
  return _ai;
}

const MODEL = process.env.AI_REASONER_MODEL || "gemini-3-flash-preview";

function teamLine(code: string): string {
  const t = TEAMS_BY_CODE[code];
  const s = TEAM_STRENGTH[code];
  const name = t?.name ?? code;
  const notes = s?.notes ?? "";
  return notes ? `${name} (${code}) — ${notes}` : `${name} (${code})`;
}

export async function POST(req: Request) {
  const auth = await readAuth();
  if (!auth) return Response.json({ ok: false, error: "unauthorized" }, { status: 401 });

  let body: { slots?: Slot[] };
  try {
    body = await req.json();
  } catch {
    return Response.json({ ok: false, error: "invalid json" }, { status: 400 });
  }

  const slots = body.slots;
  if (!Array.isArray(slots) || slots.length === 0) {
    return Response.json({ ok: false, error: "slots required" }, { status: 400 });
  }

  const matchLines = slots.map(s => {
    const a = teamLine(s.teamA);
    const b = teamLine(s.teamB);
    return `${s.slot}: ${a}  vs  ${b}  [${s.teamA} ${s.hPct}% / ${s.teamB} ${s.aPct}%]`;
  }).join("\n");

  const prompt = `Eres un analista experto en fútbol del Mundial 2026. \
Recibes los partidos de dieciseisavos de final con probabilidades de victoria \
(sin empate porque es eliminatoria directa) basadas en ranking FIFA, fuerza del equipo y forma reciente.

Tu tarea: para CADA partido, elige el equipo ganador y escribe una razón de máximo 12 palabras en español.
Sé directo y confiado. No repitas el nombre del partido. Usa lenguaje deportivo natural.

Responde ÚNICAMENTE con JSON válido, sin markdown, sin texto extra:
{"picks":[{"slot":"R32-N","pick":"COD","reason":"razón breve en español"},...]}

Partidos:
${matchLines}`;

  try {
    const ai = getClient();
    const response = await ai.models.generateContent({
      model: MODEL,
      contents: [{ role: "user", parts: [{ text: prompt }] }],
      config: { temperature: 0.7, maxOutputTokens: 1024 },
    });

    const raw = response.text?.trim() ?? "";
    const jsonStr = raw.replace(/^```(?:json)?\n?/i, "").replace(/\n?```$/i, "").trim();
    const parsed = JSON.parse(jsonStr) as { picks: PickResult[] };

    // Validate: each pick must reference a team from the submitted slot
    const slotMap = new Map(slots.map(s => [s.slot, { teamA: s.teamA, teamB: s.teamB }]));
    const valid = (parsed.picks ?? []).filter(p => {
      const s = slotMap.get(p.slot);
      return s && (p.pick === s.teamA || p.pick === s.teamB);
    });

    return Response.json({ ok: true, picks: valid });
  } catch (e) {
    console.error("[/api/bracket/ai-picks] Gemini error:", e);
    // Fallback: pick higher-probability team for each slot
    const fallback: PickResult[] = slots.map(s => ({
      slot: s.slot,
      pick: s.hPct >= s.aPct ? s.teamA : s.teamB,
      reason: "Selección por probabilidad del modelo de fuerza",
    }));
    return Response.json({ ok: true, picks: fallback, fallback: true });
  }
}
