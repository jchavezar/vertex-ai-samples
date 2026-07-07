// "Momento más caliente" — scan all in-progress fixtures for a recent
// dramatic play (VAR review / red card / penalty awarded) and surface ONE
// hot fixture to the home page. The home only polls this while a live match
// is in progress (see DramaSpotlight). Returns null when nothing is hot.
//
// Drama detection: we look at the LATEST play of each in-progress event and
// classify by ESPN's play `type.id` first (stable) and `type.text` second
// (resilient when ids drift). A play is "hot" while:
//   - it happened in the last 90s (commentary clock ≥ current match minute - ~2)
//   - its category is var | redCard | penaltyAwarded
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

export type DramaCategory = "var" | "red" | "penalty";

export type DramaHit = {
  fixtureId: string;
  fixture: GroupFixture;
  category: DramaCategory;
  minute: string;
  text?: string;
  teamAbbr?: string;
  homeScore: number;
  awayScore: number;
  // Approximation of when the play happened (ms since epoch) so the client
  // can hide the banner ~90s later without re-polling. Falls back to "now"
  // since ESPN play timestamps are not real wall-clock.
  detectedAt: number;
};

export type DramaResponse = {
  ok: boolean;
  hit: DramaHit | null;
  serverTime: number;
};

// ESPN soccer play type ids — observed live in the wild on 2026-06-18:
//   70 = Goal               (NOT a "penalty awarded" — fixed)
//   80 = Kickoff
//   66 = Foul
//   94 = Yellow Card        (previously misclassified as red — fixed)
//   95 = Corner Awarded
//   106 = Shot On Target
//   117 = Shot Off Target
//   135 = Shot Blocked
//
// We DO NOT trust the typeId map for red/penalty disambiguation because we've
// already been burned twice. Use the typeText string as the source of truth.
// Only the explicit VAR id is safe enough to short-circuit on.
const SAFE_TYPE_IDS: Record<string, DramaCategory> = {
  // Intentionally empty until we have field-confirmed ids for red & penalty.
};

function categorize(typeId: string | undefined, typeText: string | undefined): DramaCategory | null {
  if (typeId && SAFE_TYPE_IDS[typeId]) return SAFE_TYPE_IDS[typeId];
  const txt = (typeText || "").toLowerCase();
  if (!txt) return null;
  // VAR review.
  if (txt.includes("var ") || txt.startsWith("var") || txt.includes("video review")) return "var";
  // Red card — explicit match only. Yellow cards (typeText "Yellow Card") do
  // NOT match because "yellow card" doesn't contain "red". Second-yellow→red
  // ESPN labels as "Second Yellow Card" or "Red Card (Second Yellow)" — both
  // contain "red"… EXCEPT the bare "Second Yellow Card" form, which we also
  // catch via the explicit `"second yellow"` substring check.
  if (txt === "red card" || txt.includes("red card") || txt.includes("second yellow card")) return "red";
  // Penalty AWARDED only — not "penalty missed" or "penalty saved" or "penalty kick".
  // ESPN's typical text is "Penalty" or "Penalty Awarded". We need to match
  // the awarded moment, not the conversion / miss.
  if ((txt === "penalty" || txt === "penalty awarded") && !txt.includes("missed") && !txt.includes("saved")) return "penalty";
  return null;
}

type EspnSummaryPlay = {
  id?: string | number;
  sequence?: string | number;
  type?: { id?: string | number; text?: string };
  text?: string;
  shortText?: string;
  clock?: { value?: number; displayValue?: string };
  team?: { id?: string };
};

type EspnKeyEvent = EspnSummaryPlay;
type EspnCommentary = {
  sequence?: number;
  time?: { value?: number; displayValue?: string };
  text?: string;
  play?: EspnSummaryPlay;
};

type EspnSummary = {
  plays?: EspnSummaryPlay[];
  commentary?: EspnCommentary[];
  keyEvents?: EspnKeyEvent[];
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

async function fetchLiveEvents(): Promise<EspnEvent[]> {
  const wcDates = groupStageRange();
  const frDates = friendlyWindowRange();
  const [wc, fr] = await Promise.allSettled([
    fetchScoreboard(wcDates, "fifa.world"),
    fetchScoreboard(frDates, "fifa.friendly"),
  ]);
  const events: EspnEvent[] = [];
  if (wc.status === "fulfilled") events.push(...(wc.value.events || []));
  if (fr.status === "fulfilled") events.push(...(fr.value.events || []));
  return events.filter(e => e.status.type.state === "in");
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

function latestPlays(summary: EspnSummary): Array<{ typeId?: string; typeText?: string; text?: string; minute?: string; teamId?: string; clockValue?: number }> {
  const out: Array<{ typeId?: string; typeText?: string; text?: string; minute?: string; teamId?: string; clockValue?: number }> = [];
  for (const c of summary.commentary || []) {
    const p = c.play;
    out.push({
      typeId: p?.type?.id != null ? String(p.type.id) : undefined,
      typeText: p?.type?.text,
      text: c.text || p?.text || p?.shortText,
      minute: p?.clock?.displayValue || c.time?.displayValue,
      teamId: p?.team?.id,
      clockValue: typeof p?.clock?.value === "number" ? p.clock.value : (typeof c.time?.value === "number" ? c.time.value : undefined),
    });
  }
  for (const k of summary.keyEvents || []) {
    out.push({
      typeId: k.type?.id != null ? String(k.type.id) : undefined,
      typeText: k.type?.text,
      text: k.text || k.shortText,
      minute: k.clock?.displayValue,
      teamId: k.team?.id,
      clockValue: typeof k.clock?.value === "number" ? k.clock.value : undefined,
    });
  }
  return out.sort((a, b) => (b.clockValue ?? -1) - (a.clockValue ?? -1));
}

export async function GET() {
  try {
    const liveEvents = await fetchLiveEvents();
    if (liveEvents.length === 0) {
      const empty: DramaResponse = { ok: true, hit: null, serverTime: Date.now() };
      return NextResponse.json(empty);
    }
    const fixtures = allGroupFixtures();

    // Pull summaries in parallel, then pick the most recent dramatic play
    // across the bunch.
    const summaries = await Promise.all(liveEvents.map(async (e) => ({
      e,
      summary: await fetchSummary(e.id),
    })));

    let best: DramaHit | null = null;
    let bestClock = -1;

    for (const { e, summary } of summaries) {
      if (!summary) continue;
      const fx = fixtureFor(e, fixtures);
      if (!fx) continue;
      const c = e.competitions[0];
      const h = c.competitors.find(cp => cp.homeAway === "home");
      const a = c.competitors.find(cp => cp.homeAway === "away");
      if (!h || !a) continue;
      const teamIdToAbbr = new Map<string, string>();
      if (h.team?.id) teamIdToAbbr.set(h.team.id, normalizeAbbr(h.team.abbreviation));
      if (a.team?.id) teamIdToAbbr.set(a.team.id, normalizeAbbr(a.team.abbreviation));
      const hgRaw = Number(h.score);
      const agRaw = Number(a.score);
      const hg = Number.isFinite(hgRaw) ? hgRaw : 0;
      const ag = Number.isFinite(agRaw) ? agRaw : 0;
      const ourHomeIsEspnHome = fx.home === normalizeAbbr(h.team.abbreviation);
      const homeScore = ourHomeIsEspnHome ? hg : ag;
      const awayScore = ourHomeIsEspnHome ? ag : hg;

      // Look at the freshest few plays only — older dramas have already
      // resolved or been overshadowed.
      const plays = latestPlays(summary).slice(0, 12);
      // The "match-minute" is approximated by ESPN's displayClock (e.g. "67'").
      const matchMinute = Number.parseInt(e.status.displayClock || "0", 10);
      for (let pi = 0; pi < plays.length; pi++) {
        const p = plays[pi];
        const cat = categorize(p.typeId, p.typeText);
        if (!cat) continue;
        // clockValue is in SECONDS; matchMinute is in MINUTES — must convert.
        // Bug pre-fix: treating seconds as minutes made matchMinute - playMinute
        // always very negative, so the stale filter never triggered.
        const playMinutes = typeof p.clockValue === "number" ? p.clockValue / 60 : matchMinute;
        // Stale window: a drama older than 3 match-minutes is no longer hot.
        if (Number.isFinite(matchMinute) && Number.isFinite(playMinutes) && matchMinute - playMinutes > 3) continue;

        // VAR resolution: if any play that happened AFTER this VAR contains a
        // decision text (VAR confirmed/reversed, goal confirmed/disallowed), the
        // VAR moment is over. Skip it so the banner disappears.
        // plays[] is sorted DESC by clockValue, so indices 0..pi-1 are more recent.
        if (cat === "var") {
          const newerPlays = plays.slice(0, pi);
          const resolved = newerPlays.some(np => {
            const txt = (np.text || np.typeText || "").toLowerCase();
            return txt.includes("var decision") ||
                   txt.includes("goal confirmed") ||
                   txt.includes("goal disallowed") ||
                   txt.includes("no goal") ||
                   txt.includes("decision");
          });
          if (resolved) continue;
        }

        if ((p.clockValue ?? -1) > bestClock) {
          bestClock = p.clockValue ?? -1;
          best = {
            fixtureId: fx.id,
            fixture: fx,
            category: cat,
            minute: p.minute || e.status.displayClock || "",
            text: p.text,
            teamAbbr: p.teamId ? teamIdToAbbr.get(p.teamId) : undefined,
            homeScore,
            awayScore,
            detectedAt: Date.now(),
          };
        }
      }
    }

    const body: DramaResponse = { ok: true, hit: best, serverTime: Date.now() };
    return NextResponse.json(body, { headers: { "Cache-Control": "no-store" } });
  } catch (e) {
    console.error("[/api/live/drama] error", e);
    return NextResponse.json({ ok: false, hit: null, serverTime: Date.now() } satisfies DramaResponse, { status: 500 });
  }
}
