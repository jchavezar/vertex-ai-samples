// Predictions storage + scoring engine for the quiniela
import { PLAYERS } from "@/data/players";
import { allGroupFixtures, GROUPS } from "@/data/groups";
import { SCORING, CHAMPION_BONUS_MULTIPLIER, currentChampionLockRound, type ChampionLockRound } from "@/data/tournament";

// 1X2 pick + optional exact score for bonus
export type Pick1X2 = "H" | "D" | "A";

export type GroupPrediction = {
  pick: Pick1X2;
  homeGoals?: number;
  awayGoals?: number;
  source?: "ai" | "manual";
  aiAt?: number;
  // AI-only metadata: Gemini reasoning + the bot's own confidence so the UI
  // can show "por qué el bot escogió esto". Ignored for human picks.
  reasoning?: string;
  confidence?: number;
  reasonerModel?: string;
};

export type BracketPick = {
  R32?: string[]; // 16 winning team codes
  R16?: string[]; // 8
  QF?: string[];  // 4
  SF?: string[];  // 2
  THIRD?: string; // winner of 3rd place match
  FINAL?: string; // champion
};

export type PlayerPredictions = {
  playerId: string;
  group: Record<string, GroupPrediction>; // fixtureId -> prediction
  bracket: BracketPick;
  champion?: string;     // bonus pick
  runnerUp?: string;     // bonus pick
  championLockedAt?: ChampionLockRound;  // fase en la que se fijó/cambió el pick (define multiplicador)
  runnerUpLockedAt?: ChampionLockRound;
  updatedAt: number;
};

// Calcula el bonus actual (en pts) según la fase en la que se fijó el pick.
export function championBonusPoints(lockedAt: ChampionLockRound | undefined): number {
  const mult = lockedAt ? CHAMPION_BONUS_MULTIPLIER[lockedAt] : 1;
  return Math.round(SCORING.bonusChampion * mult);
}
export function runnerUpBonusPoints(lockedAt: ChampionLockRound | undefined): number {
  const mult = lockedAt ? CHAMPION_BONUS_MULTIPLIER[lockedAt] : 1;
  return Math.round(SCORING.bonusRunnerUp * mult);
}

// Helper para que la UI pueda preguntar "si lo cambio ahora, ¿cuánto vale?"
export function currentChampionBonusIfChangedNow(now: Date = new Date()): { round: ChampionLockRound; champion: number; runnerUp: number } {
  const round = currentChampionLockRound(now);
  return {
    round,
    champion: championBonusPoints(round),
    runnerUp: runnerUpBonusPoints(round),
  };
}

const KEY = (pid: string) => `q26_pred_${pid}`;

// Legacy v1 stored only homeGoals/awayGoals. Convert to v2 (pick + optional score).
type LegacyPrediction = { homeGoals?: number; awayGoals?: number; pick?: Pick1X2; source?: "ai" | "manual"; aiAt?: number; reasoning?: string; confidence?: number; reasonerModel?: string };

function migrateGroup(raw: Record<string, LegacyPrediction> | undefined): Record<string, GroupPrediction> {
  if (!raw) return {};
  const out: Record<string, GroupPrediction> = {};
  for (const [id, v] of Object.entries(raw)) {
    if (!v) continue;
    const extras: Pick<GroupPrediction, "source" | "aiAt" | "reasoning" | "confidence" | "reasonerModel"> = {};
    if (v.source === "ai" || v.source === "manual") extras.source = v.source;
    if (Number.isFinite(v.aiAt)) extras.aiAt = v.aiAt;
    if (typeof v.reasoning === "string" && v.reasoning.length > 0) extras.reasoning = v.reasoning;
    if (typeof v.confidence === "number" && Number.isFinite(v.confidence)) extras.confidence = v.confidence;
    if (typeof v.reasonerModel === "string" && v.reasonerModel.length > 0) extras.reasonerModel = v.reasonerModel;
    if (v.pick === "H" || v.pick === "D" || v.pick === "A") {
      out[id] = {
        pick: v.pick,
        homeGoals: Number.isFinite(v.homeGoals) ? v.homeGoals : undefined,
        awayGoals: Number.isFinite(v.awayGoals) ? v.awayGoals : undefined,
        ...extras,
      };
    } else if (Number.isFinite(v.homeGoals) && Number.isFinite(v.awayGoals)) {
      const h = v.homeGoals as number, a = v.awayGoals as number;
      out[id] = { pick: h > a ? "H" : h < a ? "A" : "D", homeGoals: h, awayGoals: a, ...extras };
    }
  }
  return out;
}

export function loadPredictions(playerId: string): PlayerPredictions {
  if (typeof window === "undefined") return blank(playerId);
  try {
    const raw = localStorage.getItem(KEY(playerId));
    if (raw) {
      const parsed = JSON.parse(raw) as Partial<PlayerPredictions> & { group?: Record<string, LegacyPrediction> };
      return {
        ...blank(playerId),
        ...parsed,
        group: migrateGroup(parsed.group),
      };
    }
  } catch {}
  return blank(playerId);
}

export function savePredictions(p: PlayerPredictions) {
  // Use max(now, prev+1) so the local timestamp is ALWAYS strictly greater than
  // any previous value — including server timestamps written by Cloud Run whose
  // clock can run ahead of the client. Without this, the SSE delivers a server
  // timestamp T_server > T_client and the merge in applyServerPicks runs,
  // overwriting the user's fresh pick with stale remote data.
  const prevTs = p.updatedAt ?? 0;
  p.updatedAt = Math.max(Date.now(), prevTs + 1);
  console.log(`[save] ${p.playerId} prevTs=${prevTs} newTs=${p.updatedAt} R16=${JSON.stringify(p.bracket?.R16)}`);
  localStorage.setItem(KEY(p.playerId), JSON.stringify(p));
  window.dispatchEvent(new CustomEvent("q26:predictions-updated", { detail: p.playerId }));
  scheduleRemoteSync(p.playerId);
}

// Mirror server data into localStorage without triggering an echo PUT back to
// the server. Used by hydration-from-server paths so we can treat the server
// as canonical without bouncing every read back as a write.
export function saveLocalMirror(p: PlayerPredictions) {
  if (typeof localStorage === "undefined") return;
  localStorage.setItem(KEY(p.playerId), JSON.stringify(p));
  window.dispatchEvent(new CustomEvent("q26:predictions-updated", { detail: p.playerId }));
}

// ---- Firestore mirror ----
// Short debounce + verified PUT + retry until success. Bug 2026-06-12: Charal
// llenó su quiniela y nada llegó a Firestore porque el fire-and-forget se
// comía 401/5xx. Ahora cada save reintenta hasta confirmar y dispara un
// evento que la UI puede mostrar.

const SYNC_DEBOUNCE_MS = 200;
const syncTimers: Record<string, ReturnType<typeof setTimeout>> = {};
const RETRY_DELAYS = [1500, 4000, 10000, 30000];
const lastSyncedTs: Record<string, number> = {};

// Persistent dirty flag — survives app close. Set on push failure, cleared on success.
// On next mount, hydratePredictionsFromServer will re-push if this flag is set.
function dirtyKey(playerId: string) { return `q26_sync_dirty:${playerId}`; }
function markDirty(playerId: string) {
  try { localStorage.setItem(dirtyKey(playerId), "1"); } catch {}
}
function clearDirty(playerId: string) {
  try { localStorage.removeItem(dirtyKey(playerId)); } catch {}
}
export function isDirty(playerId: string): boolean {
  try { return !!localStorage.getItem(dirtyKey(playerId)); } catch { return false; }
}

export type SyncStatus = "idle" | "pending" | "saving" | "ok" | "error" | "unauthorized";
export type SyncEvent = { playerId: string; status: SyncStatus; error?: string };

function emitSync(ev: SyncEvent) {
  if (typeof window === "undefined") return;
  window.dispatchEvent(new CustomEvent("q26:predictions-sync", { detail: ev }));
}

async function pushToServer(payload: PlayerPredictions, attempt = 0): Promise<void> {
  if (typeof window === "undefined") return;
  emitSync({ playerId: payload.playerId, status: "saving" });
  try {
    const r = await fetch("/api/predictions", {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ payload }),
      keepalive: true,
    });
    if (r.ok) {
      lastSyncedTs[payload.playerId] = payload.updatedAt;
      clearDirty(payload.playerId);
      emitSync({ playerId: payload.playerId, status: "ok" });
      try {
        const j = await r.clone().json() as { ok: boolean; picks?: Partial<PlayerPredictions> & { group?: Record<string, LegacyPrediction> } };
        if (j.ok && j.picks && typeof j.picks.updatedAt === "number" && j.picks.updatedAt >= payload.updatedAt) {
          applyServerPicks(payload.playerId, j.picks);
        }
      } catch { /* non-critical — SSE will eventually reconcile */ }
      return;
    }
    if (r.status === 401) {
      // Mark dirty so the next successful login triggers a re-push.
      markDirty(payload.playerId);
      emitSync({ playerId: payload.playerId, status: "unauthorized" });
      console.warn(`[predictions sync] 401 for ${payload.playerId} — marked dirty, will retry on re-login`);
      return;
    }
    throw new Error(`HTTP ${r.status}`);
  } catch (e) {
    markDirty(payload.playerId);
    console.warn(`[predictions sync] attempt ${attempt + 1} failed for ${payload.playerId}:`, e);
    if (attempt < RETRY_DELAYS.length) {
      emitSync({ playerId: payload.playerId, status: "pending", error: String(e) });
      setTimeout(() => {
        const fresh = loadPredictions(payload.playerId);
        if (fresh.updatedAt > (lastSyncedTs[payload.playerId] ?? 0)) {
          pushToServer(fresh, attempt + 1);
        }
      }, RETRY_DELAYS[attempt]);
    } else {
      emitSync({ playerId: payload.playerId, status: "error", error: String(e) });
    }
  }
}

function scheduleRemoteSync(playerId: string) {
  if (typeof window === "undefined") return;
  emitSync({ playerId, status: "pending" });
  if (syncTimers[playerId]) clearTimeout(syncTimers[playerId]);
  syncTimers[playerId] = setTimeout(() => {
    pushToServer(loadPredictions(playerId));
  }, SYNC_DEBOUNCE_MS);
}

// Immediately fire ONE pick to the server without debounce.
// This is the primary write path for group-stage picks. The legacy bulk PUT
// (scheduleRemoteSync) remains as a fallback for champion/bracket/network errors.
export async function firePickToServer(
  playerId: string,
  fixtureId: string,
  pick: Pick1X2,
): Promise<{ ok: boolean; error?: string }> {
  if (typeof window === "undefined") return { ok: false };
  emitSync({ playerId, status: "saving" });
  try {
    const r = await fetch("/api/picks", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ fixtureId, pick }),
      keepalive: true,
    });
    const j = (await r.json()) as { ok: boolean; error?: string };
    if (j.ok) {
      emitSync({ playerId, status: "ok" });
      // Confirmed by server — remove from offline queue if it was queued
      import("@/lib/bg-sync").then(m => m.removeFromBgSyncQueue(fixtureId)).catch(() => {});
      return { ok: true };
    }
    if (j.error === "unauthorized") {
      emitSync({ playerId, status: "unauthorized" });
      window.dispatchEvent(new CustomEvent("q26:needs-reauth"));
    } else if (j.error === "locked") {
      // Fixture already locked — caller should revert optimistic state
    } else {
      emitSync({ playerId, status: "error", error: j.error });
    }
    return { ok: false, error: j.error };
  } catch {
    // Network error: enqueue for Background Sync (Chrome/Android) so the pick
    // lands the moment connectivity returns, even if the app is closed.
    // Legacy debounce retry also runs as a fallback.
    emitSync({ playerId, status: "pending", error: "network" });
    import("@/lib/bg-sync").then(m => m.enqueuePickForBgSync(fixtureId, pick)).catch(() => {});
    return { ok: false, error: "network" };
  }
}

// Flush pending writes immediately — used on pagehide/visibilitychange so
// closing the tab on mobile doesn't leave changes stuck in the debounce.
export function flushPendingSync(playerId?: string) {
  if (typeof window === "undefined") return;
  const ids = playerId ? [playerId] : Object.keys(syncTimers);
  for (const id of ids) {
    if (syncTimers[id]) {
      clearTimeout(syncTimers[id]);
      delete syncTimers[id];
      const p = loadPredictions(id);
      if (p.updatedAt > 0) pushToServer(p);
    }
  }
}

// Bidirectional sync. Server's picks win when newer; otherwise local pushes
// up. Handles the cold-start case where one device has picks and the other
// is empty — first device to load post-deploy backfills Firestore.
export async function hydratePredictionsFromServer(playerId: string): Promise<void> {
  if (typeof window === "undefined") return;
  try {
    const r = await fetch(`/api/predictions?playerId=${encodeURIComponent(playerId)}`, { cache: "no-store" });
    const j = await r.json();
    const remote = (j.ok && j.picks) ? (j.picks as Partial<PlayerPredictions> & { group?: Record<string, LegacyPrediction> }) : null;
    const remoteTs = remote?.updatedAt ?? 0;
    // Re-read local AFTER the async fetch so any picks made during the network
    // round-trip (200-500ms) are included in the comparison and merge. Reading
    // before the await was the root cause of picks disappearing: user taps a
    // team, fetch completes with stale snapshot, merge uses empty local bracket
    // and overwrites the just-made pick with server data.
    const local = loadPredictions(playerId);
    const localTs = local.updatedAt ?? 0;
    console.log(`[hydrate] ${playerId} localTs=${localTs} remoteTs=${remoteTs} localR16=${JSON.stringify((local.bracket as BracketPick)?.R16)} remoteR16=${JSON.stringify((remote?.bracket as BracketPick)?.R16)}`);
    // Only skip the merge if local is MORE THAN 100ms newer than remote.
    // A smaller gap may be clock skew, not a genuine local-wins scenario.
    if (localTs >= remoteTs + 100) {
      console.log(`[hydrate] ${playerId} local wins → early return`);
      if (localTs > 0) pushToServer(local);
      return;
    }
    if (!remote || remoteTs === 0) return;
    // Merge per-fixture, do NOT replace. Server is canonical for keys it has,
    // but any key only the client has stays and gets re-pushed.
    const remoteGroup = migrateGroup(remote.group);
    const localGroup = local.group ?? {};
    const mergedGroup: typeof remoteGroup = { ...remoteGroup };
    const unsyncedKeys: string[] = [];
    for (const fxId of Object.keys(localGroup)) {
      if (!remoteGroup[fxId]) {
        mergedGroup[fxId] = localGroup[fxId];
        unsyncedKeys.push(fxId);
      }
    }
    // Bracket merge: local pick wins if non-empty, else use remote.
    // "remote wins" was the old behavior and caused picks to revert when the
    // server had an older selection for that slot.
    const localBracket = local.bracket ?? {};
    const remoteBracket = (remote.bracket ?? {}) as BracketPick;
    const mergedBracket: BracketPick = { ...remoteBracket };
    const ARRAY_ROUNDS: Array<keyof BracketPick> = ["R32", "R16", "QF", "SF"];
    const SIZES: Record<string, number> = { R32: 16, R16: 8, QF: 4, SF: 2 };
    for (const round of ARRAY_ROUNDS) {
      const localArr = localBracket[round] as string[] | undefined;
      const remoteArr = remoteBracket[round] as string[] | undefined;
      const size = SIZES[round as string] ?? 0;
      if (!size) continue;
      const base: string[] = (remoteArr && remoteArr.length > 0) ? [...remoteArr] : Array(size).fill("");
      const localFill: string[] = (localArr && localArr.length > 0) ? [...localArr] : Array(size).fill("");
      const roundMerged: string[] = Array(size).fill("");
      for (let i = 0; i < size; i++) {
        roundMerged[i] = localFill[i] || base[i] || "";
      }
      (mergedBracket as Record<string, unknown>)[round] = roundMerged;
    }
    if (!mergedBracket.THIRD && localBracket.THIRD) mergedBracket.THIRD = localBracket.THIRD;
    if (!mergedBracket.FINAL && localBracket.FINAL) mergedBracket.FINAL = localBracket.FINAL;

    const merged: PlayerPredictions = {
      ...blank(playerId),
      ...remote,
      group: mergedGroup,
      bracket: mergedBracket,
    };
    localStorage.setItem(KEY(playerId), JSON.stringify(merged));
    window.dispatchEvent(new CustomEvent("q26:predictions-updated", { detail: playerId }));

    // Detect unsynced bracket picks: if local has a non-empty slot that remote
    // doesn't, the previous push never reached the server — re-push now.
    const hasBracketDiff = ARRAY_ROUNDS.some(round => {
      const localArr = localBracket[round] as string[] | undefined;
      const remoteArr = remoteBracket[round] as string[] | undefined;
      if (!localArr || localArr.every(x => !x)) return false;
      if (!remoteArr || remoteArr.every(x => !x)) return true;
      return localArr.some((v, i) => v && v !== (remoteArr[i] ?? ""));
    });
    const hasSingleDiff = (
      (localBracket.THIRD && !remoteBracket.THIRD) ||
      (localBracket.FINAL && !remoteBracket.FINAL)
    );

    if (unsyncedKeys.length > 0 || hasBracketDiff || hasSingleDiff || isDirty(playerId)) {
      console.info(`[hydrate] unsynced/dirty picks detected (dirty=${isDirty(playerId)} group=${unsyncedKeys.length} bracketDiff=${hasBracketDiff}), re-pushing`);
      pushToServer({ ...merged, updatedAt: Date.now() });
    }
  } catch {}
}

export function blank(playerId: string): PlayerPredictions {
  return { playerId, group: {}, bracket: {}, updatedAt: 0 };
}

// Apply server-pushed picks (e.g. from SSE stream) into localStorage.
// Same merge logic as hydratePredictionsFromServer but without the fetch —
// the caller already has the data. Returns true if anything changed.
export function applyServerPicks(
  playerId: string,
  remote: Partial<PlayerPredictions> & { group?: Record<string, LegacyPrediction> },
): boolean {
  if (typeof window === "undefined") return false;
  const local = loadPredictions(playerId);
  const remoteTs = remote.updatedAt ?? 0;
  const localTs = local.updatedAt ?? 0;
  console.log(`[SSE-apply] ${playerId} localTs=${localTs} remoteTs=${remoteTs} localR16=${JSON.stringify((local.bracket as BracketPick)?.R16)} remoteR16=${JSON.stringify((remote.bracket as BracketPick)?.R16)}`);
  if (localTs >= remoteTs + 100) { console.log(`[SSE-apply] ${playerId} local wins → skip`); return false; }
  if (remoteTs === 0) return false;
  const remoteGroup = migrateGroup(remote.group);
  const localGroup = local.group ?? {};
  const mergedGroup: typeof remoteGroup = { ...remoteGroup };
  const unsyncedKeys: string[] = [];
  for (const fxId of Object.keys(localGroup)) {
    if (!remoteGroup[fxId]) {
      mergedGroup[fxId] = localGroup[fxId];
      unsyncedKeys.push(fxId);
    }
  }
  const localBracket2 = local.bracket ?? {};
  const remoteBracket2 = (remote.bracket ?? {}) as BracketPick;
  const mergedBracket2: BracketPick = { ...remoteBracket2 };
  const ARRAY_ROUNDS2: Array<keyof BracketPick> = ["R32", "R16", "QF", "SF"];
  const SIZES2: Record<string, number> = { R32: 16, R16: 8, QF: 4, SF: 2 };
  for (const round of ARRAY_ROUNDS2) {
    const localArr = localBracket2[round] as string[] | undefined;
    const remoteArr = remoteBracket2[round] as string[] | undefined;
    const size = SIZES2[round as string] ?? 0;
    if (!size) continue;
    // Use Array(size).fill("") as base when remote is absent OR an empty array —
    // an empty [] is truthy but [...[]] produces a 0-length array, so .map()
    // returns [] and all local picks are silently wiped.
    const base: string[] = (remoteArr && remoteArr.length > 0) ? [...remoteArr] : Array(size).fill("");
    const localFill: string[] = (localArr && localArr.length > 0) ? [...localArr] : Array(size).fill("");
    const merged: string[] = Array(size).fill("");
    for (let i = 0; i < size; i++) {
      // local pick wins — prevents server delivering stale data from reverting
      // a pick the user just made before the 200ms sync reached Firestore.
      merged[i] = localFill[i] || base[i] || "";
    }
    (mergedBracket2 as Record<string, unknown>)[round] = merged;
  }
  if (!mergedBracket2.THIRD && localBracket2.THIRD) mergedBracket2.THIRD = localBracket2.THIRD;
  if (!mergedBracket2.FINAL && localBracket2.FINAL) mergedBracket2.FINAL = localBracket2.FINAL;
  const merged: PlayerPredictions = { ...blank(playerId), ...remote, group: mergedGroup, bracket: mergedBracket2 };
  console.log(`[SSE-apply] ${playerId} writing mergedR16=${JSON.stringify(mergedBracket2.R16)} updatedAt=${merged.updatedAt}`);
  localStorage.setItem(KEY(playerId), JSON.stringify(merged));
  window.dispatchEvent(new CustomEvent("q26:predictions-updated", { detail: playerId }));
  if (unsyncedKeys.length > 0) pushToServer({ ...merged, updatedAt: Date.now() });
  return true;
}

export function loadAllPredictions(): PlayerPredictions[] {
  return PLAYERS.map(p => loadPredictions(p.id));
}

// Fetches one player's predictions from Firestore (no localStorage write).
// Used for the read-only view of another compa's quiniela.
export async function loadOnePredictionFromServer(playerId: string): Promise<PlayerPredictions> {
  try {
    const r = await fetch(`/api/predictions?playerId=${encodeURIComponent(playerId)}`, { cache: "no-store" });
    const j = await r.json();
    const remote = (j.ok && j.picks) ? (j.picks as Partial<PlayerPredictions> & { group?: Record<string, LegacyPrediction> }) : null;
    if (!remote) return blank(playerId);
    return { ...blank(playerId), ...remote, group: migrateGroup(remote.group) } as PlayerPredictions;
  } catch {
    return blank(playerId);
  }
}

// Fetches every compa's picks from Firestore so the home page / leaderboard
// can show fill% for OTHER players (localStorage only knows about the
// logged-in user on this device).
export async function loadAllPredictionsFromServer(): Promise<PlayerPredictions[]> {
  const results = await Promise.all(PLAYERS.map(async (p) => {
    try {
      const r = await fetch(`/api/predictions?playerId=${encodeURIComponent(p.id)}`, { cache: "no-store" });
      const j = await r.json();
      const remote = (j.ok && j.picks) ? (j.picks as Partial<PlayerPredictions> & { group?: Record<string, LegacyPrediction> }) : null;
      if (!remote) return blank(p.id);
      return {
        ...blank(p.id),
        ...remote,
        group: migrateGroup(remote.group),
      } as PlayerPredictions;
    } catch {
      return blank(p.id);
    }
  }));
  return results;
}

// ----------- Scoring -----------

export type MatchResult = { home: string; away: string; homeGoals: number; awayGoals: number };

export function actualPick(r: MatchResult): Pick1X2 {
  return r.homeGoals > r.awayGoals ? "H" : r.homeGoals < r.awayGoals ? "A" : "D";
}

export function scoreGroupPrediction(pred: GroupPrediction | undefined, actual: MatchResult | undefined): number {
  if (!pred || !actual) return 0;
  let pts = 0;
  if (pred.pick === actualPick(actual)) pts += SCORING.pickWinner;
  if (
    pts > 0 &&
    Number.isFinite(pred.homeGoals) && Number.isFinite(pred.awayGoals) &&
    pred.homeGoals === actual.homeGoals && pred.awayGoals === actual.awayGoals
  ) pts += SCORING.exactScoreBonus;
  return pts;
}

export function computePlayerScore(p: PlayerPredictions, actuals: Record<string, MatchResult>, koResults?: Record<string, string>): number {
  return computePlayerScoreDetail(p, actuals, koResults).score;
}

export type PlayerScoreDetail = {
  score: number;
  exactHits: number;   // 1X2 acertado + marcador exacto (grupo)
  signHits: number;    // 1X2 acertado sin exacto (grupo)
  bracketHits: number; // aciertos en rondas eliminatorias (R32+)
  streak: number;      // aciertos 1X2 consecutivos al hilo terminando en el partido jugado más reciente
};

// Como computePlayerScore pero desglosado para tiebreakers en el leaderboard.
export function computePlayerScoreDetail(
  p: PlayerPredictions,
  actuals: Record<string, MatchResult>,
  koResults?: Record<string, string>,  // slot ("R32-1", "R16-3", …) → winning team code
): PlayerScoreDetail {
  let score = 0;
  let exactHits = 0;
  let signHits = 0;
  let bracketHits = 0;
  for (const [fixtureId, pred] of Object.entries(p.group)) {
    const actual = actuals[fixtureId];
    if (!pred || !actual) continue;
    const matchedSign = pred.pick === actualPick(actual);
    if (!matchedSign) continue;
    score += SCORING.pickWinner;
    const matchedExact =
      Number.isFinite(pred.homeGoals) && Number.isFinite(pred.awayGoals) &&
      pred.homeGoals === actual.homeGoals && pred.awayGoals === actual.awayGoals;
    if (matchedExact) {
      score += SCORING.exactScoreBonus;
      exactHits += 1;
    } else {
      signHits += 1;
    }
  }

  // Bracket scoring: each correct KO pick earns points (all rounds equal)
  if (koResults && p.bracket) {
    const b = p.bracket;
    const checkRound = (picks: string[] | undefined, prefix: string, pts: number) => {
      if (!picks) return;
      for (let i = 0; i < picks.length; i++) {
        const pick = picks[i];
        const actual = koResults[`${prefix}-${i + 1}`];
        if (pick && actual && pick === actual) { score += pts; bracketHits += 1; }
      }
    };
    checkRound(b.R32,  "R32",  SCORING.knockoutWinner.R32);
    checkRound(b.R16,  "R16",  SCORING.knockoutWinner.R16);
    checkRound(b.QF,   "QF",   SCORING.knockoutWinner.QF);
    checkRound(b.SF,   "SF",   SCORING.knockoutWinner.SF);
    if (b.THIRD && koResults["THIRD"] && b.THIRD === koResults["THIRD"]) {
      score += SCORING.knockoutWinner.THIRD; bracketHits += 1;
    }
    if (b.FINAL && koResults["FINAL"] && b.FINAL === koResults["FINAL"]) {
      score += SCORING.knockoutWinner.FINAL; bracketHits += 1;
    }
  }

  // Streak: aciertos 1X2 consecutivos terminando en el partido jugado más
  // reciente (orden cronológico por kickoff). Rompe el primer fallo encontrado
  // contando hacia atrás. Solo cuenta partidos donde el jugador hizo pick.
  const fxByKickoff = allGroupFixtures()
    .filter(fx => actuals[fx.id]) // sólo jugados
    .map(fx => ({ id: fx.id, t: Date.parse(`${fx.date}T${fx.kickoffLocal}:00Z`) }))
    .sort((a, b) => b.t - a.t); // más reciente primero
  let streak = 0;
  for (const fx of fxByKickoff) {
    const pred = p.group[fx.id];
    if (!pred) break;
    const matched = pred.pick === actualPick(actuals[fx.id]);
    if (!matched) break;
    streak += 1;
  }

  return { score, exactHits, signHits, bracketHits, streak };
}

// How many predictions has the player filled?
export function fillStats(p: PlayerPredictions) {
  const totalGroupMatches = allGroupFixtures().length; // 72
  const filledGroup = Object.values(p.group).filter(g => g?.pick).length;
  const bracketFilled = !!p.champion;
  return {
    groupFilled: filledGroup,
    groupTotal: totalGroupMatches,
    bracketFilled,
    champion: p.champion,
    percent: Math.round((filledGroup / totalGroupMatches) * 100),
  };
}

// Re-export for downstream consumers
export { GROUPS };

const ROUND_SIZE: Record<keyof BracketPick, number> = {
  R32: 16, R16: 8, QF: 4, SF: 2, THIRD: 1, FINAL: 1,
};

export function bracketRoundComplete(b: BracketPick, round: "R32" | "R16" | "QF" | "SF"): boolean {
  const arr = b[round];
  if (!Array.isArray(arr)) return false;
  if (arr.length !== ROUND_SIZE[round]) return false;
  return arr.every(x => typeof x === "string" && x.length > 0);
}

