// GET /api/bracket/ko-results
// Fetches ESPN knockout results and maps to KO_SCHEDULE slot identifiers.
// Returns { ok: true, slotResults: { "R32-1": "CAN" }, slotScores: { "R32-1": "0-4" } }

import { fetchScoreboard } from "@/lib/espn";
import { KO_SCHEDULE } from "@/data/knockout-schedule";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET() {
  try {
    const data = await fetchScoreboard("20260628-20260719", "fifa.world");
    const events = data.events || [];
    const slotResults: Record<string, string> = {};
    const slotScores: Record<string, string> = {};

    for (const slot of KO_SCHEDULE) {
      const slotUtcMs = new Date(slot.dateISO).getTime();
      const match = events.find(e => {
        const eMs = new Date(e.date).getTime();
        return Math.abs(eMs - slotUtcMs) < 2 * 60 * 60 * 1000;
      });
      if (!match) continue;
      if (match.status.type.state !== "post") continue;
      const comp = match.competitions[0];
      if (!comp) continue;
      let winner = comp.competitors.find((c: { winner?: boolean }) => c.winner);
      if (!winner) {
        const [h, a] = comp.competitors;
        if (h && a) winner = Number(h.score) > Number(a.score) ? h : a;
      }
      if (!winner) continue;
      slotResults[slot.slot] = winner.team.abbreviation;
      const [h, a] = comp.competitors;
      if (h && a) slotScores[slot.slot] = `${h.score ?? 0}-${a.score ?? 0}`;
    }

    return Response.json({ ok: true, slotResults, slotScores, updatedAt: Date.now() });
  } catch (e) {
    return Response.json({ ok: false, error: (e as Error).message }, { status: 500 });
  }
}
