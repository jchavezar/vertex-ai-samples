// Daily-open streak tracker (Duolingo-style). Pure localStorage, ET-zoned so
// it lines up with the rest of the app's date math (America/New_York).
//
// What counts as "today" is the calendar day in America/New_York at the
// moment of the call. The store keeps a sorted array of ISO dates (YYYY-MM-DD)
// trimmed to the last 60 entries so it doesn't bloat localStorage.

const STORAGE_PREFIX = "q26:daily-streak:";
const MAX_DAYS = 60;
// Grace: if the user opens after midnight but the prior "today" is still
// adjacent (yesterday), the streak is preserved — they haven't missed a day.
const BROKEN_STREAK_MIN = 3;

export type DailyStreakStore = {
  days: string[];      // sorted asc, ISO YYYY-MM-DD in ET
  lastOpen: string;    // ISO YYYY-MM-DD in ET
};

function isBrowser(): boolean {
  return typeof window !== "undefined" && typeof window.localStorage !== "undefined";
}

function key(playerId: string): string {
  return `${STORAGE_PREFIX}${playerId}`;
}

// Returns YYYY-MM-DD for the given Date in America/New_York.
export function etDate(d: Date = new Date()): string {
  return new Intl.DateTimeFormat("en-CA", {
    timeZone: "America/New_York",
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  }).format(d);
}

// Shift an ET ISO date by `delta` days, returning a new ET ISO date.
export function shiftEtDate(isoDate: string, delta: number): string {
  // Use noon UTC anchor so DST shifts in the local zone don't roll the day.
  const anchor = new Date(`${isoDate}T12:00:00Z`).getTime();
  return etDate(new Date(anchor + delta * 86_400_000));
}

function read(playerId: string): DailyStreakStore {
  if (!isBrowser()) return { days: [], lastOpen: "" };
  try {
    const raw = window.localStorage.getItem(key(playerId));
    if (!raw) return { days: [], lastOpen: "" };
    const parsed = JSON.parse(raw) as Partial<DailyStreakStore>;
    const days = Array.isArray(parsed.days)
      ? parsed.days.filter((d): d is string => typeof d === "string" && /^\d{4}-\d{2}-\d{2}$/.test(d))
      : [];
    return {
      days: Array.from(new Set(days)).sort(),
      lastOpen: typeof parsed.lastOpen === "string" ? parsed.lastOpen : (days[days.length - 1] ?? ""),
    };
  } catch {
    return { days: [], lastOpen: "" };
  }
}

function write(playerId: string, store: DailyStreakStore): void {
  if (!isBrowser()) return;
  try {
    window.localStorage.setItem(key(playerId), JSON.stringify(store));
  } catch {
    /* quota — ignore */
  }
}

// Records today's open. Idempotent for the same day. Trims to MAX_DAYS.
// Returns the updated store so callers can read currentStreak without a
// second localStorage hit.
export function recordOpen(playerId: string, now: Date = new Date()): DailyStreakStore {
  if (!playerId) return { days: [], lastOpen: "" };
  const today = etDate(now);
  const store = read(playerId);
  if (store.lastOpen === today && store.days[store.days.length - 1] === today) {
    return store;
  }
  const next: DailyStreakStore = {
    days: Array.from(new Set([...store.days, today])).sort(),
    lastOpen: today,
  };
  if (next.days.length > MAX_DAYS) {
    next.days = next.days.slice(next.days.length - MAX_DAYS);
  }
  write(playerId, next);
  return next;
}

// Counts the streak ending at today (preferred) or yesterday (grace window).
// Returns 0 if neither today nor yesterday is in the store.
export function currentStreak(playerId: string, now: Date = new Date()): number {
  if (!playerId) return 0;
  const store = read(playerId);
  if (store.days.length === 0) return 0;
  const today = etDate(now);
  const yesterday = shiftEtDate(today, -1);
  const set = new Set(store.days);
  let anchor: string;
  if (set.has(today)) anchor = today;
  else if (set.has(yesterday)) anchor = yesterday;
  else return 0;
  let count = 0;
  let cursor = anchor;
  while (set.has(cursor)) {
    count += 1;
    cursor = shiftEtDate(cursor, -1);
  }
  return count;
}

// True iff (a) the user used to have a non-trivial streak (>= BROKEN_STREAK_MIN)
// and (b) more than one day has elapsed since their last open. We require a
// non-trivial prior streak so single-day "openers" don't see a "racha rota"
// banner the day after they first try the app.
export function wasBroken(playerId: string, now: Date = new Date()): boolean {
  if (!playerId) return false;
  const store = read(playerId);
  if (!store.lastOpen) return false;
  const today = etDate(now);
  if (store.lastOpen === today) return false;
  const yesterday = shiftEtDate(today, -1);
  if (store.lastOpen === yesterday) return false;
  // Count the consecutive run ending at lastOpen — needs to be >= threshold
  // for the broken-streak callout to feel earned.
  const set = new Set(store.days);
  let count = 0;
  let cursor = store.lastOpen;
  while (set.has(cursor)) {
    count += 1;
    cursor = shiftEtDate(cursor, -1);
  }
  return count >= BROKEN_STREAK_MIN;
}

// Test/debug helper — not exported for UI.
export function _peek(playerId: string): DailyStreakStore {
  return read(playerId);
}
