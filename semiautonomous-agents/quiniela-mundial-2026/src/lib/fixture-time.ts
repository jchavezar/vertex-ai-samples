// Utilities for kickoff time + per-match / per-round lock checks.
// FIFA 2026 fixtures store stadium-local time (YYYY-MM-DD + HH:MM). We convert
// to UTC using a fixed offset table per host city — DST is active in all
// hosting cities except Mexico (which doesn't observe DST).

import { CHAMPION_PHASE_STARTS, type ChampionLockRound } from "@/data/tournament";
import { KO_SCHEDULE } from "@/data/knockout-schedule";

// Signed UTC offset (hours) for each host city during June-July 2026.
// Mexico: UTC-6 year-round. US/Canada: summer DST.
const CITY_UTC_OFFSET_HOURS: Record<string, number> = {
  // Mexico (CST, no DST)
  "Ciudad de México": -6,
  "Zapopan": -6,
  "Guadalupe": -6,
  // US Eastern / Canada Eastern (EDT)
  "Atlanta": -4,
  "East Rutherford": -4,
  "Foxborough": -4,
  "Philadelphia": -4,
  "Miami Gardens": -4,
  "Toronto": -4,
  // US Central (CDT)
  "Houston": -5,
  "Kansas City": -5,
  "Arlington": -5,
  "Dallas": -5,
  // US Pacific / Canada Pacific (PDT)
  "Santa Clara": -7,
  "Inglewood": -7,
  "Seattle": -7,
  "Vancouver": -7,
  // NBA Finals 2026 venues
  "New York": -4,           // EDT
  "Oklahoma City": -5,      // CDT
  "San Antonio": -5,        // CDT
};

export type KickoffShape = { date: string; kickoffLocal: string; city: string };

export function fixtureKickoffMs(fx: KickoffShape): number {
  const offset = CITY_UTC_OFFSET_HOURS[fx.city] ?? -6;
  const [hh, mm] = fx.kickoffLocal.split(":").map(Number);
  const y = Number(fx.date.slice(0, 4));
  const mo = Number(fx.date.slice(5, 7)) - 1;
  const d = Number(fx.date.slice(8, 10));
  // local = UTC + offset  =>  UTC = local - offset
  return Date.UTC(y, mo, d, hh - offset, mm);
}

export function isFixtureLocked(fx: KickoffShape, now: number = Date.now()): boolean {
  return now >= fixtureKickoffMs(fx);
}

// Kickoff formatted in the viewer's browser timezone. Reads the runtime
// Intl default, so these are CLIENT-ONLY: on SSR they resolve to the server
// tz (UTC on Cloud Run) — wrap callers in a mount-gated component to avoid
// hydration mismatches.
export function formatKickoffTime(fx: KickoffShape): string {
  const ms = fixtureKickoffMs(fx);
  return new Intl.DateTimeFormat(undefined, {
    hour: "2-digit", minute: "2-digit", hour12: false,
  }).format(new Date(ms));
}

export function formatKickoffDate(fx: KickoffShape): string {
  const ms = fixtureKickoffMs(fx);
  const parts = new Intl.DateTimeFormat("en-CA", {
    month: "2-digit", day: "2-digit",
  }).formatToParts(new Date(ms));
  const mo = parts.find(p => p.type === "month")?.value ?? "";
  const d = parts.find(p => p.type === "day")?.value ?? "";
  return `${mo}/${d}`;
}

// Lock an individual knockout slot (e.g. "R32-5") at that match's kickoff time.
// R16+ slots don't have real kickoffs yet (teams TBD) so they fall back to round-level lock.
export function isKOSlotLocked(slot: string, now: number = Date.now()): boolean {
  const match = KO_SCHEDULE.find(m => m.slot === slot);
  if (!match) return true;
  return now >= new Date(match.dateISO).getTime();
}

// Lock an entire round once its phase window has begun.
// For R32 use isKOSlotLocked() per-match so only played games are locked.
export function isBracketRoundLocked(round: "R32" | "R16" | "QF" | "SF" | "THIRD" | "FINAL", now: number = Date.now()): boolean {
  const key: Exclude<ChampionLockRound, "PRE"> = round === "THIRD" ? "FINAL" : round;
  return now >= new Date(CHAMPION_PHASE_STARTS[key]).getTime();
}
