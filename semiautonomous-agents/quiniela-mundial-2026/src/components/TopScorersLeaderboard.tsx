"use client";

// Top scorers leaderboard — two tabs:
//   • Mundial 2026 (live) — pulled from /api/scorers, polled every 60s.
//   • Históricos        — static all-time WC top 5 from src/data/all-time-scorers.
//
// NBA-stat-leaders inspired layout: rank → photo → name + flag → goals count.
// Sits high on the home page; gets explicit pt/pb-6 breathing room because the
// home is already dense.

import Image from "next/image";
import { useEffect, useMemo, useRef, useState } from "react";
import { ChevronDown, ChevronUp, Trophy, History, Goal } from "lucide-react";
import { useLocale } from "@/lib/i18n";
import { flagUrl } from "@/data/teams";
import { ALL_TIME_TOP_SCORERS, type HistoricScorer } from "@/data/all-time-scorers";
import { useScoreboard } from "@/lib/scoreboard-cache";
import { useHomeSnapshot } from "@/lib/home-snapshot";
import type { ScorerEntry, ScorersResponse } from "@/app/api/scorers/route";

type Tab = "live" | "all-time";

// Polling cadence is computed dynamically inside the component:
//   • 15s when any World Cup match is live (state === "in"), so freshly
//     scored goals propagate within ~1 board tick.
//   • 60s otherwise (the dataset is "trickle of goals" — anything faster is
//     wasted ESPN round-trips).
const POLL_LIVE_MS = 15_000;
const POLL_IDLE_MS = 60_000;

function initialsOf(name: string): string {
  const parts = name.trim().split(/\s+/).filter(Boolean);
  if (parts.length === 0) return "?";
  if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase();
  return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
}

// Stable-ish accent for the initials avatar — derived from the name so the
// same player always gets the same chip color across renders.
function accentFor(name: string): string {
  const palette = ["#5E5BFF", "#14F195", "#FF3B82", "#F59E0B", "#06B6D4", "#A855F7", "#10B981", "#EF4444"];
  let h = 0;
  for (let i = 0; i < name.length; i++) h = (h * 31 + name.charCodeAt(i)) >>> 0;
  return palette[h % palette.length];
}

function ScorerAvatar({ name, photo, size = 44 }: { name: string; photo?: string; size?: number }) {
  if (photo) {
    return (
      <span
        className="relative rounded-full overflow-hidden ring-2 ring-white/10 shrink-0"
        style={{ width: size, height: size }}
      >
        <Image
          src={photo}
          alt={name}
          fill
          sizes={`${size}px`}
          className="object-cover"
          unoptimized
        />
      </span>
    );
  }
  const accent = accentFor(name);
  return (
    <span
      className="grid place-items-center rounded-full shrink-0 font-display font-bold ring-2 ring-white/10"
      style={{
        width: size,
        height: size,
        background: `linear-gradient(135deg, ${accent}22, ${accent}66)`,
        color: accent,
        fontSize: Math.max(11, Math.floor(size * 0.34)),
      }}
      aria-hidden
    >
      {initialsOf(name)}
    </span>
  );
}

function RankBadge({ rank }: { rank: number }) {
  const palette: Record<number, { bg: string; ink: string }> = {
    1: { bg: "linear-gradient(135deg, #FFD66E, #C7951B)", ink: "#3B2A00" },
    2: { bg: "linear-gradient(135deg, #E8ECF0, #9CA3AF)", ink: "#1F2937" },
    3: { bg: "linear-gradient(135deg, #E9A37A, #8B4A22)", ink: "#3B1A06" },
  };
  const style = palette[rank];
  if (style) {
    return (
      <span
        className="grid place-items-center w-6 h-6 rounded-full font-display text-[11px] font-extrabold tabular-nums shrink-0 shadow-sm"
        style={{ background: style.bg, color: style.ink }}
      >
        {rank}
      </span>
    );
  }
  return (
    <span className="grid place-items-center w-6 h-6 rounded-full font-display text-[11px] font-extrabold tabular-nums shrink-0 bg-[var(--bg-tint)] text-[var(--ink-soft)]">
      {rank}
    </span>
  );
}

function CountryChip({ iso2, code }: { iso2: string; code: string }) {
  return (
    <span className="inline-flex items-center gap-1.5 px-1.5 py-0.5 rounded-full bg-[var(--bg-tint)] ring-1 ring-[var(--line)]">
      <span className="relative w-3.5 h-3.5 rounded-sm overflow-hidden ring-1 ring-black/10 shrink-0">
        <Image src={flagUrl(iso2, 24)} alt={code} fill sizes="14px" className="object-cover" unoptimized />
      </span>
      <span className="font-display text-[10px] font-bold tracking-wider text-[var(--ink-soft)] tabular-nums">
        {code}
      </span>
    </span>
  );
}

// Primary flag+code badge — sits next to the player's name as the second-most
// prominent element in the row (after the name itself). Owner wants the
// country reading at first glance, not buried in a muted chip.
function TeamFlagCode({ iso2, code }: { iso2: string; code: string }) {
  return (
    <div className="flex items-center gap-2">
      <span className="relative w-5 h-3.5 rounded-sm overflow-hidden ring-1 ring-black/15 shrink-0">
        <Image
          src={flagUrl(iso2, 40)}
          alt={code}
          fill
          sizes="20px"
          className="object-cover"
          unoptimized
        />
      </span>
      <span className="text-[10px] uppercase tracking-wider font-bold tabular-nums text-[var(--ink)]">
        {code}
      </span>
    </div>
  );
}

function SkeletonRow() {
  return (
    <div className="flex items-center gap-3 py-3">
      <span className="w-6 h-6 rounded-full bg-[var(--bg-tint)] shimmer" />
      <span className="w-11 h-11 rounded-full bg-[var(--bg-tint)] shimmer" />
      <div className="flex-1 min-w-0 space-y-1.5">
        <span className="block w-32 h-3.5 rounded bg-[var(--bg-tint)] shimmer" />
        <span className="block w-16 h-2.5 rounded bg-[var(--bg-tint)] shimmer" />
      </div>
      <span className="w-8 h-6 rounded bg-[var(--bg-tint)] shimmer" />
    </div>
  );
}

function LiveRow({
  entry,
  rank,
  isLatestMatchScorer,
}: {
  entry: ScorerEntry;
  rank: number;
  isLatestMatchScorer: boolean;
}) {
  return (
    <div className="flex items-center gap-3 py-2.5">
      <RankBadge rank={rank} />
      <ScorerAvatar name={entry.shortName || entry.name} photo={entry.photo} size={44} />
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 min-w-0">
          <span className="font-semibold text-[14px] truncate text-[var(--ink)]">
            {entry.shortName || entry.name}
          </span>
          {isLatestMatchScorer && (
            <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded-full bg-[#FF3B82]/12 text-[#FF3B82] text-[9px] font-extrabold tracking-wider uppercase">
              <span className="w-1.5 h-1.5 rounded-full bg-[#FF3B82] animate-pulse" />
              EN VIVO
            </span>
          )}
        </div>
        <div className="mt-1 flex items-center gap-2">
          <TeamFlagCode iso2={entry.teamIso2} code={entry.teamCode} />
          <span className="text-[10px] text-[var(--ink-muted)] tabular-nums">
            · {entry.matchesPlayed} PJ
          </span>
        </div>
      </div>
      <div className="text-right shrink-0">
        <div className="font-display text-2xl font-bold tabular-nums leading-none">{entry.goals}</div>
        <div className="text-[9px] uppercase tracking-[0.15em] text-[var(--ink-muted)] mt-0.5">G</div>
      </div>
    </div>
  );
}

function HistoricRow({ entry }: { entry: HistoricScorer }) {
  return (
    <div className="flex items-center gap-3 py-2.5">
      <RankBadge rank={entry.rank} />
      <ScorerAvatar name={entry.name} photo={entry.photo} size={44} />
      <div className="flex-1 min-w-0">
        <div className="font-semibold text-[14px] truncate text-[var(--ink)]">{entry.name}</div>
        <div className="mt-1 flex items-center gap-2 flex-wrap">
          <TeamFlagCode
            iso2={entry.countryIso2}
            code={entry.country.slice(0, 3).toUpperCase()}
          />
          <span className="text-[10px] text-[var(--ink-muted)] truncate">· {entry.worldCups}</span>
        </div>
      </div>
      <div className="text-right shrink-0">
        <div className="font-display text-2xl font-bold tabular-nums leading-none">{entry.goals}</div>
        <div className="text-[9px] uppercase tracking-[0.15em] text-[var(--ink-muted)] mt-0.5">G</div>
      </div>
    </div>
  );
}

export function TopScorersLeaderboard() {
  const { t } = useLocale();
  const [open, setOpen] = useState(false);
  const [tab, setTab] = useState<Tab>("live");
  const [showAll, setShowAll] = useState(false);

  const snapshot = useHomeSnapshot();
  const snapshotTop5 = snapshot?.data?.scorers?.top5 ?? null;
  const [entries, setEntries] = useState<ScorerEntry[] | null>(snapshotTop5);
  const [loading, setLoading] = useState(snapshotTop5 === null);

  // Merge static pre-2026 data with live 2026 goals and re-rank dynamically
  const mergedHistoric = useMemo<HistoricScorer[]>(() => {
    const norm = (s: string) =>
      s.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase().trim();

    const map = new Map<string, HistoricScorer>();
    for (const h of ALL_TIME_TOP_SCORERS) {
      map.set(norm(h.name), { ...h });
    }

    for (const e of entries ?? []) {
      if (!e.goals) continue;
      const key = norm(e.name);
      const keyShort = norm(e.shortName || "");
      const hit = map.get(key) ?? map.get(keyShort);
      const hitKey = map.has(key) ? key : keyShort;
      if (hit) {
        map.set(hitKey, {
          ...hit,
          goals: hit.goals + e.goals,
          worldCups: hit.worldCups + " · 2026",
          photo: hit.photo ?? e.photo,
        });
      } else {
        map.set(key, {
          rank: 999,
          name: e.name,
          country: e.teamName,
          countryIso2: e.teamIso2,
          goals: e.goals,
          worldCups: "2026",
          photo: e.photo,
        });
      }
    }

    const sorted = Array.from(map.values()).sort(
      (a, b) => b.goals - a.goals || a.name.localeCompare(b.name),
    );
    for (let i = 0; i < sorted.length; i++) {
      sorted[i].rank =
        i > 0 && sorted[i].goals === sorted[i - 1].goals
          ? sorted[i - 1].rank
          : i + 1;
    }
    return sorted;
  }, [entries]);

  // Snapshot is the cheapest seed. Reflect updates whenever the home
  // provider pushes a newer payload.
  useEffect(() => {
    if (snapshotTop5) {
      setEntries(snapshotTop5);
      setLoading(false);
    }
  }, [snapshotTop5]);

  // Ref tracks whether we already have data (snapshot or prior fetch) — used
  // by the polling effect to skip the redundant initial /api/scorers fetch.
  const hasSeededRef = useRef<boolean>(entries !== null);
  useEffect(() => {
    if (entries !== null) hasSeededRef.current = true;
  }, [entries]);

  // Read live-state from the shared scoreboard cache. The cache is already
  // polling every 8s while any match is `state==="in"` (see scoreboard-cache),
  // so we (a) tighten our own scorers poll to 15s during live windows and
  // (b) piggy-back a refetch whenever the scoreboard payload itself ticks —
  // that way a fresh score will pull a fresh scorers list within ~8s instead
  // of waiting up to a full 15s.
  const { data: scoreboard, fetchedAt: scoreboardFetchedAt } = useScoreboard();
  const liveAny = (scoreboard?.events ?? []).some(
    e => e?.status?.type?.state === "in",
  );
  const POLL_MS = liveAny ? POLL_LIVE_MS : POLL_IDLE_MS;

  useEffect(() => {
    let cancelled = false;
    let timer: ReturnType<typeof setTimeout> | null = null;

    const load = async () => {
      try {
        const res = await fetch("/api/scorers", { cache: "no-store" });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const j = (await res.json()) as ScorersResponse;
        if (cancelled) return;
        if (j.ok) {
          setEntries(j.top5);
        } else {
          setEntries([]);
        }
      } catch {
        if (!cancelled) setEntries([]);
      } finally {
        if (!cancelled) setLoading(false);
      }
    };

    // Skip the initial network round-trip when the snapshot already seeded
    // entries — the snapshot endpoint just returned this same payload. Still
    // schedule the polling loop so live windows keep refreshing.
    if (!hasSeededRef.current) load();
    const tick = () => {
      timer = setTimeout(async () => {
        await load();
        if (!cancelled) tick();
      }, POLL_MS);
    };
    tick();

    return () => {
      cancelled = true;
      if (timer) clearTimeout(timer);
    };
  }, [POLL_MS]);

  // Piggy-back on the shared scoreboard cadence: every time the scoreboard
  // payload refreshes (8s live / 30s idle), trigger an out-of-band scorers
  // refetch so a newly scored goal doesn't have to wait for our own timer.
  useEffect(() => {
    if (!scoreboardFetchedAt) return;
    let cancelled = false;
    (async () => {
      try {
        const res = await fetch("/api/scorers", { cache: "no-store" });
        if (!res.ok) return;
        const j = (await res.json()) as ScorersResponse;
        if (!cancelled && j.ok) setEntries(j.top5);
      } catch { /* ignore — the timer will catch up */ }
    })();
    return () => { cancelled = true; };
  }, [scoreboardFetchedAt]);

  // "EN VIVO" chip: ESPN doesn't directly tell us which scorer is currently
  // active, so we approximate "scored most recently" by flagging anyone whose
  // count went UP since the last poll. We hold a ref-style snapshot via state.
  const [lastSnapshot, setLastSnapshot] = useState<Record<string, number>>({});
  const liveScorerIds = useMemo(() => {
    if (!entries) return new Set<string>();
    const ids = new Set<string>();
    for (const e of entries) {
      const prev = lastSnapshot[e.athleteId] ?? null;
      if (prev !== null && e.goals > prev) ids.add(e.athleteId);
    }
    return ids;
  }, [entries, lastSnapshot]);

  useEffect(() => {
    if (!entries) return;
    const next: Record<string, number> = {};
    for (const e of entries) next[e.athleteId] = e.goals;
    setLastSnapshot(prev => {
      // Avoid an infinite loop: only update when something actually changed.
      let changed = Object.keys(next).length !== Object.keys(prev).length;
      if (!changed) {
        for (const k of Object.keys(next)) {
          if (prev[k] !== next[k]) { changed = true; break; }
        }
      }
      return changed ? next : prev;
    });
    // We intentionally do not depend on lastSnapshot here.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [entries]);

  const leader = entries?.[0] ?? null;

  return (
    <section className="container-app pt-3 pb-1">
      <div className="glass rounded-3xl overflow-hidden">

        {/* ── ACCORDION TRIGGER ── */}
        <button
          type="button"
          onClick={() => setOpen(o => !o)}
          className="w-full flex items-center gap-3 px-5 py-3.5 text-left transition-colors hover:bg-[var(--bg-tint)]/50"
          aria-expanded={open}
        >
          <span className="flex items-center gap-1.5 text-[10px] font-display font-black uppercase tracking-[0.2em] text-[var(--ink-muted)]">
            <Goal size={11} />
            {t("scorers.title", "Goleadores")}
          </span>

          {/* live top scorer preview when collapsed */}
          {!open && leader && (
            <span className="flex items-center gap-1.5 min-w-0 flex-1">
              <ScorerAvatar name={leader.shortName || leader.name} photo={leader.photo} size={22} />
              <span className="text-[12px] font-semibold truncate text-[var(--ink)]">
                {leader.shortName || leader.name}
              </span>
              <span className="font-display font-black text-[13px] tabular-nums" style={{ color: "rgb(94,91,255)" }}>
                {leader.goals}G
              </span>
            </span>
          )}
          {!open && !leader && <span className="flex-1" />}

          <ChevronDown
            size={15}
            className="shrink-0 transition-transform duration-200 text-[var(--ink-muted)]"
            style={{ transform: open ? "rotate(180deg)" : "rotate(0deg)" }}
          />
        </button>

        {/* ── EXPANDED CONTENT ── */}
        {open && (
          <div className="px-5 pb-5">
            {/* tab selector */}
            <div className="flex items-center justify-between gap-3 mb-4 pt-1">
              <h2 className="font-display text-lg font-bold leading-tight">
                {tab === "live"
                  ? t("scorers.live", "Mundial 2026")
                  : t("scorers.allTime", "Históricos")}
              </h2>
              <div
                className="inline-flex items-center p-0.5 rounded-full bg-[var(--bg-tint)] ring-1 ring-[var(--line)] shrink-0"
                role="tablist"
                aria-label="Tabs"
              >
                <button
                  type="button"
                  role="tab"
                  aria-selected={tab === "live"}
                  onClick={() => { setTab("live"); setShowAll(false); }}
                  className={`px-3 py-1.5 rounded-full text-[11px] font-bold transition-colors ${
                    tab === "live"
                      ? "bg-[var(--ink)] text-white shadow"
                      : "text-[var(--ink-soft)] hover:text-[var(--ink)]"
                  }`}
                >
                  <span className="mr-1" aria-hidden>🥇</span>
                  {t("scorers.live", "Mundial 2026")}
                </button>
                <button
                  type="button"
                  role="tab"
                  aria-selected={tab === "all-time"}
                  onClick={() => { setTab("all-time"); setShowAll(false); }}
                  className={`px-3 py-1.5 rounded-full text-[11px] font-bold transition-colors ${
                    tab === "all-time"
                      ? "bg-[var(--ink)] text-white shadow"
                      : "text-[var(--ink-soft)] hover:text-[var(--ink)]"
                  }`}
                >
                  <span className="mr-1" aria-hidden>⭐</span>
                  {t("scorers.allTime", "Históricos")}
                </button>
              </div>
            </div>

            <div className="divide-y divide-[var(--line)]/60">
              {tab === "live" ? (
                loading && !entries ? (
                  <>
                    <SkeletonRow />
                    <SkeletonRow />
                    <SkeletonRow />
                    <SkeletonRow />
                    <SkeletonRow />
                  </>
                ) : !entries || entries.length === 0 ? (
                  <div className="py-8 text-center text-sm text-[var(--ink-muted)]">
                    {t("scorers.empty", "Aún sin goles registrados. Vuelve al primer pitazo.")}
                  </div>
                ) : (
                  (showAll ? entries : entries.slice(0, 5)).map((entry, i) => (
                    <LiveRow
                      key={entry.athleteId}
                      entry={entry}
                      rank={i + 1}
                      isLatestMatchScorer={liveScorerIds.has(entry.athleteId)}
                    />
                  ))
                )
              ) : (
                (showAll ? mergedHistoric : mergedHistoric.slice(0, 5)).map(entry => (
                  <HistoricRow key={`${entry.rank}-${entry.name}`} entry={entry} />
                ))
              )}
            </div>

            <div className="mt-4 flex items-center justify-between text-[10px] text-[var(--ink-muted)] uppercase tracking-[0.18em]">
              <div className="flex items-center gap-1.5">
                {tab === "live" ? <Trophy size={11} /> : <History size={11} />}
                <span>
                  {tab === "live"
                    ? `${t("scorers.goals", "Goles")} · TOP ${showAll ? (entries?.length ?? 5) : 5}`
                    : `FIFA · 1930 → 2026 · TOP ${showAll ? mergedHistoric.length : 5}`}
                </span>
              </div>
              <button
                type="button"
                onClick={() => setShowAll(v => !v)}
                className="inline-flex items-center gap-1 font-semibold text-[var(--ink-soft)] hover:text-[var(--ink)] normal-case tracking-normal"
              >
                {showAll ? "Ver menos" : "Ver más"}
                {showAll ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
              </button>
            </div>
          </div>
        )}
      </div>
    </section>
  );
}
