"use client";

import Link from "next/link";
import Image from "next/image";
import { motion, AnimatePresence } from "framer-motion";
import { useEffect, useState } from "react";
import { Crown, Trophy, Medal, Coins, TrendingUp, Target, RefreshCw } from "lucide-react";
import { POT_TOTAL_MXN, AI_PLAYER_ID } from "@/data/players";
import { TEAMS, flagUrl } from "@/data/teams";
import { allGroupFixtures } from "@/data/groups";
import { fixtureKickoffMs } from "@/lib/fixture-time";
import { loadAllPredictions, loadAllPredictionsFromServer, computePlayerScoreDetail, fillStats, actualPick, type MatchResult, type PlayerPredictions } from "@/lib/predictions";
import { etDate } from "@/lib/daily-streak";
import { usePlayer } from "@/lib/player-context";
import type { EspnScoreboard } from "@/lib/espn";
import { PlayerAvatar } from "@/components/PlayerAvatar";
import { CharalProfileTrigger } from "@/components/CharalProfileModal";
import { RankDeltaChip } from "@/components/RankDeltaChip";
import { prefetchRoast, type FinalsMap } from "@/lib/roast-cache";
import { intlLocale, useLocale } from "@/lib/i18n";

type Row = {
  id: string;
  name: string;
  emoji: string;
  accent: string;
  photoDataUrl?: string;
  score: number;
  exactHits: number;
  signHits: number;
  bracketHits: number;
  pct: number;
  champion?: string;
  isMe: boolean;
  hotStreak?: number;
};

export default function LeaderboardPage() {
  const { currentPlayer, players } = usePlayer();
  const { t, locale } = useLocale();
  const [actuals, setActuals] = useState<Record<string, MatchResult>>({});
  const [rows, setRows] = useState<Row[]>([]);
  const [refreshing, setRefreshing] = useState(false);
  const [serverPicksLoaded, setServerPicksLoaded] = useState(false);
  const [lastSync, setLastSync] = useState<number>(0);
  const [allMundialPicks, setAllMundialPicks] = useState<PlayerPredictions[]>([]);
  const [koResults, setKoResults] = useState<Record<string, string>>({});

  async function loadKoResults() {
    try {
      const res = await fetch("/api/bracket/ko-results", { cache: "no-store" });
      const j = await res.json();
      if (j?.ok) setKoResults(j.slotResults ?? {});
    } catch {}
  }

  async function loadEspnActuals() {
    setRefreshing(true);
    try {
      const res = await fetch("/api/scoreboard");
      const json: { ok: boolean } & EspnScoreboard = await res.json();
      if (!json.ok || !json.events) return;
      const map: Record<string, MatchResult> = {};
      const fixturesByPair = new Map<string, string>();
      for (const fx of allGroupFixtures()) {
        fixturesByPair.set(`${fx.home}-${fx.away}`, fx.id);
        fixturesByPair.set(`${fx.away}-${fx.home}`, fx.id);
      }
      for (const e of json.events) {
        if (e.status.type.state !== "post") continue;
        const c = e.competitions[0];
        const h = c.competitors.find(cp => cp.homeAway === "home")!;
        const a = c.competitors.find(cp => cp.homeAway === "away")!;
        const fxId = fixturesByPair.get(`${h.team.abbreviation}-${a.team.abbreviation}`);
        if (!fxId) continue;
        map[fxId] = {
          home: h.team.abbreviation,
          away: a.team.abbreviation,
          homeGoals: Number(h.score),
          awayGoals: Number(a.score),
        };
      }
      setActuals(map);
      setLastSync(Date.now());
    } catch {}
    finally { setRefreshing(false); }
  }

  function recompute() {
    const local = loadAllPredictions();
    const all = local.map(loc => {
      const remote = allMundialPicks.find(r => r.playerId === loc.playerId);
      if (!remote) return loc;
      return (loc.updatedAt ?? 0) > (remote.updatedAt ?? 0) ? loc : remote;
    });
    // Today-only hot streak: walk today's FINAL fixtures in reverse kickoff
    // order and count consecutive 1X2 hits. Players with <2 in a row don't
    // get a chip rendered.
    const today = etDate();
    const todaysFinalsByKickoff = allGroupFixtures()
      .filter(fx => fx.date === today && actuals[fx.id])
      .map(fx => ({ id: fx.id, t: fixtureKickoffMs(fx) }))
      .sort((a, b) => b.t - a.t);
    const hotStreakByPlayer = new Map<string, number>();
    for (const p of all) {
      let n = 0;
      for (const fx of todaysFinalsByKickoff) {
        const pred = p.group[fx.id];
        if (!pred) break;
        if (pred.pick !== actualPick(actuals[fx.id])) break;
        n += 1;
      }
      if (n >= 2) hotStreakByPlayer.set(p.playerId, n);
    }
    const computed = all.map(p => {
      const player = players.find(pp => pp.id === p.playerId)!;
      const stats = fillStats(p);
      const detail = computePlayerScoreDetail(p, actuals, koResults);
      return {
        id: player.id,
        name: player.name,
        emoji: player.emoji,
        accent: player.accent,
        photoDataUrl: player.photoDataUrl,
        score: detail.score,
        exactHits: detail.exactHits,
        signHits: detail.signHits,
        bracketHits: detail.bracketHits,
        pct: stats.percent,
        champion: stats.champion,
        isMe: currentPlayer?.id === player.id,
        hotStreak: hotStreakByPlayer.get(player.id),
      } satisfies Row;
    }).sort((a, b) =>
      b.score - a.score ||
      b.exactHits - a.exactHits ||
      b.signHits - a.signHits ||
      a.name.localeCompare(b.name),
    );
    setRows(computed);
  }

  useEffect(() => { loadEspnActuals(); loadKoResults(); }, []);
  useEffect(() => { recompute(); }, [actuals, currentPlayer, players, allMundialPicks, koResults]);

  // Prefetch Ava's roast for every charal in parallel as soon as we have rows
  // + finals — so clicking a row on /leaderboard lands on /jugadores/[id] with
  // the analysis already in cache. Re-fires when actuals change (a new marker
  // arrival invalidates the per-finals cache key automatically).
  useEffect(() => {
    if (rows.length === 0) return;
    const finals: FinalsMap = {};
    for (const [fxId, r] of Object.entries(actuals)) {
      finals[fxId] = { homeGoals: r.homeGoals, awayGoals: r.awayGoals };
    }
    for (const r of rows) prefetchRoast(r.id, finals, koResults);
  }, [rows, actuals]);

  // Pull every compa's picks from Firestore so the leaderboard shows real
  // progress for everyone, not just whoever is logged in on this device.
  useEffect(() => {
    let cancelled = false;
    const hydrate = async () => {
      try {
        const all = await loadAllPredictionsFromServer();
        if (!cancelled) { setAllMundialPicks(all); setServerPicksLoaded(true); }
      } catch { if (!cancelled) setServerPicksLoaded(true); }
    };
    hydrate();
    return () => { cancelled = true; };
  }, []);

  useEffect(() => {
    const onUpd = () => recompute();
    window.addEventListener("q26:predictions-updated", onUpd);
    return () => {
      window.removeEventListener("q26:predictions-updated", onUpd);
    };
  }, [actuals, currentPlayer, players, allMundialPicks, koResults]);

  // Separate humans from the AI bot. AI participates as benchmark only —
  // it doesn't compete for the pot and doesn't appear in the podium.
  const humanRows = rows.filter(r => r.id !== AI_PLAYER_ID);
  const aiRow = rows.find(r => r.id === AI_PLAYER_ID) ?? null;
  const hasAnyScore = humanRows.some(r => r.score > 0);
  const totalFinished = Object.keys(actuals).length;

  return (
    <div className="bg-canvas">
      {/* Hero */}
      <section className="container-app pt-8 md:pt-12 pb-6">
        <div className="flex flex-col md:flex-row md:items-end gap-6 md:justify-between">
          <div>
            <span className="chip mb-3"><TrendingUp size={12} /> {t("leaderboard.chip")}</span>
            <h1 className="font-display text-4xl md:text-6xl font-bold leading-tight">
              <span className="grad-text">{t("leaderboard.title.a")}</span><br />{t("leaderboard.title.b")}
            </h1>
            <p className="mt-3 text-[var(--ink-soft)] max-w-xl">
              {totalFinished === 0
                ? t("leaderboard.subtitle.pre")
                : `${totalFinished} ${t("leaderboard.subtitle.live.suffix")}`}
            </p>
          </div>
          <button onClick={loadEspnActuals} disabled={refreshing} className="btn btn-ghost">
            <RefreshCw size={14} className={refreshing ? "animate-spin" : ""} /> {t("leaderboard.recalc")}
          </button>
        </div>
      </section>

      {/* Podium — human players only, AI excluded from competition */}
      {humanRows.length >= 3 && hasAnyScore && (
        <section className="container-app pb-8">
          <Podium first={humanRows[0]} second={humanRows[1]} third={humanRows[2]} pot={POT_TOTAL_MXN} />
        </section>
      )}

      {/* Pre-tournament state — only show after data is loaded */}
      {!hasAnyScore && serverPicksLoaded && (
        <section className="container-app pb-8">
          <div className="glass-strong rounded-3xl p-6 md:p-8 grid md:grid-cols-[auto_1fr_auto] items-center gap-6">
            <div className="w-14 h-14 rounded-2xl grid place-items-center" style={{ background: "linear-gradient(135deg, #D4AF37, #FFE07A)" }}>
              <Trophy size={26} className="text-white" />
            </div>
            <div>
              <div className="font-display text-xl md:text-2xl font-bold leading-tight">{t("leaderboard.pot.title")} ${POT_TOTAL_MXN} MXN</div>
              <p className="text-sm text-[var(--ink-soft)] mt-1">{t("leaderboard.pot.copy")}</p>
            </div>
            <Link href="/quiniela" className="btn btn-primary w-full md:w-auto justify-center">
              <Target size={14} /> {t("leaderboard.fillCta")}
            </Link>
          </div>
        </section>
      )}

      {/* Full table */}
      <section className="container-app pb-20">
        <RankDeltaChip orderedIds={humanRows} currentPlayerId={currentPlayer?.id ?? null} />
        <div className="glass rounded-3xl overflow-hidden">
          <div className="px-5 py-4 flex items-center justify-between border-b border-[var(--line)]">
            <div className="font-display font-bold">{t("leaderboard.fullTable")}</div>
            <div className="text-xs text-[var(--ink-muted)]">{humanRows.length} {t("leaderboard.playersBolsa").replace("${pot}", String(POT_TOTAL_MXN))}</div>
          </div>
          <ul>
            {!serverPicksLoaded && (
              <>
                {Array.from({ length: 10 }).map((_, i) => (
                  <li key={i} className="flex items-center gap-3 px-4 py-3.5 border-b border-[var(--line)] last:border-b-0">
                    <div className="w-6 h-4 rounded bg-white/8 animate-pulse shrink-0" />
                    <div className="w-9 h-9 rounded-full bg-white/8 animate-pulse shrink-0" />
                    <div className="flex-1 space-y-1.5">
                      <div className="h-3 w-24 rounded bg-white/8 animate-pulse" />
                      <div className="h-2.5 w-16 rounded bg-white/6 animate-pulse" />
                    </div>
                    <div className="h-5 w-12 rounded-full bg-white/8 animate-pulse shrink-0" />
                  </li>
                ))}
              </>
            )}
            <AnimatePresence>
              {humanRows.map((r, idx) => {
                const champion = r.champion ? TEAMS.find(t => t.code === r.champion) : null;
                return (
                  <motion.li
                    key={r.id}
                    layout
                    transition={{ type: "spring", damping: 25, stiffness: 220 }}
                    className={`border-b border-[var(--line)] last:border-b-0 ${r.isMe ? "bg-[var(--bg-tint)]" : ""}`}
                  >
                  <Link
                    href={`/jugadores/${r.id}`}
                    className="flex items-center gap-3 md:gap-4 px-4 md:px-5 py-3.5 hover:bg-[var(--bg-tint)] transition-colors"
                  >
                    {/* Position */}
                    <div className="w-10 shrink-0 text-center">
                      {idx < 3 && hasAnyScore ? (
                        <div className={`w-8 h-8 mx-auto rounded-full grid place-items-center font-display font-bold ${
                          idx === 0 ? "bg-[#D4AF37] text-[#07090E]" :
                          idx === 1 ? "bg-[#94A3B8] text-[#07090E]" :
                          "bg-[#CD7F32] text-white"
                        }`}>
                          {idx + 1}
                        </div>
                      ) : (
                        <div className="font-display font-bold text-lg text-[var(--ink-muted)]">{idx + 1}</div>
                      )}
                    </div>

                    {/* Player */}
                    <CharalProfileTrigger player={r}>
                      <PlayerAvatar player={r} size={40} rounded="rounded-xl" textClass="text-xl" tint={0.12} />
                    </CharalProfileTrigger>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 flex-wrap">
                        <div className="font-display font-bold truncate">{r.name}</div>
                        {r.isMe && <span className="text-[9px] font-bold px-1.5 py-0.5 rounded-full bg-[var(--ink)] text-white">{t("leaderboard.you")}</span>}
                        {r.hotStreak && r.hotStreak >= 2 && (
                          <span
                            className="inline-flex items-center gap-1 text-[10px] font-bold px-1.5 py-0.5 rounded-full bg-gradient-to-r from-[#FB923C] to-[#EF4444] text-white"
                            title={`${r.hotStreak} ${t("hotStreak.suffix")}`}
                          >
                            <span aria-hidden>🔥</span>
                            <span className="tabular-nums">{r.hotStreak}</span>
                            <span className="hidden sm:inline normal-case">{t("hotStreak.suffix")}</span>
                          </span>
                        )}
                      </div>
                      <div className="flex items-center gap-2 text-[11px] text-[var(--ink-muted)] mt-0.5 flex-wrap">
                        <span>{r.pct}% {t("leaderboard.ready")}</span>
                        {(r.signHits > 0 || r.exactHits > 0 || r.bracketHits > 0) && (
                          <>
                            <span>·</span>
                            <span className="tabular-nums">
                              <strong className="text-[var(--ink)]">{r.signHits + r.exactHits + r.bracketHits}</strong> {t("leaderboard.hits")}
                              {r.bracketHits > 0 && (
                                <> · <strong className="text-[var(--ink)]">{r.bracketHits}</strong> KO</>
                              )}
                            </span>
                          </>
                        )}
                        {champion && (
                          <>
                            <span>·</span>
                            <span className="flex items-center gap-1">
                              <Crown size={10} className="text-[#D4AF37]" />
                              {t("leaderboard.champion")} <strong className="text-[var(--ink)]">{champion.code}</strong>
                            </span>
                          </>
                        )}
                      </div>
                    </div>

                    {/* Champion badge (md+) */}
                    {champion && (
                      <div className="hidden md:block relative w-8 h-8 rounded-lg overflow-hidden ring-1 ring-[var(--line)] shrink-0">
                        <Image src={flagUrl(champion.iso2, 48)} alt={champion.name} fill sizes="32px" className="object-cover" unoptimized />
                      </div>
                    )}

                    {/* Score */}
                    <div className="text-right shrink-0">
                      <div className="font-display text-2xl md:text-3xl font-bold tabular-nums leading-none" style={{ color: r.score > 0 ? r.accent : "var(--ink-muted)" }}>
                        {r.score}
                      </div>
                      <div className="text-[10px] uppercase tracking-wider text-[var(--ink-muted)] mt-1">{t("leaderboard.pts")}</div>
                    </div>
                  </Link>
                  </motion.li>
                );
              })}
            </AnimatePresence>
          </ul>
        </div>

        {/* AI benchmark — outside the competition, shown below the main table */}
        {aiRow && (
          <div className="mt-4">
            <div className="flex items-center gap-3 mb-2">
              <div className="h-px flex-1 border-t border-dashed border-[var(--line-strong)]" />
              <span className="text-[10px] uppercase tracking-[0.2em] font-bold text-[var(--ink-muted)] flex items-center gap-1.5">
                🤖 Benchmark IA · fuera de concurso
              </span>
              <div className="h-px flex-1 border-t border-dashed border-[var(--line-strong)]" />
            </div>
            <div className="glass rounded-2xl overflow-hidden opacity-75">
              <Link
                href={`/jugadores/${aiRow.id}`}
                className="flex items-center gap-3 md:gap-4 px-4 md:px-5 py-3.5 hover:bg-[var(--bg-tint)] transition-colors"
              >
                <div className="w-10 shrink-0 text-center">
                  <span className="text-xl">🤖</span>
                </div>
                <CharalProfileTrigger player={aiRow}>
                  <PlayerAvatar player={aiRow} size={40} rounded="rounded-xl" textClass="text-xl" tint={0.12} />
                </CharalProfileTrigger>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <div className="font-display font-bold truncate">{aiRow.name}</div>
                    <span className="text-[9px] font-bold px-1.5 py-0.5 rounded-full bg-[var(--bg-tint)] text-[var(--ink-muted)] border border-[var(--line)]">
                      referencia
                    </span>
                  </div>
                  <div className="flex items-center gap-2 text-[11px] text-[var(--ink-muted)] mt-0.5 flex-wrap">
                    <span>{aiRow.pct}% {t("leaderboard.ready")}</span>
                    {(aiRow.signHits > 0 || aiRow.exactHits > 0 || aiRow.bracketHits > 0) && (
                      <>
                        <span>·</span>
                        <span className="tabular-nums">
                          <strong className="text-[var(--ink)]">{aiRow.signHits + aiRow.exactHits + aiRow.bracketHits}</strong> {t("leaderboard.hits")}
                          {aiRow.bracketHits > 0 && (
                            <> · <strong className="text-[var(--ink)]">{aiRow.bracketHits}</strong> KO</>
                          )}
                        </span>
                      </>
                    )}
                    {aiRow.champion && (() => {
                      const champ = TEAMS.find(t => t.code === aiRow.champion);
                      return champ ? (
                        <>
                          <span>·</span>
                          <span className="flex items-center gap-1">
                            <Crown size={10} className="text-[#D4AF37]" />
                            {t("leaderboard.champion")} <strong className="text-[var(--ink)]">{champ.code}</strong>
                          </span>
                        </>
                      ) : null;
                    })()}
                  </div>
                </div>
                <div className="text-right shrink-0">
                  <div className="font-display text-2xl md:text-3xl font-bold tabular-nums leading-none text-[var(--ink-muted)]">
                    {aiRow.score}
                  </div>
                  <div className="text-[10px] uppercase tracking-wider text-[var(--ink-muted)] mt-1">{t("leaderboard.pts")}</div>
                </div>
              </Link>
            </div>
          </div>
        )}

        {/* Tiebreaker explanation */}
        <div className="glass rounded-2xl px-4 py-3 mt-4 text-[11px] text-[var(--ink-soft)] leading-relaxed">
          <strong className="text-[var(--ink)]">{t("leaderboard.tiebreak.title")}</strong>{" "}
          {t("leaderboard.tiebreak.copy")}{" "}
          <span className="text-[var(--ink-muted)]">{t("leaderboard.tiebreak.koNote")}</span>
        </div>
        {/* Last sync */}
        {lastSync > 0 && (
          <p className="text-center text-xs text-[var(--ink-muted)] mt-4">
            {t("leaderboard.lastSync")} {new Date(lastSync).toLocaleTimeString(intlLocale(locale))}
          </p>
        )}
      </section>
    </div>
  );
}

function Podium({ first, second, third, pot }: { first: Row; second: Row; third: Row; pot: number }) {
  return (
    <div className="glass-strong rounded-[36px] p-6 md:p-8 relative overflow-hidden">
      {/* Confetti glow */}
      <div className="absolute -top-20 -left-10 w-72 h-72 rounded-full blur-3xl opacity-30" style={{ background: "radial-gradient(closest-side, #D4AF37, transparent)" }} />
      <div className="absolute -top-16 -right-10 w-72 h-72 rounded-full blur-3xl opacity-20" style={{ background: "radial-gradient(closest-side, #5E5BFF, transparent)" }} />

      <div className="relative grid grid-cols-3 gap-4 items-end">
        <PodiumSpot row={second} place={2} height="h-32 md:h-40" />
        <PodiumSpot row={first} place={1} height="h-44 md:h-56" pot={pot} />
        <PodiumSpot row={third} place={3} height="h-24 md:h-32" />
      </div>
    </div>
  );
}

function PodiumSpot({ row, place, height, pot }: { row: Row; place: number; height: string; pot?: number }) {
  const color = place === 1 ? "#D4AF37" : place === 2 ? "#C0C0C0" : "#CD7F32";
  const icon = place === 1 ? <Crown size={20} /> : <Medal size={18} />;
  const { t } = useLocale();

  return (
    <div className="flex flex-col items-center text-center">
      <motion.div
        initial={{ scale: 0.8, opacity: 0 }} animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.4, delay: place === 1 ? 0.1 : 0.25 }}
        className="mb-3 flex flex-col items-center"
      >
        <CharalProfileTrigger player={row}>
          <PlayerAvatar player={row} size={64} rounded="rounded-2xl" textClass="text-3xl md:text-4xl" tint={0.15} className="mb-1" />
        </CharalProfileTrigger>
        <div className="font-display font-bold leading-tight">{row.name}</div>
        {row.isMe && <span className="text-[9px] font-bold px-1.5 py-0.5 rounded-full bg-[var(--ink)] text-white">{t("leaderboard.you")}</span>}
      </motion.div>

      <motion.div
        initial={{ height: 0, opacity: 0 }} animate={{ height: "100%", opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.2 }}
        className={`${height} w-full rounded-t-2xl flex flex-col items-center justify-start pt-3 relative overflow-hidden`}
        style={{ background: `linear-gradient(180deg, ${color}, ${color}CC)`, color: "white" }}
      >
        <div className="absolute inset-0 opacity-20 shimmer" />
        <div className="relative">{icon}</div>
        <div className="relative font-display font-bold text-2xl md:text-3xl tabular-nums mt-1">{row.score}</div>
        <div className="relative text-[10px] uppercase tracking-wider opacity-80">{t("leaderboard.pts")}</div>
        {place === 1 && pot && (
          <div className="relative mt-auto mb-3 px-2.5 py-1 rounded-full bg-white/20 text-[11px] font-semibold flex items-center gap-1">
            <Coins size={11} /> ${pot} MXN
          </div>
        )}
      </motion.div>
    </div>
  );
}
