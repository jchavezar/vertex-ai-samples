// GET /api/admin/ai-evolution — owner-only timeline of how the AI bot's picks
// have evolved over time. Reads the `ai_pick_history` collection (one entry
// per CHANGE the bot made), the bot's CURRENT pick payload, and the latest
// ESPN scoreboard for finished fixtures so we can grade old vs new picks.
//
// Returns three views computed off the same dataset:
//   1) `runs`       — snapshots grouped by their shared run `ts` (each cron
//                     run produces one bucket).
//   2) `perFixture` — every fixture the bot ever picked, with the full chain
//                     of snapshots and (when finished) the actual outcome.
//   3) `stats`      — aggregate metrics (changes/fixture, aggressiveness vs
//                     argmax, accuracy of changed vs never-changed picks).
//
// Gate: cookie playerId === "jesus" OR ADMIN_SECRET header. The page is
// noindex by virtue of being under /admin and we don't want random charales
// peeking at the bot's reasoning evolution.

import type { NextRequest } from "next/server";
import { readAuth } from "@/lib/auth-server";
import {
  listPickHistory,
  type AiPickSnapshot,
} from "@/lib/ai-state-server";
import { getPicks } from "@/lib/predictions-server";
import { AI_PLAYER_ID } from "@/data/players";
import { allGroupFixtures } from "@/data/groups";
import {
  fetchScoreboard,
  groupStageRange,
  normalizeAbbr,
  type EspnEvent,
} from "@/lib/espn";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const OWNER_ID = "jesus";

type Pick = "H" | "D" | "A";

type GroupPick = {
  pick?: Pick;
  homeGoals?: number;
  awayGoals?: number;
  reasoning?: string;
  confidence?: number;
  reasonerModel?: string;
  aiAt?: number;
};

type ActualResult = {
  pick: Pick;
  homeGoals: number;
  awayGoals: number;
  score: string;
};

type RunChange = {
  fixtureId: string;
  home: string;
  away: string;
  prevPick: Pick | null;
  newPick: Pick;
  prevScore: string | null;
  newScore: string;
  reasoning: string;
  confidence: number | null;
  source: string;
};

type RunBucket = {
  ts: number;
  changes: RunChange[];
  // total snapshots in this run, including "initial" entries that aren't a
  // change per se but mark the first time the bot picked a fixture
  total: number;
  initials: number;
};

type PerFixtureRow = {
  fixtureId: string;
  home: string;
  away: string;
  date: string;
  group: string;
  matchday: 1 | 2 | 3;
  snapshots: AiPickSnapshot[];
  currentPick?: Pick;
  currentScore?: string;
  changes: number;                              // # of times the H/D/A pick flipped
  actual?: ActualResult;
  initialPick?: Pick;                           // first pick the bot ever made
  initialCorrect?: boolean;
  finalCorrect?: boolean;
  verdict?: "exact" | "hit" | "miss";
};

type Stats = {
  totalFixtures: number;
  fixturesWithChanges: number;
  avgChangesPerFixture: number;
  aggressivenessScore: number;                  // % of CURRENT picks that disagree with argmax(blended)
  accuracyAll: number | null;
  accuracyChanged: number | null;               // accuracy on fixtures whose pick changed at least once
  accuracyStable: number | null;                // accuracy on fixtures whose pick never changed
  finishedFixtures: number;
};

type Payload = {
  ok: true;
  generatedAt: number;
  runs: RunBucket[];
  perFixture: PerFixtureRow[];
  stats: Stats;
};

function scoreStr(h: number | undefined, a: number | undefined): string | null {
  if (typeof h !== "number" || typeof a !== "number") return null;
  return `${h}-${a}`;
}

function argmax(p: { H: number; D: number; A: number } | undefined): Pick | null {
  if (!p) return null;
  const arr: Array<[Pick, number]> = [["H", p.H], ["D", p.D], ["A", p.A]];
  arr.sort((x, y) => y[1] - x[1]);
  return arr[0][0];
}

async function loadFinishedResults(): Promise<Map<string, ActualResult>> {
  const out = new Map<string, ActualResult>();
  const sb = await fetchScoreboard(groupStageRange(), "fifa.world").catch(() => null);
  if (!sb) return out;
  const fixtures = allGroupFixtures();
  const fxByPair = new Map<string, typeof fixtures[number]>();
  for (const fx of fixtures) {
    fxByPair.set(`${fx.home}-${fx.away}-${fx.date}`, fx);
    fxByPair.set(`${fx.away}-${fx.home}-${fx.date}`, fx);
  }
  const events: EspnEvent[] = sb.events ?? [];
  for (const e of events) {
    if (e.status.type.state !== "post") continue;
    const c = e.competitions[0];
    const h = c.competitors.find(cp => cp.homeAway === "home");
    const a = c.competitors.find(cp => cp.homeAway === "away");
    if (!h || !a) continue;
    const hCode = normalizeAbbr(h.team.abbreviation);
    const aCode = normalizeAbbr(a.team.abbreviation);
    const date = e.date.slice(0, 10);
    const fx = fxByPair.get(`${hCode}-${aCode}-${date}`);
    if (!fx) continue;
    const hg = Number(h.score);
    const ag = Number(a.score);
    if (!Number.isFinite(hg) || !Number.isFinite(ag)) continue;
    const ourHomeIsEspnHome = fx.home === hCode;
    const homeGoals = ourHomeIsEspnHome ? hg : ag;
    const awayGoals = ourHomeIsEspnHome ? ag : hg;
    const pick: Pick = homeGoals > awayGoals ? "H" : homeGoals < awayGoals ? "A" : "D";
    out.set(fx.id, { pick, homeGoals, awayGoals, score: `${homeGoals}-${awayGoals}` });
  }
  return out;
}

export async function GET(req: NextRequest) {
  const expected = process.env.ADMIN_SECRET;
  const secretOk = !!expected && req.headers.get("x-admin-secret") === expected;
  if (!secretOk) {
    const auth = await readAuth().catch(() => null);
    if (!auth) return Response.json({ ok: false, error: "unauthorized" }, { status: 401 });
    if (auth.playerId !== OWNER_ID) {
      return Response.json({ ok: false, error: "forbidden" }, { status: 403 });
    }
  }

  const fixtures = allGroupFixtures();
  const fxById = new Map(fixtures.map(fx => [fx.id, fx]));

  const [history, currentPayloadRaw, actuals] = await Promise.all([
    listPickHistory(undefined, 5000),
    getPicks(AI_PLAYER_ID),
    loadFinishedResults(),
  ]);

  const currentGroup = ((currentPayloadRaw as { group?: Record<string, GroupPick> } | null)?.group) ?? {};

  // ── Group snapshots by fixture (chronological asc) and by run ts ──────────
  const byFixture = new Map<string, AiPickSnapshot[]>();
  for (const s of history) {
    if (!s?.fixtureId) continue;
    const list = byFixture.get(s.fixtureId) ?? [];
    list.push(s);
    byFixture.set(s.fixtureId, list);
  }
  for (const [, list] of byFixture) {
    list.sort((a, b) => a.ts - b.ts);
  }

  // Group by run ts. Use the literal ts value as the bucket key — every
  // snapshot from the same sync() invocation already shares one Date.now().
  const runMap = new Map<number, RunBucket>();
  for (const s of history) {
    const ts = s.ts;
    if (!Number.isFinite(ts)) continue;
    let bucket = runMap.get(ts);
    if (!bucket) {
      bucket = { ts, changes: [], total: 0, initials: 0 };
      runMap.set(ts, bucket);
    }
    bucket.total += 1;
    const fx = fxById.get(s.fixtureId);
    const isInitial = s.source === "initial" || !s.prevPick;
    if (isInitial) {
      bucket.initials += 1;
      // We still surface initial entries so the run timeline isn't empty on
      // day 1, but call them out separately in the UI.
    }
    bucket.changes.push({
      fixtureId: s.fixtureId,
      home: fx?.home ?? "?",
      away: fx?.away ?? "?",
      prevPick: (s.prevPick as Pick | undefined) ?? null,
      newPick: s.pick,
      prevScore: null,                          // not stored; UI shows "—"
      newScore: scoreStr(s.homeGoals, s.awayGoals) ?? "",
      reasoning: s.reasoning ?? "",
      confidence: typeof s.confidence === "number" ? s.confidence : null,
      source: s.source ?? "sync",
    });
  }

  const runs: RunBucket[] = Array.from(runMap.values()).sort((a, b) => b.ts - a.ts);

  // ── Per-fixture rollup ────────────────────────────────────────────────────
  // We surface EVERY fixture that has either history OR a current pick, so
  // the admin can see fixtures the bot hasn't churned on too.
  const fixtureIds = new Set<string>([...byFixture.keys(), ...Object.keys(currentGroup)]);
  const perFixture: PerFixtureRow[] = [];
  let aggressiveCount = 0;
  let aggressiveDenom = 0;
  for (const fxId of fixtureIds) {
    const fx = fxById.get(fxId);
    if (!fx) continue;
    const snaps = byFixture.get(fxId) ?? [];
    const cur = currentGroup[fxId];
    const curPick = cur?.pick as Pick | undefined;
    const curScore = scoreStr(cur?.homeGoals, cur?.awayGoals) ?? undefined;
    // Count only changes in the H/D/A pick literal (score-only churn would
    // overstate "changes"). Initial doesn't count as a change.
    let changes = 0;
    for (let i = 1; i < snaps.length; i++) {
      if (snaps[i].pick !== snaps[i - 1].pick) changes += 1;
    }
    // First time the H/D/A pick was set (initial snapshot, when present).
    const initialPick = snaps[0]?.pick ?? curPick;
    const actual = actuals.get(fxId);
    let verdict: PerFixtureRow["verdict"] | undefined;
    let initialCorrect: boolean | undefined;
    let finalCorrect: boolean | undefined;
    if (actual && curPick) {
      finalCorrect = curPick === actual.pick;
      const exact = curScore && curScore === actual.score;
      verdict = finalCorrect ? (exact ? "exact" : "hit") : "miss";
    }
    if (actual && initialPick) {
      initialCorrect = initialPick === actual.pick;
    }
    // Aggressiveness — the bot disagreed with argmax(blended). Use the
    // latest snapshot's blendedProbs as the basis.
    const lastBlended = snaps[snaps.length - 1]?.blendedProbs;
    const am = argmax(lastBlended);
    if (am && curPick) {
      aggressiveDenom += 1;
      if (am !== curPick) aggressiveCount += 1;
    }
    perFixture.push({
      fixtureId: fxId,
      home: fx.home,
      away: fx.away,
      date: fx.date,
      group: fx.group,
      matchday: fx.matchday,
      snapshots: snaps,
      currentPick: curPick,
      currentScore: curScore,
      changes,
      actual,
      initialPick,
      initialCorrect,
      finalCorrect,
      verdict,
    });
  }
  perFixture.sort((a, b) => {
    if (b.changes !== a.changes) return b.changes - a.changes;
    return a.date.localeCompare(b.date);
  });

  // ── Stats roll-up ─────────────────────────────────────────────────────────
  const totalFixtures = perFixture.length;
  const fixturesWithChanges = perFixture.filter(r => r.changes > 0).length;
  const avgChangesPerFixture = totalFixtures > 0
    ? perFixture.reduce((acc, r) => acc + r.changes, 0) / totalFixtures
    : 0;
  const aggressivenessScore = aggressiveDenom > 0 ? aggressiveCount / aggressiveDenom : 0;

  const finished = perFixture.filter(r => !!r.actual && !!r.currentPick);
  const finishedFixtures = finished.length;
  const accuracyAll = finished.length > 0
    ? finished.filter(r => r.finalCorrect).length / finished.length
    : null;
  const changed = finished.filter(r => r.changes > 0);
  const stable = finished.filter(r => r.changes === 0);
  const accuracyChanged = changed.length > 0
    ? changed.filter(r => r.finalCorrect).length / changed.length
    : null;
  const accuracyStable = stable.length > 0
    ? stable.filter(r => r.finalCorrect).length / stable.length
    : null;

  const stats: Stats = {
    totalFixtures,
    fixturesWithChanges,
    avgChangesPerFixture,
    aggressivenessScore,
    accuracyAll,
    accuracyChanged,
    accuracyStable,
    finishedFixtures,
  };

  const payload: Payload = {
    ok: true,
    generatedAt: Date.now(),
    runs,
    perFixture,
    stats,
  };

  return Response.json(payload, {
    headers: { "Cache-Control": "private, no-store" },
  });
}
