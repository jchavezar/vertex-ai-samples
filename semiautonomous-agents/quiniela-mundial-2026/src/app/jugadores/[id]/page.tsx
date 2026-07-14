"use client";

// Per-charal profile: Ava's toxic roast + a clean hit/miss table. Public read —
// any compa can pull up anyone else's. Server does the model call and the
// per-fixture verdict computation; the page is thin and fast.

import { use, useEffect, useState } from "react";
import Link from "next/link";
import Image from "next/image";
import { Sparkles, Trophy, Loader2, ArrowLeft, ChevronRight } from "lucide-react";
import { PLAYERS, AI_PLAYER_ID } from "@/data/players";
import { TEAMS, flagUrl } from "@/data/teams";
import { PlayerAvatar } from "@/components/PlayerAvatar";
import { useLiveScoreboard } from "@/lib/live-scoreboard";
import { notFound } from "next/navigation";
import { getCachedRoast, loadRoast, type FinalsMap, type KoResultsMap, type RoastPayload, type RoastRow } from "@/lib/roast-cache";
import { verdictStyles, verdictLabelKey } from "@/lib/verdict-style";
import { useLocale } from "@/lib/i18n";

type Payload = RoastPayload;

export default function PlayerProfilePage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const player = PLAYERS.find(p => p.id === id);
  if (!player) notFound();

  const [data, setData] = useState<Payload | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);
  const [koMap, setKoMap] = useState<KoResultsMap>({});
  const { finals, loading: finalsLoading } = useLiveScoreboard();
  const { t } = useLocale();

  // Fetch KO results once for cache key + display
  useEffect(() => {
    fetch("/api/bracket/ko-results", { cache: "no-store" })
      .then(r => r.json())
      .then((j: { ok: boolean; slotResults?: KoResultsMap }) => {
        if (j.ok && j.slotResults) setKoMap(j.slotResults);
      })
      .catch(() => {});
  }, []);

  useEffect(() => {
    if (finalsLoading) return;
    let cancelled = false;
    const finalsMap: FinalsMap = {};
    for (const [k, v] of Object.entries(finals)) {
      finalsMap[k] = { homeGoals: v.homeGoals, awayGoals: v.awayGoals };
    }
    const cached = getCachedRoast(id, finalsMap, koMap);
    if (cached) {
      setData(cached);
      setError(null);
      setRefreshing(false);
      return () => { cancelled = true; };
    }
    setRefreshing(true);
    loadRoast(id, finalsMap, koMap)
      .then(j => {
        if (cancelled) return;
        if (j) { setData(j); setError(null); }
        else setError(t("profile.ava.errorShort"));
      })
      .finally(() => { if (!cancelled) setRefreshing(false); });
    return () => { cancelled = true; };
  }, [id, finalsLoading, finals, koMap, t]);

  const isAi = id === AI_PLAYER_ID;

  return (
    <main className="min-h-screen bg-[var(--bg)] pb-16">
      <section className="max-w-3xl mx-auto px-4 pt-5">
        <Link href="/leaderboard" className="inline-flex items-center gap-1.5 text-xs text-[var(--ink-soft)] hover:text-[var(--ink)] mb-4">
          <ArrowLeft size={14} /> {t("profile.back")}
        </Link>

        {/* Header */}
        <div className="glass-strong rounded-3xl p-5 md:p-6 relative overflow-hidden">
          <div className="absolute -top-12 -right-12 w-60 h-60 rounded-full blur-3xl opacity-20 pointer-events-none"
            style={{ background: `radial-gradient(closest-side, ${player!.accent}, transparent)` }} />
          <div className="relative flex items-start gap-4">
            <PlayerAvatar player={player!} size={64} rounded="rounded-2xl" tint={0.18} textClass="text-2xl" />
            <div className="min-w-0 flex-1">
              <div className="text-[10px] uppercase tracking-[0.25em] text-[var(--ink-muted)] font-bold">
                {t("profile.kicker")}
              </div>
              <h1 className="font-display text-2xl md:text-3xl font-black truncate">{player!.name}</h1>
              {data && (
                <div className="flex items-center gap-3 mt-2 flex-wrap text-xs text-[var(--ink-soft)]">
                  <span><strong className="text-[var(--ink)] tabular-nums">{data.score}</strong> {t("profile.pts")}</span>
                  <span>·</span>
                  <span><strong className="text-[var(--ink)] tabular-nums">{data.signHits + data.exactHits}</strong> {t("profile.hits")}</span>
                  {data.exactHits > 0 && <>
                    <span>·</span>
                    <span><strong className="text-[var(--ink)] tabular-nums">{data.exactHits}</strong> {t("profile.exact")}</span>
                  </>}
                  {(data.bracketHits ?? 0) > 0 && <>
                    <span>·</span>
                    <span><strong className="text-[var(--ink)] tabular-nums">{data.bracketHits}</strong> KO</span>
                  </>}
                  {data.streak > 0 && <>
                    <span>·</span>
                    <span>{t("profile.streakMax")} <strong className="text-[var(--ink)] tabular-nums">{data.streak}</strong></span>
                  </>}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Ava's roast */}
        <div className="glass rounded-3xl p-5 mt-4 relative overflow-hidden"
          style={{ border: "1px solid color-mix(in srgb, var(--accent-violet) 28%, transparent)" }}>
          <div className="flex items-center gap-2 mb-3">
            <Sparkles size={14} style={{ color: "var(--accent-violet)" }} />
            <span className="text-[10px] uppercase tracking-[0.2em] font-bold" style={{ color: "var(--accent-violet)" }}>
              {t("profile.ava.label")}
            </span>
            {data && refreshing && (
              <Loader2 size={11} className="animate-spin text-[var(--ink-muted)]" aria-label="actualizando" />
            )}
          </div>
          {!data && !error && (
            <div className="flex items-center gap-2 text-sm text-[var(--ink-muted)]">
              <Loader2 size={14} className="animate-spin" /> {t("profile.ava.loading")}
            </div>
          )}
          {error && (
            <div className="text-sm text-red-600">{t("profile.ava.error")} {error}</div>
          )}
          {data && (
            <p className="text-[var(--ink)] text-base md:text-lg leading-relaxed font-medium whitespace-pre-line">
              {data.roast}
            </p>
          )}
        </div>

        {/* Hits/misses table */}
        {!isAi && (
          <div className="glass rounded-3xl p-5 mt-4 overflow-hidden">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <Trophy size={14} className="text-[var(--ink-muted)]" />
                <span className="font-display font-bold text-sm">{t("profile.table.title")}</span>
              </div>
              {data && (
                <span className="text-[10px] uppercase tracking-wider text-[var(--ink-muted)] tabular-nums">
                  {data.verdicts.length} {t("profile.table.count")}
                </span>
              )}
            </div>
            {!data && (
              <div className="text-sm text-[var(--ink-muted)]">{t("profile.table.loading")}</div>
            )}
            {data && data.verdicts.length === 0 && (
              <div className="text-sm text-[var(--ink-muted)] italic">{t("profile.table.empty")}</div>
            )}
            {data && data.verdicts.length > 0 && (
              <div className="divide-y divide-[var(--line)] -mx-2">
                {(() => {
                  let lastIsKO = false;
                  return data.verdicts.map((r: RoastRow) => {
                    const isKO = !!r.round;
                    const showKOHeader = isKO && !lastIsKO;
                    lastIsKO = isKO;

                    const homeTeam = TEAMS.find(t => t.code === r.home);
                    const awayTeam = TEAMS.find(t => t.code === r.away);
                    const v = verdictStyles(r.verdict);
                    const verdictLabel = r.verdict === "exact" ? `★ ${t(verdictLabelKey(r.verdict))}` : t(verdictLabelKey(r.verdict));

                    // Display label for what the player picked
                    const myPickDisplay = !r.myPick ? "—"
                      : isKO ? r.myPick
                      : r.myPick === "H" ? r.home : r.myPick === "A" ? r.away : "X";

                    const rowContent = (
                      <>
                        {/* Date + round badge */}
                        <div className="flex flex-col items-start shrink-0 w-14">
                          <span className="text-[10px] uppercase tracking-wider text-[var(--ink-muted)] tabular-nums">
                            {r.date.slice(5)}
                          </span>
                          {isKO ? (
                            <span className="mt-0.5 px-1 py-px rounded text-[8px] font-extrabold uppercase tracking-wider leading-none"
                              style={{ background: "rgba(234,179,8,0.18)", color: "rgb(161,120,0)" }}>
                              {r.round}
                            </span>
                          ) : r.group ? (
                            <span className="mt-0.5 px-1 py-px rounded text-[8px] font-extrabold uppercase tracking-wider leading-none"
                              style={{ background: "var(--bg-tint)", color: "var(--ink-muted)" }}>
                              {r.group}
                            </span>
                          ) : null}
                        </div>

                        {/* Teams */}
                        <div className="flex items-center gap-1.5 min-w-0 flex-1">
                          {homeTeam && <Image src={flagUrl(homeTeam.iso2, 32)} alt="" width={16} height={16} className="rounded-sm shrink-0 object-cover" unoptimized />}
                          <span className="font-display font-bold text-sm">{r.home}</span>
                          <span className="text-[var(--ink-muted)] mx-0.5 tabular-nums font-bold text-sm">{r.actualScore}</span>
                          <span className="font-display font-bold text-sm">{r.away}</span>
                          {awayTeam && <Image src={flagUrl(awayTeam.iso2, 32)} alt="" width={16} height={16} className="rounded-sm shrink-0 object-cover" unoptimized />}
                        </div>

                        {/* Verdict + pick */}
                        <div className="flex flex-col items-end gap-0.5 shrink-0">
                          <span className="px-1.5 py-0.5 rounded-md text-[9px] font-extrabold uppercase tracking-wider leading-none"
                            style={{ background: v.bg, color: v.fg }}>
                            {verdictLabel}
                          </span>
                          <span className={`text-[10px] uppercase tracking-wider tabular-nums leading-none ${
                            r.verdict === "miss"
                              ? "line-through decoration-red-500 decoration-2 text-red-400 font-bold opacity-85"
                              : "text-slate-300 font-medium"
                          }`}>
                            {myPickDisplay !== "—" ? `${t("profile.pick")} ${myPickDisplay}${r.myScore ? ` (${r.myScore})` : ""}` : "—"}
                          </span>
                        </div>

                        {/* Running total */}
                        <div className="flex flex-col items-end gap-0.5 shrink-0 min-w-[52px]">
                          <span className="font-display font-black text-[11px] tabular-nums"
                            style={{ color: r.pts > 0 ? "rgb(16,185,129)" : "var(--ink-muted)" }}>
                            {r.pts > 0 ? `+${r.pts}` : "+0"}
                          </span>
                          <span className="font-display font-black text-[13px] tabular-nums"
                            style={{ color: "var(--ink)" }}>
                            {r.runningTotal ?? 0}
                          </span>
                        </div>

                        <ChevronRight size={14} className="text-[var(--ink-muted)] shrink-0" />
                      </>
                    );

                    const rowCls = "flex items-center gap-2 px-2 py-2.5 hover:bg-[var(--bg-tint)] transition-colors rounded-xl";

                    return (
                      <div key={r.fixtureId}>
                        {showKOHeader && (
                          <div className="flex items-center gap-2 px-2 pt-3 pb-1">
                            <div className="h-px flex-1" style={{ background: "rgba(234,179,8,0.3)" }} />
                            <span className="text-[10px] font-extrabold uppercase tracking-[0.2em]"
                              style={{ color: "rgb(161,120,0)" }}>
                              Eliminatorias
                            </span>
                            <div className="h-px flex-1" style={{ background: "rgba(234,179,8,0.3)" }} />
                          </div>
                        )}
                        {isKO ? (
                          <Link href="/bracket" className={rowCls}>
                            {rowContent}
                          </Link>
                        ) : (
                          <Link href={`/partido/${r.fixtureId}`} className={rowCls}>
                            {rowContent}
                          </Link>
                        )}
                      </div>
                    );
                  });
                })()}
              </div>
            )}
          </div>
        )}
      </section>
    </main>
  );
}
