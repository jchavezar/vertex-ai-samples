// Personalized in-app alerts surfaced through the top banner.
//
// The owner can't reliably push to phones (web push too fragile, WhatsApp
// automation too risky for a personal account), so we deliver "you should
// open the app" hints via the banner real estate on every app open.
//
// computeAlerts() is a PURE function — it takes pre-loaded inputs and
// returns the alerts that should fire RIGHT NOW for the current player,
// sorted by priority. The component decides how to render them; this file
// owns the rules and the per-alert dismissal TTL.

import { allGroupFixtures, type GroupFixture } from "@/data/groups";
import { fixtureKickoffMs } from "@/lib/fixture-time";
import { actualPick, type PlayerPredictions, type MatchResult } from "@/lib/predictions";
import type { LiveFixture } from "@/lib/live-scoreboard";

export type Alert = {
  id: string;        // stable per-trigger key for dismiss tracking
  priority: number;  // lower = higher priority
  emoji: string;
  text: string;
  href: string;
  ttlSec?: number;   // dismissal TTL override (default 6h)
};

export type MvpEntry = {
  date: string;
  playerId: string;
  name: string;
  points: number;
};

export type RankSnapshot = { playerId: string; rank: number; takenAt: number };

export type ComputeAlertsOpts = {
  playerId: string;
  playerName: string;
  predictions: PlayerPredictions;
  liveByFixture: Record<string, LiveFixture>;
  finals: Record<string, MatchResult>;
  mvpToday?: MvpEntry | null;
  myCurrentRank?: number | null;       // 1-based
  lastSeenRank?: RankSnapshot | null;
  overtakerName?: string | null;       // closest compa who passed me
  now?: number;
  // i18n hook. Caller passes useLocale().t — keeps this file SSR-safe and
  // means the dictionary stays grep-able in i18n.tsx.
  t: (key: string, fallback?: string) => string;
};

const DEFAULT_TTL_SEC = 6 * 60 * 60; // 6 hours
const PICK_CLOSING_WINDOW_MS = 3 * 60 * 60 * 1000;
const SILENT_PICK_DAYS = 1;

const DISMISS_PREFIX = "q26:alert-dismissed:";
const GOAL_SIG_KEY = (pid: string) => `q26:alert-goalSig:${pid}`;
const RANK_SNAPSHOT_KEY = (pid: string) => `q26:alert-rank:${pid}`;

// -----------------------------------------------------------------------------
// localStorage helpers
// -----------------------------------------------------------------------------

function ls(): Storage | null {
  if (typeof window === "undefined") return null;
  try { return window.localStorage; } catch { return null; }
}

export function dismissAlert(id: string, ttlSec: number = DEFAULT_TTL_SEC): void {
  const s = ls();
  if (!s) return;
  try { s.setItem(`${DISMISS_PREFIX}${id}`, String(Date.now() + ttlSec * 1000)); } catch {}
}

export function isDismissed(id: string, ttlSec: number = DEFAULT_TTL_SEC): boolean {
  const s = ls();
  if (!s) return false;
  try {
    const raw = s.getItem(`${DISMISS_PREFIX}${id}`);
    if (!raw) return false;
    const exp = Number(raw);
    if (!Number.isFinite(exp)) return false;
    if (Date.now() < exp) return true;
    // Lazy cleanup — also re-honor explicit TTL override from caller.
    s.removeItem(`${DISMISS_PREFIX}${id}`);
    // Belt-and-suspenders: if exp was minted with a longer TTL than the
    // caller passes now, the timestamp check above is the source of truth.
    void ttlSec;
    return false;
  } catch {
    return false;
  }
}

// -----------------------------------------------------------------------------
// Goal signature tracking (alert P2)
// -----------------------------------------------------------------------------

// Returns the list of "newly leading goal" alerts to fire. Marks them seen
// in the same call so we don't double-fire on the next render tick.
type GoalSig = Record<string, string>; // fixtureId -> "homeGoals-awayGoals"

function readGoalSig(playerId: string): GoalSig {
  const s = ls();
  if (!s) return {};
  try {
    const raw = s.getItem(GOAL_SIG_KEY(playerId));
    if (!raw) return {};
    const parsed = JSON.parse(raw);
    return (parsed && typeof parsed === "object") ? parsed as GoalSig : {};
  } catch { return {}; }
}

function writeGoalSig(playerId: string, sig: GoalSig): void {
  const s = ls();
  if (!s) return;
  try { s.setItem(GOAL_SIG_KEY(playerId), JSON.stringify(sig)); } catch {}
}

// -----------------------------------------------------------------------------
// Rank-history tracking (alert P5)
// -----------------------------------------------------------------------------

export function readRankSnapshot(playerId: string): RankSnapshot | null {
  const s = ls();
  if (!s) return null;
  try {
    const raw = s.getItem(RANK_SNAPSHOT_KEY(playerId));
    if (!raw) return null;
    const parsed = JSON.parse(raw);
    if (!parsed || typeof parsed !== "object") return null;
    const rank = Number(parsed.rank);
    const takenAt = Number(parsed.takenAt);
    if (!Number.isFinite(rank) || !Number.isFinite(takenAt)) return null;
    return { playerId, rank, takenAt };
  } catch { return null; }
}

export function writeRankSnapshot(playerId: string, rank: number): void {
  const s = ls();
  if (!s) return;
  try { s.setItem(RANK_SNAPSHOT_KEY(playerId), JSON.stringify({ rank, takenAt: Date.now() })); } catch {}
}

// -----------------------------------------------------------------------------
// computeAlerts
// -----------------------------------------------------------------------------

function fixtureById(): Map<string, GroupFixture> {
  return new Map(allGroupFixtures().map(fx => [fx.id, fx]));
}

// Picks the team code that's leading the live fixture, or null on draw.
function leadingTeam(fx: GroupFixture, live: LiveFixture): string | null {
  const h = live.homeGoals, a = live.awayGoals;
  if (h === undefined || a === undefined) return null;
  if (h > a) return fx.home;
  if (a > h) return fx.away;
  return null;
}

// Picks 1X2 the player chose, mapped to the actual leading team code.
function playerLeansToward(fx: GroupFixture, pick: "H" | "D" | "A"): string | null {
  if (pick === "H") return fx.home;
  if (pick === "A") return fx.away;
  return null; // draw — handled separately
}

export function computeAlerts(opts: ComputeAlertsOpts): Alert[] {
  const {
    playerId, playerName, predictions, liveByFixture, finals,
    mvpToday, myCurrentRank, lastSeenRank, overtakerName,
    t, now = Date.now(),
  } = opts;

  const out: Alert[] = [];
  if (!playerId) return out;

  const fxMap = fixtureById();
  const allFx = allGroupFixtures();

  // ----- P1: pick por cerrar -----
  // Any unfilled pick where kickoff is in the next 3h. Coalesce to the
  // single earliest one — banner is a 1-liner and showing "next 4 picks
  // closing" gets noisy. Dismiss key uses fixtureId so it auto-rotates.
  const upcomingUnfilled = allFx
    .filter(fx => {
      const ms = fixtureKickoffMs(fx);
      return ms > now && ms - now <= PICK_CLOSING_WINDOW_MS && !predictions.group[fx.id]?.pick;
    })
    .sort((a, b) => fixtureKickoffMs(a) - fixtureKickoffMs(b));
  if (upcomingUnfilled.length > 0) {
    const fx = upcomingUnfilled[0];
    const mins = Math.max(1, Math.round((fixtureKickoffMs(fx) - now) / 60_000));
    const matchLabel = `${fx.home} vs ${fx.away}`;
    out.push({
      id: `fillPick:${fx.id}`,
      priority: 1,
      emoji: "⏰",
      text: t("alert.fillPick", "Pick por cerrar")
        .replace("{match}", matchLabel)
        .replace("{mins}", String(mins)),
      href: `/quiniela#${fx.id}`,
      ttlSec: Math.max(60, Math.floor((fixtureKickoffMs(fx) - now) / 1000)),
    });
  }

  // ----- P2: gol en tu pick -----
  // For each LIVE fixture: if the player's 1X2 matches the leading team
  // AND the (homeGoals-awayGoals) signature is new since last seen, fire.
  const currentSig: GoalSig = {};
  const newGoalAlerts: Alert[] = [];
  const prevSig = readGoalSig(playerId);
  for (const [fxId, live] of Object.entries(liveByFixture)) {
    if (live.phase !== "live") continue;
    const fx = fxMap.get(fxId);
    if (!fx) continue;
    if (live.homeGoals === undefined || live.awayGoals === undefined) continue;
    const sig = `${live.homeGoals}-${live.awayGoals}`;
    currentSig[fxId] = sig;
    if (prevSig[fxId] === sig) continue; // already shown this scoreline
    if (live.homeGoals + live.awayGoals === 0) continue; // 0-0 is not a goal
    const pred = predictions.group[fxId];
    if (!pred) continue;
    const leader = leadingTeam(fx, live);
    const myTeam = playerLeansToward(fx, pred.pick);
    const matched = (pred.pick === "D" && leader === null) ||
                    (myTeam !== null && myTeam === leader);
    if (!matched) continue;
    const matchLabel = `${fx.home} ${live.homeGoals}-${live.awayGoals} ${fx.away}`;
    newGoalAlerts.push({
      id: `goalOnPick:${fxId}:${sig}`,
      priority: 2,
      emoji: "⚽",
      text: t("alert.goalOnPick", "Gol en tu pick · {match}").replace("{match}", matchLabel),
      href: `/partido/${fxId}/live`,
      ttlSec: 60 * 60, // 1h — scorelines move fast, no point dismissing for 6h
    });
  }
  // Always write back current sigs — even fixtures we filtered out for
  // "already seen" so we keep the cache consistent. Drop stale ones not in
  // currentSig so the localStorage entry doesn't grow forever.
  if (Object.keys(currentSig).length > 0 || Object.keys(prevSig).length > 0) {
    writeGoalSig(playerId, currentSig);
  }
  out.push(...newGoalAlerts);

  // ----- P3: charal del día -----
  if (mvpToday && mvpToday.points > 0) {
    if (mvpToday.playerId === playerId) {
      out.push({
        id: `mvpYou:${mvpToday.date}`,
        priority: 3,
        emoji: "👑",
        text: t("alert.mvpYou", "Eres caliente del día, +{pts} pts").replace("{pts}", String(mvpToday.points)),
        href: "/leaderboard",
      });
    } else if (mvpToday.name) {
      out.push({
        id: `mvpOther:${mvpToday.date}:${mvpToday.playerId}`,
        priority: 3,
        emoji: "👑",
        text: t("alert.mvpOther", "Caliente hoy: {name} +{pts} — checa la tabla")
          .replace("{name}", mvpToday.name)
          .replace("{pts}", String(mvpToday.points)),
        href: "/leaderboard",
      });
    }
  }

  // ----- P4: racha en juego -----
  // Hot streak (>=3) on TODAY's finalized fixtures, with another decided
  // or live fixture today they could extend on.
  const todayET = etDate(new Date(now));
  const todaysFx = allFx.filter(fx => fx.date === todayET);
  const todaysFinals = todaysFx.filter(fx => finals[fx.id]).sort((a, b) => fixtureKickoffMs(b) - fixtureKickoffMs(a));
  let hotStreak = 0;
  for (const fx of todaysFinals) {
    const pred = predictions.group[fx.id];
    const fin = finals[fx.id];
    if (!pred || !fin) break;
    if (pred.pick !== actualPick(fin)) break;
    hotStreak += 1;
  }
  if (hotStreak >= 3) {
    const hasExtension = todaysFx.some(fx => {
      if (finals[fx.id]) return false;
      const live = liveByFixture[fx.id];
      if (live && (live.phase === "live" || live.phase === "pre")) return true;
      return fixtureKickoffMs(fx) > now;
    });
    if (hasExtension) {
      out.push({
        id: `hotStreak:${todayET}:${hotStreak}`,
        priority: 4,
        emoji: "🔥",
        text: t("alert.hotStreak", "Llevas {n} al hilo hoy — no la cagues")
          .replace("{n}", String(hotStreak)),
        href: "/leaderboard",
        ttlSec: 2 * 60 * 60,
      });
    }
  }

  // ----- P5: te rebasaron -----
  if (typeof myCurrentRank === "number" && lastSeenRank && lastSeenRank.takenAt > 0) {
    const drop = myCurrentRank - lastSeenRank.rank;
    if (drop >= 2 && overtakerName) {
      out.push({
        id: `overtaken:${myCurrentRank}:${lastSeenRank.rank}`,
        priority: 5,
        emoji: "📉",
        text: t("alert.overtaken", "{name} te rebasó · vas {pos}°")
          .replace("{name}", overtakerName)
          .replace("{pos}", String(myCurrentRank)),
        href: "/leaderboard",
      });
    }
  }

  // ----- P6: bracket pelón -----
  // Knockouts haven't been wired with explicit kickoff dates yet, but the
  // first knockout fixture starts the day after the last group fixture.
  // If there are <5 days left and the player hasn't set ANY bracket picks,
  // nudge.
  const hasBracket = !!(predictions.bracket?.R32?.length ||
                        predictions.bracket?.R16?.length ||
                        predictions.champion);
  if (!hasBracket) {
    const lastGroupMs = allFx
      .map(fx => fixtureKickoffMs(fx))
      .sort((a, b) => b - a)[0];
    if (lastGroupMs) {
      const firstKoApproxMs = lastGroupMs + 24 * 60 * 60 * 1000;
      const daysLeft = (firstKoApproxMs - now) / (24 * 60 * 60 * 1000);
      if (daysLeft <= 5 && daysLeft > -1) {
        out.push({
          id: `emptyBracket:${Math.floor(daysLeft)}`,
          priority: 6,
          emoji: "🆕",
          text: t("alert.emptyBracket", "Bracket pelón — quedan {n} días")
            .replace("{n}", String(Math.max(0, Math.ceil(daysLeft)))),
          href: "/bracket",
        });
      }
    }
  }

  // ----- P7: llevas N días sin picar -----
  // Player has unfilled picks AND their predictions.updatedAt is >=1 day old.
  const totalGroupFx = allFx.length;
  const filledCount = Object.values(predictions.group).filter(g => g?.pick).length;
  const anyOpenPick = filledCount < totalGroupFx;
  if (anyOpenPick && predictions.updatedAt > 0) {
    const daysSilent = Math.floor((now - predictions.updatedAt) / (24 * 60 * 60 * 1000));
    if (daysSilent >= SILENT_PICK_DAYS) {
      out.push({
        id: `daysSilent:${daysSilent}`,
        priority: 7,
        emoji: "💀",
        text: t("alert.daysSilent", "Llevas {n} día(s) sin picar · {name}")
          .replace("{n}", String(daysSilent))
          .replace("{name}", playerName || ""),
        href: "/quiniela",
      });
    }
  }

  // Drop dismissed, then sort by priority. Goal alerts use a TTL of 1h so
  // each new scoreline still fires; everything else honors 6h default.
  const active = out.filter(a => !isDismissed(a.id, a.ttlSec ?? DEFAULT_TTL_SEC));
  active.sort((a, b) => a.priority - b.priority);
  return active;
}

// Mirror of the ET date helper from daily-streak. Keep a local copy so this
// file doesn't pull a separate dep just for one Intl call.
function etDate(d: Date): string {
  return new Intl.DateTimeFormat("en-CA", {
    timeZone: "America/New_York",
    year: "numeric", month: "2-digit", day: "2-digit",
  }).format(d);
}
