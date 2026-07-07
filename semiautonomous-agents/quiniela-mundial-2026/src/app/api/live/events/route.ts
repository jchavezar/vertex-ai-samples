// Live Event feed — surfaces ALL meaningful match events (goal / red /
// penalty awarded / substitution / VAR review) across currently in-progress
// fixtures, plus events from fixtures that finished within the last 10
// minutes (so a user opening the app sees the very recent past too).
//
// Designed for the <LiveEventOverlay> client to consume both:
//   - GET /api/live/events?sinceMs=600000   on first mount (catch-up)
//   - GET /api/live/events?sinceMs=15000    on the recurring poll
//
// Each event carries a stable `id` (signature) the client uses to dedup
// across polls AND across the catch-up→live boundary.
//
// Wallclock estimation: ESPN exposes a `clock.value` (seconds into match)
// per play. We approximate wallclock as
//   kickoff_ms + clock.value * 1000
// which is good enough for "hace N min" labelling (no real timestamp is
// available from the public ESPN summary feed).

import { NextResponse, type NextRequest } from "next/server";
import {
  fetchScoreboard,
  groupStageRange,
  friendlyWindowRange,
  normalizeAbbr,
  type EspnEvent,
} from "@/lib/espn";
import { allGroupFixtures, type GroupFixture } from "@/data/groups";
import { TEAMS } from "@/data/teams";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export type LiveEventType = "goal" | "red" | "penalty" | "sub" | "var";

export type LiveEventItem = {
  id: string;            // stable dedup signature
  fixtureId: string;
  type: LiveEventType;
  text: string;
  minute: string;        // "67'"
  clockValue: number;    // seconds into match (or NaN-safe 0)
  wallclock: number;     // ms since epoch — approximate
  team: { code: string; name: string; color: string };
  scorer?: string;
  // Score AT THE TIME of the event (best-effort — only meaningful for goals).
  homeScore?: number;
  awayScore?: number;
  homeCode: string;
  awayCode: string;
  homeName: string;
  awayName: string;
};

export type LiveEventsResponse = {
  ok: boolean;
  events: LiveEventItem[];
  serverTime: number;
};

// 10 minutes of "just finished" window — matches the spec's catch-up tail.
const JUST_FINISHED_MS = 10 * 60_000;

type EspnSummaryPlay = {
  id?: string | number;
  sequence?: string | number;
  type?: { id?: string | number; text?: string };
  text?: string;
  shortText?: string;
  clock?: { value?: number; displayValue?: string };
  team?: { id?: string };
  scoringPlay?: boolean;
  participants?: Array<{ athlete?: { displayName?: string; shortName?: string }; type?: string }>;
};

type EspnCommentary = {
  sequence?: number;
  time?: { value?: number; displayValue?: string };
  text?: string;
  play?: EspnSummaryPlay;
};

type EspnSummary = {
  plays?: EspnSummaryPlay[];
  commentary?: EspnCommentary[];
  keyEvents?: EspnSummaryPlay[];
};

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
    } catch { /* try next */ }
  }
  return null;
}

async function fetchCandidateEvents(): Promise<EspnEvent[]> {
  const wcDates = groupStageRange();
  const frDates = friendlyWindowRange();
  const [wc, fr] = await Promise.allSettled([
    fetchScoreboard(wcDates, "fifa.world"),
    fetchScoreboard(frDates, "fifa.friendly"),
  ]);
  const all: EspnEvent[] = [];
  if (wc.status === "fulfilled") all.push(...(wc.value.events || []));
  if (fr.status === "fulfilled") all.push(...(fr.value.events || []));
  const now = Date.now();
  return all.filter(e => {
    const st = e.status?.type?.state;
    if (st === "in") return true;
    if (st === "post") {
      // Approximate finish-time: kickoff + 110m (90' + stoppage + HT). Good
      // enough to include matches that ended within the last 10 minutes.
      const kickoff = Date.parse(e.date);
      if (!Number.isFinite(kickoff)) return false;
      const estFinish = kickoff + 110 * 60_000;
      return now - estFinish < JUST_FINISHED_MS;
    }
    return false;
  });
}

function fixtureFor(e: EspnEvent, fixtures: GroupFixture[]): GroupFixture | null {
  const c = e.competitions[0];
  const h = c.competitors.find(cp => cp.homeAway === "home");
  const a = c.competitors.find(cp => cp.homeAway === "away");
  if (!h || !a) return null;
  const hCode = normalizeAbbr(h.team.abbreviation);
  const aCode = normalizeAbbr(a.team.abbreviation);
  const cdmxDate = new Date(e.date).toLocaleDateString("en-CA", { timeZone: "America/Mexico_City" });
  const isoDate = e.date.slice(0, 10);
  return fixtures.find(fx =>
    ((fx.home === hCode && fx.away === aCode) || (fx.home === aCode && fx.away === hCode)) &&
    (fx.date === cdmxDate || fx.date === isoDate),
  ) || null;
}

function colorFor(team?: { color?: string; alternateColor?: string }): string {
  const raw = team?.color || team?.alternateColor;
  if (!raw) return "#5E5BFF";
  return raw.startsWith("#") ? raw : `#${raw}`;
}

// Map an ESPN play to a LiveEventType. Goals are detected via `scoringPlay`
// (more reliable than typeText for goals — penalty goals are still typeText
// "Penalty - Scored" but scoringPlay=true). For everything else we lean on
// typeText, which is the only ESPN field we can trust per the drama route.
function classify(typeText: string | undefined, isScoring: boolean): LiveEventType | null {
  if (isScoring) return "goal";
  const txt = (typeText || "").toLowerCase();
  if (!txt) return null;
  // VAR — string match, never trust the id.
  if (txt.includes("var ") || txt.startsWith("var") || txt.includes("video review")) return "var";
  // Red card — explicit, plus the "second yellow → red" variants.
  if (txt === "red card" || txt.includes("red card") || txt.includes("second yellow card")) return "red";
  // Penalty AWARDED only. Reject conversion / miss / save so we don't
  // double-fire alongside the resulting goal.
  if ((txt === "penalty" || txt === "penalty awarded") &&
      !txt.includes("missed") && !txt.includes("saved") && !txt.includes("scored")) return "penalty";
  // Substitution.
  if (txt === "substitution" || txt.includes("substitution")) return "sub";
  return null;
}

function scorerName(play: EspnSummaryPlay): string | undefined {
  const p = play.participants?.find(x => x.type === "scorer" || x.type === "Scorer") ?? play.participants?.[0];
  return p?.athlete?.shortName || p?.athlete?.displayName;
}

export async function GET(request: NextRequest) {
  try {
    const sinceMsRaw = request.nextUrl.searchParams.get("sinceMs");
    const sinceMs = Math.max(0, Math.min(JUST_FINISHED_MS, Number.parseInt(sinceMsRaw || "0", 10) || 0));
    const cutoff = sinceMs > 0 ? Date.now() - sinceMs : 0;

    const fixtureIdsParam = request.nextUrl.searchParams.get("fixtureIds");
    const fixtureIdsFilter = fixtureIdsParam
      ? new Set(fixtureIdsParam.split(",").map(s => s.trim()).filter(Boolean))
      : null;

    const candidate = await fetchCandidateEvents();
    if (candidate.length === 0) {
      const empty: LiveEventsResponse = { ok: true, events: [], serverTime: Date.now() };
      return NextResponse.json(empty, {
        headers: { "Cache-Control": "public, max-age=4, stale-while-revalidate=10" },
      });
    }

    const fixtures = allGroupFixtures();
    const summaries = await Promise.all(candidate.map(async (e) => ({
      e,
      summary: await fetchSummary(e.id),
    })));

    const out: LiveEventItem[] = [];

    for (const { e, summary } of summaries) {
      if (!summary) continue;
      const fx = fixtureFor(e, fixtures);
      if (!fx) continue;
      if (fixtureIdsFilter && !fixtureIdsFilter.has(fx.id)) continue;

      const comp = e.competitions[0];
      const h = comp.competitors.find(cp => cp.homeAway === "home");
      const a = comp.competitors.find(cp => cp.homeAway === "away");
      if (!h || !a) continue;
      const espnHomeCode = normalizeAbbr(h.team.abbreviation);
      const espnAwayCode = normalizeAbbr(a.team.abbreviation);
      const teamByEspnId = new Map<string, { code: string; name: string; color: string }>();
      if (h.team?.id) {
        const ourTeam = TEAMS.find(t => t.code === espnHomeCode);
        teamByEspnId.set(h.team.id, {
          code: espnHomeCode,
          name: ourTeam?.name || h.team.displayName || espnHomeCode,
          color: colorFor(h.team),
        });
      }
      if (a.team?.id) {
        const ourTeam = TEAMS.find(t => t.code === espnAwayCode);
        teamByEspnId.set(a.team.id, {
          code: espnAwayCode,
          name: ourTeam?.name || a.team.displayName || espnAwayCode,
          color: colorFor(a.team),
        });
      }
      const homeName = TEAMS.find(t => t.code === espnHomeCode)?.name || h.team.displayName || espnHomeCode;
      const awayName = TEAMS.find(t => t.code === espnAwayCode)?.name || a.team.displayName || espnAwayCode;

      const kickoffMs = Date.parse(e.date);

      // Walk commentary + keyEvents. commentary holds the rich `text`,
      // keyEvents catches things commentary might skip during fast bursts.
      const seenSig = new Set<string>();
      const collected: Array<{ play: EspnSummaryPlay; text?: string; minute?: string }> = [];
      for (const c of summary.commentary || []) {
        if (c.play) collected.push({ play: c.play, text: c.text || c.play.text || c.play.shortText, minute: c.play.clock?.displayValue || c.time?.displayValue });
      }
      for (const k of summary.keyEvents || []) {
        collected.push({ play: k, text: k.text || k.shortText, minute: k.clock?.displayValue });
      }

      for (const { play, text, minute } of collected) {
        const cat = classify(play.type?.text, !!play.scoringPlay);
        if (!cat) continue;
        const clockValue = typeof play.clock?.value === "number" ? play.clock.value : 0;
        const wallclock = Number.isFinite(kickoffMs)
          ? kickoffMs + Math.round(clockValue * 1000)
          : Date.now();
        if (cutoff && wallclock < cutoff) continue;

        // Signature: prefer ESPN's play id when present (most stable),
        // otherwise fall back to (fixture, category, clock, teamId) which is
        // unique enough since two same-category events at the same clock for
        // the same team are vanishingly rare.
        const espnPlayId = play.id != null ? String(play.id) : null;
        const sig = espnPlayId
          ? `${fx.id}|${espnPlayId}`
          : `${fx.id}|${cat}|${Math.round(clockValue)}|${play.team?.id ?? "?"}`;
        if (seenSig.has(sig)) continue;
        seenSig.add(sig);

        const teamMeta = play.team?.id ? teamByEspnId.get(play.team.id) : undefined;
        // Goals: pull live score from the scoreboard now (close-enough — the
        // overlay's hero text is "GOOOL" + scoreline; perfect history isn't
        // critical and ESPN doesn't expose per-play running score reliably).
        const hgRaw = Number(h.score);
        const agRaw = Number(a.score);

        out.push({
          id: sig,
          fixtureId: fx.id,
          type: cat,
          text: text || play.type?.text || "",
          minute: minute || "",
          clockValue,
          wallclock,
          team: teamMeta || {
            code: espnHomeCode,
            name: homeName,
            color: colorFor(h.team),
          },
          scorer: cat === "goal" || cat === "sub" ? scorerName(play) : undefined,
          homeScore: Number.isFinite(hgRaw) ? hgRaw : undefined,
          awayScore: Number.isFinite(agRaw) ? agRaw : undefined,
          homeCode: espnHomeCode,
          awayCode: espnAwayCode,
          homeName,
          awayName,
        });
      }
    }

    // Sort oldest → newest so the client plays the catch-up queue in
    // chronological order.
    out.sort((x, y) => x.wallclock - y.wallclock);

    const body: LiveEventsResponse = { ok: true, events: out, serverTime: Date.now() };
    return NextResponse.json(body, {
      headers: { "Cache-Control": "public, max-age=4, stale-while-revalidate=10" },
    });
  } catch (err) {
    console.error("[/api/live/events] error", err);
    return NextResponse.json(
      { ok: false, events: [], serverTime: Date.now() } satisfies LiveEventsResponse,
      { status: 500 },
    );
  }
}
