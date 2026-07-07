// Pure-function version of the /api/scorers aggregator. Extracted so the
// home snapshot endpoint (/api/home/snapshot) can call it directly without
// going through the HTTP layer. The route handler in ./route.ts wraps this
// and adds NextResponse + Cache-Control.
//
// Keep logic 1:1 with route.ts — this is a refactor, NOT a re-implementation.

import { fetchScoreboard, groupStageRange, normalizeAbbr, type EspnEvent } from "@/lib/espn";
import { TEAMS } from "@/data/teams";

export type ScorerEntry = {
  athleteId: string;
  name: string;
  shortName: string;
  photo?: string;
  teamCode: string;
  teamName: string;
  teamIso2: string;
  goals: number;
  assists?: number;
  matchesPlayed: number;
};

export type ScorersResponse =
  | { ok: true; top5: ScorerEntry[]; generatedAt: number }
  | { ok: false; error: string };

// ── ESPN summary types (loose) ──
type EspnAthlete = {
  id?: string;
  fullName?: string;
  displayName?: string;
  shortName?: string;
  headshot?: { href?: string } | string;
};

type EspnLeaderRow = {
  displayValue?: string;
  value?: number;
  athlete?: EspnAthlete;
  team?: { abbreviation?: string };
  statistics?: Array<{ name?: string; displayValue?: string; value?: number }>;
};

type EspnLeaderCategory = {
  name?: string;
  displayName?: string;
  leaders?: EspnLeaderRow[];
};

type EspnLeaderTeamGroup = { team?: { abbreviation?: string }; leaders?: EspnLeaderCategory[] };
type EspnLeadersField = EspnLeaderCategory[] | EspnLeaderTeamGroup[];

type EspnPlay = {
  scoringPlay?: boolean;
  type?: { text?: string; type?: string };
  team?: { id?: string; abbreviation?: string; displayName?: string };
  participants?: Array<{
    type?: string;
    athlete?: EspnAthlete & { team?: { abbreviation?: string } };
  }>;
};

type EspnSummary = {
  header?: {
    id?: string;
    competitions?: Array<{
      competitors?: Array<{ team?: { id?: string; abbreviation?: string } }>;
    }>;
  };
  leaders?: EspnLeadersField;
  boxscore?: { leaders?: EspnLeadersField };
  keyEvents?: EspnPlay[];
};

type EspnEventWithLeaders = EspnEvent & {
  competitions: Array<EspnEvent["competitions"][number] & { leaders?: EspnLeadersField }>;
};

function headshotUrl(a: EspnAthlete | undefined): string | undefined {
  if (!a?.headshot) return undefined;
  if (typeof a.headshot === "string") return a.headshot;
  return a.headshot.href;
}

function teamIso2(code: string): string {
  return TEAMS.find(t => t.code === code)?.iso2 ?? "un";
}

function teamName(code: string): string {
  return TEAMS.find(t => t.code === code)?.name ?? code;
}

function* iterLeaderRows(
  leaders: EspnLeadersField | undefined,
  fallbackTeamAbbr?: string,
): Generator<{ category: string; row: EspnLeaderRow; teamAbbr: string | undefined }> {
  if (!leaders || !Array.isArray(leaders) || leaders.length === 0) return;
  const first = leaders[0] as EspnLeaderTeamGroup & EspnLeaderCategory;
  const isPerTeam = first && (first.team !== undefined) && Array.isArray(first.leaders);

  if (isPerTeam) {
    for (const group of leaders as EspnLeaderTeamGroup[]) {
      const abbr = group.team?.abbreviation ?? fallbackTeamAbbr;
      for (const cat of group.leaders ?? []) {
        const catName = (cat.name || cat.displayName || "").toLowerCase();
        for (const row of cat.leaders ?? []) {
          yield { category: catName, row, teamAbbr: row.team?.abbreviation ?? abbr };
        }
      }
    }
    return;
  }

  for (const cat of leaders as EspnLeaderCategory[]) {
    const catName = (cat.name || cat.displayName || "").toLowerCase();
    for (const row of cat.leaders ?? []) {
      yield { category: catName, row, teamAbbr: row.team?.abbreviation ?? fallbackTeamAbbr };
    }
  }
}

function parseGoalCount(row: EspnLeaderRow): number {
  if (typeof row.value === "number" && Number.isFinite(row.value)) return Math.floor(row.value);
  if (row.displayValue) {
    const m = row.displayValue.match(/^\s*(\d+)/);
    if (m) return Number(m[1]);
  }
  const stat = row.statistics?.find(s => (s.name || "").toLowerCase() === "goals");
  if (stat) {
    if (typeof stat.value === "number") return Math.floor(stat.value);
    if (stat.displayValue) {
      const m = stat.displayValue.match(/^\s*(\d+)/);
      if (m) return Number(m[1]);
    }
  }
  return 0;
}

function parseAssistCount(row: EspnLeaderRow): number {
  if (typeof row.value === "number" && Number.isFinite(row.value)) return Math.floor(row.value);
  if (row.displayValue) {
    const m = row.displayValue.match(/^\s*(\d+)/);
    if (m) return Number(m[1]);
  }
  return 0;
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

type Bucket = {
  athleteId: string;
  name: string;
  shortName: string;
  photo?: string;
  teamCode: string;
  goals: number;
  assists: number;
  matches: Set<string>;
};

function upsertBucket(
  buckets: Map<string, Bucket>,
  athlete: EspnAthlete | undefined,
  teamAbbr: string | undefined,
  eventId: string,
  addGoals: number,
  addAssists: number,
) {
  if (!athlete?.id) return;
  const teamCode = normalizeAbbr(teamAbbr ?? "");
  if (!teamCode) return;
  const key = athlete.id;
  let b = buckets.get(key);
  if (!b) {
    b = {
      athleteId: key,
      name: athlete.fullName || athlete.displayName || athlete.shortName || "—",
      shortName: athlete.shortName || athlete.displayName || athlete.fullName || "—",
      photo: headshotUrl(athlete),
      teamCode,
      goals: 0,
      assists: 0,
      matches: new Set(),
    };
    buckets.set(key, b);
  }
  if (!b.photo) {
    const h = headshotUrl(athlete);
    if (h) b.photo = h;
  }
  b.goals += addGoals;
  b.assists += addAssists;
  if (eventId) b.matches.add(eventId);
}

function consumeLeaders(
  buckets: Map<string, Bucket>,
  leaders: EspnLeadersField | undefined,
  eventId: string,
  fallbackTeamAbbr?: string,
) {
  for (const { category, row, teamAbbr } of iterLeaderRows(leaders, fallbackTeamAbbr)) {
    if (category === "goals") {
      const n = parseGoalCount(row);
      if (n > 0) upsertBucket(buckets, row.athlete, teamAbbr, eventId, n, 0);
    } else if (category === "assists") {
      const n = parseAssistCount(row);
      if (n > 0) upsertBucket(buckets, row.athlete, teamAbbr, eventId, 0, n);
    }
  }
}

function consumeKeyEvents(
  buckets: Map<string, Bucket>,
  keyEvents: EspnPlay[] | undefined,
  eventId: string,
  teamIdToAbbr: Map<string, string>,
) {
  if (!keyEvents || keyEvents.length === 0) return;
  for (const play of keyEvents) {
    if (!play.scoringPlay) continue;
    const typeText = (play.type?.text || "").toLowerCase();
    if (typeText.includes("own goal")) continue;
    const participants = play.participants ?? [];
    if (participants.length === 0) continue;
    const scorer = participants.find(p => /scorer/i.test(p.type || "")) ?? participants[0];
    if (!scorer?.athlete?.id) continue;
    const teamAbbr = scorer.athlete.team?.abbreviation
      ?? play.team?.abbreviation
      ?? (play.team?.id ? teamIdToAbbr.get(play.team.id) : undefined);
    upsertBucket(buckets, scorer.athlete, teamAbbr, eventId, 1, 0);
    const assister = participants.find(p => /assist/i.test(p.type || ""))
      ?? (participants.length > 1 ? participants[1] : undefined);
    if (assister?.athlete?.id && assister.athlete.id !== scorer.athlete.id) {
      const assistTeam = assister.athlete.team?.abbreviation
        ?? play.team?.abbreviation
        ?? (play.team?.id ? teamIdToAbbr.get(play.team.id) : undefined);
      upsertBucket(buckets, assister.athlete, assistTeam, eventId, 0, 1);
    }
  }
}

export async function computeTopScorers(): Promise<ScorersResponse> {
  let board;
  try {
    board = await fetchScoreboard(groupStageRange(), "fifa.world");
  } catch (e) {
    return { ok: false, error: e instanceof Error ? e.message : String(e) };
  }

  const events = (board.events || []) as EspnEventWithLeaders[];

  const playable = events.filter(e => {
    const s = e.status?.type?.state;
    return s === "in" || s === "post";
  });

  const buckets = new Map<string, Bucket>();
  const needSummary: { id: string }[] = [];

  for (const e of playable) {
    const c = e.competitions?.[0];
    const scoreboardHasLeaders =
      c?.leaders && Array.isArray(c.leaders) && c.leaders.length > 0;
    if (scoreboardHasLeaders) {
      consumeLeaders(buckets, c!.leaders, e.id);
    } else {
      needSummary.push({ id: e.id });
    }
  }

  const CONCURRENCY = 6;
  for (let i = 0; i < needSummary.length; i += CONCURRENCY) {
    const slice = needSummary.slice(i, i + CONCURRENCY);
    const summaries = await Promise.all(slice.map(s => fetchSummary(s.id)));
    summaries.forEach((sum, idx) => {
      if (!sum) return;
      const eventId = slice[idx].id;
      const teamIdToAbbr = new Map<string, string>();
      for (const cp of sum.header?.competitions?.[0]?.competitors ?? []) {
        if (cp.team?.id && cp.team.abbreviation) {
          teamIdToAbbr.set(cp.team.id, cp.team.abbreviation);
        }
      }
      consumeKeyEvents(buckets, sum.keyEvents, eventId, teamIdToAbbr);
      consumeLeaders(buckets, sum.leaders, eventId);
      consumeLeaders(buckets, sum.boxscore?.leaders, eventId);
    });
  }

  const all = Array.from(buckets.values()).map<ScorerEntry>(b => ({
    athleteId: b.athleteId,
    name: b.name,
    shortName: b.shortName,
    photo: b.photo,
    teamCode: b.teamCode,
    teamName: teamName(b.teamCode),
    teamIso2: teamIso2(b.teamCode),
    goals: b.goals,
    assists: b.assists || undefined,
    matchesPlayed: b.matches.size,
  }));

  all.sort((a, b) =>
    b.goals - a.goals ||
    (b.assists ?? 0) - (a.assists ?? 0) ||
    a.name.localeCompare(b.name),
  );

  return { ok: true, top5: all.slice(0, 10), generatedAt: Date.now() };
}
