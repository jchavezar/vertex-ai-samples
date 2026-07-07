// Shared cache for /api/players/[id]/roast responses. Leaderboard prefetches
// all charales in parallel as soon as finals + picks are ready; the per-player
// profile page reads from cache for instant render and refreshes in background.
//
// Cache key includes a hash of the finals payload so a fresh marker arrival
// invalidates stale roasts automatically.

export type Verdict = "exact" | "hit" | "miss" | "skipped";
export type RoastRow = {
  fixtureId: string;
  date: string;
  home: string;
  away: string;
  group?: string;         // group stage group letter — optional now
  round?: string;         // "R32" | "R16" | "QF" | "SF" | "FINAL" for KO rows
  slot?: string;          // "R32-1", "R16-3" etc. for KO rows
  actualScore: string;
  truth: string;          // "H"|"D"|"A" for group, team code for KO
  myPick: string | null;  // H/D/A for group, team code for KO
  myScore: string | null;
  pts: number;
  runningTotal?: number;  // cumulative score up to and including this row
  verdict: Verdict;
};
export type RoastPayload = {
  ok: boolean;
  playerId: string;
  name: string;
  score: number;
  signHits: number;
  exactHits: number;
  streak: number;
  decided: number;
  roast: string;
  verdicts: RoastRow[];
  bracketHits: number;
};

export type FinalsMap = Record<string, { homeGoals: number; awayGoals: number }>;
export type KoResultsMap = Record<string, string>; // slot → winning team code

// Long TTL — the cache key already invalidates whenever the finals payload
// changes, so within a single "no new markers" window the roast must stay
// stable. Refetching every few minutes only generates a fresh variant that
// flickers when the user comes back to the page.
const TTL_MS = 60 * 60 * 1000;
// v3 = persisted in localStorage so the roast survives tab close + cold app
// open. Bumping orphans any leftover entries in both localStorage AND
// sessionStorage (where v1/v2 used to live).
const KEY_PREFIX = "q26.roast.v4.";
const OLD_KEY_PREFIXES = ["q26.roast.v1.", "q26.roast.v2.", "q26.roast.v3."];

function sweepStaleKeys() {
  if (typeof window === "undefined") return;
  for (const store of [sessionStorage, localStorage] as Storage[]) {
    try {
      const toDelete: string[] = [];
      for (let i = 0; i < store.length; i++) {
        const k = store.key(i);
        if (!k) continue;
        if (OLD_KEY_PREFIXES.some(p => k.startsWith(p))) toDelete.push(k);
      }
      for (const k of toDelete) store.removeItem(k);
    } catch { /* private mode / quota — best effort */ }
  }
}
sweepStaleKeys();
const MAX_CONCURRENT_PREFETCH = 3;

// In-flight requests so concurrent prefetch + click don't double-fire.
const inflight = new Map<string, Promise<RoastPayload | null>>();
// Queue of pending prefetches when we're at the concurrency cap. Vertex AI
// rate-limits aggressively (429 RESOURCE_EXHAUSTED on bursts of 11 parallel
// calls), so prefetch obeys a 3-wide semaphore. User-initiated loadRoast()
// always bypasses the queue — clicking should never be throttled.
type QueuedPrefetch = () => void;
const prefetchQueue: QueuedPrefetch[] = [];
let prefetchActive = 0;
function drainPrefetchQueue() {
  while (prefetchActive < MAX_CONCURRENT_PREFETCH && prefetchQueue.length > 0) {
    const next = prefetchQueue.shift();
    if (next) next();
  }
}

function hashFinals(finals: FinalsMap): string {
  const keys = Object.keys(finals).sort();
  let h = 0;
  for (const k of keys) {
    const v = finals[k];
    const chunk = `${k}:${v.homeGoals}-${v.awayGoals};`;
    for (let i = 0; i < chunk.length; i++) {
      h = (h * 31 + chunk.charCodeAt(i)) | 0;
    }
  }
  return `${keys.length}@${(h >>> 0).toString(36)}`;
}

function hashKo(ko: KoResultsMap): string {
  const keys = Object.keys(ko).sort();
  let h = 0;
  for (const k of keys) {
    const chunk = `${k}:${ko[k]};`;
    for (let i = 0; i < chunk.length; i++) h = (h * 31 + chunk.charCodeAt(i)) | 0;
  }
  return `${keys.length}@${(h >>> 0).toString(36)}`;
}

function cacheKey(playerId: string, finals: FinalsMap, ko?: KoResultsMap): string {
  return `${KEY_PREFIX}${playerId}.${hashFinals(finals)}.${ko ? hashKo(ko) : "0"}`;
}

// Read from localStorage so the roast survives page reloads, tab closes, AND
// the next time the user opens the app — the only thing that should invalidate
// is a marker change (handled by the finals hash in the key) or TTL expiry.
function readStored(key: string): RoastPayload | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = localStorage.getItem(key);
    if (!raw) return null;
    const parsed = JSON.parse(raw) as { at: number; payload: RoastPayload };
    if (Date.now() - parsed.at > TTL_MS) {
      localStorage.removeItem(key);
      return null;
    }
    return parsed.payload;
  } catch {
    return null;
  }
}

function writeStored(key: string, payload: RoastPayload) {
  if (typeof window === "undefined") return;
  try {
    localStorage.setItem(key, JSON.stringify({ at: Date.now(), payload }));
  } catch {
    // Quota exceeded — try to make room by deleting old roast entries before
    // giving up. A single roast is ~2KB so this should always succeed unless
    // the user has thousands of bookmarked tabs (impossible).
    try {
      const toDelete: string[] = [];
      for (let i = 0; i < localStorage.length; i++) {
        const k = localStorage.key(i);
        if (k && k.startsWith(KEY_PREFIX)) toDelete.push(k);
      }
      for (const k of toDelete) localStorage.removeItem(k);
      localStorage.setItem(key, JSON.stringify({ at: Date.now(), payload }));
    } catch { /* private mode / disabled — best effort */ }
  }
}

export function getCachedRoast(playerId: string, finals: FinalsMap, ko?: KoResultsMap): RoastPayload | null {
  return readStored(cacheKey(playerId, finals, ko));
}

async function fetchRoast(playerId: string, finals: FinalsMap, ko?: KoResultsMap, signal?: AbortSignal): Promise<RoastPayload | null> {
  try {
    const r = await fetch(`/api/players/${playerId}/roast`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ finals }),
      cache: "no-store",
      signal,
    });
    if (!r.ok) return null;
    const j = (await r.json()) as RoastPayload;
    if (!j?.ok) return null;
    writeStored(cacheKey(playerId, finals, ko), j);
    return j;
  } catch {
    return null;
  }
}

export function prefetchRoast(playerId: string, finals: FinalsMap, ko?: KoResultsMap): void {
  const key = cacheKey(playerId, finals, ko);
  if (readStored(key)) return;
  if (inflight.has(key)) return;
  const run = () => {
    prefetchActive++;
    const p = fetchRoast(playerId, finals, ko).finally(() => {
      inflight.delete(key);
      prefetchActive--;
      drainPrefetchQueue();
    });
    inflight.set(key, p);
  };
  if (prefetchActive < MAX_CONCURRENT_PREFETCH) run();
  else prefetchQueue.push(run);
}

export async function loadRoast(playerId: string, finals: FinalsMap, ko?: KoResultsMap, signal?: AbortSignal): Promise<RoastPayload | null> {
  const key = cacheKey(playerId, finals, ko);
  const cached = readStored(key);
  if (cached) return cached;
  const existing = inflight.get(key);
  if (existing) return existing;
  const p = fetchRoast(playerId, finals, ko, signal).finally(() => inflight.delete(key));
  inflight.set(key, p);
  return p;
}
