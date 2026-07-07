// Pure-function form of /api/scoreboard so it can be invoked in-process
// (e.g. from the home snapshot endpoint) without going through HTTP.
//
// 1:1 with the route.ts logic — keep them in sync.

import { fetchScoreboard, groupStageRange, friendlyWindowRange, type EspnEvent } from "@/lib/espn";

export type ScoreboardPayload = {
  ok: true;
  events: EspnEvent[];
  leagues: unknown[];
  partialErrors: string[];
};

async function safe(p: Promise<unknown>) {
  try { return { ok: true as const, value: await p }; }
  catch (e) { return { ok: false as const, error: e instanceof Error ? e.message : String(e) }; }
}

export async function computeScoreboard(wcDatesOverride?: string): Promise<ScoreboardPayload | { ok: false; error: string }> {
  const wcDates = wcDatesOverride || groupStageRange();
  const friendlyDates = friendlyWindowRange();

  const [wc, fr] = await Promise.all([
    safe(fetchScoreboard(wcDates, "fifa.world")),
    safe(fetchScoreboard(friendlyDates, "fifa.friendly")),
  ]);

  const events: EspnEvent[] = [];
  const errors: string[] = [];
  let leagues: unknown[] = [];

  if (wc.ok && wc.value) {
    const v = wc.value as { events?: EspnEvent[]; leagues?: unknown[] };
    leagues = v.leagues || [];
    for (const e of v.events || []) events.push({ ...e, competition: "world" });
  } else if (!wc.ok) errors.push(`world:${wc.error}`);

  if (fr.ok && fr.value) {
    const v = fr.value as { events?: EspnEvent[] };
    for (const e of v.events || []) events.push({ ...e, competition: "friendly" });
  } else if (!fr.ok) errors.push(`friendly:${fr.error}`);

  if (!events.length && errors.length) {
    return { ok: false, error: errors.join(" | ") };
  }
  return { ok: true, events, leagues, partialErrors: errors };
}

export function anyLiveEvent(events: EspnEvent[]): boolean {
  return events.some(e => e?.status?.type?.state === "in");
}
