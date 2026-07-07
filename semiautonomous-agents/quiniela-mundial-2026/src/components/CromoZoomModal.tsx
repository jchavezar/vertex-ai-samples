"use client";

// Cromo modal: big-image lightbox + per-player Ava roast + verdicts table +
// download button. Mounted from /album. The album page is responsible for the
// finals map (via useLiveScoreboard) so we don't double-subscribe to ESPN.
//
// Cache discipline (owner is allergic to Ava lag): on open, check
// getCachedRoast SYNCHRONOUSLY. If hit -> render immediately, never fetch.
// Only call loadRoast on a miss.

import { useEffect, useMemo, useState } from "react";
import { createPortal } from "react-dom";
import Image from "next/image";
import Link from "next/link";
import { ChevronRight, Download, Loader2, Sparkles, Trophy, X } from "lucide-react";
import { AI_PLAYER_ID, PLAYERS } from "@/data/players";
import { TEAMS, flagUrl } from "@/data/teams";
import { PlayerAvatar } from "@/components/PlayerAvatar";
import { getCachedRoast, loadRoast, type FinalsMap, type RoastPayload } from "@/lib/roast-cache";
import { verdictStyles, verdictLabelKey } from "@/lib/verdict-style";
import { intlLocale, useLocale, type Locale } from "@/lib/i18n";

export type CromoZoomTarget = {
  playerId: string;
  cromoUrl: string;
  date: string;
  theme: { label: string; accent: string };
};

type Props = {
  target: CromoZoomTarget | null;
  finals: FinalsMap;
  finalsLoading: boolean;
  onClose: () => void;
};

function formatDateLong(dateStr: string, locale: Locale): string {
  const [y, m, d] = dateStr.split("-").map(n => parseInt(n, 10));
  const date = new Date(Date.UTC(y, m - 1, d));
  const intl = intlLocale(locale);
  const weekday = new Intl.DateTimeFormat(intl, { weekday: "long", timeZone: "UTC" }).format(date);
  const day = new Intl.DateTimeFormat(intl, { day: "numeric", timeZone: "UTC" }).format(date);
  const month = new Intl.DateTimeFormat(intl, { month: "long", timeZone: "UTC" }).format(date);
  return `${weekday.charAt(0).toUpperCase()}${weekday.slice(1)} · ${day} ${month}`;
}

// Pull `.png` / `.jpg` from the GCS URL so the downloaded file gets the right
// extension. Strip query string + path noise first.
function extFromUrl(url: string): string {
  try {
    const u = new URL(url);
    const m = u.pathname.match(/\.([a-zA-Z0-9]{2,4})$/);
    if (m) return m[1].toLowerCase();
  } catch { /* relative URL or otherwise non-parseable */ }
  const m2 = url.split("?")[0].match(/\.([a-zA-Z0-9]{2,4})$/);
  return m2 ? m2[1].toLowerCase() : "png";
}

async function downloadCromo(url: string, filename: string) {
  // Try blob download (works when GCS sends permissive CORS — which it does
  // for public objects). Fall back to a direct anchor so the user at least
  // sees the image open in a new tab.
  try {
    const r = await fetch(url, { mode: "cors" });
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    const blob = await r.blob();
    const objUrl = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = objUrl;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
    setTimeout(() => URL.revokeObjectURL(objUrl), 1000);
  } catch {
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    a.target = "_blank";
    a.rel = "noopener";
    document.body.appendChild(a);
    a.click();
    a.remove();
  }
}

export function CromoZoomModal({ target, finals, finalsLoading, onClose }: Props) {
  const [mounted, setMounted] = useState(false);
  const [roast, setRoast] = useState<RoastPayload | null>(null);
  const [roastError, setRoastError] = useState<string | null>(null);
  const [roastLoading, setRoastLoading] = useState(false);
  const [downloading, setDownloading] = useState(false);
  const { t, locale } = useLocale();

  useEffect(() => { setMounted(true); }, []);

  // Esc to close + body scroll lock while open.
  useEffect(() => {
    if (!target) return;
    const onKey = (e: KeyboardEvent) => { if (e.key === "Escape") onClose(); };
    document.addEventListener("keydown", onKey);
    const prev = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => {
      document.removeEventListener("keydown", onKey);
      document.body.style.overflow = prev;
    };
  }, [target, onClose]);

  const playerId = target?.playerId ?? "";
  const isAi = playerId === AI_PLAYER_ID;
  const player = useMemo(() => PLAYERS.find(p => p.id === playerId), [playerId]);

  // Roast loader — cache-first. Reset state whenever the target player changes
  // so reopening on a different cromo doesn't flash the previous player's text.
  useEffect(() => {
    if (!target) return;
    // Don't kick off anything until we have a finals snapshot — the cache key
    // depends on the finals hash, so calling with `{}` would burn a model call
    // and write a roast under a stale key.
    if (finalsLoading) return;

    setRoast(null);
    setRoastError(null);

    const cached = getCachedRoast(target.playerId, finals);
    if (cached) {
      setRoast(cached);
      setRoastLoading(false);
      return;
    }

    let cancelled = false;
    setRoastLoading(true);
    loadRoast(target.playerId, finals)
      .then(j => {
        if (cancelled) return;
        if (j) { setRoast(j); setRoastError(null); }
        else setRoastError("No se pudo generar el análisis");
      })
      .finally(() => { if (!cancelled) setRoastLoading(false); });
    return () => { cancelled = true; };
  // finals is referentially stable per hash from useLiveScoreboard's useMemo;
  // including it directly is correct.
  }, [target, finals, finalsLoading]);

  if (!mounted || !target || typeof document === "undefined") return null;

  const playerName = player?.name ?? target.playerId;
  const ext = extFromUrl(target.cromoUrl);
  const filename = `cromo-${target.playerId}-${target.date}.${ext}`;

  const onDownload = async () => {
    if (downloading) return;
    setDownloading(true);
    try {
      await downloadCromo(target.cromoUrl, filename);
    } finally {
      setDownloading(false);
    }
  };

  return createPortal(
    <div
      className="fixed inset-0 z-[1000] bg-black/85 backdrop-blur-sm overflow-y-auto"
      onClick={onClose}
      role="dialog"
      aria-modal="true"
      aria-label={`Cromo de ${playerName}`}
    >
      <button
        type="button"
        onClick={onClose}
        aria-label={t("cromo.close")}
        className="fixed top-4 right-4 z-[1001] w-11 h-11 rounded-full bg-white/15 backdrop-blur text-white grid place-items-center hover:bg-white/25"
      >
        <X size={18} />
      </button>

      <div
        className="min-h-full w-full grid place-items-start md:place-items-center p-3 md:p-6"
        onClick={onClose}
      >
        <div
          className="w-full max-w-5xl grid grid-cols-1 md:grid-cols-[minmax(0,1fr)_minmax(0,1fr)] gap-4 md:gap-6"
          onClick={e => e.stopPropagation()}
        >
          {/* Cromo column */}
          <div className="flex flex-col items-center">
            <div className="text-center mb-3 px-2">
              <div className="text-[10px] uppercase tracking-[0.2em] text-white/70 font-bold">
                {formatDateLong(target.date, locale)}
              </div>
              <div className="font-display text-xl md:text-2xl font-black text-white mt-1">
                {target.theme.label}
              </div>
              <div className="text-sm text-white/80 mt-1">{playerName}</div>
            </div>
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={target.cromoUrl}
              alt={`Cromo ${playerName} ${target.date}`}
              className="w-full max-w-md rounded-2xl shadow-2xl ring-4 ring-white/10"
              style={{ boxShadow: `0 24px 48px -12px ${target.theme.accent}aa` }}
            />
            <button
              type="button"
              onClick={onDownload}
              disabled={downloading}
              className="mt-4 inline-flex items-center gap-2 px-4 py-2.5 rounded-full bg-white text-[var(--ink)] text-sm font-bold shadow-lg hover:scale-[1.02] active:scale-95 transition-transform disabled:opacity-60"
            >
              {downloading ? <Loader2 size={14} className="animate-spin" /> : <Download size={14} />}
              {downloading ? t("cromo.downloading") : t("cromo.download")}
            </button>
          </div>

          {/* Sidebar: player meta + Ava + verdicts */}
          <div className="flex flex-col gap-3 md:max-h-[calc(100vh-3rem)] md:overflow-y-auto pb-6 md:pb-0 md:pr-1">
            {/* Player card */}
            <div className="glass-strong rounded-2xl p-4 relative overflow-hidden">
              <div className="absolute -top-12 -right-12 w-40 h-40 rounded-full blur-3xl opacity-25 pointer-events-none"
                style={{ background: `radial-gradient(closest-side, ${player?.accent ?? target.theme.accent}, transparent)` }} />
              <div className="relative flex items-center gap-3">
                {player && (
                  <PlayerAvatar player={player} size={48} rounded="rounded-xl" tint={0.18} textClass="text-xl" />
                )}
                <div className="min-w-0 flex-1">
                  <Link
                    href={`/jugadores/${target.playerId}`}
                    className="font-display text-lg md:text-xl font-black truncate text-[var(--ink)] hover:underline"
                  >
                    {playerName}
                  </Link>
                  {roast && (
                    <div className="flex items-center gap-2 mt-0.5 flex-wrap text-[11px] text-[var(--ink-soft)]">
                      <span><strong className="text-[var(--ink)] tabular-nums">{roast.score}</strong> {t("profile.pts")}</span>
                      <span>·</span>
                      <span><strong className="text-[var(--ink)] tabular-nums">{roast.signHits + roast.exactHits}</strong> {t("profile.hits")}</span>
                      {roast.exactHits > 0 && <>
                        <span>·</span>
                        <span><strong className="text-[var(--ink)] tabular-nums">{roast.exactHits}</strong> {t("profile.exact")}</span>
                      </>}
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Ava */}
            <div className="glass rounded-2xl p-4 relative overflow-hidden"
              style={{ border: "1px solid color-mix(in srgb, var(--accent-violet) 28%, transparent)" }}>
              <div className="flex items-center gap-2 mb-2">
                <Sparkles size={13} style={{ color: "var(--accent-violet)" }} />
                <span className="text-[10px] uppercase tracking-[0.2em] font-bold" style={{ color: "var(--accent-violet)" }}>
                  {t("profile.ava.label")}
                </span>
                {roast && roastLoading && (
                  <Loader2 size={11} className="animate-spin text-[var(--ink-muted)]" aria-label="actualizando" />
                )}
              </div>
              {!roast && !roastError && (roastLoading || finalsLoading) && (
                <div className="flex items-center gap-2 text-sm text-[var(--ink-muted)]">
                  <Loader2 size={14} className="animate-spin" /> {t("profile.ava.loading")}
                </div>
              )}
              {roastError && !roast && (
                <div className="text-sm text-red-600">{t("profile.ava.error")} {roastError}</div>
              )}
              {roast && (
                <p className="text-[var(--ink)] text-sm md:text-base leading-relaxed font-medium whitespace-pre-line">
                  {roast.roast}
                </p>
              )}
            </div>

            {/* Verdicts table — hidden for AI bot (no human picks) */}
            {!isAi && (
              <div className="glass rounded-2xl p-4">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <Trophy size={13} className="text-[var(--ink-muted)]" />
                    <span className="font-display font-bold text-sm">{t("profile.table.title")}</span>
                  </div>
                  {roast && (
                    <span className="text-[10px] uppercase tracking-wider text-[var(--ink-muted)] tabular-nums">
                      {roast.verdicts.length} {t("profile.table.short")}
                    </span>
                  )}
                </div>
                {!roast && (roastLoading || finalsLoading) && (
                  <div className="text-sm text-[var(--ink-muted)]">{t("profile.table.loading")}</div>
                )}
                {roast && roast.verdicts.length === 0 && (
                  <div className="text-sm text-[var(--ink-muted)] italic">{t("profile.table.empty")}</div>
                )}
                {roast && roast.verdicts.length > 0 && (
                  <div className="divide-y divide-[var(--line)] -mx-1">
                    {roast.verdicts.map(r => {
                      const homeTeam = TEAMS.find(t => t.code === r.home);
                      const awayTeam = TEAMS.find(t => t.code === r.away);
                      const v = verdictStyles(r.verdict);
                      const verdictLabel = r.verdict === "exact" ? `★ ${t(verdictLabelKey(r.verdict))}` : t(verdictLabelKey(r.verdict));
                      return (
                        <Link
                          key={r.fixtureId}
                          href={`/partido/${r.fixtureId}`}
                          className="flex items-center gap-2 px-1 py-2 hover:bg-[var(--bg-tint)] transition-colors rounded-lg"
                        >
                          <span className="w-11 shrink-0 text-[10px] uppercase tracking-wider text-[var(--ink-muted)] tabular-nums">
                            {r.date.slice(5)}
                          </span>
                          <div className="flex items-center gap-1.5 min-w-0 flex-1">
                            {homeTeam && <Image src={flagUrl(homeTeam.iso2, 32)} alt="" width={14} height={14} className="rounded-sm shrink-0 object-cover" unoptimized />}
                            <span className="font-display font-bold text-xs">{r.home}</span>
                            <span className="text-[var(--ink-muted)] mx-0.5 tabular-nums font-bold text-xs">{r.actualScore}</span>
                            <span className="font-display font-bold text-xs">{r.away}</span>
                            {awayTeam && <Image src={flagUrl(awayTeam.iso2, 32)} alt="" width={14} height={14} className="rounded-sm shrink-0 object-cover" unoptimized />}
                          </div>
                          <div className="flex flex-col items-end gap-0.5 shrink-0">
                            <span className="px-1.5 py-0.5 rounded-md text-[9px] font-extrabold uppercase tracking-wider leading-none"
                              style={{ background: v.bg, color: v.fg }}>
                              {verdictLabel}
                            </span>
                            <span className="text-[9px] uppercase tracking-wider text-[var(--ink-muted)] tabular-nums leading-none">
                              {r.myPick ? `${r.myPick === "H" ? r.home : r.myPick === "A" ? r.away : "X"}${r.myScore ? ` (${r.myScore})` : ""}` : "—"} · +{r.pts}
                            </span>
                          </div>
                          <ChevronRight size={12} className="text-[var(--ink-muted)] shrink-0" />
                        </Link>
                      );
                    })}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>,
    document.body,
  );
}
