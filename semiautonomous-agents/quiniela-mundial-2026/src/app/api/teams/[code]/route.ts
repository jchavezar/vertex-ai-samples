// Team stats API: completed match results, goalscorers, group standing, player stats.
// GET /api/teams/[code]  →  TeamStatsResponse
import { NextResponse, type NextRequest } from "next/server";
import {
  fetchScoreboard,
  groupStageRange,
  normalizeAbbr,
  type EspnEvent,
} from "@/lib/espn";
import { allGroupFixtures, GROUPS, type GroupFixture } from "@/data/groups";
import { TEAMS_BY_CODE } from "@/data/teams";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

// ─── ESPN summary types (minimal subset) ──────────────────────────────────────
type SummaryPlay = {
  scoringPlay?: boolean;
  type?: { text?: string };
  clock?: { value?: number; displayValue?: string };
  team?: { id?: string };
  participants?: Array<{
    type?: string;
    athlete?: { shortName?: string; displayName?: string };
  }>;
};
type EspnSummary = { plays?: SummaryPlay[]; keyEvents?: SummaryPlay[] };

async function fetchSummary(eventId: string): Promise<EspnSummary | null> {
  const url = `https://site.api.espn.com/apis/site/v2/sports/soccer/fifa.world/summary?event=${encodeURIComponent(eventId)}`;
  try {
    const res = await fetch(url, { cache: "no-store" });
    if (!res.ok) return null;
    return (await res.json()) as EspnSummary;
  } catch { return null; }
}

function athleteName(play: SummaryPlay): string | undefined {
  const p = play.participants?.find(x => x.type === "scorer" || x.type === "Scorer")
    ?? play.participants?.[0];
  return p?.athlete?.shortName ?? p?.athlete?.displayName;
}

// ─── Public types ──────────────────────────────────────────────────────────────
export type MatchResult = {
  fixtureId: string;
  date: string;
  matchday: number;
  opponent: string;
  homeGoals: number;
  awayGoals: number;
  isHome: boolean;
  result: "W" | "D" | "L";
  goalscorers: string[];
};

export type GroupStanding = {
  pj: number; pts: number;
  pg: number; pe: number; pp: number;
  gf: number; ga: number; gd: number;
  position: number;
};

export type PlayerStat = {
  name: string;
  goals: number;
  yellows: number;
  reds: number;
};

export type TeamStatsResponse = {
  ok: true;
  code: string;
  group: string;
  completed: MatchResult[];
  upcoming: Array<{ fixtureId: string; date: string; matchday: number; opponent: string; isHome: boolean }>;
  standing: GroupStanding;
  playerStats: PlayerStat[];
};

export type TeamStatsError = { ok: false; error: string };

// ─── Handler ──────────────────────────────────────────────────────────────────
export async function GET(
  _req: NextRequest,
  { params }: { params: Promise<{ code: string }> },
) {
  const { code } = await params;
  const teamCode = code.toUpperCase();

  const team = TEAMS_BY_CODE[teamCode];
  if (!team) {
    return NextResponse.json({ ok: false, error: "team_not_found" } satisfies TeamStatsError, { status: 404 });
  }

  const fixtures = allGroupFixtures().filter(fx => fx.home === teamCode || fx.away === teamCode);

  // Fetch scoreboard to match ESPN event IDs to our fixture IDs.
  let espnEvents: EspnEvent[] = [];
  try {
    const sb = await fetchScoreboard(groupStageRange(), "fifa.world");
    espnEvents = sb.events ?? [];
  } catch { /* proceed without ESPN data */ }

  // Build fixture-id → ESPN event map.
  const espnByFixtureId = new Map<string, EspnEvent>();
  for (const e of espnEvents) {
    const c = e.competitions[0];
    const h = c.competitors.find(cp => cp.homeAway === "home");
    const a = c.competitors.find(cp => cp.homeAway === "away");
    if (!h || !a) continue;
    const hCode = normalizeAbbr(h.team.abbreviation);
    const aCode = normalizeAbbr(a.team.abbreviation);
    const cdmxDate = new Date(e.date).toLocaleDateString("en-CA", { timeZone: "America/Mexico_City" });
    const match = fixtures.find(fx =>
      ((fx.home === hCode && fx.away === aCode) || (fx.home === aCode && fx.away === hCode)) &&
      (fx.date === cdmxDate || fx.date === e.date.slice(0, 10)),
    );
    if (match) espnByFixtureId.set(match.id, e);
  }

  const completed: MatchResult[] = [];
  const upcoming: TeamStatsResponse["upcoming"] = [];

  const completedFixtures = fixtures.filter(fx => {
    const e = espnByFixtureId.get(fx.id);
    return e?.status.type.state === "post";
  });

  const summaries = await Promise.all(
    completedFixtures.map(async fx => ({ fx, summary: await fetchSummary(espnByFixtureId.get(fx.id)!.id) })),
  );

  // Aggregate player stats across all completed matches
  const playerStatsMap = new Map<string, PlayerStat>();

  for (const { fx, summary } of summaries) {
    const e = espnByFixtureId.get(fx.id)!;
    const c = e.competitions[0];
    const espnHome = c.competitors.find(cp => cp.homeAway === "home")!;
    const espnAway = c.competitors.find(cp => cp.homeAway === "away")!;
    const espnHomeCode = normalizeAbbr(espnHome.team.abbreviation);
    const ourHomeIsEspnHome = fx.home === espnHomeCode;
    const hgRaw = Number(espnHome.score);
    const agRaw = Number(espnAway.score);
    const hg = Number.isFinite(hgRaw) ? hgRaw : 0;
    const ag = Number.isFinite(agRaw) ? agRaw : 0;
    const ourHg = ourHomeIsEspnHome ? hg : ag;
    const ourAg = ourHomeIsEspnHome ? ag : hg;
    const isHome = fx.home === teamCode;
    const teamGoals = isHome ? ourHg : ourAg;
    const oppGoals = isHome ? ourAg : ourHg;
    const result: "W" | "D" | "L" = teamGoals > oppGoals ? "W" : teamGoals < oppGoals ? "L" : "D";
    const opponent = isHome ? fx.away : fx.home;

    const espnTeamId = isHome
      ? (ourHomeIsEspnHome ? espnHome.team.id : espnAway.team.id)
      : (ourHomeIsEspnHome ? espnAway.team.id : espnHome.team.id);

    const goalscorers: string[] = [];
    if (summary) {
      const plays = [...(summary.plays ?? []), ...(summary.keyEvents ?? [])];
      for (const p of plays) {
        if (espnTeamId && p.team?.id && p.team.id !== espnTeamId) continue;
        const name = athleteName(p);
        if (!name) continue;
        const typeText = (p.type?.text ?? "").toLowerCase();

        if (p.scoringPlay && !typeText.includes("own goal")) {
          goalscorers.push(name);
          const ps = playerStatsMap.get(name) ?? { name, goals: 0, yellows: 0, reds: 0 };
          ps.goals++;
          playerStatsMap.set(name, ps);
        } else if (!p.scoringPlay) {
          if (typeText.includes("red") || typeText.includes("second yellow")) {
            const ps = playerStatsMap.get(name) ?? { name, goals: 0, yellows: 0, reds: 0 };
            ps.reds++;
            playerStatsMap.set(name, ps);
          } else if (typeText.includes("yellow")) {
            const ps = playerStatsMap.get(name) ?? { name, goals: 0, yellows: 0, reds: 0 };
            ps.yellows++;
            playerStatsMap.set(name, ps);
          }
        }
      }
    }

    completed.push({ fixtureId: fx.id, date: fx.date, matchday: fx.matchday, opponent, homeGoals: ourHg, awayGoals: ourAg, isHome, result, goalscorers });
  }

  // Upcoming fixtures.
  for (const fx of fixtures) {
    const e = espnByFixtureId.get(fx.id);
    if (e?.status.type.state === "post") continue;
    upcoming.push({ fixtureId: fx.id, date: fx.date, matchday: fx.matchday, opponent: fx.home === teamCode ? fx.away : fx.home, isHome: fx.home === teamCode });
  }

  // Compute group standing from completed results.
  const standing: GroupStanding = { pj: 0, pts: 0, pg: 0, pe: 0, pp: 0, gf: 0, ga: 0, gd: 0, position: 0 };
  for (const m of completed) {
    standing.pj++;
    const gf = m.isHome ? m.homeGoals : m.awayGoals;
    const ga = m.isHome ? m.awayGoals : m.homeGoals;
    standing.gf += gf;
    standing.ga += ga;
    standing.gd += gf - ga;
    if (m.result === "W") { standing.pg++; standing.pts += 3; }
    else if (m.result === "D") { standing.pe++; standing.pts += 1; }
    else { standing.pp++; }
  }

  // Compute position within group (simple pts → GD → GF → alpha tiebreak).
  const groupTeams = GROUPS[team.group as keyof typeof GROUPS] ?? [];
  type TeamRow = { code: string; pts: number; gd: number; gf: number };
  const groupRows: TeamRow[] = groupTeams.map(tc => {
    if (tc === teamCode) return { code: tc, pts: standing.pts, gd: standing.gd, gf: standing.gf };
    // Build row for other teams from ESPN data.
    const theirFixtures = allGroupFixtures().filter(fx => (fx.home === tc || fx.away === tc) && espnByFixtureId.get(fx.id)?.status.type.state === "post");
    let pts = 0, gd = 0, gf = 0;
    for (const fx of theirFixtures) {
      const e2 = espnByFixtureId.get(fx.id);
      if (!e2) continue;
      const c2 = e2.competitions[0];
      const h2 = c2.competitors.find(cp => cp.homeAway === "home");
      const a2 = c2.competitors.find(cp => cp.homeAway === "away");
      if (!h2 || !a2) continue;
      const hgr = Number(h2.score), agr = Number(a2.score);
      if (!Number.isFinite(hgr) || !Number.isFinite(agr)) continue;
      const espnHCode = normalizeAbbr(h2.team.abbreviation);
      const ourHomeIsEspn = fx.home === espnHCode;
      const ourH = ourHomeIsEspn ? hgr : agr, ourA = ourHomeIsEspn ? agr : hgr;
      const isH = fx.home === tc;
      const myG = isH ? ourH : ourA, oppG = isH ? ourA : ourH;
      gf += myG; gd += myG - oppG;
      if (myG > oppG) pts += 3; else if (myG === oppG) pts += 1;
    }
    return { code: tc, pts, gd, gf };
  });
  groupRows.sort((a, b) => b.pts - a.pts || b.gd - a.gd || b.gf - a.gf || a.code.localeCompare(b.code));
  standing.position = (groupRows.findIndex(r => r.code === teamCode) ?? 0) + 1;

  // Sort: goals desc → yellows desc → alpha
  const playerStats = [...playerStatsMap.values()].sort(
    (a, b) => b.goals - a.goals || b.yellows - a.yellows || a.name.localeCompare(b.name),
  );

  const body: TeamStatsResponse = {
    ok: true,
    code: teamCode,
    group: team.group,
    completed: completed.sort((a, b) => a.matchday - b.matchday),
    upcoming: upcoming.sort((a, b) => a.matchday - b.matchday),
    standing,
    playerStats,
  };

  return NextResponse.json(body, {
    headers: { "Cache-Control": "public, max-age=30, stale-while-revalidate=60" },
  });
}
