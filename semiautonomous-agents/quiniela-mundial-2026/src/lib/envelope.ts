// Shared types + helpers for the "Sobre del día" (daily envelope) feature.
// The envelope is a NON-POINTS reward: visual collectibles, personal AVA
// stats, future-fixture spoilers, cromo previews, or AVA challenges. None
// of these touch `quiniela_charales_picks` or the leaderboard.
//
// Storage:
//   daily_envelopes/{playerId}/opens/{YYYY-MM-DD}  — one doc per open
//   player_unlocks/{playerId}                      — cumulative collection

export type RewardType = "visual" | "insight" | "spoiler" | "preview" | "reto";

export type VisualReward = {
  type: "visual";
  unlockId: string;          // matches VISUAL_UNLOCKS[id]
};

export type InsightReward = {
  type: "insight";
  text: string;              // 1-2 Spanish sentences from Gemini
  basedOn: { decided: number; signHits: number; exactHits: number; score: number };
};

export type SpoilerReward = {
  type: "spoiler";
  fixtureId: string;
  home: string;
  away: string;
  kickoffMs: number;
  probabilities: { home: number; draw: number; away: number };
  hotTake: string;           // Spanish "AVA's hot take" string
};

export type PreviewReward = {
  type: "preview";
  date: string;              // YYYY-MM-DD (4-7 days ahead)
  styleName: string;
  styleLabel: string;        // human-readable label, e.g. "Vaporwave"
};

export type RetoReward = {
  type: "reto";
  fixtureId: string;
  home: string;
  away: string;
  kickoffMs: number;
  aiPick: "H" | "D" | "A";
  status: "pending" | "won" | "lost" | "missed";
};

export type EnvelopeReward = VisualReward | InsightReward | SpoilerReward | PreviewReward | RetoReward;

export type EnvelopeOpenDoc = {
  date: string;              // YYYY-MM-DD (ET)
  openedAt: number;
  reward: EnvelopeReward;
};

// Cumulative collection — each unlock recorded as a small entry.
export type UnlockEntry = {
  type: RewardType | "badge";
  id: string;                // visual unlock id, fixtureId, badge id, etc.
  awardedAt: number;
  // Inline payload so the gallery doesn't need a second fetch.
  payload: EnvelopeReward | BadgePayload;
};

export type BadgePayload = {
  type: "badge";
  badgeId: string;
  label: string;
  description?: string;
};

// Weights — must sum to 100. Owner-defined in the brief.
export const REWARD_WEIGHTS: Record<RewardType, number> = {
  visual:  35,
  insight: 25,
  spoiler: 15,
  preview: 15,
  reto:    10,
};

// Weighted random pick of a reward type.
export function pickRewardType(rand: number = Math.random()): RewardType {
  let cumulative = 0;
  const r = rand * 100;
  const order: RewardType[] = ["visual", "insight", "spoiler", "preview", "reto"];
  for (const t of order) {
    cumulative += REWARD_WEIGHTS[t];
    if (r < cumulative) return t;
  }
  return "visual";
}

// Compute the millis until the next ET-midnight (envelope rolls at 00:00 ET).
export function msUntilNextEtMidnight(now: number = Date.now()): number {
  // Get today's date string in ET, then build the start of "tomorrow" in ET.
  const fmt = new Intl.DateTimeFormat("en-CA", {
    timeZone: "America/New_York",
    year: "numeric", month: "2-digit", day: "2-digit",
  });
  const todayEt = fmt.format(new Date(now));
  const [y, m, d] = todayEt.split("-").map(n => parseInt(n, 10));
  // Tomorrow at 00:00 ET = today's ET midnight + 24h.
  // We compute "today 00:00 ET" by taking ET-noon UTC and subtracting 12h then
  // adding offset compensation — too fragile. Instead, sweep: from now, add
  // hours until the ET date string flips. Cheap and DST-safe.
  const target = Date.UTC(y, m - 1, d) + 86_400_000; // not exact but bounded
  // Compensate: walk back hours until just past the ET midnight transition.
  // Simpler: try a few candidate UTC times and find the smallest > now whose
  // ET date is the next day at the day boundary.
  let best = target + 12 * 3600_000;
  for (let h = -14; h <= 14; h++) {
    const cand = target + h * 3600_000;
    if (cand <= now) continue;
    const candEt = fmt.format(new Date(cand));
    if (candEt > todayEt) {
      // Walk back to find the boundary minute.
      let lo = cand - 3600_000;
      let hi = cand;
      while (hi - lo > 60_000) {
        const mid = Math.floor((lo + hi) / 2);
        const midEt = fmt.format(new Date(mid));
        if (midEt > todayEt) hi = mid; else lo = mid;
      }
      if (hi < best) best = hi;
      break;
    }
  }
  return Math.max(0, best - now);
}

export function etTodayKey(now: number = Date.now()): string {
  return new Intl.DateTimeFormat("en-CA", {
    timeZone: "America/New_York",
    year: "numeric", month: "2-digit", day: "2-digit",
  }).format(new Date(now));
}
