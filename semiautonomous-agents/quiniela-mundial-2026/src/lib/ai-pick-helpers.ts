// Client helpers for the /quiniela page: count and undo AI picks.
import type { PlayerPredictions } from "@/lib/predictions";

export function aiPickCount(p: PlayerPredictions): number {
  return Object.values(p.group).filter(g => g?.source === "ai").length;
}

export function undoAiPicks(p: PlayerPredictions): PlayerPredictions {
  const next: PlayerPredictions = { ...p, group: {} };
  for (const [fxId, pick] of Object.entries(p.group)) {
    if (pick?.source === "ai") continue;
    next.group[fxId] = pick;
  }
  return next;
}
