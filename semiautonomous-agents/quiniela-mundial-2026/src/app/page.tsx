"use client";

import Link from "next/link";
import Image from "next/image";
import dynamic from "next/dynamic";
import { motion } from "framer-motion";
import { useEffect, useMemo, useRef, useState } from "react";
import {
  ArrowUpRight, Sparkles, Target, Trophy, Users, Flame, MapPin, CalendarDays, Coins, Activity,
  Swords, Crown, Bot, Radio, BookImage, BarChart3, X,
} from "lucide-react";
import { HomeSnapshotProvider } from "@/lib/home-snapshot";
import { TOURNAMENT, SCORING } from "@/data/tournament";
import { POT_TOTAL_MXN, PER_PLAYER_MXN } from "@/data/players";
import { TEAMS, flagUrl } from "@/data/teams";
import { allGroupFixtures, type GroupFixture } from "@/data/groups";
import { fixtureKickoffMs, isFixtureLocked } from "@/lib/fixture-time";
import { getTournamentPhase } from "@/lib/tournament-phase";
import { ViewerKickoffTime, ViewerKickoffDate } from "@/components/ViewerKickoff";
import { usePlayer } from "@/lib/player-context";
import {
  loadAllPredictions, loadAllPredictionsFromServer, fillStats, loadPredictions, savePredictions, firePickToServer,
  computePlayerScoreDetail, actualPick, scoreGroupPrediction, type MatchResult, type PlayerPredictions, type Pick1X2,
} from "@/lib/predictions";
import { PlayerAvatar } from "@/components/PlayerAvatar";
import { useLiveScoreboard, type LiveFixture } from "@/lib/live-scoreboard";
import { useAllPicksByFixture, type PlayerLite } from "@/lib/all-picks";
import { CromoCard } from "@/components/CromoCard";
import { CromoZoomModal, type CromoZoomTarget } from "@/components/CromoZoomModal";
import { themeFor } from "@/lib/cromo-theme";
import { prefetchRoast, type FinalsMap } from "@/lib/roast-cache";
import { ActivityFeed } from "@/components/ActivityFeed";
import { CromoDeltaBanner } from "@/components/CromoDeltaBanner";
import { SelfBeatChip } from "@/components/SelfBeatChip";
import { PushActivationModal } from "@/components/PushActivationFlow";
import { AtinandoSheet } from "@/components/AtinandoSheet";
import { CharalDelDiaChip } from "@/components/CharalDelDiaChip";
import { TopScorersLeaderboard } from "@/components/TopScorersLeaderboard";
import { LateSaverBanner } from "@/components/LateSaverBanner";
import { DramaSpotlight } from "@/components/DramaSpotlight";
import { KOOpenBanner } from "@/components/KOOpenBanner";
import { EnvelopeChip } from "@/components/EnvelopeChip";
import { KnockoutSection } from "@/components/KnockoutSection";
import { BracketMiniLeaderboard } from "@/components/BracketMiniLeaderboard";
import { KOMatchFeed } from "@/components/KOMatchFeed";

// Below-the-fold components — defer JS bundle so first paint isn't blocked
// hydrating chips that don't matter until the user scrolls. ssr:false keeps
// the server payload smaller too.
const DailyRecapCard = dynamic(
  () => import("@/components/DailyRecapCard").then(m => ({ default: m.DailyRecapCard })),
  { ssr: false },
);
const CafeAmCard = dynamic(
  () => import("@/components/CafeAmCard").then(m => ({ default: m.CafeAmCard })),
  { ssr: false },
);
const AvaThinkingChip = dynamic(
  () => import("@/components/AvaThinkingChip").then(m => ({ default: m.AvaThinkingChip })),
  { ssr: false },
);
const GhostActivityFeed = dynamic(
  () => import("@/components/GhostActivityFeed").then(m => ({ default: m.GhostActivityFeed })),
  { ssr: false },
);
const PackOpening = dynamic(
  () => import("@/components/PackOpening").then(m => ({ default: m.PackOpening })),
  { ssr: false },
);
import { useLocale } from "@/lib/i18n";
import { computeCromo, isTierPromotion, readStoredTier, writeStoredTier, type Cromo } from "@/lib/cromos";
import { track } from "@/lib/track";
import { winProbabilities } from "@/data/team-ratings";

export default function HomePage() {
  // The provider is scoped to the home tree only — other routes that still
  // ship their own per-component fetches keep working unchanged.
  return (
    <HomeSnapshotProvider>
      <MundialHome />
    </HomeSnapshotProvider>
  );
}

function MundialHome() {
  const { currentPlayer, players } = usePlayer();
  const { t } = useLocale();

  const [allFill, setAllFill] = useState<{ id: string; pct: number; champion?: string }[]>([]);
  const [allMundialPicks, setAllMundialPicks] = useState<PlayerPredictions[]>([]);
  const { byId: liveById, finals } = useLiveScoreboard();
  const { byFixture: pickersByFx } = useAllPicksByFixture();

  useEffect(() => {
    const refresh = () => {
      const all = loadAllPredictions();
      setAllFill(all.map(p => {
        const s = fillStats(p);
        return { id: p.playerId, pct: s.percent, champion: s.champion };
      }));
    };
    const refreshFromServer = async () => {
      try {
        const all = await loadAllPredictionsFromServer();
        setAllMundialPicks(all);
        const local = loadAllPredictions();
        const merged = all.map(remote => {
          const loc = local.find(l => l.playerId === remote.playerId);
          const pick = (loc?.updatedAt ?? 0) > (remote.updatedAt ?? 0) ? loc! : remote;
          const s = fillStats(pick);
          return { id: pick.playerId, pct: s.percent, champion: s.champion };
        });
        setAllFill(merged);
      } catch {}
    };
    refresh();
    refreshFromServer();
    const onUpd = () => { refresh(); refreshFromServer(); };
    window.addEventListener("q26:predictions-updated", onUpd);
    return () => {
      window.removeEventListener("q26:predictions-updated", onUpd);
    };
  }, []);

  // Map RealResults → MatchResult (needs home/away codes from fixtures)
  const actuals = useMemo(() => {
    const map: Record<string, MatchResult> = {};
    const fxById = new Map(allGroupFixtures().map(fx => [fx.id, fx]));
    for (const [fxId, r] of Object.entries(finals)) {
      const fx = fxById.get(fxId);
      if (!fx) continue;
      map[fxId] = { home: fx.home, away: fx.away, homeGoals: r.homeGoals, awayGoals: r.awayGoals };
    }
    return map;
  }, [finals]);

  // Top scorers by computePlayerScoreDetail with finals-only actuals.
  // Bot players are excluded — AI competes as benchmark only, not in the pot.
  const punteros = useMemo(() => {
    if (allMundialPicks.length === 0) return [];
    return allMundialPicks
      .map(p => {
        const player = players.find(pp => pp.id === p.playerId);
        if (!player || player.isBot) return null;
        const detail = computePlayerScoreDetail(p, actuals);
        const stats = fillStats(p);
        return {
          id: player.id,
          name: player.name,
          emoji: player.emoji,
          accent: player.accent,
          photoDataUrl: player.photoDataUrl,
          score: detail.score,
          exactHits: detail.exactHits,
          signHits: detail.signHits,
          streak: detail.streak,
          pct: stats.percent,
        };
      })
      .filter((x): x is NonNullable<typeof x> => x !== null)
      .sort((a, b) =>
        b.score - a.score ||
        b.exactHits - a.exactHits ||
        b.signHits - a.signHits ||
        b.streak - a.streak ||
        a.name.localeCompare(b.name),
      );
  }, [allMundialPicks, players, actuals]);

  // Cromos FUT — uno por jugador, con tier dinámico según rating
  const cromos: { cromo: Cromo; player: typeof players[number] }[] = useMemo(() => {
    if (allMundialPicks.length === 0) return [];
    const local = loadAllPredictions();
    return players.map(player => {
      const remote = allMundialPicks.find(p => p.playerId === player.id);
      const loc = local.find(l => l.playerId === player.id);
      // Server wins always. Local was authoritative before but caused stale
      // picks to overwrite good Firestore data when localStorage timestamps
      // drifted. Server PUT is verified + retried (see scheduleRemoteSync),
      // so the canonical state always lives there.
      const pick = remote || loc;
      if (!pick) return null;
      return { cromo: computeCromo(pick, actuals, allMundialPicks), player };
    }).filter((x): x is { cromo: Cromo; player: typeof players[number] } => x !== null)
      .sort((a, b) => b.cromo.rating - a.cromo.rating);
  }, [allMundialPicks, players, actuals]);

  const myCromo = useMemo(
    () => (currentPlayer ? cromos.find(c => c.cromo.playerId === currentPlayer.id) : undefined),
    [cromos, currentPlayer],
  );

  // Pack opening al subir de tier.
  //
  // Defensive belt + braces: writeStoredTier locks the high-water mark so the
  // tier never visibly demotes. Additionally we session-guard the trigger so
  // even if a future bug oscillates the stored tier, this can only fire ONCE
  // per page lifetime — never the "confetti every 8 seconds" failure mode.
  const [packOpen, setPackOpen] = useState(false);
  const packFiredRef = useRef(false);
  useEffect(() => {
    if (!myCromo) return;
    if (packFiredRef.current) {
      // Still write so the high-water mark advances quietly.
      writeStoredTier(myCromo.cromo.playerId, myCromo.cromo.tier);
      return;
    }
    const prev = readStoredTier(myCromo.cromo.playerId);
    if (isTierPromotion(prev, myCromo.cromo.tier)) {
      packFiredRef.current = true;
      setPackOpen(true);
    }
    writeStoredTier(myCromo.cromo.playerId, myCromo.cromo.tier);
  }, [myCromo]);
  useEffect(() => {
    if (packOpen && myCromo) track("pack_opened", { tier: myCromo.cromo.tier });
  }, [packOpen, myCromo]);

  // Cromo zoom modal — click any cromo card on the home to open the same
  // full-size + Ava-analysis sidebar surface used in /album. Today's style
  // metadata is pulled from /api/cromos/album (cheap, also primes the SW).
  const [lightbox, setLightbox] = useState<CromoZoomTarget | null>(null);
  const [todayMeta, setTodayMeta] = useState<{ date: string; style: string | null; urlByPlayer: Map<string, string> } | null>(null);
  useEffect(() => {
    let cancelled = false;
    fetch("/api/cromos/album", { cache: "no-store" })
      .then(r => r.json())
      .then((j: { ok: boolean; today: string; days: Array<{ date: string; style: string | null; cromos: Array<{ playerId: string; url: string }> }> }) => {
        if (cancelled || !j?.ok) return;
        const today = j.days.find(d => d.date === j.today);
        const urlByPlayer = new Map<string, string>();
        for (const c of today?.cromos ?? []) urlByPlayer.set(c.playerId, c.url);
        setTodayMeta({ date: j.today, style: today?.style ?? null, urlByPlayer });
      })
      .catch(() => {});
    return () => { cancelled = true; };
  }, []);

  // Pre-warm Ava roasts for every charal with a cromo on screen as soon as
  // finals are ready. Click → instant render from localStorage cache (per
  // roast-cache.ts), no LLM spinner. Re-fires when actuals change because
  // the cache key hashes finals — a new marker invalidates the right entries
  // automatically and prefetch repopulates.
  useEffect(() => {
    if (cromos.length === 0) return;
    const finalsMap: FinalsMap = {};
    for (const [k, v] of Object.entries(actuals)) {
      finalsMap[k] = { homeGoals: v.homeGoals, awayGoals: v.awayGoals };
    }
    for (const { player } of cromos) prefetchRoast(player.id, finalsMap);
  }, [cromos, actuals]);

  const openCromoZoom = useMemo(
    () => (info: { portraitSrc: string | null; playerId: string }) => {
      if (!todayMeta) return;
      const url = info.portraitSrc ?? todayMeta.urlByPlayer.get(info.playerId);
      if (!url) return;
      const player = players.find(p => p.id === info.playerId);
      const theme = themeFor(todayMeta.style);
      setLightbox({
        cromoUrl: url,
        playerId: info.playerId,
        date: todayMeta.date,
        theme: { label: theme.label, accent: player?.accent ?? theme.accent },
      });
    },
    [todayMeta, players],
  );

  // Fire-and-forget bootstrap of the AI bot's picks. Throttled to once every
  // 10 min per device via localStorage so opening the home doesn't hammer the
  // ESPN scoreboard. The AI card sits at 0% / "Sin predicciones" until this
  // resolves, so the first visit auto-fills it.
  useEffect(() => {
    const KEY = "q26:last-ai-sync";
    const THROTTLE_MS = 10 * 60 * 1000;
    const last = Number(localStorage.getItem(KEY) ?? "0");
    if (Date.now() - last < THROTTLE_MS) return;
    localStorage.setItem(KEY, String(Date.now()));
    fetch("/api/ai/sync", { method: "POST" })
      .then(r => r.ok ? r.json() : null)
      .then(j => {
        if (j?.ok) window.dispatchEvent(new CustomEvent("q26:predictions-updated"));
      })
      .catch(() => {});
  }, []);

  return (
    <div className="bg-canvas">
      {/* HERO */}
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 bg-grid opacity-50 [mask-image:radial-gradient(ellipse_at_center,black,transparent_70%)]" />
        <div className="absolute -top-40 -left-32 w-[520px] h-[520px] rounded-full blob opacity-40"
             style={{ background: "radial-gradient(closest-side, rgba(94,91,255,0.35), transparent)" }} />
        <div className="absolute -top-32 right-0 w-[460px] h-[460px] rounded-full blob opacity-40"
             style={{ background: "radial-gradient(closest-side, rgba(20,241,149,0.30), transparent)", animationDelay: "-4s" }} />
        <div className="absolute top-60 left-1/3 w-[380px] h-[380px] rounded-full blob opacity-30"
             style={{ background: "radial-gradient(closest-side, rgba(255,59,130,0.30), transparent)", animationDelay: "-8s" }} />

        <div className="container-app pt-10 md:pt-16 pb-20 relative">
          <div className="flex flex-wrap items-center gap-2 mb-6">
            <CharalDelDiaChip />
            <EnvelopeChip />
            <span className="chip"><span className="live-dot" /> {t("home.chip.live")}</span>
            <span className="chip">🇲🇽 🇺🇸 🇨🇦 · {t("home.chip.hosts")}</span>
            <span className="chip">{t("home.chip.scope")}</span>
          </div>

          {/* Mobile: leaderboard above the hero — first thing you see. */}
          <div className="md:hidden -mx-4 mb-6">
            <TopScorersLeaderboard />
          </div>

          {/* Desktop hero grid — items-start (not items-center) so the left
              column can extend below the hero without forcing the spotlight
              stack to grow with it. Wider gap on xl for a real web-app feel. */}
          <div className="grid md:grid-cols-[1.2fr_1fr] xl:grid-cols-[1.3fr_1fr] gap-8 xl:gap-10 items-start">
            <div>
              <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: .5 }}
                className="font-display uppercase tracking-[0.28em] text-xs text-[var(--ink-muted)] mb-3">
                {t("home.hero.kicker")}
              </motion.div>
              {/* Compact wordmark — full-size CHARALES 2026 hero was eating
                  too much vertical real estate on desktop. Keeps the brand
                  visible without dominating the fold. */}
              <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: .6 }}
                className="font-display font-bold leading-none tracking-tight flex items-baseline gap-2">
                <span className="text-[clamp(24px,4vw,40px)]">CHARALES</span>
                <span className="text-[clamp(24px,4vw,40px)] grad-text">2026</span>
              </motion.div>

              <p className="mt-6 text-lg md:text-xl text-[var(--ink-soft)] max-w-xl leading-relaxed">
                {t("home.hero.subtitle.prefix")} <strong className="text-[var(--ink)]">{t("home.hero.subtitle.compas")}</strong>{t("home.hero.subtitle.suffix")}
              </p>

              <div className="mt-8 flex flex-wrap items-center gap-3">
                {(() => {
                  const phaseMeta = getTournamentPhase();
                  const href = phaseMeta.isGroupPredictionsOpen ? "/quiniela" : phaseMeta.primaryCtaHref;
                  const text = phaseMeta.isGroupPredictionsOpen ? t("home.cta.fill") : phaseMeta.primaryCtaText;
                  const Icon = phaseMeta.isGroupPredictionsOpen ? Target : phaseMeta.phase === "ENDED" ? Trophy : Swords;
                  return (
                    <Link href={href} className="btn btn-primary">
                      <Icon size={16} /> {text}
                    </Link>
                  );
                })()}
                <button
                  type="button"
                  onClick={() => {
                    if (!currentPlayer) {
                      alert(t("home.cta.aiAlert"));
                      return;
                    }
                    window.dispatchEvent(new CustomEvent("q26:open-chat", { detail: { seedMessage: "AI_FILL_START" } }));
                  }}
                  className="btn btn-ghost"
                >
                  <Bot size={16} /> {t("home.cta.aiHelp")}
                </button>
                {currentPlayer && (
                  <Link
                    href="/perfil/foto"
                    className="btn btn-ghost relative"
                  >
                    <Sparkles size={16} /> {t("home.cta.photoStudio")}
                    <span className="absolute -top-2 -right-2 text-[9px] font-extrabold tracking-wider px-1.5 py-0.5 rounded-full bg-gradient-to-r from-[#5E5BFF] to-[#14F195] text-white shadow ring-2 ring-white/20">
                      {t("home.cta.new")}
                    </span>
                  </Link>
                )}
                <Link
                  href="/album"
                  className="btn btn-ghost relative"
                >
                  <BookImage size={16} /> {t("home.cta.album")}
                  <span className="absolute -top-2 -right-2 text-[9px] font-extrabold tracking-wider px-1.5 py-0.5 rounded-full bg-gradient-to-r from-[#14F195] to-[#5E5BFF] text-white shadow ring-2 ring-white/20">
                    {t("home.cta.new")}
                  </span>
                </Link>
                <BracketCtaLink label={t("home.cta.bracket")} newLabel={t("home.cta.new")} />
              </div>

              {/* Desktop-only: leaderboard lives BELOW the hero+CTAs in the
                  left column. Fills the empty space the column had and keeps
                  the right column (spotlight + today's matches) tight at the
                  top — looks like a real web layout, not a mobile spine. */}
              <div className="hidden md:block mt-8">
                <TopScorersLeaderboard />
              </div>
            </div>

            <div className="space-y-4">
              <KOOpenBanner />
              <LateSaverBanner />
              <KOMatchFeed />
              <SelfBeatChip playerId={currentPlayer?.id ?? null} finals={finals} />
            </div>
          </div>
        </div>
      </section>

      {/* ── DIECISEISAVOS · bracket en la home ── */}
      <KnockoutSection />

      <BracketMiniLeaderboard />

      {/* CROMOS STRIP — el álbum del torneo, justo después del hero */}
      {cromos.length > 0 && (
        <section className="container-app pt-4 pb-6">
          <div className="flex items-end justify-between mb-4">
            <div>
              <div className="chip mb-2"><Sparkles size={11} /> {t("home.cromos.chip")}</div>
              <h2 className="font-display text-2xl md:text-3xl font-bold">{t("home.cromos.title")}</h2>
              <p className="text-[var(--ink-soft)] text-sm mt-1">{t("home.cromos.subtitle")}</p>
            </div>
          </div>
          <div className="-mx-4 px-4 md:mx-0 md:px-0 overflow-x-auto pb-4">
            <div className="flex gap-4 md:flex-wrap md:justify-start min-w-min">
              {cromos.map(({ cromo, player }) => (
                <div key={player.id} className="shrink-0">
                  <CromoCard cromo={cromo} player={player} size="sm" onClick={openCromoZoom} />
                </div>
              ))}
            </div>
          </div>
        </section>
      )}

      <AvaThinkingChip />

      <DailyRecapCard />
      <CafeAmCard />
      <ActivityFeed />
      <GhostActivityFeed />
      <PushActivationModal />

      {/* CROMO HERO — la carta FUT del jugador logueado */}
      {myCromo && (
        <section className="container-app pt-2 pb-6">
          <div className="glass-strong rounded-3xl p-5 md:p-7 relative overflow-hidden">
            <div className="absolute -top-16 -right-16 w-72 h-72 rounded-full blur-3xl opacity-20"
              style={{ background: `radial-gradient(closest-side, ${myCromo.player.accent}, transparent)` }} />
            <div className="relative grid md:grid-cols-[auto_1fr] gap-6 items-center">
              <div className="flex justify-center md:justify-start flex-col items-center md:items-start">
                <CromoDeltaBanner playerId={myCromo.cromo.playerId} rating={myCromo.cromo.rating} />
                <CromoCard cromo={myCromo.cromo} player={myCromo.player} size="md" onClick={openCromoZoom} />
              </div>
              <div>
                <div className="chip mb-3"><Sparkles size={12} /> {t("home.myCromo.chip")}</div>
                <h2 className="font-display text-2xl md:text-4xl font-bold leading-tight">
                  {t("home.myCromo.youAre")} <span className="grad-text">{myCromo.cromo.rating} {t("home.myCromo.ovr")}</span> · {myCromo.cromo.position}
                </h2>
                <p className="text-[var(--ink-soft)] mt-2 max-w-md text-sm md:text-base leading-relaxed">
                  {t("home.myCromo.copy")}
                </p>
                <div className="mt-4 grid grid-cols-2 sm:grid-cols-3 gap-2 max-w-md">
                  {myCromo.cromo.statRows.map(s => (
                    <div key={s.key} className="rounded-xl bg-[var(--bg-tint)] px-3 py-2">
                      <div className="flex items-baseline gap-2">
                        <div className="text-[10px] uppercase tracking-wider text-[var(--ink-muted)] font-semibold">{s.label}</div>
                        <div className="font-display text-xl font-bold tabular-nums leading-none">{s.value}</div>
                      </div>
                      <div className="text-[10px] text-[var(--ink-muted)] mt-1 leading-tight">{s.meaning}</div>
                    </div>
                  ))}
                </div>
                <p className="text-[11px] text-[var(--ink-muted)] mt-3 max-w-md">
                  {t("home.myCromo.legend")}
                </p>
                <button
                  type="button"
                  onClick={() => setPackOpen(true)}
                  className="mt-5 inline-flex items-center gap-2 text-sm font-semibold text-[var(--accent-violet)] hover:underline"
                >
                  {t("home.myCromo.viewPack")} <ArrowUpRight size={14} />
                </button>
              </div>
            </div>
          </div>
        </section>
      )}

      {/* PUNTEROS — top 5 charales por puntos */}
      {punteros.length > 0 && (
        <section className="container-app pt-2 pb-6">
          <div className="flex items-end justify-between mb-3">
            <div>
              <div className="chip mb-2"><Trophy size={11} /> {t("home.punteros.chip")}</div>
              <h2 className="font-display text-2xl md:text-3xl font-bold">{t("home.punteros.title")}</h2>
            </div>
            <Link href="/leaderboard" className="hidden md:flex items-center gap-1.5 text-sm font-semibold hover:text-[var(--accent-violet)]">
              {t("home.punteros.fullTable")} <ArrowUpRight size={14} />
            </Link>
          </div>
          <PunterosTop5 rows={punteros.slice(0, 5)} currentPlayerId={currentPlayer?.id} />
        </section>
      )}

      {/* STATS BAND */}
      <section className="container-app py-10">
        <div className="glass rounded-[28px] p-6 md:p-8 grid grid-cols-2 md:grid-cols-4 gap-6 md:gap-2">
          <Stat icon={<Trophy size={18} />} value="48" label={t("home.stats.teams")} />
          <Stat icon={<Activity size={18} />} value="104" label={t("home.stats.matches")} />
          <Stat icon={<MapPin size={18} />} value="16" label={t("home.stats.hosts")} />
          <Stat icon={<CalendarDays size={18} />} value={t("home.stats.duration")} label={t("home.stats.durationLabel")} />
        </div>
      </section>

      <PlayersGrid players={players} currentPlayer={currentPlayer} allFill={allFill} />

      {/* Pack opening overlay para promoción de tier */}
      {myCromo && (
        <PackOpening
          open={packOpen}
          onClose={() => setPackOpen(false)}
          cromo={myCromo.cromo}
          player={myCromo.player}
        />
      )}

      {/* TEAMS PREVIEW */}
      <section className="container-app py-12">
        <div className="flex items-end justify-between mb-6">
          <div>
            <div className="chip mb-2">{t("home.teams.chip")}</div>
            <h2 className="font-display text-3xl md:text-4xl font-bold">{t("home.teams.title")}</h2>
            <p className="text-[var(--ink-soft)] mt-1">{t("home.teams.subtitle")}</p>
          </div>
          <Link href="/grupos" className="hidden md:flex items-center gap-1.5 text-sm font-semibold hover:text-[var(--accent-violet)]">
            {t("home.teams.cta")} <ArrowUpRight size={14} />
          </Link>
        </div>
        <div className="relative">
          <div className="absolute left-0 top-0 bottom-0 w-12 bg-gradient-to-r from-[var(--bg)] to-transparent z-10 pointer-events-none" />
          <div className="absolute right-0 top-0 bottom-0 w-12 bg-gradient-to-l from-[var(--bg)] to-transparent z-10 pointer-events-none" />
          <div className="overflow-hidden">
            <div className="flex gap-3 animate-[float_8s_ease-in-out_infinite] flex-wrap justify-center">
              {TEAMS.map(t => (
                <Link key={t.code} href={`/equipos/${t.code}`} className="group" title={t.name}>
                  <div className="relative w-12 h-12 rounded-xl overflow-hidden ring-1 ring-[var(--line)] hover:ring-[var(--ink)] transition-all hover:-translate-y-0.5 hairline-strong">
                    <Image src={flagUrl(t.iso2, 80)} alt={t.name} fill sizes="48px" className="object-cover" unoptimized />
                  </div>
                </Link>
              ))}
            </div>
          </div>
        </div>
        <div className="mt-6 flex md:hidden justify-center">
          <Link href="/grupos" className="btn btn-ghost">{t("home.teams.cta")} <ArrowUpRight size={14} /></Link>
        </div>
      </section>

      {/* HOW IT WORKS */}
      <section className="container-app py-12">
        <div className="grid md:grid-cols-3 gap-4">
          {[
            { icon: Users, n: "01", t: t("home.how.1.title"), d: t("home.how.1.body") },
            { icon: Target, n: "02", t: t("home.how.2.title"), d: t("home.how.2.body") },
            { icon: Flame, n: "03", t: t("home.how.3.title"), d: t("home.how.3.body") },
          ].map((b, i) => (
            <motion.div key={b.n} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: .35, delay: i * 0.08 }}
              className="glass rounded-3xl p-6 relative overflow-hidden">
              <div className="absolute -top-6 -right-4 font-display text-[120px] font-bold text-[var(--bg-tint)] leading-none select-none">{b.n}</div>
              <div className="relative">
                <div className="w-11 h-11 rounded-2xl grid place-items-center mb-4 bg-[var(--ink)] text-white"><b.icon size={20} /></div>
                <div className="font-display text-xl font-bold mb-1">{b.t}</div>
                <p className="text-sm text-[var(--ink-soft)] leading-relaxed">{b.d}</p>
              </div>
            </motion.div>
          ))}
        </div>
      </section>

      <ScoringRules />

      <BolsaCard players={players} />

      <CtaFooter copy={t("home.cta.copy")} />

      <CromoZoomModal
        target={lightbox}
        finals={actuals as unknown as FinalsMap}
        finalsLoading={false}
        onClose={() => setLightbox(null)}
      />
    </div>
  );
}

// Same NUEVO-chip-with-TTL pattern as the old StandingsNewCard: first view
// stamps q26:bracket-cta-seen-at, then we hide the chip 7 days later. SSR
// renders without the chip to avoid hydration mismatch.
function BracketCtaLink({ label, newLabel }: { label: string; newLabel: string }) {
  const SEEN_KEY = "q26:bracket-cta-seen-at";
  const TTL_MS = 7 * 24 * 60 * 60 * 1000;
  const [showNew, setShowNew] = useState(false);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    try {
      const seenAt = Number(localStorage.getItem(SEEN_KEY) ?? 0);
      if (!Number.isFinite(seenAt) || seenAt <= 0) {
        localStorage.setItem(SEEN_KEY, String(Date.now()));
        setShowNew(true);
        return;
      }
      setShowNew(Date.now() - seenAt < TTL_MS);
    } catch {
      setShowNew(true);
    }
  }, []);

  return (
    <Link
      href="/bracket"
      className="btn btn-ghost border border-[var(--accent-mint)]/40 text-[var(--ink)] relative"
    >
      <Swords size={16} /> {label}
      {mounted && showNew && (
        <span className="absolute -top-2 -right-2 text-[9px] font-extrabold tracking-wider px-1.5 py-0.5 rounded-full bg-gradient-to-r from-[#5E5BFF] to-[#14F195] text-white shadow ring-2 ring-white">
          {newLabel}
        </span>
      )}
    </Link>
  );
}

function ScoringRules() {
  const { t } = useLocale();
  return (
    <section className="container-app py-12">
      <div className="flex items-end justify-between mb-6 flex-wrap gap-3">
        <div>
          <div className="chip mb-2">{t("home.scoring.chip")}</div>
          <h2 className="font-display text-3xl md:text-4xl font-bold">{t("home.scoring.title")}</h2>
          <p className="text-[var(--ink-soft)] mt-1">{t("home.scoring.subtitle")}</p>
        </div>
      </div>
      <div className="grid md:grid-cols-3 gap-4">
        <div className="glass rounded-3xl p-6">
          <div className="flex items-center gap-2 text-sm uppercase tracking-[0.18em] text-[var(--ink-muted)] font-semibold mb-3">
            <Target size={14} /> {t("home.scoring.groups")}
          </div>
          <div className="font-display text-4xl font-bold leading-none">{SCORING.pickWinner}<span className="text-base opacity-60"> {t("home.scoring.pts")}</span></div>
          <div className="text-sm text-[var(--ink-soft)] mt-1">{t("home.scoring.groups.copy")}</div>
          <div className="mt-4 pt-4 border-t border-[var(--line)]">
            <div className="text-xs uppercase tracking-[0.18em] text-[var(--ink-muted)] font-semibold mb-1">{t("home.scoring.exact")}</div>
            <div className="text-xs text-[var(--ink-soft)] leading-relaxed">{t("home.scoring.exact.copy")}</div>
          </div>
        </div>
        <div className="glass rounded-3xl p-6">
          <div className="flex items-center gap-2 text-sm uppercase tracking-[0.18em] text-[var(--ink-muted)] font-semibold mb-3">
            <Swords size={14} /> {t("home.scoring.ko")}
          </div>
          <div className="font-display text-4xl font-bold leading-none">0<span className="text-base opacity-60"> {t("home.scoring.pts")}</span></div>
          <div className="text-sm text-[var(--ink-soft)] mt-1">
            {t("home.scoring.ko.copy")}
          </div>
        </div>
        <div className="glass rounded-3xl p-6 ring-2 ring-[var(--accent-violet)]/40">
          <div className="flex items-center gap-2 text-sm uppercase tracking-[0.18em] text-[var(--ink-muted)] font-semibold mb-3">
            <Crown size={14} /> {t("home.scoring.champion")}
          </div>
          <div className="font-display text-4xl font-bold leading-none">+{SCORING.bonusChampion}<span className="text-base opacity-60"> {t("home.scoring.pts")}</span></div>
          <div className="text-sm text-[var(--ink-soft)] mt-1">
            {t("home.scoring.champion.copy")}
          </div>
          <ul className="text-xs text-[var(--ink-soft)] mt-3 space-y-1 leading-relaxed">
            <li>· Lo fijaste pre-torneo → +{SCORING.bonusChampion} pts</li>
            <li>· Lo cambiaste en R32 → +{Math.round(SCORING.bonusChampion * 0.8)} pts</li>
            <li>· En Octavos → +{Math.round(SCORING.bonusChampion * 0.6)} pts</li>
            <li>· En Cuartos → +{Math.round(SCORING.bonusChampion * 0.4)} pts</li>
            <li>· En Semis → +{Math.round(SCORING.bonusChampion * 0.2)} pts</li>
            <li>· Empezada la Final → 0 pts</li>
          </ul>
        </div>
      </div>
    </section>
  );
}

// =====================================================================
//                        SHARED COMPONENTS
// =====================================================================

function PlayersGrid({
  players, currentPlayer, allFill, championLabel,
}: {
  players: ReturnType<typeof usePlayer>["players"];
  currentPlayer: ReturnType<typeof usePlayer>["currentPlayer"];
  allFill: { id: string; pct: number; champion?: string }[];
  championLabel?: string;
}) {
  const { t } = useLocale();
  const champLabel = championLabel ?? t("home.players.champion");
  return (
    <section className="container-app py-12">
      <div className="flex items-end justify-between mb-6">
        <div>
          <div className="chip mb-2">{t("home.players.chip")}</div>
          <h2 className="font-display text-3xl md:text-4xl font-bold">{t("home.players.title")}</h2>
          <p className="text-[var(--ink-soft)] mt-1">{t("home.players.subtitle")}</p>
        </div>
        <Link href="/leaderboard" className="hidden md:flex items-center gap-1.5 text-sm font-semibold hover:text-[var(--accent-violet)]">
          {t("home.players.viewRanking")} <ArrowUpRight size={14} />
        </Link>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-3 lg:grid-cols-3 gap-3">
        {players.map((p, idx) => {
          const fill = allFill.find(f => f.id === p.id);
          const pct = fill?.pct ?? 0;
          const isMe = currentPlayer?.id === p.id;
          const href = !currentPlayer ? "/jugadores" : isMe ? "/quiniela" : `/quiniela?view=${p.id}`;
          const isBot = p.isBot;
          const championTeam = fill?.champion ? TEAMS.find(t => t.code === fill.champion) : undefined;
          return (
            <motion.div key={p.id} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
              transition={{ duration: .35, delay: idx * 0.04 }}
              className="relative">
              {isBot && (
                <>
                  <span
                    aria-hidden
                    className="pointer-events-none absolute inset-0 rounded-2xl z-10 ai-liquid-border"
                  />
                  <span className="absolute -top-2 -right-2 z-20 text-[9px] font-extrabold tracking-wider px-2 py-0.5 rounded-full bg-gradient-to-r from-[#5E5BFF] to-[#14F195] text-white shadow-lg ring-2 ring-white">
                    NUEVO
                  </span>
                </>
              )}
              <Link href={href} className={`group relative z-0 block glass rounded-2xl p-4 transition-transform hover:-translate-y-0.5 ${isMe ? "ring-2 ring-[var(--ink)]" : ""}`}>
                <div className="flex items-center gap-3">
                  <PlayerAvatar player={p} size={48} rounded="rounded-2xl" textClass="text-2xl" tint={0.12} enableLightbox />
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 min-w-0">
                      <div className="font-semibold truncate min-w-0">{p.name}</div>
                      {isMe && <span className="text-[9px] font-bold px-1.5 py-0.5 rounded-full bg-[var(--ink)] text-white shrink-0">{t("home.players.you")}</span>}
                      {isBot && <span className="text-[9px] font-bold px-1.5 py-0.5 rounded-full bg-[var(--ink)] text-white shrink-0">{t("home.players.bot")}</span>}
                    </div>
                    <div className="text-xs text-[var(--ink-muted)]">
                      {pct === 0 ? t("home.players.noPicks") : `${pct}% ${t("home.players.ready")}`}
                    </div>
                  </div>
                  {championTeam ? (
                    <div
                      className="hidden sm:flex items-center gap-1.5 px-2 py-1 rounded-full bg-[var(--bg-tint)] ring-1 ring-[var(--line)] shrink-0"
                      title={`${champLabel}: ${championTeam.name}`}
                    >
                      <span className="relative w-4 h-4 rounded-sm overflow-hidden ring-1 ring-black/10 shrink-0">
                        <Image src={flagUrl(championTeam.iso2, 32)} alt={championTeam.name} fill sizes="16px" className="object-cover" unoptimized />
                      </span>
                      <span className="font-display text-[11px] font-bold tracking-wider tabular-nums" style={{ color: p.accent }}>{championTeam.code}</span>
                    </div>
                  ) : (
                    <div className="hidden sm:block text-[10px] font-semibold uppercase tracking-wider text-[var(--ink-muted)] px-2 py-1 rounded-full bg-[var(--bg-tint)] ring-1 ring-[var(--line)] shrink-0">
                      {t("home.players.noChampion")}
                    </div>
                  )}
                </div>
                <div className="mt-3 flex items-center gap-2 sm:hidden">
                  <div className="flex-1 h-1.5 rounded-full bg-[var(--bg-tint)] overflow-hidden min-w-0">
                    <div className="h-full rounded-full transition-all" style={{ width: `${pct}%`, background: p.accent }} />
                  </div>
                  {championTeam ? (
                    <div
                      className="flex items-center gap-1 px-1.5 py-0.5 rounded-full bg-[var(--bg-tint)] ring-1 ring-[var(--line)] shrink-0"
                      title={`${champLabel}: ${championTeam.name}`}
                    >
                      <span className="relative w-3 h-3 rounded-sm overflow-hidden ring-1 ring-black/10 shrink-0">
                        <Image src={flagUrl(championTeam.iso2, 24)} alt={championTeam.name} fill sizes="12px" className="object-cover" unoptimized />
                      </span>
                      <span className="font-display text-[10px] font-bold tracking-wider tabular-nums leading-none" style={{ color: p.accent }}>{championTeam.code}</span>
                    </div>
                  ) : (
                    <div className="text-[9px] font-semibold uppercase tracking-wider text-[var(--ink-muted)] px-1.5 py-0.5 rounded-full bg-[var(--bg-tint)] ring-1 ring-[var(--line)] shrink-0 leading-none">
                      {t("home.players.noChampion")}
                    </div>
                  )}
                </div>
                <div className="mt-3 h-1.5 rounded-full bg-[var(--bg-tint)] overflow-hidden hidden sm:block">
                  <div className="h-full rounded-full transition-all" style={{ width: `${pct}%`, background: p.accent }} />
                </div>
              </Link>
            </motion.div>
          );
        })}
      </div>
    </section>
  );
}

function BolsaCard({ players }: { players: ReturnType<typeof usePlayer>["players"] }) {
  const { t } = useLocale();
  return (
    <section className="container-app pt-6 pb-2">
      <div className="glass-strong rounded-3xl p-5 md:p-6 max-w-xl mx-auto">
        <div className="flex items-center gap-4">
          <div className="w-14 h-14 rounded-2xl grid place-items-center shrink-0"
               style={{ background: "linear-gradient(135deg, #D4AF37, #FFE07A)" }}>
            <Coins className="text-white" size={26} />
          </div>
          <div className="flex-1 min-w-0">
            <div className="text-xs uppercase tracking-[0.18em] text-[var(--ink-muted)]">{t("home.bolsa.total")}</div>
            <div className="font-display text-3xl font-bold">${POT_TOTAL_MXN} <span className="text-base font-medium text-[var(--ink-soft)]">MXN</span></div>
          </div>
          <div className="text-right shrink-0">
            <div className="text-xs text-[var(--ink-muted)]">{t("home.bolsa.perPlayer")}</div>
            <div className="font-display text-xl font-semibold">${PER_PLAYER_MXN}</div>
          </div>
        </div>
        <div className="mt-4 flex -space-x-2 flex-wrap">
          {players.map(p => (
            <div key={p.id} className="ring-2 ring-white rounded-full">
              <PlayerAvatar player={p} size={32} rounded="rounded-full" textClass="text-sm" tint={0.2} enableLightbox />
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

function CtaFooter({ copy }: { copy: React.ReactNode }) {
  const { t } = useLocale();
  return (
    <section className="container-app pt-8 pb-20">
      <div className="rounded-[36px] relative overflow-hidden p-10 md:p-14 text-center" style={{ background: "linear-gradient(135deg, #0A0A0A 0%, #1A1A2E 100%)" }}>
        <div className="absolute inset-0 opacity-20" style={{
          background: "radial-gradient(circle at 20% 30%, rgba(20,241,149,0.4), transparent 40%), radial-gradient(circle at 80% 70%, rgba(94,91,255,0.4), transparent 40%)",
        }} />
        <div className="relative">
          <div className="inline-block chip mb-4" style={{ background: "rgba(255,255,255,0.1)", color: "white" }}>
            <Sparkles size={12} /> {t("home.cta.lastCall")}
          </div>
          <h3 className="font-display text-4xl md:text-6xl font-bold text-white leading-tight">
            <span className="grad-text">{t("home.cta.amount")}</span>
            <br />
            {t("home.cta.tagline.a")}
          </h3>
          <p className="text-white/70 mt-4 max-w-xl mx-auto">{copy}</p>
          <Link href="/quiniela" className="inline-flex items-center gap-2 mt-8 px-8 h-14 rounded-full bg-white text-[var(--ink)] font-bold shadow-2xl hover:scale-[1.02] transition-transform">
            <Target size={18} /> {t("home.cta.start")}
          </Link>
        </div>
      </div>
    </section>
  );
}

function LiveTeamSide({ team, align }: { team: typeof TEAMS[number] | undefined; align: "left" | "right" }) {
  if (!team) return <div />;
  return (
    <Link href={`/equipos/${team.code}`} className={`flex items-center gap-2 min-w-0 hover:opacity-80 transition-opacity ${align === "right" ? "flex-row-reverse text-right" : ""}`}>
      <div className="relative w-10 h-10 rounded-xl overflow-hidden ring-1 ring-[var(--line)] shrink-0">
        <Image src={flagUrl(team.iso2, 64)} alt={team.name} fill sizes="40px" className="object-cover" unoptimized />
      </div>
      <div className="min-w-0 flex-1">
        <div className="font-display text-lg font-bold leading-none">{team.code}</div>
        <div className="text-[10px] text-[var(--ink-muted)] truncate uppercase tracking-wider">{team.name}</div>
      </div>
    </Link>
  );
}

function useNow(intervalMs = 1000) {
  const [now, setNow] = useState<number | null>(null);
  useEffect(() => {
    setNow(Date.now());
    const id = setInterval(() => setNow(Date.now()), intervalMs);
    return () => clearInterval(id);
  }, [intervalMs]);
  return now;
}

function cdmxDateOf(ms: number): string {
  return new Date(ms).toLocaleDateString("en-CA", { timeZone: "America/Mexico_City" });
}

// Higher = more anticipated. Sum of both teams' strength (200 - FIFA rank, with
// null treated as 200 = weakest), plus a big bonus when Mexico plays (this is a
// Mexico-themed quiniela) and a smaller bonus for knockout rounds. Used as
// tie-breaker when multiple kickoffs share the same time slot.
function fixtureImportance(fx: GroupFixture): number {
  const rank = (code: string) => TEAMS.find(t => t.code === code)?.ranking ?? 200;
  let score = (200 - rank(fx.home)) + (200 - rank(fx.away));
  if (fx.home === "MEX" || fx.away === "MEX") score += 500;
  if (fx.matchday > 3) score += 150;
  return score;
}

function formatCountdown(ms: number): string {
  if (ms <= 0) return "0s";
  const s = Math.floor(ms / 1000);
  const days = Math.floor(s / 86400);
  const h = Math.floor((s % 86400) / 3600);
  const m = Math.floor((s % 3600) / 60);
  const sec = s % 60;
  if (days > 0) return `${days}d ${h}h`;
  if (h > 0) return `${h}h ${m.toString().padStart(2, "0")}m`;
  return `${m}m ${sec.toString().padStart(2, "0")}s`;
}

// Chip aislado para que el tick por segundo NO re-renderice el componente
// padre (TodayRail / NextWhistleCard). Esto era el principal causante del
// "temblor" al hacer scroll.
function CountdownChip({
  kickoffMs,
  size = "sm",
  className,
}: {
  kickoffMs: number;
  size?: "sm" | "lg";
  className?: string;
}) {
  // Cerca del partido (≤1h) refresca cada segundo. Lejos, cada minuto: nadie
  // mira un contador de 23h cambiar cada segundo y el costo en perf es real.
  const initial = typeof window === "undefined" ? kickoffMs : Date.now();
  const [now, setNow] = useState<number>(initial);
  useEffect(() => {
    setNow(Date.now());
    let id: ReturnType<typeof setTimeout>;
    const tick = () => {
      const dt = kickoffMs - Date.now();
      const interval = dt < 60 * 60 * 1000 ? 1000 : 60_000;
      id = setTimeout(() => { setNow(Date.now()); tick(); }, interval);
    };
    tick();
    return () => clearTimeout(id);
  }, [kickoffMs]);

  const remaining = kickoffMs - now;
  if (remaining <= 0) return null;
  const urgent = remaining < 60 * 60 * 1000;
  const base = size === "lg"
    ? "text-xs font-extrabold tabular-nums leading-none"
    : "text-[10px] font-extrabold tabular-nums leading-none";
  return (
    <span
      className={`${base} ${className ?? ""}`}
      style={{ color: urgent ? "#FF3B82" : "var(--ink-muted)" }}
    >
      {formatCountdown(remaining)}
    </span>
  );
}

function SpotlightCountdownBlocks({ kickoffMs }: { kickoffMs: number }) {
  const { t } = useLocale();
  // Mismo patrón de cadencia adaptativa: 1s cerca, 60s lejos. Aislado para
  // que el resto del card no rerenderice.
  const [now, setNow] = useState<number>(typeof window === "undefined" ? kickoffMs : Date.now());
  useEffect(() => {
    setNow(Date.now());
    let id: ReturnType<typeof setTimeout>;
    const tick = () => {
      const dt = kickoffMs - Date.now();
      const interval = dt < 60 * 60 * 1000 ? 1000 : 60_000;
      id = setTimeout(() => { setNow(Date.now()); tick(); }, interval);
    };
    tick();
    return () => clearTimeout(id);
  }, [kickoffMs]);

  const ms = Math.max(0, kickoffMs - now);
  const urgent = ms > 0 && ms < 60 * 60 * 1000;
  const d = Math.floor(ms / 86400000);
  const h = Math.floor((ms / 3600000) % 24);
  const m = Math.floor((ms / 60000) % 60);
  const s = Math.floor((ms / 1000) % 60);
  const pad = (n: number) => String(n).padStart(2, "0");
  const boxes = [
    { label: t("home.next.countdown.days"),  v: pad(d) },
    { label: t("home.next.countdown.hours"), v: pad(h) },
    { label: t("home.next.countdown.min"),   v: pad(m) },
    { label: t("home.next.countdown.sec"),   v: pad(s) },
  ];
  return (
    <div className={`mt-4 grid grid-cols-4 gap-1.5 ${urgent ? "animate-pulse" : ""}`}>
      {boxes.map((b, i) => (
        <div key={i} className="text-center">
          <div className="bg-[var(--ink)] text-white rounded-xl py-2">
            <div className="font-display text-lg md:text-2xl font-bold tabular-nums leading-none">{b.v}</div>
          </div>
          <div className="mt-1 text-[9px] uppercase tracking-[0.15em] text-[var(--ink-muted)]">{b.label}</div>
        </div>
      ))}
    </div>
  );
}

function pickNextSpotlight(
  fixtures: GroupFixture[],
  liveById: Record<string, LiveFixture>,
  finals: Record<string, { homeGoals: number; awayGoals: number }>,
  now: number,
): { mode: "live" | "upcoming" | "justFinal"; fx: GroupFixture; live?: LiveFixture } | null {
  const live = fixtures
    .map(fx => ({ fx, live: liveById[fx.id] }))
    .find(x => x.live?.phase === "live");
  if (live) return { mode: "live", fx: live.fx, live: live.live };

  const upcoming = fixtures
    .filter(fx => !finals[fx.id] && fixtureKickoffMs(fx) > now)
    .sort((a, b) => {
      const dt = fixtureKickoffMs(a) - fixtureKickoffMs(b);
      if (dt !== 0) return dt;
      return fixtureImportance(b) - fixtureImportance(a);
    })[0];
  if (upcoming) return { mode: "upcoming", fx: upcoming };

  const justFinal = fixtures
    .filter(fx => finals[fx.id])
    .sort((a, b) => fixtureKickoffMs(b) - fixtureKickoffMs(a))[0];
  if (justFinal) return { mode: "justFinal", fx: justFinal };

  return null;
}

function NextWhistleCard({
  liveById, finals, pickersByFx,
}: {
  liveById: Record<string, LiveFixture>;
  finals: Record<string, { homeGoals: number; awayGoals: number }>;
  pickersByFx: Record<string, { H: PlayerLite[]; D: PlayerLite[]; A: PlayerLite[] }>;
}) {
  // El card mismo se reevalúa cada minuto (cambio de fase). Los segundos del
  // countdown viven en <SpotlightCountdownBlocks/>, que no rerenderiza al
  // padre — así el resto del home no tiembla mientras haces scroll.
  const now = useNow(60_000);
  const { t } = useLocale();
  const fixtures = useMemo(() => allGroupFixtures(), []);
  const spot = useMemo(
    () => (now === null ? null : pickNextSpotlight(fixtures, liveById, finals, now)),
    [fixtures, liveById, finals, now],
  );
  const [atinandoOpen, setAtinandoOpen] = useState(false);

  if (!spot) {
    return (
      <div className="glass-strong rounded-3xl p-5 md:p-6 relative overflow-hidden">
        <div className="absolute inset-0 shimmer opacity-30" />
        <div className="relative text-center py-6">
          <span className="chip mb-3"><Sparkles size={12} /> {t("home.next.mundialChip")}</span>
          <div className="font-display text-2xl font-bold">{t("home.next.tournamentOver")}</div>
          <div className="text-sm text-[var(--ink-muted)] mt-1">{t("home.next.tournamentOverSub")}</div>
        </div>
      </div>
    );
  }

  const fx = spot.fx;
  const homeTeam = TEAMS.find(t => t.code === fx.home);
  const awayTeam = TEAMS.find(t => t.code === fx.away);
  const koMs = fixtureKickoffMs(fx);

  const accent =
    spot.mode === "live" ? "rgba(255,59,130,0.95)" :
    spot.mode === "justFinal" ? "rgba(20,241,149,0.95)" :
    "rgba(94,91,255,0.95)";

  return (
    <motion.div initial={{ opacity: 0, scale: .96 }} animate={{ opacity: 1, scale: 1 }} transition={{ duration: .5 }}
      className="glass-strong rounded-3xl p-5 md:p-6 relative overflow-hidden">
      <div className="absolute inset-0 opacity-30 pointer-events-none"
        style={{ background: `radial-gradient(circle at 50% 0%, ${accent.replace("0.95", "0.28")}, transparent 60%)` }} />
      <div className="relative">
        <div className="flex items-center justify-between mb-4 gap-2">
          {spot.mode === "live" ? (
            <span className="chip" style={{ background: "rgba(255,59,130,0.18)", color: "#FF3B82" }}>
              <Radio size={11} className="animate-pulse" /> {t("home.next.live")} · {spot.live?.minute ?? ""}
            </span>
          ) : spot.mode === "justFinal" ? (
            <span className="chip" style={{ background: "rgba(20,241,149,0.15)", color: "#0B8A4E" }}>
              <Sparkles size={12} /> {t("home.next.recent")}
            </span>
          ) : (
            <span className="chip"><Sparkles size={12} /> {t("home.next.upcoming")}</span>
          )}
          <span className="text-[10px] uppercase tracking-wider text-[var(--ink-muted)] truncate">
            {t("home.next.group")} {fx.group} · {t("home.next.matchday")}{fx.matchday}
          </span>
        </div>

        <div className="grid grid-cols-[minmax(0,1fr)_auto_minmax(0,1fr)] items-center gap-2 sm:gap-3">
          <LiveTeamSide team={homeTeam} align="left" />
          <div className="text-center shrink-0 px-1">
            {spot.mode === "live" && spot.live ? (
              <>
                <div className="font-display text-3xl md:text-4xl font-bold tabular-nums leading-none whitespace-nowrap">
                  {spot.live.homeGoals ?? 0}<span className="text-[var(--ink-muted)] mx-1.5">-</span>{spot.live.awayGoals ?? 0}
                </div>
                <div className="text-[10px] uppercase tracking-[0.18em] text-[var(--ink-muted)] mt-1">vs</div>
              </>
            ) : spot.mode === "justFinal" && finals[fx.id] ? (
              <>
                <div className="font-display text-3xl md:text-4xl font-bold tabular-nums leading-none whitespace-nowrap">
                  {finals[fx.id].homeGoals}<span className="text-[var(--ink-muted)] mx-1.5">-</span>{finals[fx.id].awayGoals}
                </div>
                <div className="text-[10px] uppercase tracking-[0.18em] text-[var(--ink-muted)] mt-1">{t("home.next.final")}</div>
              </>
            ) : (
              <>
                <div className="font-display text-2xl md:text-3xl font-bold text-[var(--ink-muted)]">vs</div>
                <div className="text-[10px] uppercase tracking-[0.15em] text-[var(--ink-muted)] mt-1">
                  <ViewerKickoffTime fx={fx} /> · <ViewerKickoffDate fx={fx} />
                </div>
              </>
            )}
          </div>
          <LiveTeamSide team={awayTeam} align="right" />
        </div>

        {spot.mode === "upcoming" && <SpotlightCountdownBlocks kickoffMs={koMs} />}

        {(() => {
          if (spot.mode !== "live" || !spot.live) return null;
          const h = spot.live.homeGoals ?? 0;
          const a = spot.live.awayGoals ?? 0;
          const lead: "H" | "D" | "A" = h > a ? "H" : h < a ? "A" : "D";
          const atinando = pickersByFx[fx.id]?.[lead] ?? [];
          if (atinando.length === 0) return null;
          const leadLabel = lead === "H" ? t("home.next.home") : lead === "D" ? t("home.next.draw") : t("home.next.away");
          const subtitle = `${homeTeam?.code ?? fx.home} ${h}-${a} ${awayTeam?.code ?? fx.away} · ${t("home.next.pickedHome")} ${leadLabel}`;
          return (
            <>
              <div className="mt-4 border-t border-[var(--line)] pt-3 space-y-2">
                <div className="text-[10px] uppercase tracking-wider text-[var(--ink-muted)]">
                  {t("home.next.atinando")} · <span className="text-[var(--ink)] font-semibold tabular-nums">{atinando.length}</span>
                </div>
                <button
                  type="button"
                  onClick={() => setAtinandoOpen(true)}
                  aria-label={`${t("home.next.atinando")} (${atinando.length})`}
                  title={t("home.next.atinando")}
                  className="flex -space-x-2 items-center cursor-pointer rounded-full -mx-1 px-1 py-0.5 hover:bg-[var(--bg-tint)] active:scale-[0.98] transition-all"
                >
                  {atinando.slice(0, 6).map(p => (
                    <div key={p.id} className="ring-2 ring-white rounded-full">
                      <PlayerAvatar player={p} size={26} rounded="rounded-full" textClass="text-xs" tint={0.2} />
                    </div>
                  ))}
                  {atinando.length > 6 && (
                    <div className="ring-2 ring-white rounded-full bg-[var(--ink)] text-white w-[26px] h-[26px] grid place-items-center text-[10px] font-bold">
                      +{atinando.length - 6}
                    </div>
                  )}
                </button>
              </div>
              <AtinandoSheet
                open={atinandoOpen}
                onClose={() => setAtinandoOpen(false)}
                title={`${t("home.next.atinando")} · ${atinando.length}`}
                subtitle={subtitle}
                players={atinando}
                accent="#FF3B82"
              />
            </>
          );
        })()}

        <Link
          href={
            spot.mode === "live" ? `/partido/${fx.id}/live` :
            spot.mode === "upcoming" ? "/quiniela" :
            "/partidos"
          }
          className="mt-4 flex items-center justify-center gap-1.5 text-sm font-semibold text-[var(--ink)] hover:text-[var(--accent-violet)] transition-colors"
        >
          {spot.mode === "upcoming" ? t("home.next.predict") : spot.mode === "live" ? t("home.next.followLive") : t("home.next.moreMatches")}
          <ArrowUpRight size={14} />
        </Link>
      </div>
    </motion.div>
  );
}

function PickersCluster({ label, players, accent }: { label: string; players: PlayerLite[]; accent: string }) {
  if (players.length === 0) return null;
  const MAX = 4;
  const visible = players.slice(0, MAX);
  const overflow = Math.max(0, players.length - MAX);
  return (
    <div className="flex items-center gap-1 min-w-0" title={`${label}: ${players.map(p => p.name).join(", ")}`}>
      <span className="text-[10px] uppercase tracking-wider font-extrabold shrink-0" style={{ color: accent }}>{label}</span>
      <div className="flex -space-x-1.5">
        {visible.map(p => (
          <Link
            key={p.id}
            href={`/quiniela?view=${p.id}`}
            onClick={e => e.stopPropagation()}
            title={p.name}
            className="inline-block rounded-full hover:scale-110 hover:z-10 transition-transform relative"
            style={{ boxShadow: `0 0 0 1.5px ${accent}, 0 0 0 2.5px white` }}
          >
            <PlayerAvatar player={p} size={18} rounded="rounded-full" textClass="text-[8px]" tint={0.2} />
          </Link>
        ))}
        {overflow > 0 && (
          <span className="w-[18px] h-[18px] rounded-full grid place-items-center text-[8px] font-bold text-white" style={{ background: accent, boxShadow: "0 0 0 1.5px white" }}>
            +{overflow}
          </span>
        )}
      </div>
    </div>
  );
}

function InlinePicker({
  fx, playerId, probs,
}: {
  fx: GroupFixture;
  playerId: string;
  probs: { home: number; draw: number; away: number };
}) {
  const homeTeam = TEAMS.find(t => t.code === fx.home);
  const awayTeam = TEAMS.find(t => t.code === fx.away);
  const [pick, setPick] = useState<Pick1X2 | undefined>(undefined);
  const [flash, setFlash] = useState<Pick1X2 | null>(null);

  useEffect(() => {
    const refresh = () => {
      const p = loadPredictions(playerId);
      setPick(p.group[fx.id]?.pick);
    };
    refresh();
    const onUpd = (e: Event) => {
      const ce = e as CustomEvent<string>;
      if (ce.detail === playerId) refresh();
    };
    window.addEventListener("q26:predictions-updated", onUpd as EventListener);
    return () => window.removeEventListener("q26:predictions-updated", onUpd as EventListener);
  }, [playerId, fx.id]);

  function commit(e: React.MouseEvent, next: Pick1X2) {
    e.preventDefault();
    e.stopPropagation();
    const all = loadPredictions(playerId);
    const prev = all.group[fx.id] ?? { pick: next };
    all.group[fx.id] = { ...prev, pick: next, source: "manual" };
    // Optimistic: write localStorage immediately + legacy bulk fallback
    savePredictions(all);
    setPick(next);
    setFlash(next);
    setTimeout(() => setFlash(f => (f === next ? null : f)), 600);
    // Primary write: fire directly to server without debounce
    firePickToServer(playerId, fx.id, next).then(result => {
      if (result.error === "locked") setPick(prev.pick as Pick1X2 | undefined);
    });
    track("pick_quick", { fixtureId: fx.id, pick: next });
  }

  const labelFor = (k: Pick1X2) =>
    k === "H" ? (homeTeam?.code ?? fx.home) : k === "A" ? (awayTeam?.code ?? fx.away) : "X";

  const probFor = (k: Pick1X2) =>
    k === "H" ? probs.home : k === "A" ? probs.away : probs.draw;
  const accentFor = (k: Pick1X2) =>
    k === "H" ? "#047857" : k === "A" ? "#BE123C" : "#64748B";

  return (
    <div className="px-3 pb-3">
      <div className="flex items-center gap-1.5">
        {(["H", "D", "A"] as const).map(k => {
          const active = pick === k;
          const isFlashing = flash === k;
          const prob = probFor(k);
          return (
            <button
              key={k}
              type="button"
              onClick={(e) => commit(e, k)}
              className={`flex-1 relative py-2.5 rounded-xl text-[11px] font-extrabold uppercase tracking-wider overflow-hidden transition-all active:scale-95 ${
                active ? "text-white shadow-md" : "text-[var(--ink-soft)] hover:text-[var(--ink)]"
              } ${isFlashing ? "ring-2 ring-[var(--accent-mint)]" : ""}`}
              style={{
                background: active ? "var(--ink)" : "var(--bg-tint)",
                boxShadow: active ? "0 4px 12px -4px rgba(0,0,0,0.3)" : "none",
              }}
            >
              {!active && (
                <span
                  className="absolute bottom-0 left-0 h-[3px] rounded-full transition-all duration-700"
                  style={{ width: `${prob}%`, background: accentFor(k) }}
                />
              )}
              <span className="relative z-10 block text-center leading-none">{labelFor(k)}</span>
              <span className="relative z-10 block text-center text-[9px] opacity-60 leading-none mt-0.5">{prob}%</span>
            </button>
          );
        })}
        <Link
          href={`/quiniela?fixture=${fx.id}`}
          onClick={(e) => e.stopPropagation()}
          className="w-9 h-9 flex items-center justify-center rounded-xl bg-[var(--bg-tint)] text-[var(--ink-muted)] hover:text-[var(--ink)] hover:bg-[var(--hairline)] transition-colors shrink-0"
          title="Marcador exacto"
        >
          ✎
        </Link>
      </div>
    </div>
  );
}

// Per-fixture verdict for the current player: ACERTASTE / EXACTO / MAMASTE.
// Returns null if no pick or fixture not finished — keeps the row clean.
type Verdict = { label: string; tone: "good" | "best" | "bad" };
function verdictFor(
  pred: { pick?: Pick1X2 | null; homeGoals?: number; awayGoals?: number } | undefined,
  final: { homeGoals: number; awayGoals: number } | undefined,
  fxHome: string,
  fxAway: string,
): Verdict | null {
  if (!final || !pred || !pred.pick) return null;
  const actual: MatchResult = {
    home: fxHome,
    away: fxAway,
    homeGoals: final.homeGoals,
    awayGoals: final.awayGoals,
  };
  const exact =
    typeof pred.homeGoals === "number" && typeof pred.awayGoals === "number" &&
    pred.homeGoals === final.homeGoals && pred.awayGoals === final.awayGoals;
  if (exact) return { label: "EXACTO", tone: "best" };
  if (pred.pick === actualPick(actual)) return { label: "ACERTASTE", tone: "good" };
  return { label: "MAMASTE", tone: "bad" };
}

function TodayRail({
  liveById, finals, allPicks, players, punteros, pickersByFx,
}: {
  liveById: Record<string, LiveFixture>;
  finals: Record<string, { homeGoals: number; awayGoals: number }>;
  allPicks: PlayerPredictions[];
  players: ReadonlyArray<import("@/data/players").Player>;
  punteros: PunteroRow[];
  pickersByFx: Record<string, { H: PlayerLite[]; D: PlayerLite[]; A: PlayerLite[] }>;
}) {
  // Sólo necesitamos saber qué día es y filtrar partidos pasados. Cada minuto
  // basta: los countdowns por fila se rerenderean solos vía <CountdownChip/>.
  const now = useNow(60_000);
  const { currentPlayer } = usePlayer();
  const { t } = useLocale();
  const myPicks = useMemo<PlayerPredictions | null>(
    () => currentPlayer ? loadPredictions(currentPlayer.id) : null,
    [currentPlayer],
  );
  const [overlayFxId, setOverlayFxId] = useState<string | null>(null);

  // Per-player 1X2 accuracy over the whole tournament so we can show "X acertó
  // 14 de 20" next to each picker in the overlay. Lightweight: just walks the
  // finals map and counts. Memoized so the overlay opens instantly.
  const accuracyByPlayer = useMemo(() => {
    const acc: Record<string, { hits: number; decided: number }> = {};
    const fxIdx = new Map(allGroupFixtures().map(fx => [fx.id, fx]));
    for (const p of allPicks) {
      let hits = 0, decided = 0;
      for (const [fxId, real] of Object.entries(finals)) {
        const fx = fxIdx.get(fxId);
        if (!fx) continue;
        const pick = p.group[fxId]?.pick;
        if (!pick) continue;
        decided++;
        const truth: "H" | "D" | "A" = real.homeGoals > real.awayGoals ? "H" : real.homeGoals < real.awayGoals ? "A" : "D";
        if (pick === truth) hits++;
      }
      acc[p.playerId] = { hits, decided };
    }
    return acc;
  }, [allPicks, finals]);
  const today = useMemo(() => {
    if (now === null) return [];
    const todayStr = cdmxDateOf(now);
    return allGroupFixtures()
      .filter(fx => fx.date === todayStr)
      .sort((a, b) => fixtureKickoffMs(a) - fixtureKickoffMs(b));
  }, [now]);

  // Aggregate today's outcome for the current player: total points + W/L/exact
  // tally. Drives the "Tus puntos hoy" pill and verdict badges below.
  const myTodayTally = useMemo(() => {
    if (!myPicks) return null;
    let pts = 0, hits = 0, exactos = 0, mamadas = 0, decided = 0;
    for (const fx of today) {
      const final = finals[fx.id];
      if (!final) continue;
      decided += 1;
      const pred = myPicks.group[fx.id];
      if (!pred?.pick) { mamadas += 1; continue; }
      const v = verdictFor(pred, final, fx.home, fx.away);
      if (!v) continue;
      const actual: MatchResult = {
        home: fx.home, away: fx.away,
        homeGoals: final.homeGoals, awayGoals: final.awayGoals,
      };
      pts += scoreGroupPrediction(pred, actual);
      if (v.tone === "best") exactos += 1;
      else if (v.tone === "good") hits += 1;
      else mamadas += 1;
    }
    return { pts, hits, exactos, mamadas, decided };
  }, [myPicks, today, finals]);

  // Streak of consecutive 1X2 hits in today's decided fixtures (chronological).
  const myStreakToday = useMemo(() => {
    if (!myPicks) return 0;
    let best = 0, run = 0;
    for (const fx of today) {
      const final = finals[fx.id];
      if (!final) continue;
      const pred = myPicks.group[fx.id];
      const v = pred ? verdictFor(pred, final, fx.home, fx.away) : null;
      if (v && (v.tone === "good" || v.tone === "best")) {
        run += 1;
        if (run > best) best = run;
      } else {
        run = 0;
      }
    }
    return best;
  }, [myPicks, today, finals]);

  // Hottest charal today: most +pts from today's decided fixtures across the
  // group. Ties broken by exact-score count. Excludes the AI bot.
  const hottestToday = useMemo(() => {
    if (today.length === 0 || allPicks.length === 0) return null;
    type Row = { id: string; pts: number; exactos: number };
    const rows: Row[] = [];
    for (const p of allPicks) {
      const player = players.find(pp => pp.id === p.playerId);
      if (!player || player.isBot) continue;
      let pts = 0, exactos = 0;
      for (const fx of today) {
        const final = finals[fx.id];
        if (!final) continue;
        const pred = p.group[fx.id];
        if (!pred?.pick) continue;
        const actual: MatchResult = { home: fx.home, away: fx.away, homeGoals: final.homeGoals, awayGoals: final.awayGoals };
        pts += scoreGroupPrediction(pred, actual);
        if (pred.homeGoals === final.homeGoals && pred.awayGoals === final.awayGoals) exactos += 1;
      }
      if (pts > 0) rows.push({ id: p.playerId, pts, exactos });
    }
    if (rows.length === 0) return null;
    rows.sort((a, b) => b.pts - a.pts || b.exactos - a.exactos);
    const top = rows[0];
    return { player: players.find(pp => pp.id === top.id) ?? null, pts: top.pts };
  }, [today, finals, allPicks, players]);

  // Position diff vs "before today": recompute punteros using actuals BUT
  // excluding today's fixtures, find current player's rank in that snapshot.
  // Positive number = climbed N spots today.
  const myPositionDiff = useMemo(() => {
    if (!currentPlayer || punteros.length === 0) return null;
    const todayIds = new Set(today.map(fx => fx.id));
    const rankNow = punteros.findIndex(p => p.id === currentPlayer.id);
    if (rankNow < 0) return null;
    // Build yesterday's scoring quickly (just total points, same tiebreakers
    // wouldn't fully reproduce, but it's an honest approximation for the chip).
    const yesterdayScores = allPicks.map(pp => {
      let pts = 0;
      for (const [fxId, pred] of Object.entries(pp.group)) {
        if (todayIds.has(fxId)) continue;
        const fx = allGroupFixtures().find(f => f.id === fxId);
        const final = fx ? finals[fxId] : undefined;
        if (!fx || !final || !pred?.pick) continue;
        const actual: MatchResult = { home: fx.home, away: fx.away, homeGoals: final.homeGoals, awayGoals: final.awayGoals };
        pts += scoreGroupPrediction(pred, actual);
      }
      return { id: pp.playerId, pts };
    }).sort((a, b) => b.pts - a.pts || a.id.localeCompare(b.id));
    const rankYesterday = yesterdayScores.findIndex(p => p.id === currentPlayer.id);
    if (rankYesterday < 0) return null;
    return rankYesterday - rankNow; // positive = climbed
  }, [currentPlayer, punteros, today, allPicks, finals]);

  // Who got each fixture right (for the mini avatar cluster below decided rows).
  const winnersByFx = useMemo(() => {
    const out: Record<string, import("@/data/players").Player[]> = {};
    for (const fx of today) {
      const final = finals[fx.id];
      if (!final) continue;
      const truth = actualPick({ home: fx.home, away: fx.away, homeGoals: final.homeGoals, awayGoals: final.awayGoals });
      const winners: import("@/data/players").Player[] = [];
      for (const p of allPicks) {
        const pl = players.find(pp => pp.id === p.playerId);
        if (!pl || pl.isBot) continue;
        if (p.group[fx.id]?.pick === truth) winners.push(pl);
      }
      out[fx.id] = winners;
    }
    return out;
  }, [today, finals, allPicks, players]);

  if (today.length === 0 || now === null) return null;

  return (
    <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: .5, delay: .1 }}
      className="glass rounded-3xl p-4 md:p-5">
      <div className="flex items-center justify-between mb-3 gap-2 flex-wrap">
        <div className="flex items-center gap-1.5 flex-wrap">
          <span className="chip"><CalendarDays size={12} /> {t("home.today.chip")}</span>
          {myStreakToday >= 2 && (
            <span
              className="inline-flex items-center gap-0.5 px-2 py-0.5 rounded-full text-[10px] font-extrabold uppercase tracking-wider tabular-nums"
              style={{ background: "color-mix(in srgb, #FF7F11 22%, transparent)", color: "#C2410C" }}
              title={`Racha: ${myStreakToday} aciertos al hilo hoy`}
            >
              <Flame size={10} /> {myStreakToday}
            </span>
          )}
          {myPositionDiff !== null && myPositionDiff !== 0 && myTodayTally && myTodayTally.decided > 0 && (
            <span
              className="inline-flex items-center gap-0.5 px-2 py-0.5 rounded-full text-[10px] font-extrabold uppercase tracking-wider tabular-nums"
              style={{
                background: myPositionDiff > 0 ? "color-mix(in srgb, var(--accent-mint) 22%, transparent)" : "color-mix(in srgb, #FF3B82 14%, transparent)",
                color: myPositionDiff > 0 ? "#059669" : "#BE123C",
              }}
              title={myPositionDiff > 0 ? `${t("home.today.posUp")} ${myPositionDiff} ${myPositionDiff > 1 ? t("home.today.posSpots") : t("home.today.posSpot")}` : `${t("home.today.posDown")} ${Math.abs(myPositionDiff)} ${Math.abs(myPositionDiff) > 1 ? t("home.today.posSpots") : t("home.today.posSpot")}`}
            >
              {myPositionDiff > 0 ? "▲" : "▼"} {Math.abs(myPositionDiff)}
            </span>
          )}
          {hottestToday && hottestToday.player && (
            <span
              className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded-full text-[10px] font-extrabold uppercase tracking-wider"
              style={{ background: "color-mix(in srgb, #D4AF37 20%, transparent)", color: "#854D0E" }}
              title={`Caliente hoy: ${hottestToday.player.name} con +${hottestToday.pts} pts`}
            >
              <Crown size={10} /> {hottestToday.player.name.split(" ")[0]} +{hottestToday.pts}
            </span>
          )}
        </div>
        <div className="flex items-center gap-2">
          {myTodayTally && myTodayTally.decided > 0 && (
            <span
              className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-extrabold uppercase tracking-wider tabular-nums"
              style={{
                background: myTodayTally.pts > 0 ? "color-mix(in srgb, var(--accent-mint) 22%, transparent)" : "var(--bg-tint)",
                color: myTodayTally.pts > 0 ? "#059669" : "var(--ink-muted)",
              }}
              title={`${myTodayTally.exactos} exactos · ${myTodayTally.hits} aciertos · ${myTodayTally.mamadas} mamadas`}
            >
              {myTodayTally.pts > 0 ? `+${myTodayTally.pts}` : myTodayTally.pts} {t("home.today.ptsToday")}
            </span>
          )}
          <span className="text-[10px] uppercase tracking-wider text-[var(--ink-muted)] tabular-nums">{today.length} {t("home.today.matches")}</span>
        </div>
      </div>
      <div className="space-y-2">
        {today.map(fx => {
          const live = liveById[fx.id];
          const final = finals[fx.id];
          const phase: "pre" | "live" | "final" = final ? "final" : live?.phase === "live" ? "live" : "pre";
          const homeTeam = TEAMS.find(t => t.code === fx.home);
          const awayTeam = TEAMS.find(t => t.code === fx.away);
          const canPick = !!currentPlayer && phase === "pre" && !isFixtureLocked(fx);
          const pred = myPicks?.group[fx.id];
          const verdict = verdictFor(pred, final, fx.home, fx.away);
          const probs = winProbabilities(fx.home, fx.away);
          const pickers = pickersByFx[fx.id] ?? { H: [], D: [], A: [] };
          const totalPicks = pickers.H.length + pickers.D.length + pickers.A.length;
          return (
            <div key={fx.id} className={`rounded-2xl overflow-hidden transition-all ${
              phase === "live" ? "ring-2 ring-[#FF3B82]/60 shadow-[0_0_20px_-4px_rgba(244,63,94,0.25)]" :
              phase === "final" ? "bg-[rgba(20,241,149,0.04)] ring-1 ring-[rgba(20,241,149,0.2)]" :
              "glass-strong"
            }`}>
              {/* Main row */}
              <Link
                href={phase === "live" ? `/partido/${fx.id}/live` : `/partido/${fx.id}`}
                className="flex items-center gap-3 px-3 py-3 hover:bg-[var(--bg-tint)] transition-colors"
              >
                {/* Status */}
                <div className="w-10 shrink-0 text-center">
                  {phase === "final" ? (
                    <span className="text-[10px] font-bold text-[#059669] uppercase leading-none">FT</span>
                  ) : phase === "live" ? (
                    <span className="text-[10px] font-bold text-[#FF3B82] flex flex-col items-center gap-0.5">
                      <span className="w-1.5 h-1.5 rounded-full bg-[#FF3B82] animate-pulse inline-block" />
                      <span>{live?.minute?.replace("'", "") || "·"}{"'"}</span>
                    </span>
                  ) : (
                    <div className="flex flex-col items-center gap-0.5">
                      <ViewerKickoffTime fx={fx} />
                      <CountdownChip kickoffMs={fixtureKickoffMs(fx)} />
                    </div>
                  )}
                </div>

                {/* Teams + Score */}
                <div className="flex-1 min-w-0 flex items-center gap-1.5">
                  {/* Home */}
                  <div className="flex items-center gap-1.5 flex-1 justify-end min-w-0">
                    <span className={`font-display font-bold text-sm truncate ${
                      phase !== "pre" && final && final.homeGoals > final.awayGoals ? "text-[var(--ink)]" :
                      phase !== "pre" && (final || phase === "live") ? "text-[var(--ink-muted)]" : ""
                    }`}>{fx.home}</span>
                    {homeTeam && (
                      <div className="relative w-7 h-7 rounded-lg overflow-hidden ring-1 ring-[var(--line)] shrink-0">
                        <Image src={flagUrl(homeTeam.iso2, 32)} alt="" fill sizes="28px" className="object-cover" unoptimized />
                      </div>
                    )}
                  </div>

                  {/* Score */}
                  <div className="flex items-center gap-0.5 shrink-0">
                    {(phase === "final" && final) || (phase === "live" && live) ? (
                      <>
                        <span className={`font-display font-black text-xl tabular-nums w-6 text-center leading-none ${phase === "live" ? "text-[#FF3B82]" : ""}`}>
                          {phase === "final" ? final!.homeGoals : live?.homeGoals ?? 0}
                        </span>
                        <span className="text-[var(--ink-muted)] font-bold text-sm">–</span>
                        <span className={`font-display font-black text-xl tabular-nums w-6 text-center leading-none ${phase === "live" ? "text-[#FF3B82]" : ""}`}>
                          {phase === "final" ? final!.awayGoals : live?.awayGoals ?? 0}
                        </span>
                      </>
                    ) : (
                      <span className="text-[var(--ink-muted)] font-bold text-sm px-2">vs</span>
                    )}
                  </div>

                  {/* Away */}
                  <div className="flex items-center gap-1.5 flex-1 min-w-0">
                    {awayTeam && (
                      <div className="relative w-7 h-7 rounded-lg overflow-hidden ring-1 ring-[var(--line)] shrink-0">
                        <Image src={flagUrl(awayTeam.iso2, 32)} alt="" fill sizes="28px" className="object-cover" unoptimized />
                      </div>
                    )}
                    <span className={`font-display font-bold text-sm truncate ${
                      phase !== "pre" && final && final.awayGoals > final.homeGoals ? "text-[var(--ink)]" :
                      phase !== "pre" && (final || phase === "live") ? "text-[var(--ink-muted)]" : ""
                    }`}>{fx.away}</span>
                  </div>
                </div>

                {/* Right: verdict / countdown / group */}
                <div className="flex flex-col items-end gap-1 shrink-0">
                  {verdict ? (
                    <span
                      className="px-1.5 py-0.5 rounded-md text-[9px] font-extrabold uppercase tracking-wider leading-none"
                      style={{
                        background: verdict.tone === "best" ? "color-mix(in srgb, #D4AF37 28%, transparent)" :
                                    verdict.tone === "good" ? "color-mix(in srgb, var(--accent-mint) 25%, transparent)" :
                                    "color-mix(in srgb, #FF3B82 18%, transparent)",
                        color: verdict.tone === "best" ? "#854D0E" : verdict.tone === "good" ? "#059669" : "#BE123C",
                      }}
                    >
                      {verdict.tone === "best" && "★ "}
                      {verdict.tone === "best" ? t("verdict.exact") : verdict.tone === "good" ? t("verdict.hit") : t("verdict.miss")}
                    </span>
                  ) : null}
                  <span className="text-[9px] text-[var(--ink-muted)] font-semibold leading-none">G{fx.group}</span>
                </div>
              </Link>

              {/* Probability fill bar */}
              {phase !== "final" && (
                <div className="px-3 pb-2">
                  <div className="h-1.5 rounded-full overflow-hidden flex bg-[var(--line)]">
                    <div className="transition-all duration-700" style={{ width: `${probs.home}%`, background: "#047857" }} />
                    <div className="transition-all duration-700" style={{ width: `${probs.draw}%`, background: "#94A3B8" }} />
                    <div className="transition-all duration-700" style={{ width: `${probs.away}%`, background: "#BE123C" }} />
                  </div>
                  <div className="flex justify-between mt-1 text-[9px] font-bold tabular-nums">
                    <span style={{ color: "#047857" }}>{fx.home} {probs.home}%</span>
                    <span className="text-[var(--ink-muted)]">X {probs.draw}%</span>
                    <span style={{ color: "#BE123C" }}>{probs.away}%</span>
                  </div>
                </div>
              )}

              {/* Pickers breakdown */}
              {totalPicks > 0 && (
                <div className="flex items-center justify-between gap-2 px-3 pb-2 text-[9px] tabular-nums">
                  <div className="flex items-start gap-2 flex-wrap min-w-0">
                    <PickersCluster label={fx.home} players={pickers.H} accent="#047857" />
                    <PickersCluster label="X" players={pickers.D} accent="#64748B" />
                    <PickersCluster label={fx.away} players={pickers.A} accent="#BE123C" />
                  </div>
                  <button
                    type="button"
                    onClick={() => setOverlayFxId(fx.id)}
                    aria-label="Ver detalle de votos y efectividad"
                    title="Ver detalle de votos y efectividad"
                    className="shrink-0 w-6 h-6 rounded-full grid place-items-center bg-[var(--bg-tint)] hover:bg-[var(--bg-strong,#fff)] hairline-strong text-[var(--ink-soft)] hover:text-[var(--ink)] transition-colors"
                  >
                    <BarChart3 size={11} />
                  </button>
                </div>
              )}

              {/* Inline pick buttons */}
              {canPick && (
                <InlinePicker fx={fx} playerId={currentPlayer!.id} probs={probs} />
              )}

              {/* Winners (final) */}
              {phase === "final" && (winnersByFx[fx.id]?.length ?? 0) > 0 && (
                <div className="flex items-center gap-1.5 px-3 pb-2">
                  <span className="text-[9px] uppercase tracking-wider text-[var(--ink-muted)] font-bold">{t("home.today.hits")}</span>
                  <div className="flex -space-x-1.5">
                    {winnersByFx[fx.id].slice(0, 4).map(w => (
                      <Link key={w.id} href={`/quiniela?view=${w.id}`} onClick={e => e.stopPropagation()} className="rounded-full ring-1 ring-white hover:scale-110 transition-transform inline-block">
                        <PlayerAvatar player={w} size={20} rounded="rounded-full" textClass="text-[8px]" tint={0.18} />
                      </Link>
                    ))}
                  </div>
                  {winnersByFx[fx.id].length > 4 && (
                    <span className="text-[9px] font-bold text-[var(--ink-muted)] tabular-nums">+{winnersByFx[fx.id].length - 4}</span>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>
      {currentPlayer && today.some(fx => !isFixtureLocked(fx) && !finals[fx.id]) && (
        <div className="mt-2 text-[10px] text-[var(--ink-muted)] text-center">
          {t("home.today.helper")}
        </div>
      )}
      <div className="mt-3 pt-3 border-t border-[var(--line)] flex items-center justify-between gap-2">
        <Link
          href="/leaderboard"
          className="flex-1 inline-flex items-center justify-center gap-2 px-3 py-2 rounded-xl bg-[var(--ink)] text-white text-xs font-bold tracking-wider hover:opacity-90 transition-opacity"
        >
          <BarChart3 size={14} /> {t("home.today.standings")}
        </Link>
        <Link
          href="/ranking"
          className="inline-flex items-center justify-center gap-2 px-3 py-2 rounded-xl hairline-strong bg-white text-[var(--ink-soft)] text-xs font-bold tracking-wider hover:text-[var(--ink)] transition-colors"
        >
          <Activity size={14} /> {t("home.today.teams")}
        </Link>
      </div>
      <PickersOverlay
        fxId={overlayFxId}
        onClose={() => setOverlayFxId(null)}
        pickersByFx={pickersByFx}
        accuracyByPlayer={accuracyByPlayer}
        allPicks={allPicks}
      />
    </motion.div>
  );
}

function PickersOverlay({
  fxId, onClose, pickersByFx, accuracyByPlayer, allPicks,
}: {
  fxId: string | null;
  onClose: () => void;
  pickersByFx: Record<string, { H: PlayerLite[]; D: PlayerLite[]; A: PlayerLite[] }>;
  accuracyByPlayer: Record<string, { hits: number; decided: number }>;
  allPicks: PlayerPredictions[];
}) {
  // Close on Escape; lock body scroll while open.
  useEffect(() => {
    if (!fxId) return;
    const onKey = (e: KeyboardEvent) => { if (e.key === "Escape") onClose(); };
    window.addEventListener("keydown", onKey);
    const prevOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => {
      window.removeEventListener("keydown", onKey);
      document.body.style.overflow = prevOverflow;
    };
  }, [fxId, onClose]);

  if (!fxId) return null;
  const fxIdSafe: string = fxId; // narrowed for closures
  const fx = allGroupFixtures().find(f => f.id === fxIdSafe);
  if (!fx) return null;
  const pickers = pickersByFx[fxIdSafe] ?? { H: [], D: [], A: [] };
  const homeTeam = TEAMS.find(t => t.code === fx.home);
  const awayTeam = TEAMS.find(t => t.code === fx.away);

  function row(player: PlayerLite, outcomeColor: string) {
    const acc = accuracyByPlayer[player.id] ?? { hits: 0, decided: 0 };
    const pct = acc.decided > 0 ? Math.round((acc.hits / acc.decided) * 100) : null;
    const pick = allPicks.find(p => p.playerId === player.id)?.group[fxIdSafe];
    const score = pick && typeof pick.homeGoals === "number" && typeof pick.awayGoals === "number"
      ? `${pick.homeGoals}-${pick.awayGoals}` : null;
    return (
      <div key={player.id} className="flex items-center gap-3 px-3 py-2 rounded-xl hover:bg-[var(--bg-tint)] transition-colors">
        <PlayerAvatar player={player} size={32} rounded="rounded-full" textClass="text-xs" tint={0.18} />
        <div className="flex-1 min-w-0">
          <div className="font-display font-bold text-sm truncate">{player.name}</div>
          <div className="text-[10px] text-[var(--ink-muted)] tabular-nums flex items-center gap-1.5">
            {score && <span className="font-bold" style={{ color: outcomeColor }}>{score}</span>}
            {pct !== null && (
              <>
                {score && <span>·</span>}
                <span>{acc.hits}/{acc.decided} aciertos</span>
                <span className="font-bold" style={{ color: pct >= 60 ? "#059669" : pct >= 40 ? "#D97706" : "#BE123C" }}>
                  {pct}%
                </span>
              </>
            )}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div
      role="dialog"
      aria-modal="true"
      className="fixed inset-0 z-[70] bg-black/60 backdrop-blur-sm grid place-items-center p-4"
      onClick={onClose}
    >
      <div
        onClick={e => e.stopPropagation()}
        className="bg-white rounded-3xl w-full max-w-md max-h-[85vh] overflow-y-auto shadow-2xl"
      >
        {/* Header */}
        <div className="sticky top-0 bg-white border-b border-[var(--line)] px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-2">
            {homeTeam && <Image src={flagUrl(homeTeam.iso2, 32)} alt="" width={20} height={14} className="rounded-sm object-cover" unoptimized />}
            <span className="font-display font-bold">{fx.home}</span>
            <span className="text-[var(--ink-muted)]">vs</span>
            <span className="font-display font-bold">{fx.away}</span>
            {awayTeam && <Image src={flagUrl(awayTeam.iso2, 32)} alt="" width={20} height={14} className="rounded-sm object-cover" unoptimized />}
          </div>
          <button type="button" onClick={onClose} aria-label="Cerrar" className="w-8 h-8 rounded-full grid place-items-center hover:bg-[var(--bg-tint)] text-[var(--ink-soft)]">
            <X size={18} />
          </button>
        </div>
        <div className="px-4 py-3 space-y-4">
          <Section title={`Gana ${fx.home}`} count={pickers.H.length} color="#047857">
            {pickers.H.length === 0
              ? <p className="text-xs text-[var(--ink-muted)] italic px-3 py-2">Nadie votó por esto</p>
              : pickers.H.map(p => row(p, "#047857"))}
          </Section>
          <Section title="Empate" count={pickers.D.length} color="#64748B">
            {pickers.D.length === 0
              ? <p className="text-xs text-[var(--ink-muted)] italic px-3 py-2">Nadie votó por esto</p>
              : pickers.D.map(p => row(p, "#64748B"))}
          </Section>
          <Section title={`Gana ${fx.away}`} count={pickers.A.length} color="#BE123C">
            {pickers.A.length === 0
              ? <p className="text-xs text-[var(--ink-muted)] italic px-3 py-2">Nadie votó por esto</p>
              : pickers.A.map(p => row(p, "#BE123C"))}
          </Section>
        </div>
      </div>
    </div>
  );
}

function Section({ title, count, color, children }: { title: string; count: number; color: string; children: React.ReactNode }) {
  return (
    <div>
      <div className="flex items-center justify-between mb-1.5 px-1">
        <h3 className="text-[10px] uppercase tracking-wider font-extrabold" style={{ color }}>{title}</h3>
        <span className="text-[10px] font-bold tabular-nums text-[var(--ink-muted)]">{count}</span>
      </div>
      <div className="space-y-0.5">{children}</div>
    </div>
  );
}

type PunteroRow = {
  id: string;
  name: string;
  emoji: string;
  accent: string;
  photoDataUrl?: string;
  score: number;
  exactHits: number;
  signHits: number;
  streak: number;
  pct: number;
};

function PunterosTop5({ rows, currentPlayerId }: { rows: PunteroRow[]; currentPlayerId?: string }) {
  const { t } = useLocale();
  // Crown only when #1 has a strict point lead over #2.
  const tiedAtTop = rows.length > 1 && rows[0].score === rows[1].score;
  const accentFor = (place: number) =>
    place === 1 ? "#D4AF37" : place === 2 ? "#C0C0C0" : place === 3 ? "#CD7F32" : "var(--ink-muted)";
  return (
    <div className="glass-strong rounded-3xl p-3 md:p-4 relative overflow-hidden">
      <div className="absolute -top-12 left-1/2 -translate-x-1/2 w-72 h-72 rounded-full blur-3xl opacity-20" style={{ background: "radial-gradient(closest-side, #D4AF37, transparent)" }} />
      <ol className="relative space-y-1.5">
        {rows.map((row, i) => {
          const place = i + 1;
          const isMe = currentPlayerId === row.id;
          const accent = accentFor(place);
          const aciertos = row.signHits + row.exactHits;
          const showCrown = place === 1 && !tiedAtTop;
          const rowClassName = `flex items-center gap-3 px-3 py-2.5 rounded-2xl border transition ${
            isMe
              ? "bg-[var(--accent-violet)]/15 border-[var(--accent-violet)]/50 text-[var(--ink)]"
              : "bg-[var(--bg-tint)] border-[var(--line)] hover:bg-[var(--bg-elev)] text-[var(--ink)]"
          }`;
          const rowInner = (
            <>
              <div
                className="font-display font-extrabold text-lg md:text-xl tabular-nums w-7 text-center shrink-0"
                style={{ color: accent }}
              >
                {showCrown ? <Crown size={18} className="mx-auto" /> : place}
              </div>
              <PlayerAvatar player={row} size={36} rounded="rounded-xl" textClass="text-base" tint={0.15} enableLightbox />
              <div className="min-w-0 flex-1">
                <div className="flex items-center gap-2">
                  <span className="font-display font-bold text-sm md:text-base truncate">{row.name}</span>
                  {isMe && (
                    <span className="text-[9px] font-extrabold uppercase tracking-wider px-1.5 py-0.5 rounded-full bg-[var(--accent-violet)] text-white shrink-0">
                      {t("home.punteros.you")}
                    </span>
                  )}
                  {row.streak >= 2 && (
                    <span
                      className="text-[10px] font-extrabold uppercase tracking-wider px-1.5 py-0.5 rounded-full text-white shrink-0 flex items-center gap-0.5"
                      style={{ background: "linear-gradient(90deg, #FF6A00, #FF3B82)" }}
                      title={`${row.streak} aciertos al hilo`}
                    >
                      <Flame size={10} /> {row.streak}
                    </span>
                  )}
                </div>
                <div className="text-[11px] text-[var(--ink-muted)] tabular-nums">
                  {aciertos > 0 ? `${aciertos} ac · ${row.exactHits} ex` : t("home.punteros.noHitsYet")}
                </div>
              </div>
              <div className="text-right shrink-0">
                <div className="font-display font-bold text-xl md:text-2xl tabular-nums leading-none" style={{ color: place <= 3 ? accent : "var(--ink)" }}>
                  {row.score}
                </div>
                <div className="text-[9px] uppercase tracking-wider text-[var(--ink-muted)] mt-0.5">{t("home.scoring.pts")}</div>
              </div>
            </>
          );
          return (
            <li key={row.id} className="list-none">
              {isMe ? (
                <div className={rowClassName}>{rowInner}</div>
              ) : (
                <Link
                  href={`/quiniela?view=${row.id}`}
                  className={rowClassName}
                  aria-label={`Ver quiniela de ${row.name}`}
                >
                  {rowInner}
                </Link>
              )}
            </li>
          );
        })}
      </ol>
      <div className="relative mt-3 text-[10px] md:text-[11px] text-[var(--ink-muted)] leading-snug px-1">
        <strong className="text-[var(--ink-soft)]">{t("home.punteros.tiebreak")}</strong>{" "}
        {t("home.punteros.tiebreak.copy")} 🔥.
      </div>
    </div>
  );
}

function Stat({ icon, value, label }: { icon: React.ReactNode; value: string; label: string }) {
  return (
    <div className="flex items-center gap-3 min-w-0">
      <div className="w-10 h-10 rounded-xl grid place-items-center bg-[var(--bg-tint)] text-[var(--ink)] shrink-0">{icon}</div>
      <div className="min-w-0">
        <div className="font-display text-xl md:text-2xl font-bold leading-none truncate">{value}</div>
        <div className="text-xs text-[var(--ink-muted)] mt-1 truncate">{label}</div>
      </div>
    </div>
  );
}
