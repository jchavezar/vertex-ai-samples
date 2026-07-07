"use client";

// /standings — Live Mundial 2026 group standings + 7 creative per-group widgets.
//
// Separate from /grupos (which stays the roster directory) and from /leaderboard
// (which is the POOL table). This page is purely the TOURNAMENT table:
// real finals → Pts/PJ/W/D/L/GF/GA/GD per group + Drama meter, AI bot vs reality
// scoreboard, surprise/disappointment, top-scoring teams, charales champion
// favorites, projected R32 qualifiers (incl. "best 3rd"), and next group fixture.
//
// All data is computed client-side from:
//  - useLiveScoreboard() — shared cached ESPN feed → finals map
//  - one fetch each of AI predictions and human predictions (loadAllPredictionsFromServer)
//  - ELO-derived winProbabilities for the surprise widget
//
// Cross-group "best 3rd" math: rank every group's 3rd place across the 12 groups
// using the same tiebreak chain (pts → GD → GF → alphabetic) and mark the top 8.
// Pre-tournament (no matches played) we still surface the slot via ELO to keep
// the panel useful before kickoff. FIFA's head-to-head tiebreaker is explicitly
// out of scope — comment marks the spot.

import Link from "next/link";
import Image from "next/image";
import { useEffect, useMemo, useState } from "react";
import {
  Trophy, Flame, Sparkles, Crown, Goal, Bot, Gem, Skull, ArrowRight,
  CalendarClock, BarChart3,
} from "lucide-react";

import {
  GROUP_LETTERS, GROUPS, groupFixtures, allGroupFixtures,
  type GroupLetter, type GroupFixture,
} from "@/data/groups";
import { TEAMS, flagUrl, CONFEDERATION_COLORS, type Team } from "@/data/teams";
import { useLiveScoreboard } from "@/lib/live-scoreboard";
import { useLocale } from "@/lib/i18n";
import { winProbabilities } from "@/data/team-ratings";
import { eloOf } from "@/lib/team-strength";
import {
  loadAllPredictionsFromServer, loadOnePredictionFromServer,
  actualPick, type PlayerPredictions, type GroupPrediction, type Pick1X2,
} from "@/lib/predictions";
import { AI_PLAYER_ID } from "@/data/players";
import { fixtureKickoffMs } from "@/lib/fixture-time";
import type { RealResults } from "@/lib/standings";

// ----------------------------------------------------------------------------
// Per-group standings derived ONLY from real finals. Mirrors the math in
// `src/lib/standings.ts` but skipping the player-prediction fallback because
// this page exists to show what's ACTUALLY happening, not what someone picked.
//
// FIFA's official tiebreak chain is head-to-head → GD → GF → fair-play. We
// intentionally do GD → GF → alphabetic; head-to-head is out of scope for the
// live UI and would diverge from the rest of the app's `sortStandings`.
// ----------------------------------------------------------------------------
type LiveStanding = {
  team: string;
  pj: number; pg: number; pe: number; pp: number;
  gf: number; ga: number; gd: number;
  pts: number;
  groupLetter: GroupLetter;
};

function emptyStanding(team: string, group: GroupLetter): LiveStanding {
  return { team, pj: 0, pg: 0, pe: 0, pp: 0, gf: 0, ga: 0, gd: 0, pts: 0, groupLetter: group };
}

function liveSortChain(a: LiveStanding, b: LiveStanding): number {
  if (b.pts !== a.pts) return b.pts - a.pts;
  if (b.gd !== a.gd) return b.gd - a.gd;
  if (b.gf !== a.gf) return b.gf - a.gf;
  return a.team.localeCompare(b.team);
}

function computeLiveGroup(letter: GroupLetter, finals: RealResults): LiveStanding[] {
  const teams = GROUPS[letter];
  const table: Record<string, LiveStanding> = {};
  for (const t of teams) table[t] = emptyStanding(t, letter);
  for (const fx of groupFixtures(letter)) {
    const r = finals[fx.id];
    if (!r) continue;
    const h = table[fx.home];
    const a = table[fx.away];
    if (!h || !a) continue;
    h.pj++; a.pj++;
    h.gf += r.homeGoals; h.ga += r.awayGoals;
    a.gf += r.awayGoals; a.ga += r.homeGoals;
    h.gd = h.gf - h.ga;
    a.gd = a.gf - a.ga;
    if (r.homeGoals > r.awayGoals) { h.pts += 3; h.pg++; a.pp++; }
    else if (r.homeGoals < r.awayGoals) { a.pts += 3; a.pg++; h.pp++; }
    else { h.pts++; a.pts++; h.pe++; a.pe++; }
  }
  return Object.values(table).sort(liveSortChain);
}

// Best 3rd computation across ALL groups. Returns the set of team codes that
// would advance as "best 3rd" today (top 8 of the 12 third-placed teams).
function computeBestThirdSet(finalsByGroup: Record<string, LiveStanding[]>): Set<string> {
  const thirds: LiveStanding[] = [];
  for (const letter of GROUP_LETTERS) {
    const t = finalsByGroup[letter]?.[2];
    if (t) thirds.push(t);
  }
  const sorted = [...thirds].sort(liveSortChain);
  return new Set(sorted.slice(0, 8).map(t => t.team));
}

// ----------------------------------------------------------------------------
// Page
// ----------------------------------------------------------------------------
export default function StandingsPage() {
  const { t } = useLocale();
  const { finals, loading } = useLiveScoreboard();
  const [now, setNow] = useState(() => Date.now());
  const [humanPicks, setHumanPicks] = useState<PlayerPredictions[]>([]);
  const [aiPicks, setAiPicks] = useState<PlayerPredictions | null>(null);

  useEffect(() => {
    const tick = setInterval(() => setNow(Date.now()), 60_000);
    return () => clearInterval(tick);
  }, []);

  useEffect(() => {
    let cancel = false;
    (async () => {
      const [allHumans, ai] = await Promise.all([
        loadAllPredictionsFromServer(),
        loadOnePredictionFromServer(AI_PLAYER_ID),
      ]);
      if (cancel) return;
      // Strip the AI from the humans list — we treat it separately.
      setHumanPicks(allHumans.filter(p => p.playerId !== AI_PLAYER_ID));
      setAiPicks(ai);
    })();
    return () => { cancel = true; };
  }, []);

  // Mark the standings-NEW chip seen on /standings landing so the home card
  // can hide it ahead of the 7-day TTL.
  useEffect(() => {
    try { localStorage.setItem("q26:standings-new-seen-at", String(Date.now() - 7 * 24 * 60 * 60 * 1000)); } catch { /* ignore */ }
  }, []);

  // Compute every group's standings up front so widgets (incl. best-3rd) share
  // the same materialized snapshot.
  const standingsByGroup = useMemo(() => {
    const out: Record<string, LiveStanding[]> = {};
    for (const letter of GROUP_LETTERS) {
      out[letter] = computeLiveGroup(letter, finals);
    }
    return out;
  }, [finals]);

  const bestThirdSet = useMemo(
    () => computeBestThirdSet(standingsByGroup),
    [standingsByGroup],
  );

  const totalFinished = Object.keys(finals).length;
  const totalGroupMatches = allGroupFixtures().length;

  return (
    <div className="bg-canvas">
      {/* Header */}
      <section className="container-app pt-10 md:pt-14 pb-4">
        <div className="flex flex-col md:flex-row md:items-end gap-6 md:justify-between">
          <div>
            <span className="chip mb-3"><BarChart3 size={12} /> {t("standings.kicker")}</span>
            <h1 className="font-display text-4xl md:text-6xl font-bold leading-tight">
              <span className="grad-text">{t("standings.titleA")}</span><br />
              {t("standings.titleB")}
            </h1>
            <p className="mt-3 text-[var(--ink-soft)] max-w-2xl">
              {t("standings.subtitle")}
            </p>
          </div>

          <div className="self-start glass rounded-3xl px-4 py-3 text-sm flex items-center gap-4">
            <div>
              <div className="text-[10px] uppercase tracking-[0.18em] text-[var(--ink-muted)]">{t("standings.played")}</div>
              <div className="font-display text-xl font-bold tnum">
                {totalFinished}<span className="text-[var(--ink-muted)] text-base">/{totalGroupMatches}</span>
              </div>
            </div>
            <div className="w-px h-8 bg-[var(--line)]" />
            <div>
              <div className="text-[10px] uppercase tracking-[0.18em] text-[var(--ink-muted)]">{t("standings.live")}</div>
              <div className="flex items-center gap-1.5 text-xs font-semibold">
                <span className="live-dot" /> ESPN
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Legend */}
      <section className="container-app pb-6">
        <div className="flex flex-wrap items-center gap-2 text-[10px]">
          <span className="inline-flex items-center gap-1.5 chip" style={{ background: "#D4AF3722", color: "#A07A1F" }}>
            <Crown size={10} /> 1° {t("standings.legend.qualifies")}
          </span>
          <span className="inline-flex items-center gap-1.5 chip" style={{ background: "#9CA3AF22", color: "#525252" }}>
            <Crown size={10} /> 2° {t("standings.legend.qualifies")}
          </span>
          <span className="inline-flex items-center gap-1.5 chip" style={{ background: "#B4530922", color: "#92400E" }}>
            <Sparkles size={10} /> 3° {t("standings.legend.bestThird")}
          </span>
          <span className="chip" style={{ background: "var(--bg-tint)" }}>{t("standings.legend.out")}</span>
        </div>
      </section>

      {/* Groups grid: 1 col mobile, 2 cols on md+ */}
      <section className="container-app pb-20">
        {loading && totalFinished === 0 && (
          <div className="glass rounded-2xl p-4 mb-5 text-sm text-[var(--ink-soft)]">
            {t("standings.loading")}
          </div>
        )}

        <div className="grid md:grid-cols-2 gap-5">
          {GROUP_LETTERS.map((letter, idx) => (
            <GroupStandingsPanel
              key={letter}
              letter={letter}
              standings={standingsByGroup[letter] ?? []}
              finals={finals}
              now={now}
              humanPicks={humanPicks}
              aiPicks={aiPicks}
              standingsByGroup={standingsByGroup}
              bestThirdSet={bestThirdSet}
              defaultExpanded={idx === 0}
            />
          ))}
        </div>
      </section>
    </div>
  );
}

// ----------------------------------------------------------------------------
// Per-group panel
// ----------------------------------------------------------------------------
function GroupStandingsPanel({
  letter, standings, finals, now, humanPicks, aiPicks, standingsByGroup, bestThirdSet, defaultExpanded,
}: {
  letter: GroupLetter;
  standings: LiveStanding[];
  finals: RealResults;
  now: number;
  humanPicks: PlayerPredictions[];
  aiPicks: PlayerPredictions | null;
  standingsByGroup: Record<string, LiveStanding[]>;
  bestThirdSet: Set<string>;
  defaultExpanded: boolean;
}) {
  const { t } = useLocale();
  const teams = standings.map(s => TEAMS.find(x => x.code === s.team)).filter(Boolean) as Team[];
  const accent = teams[0] ? CONFEDERATION_COLORS[teams[0].confederation] : "#5E5BFF";
  const fixtures = groupFixtures(letter);

  const totalGroupFinished = fixtures.filter(fx => finals[fx.id]).length;

  return (
    <div className="glass rounded-3xl overflow-hidden relative">
      {/* Accent rail */}
      <div className="h-1.5 w-full" style={{ background: `linear-gradient(90deg, ${accent}, ${accent}66, transparent)` }} />

      <div className="p-5 relative">
        {/* Group letter watermark */}
        <div className="absolute -top-4 right-3 font-display text-[96px] font-bold text-[var(--bg-tint)] leading-none select-none pointer-events-none">
          {letter}
        </div>

        {/* Header */}
        <div className="flex items-center justify-between mb-4 relative">
          <div className="flex items-center gap-2">
            <div
              className="w-10 h-10 rounded-xl text-white grid place-items-center font-display font-bold"
              style={{ background: "var(--ink)" }}
            >
              {letter}
            </div>
            <div>
              <div className="text-[10px] uppercase tracking-[0.18em] text-[var(--ink-muted)]">
                {t("standings.groupKicker")}
              </div>
              <div className="font-display font-semibold text-sm">
                {totalGroupFinished}/{fixtures.length} {t("standings.matchesPlayed")}
              </div>
            </div>
          </div>
          <Link
            href={`/grupos#${letter}`}
            className="text-[10px] uppercase tracking-[0.18em] text-[var(--ink-muted)] hover:text-[var(--ink)] inline-flex items-center gap-1"
          >
            {t("standings.roster")} <ArrowRight size={11} />
          </Link>
        </div>

        {/* Standings table */}
        <StandingsTable
          rows={standings}
          bestThirdSet={bestThirdSet}
          accent={accent}
        />

        {/* Widget grid (7 widgets) — Group A starts expanded so users see the
            feature exists; B–L collapsed to keep the page scannable. */}
        <details open={defaultExpanded} className="group mt-5">
          <summary className="cursor-pointer list-none flex items-center justify-between rounded-xl px-3 py-2 hover:bg-[var(--bg-tint)] transition-colors select-none">
            <span className="text-[11px] uppercase tracking-[0.18em] font-bold text-[var(--ink-soft)]">
              {t("standings.widgets.title")}
            </span>
            <span className="text-[10px] uppercase tracking-wider text-[var(--ink-muted)] inline-flex items-center gap-1">
              <span className="group-open:hidden">{t("standings.widgets.show")}</span>
              <span className="hidden group-open:inline">{t("standings.widgets.hide")}</span>
              <span aria-hidden className="inline-block transition-transform group-open:rotate-180">▾</span>
            </span>
          </summary>
          <div className="mt-3 grid sm:grid-cols-2 gap-3">
            <DramaMeterWidget standings={standings} accent={accent} />
            <AiVsRealityWidget letter={letter} aiPicks={aiPicks} finals={finals} fixtures={fixtures} />
            <SurpriseWidget standings={standings} fixtures={fixtures} finals={finals} />
            <TopScorerWidget standings={standings} />
            <ChampionFavoriteWidget letter={letter} humanPicks={humanPicks} />
            <QualifiersWidget standings={standings} bestThirdSet={bestThirdSet} fixtures={fixtures} finals={finals} />
            <NextFixtureWidget letter={letter} fixtures={fixtures} finals={finals} now={now} />
          </div>
        </details>
      </div>
    </div>
  );
}

// ----------------------------------------------------------------------------
// Standings table
// ----------------------------------------------------------------------------
function rowAccent(idx: number, team: string, bestThirdSet: Set<string>): { bg: string; bar: string; pill: string; label?: string } {
  // 1st = gold, 2nd = silver, 3rd = bronze (only if best-3rd qualifies), 4th plain
  if (idx === 0) return { bg: "linear-gradient(90deg, #FFF5C422 0%, transparent 100%)", bar: "#D4AF37", pill: "bg-amber-100 text-amber-800 ring-amber-200" };
  if (idx === 1) return { bg: "linear-gradient(90deg, #E5E5E522 0%, transparent 100%)", bar: "#9CA3AF", pill: "bg-zinc-100 text-zinc-700 ring-zinc-200" };
  if (idx === 2 && bestThirdSet.has(team)) return { bg: "linear-gradient(90deg, #FED7AA22 0%, transparent 100%)", bar: "#B45309", pill: "bg-orange-100 text-orange-800 ring-orange-200" };
  return { bg: "transparent", bar: "transparent", pill: "bg-transparent text-[var(--ink-muted)] ring-transparent" };
}

function StandingsTable({
  rows, bestThirdSet, accent,
}: {
  rows: LiveStanding[];
  bestThirdSet: Set<string>;
  accent: string;
}) {
  const { t } = useLocale();
  return (
    <div className="rounded-2xl overflow-hidden ring-1 ring-[var(--line)]">
      <div className="grid grid-cols-[28px_1fr_28px_28px_28px_28px_28px_28px_36px] sm:grid-cols-[28px_1fr_30px_30px_30px_30px_38px_38px_40px] gap-1 px-2.5 py-1.5 bg-[var(--bg-tint)] text-[9px] font-bold uppercase tracking-wider text-[var(--ink-muted)]">
        <span className="text-center">#</span>
        <span>{t("standings.col.team")}</span>
        <span className="text-center hidden sm:inline">{t("standings.col.pj")}</span>
        <span className="text-center hidden sm:inline">{t("standings.col.pg")}</span>
        <span className="text-center hidden sm:inline">{t("standings.col.pe")}</span>
        <span className="text-center hidden sm:inline">{t("standings.col.pp")}</span>
        <span className="text-center sm:hidden">{t("standings.col.pj")}</span>
        <span className="text-center hidden sm:inline">{t("standings.col.gf")}</span>
        <span className="text-center hidden sm:inline">{t("standings.col.ga")}</span>
        <span className="text-center">{t("standings.col.gd")}</span>
        <span className="text-center">{t("standings.col.pts")}</span>
      </div>
      {rows.map((r, idx) => {
        const team = TEAMS.find(x => x.code === r.team);
        if (!team) return null;
        const acc = rowAccent(idx, r.team, bestThirdSet);
        return (
          <div
            key={r.team}
            className="grid grid-cols-[28px_1fr_28px_28px_28px_28px_28px_28px_36px] sm:grid-cols-[28px_1fr_30px_30px_30px_30px_38px_38px_40px] gap-1 items-center px-2.5 py-2 border-t border-[var(--line)] relative"
            style={{ background: acc.bg }}
          >
            <div className="absolute left-0 top-0 bottom-0 w-1" style={{ background: acc.bar }} />
            <span className="text-center text-xs font-bold tnum">{idx + 1}</span>
            <Link href={`/equipos/${team.code}`} className="flex items-center gap-2 min-w-0 hover:opacity-80 transition-opacity">
              <div className="relative w-5 h-5 rounded-full overflow-hidden ring-1 ring-[var(--line)] shrink-0">
                <Image src={flagUrl(team.iso2, 32)} alt={team.name} fill sizes="20px" className="object-cover" unoptimized />
              </div>
              <span className="font-display text-xs font-bold truncate">{team.code}</span>
              <span className="text-[10px] text-[var(--ink-muted)] hidden md:inline truncate">{team.name}</span>
            </Link>
            <span className="text-center text-[11px] tnum hidden sm:inline">{r.pj}</span>
            <span className="text-center text-[11px] tnum hidden sm:inline">{r.pg}</span>
            <span className="text-center text-[11px] tnum hidden sm:inline">{r.pe}</span>
            <span className="text-center text-[11px] tnum hidden sm:inline">{r.pp}</span>
            <span className="text-center text-[11px] tnum sm:hidden">{r.pj}</span>
            <span className="text-center text-[11px] tnum hidden sm:inline">{r.gf}</span>
            <span className="text-center text-[11px] tnum hidden sm:inline">{r.ga}</span>
            <span className={`text-center text-[11px] tnum ${r.gd > 0 ? "text-emerald-600" : r.gd < 0 ? "text-rose-600" : ""}`}>
              {r.gd > 0 ? `+${r.gd}` : r.gd}
            </span>
            <span className="text-center text-[12px] font-extrabold tnum">{r.pts}</span>
          </div>
        );
      })}
    </div>
  );
}

// ----------------------------------------------------------------------------
// Widget 1 — Drama Meter
// ----------------------------------------------------------------------------
function DramaMeterWidget({ standings, accent }: { standings: LiveStanding[]; accent: string }) {
  const { t } = useLocale();
  const played = standings.reduce((sum, s) => sum + s.pj, 0) / 2; // each match counted twice
  // No matches → drama is undefined; show neutral state.
  if (played < 1) {
    return (
      <WidgetCard icon={<Flame size={12} />} title={t("standings.widget.drama")} accent={accent}>
        <div className="text-[11px] text-[var(--ink-muted)]">{t("standings.widget.dramaIdle")}</div>
      </WidgetCard>
    );
  }
  const pts = standings.map(s => s.pts);
  const mean = pts.reduce((a, b) => a + b, 0) / pts.length;
  const variance = pts.reduce((a, b) => a + (b - mean) ** 2, 0) / pts.length;
  const std = Math.sqrt(variance);
  // Max possible stdev when one team has 9 pts and others have 0 → 3.897.
  // Scale relative to 9 pts cap; this is a "feel" metric not a math identity.
  const maxStd = 3.897;
  const drama = Math.max(0, Math.min(1, 1 - std / maxStd));
  const dramaPct = Math.round(drama * 100);
  const label =
    drama >= 0.78 ? `🔪 ${t("standings.widget.dramaKnife")}` :
    drama >= 0.55 ? `🌶️ ${t("standings.widget.dramaTight")}` :
    `💣 ${t("standings.widget.dramaBlowout")}`;

  return (
    <WidgetCard icon={<Flame size={12} />} title={t("standings.widget.drama")} accent={accent}>
      <div className="flex items-baseline justify-between mb-1">
        <span className="text-xs font-extrabold">{dramaPct}</span>
        <span className="text-[10px] font-semibold">{label}</span>
      </div>
      <div className="h-2 rounded-full bg-[var(--bg-tint)] overflow-hidden">
        <div
          className="h-full rounded-full transition-all duration-500"
          style={{ width: `${dramaPct}%`, background: `linear-gradient(90deg, ${accent}, ${accent}aa)` }}
        />
      </div>
    </WidgetCard>
  );
}

// ----------------------------------------------------------------------------
// Widget 2 — AI Bot Pick vs Reality
// ----------------------------------------------------------------------------
function AiVsRealityWidget({
  letter, aiPicks, finals, fixtures,
}: {
  letter: GroupLetter;
  aiPicks: PlayerPredictions | null;
  finals: RealResults;
  fixtures: GroupFixture[];
}) {
  const { t } = useLocale();
  const accent = "#5E5BFF";

  if (!aiPicks) {
    return (
      <WidgetCard icon={<Bot size={12} />} title={t("standings.widget.aiVsReality")} accent={accent}>
        <div className="text-[11px] text-[var(--ink-muted)]">{t("standings.widget.aiLoading")}</div>
      </WidgetCard>
    );
  }

  type Cell = { fxId: string; status: "exact" | "sign" | "miss" | "pending" | "nopick" };
  const cells: Cell[] = fixtures.map(fx => {
    const ai = aiPicks.group[fx.id];
    const real = finals[fx.id];
    if (!ai?.pick) return { fxId: fx.id, status: "nopick" };
    if (!real) return { fxId: fx.id, status: "pending" };
    const realPick: Pick1X2 = actualPick({ home: fx.home, away: fx.away, homeGoals: real.homeGoals, awayGoals: real.awayGoals });
    const matchedSign = ai.pick === realPick;
    if (!matchedSign) return { fxId: fx.id, status: "miss" };
    const matchedExact =
      Number.isFinite(ai.homeGoals) && Number.isFinite(ai.awayGoals) &&
      ai.homeGoals === real.homeGoals && ai.awayGoals === real.awayGoals;
    return { fxId: fx.id, status: matchedExact ? "exact" : "sign" };
  });

  const evalCount = cells.filter(c => c.status === "exact" || c.status === "sign" || c.status === "miss").length;
  const hits = cells.filter(c => c.status === "exact" || c.status === "sign").length;
  const hitPct = evalCount > 0 ? Math.round((hits / evalCount) * 100) : null;

  return (
    <WidgetCard icon={<Bot size={12} />} title={t("standings.widget.aiVsReality")} accent={accent}>
      <div className="flex items-center justify-between">
        <div className="grid grid-cols-6 gap-1">
          {cells.map((c, i) => {
            const cls =
              c.status === "exact" ? "bg-emerald-500 ring-emerald-300" :
              c.status === "sign" ? "bg-emerald-200 ring-emerald-300" :
              c.status === "miss" ? "bg-rose-400 ring-rose-300" :
              c.status === "pending" ? "bg-[var(--bg-tint)] ring-[var(--line)]" :
              "bg-white ring-[var(--line)]";
            const label =
              c.status === "exact" ? t("standings.widget.aiExact") :
              c.status === "sign" ? t("standings.widget.aiHit") :
              c.status === "miss" ? t("standings.widget.aiMiss") :
              c.status === "pending" ? t("standings.widget.aiPending") :
              t("standings.widget.aiNoPick");
            return (
              <div
                key={i}
                title={`${c.fxId} · ${label}`}
                className={`w-4 h-4 rounded-md ring-1 ${cls}`}
              />
            );
          })}
        </div>
        <span className="text-[11px] font-extrabold tnum">
          {hitPct == null ? "—" : `${hitPct}%`}
        </span>
      </div>
      <div className="text-[10px] text-[var(--ink-muted)] mt-1.5">
        {t("standings.widget.aiHint")}
      </div>
    </WidgetCard>
  );
}

// ----------------------------------------------------------------------------
// Widget 3 — Sorpresa / Decepción
// ----------------------------------------------------------------------------
function SurpriseWidget({
  standings, fixtures, finals,
}: {
  standings: LiveStanding[];
  fixtures: GroupFixture[];
  finals: RealResults;
}) {
  const { t } = useLocale();
  const accent = "#10B981";

  // Compute expected pts per team using winProbabilities of each played match.
  const expected: Record<string, number> = {};
  for (const s of standings) expected[s.team] = 0;
  let matchesScored = 0;
  for (const fx of fixtures) {
    if (!finals[fx.id]) continue;
    const probs = winProbabilities(fx.home, fx.away); // 0..100 ints summing to 100
    const eHome = (3 * probs.home + probs.draw) / 100;
    const eAway = (3 * probs.away + probs.draw) / 100;
    if (expected[fx.home] !== undefined) expected[fx.home] += eHome;
    if (expected[fx.away] !== undefined) expected[fx.away] += eAway;
    matchesScored++;
  }

  if (matchesScored === 0) {
    return (
      <WidgetCard icon={<Gem size={12} />} title={t("standings.widget.surprise")} accent={accent}>
        <div className="text-[11px] text-[var(--ink-muted)]">{t("standings.widget.surpriseIdle")}</div>
      </WidgetCard>
    );
  }

  const deltas = standings.map(s => ({ team: s.team, delta: s.pts - (expected[s.team] ?? 0) }));
  const surprise = deltas.reduce((best, d) => d.delta > best.delta ? d : best, deltas[0]);
  const disappoint = deltas.reduce((worst, d) => d.delta < worst.delta ? d : worst, deltas[0]);

  return (
    <WidgetCard icon={<Gem size={12} />} title={t("standings.widget.surprise")} accent={accent}>
      <div className="space-y-1">
        {surprise.delta > 0.5 && (
          <div className="flex items-center gap-1.5 text-[11px]">
            <span className="text-emerald-600 font-bold">💎</span>
            <TeamChip code={surprise.team} />
            <span className="text-[10px] text-emerald-600 font-bold tnum ml-auto">+{surprise.delta.toFixed(1)}</span>
          </div>
        )}
        {disappoint.delta < -0.5 && disappoint.team !== surprise.team && (
          <div className="flex items-center gap-1.5 text-[11px]">
            <Skull size={11} className="text-rose-500" />
            <TeamChip code={disappoint.team} />
            <span className="text-[10px] text-rose-500 font-bold tnum ml-auto">{disappoint.delta.toFixed(1)}</span>
          </div>
        )}
        {surprise.delta <= 0.5 && disappoint.delta >= -0.5 && (
          <div className="text-[10px] text-[var(--ink-muted)]">{t("standings.widget.surpriseFlat")}</div>
        )}
      </div>
    </WidgetCard>
  );
}

// ----------------------------------------------------------------------------
// Widget 4 — Top scorer (DEGRADED: team-level only)
// ESPN's scoreboard summary doesn't expose player-level scorers in our cached
// payload (see src/lib/scoreboard-cache.ts → EspnEvent shape). Player goal
// data lives in the per-event summary endpoint we don't fetch on this page.
// Fallback: rank teams by goals scored.
// ----------------------------------------------------------------------------
function TopScorerWidget({ standings }: { standings: LiveStanding[] }) {
  const { t } = useLocale();
  const accent = "#F59E0B";
  const played = standings.reduce((sum, s) => sum + s.pj, 0) / 2;
  if (played < 1) {
    return (
      <WidgetCard icon={<Goal size={12} />} title={t("standings.widget.scorers")} accent={accent}>
        <div className="text-[11px] text-[var(--ink-muted)]">{t("standings.widget.scorersIdle")}</div>
      </WidgetCard>
    );
  }
  const ranked = [...standings].sort((a, b) => b.gf - a.gf).slice(0, 3).filter(s => s.gf > 0);
  return (
    <WidgetCard icon={<Goal size={12} />} title={t("standings.widget.scorers")} accent={accent}>
      <div className="flex flex-col gap-1">
        {ranked.length === 0 && (
          <div className="text-[11px] text-[var(--ink-muted)]">{t("standings.widget.scorersNone")}</div>
        )}
        {ranked.map((s, idx) => (
          <div key={s.team} className="flex items-center gap-1.5 text-[11px]">
            <span className="text-[10px] font-bold w-3 text-[var(--ink-muted)]">{idx + 1}</span>
            <TeamChip code={s.team} />
            <span className="text-[10px] text-[var(--ink-muted)] ml-auto">⚽ <span className="font-extrabold text-[var(--ink)] tnum">{s.gf}</span></span>
          </div>
        ))}
      </div>
    </WidgetCard>
  );
}

// ----------------------------------------------------------------------------
// Widget 5 — Charales champion favorite (in this group)
// ----------------------------------------------------------------------------
function ChampionFavoriteWidget({
  letter, humanPicks,
}: {
  letter: GroupLetter;
  humanPicks: PlayerPredictions[];
}) {
  const { t } = useLocale();
  const accent = "#EAB308";
  const groupTeams = new Set(GROUPS[letter]);
  const counts = new Map<string, { champion: number; runnerUp: number }>();
  for (const p of humanPicks) {
    if (p.champion && groupTeams.has(p.champion)) {
      const cur = counts.get(p.champion) ?? { champion: 0, runnerUp: 0 };
      cur.champion++;
      counts.set(p.champion, cur);
    }
    if (p.runnerUp && groupTeams.has(p.runnerUp)) {
      const cur = counts.get(p.runnerUp) ?? { champion: 0, runnerUp: 0 };
      cur.runnerUp++;
      counts.set(p.runnerUp, cur);
    }
  }
  const sorted = [...counts.entries()]
    .map(([team, c]) => ({ team, ...c, total: c.champion + c.runnerUp }))
    .sort((a, b) => b.champion - a.champion || b.runnerUp - a.runnerUp)
    .filter(r => r.total > 0)
    .slice(0, 2);

  if (sorted.length === 0) {
    return (
      <WidgetCard icon={<Crown size={12} />} title={t("standings.widget.charalFav")} accent={accent}>
        <div className="text-[11px] text-[var(--ink-muted)]">{t("standings.widget.charalFavNone")}</div>
      </WidgetCard>
    );
  }

  return (
    <WidgetCard icon={<Crown size={12} />} title={t("standings.widget.charalFav")} accent={accent}>
      <div className="space-y-1">
        {sorted.map(r => (
          <div key={r.team} className="flex items-center gap-1.5 text-[11px]">
            <TeamChip code={r.team} />
            <div className="ml-auto flex items-center gap-1.5 text-[10px]">
              {r.champion > 0 && (
                <span className="inline-flex items-center gap-0.5 px-1.5 py-0.5 rounded-full bg-amber-100 text-amber-800 font-bold">
                  👑 {r.champion}
                </span>
              )}
              {r.runnerUp > 0 && (
                <span className="inline-flex items-center gap-0.5 px-1.5 py-0.5 rounded-full bg-zinc-100 text-zinc-700 font-bold">
                  🥈 {r.runnerUp}
                </span>
              )}
            </div>
          </div>
        ))}
      </div>
    </WidgetCard>
  );
}

// ----------------------------------------------------------------------------
// Widget 6 — Pase a 32avos (provisional)
// ----------------------------------------------------------------------------
function QualifiersWidget({
  standings, bestThirdSet, fixtures, finals,
}: {
  standings: LiveStanding[];
  bestThirdSet: Set<string>;
  fixtures: GroupFixture[];
  finals: RealResults;
}) {
  const { t } = useLocale();
  const accent = "#0EA5E9";
  const top2 = standings.slice(0, 2);
  const third = standings[2];
  const groupFinished = fixtures.every(fx => finals[fx.id]);
  const matchesPlayed = fixtures.filter(fx => finals[fx.id]).length;

  // Pre-tournament expectation: top-2 by ELO.
  const expectedTop2 = [...GROUPS[standings[0]?.groupLetter ?? "A"]]
    .map(code => ({ code, elo: eloOf(code) }))
    .sort((a, b) => b.elo - a.elo)
    .slice(0, 2)
    .map(x => x.code);

  return (
    <WidgetCard icon={<Trophy size={12} />} title={t("standings.widget.qualifiers")} accent={accent}>
      <div className="space-y-1">
        {top2.map((s, idx) => {
          const isExpected = expectedTop2.includes(s.team);
          return (
            <div key={s.team} className="flex items-center gap-1.5 text-[11px]">
              <span className="text-[10px] font-bold text-[var(--ink-muted)] w-3">{idx + 1}°</span>
              <TeamChip code={s.team} highlight />
              {!isExpected && matchesPlayed > 0 && (
                <span className="text-[9px] text-emerald-600 font-bold ml-1">⚡</span>
              )}
              <span className="ml-auto text-[10px] text-[var(--ink-muted)] tnum">{s.pts} pts</span>
            </div>
          );
        })}
        {third && (
          <div className="flex items-center gap-1.5 text-[11px] mt-0.5 pt-1 border-t border-[var(--line)]">
            <span className="text-[10px] font-bold text-[var(--ink-muted)] w-3">3°</span>
            <TeamChip code={third.team} dimmed={!bestThirdSet.has(third.team)} />
            {bestThirdSet.has(third.team) && (
              <span className="text-[9px] font-bold text-orange-700 ml-1">✨ {t("standings.widget.qualifiersBest3rd")}</span>
            )}
            <span className="ml-auto text-[10px] text-[var(--ink-muted)] tnum">{third.pts} pts</span>
          </div>
        )}
        {!groupFinished && matchesPlayed > 0 && (
          <div className="text-[9px] text-[var(--ink-muted)] mt-0.5 italic">
            {t("standings.widget.qualifiersProvisional")}
          </div>
        )}
      </div>
    </WidgetCard>
  );
}

// ----------------------------------------------------------------------------
// Widget 7 — Next group fixture
// ----------------------------------------------------------------------------
function NextFixtureWidget({
  letter, fixtures, finals, now,
}: {
  letter: GroupLetter;
  fixtures: GroupFixture[];
  finals: RealResults;
  now: number;
}) {
  const { t } = useLocale();
  const accent = "#EC4899";
  const upcoming = fixtures
    .filter(fx => !finals[fx.id])
    .map(fx => ({ fx, ms: fixtureKickoffMs(fx) }))
    .filter(x => x.ms >= now - 6 * 60 * 60 * 1000) // include the past 6h so live matches don't drop off
    .sort((a, b) => a.ms - b.ms)[0];

  if (!upcoming) {
    return (
      <WidgetCard icon={<CalendarClock size={12} />} title={t("standings.widget.next")} accent={accent}>
        <div className="text-[11px] text-[var(--ink-muted)]">{t("standings.widget.nextDone")}</div>
      </WidgetCard>
    );
  }

  const fx = upcoming.fx;
  const home = TEAMS.find(t => t.code === fx.home);
  const away = TEAMS.find(t => t.code === fx.away);
  const isToday = new Date(upcoming.ms).toDateString() === new Date(now).toDateString();
  const dateLabel = new Intl.DateTimeFormat(undefined, { weekday: "short", day: "numeric", month: "short" }).format(new Date(upcoming.ms));
  const timeLabel = new Intl.DateTimeFormat(undefined, { hour: "2-digit", minute: "2-digit", hour12: false }).format(new Date(upcoming.ms));

  return (
    <WidgetCard icon={<CalendarClock size={12} />} title={t("standings.widget.next")} accent={accent}>
      <Link href={`/quiniela#${letter}-M${fx.matchday}`} className="block group">
        <div className="flex items-center gap-2">
          <div className="relative w-5 h-5 rounded-full overflow-hidden ring-1 ring-[var(--line)] shrink-0">
            {home && <Image src={flagUrl(home.iso2, 32)} alt="" fill sizes="20px" className="object-cover" unoptimized />}
          </div>
          <span className="font-display text-xs font-bold">{fx.home}</span>
          <span className="text-[10px] text-[var(--ink-muted)]">vs</span>
          <span className="font-display text-xs font-bold">{fx.away}</span>
          <div className="relative w-5 h-5 rounded-full overflow-hidden ring-1 ring-[var(--line)] shrink-0">
            {away && <Image src={flagUrl(away.iso2, 32)} alt="" fill sizes="20px" className="object-cover" unoptimized />}
          </div>
          <span className="ml-auto text-[10px] font-semibold text-[var(--ink-muted)] group-hover:text-[var(--ink)]">
            {isToday ? t("standings.widget.nextToday") : dateLabel} · {timeLabel}
          </span>
        </div>
      </Link>
    </WidgetCard>
  );
}

// ----------------------------------------------------------------------------
// Shared widget card chrome
// ----------------------------------------------------------------------------
function WidgetCard({
  icon, title, accent, children,
}: {
  icon: React.ReactNode;
  title: string;
  accent: string;
  children: React.ReactNode;
}) {
  return (
    <div className="rounded-2xl bg-white/70 ring-1 ring-[var(--line)] p-2.5 relative overflow-hidden">
      <div className="absolute top-0 left-0 w-1 h-full" style={{ background: accent }} />
      <div className="flex items-center gap-1.5 mb-1.5 text-[10px] uppercase tracking-[0.16em] font-bold text-[var(--ink-muted)]">
        <span style={{ color: accent }}>{icon}</span>
        <span>{title}</span>
      </div>
      {children}
    </div>
  );
}

function TeamChip({ code, highlight, dimmed }: { code: string; highlight?: boolean; dimmed?: boolean }) {
  const team = TEAMS.find(t => t.code === code);
  if (!team) return <span className="text-[11px]">{code}</span>;
  return (
    <Link href={`/equipos/${code}`} className={`inline-flex items-center gap-1.5 hover:opacity-80 transition-opacity ${dimmed ? "opacity-60" : ""}`}>
      <div className="relative w-4 h-4 rounded-full overflow-hidden ring-1 ring-[var(--line)] shrink-0">
        <Image src={flagUrl(team.iso2, 32)} alt="" fill sizes="16px" className="object-cover" unoptimized />
      </div>
      <span className={`font-display text-[11px] font-bold ${highlight ? "text-[var(--ink)]" : ""}`}>{team.code}</span>
    </Link>
  );
}
