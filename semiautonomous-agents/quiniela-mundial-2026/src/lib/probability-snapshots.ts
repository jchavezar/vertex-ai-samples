// Firestore-backed snapshots for both per-fixture probabilities and
// per-team bracket probabilities. Two write paths per kind:
//   - `current` doc: latest snapshot (read-heavy endpoints).
//   - `history/{YYYY-MM-DD}` doc: one snapshot per UTC day (for sparkline UI).

import { db } from "@/lib/firestore-server";
import type { Probs } from "@/lib/probability-engine";

export const FIXTURE_PROBS_COLLECTION = "fixture_probabilities";
export const FIXTURE_PROBS_HISTORY = "fixture_probabilities_history";
export const BRACKET_PROBS_COLLECTION = "bracket_probabilities";
export const BRACKET_PROBS_HISTORY = "bracket_probabilities_history";

export type FixtureProbsEntry = {
  fixtureId: string;
  home: string;
  away: string;
  date: string;             // YYYY-MM-DD
  probs: Probs;
  market: Probs | null;
  homeXg?: number;
  awayXg?: number;
  components?: {
    model: Probs;
    formAdjustment: number;
    hostAdjustment: number;
  };
};

export type FixtureProbsDoc = {
  snapshotDate: string;     // YYYY-MM-DD (UTC)
  updatedAt: number;
  fixtures: Record<string, FixtureProbsEntry>;
  source: "blend-v2";
};

export type BracketTeamProbs = {
  code: string;
  pTop2: number;            // P(finish top 2 in group)
  pBest3rd: number;         // P(advance as best-third)
  pR32: number;             // P(reach R32, i.e. advance)
  pR16: number;
  pQF: number;
  pSF: number;
  pFinal: number;
  pChampion: number;
  // Group stage helpers for the UI
  expectedPoints: number;
  expectedGoalDiff: number;
};

export type BracketProbsDoc = {
  snapshotDate: string;
  updatedAt: number;
  simulations: number;
  teams: Record<string, BracketTeamProbs>;
};

function utcDateKey(now = Date.now()): string {
  const d = new Date(now);
  const y = d.getUTCFullYear();
  const mo = String(d.getUTCMonth() + 1).padStart(2, "0");
  const da = String(d.getUTCDate()).padStart(2, "0");
  return `${y}-${mo}-${da}`;
}

export async function readFixtureProbs(): Promise<FixtureProbsDoc | null> {
  const snap = await db.collection(FIXTURE_PROBS_COLLECTION).doc("current").get();
  return snap.exists ? (snap.data() as FixtureProbsDoc) : null;
}

export async function writeFixtureProbs(doc: Omit<FixtureProbsDoc, "snapshotDate" | "updatedAt">): Promise<FixtureProbsDoc> {
  const snapshotDate = utcDateKey();
  const updatedAt = Date.now();
  const payload: FixtureProbsDoc = { ...doc, snapshotDate, updatedAt };
  await db.collection(FIXTURE_PROBS_COLLECTION).doc("current").set(payload, { merge: false });
  await db.collection(FIXTURE_PROBS_HISTORY).doc(snapshotDate).set(payload, { merge: false });
  return payload;
}

export async function readBracketProbs(): Promise<BracketProbsDoc | null> {
  const snap = await db.collection(BRACKET_PROBS_COLLECTION).doc("current").get();
  return snap.exists ? (snap.data() as BracketProbsDoc) : null;
}

export async function writeBracketProbs(doc: Omit<BracketProbsDoc, "snapshotDate" | "updatedAt">): Promise<BracketProbsDoc> {
  const snapshotDate = utcDateKey();
  const updatedAt = Date.now();
  const payload: BracketProbsDoc = { ...doc, snapshotDate, updatedAt };
  await db.collection(BRACKET_PROBS_COLLECTION).doc("current").set(payload, { merge: false });
  await db.collection(BRACKET_PROBS_HISTORY).doc(snapshotDate).set(payload, { merge: false });
  return payload;
}

export async function listFixtureProbsHistory(limit = 90): Promise<FixtureProbsDoc[]> {
  const snap = await db.collection(FIXTURE_PROBS_HISTORY).orderBy("snapshotDate", "desc").limit(limit).get();
  return snap.docs.map(d => d.data() as FixtureProbsDoc);
}

export async function listBracketProbsHistory(limit = 90): Promise<BracketProbsDoc[]> {
  const snap = await db.collection(BRACKET_PROBS_HISTORY).orderBy("snapshotDate", "desc").limit(limit).get();
  return snap.docs.map(d => d.data() as BracketProbsDoc);
}
