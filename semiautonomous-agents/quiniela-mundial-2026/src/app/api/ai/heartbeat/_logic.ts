// Shared reader for the latest AVA pick snapshot. Used by ./route.ts and
// by /api/home/snapshot.

import { db } from "@/lib/firestore-server";
import { AI_PICK_HISTORY_COLLECTION, type AiPickSnapshot } from "@/lib/ai-state-server";
import { allGroupFixtures } from "@/data/groups";

function clipReasoning(text: string | undefined | null): string {
  if (!text) return "";
  const trimmed = text.trim().replace(/\s+/g, " ");
  if (trimmed.length <= 140) return trimmed;
  return trimmed.slice(0, 137) + "…";
}

export type HeartbeatPayload = {
  fixtureId: string;
  fixtureLabel: string;
  ts: number;
  pick: "H" | "D" | "A";
  prevPick: "H" | "D" | "A" | null;
  reasoning?: string;
};

export async function fetchLatestHeartbeat(): Promise<HeartbeatPayload | null> {
  const snap = await db
    .collection(AI_PICK_HISTORY_COLLECTION)
    .orderBy("ts", "desc")
    .limit(1)
    .get();
  if (snap.empty) return null;
  const doc = snap.docs[0].data() as AiPickSnapshot;
  const fx = allGroupFixtures().find(f => f.id === doc.fixtureId);
  const label = fx ? `${fx.home} vs ${fx.away}` : doc.fixtureId;
  return {
    fixtureId: doc.fixtureId,
    fixtureLabel: label,
    ts: doc.ts ?? 0,
    pick: doc.pick,
    prevPick: doc.prevPick ?? null,
    reasoning: clipReasoning(doc.reasoning),
  };
}
