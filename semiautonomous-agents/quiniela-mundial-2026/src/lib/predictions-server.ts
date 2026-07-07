// Firestore mirror for player Mundial predictions. Auto-saved from the client
// so switching browsers / clearing cache / changing UI never loses picks.
import { db } from "@/lib/firestore-server";
import { allGroupFixtures } from "@/data/groups";
import { isFixtureLocked, isBracketRoundLocked, isKOSlotLocked } from "@/lib/fixture-time";

export const PICKS_COLLECTION = "quiniela_charales_picks";

export async function getPicks(playerId: string): Promise<Record<string, unknown> | null> {
  const snap = await db.collection(PICKS_COLLECTION).doc(playerId).get();
  if (!snap.exists) return null;
  return snap.data() as Record<string, unknown>;
}

type GroupPick = { pick?: string; homeGoals?: number; awayGoals?: number; source?: string; aiAt?: number };
type BracketPayload = { R32?: string[]; R16?: string[]; QF?: string[]; SF?: string[]; THIRD?: string; FINAL?: string };
type PicksPayload = {
  group?: Record<string, GroupPick>;
  bracket?: BracketPayload;
  champion?: string;
  runnerUp?: string;
  championLockedAt?: string;
  runnerUpLockedAt?: string;
  updatedAt?: number;
};

const FIXTURE_BY_ID = new Map(allGroupFixtures().map(fx => [fx.id, fx]));

// Server-side lock enforcement: clients can be tricked or run stale, so the
// server is the source of truth. For every locked fixture we keep whatever
// was in the doc before — if nothing was there, the late attempt is dropped.
function mergeWithServerLocks(existing: PicksPayload | null, incoming: PicksPayload): PicksPayload {
  const prev = existing ?? {};
  const merged: PicksPayload = { ...incoming };

  // GROUPS: per-fixture lock by kickoff
  const incomingGroup = incoming.group ?? {};
  const prevGroup = prev.group ?? {};
  const nextGroup: Record<string, GroupPick> = {};
  const allKeys = new Set([...Object.keys(prevGroup), ...Object.keys(incomingGroup)]);
  for (const fxId of allKeys) {
    const fx = FIXTURE_BY_ID.get(fxId);
    const locked = fx ? isFixtureLocked(fx) : false;
    if (locked) {
      if (prevGroup[fxId]) nextGroup[fxId] = prevGroup[fxId];
      continue;
    }
    if (incomingGroup[fxId]) nextGroup[fxId] = incomingGroup[fxId];
    else if (prevGroup[fxId]) nextGroup[fxId] = prevGroup[fxId];
  }
  merged.group = nextGroup;

  // BRACKET: per-slot lock for R32; per-round lock for the rest.
  const prevBracket = prev.bracket ?? {};
  const incomingBracket = incoming.bracket ?? {};
  const nextBracket: BracketPayload = {};

  // R32: each of the 16 slots locks at its own kickoff time.
  const prevR32 = (prevBracket.R32 as string[] | undefined) ?? [];
  const incomingR32 = (incomingBracket.R32 as string[] | undefined) ?? [];
  const nextR32: string[] = [];
  for (let i = 0; i < 16; i++) {
    const slotLocked = isKOSlotLocked(`R32-${i + 1}`);
    nextR32.push(slotLocked ? (prevR32[i] ?? "") : (incomingR32[i] ?? prevR32[i] ?? ""));
  }
  nextBracket.R32 = nextR32;

  // R16/QF/SF: per-slot non-empty merge (same pattern as R32) so concurrent
  // saves from multiple devices don't wipe each other's picks.
  const ROUND_SIZES: Record<string, number> = { R16: 8, QF: 4, SF: 2 };
  const arrayRounds: Array<keyof BracketPayload> = ["R16", "QF", "SF"];
  for (const r of arrayRounds) {
    const lockKey = r;
    const locked = isBracketRoundLocked(lockKey as "R16" | "QF" | "SF");
    const size = ROUND_SIZES[r] ?? 0;
    if (!size) continue;
    if (locked) {
      // Round locked: preserve whatever was saved before; ignore incoming.
      const v = prevBracket[r] as string[] | undefined;
      if (v && v.length > 0) (nextBracket[r] as string[]) = [...v];
    } else {
      // Round open: per-slot merge — incoming pick wins if non-empty, else keep prev.
      const inc = (incomingBracket[r] as string[] | undefined) ?? [];
      const prv = (prevBracket[r] as string[] | undefined) ?? [];
      const merged_slots: string[] = Array(size).fill("");
      for (let i = 0; i < size; i++) {
        merged_slots[i] = inc[i] || prv[i] || "";
      }
      (nextBracket[r] as string[]) = merged_slots;
    }
  }
  // THIRD/FINAL: single string, round-level lock.
  for (const r of ["THIRD", "FINAL"] as const) {
    const locked = isBracketRoundLocked("FINAL");
    const v = (locked ? prevBracket[r] : incomingBracket[r]) as string | undefined;
    // Prefer prev if incoming is empty (don't erase an existing pick).
    const final_v = (locked ? v : (incomingBracket[r] as string | undefined) || (prevBracket[r] as string | undefined));
    if (final_v) (nextBracket[r] as string) = final_v;
  }
  merged.bracket = nextBracket;

  // Champion / runner-up stay editable — the decaying bonus handles late picks.
  return merged;
}

export async function upsertPicks(
  playerId: string,
  payload: Record<string, unknown>,
): Promise<Record<string, unknown>> {
  const ref = db.collection(PICKS_COLLECTION).doc(playerId);
  const existing = (await ref.get()).data() as PicksPayload | undefined;
  const merged = mergeWithServerLocks(existing ?? null, payload as PicksPayload);
  const next = { ...merged, playerId, updatedAt: Date.now() };
  await ref.set(next, { merge: false });
  return next as Record<string, unknown>;
}
