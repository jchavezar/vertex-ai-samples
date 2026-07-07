"use client";

// Full-screen LIVE match dashboard. Polls /api/match-live/[fixtureId] every
// ~10s while the match is in-progress. Fires a celebration overlay when a new
// goal play appears since the last poll. Falls back to the regular pre/post
// summary at /partido/[fixtureId] when the match isn't live.

import { use, useCallback, useEffect, useMemo, useRef, useState } from "react";
import Link from "next/link";
import Image from "next/image";
import { notFound } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronLeft, Radio, Flag, Trophy, AlertTriangle, Repeat, Sparkles } from "lucide-react";

import { allGroupFixtures } from "@/data/groups";
import { TEAMS_BY_CODE, flagUrl } from "@/data/teams";
import { PlayerAvatar } from "@/components/PlayerAvatar";
import { useAllPicksByFixture } from "@/lib/all-picks";
import type { LivePlay, LiveResponse, LiveStat } from "@/app/api/match-live/[fixtureId]/route";

type Params = { fixtureId: string };

const POLL_MS_LIVE = 10_000;       // while state === "in" | "halftime"
const POLL_MS_IDLE = 60_000;       // while state === "pre" | "post"
const CELEBRATION_MS = 3200;

export default function LiveMatchPage({ params }: { params: Promise<Params> }) {
  const { fixtureId } = use(params);
  const fx = useMemo(() => allGroupFixtures().find(f => f.id === fixtureId), [fixtureId]);
  if (!fx) notFound();

  const home = TEAMS_BY_CODE[fx.home];
  const away = TEAMS_BY_CODE[fx.away];

  const [data, setData] = useState<LiveResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const lastGoalRef = useRef<string | null>(null);
  const [celebration, setCelebration] = useState<{ scorer?: string; teamAbbr?: string; key: string } | null>(null);

  const fetchOnce = useCallback(async (signal?: AbortSignal) => {
    try {
      const res = await fetch(`/api/match-live/${encodeURIComponent(fixtureId)}`, { cache: "no-store", signal });
      const json: LiveResponse = await res.json();
      setData(json);
      setError(null);

      // Goal-celebration trigger: only fire after the first successful payload
      // (so we don't celebrate the historical last goal on page load).
      const nextGoalId = json.lastGoalId ?? null;
      const prev = lastGoalRef.current;
      if (prev === null) {
        lastGoalRef.current = nextGoalId;
      } else if (nextGoalId && nextGoalId !== prev) {
        const goalPlay = json.plays?.find(p => p.id === nextGoalId);
        setCelebration({
          scorer: goalPlay?.athleteName,
          teamAbbr: goalPlay?.teamAbbr,
          key: nextGoalId,
        });
        lastGoalRef.current = nextGoalId;
      }
    } catch (e) {
      if ((e as { name?: string })?.name === "AbortError") return;
      setError(e instanceof Error ? e.message : String(e));
    }
  }, [fixtureId]);

  useEffect(() => {
    const ac = new AbortController();
    fetchOnce(ac.signal);
    return () => ac.abort();
  }, [fetchOnce]);

  useEffect(() => {
    const live = data?.state === "in" || data?.state === "halftime";
    const ms = live ? POLL_MS_LIVE : POLL_MS_IDLE;
    const id = setInterval(() => { fetchOnce(); }, ms);
    return () => clearInterval(id);
  }, [data?.state, fetchOnce]);

  // Auto-dismiss the goal overlay
  useEffect(() => {
    if (!celebration) return;
    const t = setTimeout(() => setCelebration(null), CELEBRATION_MS);
    return () => clearTimeout(t);
  }, [celebration]);

  const homeColor = `#${(data?.teams?.home.color || "0EA5E9").replace(/^#/, "")}`;
  const awayColor = `#${(data?.teams?.away.color || "EF4444").replace(/^#/, "")}`;
  const state = data?.state;
  const isLive = state === "in" || state === "halftime";

  const homeName = home?.name ?? fx.home;
  const awayName = away?.name ?? fx.away;
  const homeScore = data?.score?.home ?? 0;
  const awayScore = data?.score?.away ?? 0;

  const clockLabel = useMemo(() => {
    if (state === "halftime") return "HT";
    if (state === "post") return "FT";
    if (state === "pre") return "Pre";
    return data?.clock || "—";
  }, [state, data?.clock]);

  const { byFixture: picksByFixture } = useAllPicksByFixture();
  const picks = picksByFixture[fx.id] ?? { H: [], D: [], A: [] };

  return (
    <main className="min-h-screen bg-[#0a0a14] text-white relative overflow-hidden">
      {/* Animated radial gradient backdrop */}
      <div className="pointer-events-none fixed inset-0 -z-10">
        <div className="absolute inset-0 opacity-40"
          style={{ background: `radial-gradient(circle at 18% 12%, ${homeColor}55, transparent 50%), radial-gradient(circle at 82% 88%, ${awayColor}55, transparent 50%)` }} />
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_-10%,rgba(255,255,255,0.06),transparent_60%)]" />
      </div>

      {/* Top bar */}
      <div className="px-4 md:px-8 pt-4 pb-2 flex items-center justify-between text-[11px]">
        <Link href="/" className="inline-flex items-center gap-1 text-white/60 hover:text-white">
          <ChevronLeft size={14} /> Inicio
        </Link>
        <Link href={`/partido/${fx.id}`} className="text-white/60 hover:text-white uppercase tracking-wider">
          Ver resumen
        </Link>
      </div>

      {/* HERO */}
      <section className="px-4 md:px-8 pt-2 pb-6">
        <div className="flex items-center justify-center gap-2 mb-4">
          {isLive ? (
            <span className="inline-flex items-center gap-1.5 text-[10px] uppercase tracking-[0.22em] font-bold text-[#FF3B82]">
              <span className="relative inline-flex w-2 h-2">
                <span className="absolute inset-0 rounded-full bg-[#FF3B82] animate-ping opacity-75" />
                <span className="relative rounded-full w-2 h-2 bg-[#FF3B82]" />
              </span>
              En vivo · Grupo {fx.group} · J{fx.matchday}
            </span>
          ) : state === "post" ? (
            <span className="text-[10px] uppercase tracking-[0.22em] font-bold text-white/60">
              Finalizado · Grupo {fx.group} · J{fx.matchday}
            </span>
          ) : (
            <span className="text-[10px] uppercase tracking-[0.22em] font-bold text-white/60">
              Próximamente · Grupo {fx.group} · J{fx.matchday}
            </span>
          )}
        </div>

        <div className="grid grid-cols-[1fr_auto_1fr] items-center gap-4 md:gap-10 max-w-5xl mx-auto">
          <HeroTeam name={homeName} iso2={home?.iso2 ?? ""} code={fx.home} accent={homeColor} align="left" />
          <div className="flex flex-col items-center">
            <div className="font-display font-extrabold tabular-nums leading-none text-[64px] sm:text-[88px] md:text-[120px]"
              style={{ textShadow: "0 6px 36px rgba(0,0,0,0.55)" }}
            >
              {homeScore}<span className="text-white/30 mx-2">–</span>{awayScore}
            </div>
            <div className="mt-3 inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/10 border border-white/10 text-[11px] font-bold tabular-nums">
              {clockLabel}
              {data?.period && state === "in" ? <span className="text-white/60">· {data.period === 1 ? "1T" : data.period === 2 ? "2T" : `P${data.period}`}</span> : null}
            </div>
            {data?.statusText && <div className="mt-1.5 text-[10px] uppercase tracking-wider text-white/50">{data.statusText}</div>}
          </div>
          <HeroTeam name={awayName} iso2={away?.iso2 ?? ""} code={fx.away} accent={awayColor} align="right" />
        </div>

        <div className="mt-5 text-center text-[11px] text-white/50">
          {fx.venue} · {fx.city}
        </div>
        {error && (
          <div className="mt-3 mx-auto max-w-md text-center text-[11px] text-amber-300/80 inline-flex items-center justify-center gap-1.5">
            <AlertTriangle size={12} /> Sin contacto con el feed: {error}
          </div>
        )}
      </section>

      {/* Stats + Timeline */}
      <section className="px-4 md:px-8 pb-12 max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-[1.1fr_1fr] gap-5">
        {/* Stats panel */}
        <div className="rounded-3xl bg-white/[0.04] border border-white/10 backdrop-blur-sm p-5 md:p-6">
          <h2 className="text-[11px] uppercase tracking-[0.2em] text-white/60 font-bold mb-4 inline-flex items-center gap-1.5">
            <Sparkles size={12} /> Estadísticas
          </h2>
          {data?.stats && data.stats.length > 0 ? (
            <div className="space-y-3.5">
              {data.stats.map((s) => (
                <StatRow key={s.name} s={s} homeColor={homeColor} awayColor={awayColor} />
              ))}
            </div>
          ) : (
            <div className="text-[12px] text-white/40 italic py-6 text-center">
              {state === "pre" ? "El partido aún no comienza." : "Las estadísticas aparecerán cuando ESPN las publique."}
            </div>
          )}

          {/* Picks-overlay: lo que apostaron los charales para este partido */}
          <div className="mt-6 pt-5 border-t border-white/10">
            <h3 className="text-[11px] uppercase tracking-[0.2em] text-white/60 font-bold mb-3 inline-flex items-center gap-1.5">
              <Trophy size={12} /> Charales · cómo votaron
            </h3>
            <PickColumns
              homeName={homeName}
              awayName={awayName}
              picks={picks}
              homeColor={homeColor}
              awayColor={awayColor}
            />
          </div>
        </div>

        {/* Timeline */}
        <div className="rounded-3xl bg-white/[0.04] border border-white/10 backdrop-blur-sm p-5 md:p-6">
          <h2 className="text-[11px] uppercase tracking-[0.2em] text-white/60 font-bold mb-4 inline-flex items-center gap-1.5">
            <Radio size={12} /> Minuto a minuto
          </h2>
          {data?.plays && data.plays.length > 0 ? (
            <ul className="space-y-2 max-h-[640px] overflow-y-auto pr-1 -mr-1">
              <AnimatePresence initial={false}>
                {data.plays.map((p) => (
                  <PlayRow key={p.id} play={p} homeAbbr={fx.home} awayAbbr={fx.away} homeColor={homeColor} awayColor={awayColor} />
                ))}
              </AnimatePresence>
            </ul>
          ) : (
            <div className="text-[12px] text-white/40 italic py-6 text-center">
              {isLive ? "Esperando jugadas del feed…" : state === "pre" ? "El partido aún no comienza." : "Sin jugadas reportadas."}
            </div>
          )}
        </div>
      </section>

      {/* Goal celebration overlay */}
      <AnimatePresence>
        {celebration && (
          <motion.div
            key={celebration.key}
            initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="fixed inset-0 z-50 flex items-center justify-center pointer-events-none"
          >
            <div className="absolute inset-0 bg-black/70" />
            <ConfettiBurst color={celebration.teamAbbr === fx.away ? awayColor : homeColor} />
            <div className="relative text-center px-4">
              <motion.div
                initial={{ scale: 0.4, y: 30, opacity: 0 }}
                animate={{ scale: 1, y: 0, opacity: 1 }}
                exit={{ scale: 1.4, opacity: 0 }}
                transition={{ type: "spring", stiffness: 220, damping: 14 }}
                className="font-display font-extrabold leading-none tracking-tighter"
                style={{
                  fontSize: "min(28vw, 220px)",
                  color: celebration.teamAbbr === fx.away ? awayColor : homeColor,
                  textShadow: "0 12px 60px rgba(0,0,0,0.7)",
                }}
              >
                ¡GOOOL!
              </motion.div>
              {celebration.scorer && (
                <motion.div
                  initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.18 }}
                  className="mt-4 font-display text-2xl md:text-4xl text-white"
                >
                  {celebration.scorer}
                </motion.div>
              )}
              {celebration.teamAbbr && (
                <div className="mt-1 text-[10px] uppercase tracking-[0.25em] text-white/70">{celebration.teamAbbr}</div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </main>
  );
}

function HeroTeam({ name, iso2, code, accent, align }: { name: string; iso2: string; code: string; accent: string; align: "left" | "right" }) {
  return (
    <div className={`flex ${align === "right" ? "flex-row-reverse text-right" : "flex-row text-left"} items-center gap-3 md:gap-5 min-w-0`}>
      {iso2 && (
        <Link href={`/equipos/${code}`} className="shrink-0 rounded-2xl overflow-hidden border border-white/15 shadow-[0_10px_28px_-12px_rgba(0,0,0,0.6)] ring-2 hover:opacity-90 transition-opacity"
          style={{ boxShadow: `0 0 0 2px ${accent}55` }}
        >
          <Image src={flagUrl(iso2, 320)} alt={name} width={120} height={80} className="object-cover w-[80px] h-[56px] md:w-[120px] md:h-[80px]" unoptimized />
        </Link>
      )}
      <Link href={`/equipos/${code}`} className={`min-w-0 hover:opacity-90 transition-opacity ${align === "right" ? "text-right" : "text-left"}`}>
        <div className="font-display font-extrabold text-xl md:text-3xl leading-tight truncate">{name}</div>
        <div className="text-[10px] uppercase tracking-[0.22em] text-white/50 mt-1">
          <span className="inline-block w-2 h-2 rounded-full mr-1.5 align-middle" style={{ background: accent }} />
          {align === "right" ? "Visitante" : "Local"}
        </div>
      </Link>
    </div>
  );
}

function StatRow({ s, homeColor, awayColor }: { s: LiveStat; homeColor: string; awayColor: string }) {
  // For numeric stats we render a comparative bar. Strings (e.g. "55%") still
  // render OK as labels even if we can't proportion the bar.
  const hNum = toNumber(s.home);
  const aNum = toNumber(s.away);
  const total = hNum + aNum;
  const hPct = total > 0 ? hNum / total : 0.5;
  const aPct = total > 0 ? aNum / total : 0.5;

  return (
    <div>
      <div className="flex items-center justify-between text-[11px] font-bold tabular-nums">
        <motion.span
          key={`h-${s.home}`}
          initial={{ scale: 1.25, color: "#fff" }}
          animate={{ scale: 1, color: "rgba(255,255,255,0.95)" }}
          transition={{ duration: 0.4 }}
        >
          {s.home}
        </motion.span>
        <span className="text-[10px] uppercase tracking-[0.18em] text-white/55 font-semibold">{s.label}</span>
        <motion.span
          key={`a-${s.away}`}
          initial={{ scale: 1.25, color: "#fff" }}
          animate={{ scale: 1, color: "rgba(255,255,255,0.95)" }}
          transition={{ duration: 0.4 }}
        >
          {s.away}
        </motion.span>
      </div>
      <div className="mt-1.5 h-2 rounded-full overflow-hidden bg-white/10 flex">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${hPct * 100}%` }}
          transition={{ duration: 0.6, ease: "easeOut" }}
          style={{ background: homeColor }}
        />
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${aPct * 100}%` }}
          transition={{ duration: 0.6, ease: "easeOut" }}
          style={{ background: awayColor }}
        />
      </div>
    </div>
  );
}

function toNumber(v: string | number): number {
  if (typeof v === "number") return v;
  const cleaned = v.replace(/[^\d.]/g, "");
  const n = Number(cleaned);
  return Number.isFinite(n) ? n : 0;
}

function PlayRow({ play, homeAbbr, awayAbbr, homeColor, awayColor }: {
  play: LivePlay;
  homeAbbr: string;
  awayAbbr: string;
  homeColor: string;
  awayColor: string;
}) {
  const isGoal = !!play.scoringPlay || /goal/i.test(play.typeText || "");
  const isYellow = /yellow/i.test(play.typeText || "");
  const isRed = /red/i.test(play.typeText || "");
  const isSub = /substitut/i.test(play.typeText || "");
  const sideColor = play.teamAbbr === awayAbbr ? awayColor : play.teamAbbr === homeAbbr ? homeColor : "rgba(255,255,255,0.4)";

  return (
    <motion.li
      layout
      initial={{ opacity: 0, y: -6 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25 }}
      className={`rounded-2xl px-3 py-2.5 flex items-start gap-3 border ${isGoal ? "bg-white/[0.07] border-white/20" : "bg-white/[0.02] border-white/5"}`}
      style={isGoal ? { boxShadow: `inset 0 0 0 1px ${sideColor}66` } : undefined}
    >
      <div className="shrink-0 w-12 text-right">
        <span className="text-[11px] font-bold tabular-nums text-white/85">{play.minute || "—"}</span>
      </div>
      <div className="shrink-0 w-6 h-6 rounded-full grid place-items-center" style={{ background: `${sideColor}22`, color: sideColor }}>
        {isGoal ? <Trophy size={12} /> : isYellow || isRed ? <Flag size={12} /> : isSub ? <Repeat size={12} /> : <Sparkles size={12} />}
      </div>
      <div className="min-w-0 flex-1">
        <div className="text-[12px] leading-snug">
          {isGoal && <span className="font-extrabold mr-1" style={{ color: sideColor }}>GOL</span>}
          {play.athleteName && <span className="font-semibold">{play.athleteName}</span>}
          {play.athleteName && play.text ? " · " : ""}
          <span className="text-white/75">{play.text || play.typeText || "Jugada"}</span>
        </div>
        {play.teamAbbr && (
          <div className="text-[9px] uppercase tracking-[0.18em] text-white/40 mt-0.5">{play.teamAbbr}</div>
        )}
      </div>
    </motion.li>
  );
}

function PickColumns({ homeName, awayName, picks, homeColor, awayColor }: {
  homeName: string;
  awayName: string;
  picks: { H: Array<{ id: string; name: string; emoji: string; accent: string; photoDataUrl?: string }>; D: typeof picks.H; A: typeof picks.H };
  homeColor: string;
  awayColor: string;
}) {
  const total = picks.H.length + picks.D.length + picks.A.length;
  if (total === 0) {
    return <div className="text-[11px] text-white/40 italic py-3 text-center">Nadie del grupo votó este partido.</div>;
  }
  const drawColor = "#a855f7";
  return (
    <div className="grid grid-cols-3 gap-2">
      <PickColumn label={homeName} small="Local" players={picks.H} color={homeColor} />
      <PickColumn label="Empate"   small="X"     players={picks.D} color={drawColor} />
      <PickColumn label={awayName} small="Visit" players={picks.A} color={awayColor} />
    </div>
  );
}

function PickColumn({ label, small, players, color }: {
  label: string;
  small: string;
  players: Array<{ id: string; name: string; emoji: string; accent: string; photoDataUrl?: string }>;
  color: string;
}) {
  return (
    <div className="rounded-2xl bg-white/[0.03] border border-white/10 p-2.5">
      <div className="flex items-center justify-between mb-1.5">
        <span className="text-[9px] uppercase tracking-[0.18em] font-extrabold" style={{ color }}>{small}</span>
        <span className="text-[11px] font-bold tabular-nums">{players.length}</span>
      </div>
      <div className="text-[10px] text-white/55 truncate font-medium mb-2">{label}</div>
      {players.length === 0 ? (
        <div className="text-[10px] text-white/30 italic py-1">—</div>
      ) : (
        <div className="flex flex-wrap gap-1.5">
          {players.map(p => (
            <div key={p.id} title={p.name}>
              <PlayerAvatar player={p} size={24} rounded="rounded-full" textClass="text-[10px]" tint={0.18} />
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// Lightweight CSS-only confetti — no extra dep, no canvas.
function ConfettiBurst({ color }: { color: string }) {
  // 32 streamers fanning outward
  const pieces = Array.from({ length: 32 });
  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none">
      {pieces.map((_, i) => {
        const angle = (i / pieces.length) * Math.PI * 2;
        const dist = 240 + Math.random() * 360;
        const dx = Math.cos(angle) * dist;
        const dy = Math.sin(angle) * dist;
        const delay = Math.random() * 0.2;
        const dur = 1.4 + Math.random() * 0.7;
        const bg = i % 3 === 0 ? color : i % 3 === 1 ? "#ffffff" : "#FFD400";
        return (
          <motion.div
            key={i}
            initial={{ x: 0, y: 0, opacity: 1, rotate: 0 }}
            animate={{ x: dx, y: dy, opacity: 0, rotate: 720 }}
            transition={{ duration: dur, delay, ease: "easeOut" }}
            className="absolute top-1/2 left-1/2 w-2 h-3 rounded-sm"
            style={{ background: bg, marginLeft: -4, marginTop: -6 }}
          />
        );
      })}
    </div>
  );
}
