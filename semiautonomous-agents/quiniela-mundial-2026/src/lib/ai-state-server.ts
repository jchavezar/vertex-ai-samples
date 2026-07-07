// Firestore mirror for the AI engine state: per-team delta from the curated
// strength baseline, the set of fixtures already ingested (idempotency), the
// initial probability snapshot per fixture (frozen), and the ordered event log.

import { db } from "@/lib/firestore-server";
import type { EloDelta, EloEvent } from "@/lib/elo-dynamic";
import type { Pick1X2 } from "@/lib/predictions";

export const AI_STATE_DOC = "ai_state/main";
export const AI_INITIAL_PROBS_DOC = "ai_state/initial_probs";
export const AI_MARKET_ODDS_DOC = "ai_state/market_odds";
export const AI_EVENT_LOG_COLLECTION = "ai_event_log";
export const AI_PICK_HISTORY_COLLECTION = "ai_pick_history";

export type AiState = {
  delta: EloDelta;
  ingestedFixtures: string[];
  lastSyncAt: number;
};

export type InitialProb = { H: number; D: number; A: number };
export type InitialProbsDoc = {
  fixtures: Record<string, InitialProb>;
  createdAt: number;
};

export async function getAiState(): Promise<AiState> {
  const snap = await db.doc(AI_STATE_DOC).get();
  if (!snap.exists) return { delta: {}, ingestedFixtures: [], lastSyncAt: 0 };
  const data = snap.data() as Partial<AiState>;
  return {
    delta: data.delta ?? {},
    ingestedFixtures: data.ingestedFixtures ?? [],
    lastSyncAt: data.lastSyncAt ?? 0,
  };
}

export async function setAiState(state: AiState): Promise<void> {
  await db.doc(AI_STATE_DOC).set(state, { merge: false });
}

export async function getInitialProbs(): Promise<InitialProbsDoc | null> {
  const snap = await db.doc(AI_INITIAL_PROBS_DOC).get();
  if (!snap.exists) return null;
  return snap.data() as InitialProbsDoc;
}

export async function setInitialProbs(doc: InitialProbsDoc): Promise<void> {
  await db.doc(AI_INITIAL_PROBS_DOC).set(doc, { merge: false });
}

export type MarketProb = { H: number; D: number; A: number; updatedAt: number };
export type MarketOddsDoc = {
  fixtures: Record<string, MarketProb>;
  updatedAt: number;
};

export async function getMarketOdds(): Promise<MarketOddsDoc | null> {
  const snap = await db.doc(AI_MARKET_ODDS_DOC).get();
  if (!snap.exists) return null;
  return snap.data() as MarketOddsDoc;
}

export async function setMarketOdds(doc: MarketOddsDoc): Promise<void> {
  await db.doc(AI_MARKET_ODDS_DOC).set(doc, { merge: false });
}

export async function appendEvent(event: EloEvent): Promise<void> {
  await db.collection(AI_EVENT_LOG_COLLECTION).doc(event.fixtureId).set(event, { merge: false });
}

export async function listEvents(limit = 100): Promise<EloEvent[]> {
  const snap = await db.collection(AI_EVENT_LOG_COLLECTION).orderBy("ts", "desc").limit(limit).get();
  return snap.docs.map(d => d.data() as EloEvent);
}

// ─────────────────────────────────────────────────────────────────────────────
// AI pick history — one entry per CHANGE the bot makes on a fixture's pick
// (or the first time the bot picks it). Lets the admin see the evolution
// across cron runs and answer "did the bot's churn pay off?".

export type AiPickSnapshot = {
  fixtureId: string;
  ts: number;                                  // cron run timestamp (shared per run)
  pick: "H" | "D" | "A";
  homeGoals?: number;
  awayGoals?: number;
  confidence?: number;
  reasoning?: string;
  prevPick?: "H" | "D" | "A" | null;           // pick this REPLACED
  prevReasoning?: string | null;
  source?: string;                             // "sync" | "manual" | "initial"
  blendedProbs?: { H: number; D: number; A: number };
  reasonerModel?: string;
};

export async function appendPickSnapshot(s: AiPickSnapshot): Promise<void> {
  await db.collection(AI_PICK_HISTORY_COLLECTION).add(s);
}

export async function listPickHistory(fixtureId?: string, limit = 500): Promise<AiPickSnapshot[]> {
  let q: FirebaseFirestore.Query = db.collection(AI_PICK_HISTORY_COLLECTION);
  if (fixtureId) q = q.where("fixtureId", "==", fixtureId);
  const snap = await q.orderBy("ts", "desc").limit(limit).get();
  return snap.docs.map(d => d.data() as AiPickSnapshot);
}

// Type re-export so callers don't need a second import for the pick literal.
export type { Pick1X2 };
