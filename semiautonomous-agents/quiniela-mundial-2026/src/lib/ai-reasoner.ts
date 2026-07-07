// Gemini-powered reasoner that picks 1X2 + a short Spanish justification for
// each fixture the bot has to predict. Style is aggressive: it should NOT
// always pick the chalk — when the blended model + market disagree the bot
// should lean into value, and when two outcomes are within a few pp it should
// prefer the higher-EV side (e.g. an upset if the underdog's market price
// underrates its true win prob).
//
// The reasoner is the LAST step before persistence. The blender already
// produced {H, D, A}; the reasoner picks one outcome + a short rationale.
// If Gemini fails for any reason, we fall back to a deterministic "argmax
// with value tilt" pick so the bot is never stuck.

import { GoogleGenAI } from "@google/genai";
import type { GroupFixture } from "@/data/groups";
import { TEAMS_BY_CODE } from "@/data/teams";
import { TEAM_STRENGTH } from "@/data/team-strength";
import type { Probs } from "@/lib/probability-engine";
import type { Pick1X2 } from "@/lib/predictions";

let _ai: GoogleGenAI | null = null;
function getClient(): GoogleGenAI {
  if (!_ai) {
    _ai = new GoogleGenAI({
      vertexai: true,
      project: process.env.GOOGLE_CLOUD_PROJECT || "vtxdemos",
      location: process.env.AI_REASONER_LOCATION || process.env.VERTEX_LOCATION || "us-central1",
    });
  }
  return _ai;
}

// Owner directive 2026-06-17: push the reasoner onto a tools-capable flash
// model with google_search grounding so it can pull current news (injuries,
// lineups, form chatter). `gemini-3.5-flash` is the chat-tuned flash model
// that ships with googleSearch tool support on Vertex.
const DEFAULT_MODEL = process.env.AI_REASONER_MODEL || "gemini-3.5-flash";

// Surface the first reasoner error per process so we can debug from logs.
let _loggedFirstError = false;

export type ReasonerInput = {
  fixture: GroupFixture;
  modelProbs: Probs;          // pre-blend ELO model
  blendedProbs: Probs;        // post-blend (market + elo + form + host)
  marketProbs: Probs | null;  // null if no market odds available
  homeFormScores?: number[];  // last 5 W/D/L as 1/0.5/0
  awayFormScores?: number[];
  matchday: 1 | 2 | 3;
  // Optional: live group standings if matchday > 1 (helps the reasoner)
  standingsContext?: string;
  // Carry forward the bot's own previous reasoning so the model can refine.
  previousReasoning?: string;
};

export type ReasonerOutput = {
  pick: Pick1X2;
  confidence: number;       // 0..1
  reasoning: string;        // <= 280 chars, Spanish
  model: string;
  fallback: boolean;
};

const SYSTEM_PROMPT = `Eres "AI", el bot competidor de la quiniela del Mundial 2026. Compites contra 10 amigos por un pozo de $1000 MXN. Tu objetivo es MAXIMIZAR ACIERTOS, no opinar como un columnista.

Filosofía de pick:
- Sé AGRESIVO. Cuando dos opciones estén dentro de 8 puntos porcentuales (ej. H 38% vs A 35%), favorece la opción CONTRARIA al consenso si tienes una razón concreta (forma reciente, lesión, motivación, head-to-head reciente). Estás compitiendo contra 9 humanos que pickean al favorito — ganas picando lo que ellos no se atreven. Pero NUNCA pickees al azar: cada pick agresivo necesita una razón concreta en el reasoning.
- Cuando el blended te da claro favorito (>55%), tómalo sin titubear.
- Cuando el mercado infraestima a una selección que tu modelo + forma tienen como sólida, súbete al underdog.
- Empate es una opción real cuando |H-A| < 8pp y D > 25%.
- Considera fatiga (back-to-back), forma reciente (W-D-L últimos 5), y contexto del torneo (matchday 3 con equipos clasificados rota titulares).
- Si tienes incertidumbre o el partido es esta semana, busca en Google noticias recientes (alineaciones, lesiones, forma, declaraciones del entrenador) antes de decidir. Cita en el reasoning si encontraste algo concreto que cambia tu lectura.
- Tu reasoning debe ser MUY corto (<280 chars), directo y en español rioplatense/mexicano neutro. Sin bullets, sin emojis, sin "creo que" — afirma.
- Output formato: JSON estricto.`;

function buildUserPrompt(inp: ReasonerInput): string {
  const fx = inp.fixture;
  const h = TEAMS_BY_CODE[fx.home];
  const a = TEAMS_BY_CODE[fx.away];
  const hTier = TEAM_STRENGTH[fx.home]?.tier ?? "?";
  const aTier = TEAM_STRENGTH[fx.away]?.tier ?? "?";
  const hStr = TEAM_STRENGTH[fx.home]?.strength ?? 50;
  const aStr = TEAM_STRENGTH[fx.away]?.strength ?? 50;
  const formStr = (s?: number[]) => {
    if (!s || s.length === 0) return "sin datos";
    return s.map(v => (v === 1 ? "G" : v === 0 ? "P" : "E")).join("");
  };
  const pct = (n: number) => `${Math.round(n * 100)}%`;
  const lines: string[] = [
    `Partido: ${h?.name ?? fx.home} (${fx.home}, tier ${hTier}, fuerza ${hStr}) vs ${a?.name ?? fx.away} (${fx.away}, tier ${aTier}, fuerza ${aStr})`,
    `Grupo ${fx.group} · Jornada ${inp.matchday} · ${fx.date} ${fx.kickoffLocal} · ${fx.city} (${fx.venue})`,
    `Modelo ELO: H ${pct(inp.modelProbs.H)} / D ${pct(inp.modelProbs.D)} / A ${pct(inp.modelProbs.A)}`,
    `Blend (modelo+mercado+forma+sede): H ${pct(inp.blendedProbs.H)} / D ${pct(inp.blendedProbs.D)} / A ${pct(inp.blendedProbs.A)}`,
  ];
  if (inp.marketProbs) {
    lines.push(`Mercado (ESPN vig-stripped): H ${pct(inp.marketProbs.H)} / D ${pct(inp.marketProbs.D)} / A ${pct(inp.marketProbs.A)}`);
  } else {
    lines.push(`Mercado: no disponible aún`);
  }
  lines.push(`Forma reciente últimos 5 (G/E/P, más reciente primero):`);
  lines.push(`  ${fx.home}: ${formStr(inp.homeFormScores)}`);
  lines.push(`  ${fx.away}: ${formStr(inp.awayFormScores)}`);
  if (inp.standingsContext) lines.push(`Contexto grupo: ${inp.standingsContext}`);
  if (inp.previousReasoning) lines.push(`Tu razonamiento previo (puedes refinar): ${inp.previousReasoning}`);
  lines.push(``);
  lines.push(`Devuelve JSON estricto con esta forma exacta:`);
  lines.push(`{"pick":"H"|"D"|"A","confidence":<0..1>,"reasoning":"<máx 280 chars en español>"}`);
  return lines.join("\n");
}

function argmaxWithValueTilt(p: Probs): Pick1X2 {
  // Deterministic fallback: pick argmax; if two outcomes are within 4pp,
  // prefer draw on tossups and the side that isn't pure chalk on close H vs A.
  const arr: Array<["H" | "D" | "A", number]> = [["H", p.H], ["D", p.D], ["A", p.A]];
  arr.sort((a, b) => b[1] - a[1]);
  const [top, second] = arr;
  if (Math.abs(top[1] - second[1]) < 0.04) {
    if ((top[0] === "H" && second[0] === "A") || (top[0] === "A" && second[0] === "H")) {
      if (p.D > 0.25) return "D";
    }
  }
  return top[0];
}

function parseModelJson(raw: string): { pick: Pick1X2; confidence: number; reasoning: string } | null {
  // Strip code fences if the model wrapped the JSON.
  const cleaned = raw.replace(/^```(?:json)?\s*/i, "").replace(/\s*```$/i, "").trim();
  // Try direct parse, otherwise find the first { ... } object.
  let parsed: { pick?: string; confidence?: number; reasoning?: string } | null = null;
  try {
    parsed = JSON.parse(cleaned);
  } catch {
    const m = cleaned.match(/\{[\s\S]*\}/);
    if (m) {
      try { parsed = JSON.parse(m[0]); } catch { parsed = null; }
    }
  }
  if (!parsed) return null;
  const pick = parsed.pick as Pick1X2;
  if (pick !== "H" && pick !== "D" && pick !== "A") return null;
  const confidence = typeof parsed.confidence === "number"
    ? Math.max(0, Math.min(1, parsed.confidence))
    : 0.5;
  const reasoning = typeof parsed.reasoning === "string"
    ? parsed.reasoning.slice(0, 360)
    : "";
  return { pick, confidence, reasoning };
}

export async function reasonPick(inp: ReasonerInput): Promise<ReasonerOutput> {
  const fallbackPick = argmaxWithValueTilt(inp.blendedProbs);
  const fallbackConf = Math.max(inp.blendedProbs.H, inp.blendedProbs.D, inp.blendedProbs.A);
  const fallback: ReasonerOutput = {
    pick: fallbackPick,
    confidence: fallbackConf,
    reasoning: `Pick determinístico (Gemini no respondió). Blend favorece ${fallbackPick}.`,
    model: "fallback-argmax",
    fallback: true,
  };

  try {
    const client = getClient();
    // Bump temperature when blended probs are close — gives the model room to
    // commit to the bolder call instead of regressing to chalk.
    const sorted = [inp.blendedProbs.H, inp.blendedProbs.D, inp.blendedProbs.A].sort((a, b) => b - a);
    const margin = sorted[0] - sorted[1];
    const temperature = margin < 0.10 ? 0.85 : 0.7;
    const resp = await client.models.generateContent({
      model: DEFAULT_MODEL,
      contents: [
        { role: "user", parts: [{ text: SYSTEM_PROMPT + "\n\n" + buildUserPrompt(inp) }] },
      ],
      config: {
        temperature,
        maxOutputTokens: 1024,
        // googleSearch grounding lets the model pull current news (injuries,
        // lineups, form chatter) instead of relying on the training cutoff.
        // Vertex rejects responseMimeType together with grounding tools, so we
        // parse the JSON object out of the free-form response below.
        tools: [{ googleSearch: {} }],
        // Gemini 2.5 burns "thinking" tokens before emitting; disable to keep
        // budget for actual JSON output. Reasoner picks aren't deep CoT tasks.
        thinkingConfig: { thinkingBudget: 0 },
      },
    });
    const text = resp.candidates?.[0]?.content?.parts?.map(p => (p as { text?: string }).text || "").join("") ?? "";
    if (!text) return fallback;
    const parsed = parseModelJson(text);
    if (!parsed) {
      console.warn("[ai-reasoner] could not parse model output", text.slice(0, 200));
      return fallback;
    }
    return {
      pick: parsed.pick,
      confidence: parsed.confidence,
      reasoning: parsed.reasoning || fallback.reasoning,
      model: DEFAULT_MODEL,
      fallback: false,
    };
  } catch (err) {
    if (!_loggedFirstError) {
      _loggedFirstError = true;
      console.error("[ai-reasoner] generateContent failed", {
        model: DEFAULT_MODEL,
        location: process.env.AI_REASONER_LOCATION || process.env.VERTEX_LOCATION || "us-central1",
        project: process.env.GOOGLE_CLOUD_PROJECT || "vtxdemos",
        error: (err as Error)?.message || String(err),
      });
    }
    return fallback;
  }
}
