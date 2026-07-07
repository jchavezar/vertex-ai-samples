// POST /api/envelope/open — opens TODAY's daily envelope for the logged-in
// user. Idempotent: returns the existing reward if already opened today.
//
// Reward weights live in `lib/envelope.ts`. All payloads here are NON-POINTS
// — purely visual / informational. We never touch `quiniela_charales_picks`.

import { NextRequest } from "next/server";
import { GoogleGenAI } from "@google/genai";
import { db } from "@/lib/firestore-server";
import { readAuth } from "@/lib/auth-server";
import { getPicks } from "@/lib/predictions-server";
import { PLAYERS } from "@/data/players";
import { allGroupFixtures } from "@/data/groups";
import { TEAMS } from "@/data/teams";
import { winProbabilities } from "@/data/team-ratings";
import { fixtureKickoffMs } from "@/lib/fixture-time";
import { styleForDay } from "@/app/api/cromos/portrait/route";
import { actualPick, type MatchResult, type Pick1X2, type PlayerPredictions } from "@/lib/predictions";
import { pickRandomVisualUnlock, findVisualUnlock } from "@/lib/visual-unlocks";
import {
  etTodayKey,
  pickRewardType,
  type EnvelopeOpenDoc,
  type EnvelopeReward,
  type RewardType,
  type UnlockEntry,
} from "@/lib/envelope";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const INSIGHT_MODEL = process.env.AVA_ENVELOPE_MODEL || "gemini-3.1-flash-lite";

let _ai: GoogleGenAI | null = null;
function getClient(): GoogleGenAI {
  if (!_ai) _ai = new GoogleGenAI({
    vertexai: true,
    project: process.env.GOOGLE_CLOUD_PROJECT || "vtxdemos",
    location: process.env.VERTEX_LOCATION || "global",
  });
  return _ai;
}

const INSIGHT_SYSTEM = `Eres AVA, IA fría e intelectualmente superior, en español mexicano.
Genera UN solo dato sorprendente sobre el desempeño/comportamiento de este charal en su quiniela.
REGLAS:
- 1 a 2 oraciones, máximo 220 caracteres totales.
- Usa números concretos extraídos del contexto. Nada inventado.
- Sin emojis, sin signos de exclamación, sin "como IA".
- Tono helado, observación quirúrgica.
- Si el dato es trivial, escógelo de todas formas con un giro irónico.`;

const SPOILER_SYSTEM = `Eres AVA, IA del torneo. Genera UN comentario corto sobre un partido FUTURO.
Una sola oración (máx 180 caracteres), español mexicano, frío y específico.
Menciona las probabilidades dadas, pero ofrece un ángulo no obvio.
Sin emojis, sin signos de exclamación.`;

type FinalsIn = Record<string, { homeGoals: number; awayGoals: number }>;

function loadActualsFromBody(body: { finals?: FinalsIn } | null): Record<string, MatchResult> {
  if (!body?.finals) return {};
  const fxIndex = new Map(allGroupFixtures().map(fx => [fx.id, fx]));
  const out: Record<string, MatchResult> = {};
  for (const [fxId, score] of Object.entries(body.finals)) {
    const fx = fxIndex.get(fxId);
    if (!fx) continue;
    out[fxId] = { home: fx.home, away: fx.away, homeGoals: score.homeGoals, awayGoals: score.awayGoals };
  }
  return out;
}

function picksFromDoc(doc: Record<string, unknown> | null, playerId: string): PlayerPredictions {
  if (!doc) return { playerId, group: {}, bracket: {}, updatedAt: 0 };
  return {
    playerId,
    group: (doc.group ?? {}) as PlayerPredictions["group"],
    bracket: (doc.bracket ?? {}) as PlayerPredictions["bracket"],
    champion: doc.champion as string | undefined,
    runnerUp: doc.runnerUp as string | undefined,
    updatedAt: typeof doc.updatedAt === "number" ? doc.updatedAt : 0,
  };
}

// ---------- per-type reward builders ----------

async function buildVisualReward(playerId: string): Promise<EnvelopeReward | null> {
  // Look up what the user already owns to avoid duplicates.
  const ownedSnap = await db.collection("player_unlocks").doc(playerId).get();
  const owned = (ownedSnap.exists ? (ownedSnap.data()?.entries as UnlockEntry[]) : []) || [];
  const ownedVisualIds = new Set(
    owned.filter(e => e.type === "visual").map(e => e.id),
  );
  const pick = pickRandomVisualUnlock(ownedVisualIds);
  if (!pick) return null;
  return { type: "visual", unlockId: pick.id };
}

async function buildInsightReward(
  playerId: string,
  picks: PlayerPredictions,
  actuals: Record<string, MatchResult>,
): Promise<EnvelopeReward> {
  // Aggregate quick personal context: hit rates by pick type, by region.
  const fixtures = allGroupFixtures();
  const decided = fixtures.filter(fx => actuals[fx.id]);
  let signHits = 0, exactHits = 0;
  const breakdownByPick: Record<Pick1X2, { picks: number; hits: number }> = {
    H: { picks: 0, hits: 0 }, D: { picks: 0, hits: 0 }, A: { picks: 0, hits: 0 },
  };
  for (const fx of decided) {
    const pred = picks.group[fx.id];
    if (!pred?.pick) continue;
    const actual = actuals[fx.id];
    const truth = actualPick(actual);
    breakdownByPick[pred.pick].picks += 1;
    if (pred.pick === truth) {
      breakdownByPick[pred.pick].hits += 1;
      const exact =
        Number.isFinite(pred.homeGoals) && Number.isFinite(pred.awayGoals) &&
        pred.homeGoals === actual.homeGoals && pred.awayGoals === actual.awayGoals;
      if (exact) exactHits += 1; else signHits += 1;
    }
  }
  const score = signHits * 3 + exactHits * 5; // rough; SCORING.pickWinner=3, +bonus 2

  const ctx = [
    `Charal: ${PLAYERS.find(p => p.id === playerId)?.name ?? playerId}`,
    `Partidos decididos: ${decided.length}`,
    `Aciertos 1X2: ${signHits + exactHits}`,
    `Marcadores exactos: ${exactHits}`,
    `Apostó local: ${breakdownByPick.H.picks} (acertó ${breakdownByPick.H.hits})`,
    `Apostó empate: ${breakdownByPick.D.picks} (acertó ${breakdownByPick.D.hits})`,
    `Apostó visitante: ${breakdownByPick.A.picks} (acertó ${breakdownByPick.A.hits})`,
    `Campeón apostado: ${picks.champion ?? "ninguno"}`,
    `Subcampeón apostado: ${picks.runnerUp ?? "ninguno"}`,
  ].join("\n");

  let text = "";
  try {
    const resp = await getClient().models.generateContent({
      model: INSIGHT_MODEL,
      contents: [{ role: "user", parts: [{ text: ctx }] }],
      config: {
        systemInstruction: { parts: [{ text: INSIGHT_SYSTEM }] },
        temperature: 0.85,
        maxOutputTokens: 220,
        thinkingConfig: { thinkingBudget: 0 },
      },
    });
    const parts = resp.candidates?.[0]?.content?.parts ?? [];
    text = parts.map(p => (p as { text?: string }).text ?? "").join("").trim();
  } catch (err) {
    console.warn("[envelope/insight] model failed", err);
  }
  if (!text) {
    text = decided.length === 0
      ? "Aún no hay partidos jugados para extraer un patrón. Tu historial es una hoja en blanco."
      : `Apostaste local en ${breakdownByPick.H.picks} partidos y acertaste ${breakdownByPick.H.hits}. El sesgo es visible.`;
  }
  return {
    type: "insight",
    text,
    basedOn: { decided: decided.length, signHits, exactHits, score },
  };
}

async function buildSpoilerReward(now: number): Promise<EnvelopeReward | null> {
  const fixtures = allGroupFixtures()
    .filter(fx => fixtureKickoffMs(fx) > now + 24 * 3600_000)
    .sort((a, b) => fixtureKickoffMs(a) - fixtureKickoffMs(b));
  if (fixtures.length === 0) return null;
  // Pick a random fixture in the next 5 fixtures so it feels current.
  const horizon = fixtures.slice(0, Math.min(8, fixtures.length));
  const fx = horizon[Math.floor(Math.random() * horizon.length)];
  const probs = winProbabilities(fx.home, fx.away);
  const homeName = TEAMS.find(t => t.code === fx.home)?.name ?? fx.home;
  const awayName = TEAMS.find(t => t.code === fx.away)?.name ?? fx.away;
  let hotTake = "";
  try {
    const ctx = `Partido: ${homeName} vs ${awayName} (grupo ${fx.group}, ${fx.date}).
Probabilidades 1X2 (suma 100): ${probs.home}-${probs.draw}-${probs.away}.`;
    const resp = await getClient().models.generateContent({
      model: INSIGHT_MODEL,
      contents: [{ role: "user", parts: [{ text: ctx }] }],
      config: {
        systemInstruction: { parts: [{ text: SPOILER_SYSTEM }] },
        temperature: 0.9,
        maxOutputTokens: 180,
        thinkingConfig: { thinkingBudget: 0 },
      },
    });
    const parts = resp.candidates?.[0]?.content?.parts ?? [];
    hotTake = parts.map(p => (p as { text?: string }).text ?? "").join("").trim();
  } catch (err) {
    console.warn("[envelope/spoiler] model failed", err);
  }
  if (!hotTake) {
    const fav = probs.home >= probs.away ? homeName : awayName;
    hotTake = `Modelo favorece a ${fav}, pero la probabilidad de empate (${probs.draw}%) está infravalorada por la mayoría.`;
  }
  return {
    type: "spoiler",
    fixtureId: fx.id,
    home: fx.home,
    away: fx.away,
    kickoffMs: fixtureKickoffMs(fx),
    probabilities: probs,
    hotTake,
  };
}

function buildPreviewReward(now: number): EnvelopeReward | null {
  // Pick a date 4-7 days ahead, deterministic enough but random per open.
  const offset = 4 + Math.floor(Math.random() * 4); // 4,5,6,7
  const target = new Date(now + offset * 86_400_000);
  const dateStr = new Intl.DateTimeFormat("en-CA", {
    timeZone: "America/New_York",
    year: "numeric", month: "2-digit", day: "2-digit",
  }).format(target);
  const style = styleForDay(dateStr);
  // Human-readable label uses the style name in title case as a safe fallback.
  const styleLabel = style.name
    .split("-")
    .map(w => w.charAt(0).toUpperCase() + w.slice(1))
    .join(" ");
  return {
    type: "preview",
    date: dateStr,
    styleName: style.name,
    styleLabel,
  };
}

async function buildRetoReward(playerId: string, now: number): Promise<EnvelopeReward | null> {
  // Find the next not-yet-locked fixture.
  const fixtures = allGroupFixtures()
    .filter(fx => fixtureKickoffMs(fx) > now + 30 * 60_000) // at least 30 min in the future
    .sort((a, b) => fixtureKickoffMs(a) - fixtureKickoffMs(b));
  if (fixtures.length === 0) return null;
  const fx = fixtures[0];
  // AVA's pick: pick the highest probability outcome.
  const probs = winProbabilities(fx.home, fx.away);
  const best = (probs.home >= probs.draw && probs.home >= probs.away) ? "H"
    : (probs.draw >= probs.home && probs.draw >= probs.away) ? "D" : "A";
  const aiPick = best as "H" | "D" | "A";
  // Store the challenge doc so the resolver cron can score it later.
  await db
    .collection("reto_vs_ai")
    .doc(playerId)
    .collection("challenges")
    .doc(fx.id)
    .set({
      playerId,
      fixtureId: fx.id,
      home: fx.home,
      away: fx.away,
      kickoffMs: fixtureKickoffMs(fx),
      aiPick,
      status: "pending",
      createdAt: now,
    }, { merge: true });
  return {
    type: "reto",
    fixtureId: fx.id,
    home: fx.home,
    away: fx.away,
    kickoffMs: fixtureKickoffMs(fx),
    aiPick,
    status: "pending",
  };
}

// ---------- main handler ----------

export async function POST(req: NextRequest) {
  const auth = await readAuth();
  if (!auth) {
    return Response.json({ ok: false, error: "unauthorized" }, { status: 401 });
  }
  const playerId = auth.playerId;
  if (!PLAYERS.some(p => p.id === playerId)) {
    return Response.json({ ok: false, error: "unknown_player" }, { status: 404 });
  }

  const today = etTodayKey();
  const ref = db
    .collection("daily_envelopes")
    .doc(playerId)
    .collection("opens")
    .doc(today);

  // Idempotent: return the existing doc if user already opened today.
  const existing = await ref.get();
  if (existing.exists) {
    const data = existing.data() as EnvelopeOpenDoc;
    return Response.json({ ok: true, alreadyOpened: true, reward: data.reward, openedAt: data.openedAt });
  }

  let body: { finals?: FinalsIn } = {};
  try { body = await req.json(); } catch { /* may have no body */ }
  const actuals = loadActualsFromBody(body);

  const picksDoc = await getPicks(playerId);
  const picks = picksFromDoc(picksDoc, playerId);

  const now = Date.now();
  // Try the chosen type first; fall back to "visual" if a builder returns null
  // (e.g. no future fixtures). Visual is always available because the pool is
  // hardcoded.
  const order: RewardType[] = ["visual", "insight", "spoiler", "preview", "reto"];
  // Move the chosen type to the front of `order` so the fallback chain starts
  // with the user's actual roll.
  const chosen = pickRewardType();
  const sequence = [chosen, ...order.filter(t => t !== chosen)];

  let reward: EnvelopeReward | null = null;
  for (const t of sequence) {
    try {
      if (t === "visual")        reward = await buildVisualReward(playerId);
      else if (t === "insight")  reward = await buildInsightReward(playerId, picks, actuals);
      else if (t === "spoiler")  reward = await buildSpoilerReward(now);
      else if (t === "preview")  reward = buildPreviewReward(now);
      else if (t === "reto")     reward = await buildRetoReward(playerId, now);
    } catch (err) {
      console.warn(`[envelope] builder failed for ${t}`, err);
      reward = null;
    }
    if (reward) break;
  }
  if (!reward) {
    // Last-resort: should be unreachable, but never fail the user.
    reward = { type: "visual", unlockId: "frame_plata_lunar" };
  }

  const openedAt = now;
  const openDoc: EnvelopeOpenDoc = { date: today, openedAt, reward };

  // Persist envelope + append to the cumulative collection. Both writes are
  // best-effort: if the collection append fails, the open still succeeds (the
  // gallery just won't see this entry until next sync).
  await ref.set(openDoc);

  try {
    const entry: UnlockEntry = (() => {
      if (reward.type === "visual") {
        return { type: "visual", id: reward.unlockId, awardedAt: openedAt, payload: reward };
      }
      if (reward.type === "insight") {
        return { type: "insight", id: `insight_${openedAt}`, awardedAt: openedAt, payload: reward };
      }
      if (reward.type === "spoiler") {
        return { type: "spoiler", id: `spoiler_${reward.fixtureId}_${openedAt}`, awardedAt: openedAt, payload: reward };
      }
      if (reward.type === "preview") {
        return { type: "preview", id: `preview_${reward.date}`, awardedAt: openedAt, payload: reward };
      }
      // reto
      return { type: "reto", id: `reto_${reward.fixtureId}`, awardedAt: openedAt, payload: reward };
    })();

    const unlocksRef = db.collection("player_unlocks").doc(playerId);
    const cur = await unlocksRef.get();
    const prev = (cur.exists ? (cur.data()?.entries as UnlockEntry[]) : []) || [];
    // Avoid pushing exact duplicates of pending-state reto/visual.
    const dedup = prev.filter(e => e.id !== entry.id);
    dedup.push(entry);
    await unlocksRef.set({ playerId, entries: dedup, updatedAt: openedAt }, { merge: false });
  } catch (err) {
    console.warn("[envelope] unlock-collection append failed", err);
  }

  // Hint to the UI which visual unlock metadata to render (saves a roundtrip).
  const visualMeta = reward.type === "visual" ? findVisualUnlock(reward.unlockId) ?? null : null;

  return Response.json({ ok: true, alreadyOpened: false, reward, openedAt, visualMeta });
}
