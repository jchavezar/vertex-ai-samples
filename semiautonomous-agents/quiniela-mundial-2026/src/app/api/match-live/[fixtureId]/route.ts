// Per-fixture LIVE BFF. Matches our internal fixture (e.g. "A-M1") to the ESPN
// event via the (home, away, date) abbreviation triple, then -- if the match is
// in-progress or final -- fetches ESPN's per-event summary for plays + stats.
//
// Response shape is consumed by /partido/[fixtureId]/live.
import { NextResponse } from "next/server";
import {
  fetchScoreboard,
  groupStageRange,
  friendlyWindowRange,
  normalizeAbbr,
  type EspnEvent,
} from "@/lib/espn";
import { allGroupFixtures, type GroupFixture } from "@/data/groups";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";
export const revalidate = 0;

type Params = { fixtureId: string };

export type LivePlay = {
  id: string;
  minute: string;        // e.g. "47'", "HT", "FT"
  clockValue?: number;   // raw minutes for sorting
  typeId?: string;
  typeText?: string;     // ESPN's play.type.text -- "Goal", "Yellow Card", etc.
  text?: string;         // narration
  scoreValue?: number;   // for goal plays
  teamId?: string;
  teamAbbr?: string;     // mapped to our 3-letter code when possible
  athleteName?: string;
  scoringPlay?: boolean;
};

export type LiveStat = {
  name: string;          // ESPN field name (e.g. "possessionPct")
  label: string;         // display label
  home: string | number;
  away: string | number;
};

export type LiveScore = { home: number; away: number };

export type LiveResponse = {
  ok: boolean;
  error?: string;
  fixture?: GroupFixture;
  espnEventId?: string;
  state?: "pre" | "in" | "post" | "halftime";
  statusText?: string;
  clock?: string;        // displayClock e.g. "47'"
  period?: number;
  score?: LiveScore;
  teams?: {
    home: { abbr: string; name: string; logo?: string; color?: string };
    away: { abbr: string; name: string; logo?: string; color?: string };
  };
  plays?: LivePlay[];    // reverse-chronological (most recent first)
  stats?: LiveStat[];
  // Convenience subset for the celebration trigger
  lastGoalId?: string;
};

type EspnSummaryAthlete = { displayName?: string; shortName?: string; jersey?: string };
type EspnSummaryPlay = {
  id?: string | number;
  sequence?: string | number;
  type?: { id?: string | number; text?: string };
  text?: string;
  shortText?: string;
  scoringPlay?: boolean;
  scoreValue?: number;
  clock?: { value?: number; displayValue?: string };
  period?: { number?: number; displayValue?: string };
  team?: { id?: string };
  athletesInvolved?: EspnSummaryAthlete[];
};

type EspnSummaryStat = {
  name?: string;
  displayName?: string;
  displayValue?: string;
  value?: number | string;
  abbreviation?: string;
};

type EspnSummaryCompetitor = {
  id?: string;
  homeAway?: "home" | "away";
  score?: string | number;
  team?: {
    id?: string;
    abbreviation?: string;
    displayName?: string;
    logo?: string;
    color?: string;
    alternateColor?: string;
  };
  statistics?: EspnSummaryStat[];
};

type EspnSummary = {
  header?: {
    id?: string;
    competitions?: Array<{
      status?: {
        displayClock?: string;
        period?: number;
        type?: { state?: string; detail?: string; shortDetail?: string };
      };
      competitors?: EspnSummaryCompetitor[];
    }>;
  };
  // ESPN World Cup feed: "plays" is NOT populated; live data lives in
  // "commentary" (minute-by-minute narration + embedded play object) and
  // "keyEvents" (major events: goals, cards, subs, halftime, kickoff).
  plays?: EspnSummaryPlay[];
  commentary?: EspnCommentary[];
  keyEvents?: EspnKeyEvent[];
  boxscore?: { teams?: EspnSummaryCompetitor[] };
};

type EspnKeyEvent = {
  id?: string;
  type?: { id?: string; text?: string; type?: string };
  text?: string;
  shortText?: string;
  period?: { number?: number };
  clock?: { value?: number; displayValue?: string };
  scoringPlay?: boolean;
  team?: { id?: string; displayName?: string };
  participants?: Array<{ athlete?: { id?: string; displayName?: string } }>;
};

type EspnCommentary = {
  sequence?: number;
  time?: { value?: number; displayValue?: string };
  text?: string;
  play?: EspnKeyEvent;
};

async function safe<T>(p: Promise<T>): Promise<{ ok: true; value: T } | { ok: false; error: string }> {
  try { return { ok: true, value: await p }; }
  catch (e) { return { ok: false, error: e instanceof Error ? e.message : String(e) }; }
}

// Mirror the matching the scoreboard route does: scan both world-cup + friendly
// windows so the live page works in the pre-WC friendly period too.
async function findEspnEvent(fx: GroupFixture): Promise<EspnEvent | null> {
  const wcDates = groupStageRange();
  const frDates = friendlyWindowRange();
  const [wc, fr] = await Promise.all([
    safe(fetchScoreboard(wcDates, "fifa.world")),
    safe(fetchScoreboard(frDates, "fifa.friendly")),
  ]);
  const events: EspnEvent[] = [];
  if (wc.ok && wc.value) events.push(...(wc.value.events || []));
  if (fr.ok && fr.value) events.push(...(fr.value.events || []));

  for (const e of events) {
    const c = e.competitions[0];
    const h = c.competitors.find(cp => cp.homeAway === "home");
    const a = c.competitors.find(cp => cp.homeAway === "away");
    if (!h || !a) continue;
    const hCode = normalizeAbbr(h.team.abbreviation);
    const aCode = normalizeAbbr(a.team.abbreviation);
    const cdmxDate = new Date(e.date).toLocaleDateString("en-CA", { timeZone: "America/Mexico_City" });
    const isoDate = e.date.slice(0, 10);
    const samePair =
      (hCode === fx.home && aCode === fx.away) || (hCode === fx.away && aCode === fx.home);
    if (!samePair) continue;
    if (cdmxDate === fx.date || isoDate === fx.date) return e;
  }
  return null;
}

async function fetchSummary(eventId: string): Promise<EspnSummary | null> {
  const tries = [
    `https://site.api.espn.com/apis/site/v2/sports/soccer/fifa.world/summary?event=${encodeURIComponent(eventId)}`,
    `https://site.api.espn.com/apis/site/v2/sports/soccer/fifa.friendly/summary?event=${encodeURIComponent(eventId)}`,
  ];
  for (const url of tries) {
    try {
      const res = await fetch(url, { cache: "no-store" });
      if (!res.ok) continue;
      return (await res.json()) as EspnSummary;
    } catch { /* fall through */ }
  }
  return null;
}

const STAT_LABELS: Record<string, string> = {
  possessionPct: "Posesión",
  totalShots: "Tiros",
  shotsOnTarget: "Tiros a puerta",
  shotsOnGoal: "Tiros a puerta",
  wonCorners: "Tiros de esquina",
  corners: "Tiros de esquina",
  fouls: "Faltas",
  foulsCommitted: "Faltas",
  yellowCards: "Amarillas",
  redCards: "Rojas",
  offsides: "Fueras de lugar",
  saves: "Atajadas",
  totalPasses: "Pases",
  accuratePasses: "Pases certeros",
};

// Stat keys we want, in display order. We pick whichever ESPN gave us.
const STAT_PREFERENCE: string[][] = [
  ["possessionPct"],
  ["totalShots"],
  ["shotsOnTarget", "shotsOnGoal"],
  ["wonCorners", "corners"],
  ["fouls", "foulsCommitted"],
  ["yellowCards"],
  ["redCards"],
];

function pickStat(stats: EspnSummaryStat[] | undefined, keys: string[]): EspnSummaryStat | undefined {
  if (!stats) return undefined;
  for (const k of keys) {
    const hit = stats.find(s => s.name === k);
    if (hit) return hit;
  }
  return undefined;
}

function statValue(s: EspnSummaryStat | undefined): string | number {
  if (!s) return 0;
  if (s.displayValue !== undefined && s.displayValue !== null && s.displayValue !== "") return s.displayValue;
  if (s.value !== undefined && s.value !== null) return s.value;
  return 0;
}

export async function GET(_req: Request, ctx: { params: Promise<Params> }) {
  const { fixtureId } = await ctx.params;
  const fx = allGroupFixtures().find(f => f.id === fixtureId);
  if (!fx) {
    return NextResponse.json({ ok: false, error: "fixture-not-found" } satisfies LiveResponse, { status: 404 });
  }

  let espn: EspnEvent | null = null;
  try { espn = await findEspnEvent(fx); } catch { espn = null; }

  if (!espn) {
    // ESPN doesn't list this fixture yet (common pre-tournament). Return the
    // bare fixture so the page can still render its pre-match shell.
    return NextResponse.json({
      ok: true,
      fixture: fx,
      state: "pre",
    } satisfies LiveResponse);
  }

  const c = espn.competitions[0];
  const h = c.competitors.find(cp => cp.homeAway === "home")!;
  const a = c.competitors.find(cp => cp.homeAway === "away")!;
  const hCode = normalizeAbbr(h.team.abbreviation);
  const aCode = normalizeAbbr(a.team.abbreviation);
  const ourHomeIsEspnHome = fx.home === hCode;

  const hgRaw = Number(h.score);
  const agRaw = Number(a.score);
  const hg = Number.isFinite(hgRaw) ? hgRaw : 0;
  const ag = Number.isFinite(agRaw) ? agRaw : 0;
  const score: LiveScore = {
    home: ourHomeIsEspnHome ? hg : ag,
    away: ourHomeIsEspnHome ? ag : hg,
  };

  const espnState = espn.status.type.state;
  // ESPN reports "in" for halftime too; rely on status name when present.
  const statusName = espn.status.type.name || "";
  const isHalftime = /HALFTIME/i.test(statusName);
  const state: LiveResponse["state"] = isHalftime ? "halftime" : (espnState as LiveResponse["state"]);

  const base: LiveResponse = {
    ok: true,
    fixture: fx,
    espnEventId: espn.id,
    state,
    statusText: espn.status.type.shortDetail || espn.status.type.detail,
    clock: espn.status.displayClock,
    score,
    teams: {
      home: {
        abbr: fx.home,
        name: ourHomeIsEspnHome ? h.team.displayName : a.team.displayName,
        logo: ourHomeIsEspnHome ? h.team.logo : a.team.logo,
        color: ourHomeIsEspnHome ? h.team.color : a.team.color,
      },
      away: {
        abbr: fx.away,
        name: ourHomeIsEspnHome ? a.team.displayName : h.team.displayName,
        logo: ourHomeIsEspnHome ? a.team.logo : h.team.logo,
        color: ourHomeIsEspnHome ? a.team.color : h.team.color,
      },
    },
  };

  if (state !== "in" && state !== "post" && state !== "halftime") {
    return NextResponse.json(base);
  }

  const summary = await fetchSummary(espn.id);
  if (!summary) return NextResponse.json(base);

  // ---- Plays: normalize + reverse-chronological ----
  const teamIdToAbbr = new Map<string, string>();
  for (const cp of c.competitors) {
    if (cp.team?.id) teamIdToAbbr.set(cp.team.id, normalizeAbbr(cp.team.abbreviation));
  }

  // Build timeline from commentary (rich minute-by-minute). Each commentary
  // entry has narration text + an embedded `play` with type/team/athletes.
  // Fall back to keyEvents (sparser, only major events) when commentary is
  // empty. Lineups/warming-up entries with no `play` are kept as text.
  const commentaryRaw: EspnCommentary[] = Array.isArray(summary.commentary) ? summary.commentary : [];
  const keyEventsRaw: EspnKeyEvent[] = Array.isArray(summary.keyEvents) ? summary.keyEvents : [];
  // Index keyEvents by id so we can flag commentary entries as scoring plays
  // even when the embedded play object lacks the flag.
  const scoringPlayIds = new Set<string>();
  for (const k of keyEventsRaw) if (k.scoringPlay && k.id) scoringPlayIds.add(String(k.id));

  const mapPlay = (
    src: { id?: string; sequence?: number; clock?: { value?: number; displayValue?: string }; type?: { id?: string; text?: string }; text?: string; shortText?: string; team?: { id?: string; displayName?: string }; participants?: Array<{ athlete?: { id?: string; displayName?: string } }>; scoringPlay?: boolean },
    fallbackId: string,
    fallbackText?: string,
  ): LivePlay => {
    const tId = src.team?.id;
    const athlete = src.participants?.[0]?.athlete;
    const minuteRaw = src.clock?.displayValue || (typeof src.clock?.value === "number" ? `${src.clock.value}'` : "");
    const id = String(src.id ?? src.sequence ?? fallbackId);
    return {
      id,
      minute: minuteRaw || "",
      clockValue: typeof src.clock?.value === "number" ? src.clock.value : undefined,
      typeId: src.type?.id != null ? String(src.type.id) : undefined,
      typeText: src.type?.text,
      text: fallbackText || src.text || src.shortText,
      teamId: tId,
      teamAbbr: tId ? teamIdToAbbr.get(tId) : undefined,
      athleteName: athlete?.displayName,
      scoringPlay: !!src.scoringPlay || (!!src.id && scoringPlayIds.has(String(src.id))),
    } satisfies LivePlay;
  };

  let plays: LivePlay[] = [];
  if (commentaryRaw.length > 0) {
    plays = commentaryRaw.map((c, i) => {
      const text = c.text;
      if (c.play) return mapPlay({ ...c.play, sequence: c.sequence }, `c-${i}`, text);
      // Commentary entry with no embedded play (e.g. "Lineups are announced…")
      const fallbackMinute = c.time?.displayValue || (typeof c.time?.value === "number" ? `${c.time.value}'` : "");
      return {
        id: `c-${c.sequence ?? i}`,
        minute: fallbackMinute,
        clockValue: typeof c.time?.value === "number" ? c.time.value : undefined,
        text,
        scoringPlay: false,
      } satisfies LivePlay;
    }).sort((a, b) => (b.clockValue ?? -1) - (a.clockValue ?? -1));
  } else if (keyEventsRaw.length > 0) {
    plays = keyEventsRaw
      .map((k, i) => mapPlay(k, `k-${i}`))
      .sort((a, b) => (b.clockValue ?? -1) - (a.clockValue ?? -1));
  }

  // ---- Stats: pull from boxscore.teams when present, else competition.competitors ----
  const boxTeams = summary.boxscore?.teams || [];
  const findBoxTeam = (id?: string) => boxTeams.find(t => t.team?.id === id || t.id === id);
  const espnHomeStats = (findBoxTeam(h.team.id) as EspnSummaryCompetitor | undefined)?.statistics;
  const espnAwayStats = (findBoxTeam(a.team.id) as EspnSummaryCompetitor | undefined)?.statistics;

  const stats: LiveStat[] = [];
  for (const keys of STAT_PREFERENCE) {
    const hh = pickStat(espnHomeStats, keys);
    const aa = pickStat(espnAwayStats, keys);
    if (!hh && !aa) continue;
    const name = hh?.name || aa?.name || keys[0];
    const label = STAT_LABELS[name] || hh?.displayName || aa?.displayName || name;
    const hv = statValue(hh);
    const av = statValue(aa);
    stats.push({
      name,
      label,
      home: ourHomeIsEspnHome ? hv : av,
      away: ourHomeIsEspnHome ? av : hv,
    });
  }

  const lastGoal = plays.find(p => p.scoringPlay || /goal/i.test(p.typeText || ""));

  return NextResponse.json({
    ...base,
    period: summary.header?.competitions?.[0]?.status?.period,
    plays,
    stats,
    lastGoalId: lastGoal?.id,
  } satisfies LiveResponse, {
    headers: { "Cache-Control": "no-store" },
  });
}
