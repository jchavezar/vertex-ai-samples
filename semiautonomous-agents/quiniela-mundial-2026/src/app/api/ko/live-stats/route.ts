// GET /api/ko/live-stats?eventId=<espnId>
// Proxies to ESPN summary endpoint, returns simplified stats

import { NextRequest } from "next/server";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

type StatRow = { name: string; displayValue: string };

export async function GET(req: NextRequest) {
  const eventId = req.nextUrl.searchParams.get("eventId");
  if (!eventId) return Response.json({ ok: false, error: "missing eventId" }, { status: 400 });

  try {
    const url = `https://site.api.espn.com/apis/site/v2/sports/soccer/FIFA.WORLD/summary?event=${eventId}`;
    const res = await fetch(url, { next: { revalidate: 20 } });
    if (!res.ok) throw new Error(`ESPN ${res.status}`);
    const data = await res.json();

    // Extract team stats from boxscore
    const teams = data?.boxscore?.teams ?? [];
    const statsMap: Record<string, Record<string, string>> = {};
    for (const t of teams) {
      const code = t.team?.abbreviation ?? "UNK";
      statsMap[code] = {};
      for (const s of (t.statistics ?? []) as StatRow[]) {
        statsMap[code][s.name] = s.displayValue;
      }
    }

    // Extract goal events from commentary
    const keyEvents: Array<{ type: string; clock: string; team?: string; athlete?: string; text?: string }> = [];
    for (const play of data?.commentary ?? []) {
      const t = play.type?.id;
      if (["goal", "yellow_card", "red_card", "substitution"].includes(t)) {
        keyEvents.push({
          type: t,
          clock: play.clock?.displayValue ?? "",
          team: play.team?.abbreviation,
          athlete: play.athlete?.displayName,
          text: play.text,
        });
      }
    }

    // Also check scoring plays
    for (const sp of data?.scoringPlays ?? []) {
      keyEvents.push({
        type: "goal",
        clock: sp.clock?.displayValue ?? "",
        team: sp.team?.abbreviation,
        athlete: sp.athletesInvolved?.[0]?.displayName,
        text: sp.text,
      });
    }

    return Response.json({ ok: true, statsMap, keyEvents, updatedAt: Date.now() });
  } catch (e) {
    return Response.json({ ok: false, error: (e as Error).message }, { status: 500 });
  }
}
