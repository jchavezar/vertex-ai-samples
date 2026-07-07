// ESPN World Cup hidden API (no auth) — scoreboard + standings

export type EspnTeam = {
  id: string;
  abbreviation: string;
  displayName: string;
  shortDisplayName: string;
  location: string;
  color: string;
  alternateColor: string;
  logo: string;
};

export type EspnCompetitor = {
  homeAway: "home" | "away";
  score: string;
  winner?: boolean;
  form?: string;
  team: EspnTeam;
};

export type Competition = "world" | "friendly";

export type EspnEvent = {
  id: string;
  date: string;            // ISO
  name: string;
  shortName: string;
  competition?: Competition;
  status: {
    clock: number;
    displayClock: string;
    type: {
      id: string;
      name: string;        // STATUS_SCHEDULED, STATUS_IN_PROGRESS, STATUS_FULL_TIME, STATUS_HALFTIME
      state: "pre" | "in" | "post";
      completed: boolean;
      description: string;
      detail: string;
      shortDetail: string;
    };
  };
  venue?: { displayName: string };
  competitions: Array<{
    competitors: EspnCompetitor[];
    status: EspnEvent["status"];
    venue?: { fullName: string; address?: { city: string; country: string } };
    broadcasts?: Array<{ market: string; names: string[] }>;
    odds?: EspnOdds[];
  }>;
};

export type EspnMoneyLineSide = { open?: { odds?: string }; close?: { odds?: string } };
export type EspnOdds = {
  provider?: { id: string; name: string };
  details?: string;
  moneyline?: {
    home?: EspnMoneyLineSide;
    away?: EspnMoneyLineSide;
    draw?: EspnMoneyLineSide;
  };
  // Older shape (some leagues): top-level drawOdds / homeTeamOdds / awayTeamOdds
  drawOdds?: { moneyLine?: number };
  homeTeamOdds?: { moneyLine?: number };
  awayTeamOdds?: { moneyLine?: number };
};

// American moneyline → implied probability (decimal 0..1).
// Negative: |x|/(|x|+100). Positive: 100/(x+100).
export function moneylineToImpliedProb(american: string | number | undefined | null): number | null {
  if (american == null) return null;
  const n = typeof american === "string" ? Number(american) : american;
  if (!Number.isFinite(n) || n === 0) return null;
  if (n < 0) return -n / (-n + 100);
  return 100 / (n + 100);
}

// Strip the bookmaker's vig: take H/D/A implied probs and normalize so sum = 1.
export function extractMarketProb(odds: EspnOdds | undefined): { H: number; D: number; A: number } | null {
  if (!odds) return null;
  let h = moneylineToImpliedProb(odds.moneyline?.home?.close?.odds ?? odds.moneyline?.home?.open?.odds);
  let a = moneylineToImpliedProb(odds.moneyline?.away?.close?.odds ?? odds.moneyline?.away?.open?.odds);
  let d = moneylineToImpliedProb(odds.moneyline?.draw?.close?.odds ?? odds.moneyline?.draw?.open?.odds);
  if (h == null) h = moneylineToImpliedProb(odds.homeTeamOdds?.moneyLine);
  if (a == null) a = moneylineToImpliedProb(odds.awayTeamOdds?.moneyLine);
  if (d == null) d = moneylineToImpliedProb(odds.drawOdds?.moneyLine);
  if (h == null || a == null || d == null) return null;
  const sum = h + d + a;
  if (sum <= 0) return null;
  return { H: h / sum, D: d / sum, A: a / sum };
}

export type EspnScoreboard = {
  leagues: Array<{ name: string; season: { year: number; displayName: string } }>;
  events: EspnEvent[];
};

const ESPN_ROOT = "https://site.api.espn.com/apis/site/v2/sports/soccer";

// Fetch scoreboard for a given ESPN league slug.
export async function fetchScoreboard(dates?: string, league = "fifa.world"): Promise<EspnScoreboard> {
  const url = `${ESPN_ROOT}/${league}/scoreboard${dates ? `?dates=${dates}` : ""}`;
  const res = await fetch(url, { next: { revalidate: 30 } });
  if (!res.ok) throw new Error(`ESPN ${league} ${res.status}`);
  return res.json();
}

// Full World Cup window (group stage + knockouts + final)
export function groupStageRange() {
  return "20260611-20260719";
}

// Pre-WC friendlies window: from today through the day before kickoff
export function friendlyWindowRange() {
  const today = new Date();
  const start = today.toISOString().slice(0, 10).replace(/-/g, "");
  return `${start}-20260610`;
}

// Map ESPN abbr → our 3-letter codes when they differ
const ABBR_MAP: Record<string, string> = {
  // ESPN often matches FIFA codes already; only override when they don't
  "DRC": "COD",  // Congo DR (ESPN may use DRC or COD)
  "CGO": "COD",
  "KSA": "KSA",
  "USA": "USA",
  "MEX": "MEX",
  "CAN": "CAN",
  "RSA": "RSA",
};

export function normalizeAbbr(espnAbbr: string): string {
  return ABBR_MAP[espnAbbr] || espnAbbr;
}

export function isLive(e: EspnEvent): boolean {
  return e.status.type.state === "in";
}

export function homeAway(e: EspnEvent) {
  const cs = e.competitions[0].competitors;
  const home = cs.find(c => c.homeAway === "home")!;
  const away = cs.find(c => c.homeAway === "away")!;
  return { home, away };
}
