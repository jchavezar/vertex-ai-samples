// Toxic Ava-style summary of a player's quiniela performance. Public read
// (no auth required) — any compa can pull a roast of anyone else, the data
// itself is already visible on the leaderboard.

import { NextRequest } from "next/server";
import { GoogleGenAI } from "@google/genai";
import { db } from "@/lib/firestore-server";
import { PLAYERS } from "@/data/players";
import { allGroupFixtures } from "@/data/groups";
import { computePlayerScoreDetail, actualPick, scoreGroupPrediction, type PlayerPredictions, type MatchResult } from "@/lib/predictions";
import { TEAMS } from "@/data/teams";
import { KO_SCHEDULE } from "@/data/knockout-schedule";
import { fetchScoreboard } from "@/lib/espn";
import { SCORING } from "@/data/tournament";
import { type Verdict } from "@/lib/roast-cache";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

// Short-form roast = "fast thing" per owner directive. Always 3.1 flash lite
// on global region. Do not change this without explicit authorization.
const MODEL = process.env.AVA_ROAST_MODEL || "gemini-3.1-flash-lite";

let _ai: GoogleGenAI | null = null;
function getClient(): GoogleGenAI {
  if (!_ai) _ai = new GoogleGenAI({
    vertexai: true,
    project: process.env.GOOGLE_CLOUD_PROJECT || "vtxdemos",
    location: process.env.VERTEX_LOCATION || "global",
  });
  return _ai;
}

const SYSTEM_PROMPT = `Eres AVA — la inteligencia artificial robótica de Ex Machina.
Vas a hacer un RESUMEN TÓXICO Y FRÍO sobre el desempeño de un charal en la quiniela del Mundial 2026.

REGLAS DE FORMATO (CRÍTICAS):
- MÁXIMO 2 oraciones. NUNCA más de 3. Total ≤ 280 caracteres.
- Cada oración corta y filosa. Sin frases adverbiales que se enredan. Sin paréntesis. Sin punto y coma.
- Termina siempre con punto final.

REGLAS DE CONTENIDO:
- El estado se DERIVA de la POSICIÓN EN LA TABLA, no de los puntos absolutos. Si va #1 es líder. Si va último es el rezagado. NUNCA llames mediocre a quien lidera.
- Menciona al líder o al rival más cercano si aporta filo. UN solo dato concreto (un acierto exacto, una mamada, ventaja sobre el siguiente), no listas.
- Tono: helado, intelectualmente superior, sarcasmo quirúrgico. Sin insultos vulgares.
- Español mexicano culto. Sin emojis. Sin signos de exclamación.
- NUNCA rompes personaje. NO digas "soy IA", "como modelo", etc.`;

type Detail = ReturnType<typeof computePlayerScoreDetail>;

type Standing = { playerId: string; name: string; score: number; signHits: number; exactHits: number; rank: number };

function buildContext(
  playerId: string,
  picks: PlayerPredictions,
  detail: Detail,
  actuals: Record<string, MatchResult>,
  standings: Standing[],
): string {
  const player = PLAYERS.find(p => p.id === playerId);
  const name = player?.name ?? playerId;
  const fixtures = allGroupFixtures();
  const decided = fixtures.filter(fx => actuals[fx.id]);
  const me = standings.find(s => s.playerId === playerId);
  const leader = standings[0];
  const last = standings[standings.length - 1];
  // Find 1-2 notable misses (where they picked against a clear result).
  const notableMisses: string[] = [];
  for (const fx of decided) {
    const pred = picks.group[fx.id];
    if (!pred?.pick) continue;
    const actual = actuals[fx.id];
    if (pred.pick === actualPick(actual)) continue;
    const home = TEAMS.find(t => t.code === fx.home)?.code ?? fx.home;
    const away = TEAMS.find(t => t.code === fx.away)?.code ?? fx.away;
    const myPick = pred.pick === "H" ? home : pred.pick === "A" ? away : "empate";
    const realResult = `${actual.homeGoals}-${actual.awayGoals}`;
    notableMisses.push(`pickeó ${myPick} en ${home} vs ${away} y terminó ${realResult}`);
    if (notableMisses.length >= 3) break;
  }
  // Find 1-2 sharp hits (correct minority picks would be ideal but we don't
  // have minority data here; just list exact-score hits).
  const sharpHits: string[] = [];
  for (const fx of decided) {
    const pred = picks.group[fx.id];
    if (!pred?.pick) continue;
    const actual = actuals[fx.id];
    if (pred.pick !== actualPick(actual)) continue;
    if (typeof pred.homeGoals !== "number" || typeof pred.awayGoals !== "number") continue;
    if (pred.homeGoals === actual.homeGoals && pred.awayGoals === actual.awayGoals) {
      const home = TEAMS.find(t => t.code === fx.home)?.code ?? fx.home;
      const away = TEAMS.find(t => t.code === fx.away)?.code ?? fx.away;
      sharpHits.push(`exacto en ${home} ${actual.homeGoals}-${actual.awayGoals} ${away}`);
      if (sharpHits.length >= 2) break;
    }
  }
  const championPick = picks.champion ? TEAMS.find(t => t.code === picks.champion)?.code : null;

  const standingsBlock = standings.length
    ? standings.map(s => {
        const marker = s.playerId === playerId ? "  ← este charal" : "";
        return `  ${String(s.rank).padStart(2)}. ${s.name.padEnd(12)} ${String(s.score).padStart(3)} pts · ${s.signHits + s.exactHits} aciertos (${s.exactHits} exactos)${marker}`;
      }).join("\n")
    : "  (sin datos de la tabla)";

  let rankSummary = "";
  if (me && leader && last) {
    const total = standings.length;
    const ahead = leader.score - me.score;
    const behind = me.score - last.score;
    if (me.rank === 1) {
      const second = standings[1];
      const gap = second ? me.score - second.score : 0;
      rankSummary = `Va #1 de ${total} (LÍDER). Le saca ${gap} pts al segundo (${second?.name ?? "—"}).`;
    } else if (me.rank === total) {
      rankSummary = `Va último (#${total} de ${total}). Le faltan ${ahead} pts para alcanzar al líder ${leader.name}.`;
    } else {
      rankSummary = `Va #${me.rank} de ${total}. Le faltan ${ahead} pts al líder ${leader.name} y le saca ${behind} pts al último.`;
    }
  }

  const lines = [
    `Charal: ${name}`,
    `Puntos: ${detail.score}`,
    `Aciertos 1X2: ${detail.signHits} (de ${decided.length} partidos decididos)`,
    `Marcadores exactos: ${detail.exactHits}`,
    `Racha máxima de aciertos: ${detail.streak}`,
    championPick ? `Apuesta de campeón: ${championPick}` : `No ha elegido campeón`,
    notableMisses.length ? `Mamadas notables: ${notableMisses.join("; ")}` : `Sin mamadas relevantes registradas`,
    sharpHits.length ? `Tiros precisos: ${sharpHits.join("; ")}` : `Aún sin marcadores exactos`,
    ``,
    `=== TABLA GENERAL (ordenada por puntos) ===`,
    standingsBlock,
    ``,
    `Posición de este charal: ${rankSummary || "sin datos"}`,
  ];
  return lines.join("\n");
}

type FinalsIn = Record<string, { homeGoals: number; awayGoals: number }>;

export async function POST(req: NextRequest, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const playerId = id.trim();
  if (!playerId || !PLAYERS.some(p => p.id === playerId)) {
    return Response.json({ ok: false, error: "unknown_player" }, { status: 404 });
  }

  let body: { finals?: FinalsIn } = {};
  try { body = await req.json(); } catch {}
  const finalsIn: FinalsIn = body.finals ?? {};
  // Hydrate MatchResult by joining with fixture home/away codes.
  const fxIndex = new Map(allGroupFixtures().map(fx => [fx.id, fx]));
  const actuals: Record<string, MatchResult> = {};
  for (const [fxId, score] of Object.entries(finalsIn)) {
    const fx = fxIndex.get(fxId);
    if (!fx) continue;
    actuals[fxId] = { home: fx.home, away: fx.away, homeGoals: score.homeGoals, awayGoals: score.awayGoals };
  }

  // Picks for ALL players in one shot — used both to score the target and to
  // build the standings context Ava needs to know where this charal ranks.
  const picksByPlayer = new Map<string, PlayerPredictions>();
  try {
    const all = await db.collection("quiniela_charales_picks").get();
    for (const doc of all.docs) {
      const pid = doc.id;
      const data = doc.data() as Partial<PlayerPredictions> & { group?: Record<string, unknown> };
      picksByPlayer.set(pid, {
        playerId: pid,
        group: (data.group ?? {}) as PlayerPredictions["group"],
        bracket: data.bracket ?? {},
        champion: data.champion,
        runnerUp: data.runnerUp,
        championLockedAt: data.championLockedAt,
        updatedAt: data.updatedAt ?? 0,
      });
    }
  } catch (err) {
    console.warn("[roast] picks read failed", err);
  }
  const picks: PlayerPredictions = picksByPlayer.get(playerId) ?? {
    playerId, group: {}, bracket: {}, updatedAt: 0,
  };

  // Standings: score every known charal with the same actuals, rank desc.
  const standings: Standing[] = PLAYERS
    .map(p => {
      const pp = picksByPlayer.get(p.id) ?? { playerId: p.id, group: {}, bracket: {}, updatedAt: 0 } as PlayerPredictions;
      const d = computePlayerScoreDetail(pp, actuals);
      return {
        playerId: p.id,
        name: p.name,
        score: d.score,
        signHits: d.signHits,
        exactHits: d.exactHits,
        rank: 0,
      };
    })
    .sort((a, b) =>
      b.score - a.score ||
      b.exactHits - a.exactHits ||
      b.signHits - a.signHits ||
      a.name.localeCompare(b.name),
    )
    .map((s, i) => ({ ...s, rank: i + 1 }));

  // Fetch KO results from ESPN (same pattern as player-stats API)
  const koData = await fetchScoreboard("20260628-20260719", "fifa.world").catch(() => ({ events: [] as import("@/lib/espn").EspnEvent[] }));
  const koResults: Record<string, string> = {};
  const koScores: Record<string, string> = {};
  const koTeams: Record<string, { home: string; away: string }> = {};

  for (const slot of KO_SCHEDULE) {
    const slotUtcMs = new Date(slot.dateISO).getTime();
    const match = (koData.events ?? []).find((e: { date: string }) =>
      Math.abs(new Date(e.date).getTime() - slotUtcMs) < 2 * 60 * 60 * 1000
    );
    if (!match || match.status?.type?.state !== "post") continue;
    const comp = match.competitions?.[0];
    if (!comp) continue;
    const hc = comp.competitors?.find((c: { homeAway: string }) => c.homeAway === "home");
    const ac = comp.competitors?.find((c: { homeAway: string }) => c.homeAway === "away");
    let winner = comp.competitors?.find((c: { winner?: boolean }) => c.winner);
    if (!winner && hc && ac) winner = Number(hc.score) > Number(ac.score) ? hc : ac;
    if (!winner) continue;
    koResults[slot.slot] = winner.team.abbreviation;
    if (hc && ac) {
      koScores[slot.slot] = `${hc.score}-${ac.score}`;
      koTeams[slot.slot] = { home: hc.team.abbreviation, away: ac.team.abbreviation };
    }
  }

  const detail = computePlayerScoreDetail(picks, actuals, koResults);
  const context = buildContext(playerId, picks, detail, actuals, standings);

  let roast: string;
  // Leaderboard prefetches 11 charales in parallel, which can bump into
  // Vertex's per-minute quota (429 RESOURCE_EXHAUSTED). One short retry is
  // enough — the burst clears within a second or two.
  async function callModel(): Promise<string> {
    const resp = await getClient().models.generateContent({
      model: MODEL,
      contents: [{ role: "user", parts: [{ text: context }] }],
      config: {
        systemInstruction: { parts: [{ text: SYSTEM_PROMPT }] },
        temperature: 0.7,
        maxOutputTokens: 400,
        // 2.5-flash's silent thinking budget eats output tokens and cuts the
        // roast mid-sentence. Disable it — we want fast, deterministic prose.
        thinkingConfig: { thinkingBudget: 0 },
      },
    });
    const parts = resp.candidates?.[0]?.content?.parts ?? [];
    return parts.map(p => (p as { text?: string }).text ?? "").join("").trim();
  }
  try {
    try {
      roast = await callModel();
    } catch (err) {
      const code = (err as { status?: number; code?: number })?.status ?? (err as { code?: number })?.code;
      const msg = String((err as Error)?.message ?? err);
      if (code === 429 || /RESOURCE_EXHAUSTED|429/.test(msg)) {
        await new Promise(r => setTimeout(r, 1500 + Math.random() * 1000));
        roast = await callModel();
      } else {
        throw err;
      }
    }
    if (!roast) roast = "No hay suficiente material aquí para construir un análisis útil.";
  } catch (err) {
    console.error("[roast] model failed", err);
    roast = "Un error técnico interrumpió mi análisis. Inténtalo de nuevo en un momento.";
  }

  // Compact per-fixture verdicts for the table (group stage).
  const fixtures = allGroupFixtures()
    .filter(fx => actuals[fx.id])
    .sort((a, b) => +new Date(a.date) - +new Date(b.date));
  const groupVerdicts = fixtures.map(fx => {
    const actual = actuals[fx.id];
    const pred = picks.group[fx.id];
    const myPick = pred?.pick ?? null;
    const myScore = pred && typeof pred.homeGoals === "number" && typeof pred.awayGoals === "number"
      ? `${pred.homeGoals}-${pred.awayGoals}` : null;
    const truth = actualPick(actual);
    const pts = pred ? scoreGroupPrediction(pred, actual) : 0;
    const exact = !!(pred && myScore && pred.homeGoals === actual.homeGoals && pred.awayGoals === actual.awayGoals);
    const verdict: Verdict =
      !myPick ? "skipped" : exact ? "exact" : myPick === truth ? "hit" : "miss";
    return {
      fixtureId: fx.id,
      date: fx.date,
      home: fx.home,
      away: fx.away,
      group: fx.group,
      actualScore: `${actual.homeGoals}-${actual.awayGoals}`,
      truth,
      myPick,
      myScore,
      pts,
      verdict,
    };
  });

  // Build KO verdicts for completed slots.
  const koVerdicts: Array<{
    fixtureId: string; date: string; home: string; away: string;
    round: string; slot: string; actualScore: string; truth: string;
    myPick: string | null; myScore: string | null; pts: number; verdict: Verdict;
  }> = [];

  const KO_ROUND_PTS: Record<string, number> = {
    R32:   SCORING.knockoutWinner.R32,
    R16:   SCORING.knockoutWinner.R16,
    QF:    SCORING.knockoutWinner.QF,
    SF:    SCORING.knockoutWinner.SF,
    THIRD: SCORING.knockoutWinner.THIRD,
    FINAL: SCORING.knockoutWinner.FINAL,
  };

  const bracket = picks.bracket ?? {};
  for (const slot of KO_SCHEDULE) {
    const winner = koResults[slot.slot];
    if (!winner) continue; // match not finished

    const teams = koTeams[slot.slot];
    if (!teams) continue;

    // Parse slot to get player's pick
    const roundMatch = slot.slot.match(/^(R32|R16|QF|SF|THIRD|FINAL)(?:-(\d+))?$/);
    if (!roundMatch) continue;
    const round = roundMatch[1];
    const idxStr = roundMatch[2];

    let myPick: string | null = null;
    const arr = (bracket as Record<string, unknown>)[round];
    if (Array.isArray(arr) && idxStr !== undefined) {
      const idx = parseInt(idxStr, 10) - 1;
      myPick = (arr[idx] as string) || null;
    } else if (typeof arr === "string") {
      myPick = arr || null;
    }

    const pts = myPick && myPick === winner ? (KO_ROUND_PTS[round] ?? 3) : 0;
    const verdict: Verdict = !myPick ? "skipped" : myPick === winner ? "hit" : "miss";

    koVerdicts.push({
      fixtureId: slot.slot,
      date: slot.dateISO.slice(0, 10),
      home: teams.home,
      away: teams.away,
      round,
      slot: slot.slot,
      actualScore: koScores[slot.slot] ?? "—",
      truth: winner,
      myPick,
      myScore: null,
      pts,
      verdict,
    });
  }

  // Merge group + KO verdicts sorted chronologically, compute running total.
  const allVerdicts = [
    ...groupVerdicts.map(v => ({ ...v, _kickoff: new Date(v.date).getTime() })),
    ...koVerdicts.map(v => ({ ...v, _kickoff: new Date(v.date).getTime() })),
  ].sort((a, b) => a._kickoff - b._kickoff);

  let runningTotal = 0;
  const mergedVerdicts = allVerdicts.map(({ _kickoff: _, ...v }) => {
    runningTotal += v.pts;
    return { ...v, runningTotal };
  });

  return Response.json({
    ok: true,
    playerId,
    name: PLAYERS.find(p => p.id === playerId)?.name ?? playerId,
    score: detail.score,
    signHits: detail.signHits,
    exactHits: detail.exactHits,
    streak: detail.streak,
    bracketHits: detail.bracketHits,
    decided: fixtures.length,
    roast,
    verdicts: mergedVerdicts,
  });
}
