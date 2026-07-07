// POST /api/cron/charal-del-dia
//
// Computes the "Charal del Día" — the player who scored the most pool points
// from the fixtures that finished on the requested date (ET-zoned). Owner is
// expected to run it hourly via Cloud Scheduler; the endpoint is idempotent
// and short-circuits cheaply when the day isn't complete yet.
//
// Auth: gated by `x-cron-secret` (matches CRON_SECRET env).
// Query params:
//   ?date=today | yesterday | YYYY-MM-DD   (default: today, ET)
//   ?force=1                               (re-compute even if doc already written today)

import { NextRequest } from "next/server";
import { db } from "@/lib/firestore-server";
import { allGroupFixtures } from "@/data/groups";
import { fetchScoreboard, groupStageRange, normalizeAbbr } from "@/lib/espn";
import { PLAYERS, AI_PLAYER_ID } from "@/data/players";
import { getPicks } from "@/lib/predictions-server";
import { SCORING } from "@/data/tournament";
import { sendPushToAll } from "@/lib/push-server";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";
export const maxDuration = 120;

const COLLECTION = "daily_mvp";

type StoredGroupPick = { pick?: "H" | "D" | "A"; homeGoals?: number; awayGoals?: number };
type StoredPicks = { group?: Record<string, StoredGroupPick> } | null;

type MvpDoc = {
  date: string;
  playerId: string;
  name: string;
  points: number;
  pickedExact: number;
  pickedSign: number;
  computedAt: number;
  detail: string;
};

function etDate(d = new Date()): string {
  return new Intl.DateTimeFormat("en-CA", {
    timeZone: "America/New_York",
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  }).format(d);
}

function shiftEt(dateStr: string, deltaDays: number): string {
  const anchor = new Date(`${dateStr}T12:00:00Z`).getTime();
  return etDate(new Date(anchor + deltaDays * 86_400_000));
}

function resolveDateParam(raw: string | null): string {
  if (!raw) return etDate();
  if (raw === "today") return etDate();
  if (raw === "yesterday") return shiftEt(etDate(), -1);
  if (/^\d{4}-\d{2}-\d{2}$/.test(raw)) return raw;
  return etDate();
}

function sideOf(homeGoals: number, awayGoals: number): "H" | "D" | "A" {
  if (homeGoals > awayGoals) return "H";
  if (homeGoals < awayGoals) return "A";
  return "D";
}

type DateFinal = { fixtureId: string; homeGoals: number; awayGoals: number };

// Resolves finals for a given ET date by intersecting ESPN's scoreboard with
// our static fixture list. Returns ONLY post-game fixtures whose ET calendar
// date matches the requested date.
async function loadFinalsForEtDate(dateStr: string): Promise<DateFinal[]> {
  const fixtures = allGroupFixtures().filter(fx => fx.date === dateStr);
  if (fixtures.length === 0) return [];
  const fxByPair = new Map<string, typeof fixtures[number]>();
  for (const fx of fixtures) {
    fxByPair.set(`${fx.home}-${fx.away}`, fx);
    fxByPair.set(`${fx.away}-${fx.home}`, fx);
  }
  const sb = await fetchScoreboard(groupStageRange(), "fifa.world").catch(() => null);
  if (!sb?.events) return [];
  const out: DateFinal[] = [];
  const seen = new Set<string>();
  for (const e of sb.events) {
    if (e.status.type.state !== "post") continue;
    const c = e.competitions[0];
    const h = c.competitors.find(cp => cp.homeAway === "home");
    const a = c.competitors.find(cp => cp.homeAway === "away");
    if (!h || !a) continue;
    const hCode = normalizeAbbr(h.team.abbreviation);
    const aCode = normalizeAbbr(a.team.abbreviation);
    const fx = fxByPair.get(`${hCode}-${aCode}`);
    if (!fx || fx.date !== dateStr) continue;
    if (seen.has(fx.id)) continue;
    const hg = Number(h.score);
    const ag = Number(a.score);
    if (!Number.isFinite(hg) || !Number.isFinite(ag)) continue;
    const ourHomeIsEspnHome = fx.home === hCode;
    out.push({
      fixtureId: fx.id,
      homeGoals: ourHomeIsEspnHome ? hg : ag,
      awayGoals: ourHomeIsEspnHome ? ag : hg,
    });
    seen.add(fx.id);
  }
  return out;
}

type Scored = {
  playerId: string;
  name: string;
  points: number;
  pickedExact: number;
  pickedSign: number;
  hits: Array<{ fixtureId: string; correct: boolean; exact: boolean }>;
};

function scoreForDate(
  picks: StoredPicks,
  finals: DateFinal[],
): Pick<Scored, "points" | "pickedExact" | "pickedSign" | "hits"> {
  let points = 0;
  let pickedExact = 0;
  let pickedSign = 0;
  const hits: Scored["hits"] = [];
  if (!picks?.group) return { points, pickedExact, pickedSign, hits };
  for (const f of finals) {
    const pred = picks.group[f.fixtureId];
    if (!pred?.pick) continue;
    const actual = sideOf(f.homeGoals, f.awayGoals);
    const correct = pred.pick === actual;
    if (!correct) {
      hits.push({ fixtureId: f.fixtureId, correct: false, exact: false });
      continue;
    }
    points += SCORING.pickWinner;
    const exact =
      Number.isFinite(pred.homeGoals) && Number.isFinite(pred.awayGoals) &&
      pred.homeGoals === f.homeGoals && pred.awayGoals === f.awayGoals;
    if (exact) {
      points += SCORING.exactScoreBonus;
      pickedExact += 1;
    } else {
      pickedSign += 1;
    }
    hits.push({ fixtureId: f.fixtureId, correct: true, exact });
  }
  return { points, pickedExact, pickedSign, hits };
}

export async function POST(req: NextRequest) {
  const expected = process.env.CRON_SECRET;
  if (!expected) {
    return Response.json({ ok: false, error: "cron_disabled" }, { status: 503 });
  }
  if (req.headers.get("x-cron-secret") !== expected) {
    return Response.json({ ok: false, error: "forbidden" }, { status: 403 });
  }

  const url = new URL(req.url);
  const dateStr = resolveDateParam(url.searchParams.get("date"));
  const force = url.searchParams.get("force") === "1";

  // 1) Are there fixtures on this date at all?
  const fixturesToday = allGroupFixtures().filter(fx => fx.date === dateStr);
  if (fixturesToday.length === 0) {
    return Response.json({ ok: true, ready: false, date: dateStr, reason: "no_fixtures" });
  }

  // 2) Idempotent short-circuit unless force.
  const docRef = db.collection(COLLECTION).doc(dateStr);
  if (!force) {
    const existing = await docRef.get().catch(() => null);
    if (existing?.exists) {
      return Response.json({ ok: true, ready: true, date: dateStr, skipped: "already_computed" });
    }
  }

  // 3) Pull finals. Require ALL of today's fixtures to be FINAL before
  //    committing — otherwise it's not yet "the day's" winner.
  const finals = await loadFinalsForEtDate(dateStr);
  if (finals.length < fixturesToday.length) {
    return Response.json({
      ok: true,
      ready: false,
      date: dateStr,
      finalsCount: finals.length,
      expected: fixturesToday.length,
    });
  }

  // 4) Pull every (human) player's picks and score them for today only.
  const humans = PLAYERS.filter(p => p.id !== AI_PLAYER_ID);
  const scored: Scored[] = await Promise.all(
    humans.map(async p => {
      const picks = (await getPicks(p.id).catch(() => null)) as StoredPicks;
      const s = scoreForDate(picks, finals);
      return { playerId: p.id, name: p.name, ...s };
    }),
  );

  // Anyone with at least one pick on a today fixture counts; otherwise skip.
  const competitors = scored.filter(s => s.hits.length > 0);
  if (competitors.length === 0) {
    return Response.json({ ok: true, ready: true, date: dateStr, reason: "no_picks" });
  }

  // 5) Tie-break: points desc → exacts desc → alphabetic asc.
  competitors.sort((a, b) =>
    b.points - a.points ||
    b.pickedExact - a.pickedExact ||
    a.name.localeCompare(b.name),
  );
  const winner = competitors[0];

  // 6) Compose a short "detail" summary for the push body.
  const correctCount = winner.hits.filter(h => h.correct).length;
  const detail = `${correctCount}/${winner.hits.length} aciertos${winner.pickedExact > 0 ? ` · ${winner.pickedExact} exacto${winner.pickedExact === 1 ? "" : "s"}` : ""}`;

  const doc: MvpDoc = {
    date: dateStr,
    playerId: winner.playerId,
    name: winner.name,
    points: winner.points,
    pickedExact: winner.pickedExact,
    pickedSign: winner.pickedSign,
    computedAt: Date.now(),
    detail,
  };
  await docRef.set(doc, { merge: false });

  // 7) Fanout push (best-effort; failures don't poison the cron).
  let pushResult: { sent: number; pruned: number; failed: number } = { sent: 0, pruned: 0, failed: 0 };
  try {
    pushResult = await sendPushToAll({
      title: `👑 Caliente del día: ${winner.name} +${winner.points}`,
      body: detail,
      url: "/leaderboard",
      tag: `daily-mvp-${dateStr}`,
    });
  } catch (e) {
    console.warn("[charal-del-dia] push fanout failed", e);
  }

  return Response.json({
    ok: true,
    ready: true,
    date: dateStr,
    playerId: winner.playerId,
    points: winner.points,
    push: pushResult,
  });
}
