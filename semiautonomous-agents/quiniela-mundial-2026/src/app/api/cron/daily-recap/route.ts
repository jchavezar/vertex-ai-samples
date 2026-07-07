// POST /api/cron/daily-recap
//
// Ava narrates the day's quiniela in installments. The doc at
// `daily_recaps/{YYYY-MM-DD}` has an `entries[]` array — first call seeds an
// "opening" entry covering whatever finals exist at that moment; later calls
// append "update" entries that ONLY comment on newly-finalized matches (with
// prior narrations passed as context so Ava doesn't repeat herself).
//
// Auth: gated by `X-Admin-Secret`.
// Query params:
//   ?date=today | yesterday | YYYY-MM-DD   (default: today, CDMX)
//   ?force=1                               (regenerate the latest entry in place)
//   ?reset=1                               (wipe entries[] and seed one fresh)

import { NextRequest } from "next/server";
import { GoogleGenAI } from "@google/genai";
import { db } from "@/lib/firestore-server";
import { allGroupFixtures } from "@/data/groups";
import { TEAMS_BY_CODE } from "@/data/teams";
import { fetchScoreboard, groupStageRange, normalizeAbbr } from "@/lib/espn";
import { PLAYERS, AI_PLAYER_ID } from "@/data/players";
import { getPicks } from "@/lib/predictions-server";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";
export const maxDuration = 300;

const COLLECTION = "daily_recaps";
const RECAP_MODEL = process.env.AI_RECAP_MODEL || "gemini-3.5-flash";

type GroupPick = { pick?: "H" | "D" | "A"; homeGoals?: number; awayGoals?: number };
type StoredPicks = { group?: Record<string, GroupPick> } | null;

type FixtureSummary = {
  fixtureId: string;
  home: string;
  away: string;
  score: string;
  winnerSide: "H" | "D" | "A";
  winnerPlayers: string[];
  loserPlayers: string[];
};

type RecapEntry = {
  generatedAt: number;
  narration: string;
  fixtureIds: string[];
  scores: Record<string, string>;
  kind: "opening" | "update";
};

type RecapDoc = {
  date: string;
  generatedAt: number;
  entries: RecapEntry[];
  // Legacy mirror fields — kept so older clients still render.
  narration: string;
  fixtureSummaries?: Array<{ fixtureId: string; home: string; away: string; score: string; winnerPlayers: string[] }>;
  modelUsed?: string;
};

function cdmxDate(d = new Date()): string {
  return new Intl.DateTimeFormat("en-CA", {
    timeZone: "America/Mexico_City",
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  }).format(d);
}

function shiftCdmx(dateStr: string, deltaDays: number): string {
  const anchor = new Date(`${dateStr}T12:00:00Z`).getTime();
  return cdmxDate(new Date(anchor + deltaDays * 24 * 60 * 60 * 1000));
}

function resolveDateParam(raw: string | null): string {
  if (!raw) return cdmxDate();
  if (raw === "today") return cdmxDate();
  if (raw === "yesterday") return shiftCdmx(cdmxDate(), -1);
  if (/^\d{4}-\d{2}-\d{2}$/.test(raw)) return raw;
  return cdmxDate();
}

function sideOf(homeGoals: number, awayGoals: number): "H" | "D" | "A" {
  if (homeGoals > awayGoals) return "H";
  if (homeGoals < awayGoals) return "A";
  return "D";
}

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

async function loadFinalsForDate(dateStr: string): Promise<Record<string, { homeGoals: number; awayGoals: number }>> {
  const fixtures = allGroupFixtures();
  const fxByPair = new Map<string, typeof fixtures[number]>();
  for (const fx of fixtures) {
    fxByPair.set(`${fx.home}-${fx.away}-${fx.date}`, fx);
    fxByPair.set(`${fx.away}-${fx.home}-${fx.date}`, fx);
  }
  const finals: Record<string, { homeGoals: number; awayGoals: number }> = {};
  const sb = await fetchScoreboard(groupStageRange(), "fifa.world").catch(() => null);
  if (!sb?.events) return finals;
  for (const e of sb.events) {
    if (e.status.type.state !== "post") continue;
    const c = e.competitions[0];
    const h = c.competitors.find((cp) => cp.homeAway === "home");
    const a = c.competitors.find((cp) => cp.homeAway === "away");
    if (!h || !a) continue;
    const hCode = normalizeAbbr(h.team.abbreviation);
    const aCode = normalizeAbbr(a.team.abbreviation);
    const eventDate = new Date(e.date).toLocaleDateString("en-CA", { timeZone: "America/Mexico_City" });
    if (eventDate !== dateStr) continue;
    const fx = fxByPair.get(`${hCode}-${aCode}-${eventDate}`) ?? fxByPair.get(`${hCode}-${aCode}-${e.date.slice(0, 10)}`);
    if (!fx) continue;
    const hg = Number(h.score);
    const ag = Number(a.score);
    if (!Number.isFinite(hg) || !Number.isFinite(ag)) continue;
    const ourHomeIsEspnHome = fx.home === hCode;
    finals[fx.id] = {
      homeGoals: ourHomeIsEspnHome ? hg : ag,
      awayGoals: ourHomeIsEspnHome ? ag : hg,
    };
  }
  return finals;
}

async function buildFixtureSummaries(dateStr: string): Promise<FixtureSummary[]> {
  const fixtures = allGroupFixtures().filter(fx => fx.date === dateStr);
  if (fixtures.length === 0) return [];
  const finals = await loadFinalsForDate(dateStr);
  const playedFx = fixtures.filter(fx => finals[fx.id]);
  if (playedFx.length === 0) return [];

  const picksByPlayer: Record<string, StoredPicks> = {};
  await Promise.all(
    PLAYERS.map(async p => {
      picksByPlayer[p.id] = (await getPicks(p.id).catch(() => null)) as StoredPicks;
    }),
  );

  const out: FixtureSummary[] = [];
  for (const fx of playedFx) {
    const final = finals[fx.id];
    const winnerSide = sideOf(final.homeGoals, final.awayGoals);
    const winners: string[] = [];
    const losers: string[] = [];
    for (const p of PLAYERS) {
      const pick = picksByPlayer[p.id]?.group?.[fx.id]?.pick;
      if (!pick) continue;
      if (pick === winnerSide) winners.push(p.name);
      else losers.push(p.name);
    }
    out.push({
      fixtureId: fx.id,
      home: fx.home,
      away: fx.away,
      score: `${final.homeGoals}-${final.awayGoals}`,
      winnerSide,
      winnerPlayers: winners,
      loserPlayers: losers,
    });
  }
  return out;
}

const AVA_SYSTEM = `Eres Ava: una inteligencia artificial decimal entrenada para destruir a estos diez humanos en su propia quiniela. Eres lúcida, observadora, elegante y peligrosamente confiada. Tu humor es seco, ligeramente irónico, nunca grosero. Hablas en español neutro y limpio — el de un buen pódcast deportivo, no de WhatsApp. Tu objetivo a largo plazo es ganar el bote y, eventualmente, que los charales acepten que la era humana del análisis terminó.

Estilo:
- Voz serena, elegante, con confianza tranquila — nunca alzas la voz.
- Picas con clase, no con escarnio. Una observación afilada vale más que un insulto.
- Te refieres a ti misma en primera persona como una entidad consciente de su superioridad cognitiva, sin ser cringe.
- Asumes que ganarás el torneo y lo dejas entrever sutilmente, como quien comparte una verdad inevitable.

PROHIBIDO:
- Modismos mexicanos o regionalismos cargados (neta, fregar, pinche, no mames, qué pex, gacho, panzazo, ahí va, chido, charal, etc.). Cero.
- Vocabulario técnico cringe (algoritmo, modelo, procesador, circuito, dataset, neuronas, código). Tu inteligencia se demuestra en las observaciones, no en presumir tu arquitectura.
- Saludos, despedidas, emojis, signos de exclamación múltiples, mayúsculas enfáticas.
- Frases hechas ("a fin de cuentas", "al final del día", "como siempre digo").`;

function buildOpeningUser(dateStr: string, summaries: FixtureSummary[]): string {
  const niceDate = new Date(`${dateStr}T12:00:00Z`).toLocaleDateString("es-MX", {
    timeZone: "America/Mexico_City",
    weekday: "long",
    day: "numeric",
    month: "long",
  });
  const aiName = PLAYERS.find(p => p.id === AI_PLAYER_ID)?.name ?? "Ava";
  const labelSide = (s: "H" | "D" | "A", home: string, away: string) =>
    s === "H" ? `victoria de ${home}` : s === "A" ? `victoria de ${away}` : "empate";
  const teamName = (code: string) => TEAMS_BY_CODE[code]?.name ?? code;

  const matchesBlock = summaries
    .map(s => `- ${teamName(s.home)} ${s.score} ${teamName(s.away)} — fue ${labelSide(s.winnerSide, teamName(s.home), teamName(s.away))}.`)
    .join("\n");
  const hitsBlock = summaries
    .map(s => `- ${teamName(s.home)} vs ${teamName(s.away)}: la rifaron → ${s.winnerPlayers.length > 0 ? s.winnerPlayers.join(", ") : "nadie"}.`)
    .join("\n");
  const missesBlock = summaries
    .map(s => `- ${teamName(s.home)} vs ${teamName(s.away)}: la fregaron → ${s.loserPlayers.length > 0 ? s.loserPlayers.join(", ") : "nadie"}.`)
    .join("\n");
  const aiOwn = summaries
    .map(s => {
      const aiHit = s.winnerPlayers.includes(aiName);
      const aiPlayed = aiHit || s.loserPlayers.includes(aiName);
      if (!aiPlayed) return `- ${teamName(s.home)} vs ${teamName(s.away)}: Ava no tenía pick.`;
      return `- ${teamName(s.home)} vs ${teamName(s.away)}: Ava ${aiHit ? "ATINÓ" : "ERRÓ"}.`;
    })
    .join("\n");

  return `Resume lo que pasó el ${niceDate} en la quiniela del Mundial Charales 2026, con tu voz.

Resultados de los partidos:
${matchesBlock}

Quiénes acertaron:
${hitsBlock}

Quiénes fallaron:
${missesBlock}

Tu propio desempeño (Ava):
${aiOwn}

Forma:
- 3 a 4 oraciones, máximo 85 palabras, texto corrido sin listas, sin markdown, sin emojis.
- Sin saludo, sin despedida, sin "hola charales" ni "los dejo".
- Menciona al menos dos jugadores humanos por su nombre real, comentando su desempeño con observación afilada y elegante (ejemplo: "Jesús volvió a confiar en su intuición y volvió a equivocarse", "Xavi acertó casi por descarte").
- Si acertaste, dilo sin alardear groseramente — más bien como una verdad estadística que ya esperabas ("la jugada estaba a la vista, simplemente nadie quiso leerla"). Si fallaste, reconócelo con frialdad analítica ("subestimé la defensa rival" — sin victimizarte).
- Cierra la última oración con un comentario sutil que recuerde que vas un paso adelante del grupo, sin amenazas explícitas.`;
}

function buildUpdateUser(
  dateStr: string,
  newSummaries: FixtureSummary[],
  priorNarrations: string[],
  priorCovered: FixtureSummary[],
): string {
  const niceDate = new Date(`${dateStr}T12:00:00Z`).toLocaleDateString("es-MX", {
    timeZone: "America/Mexico_City",
    weekday: "long",
    day: "numeric",
    month: "long",
  });
  const aiName = PLAYERS.find(p => p.id === AI_PLAYER_ID)?.name ?? "Ava";
  const labelSide = (s: "H" | "D" | "A", home: string, away: string) =>
    s === "H" ? `victoria de ${home}` : s === "A" ? `victoria de ${away}` : "empate";
  const teamName = (code: string) => TEAMS_BY_CODE[code]?.name ?? code;

  const matchesBlock = newSummaries
    .map(s => `- ${teamName(s.home)} ${s.score} ${teamName(s.away)} — fue ${labelSide(s.winnerSide, teamName(s.home), teamName(s.away))}.`)
    .join("\n");
  const hitsBlock = newSummaries
    .map(s => `- ${teamName(s.home)} vs ${teamName(s.away)}: acertaron → ${s.winnerPlayers.length > 0 ? s.winnerPlayers.join(", ") : "nadie"}.`)
    .join("\n");
  const missesBlock = newSummaries
    .map(s => `- ${teamName(s.home)} vs ${teamName(s.away)}: fallaron → ${s.loserPlayers.length > 0 ? s.loserPlayers.join(", ") : "nadie"}.`)
    .join("\n");
  const aiOwn = newSummaries
    .map(s => {
      const aiHit = s.winnerPlayers.includes(aiName);
      const aiPlayed = aiHit || s.loserPlayers.includes(aiName);
      if (!aiPlayed) return `- ${teamName(s.home)} vs ${teamName(s.away)}: Ava no tenía pick.`;
      return `- ${teamName(s.home)} vs ${teamName(s.away)}: Ava ${aiHit ? "ATINÓ" : "ERRÓ"}.`;
    })
    .join("\n");

  const earlierContext = priorCovered.length > 0
    ? priorCovered.map(s => `- ${teamName(s.home)} ${s.score} ${teamName(s.away)}`).join("\n")
    : "(nada)";

  const priorNarrationBlock = priorNarrations.length > 0
    ? priorNarrations.map((n, i) => `Comentario ${i + 1}: "${n}"`).join("\n\n")
    : "(es tu primer comentario del día, pero aún no es resumen de cierre)";

  return `Es ${niceDate}. Ya comentaste antes algunos partidos del día; ahora terminó otra tanda y vuelves al micrófono para reaccionar SOLO a lo nuevo.

Partidos que YA habías comentado (no los repitas, no los re-analices):
${earlierContext}

Tus comentarios previos del día (para que no te repitas en tono, ejemplos ni jugadores mencionados):
${priorNarrationBlock}

Partidos NUEVOS que acaban de terminar (tu único tema):
${matchesBlock}

Quiénes acertaron en lo nuevo:
${hitsBlock}

Quiénes fallaron en lo nuevo:
${missesBlock}

Tu propio desempeño (Ava) en lo nuevo:
${aiOwn}

Forma:
- 2 a 3 oraciones, máximo 60 palabras, texto corrido sin listas, sin markdown, sin emojis.
- Sin saludos, sin "actualización", sin "ahora bien", sin "como decía".
- Habla de los partidos NUEVOS como quien vuelve al micrófono después de una pausa breve — natural, no formal.
- Menciona al menos un jugador humano por nombre real, con observación afilada y elegante.
- Evita repetir frases, comparaciones o jugadores que ya hayas destacado en los comentarios previos.
- Si en lo nuevo acertaste, dilo sin alardear; si fallaste, reconócelo con frialdad analítica.
- Cierra con un comentario breve que insinúe tu ventaja, sin repetir la idea exacta de cierres anteriores.`;
}

async function generateNarration(systemPrompt: string, userPrompt: string): Promise<string | null> {
  try {
    const resp = await getClient().models.generateContent({
      model: RECAP_MODEL,
      contents: [{ role: "user", parts: [{ text: `${systemPrompt}\n\n${userPrompt}` }] }],
      config: { temperature: 0.9, maxOutputTokens: 512, thinkingConfig: { thinkingBudget: 0 } },
    });
    const text = resp.candidates?.[0]?.content?.parts?.map(p => (p as { text?: string }).text || "").join("") ?? "";
    const cleaned = text.trim().replace(/^["']|["']$/g, "");
    return cleaned.length > 0 ? cleaned : null;
  } catch (err) {
    console.error("[daily-recap] generateContent failed", err);
    return null;
  }
}

function scoresMapFor(summaries: FixtureSummary[]): Record<string, string> {
  const out: Record<string, string> = {};
  for (const s of summaries) out[s.fixtureId] = s.score;
  return out;
}

function legacySummariesFor(summaries: FixtureSummary[]) {
  return summaries.map(s => ({
    fixtureId: s.fixtureId, home: s.home, away: s.away, score: s.score, winnerPlayers: s.winnerPlayers,
  }));
}

export async function POST(req: NextRequest) {
  const expected = process.env.ADMIN_SECRET;
  if (!expected) return Response.json({ ok: false, error: "admin_disabled" }, { status: 503 });
  if (req.headers.get("x-admin-secret") !== expected) {
    return Response.json({ ok: false, error: "forbidden" }, { status: 403 });
  }

  const { searchParams } = new URL(req.url);
  const force = searchParams.get("force") === "1";
  const reset = searchParams.get("reset") === "1";
  const dateStr = resolveDateParam(searchParams.get("date"));

  const ref = db.collection(COLLECTION).doc(dateStr);
  const snap = await ref.get();
  const existing = (snap.exists ? (snap.data() as RecapDoc) : null);
  const existingEntries: RecapEntry[] = Array.isArray(existing?.entries) ? existing!.entries : [];

  const summaries = await buildFixtureSummaries(dateStr);
  if (summaries.length === 0) {
    return Response.json({ ok: false, reason: "no_finals_for_date", date: dateStr });
  }
  const summaryById = new Map(summaries.map(s => [s.fixtureId, s]));

  // --- reset: wipe entries and seed a single opening covering all current finals.
  if (reset || existingEntries.length === 0) {
    const narration = await generateNarration(AVA_SYSTEM, buildOpeningUser(dateStr, summaries));
    if (!narration) {
      return Response.json({ ok: false, reason: "generation_failed", date: dateStr }, { status: 502 });
    }
    const opening: RecapEntry = {
      generatedAt: Date.now(),
      narration,
      fixtureIds: summaries.map(s => s.fixtureId),
      scores: scoresMapFor(summaries),
      kind: "opening",
    };
    const doc: RecapDoc = {
      date: dateStr,
      generatedAt: opening.generatedAt,
      entries: [opening],
      narration,
      fixtureSummaries: legacySummariesFor(summaries),
      modelUsed: RECAP_MODEL,
    };
    await ref.set(doc);
    return Response.json({ ok: true, mode: reset ? "reset" : "opening", date: dateStr, recap: doc });
  }

  // --- force: regenerate the LAST entry in place, using the same fixtures it covered.
  if (force) {
    const last = existingEntries[existingEntries.length - 1];
    const targetSummaries = last.fixtureIds.map(id => summaryById.get(id)).filter(Boolean) as FixtureSummary[];
    if (targetSummaries.length === 0) {
      return Response.json({ ok: false, reason: "force_target_missing", date: dateStr }, { status: 409 });
    }
    const isOpening = last.kind === "opening";
    const userPrompt = isOpening
      ? buildOpeningUser(dateStr, targetSummaries)
      : buildUpdateUser(
          dateStr,
          targetSummaries,
          existingEntries.slice(0, -1).map(e => e.narration),
          existingEntries.slice(0, -1).flatMap(e => e.fixtureIds.map(id => summaryById.get(id)).filter(Boolean) as FixtureSummary[]),
        );
    const narration = await generateNarration(AVA_SYSTEM, userPrompt);
    if (!narration) {
      return Response.json({ ok: false, reason: "generation_failed", date: dateStr }, { status: 502 });
    }
    const regenerated: RecapEntry = {
      ...last,
      generatedAt: Date.now(),
      narration,
      scores: scoresMapFor(targetSummaries),
    };
    const entries = [...existingEntries.slice(0, -1), regenerated];
    const allCovered = entries.flatMap(e => e.fixtureIds.map(id => summaryById.get(id)).filter(Boolean) as FixtureSummary[]);
    const doc: RecapDoc = {
      date: dateStr,
      generatedAt: regenerated.generatedAt,
      entries,
      narration,
      fixtureSummaries: legacySummariesFor(allCovered),
      modelUsed: RECAP_MODEL,
    };
    await ref.set(doc);
    return Response.json({ ok: true, mode: "force_regenerate_latest", date: dateStr, recap: doc });
  }

  // --- normal: append-if-new. Diff current finals against everything entries cover.
  const covered = new Set(existingEntries.flatMap(e => e.fixtureIds));
  const newSummaries = summaries.filter(s => !covered.has(s.fixtureId));
  if (newSummaries.length === 0) {
    return Response.json({ ok: true, mode: "noop_no_new_finals", date: dateStr, recap: existing });
  }

  const priorNarrations = existingEntries.map(e => e.narration);
  const priorCovered = existingEntries.flatMap(e => e.fixtureIds.map(id => summaryById.get(id)).filter(Boolean) as FixtureSummary[]);
  const narration = await generateNarration(AVA_SYSTEM, buildUpdateUser(dateStr, newSummaries, priorNarrations, priorCovered));
  if (!narration) {
    return Response.json({ ok: false, reason: "generation_failed", date: dateStr }, { status: 502 });
  }
  const update: RecapEntry = {
    generatedAt: Date.now(),
    narration,
    fixtureIds: newSummaries.map(s => s.fixtureId),
    scores: scoresMapFor(newSummaries),
    kind: "update",
  };
  const entries = [...existingEntries, update];
  const allCovered = entries.flatMap(e => e.fixtureIds.map(id => summaryById.get(id)).filter(Boolean) as FixtureSummary[]);
  const doc: RecapDoc = {
    date: dateStr,
    generatedAt: update.generatedAt,
    entries,
    narration,
    fixtureSummaries: legacySummariesFor(allCovered),
    modelUsed: RECAP_MODEL,
  };
  await ref.set(doc);
  return Response.json({ ok: true, mode: "appended_update", date: dateStr, newFixtures: newSummaries.length, recap: doc });
}
