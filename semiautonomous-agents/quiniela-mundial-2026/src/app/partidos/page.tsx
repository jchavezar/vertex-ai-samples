"use client";

import Image from "next/image";
import Link from "next/link";
import { motion, AnimatePresence } from "framer-motion";
import { useEffect, useMemo, useRef, useState } from "react";
import {
  Activity, CalendarDays, MapPin, Radio, RefreshCw, Tv2, AlertCircle, Sparkles, Swords, Trophy,
} from "lucide-react";
import { getTournamentPhase } from "@/lib/tournament-phase";
import { getKnockoutEspnEvents } from "@/lib/espn-knockout-adapter";
import { normalizeAbbr, type EspnEvent } from "@/lib/espn";
import { TEAMS, flagUrl } from "@/data/teams";
import { KickoffCountdown } from "@/components/KickoffCountdown";
import { useScoreboard, getScoreboard } from "@/lib/scoreboard-cache";
import { allGroupFixtures } from "@/data/groups";
import { useFixtureProbs } from "@/lib/probabilities-client";
import { ProbabilityBar } from "@/components/ProbabilityBar";
import { usePlayer } from "@/lib/player-context";
import { loadPredictions, savePredictions, firePickToServer, type Pick1X2 } from "@/lib/predictions";

type Section = "live" | "today" | "upcoming" | "results";

function pickSectionFor(events: EspnEvent[] | undefined): Section {
  if (!events?.length) return "upcoming";
  const now = Date.now();
  const startOfToday = new Date(); startOfToday.setHours(0, 0, 0, 0);
  const endOfToday = new Date(startOfToday); endOfToday.setDate(endOfToday.getDate() + 1);
  let live = 0, today = 0;
  for (const e of events) {
    const t = new Date(e.date).getTime();
    if (e.status.type.state === "in") live++;
    else if (e.status.type.state !== "post" && t >= startOfToday.getTime() && t < endOfToday.getTime()) today++;
  }
  if (live) return "live";
  if (today) return "today";
  return "upcoming";
}

export default function PartidosPage() {
  const { data, loading, fetchedAt, refresh } = useScoreboard();
  const { byFixture: fxProbs, loading: probsLoading } = useFixtureProbs();
  // Pick the right tab synchronously from cached scoreboard so first paint
  // already lands on Live / Hoy when applicable — no flash from "upcoming".
  const [section, setSection] = useState<Section>(() => pickSectionFor(getScoreboard().data?.events));
  const userTouched = useRef(false);
  const handleTab = (s: Section) => { userTouched.current = true; setSection(s); };
  const error = !data && !loading && fetchedAt === 0 ? "No se pudo cargar" : null;

  const fxByPair = useMemo(() => {
    const m = new Map<string, string>();
    for (const fx of allGroupFixtures()) {
      m.set(`${fx.home}-${fx.away}-${fx.date}`, fx.id);
      m.set(`${fx.away}-${fx.home}-${fx.date}`, fx.id);
    }
    return m;
  }, []);

  function resolveFixtureId(e: EspnEvent): string | undefined {
    const c = e.competitions[0];
    const h = c.competitors.find(cp => cp.homeAway === "home");
    const a = c.competitors.find(cp => cp.homeAway === "away");
    if (!h || !a) return undefined;
    const hCode = normalizeAbbr(h.team.abbreviation);
    const aCode = normalizeAbbr(a.team.abbreviation);
    const cdmxDate = new Date(e.date).toLocaleDateString("en-CA", { timeZone: "America/Mexico_City" });
    return fxByPair.get(`${hCode}-${aCode}-${cdmxDate}`) ?? fxByPair.get(`${hCode}-${aCode}-${e.date.slice(0, 10)}`);
  }

  const buckets = useMemo(() => {
    const now = Date.now();
    const startOfToday = new Date(); startOfToday.setHours(0, 0, 0, 0);
    const endOfToday = new Date(startOfToday); endOfToday.setDate(endOfToday.getDate() + 1);

    const live: EspnEvent[] = [];
    const today: EspnEvent[] = [];
    const upcoming: EspnEvent[] = [];
    const results: EspnEvent[] = [];

    const existingIds = new Set<string>();
    const allEvents: EspnEvent[] = [...(data?.events || [])];
    for (const e of allEvents) existingIds.add(e.id);

    const syntheticKnockouts = getKnockoutEspnEvents(existingIds, now);
    allEvents.push(...syntheticKnockouts);

    for (const e of allEvents) {
      const t = new Date(e.date).getTime();
      const state = e.status.type.state;
      if (state === "in") {
        live.push(e);
      } else if (state === "post") {
        results.push(e);
      } else {
        if (t >= startOfToday.getTime() && t < endOfToday.getTime()) {
          today.push(e);
        }
        if (t > now) {
          upcoming.push(e);
        }
      }
    }
    upcoming.sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());
    results.sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());
    return { live, today, upcoming, results };
  }, [data]);

  // Auto-pick best initial section once data loads, but ONLY if the user
  // hasn't manually selected a tab. Without this guard, the periodic 30s
  // scoreboard refresh would yank them back to "live"/"today" mid-browse.
  useEffect(() => {
    if (!data || userTouched.current) return;
    setSection(pickSectionFor(data.events));
  }, [data]);

  const list = buckets[section];

  return (
    <div className="bg-canvas">
      {/* Header */}
      <section className="container-app pt-8 md:pt-12 pb-4">
        <div className="flex items-center justify-between gap-4 flex-wrap">
          <div>
            <span className="chip mb-3">
              <span className={`w-1.5 h-1.5 rounded-full ${buckets.live.length ? "bg-[#FF3B82] animate-pulse" : "bg-[var(--ink-muted)]"}`} />
              {buckets.live.length ? `${buckets.live.length} en vivo` : "Sin partidos en vivo"}
            </span>
            <h1 className="font-display text-3xl md:text-6xl font-bold leading-tight">
              Marcadores <span className="grad-text">en tiempo real</span>
            </h1>
            <p className="mt-2 text-sm md:text-base text-[var(--ink-soft)]">Datos directos de ESPN · actualiza cada 45 seg.</p>
          </div>
          <button onClick={() => refresh(true)} disabled={loading} className="btn btn-ghost">
            <RefreshCw size={14} className={loading ? "animate-spin" : ""} /> Actualizar
          </button>
        </div>
      </section>

      {/* Tabs */}
      <section className="container-app pt-2 pb-4">
        <div className="glass-strong rounded-full p-1 flex gap-1 overflow-x-auto max-w-full no-scrollbar">
          <Tab id="live" active={section === "live"} onClick={() => handleTab("live")} count={buckets.live.length} icon={<Radio size={13} />} label="En vivo" />
          <Tab id="today" active={section === "today"} onClick={() => handleTab("today")} count={buckets.today.length} icon={<Activity size={13} />} label="Hoy" />
          <Tab id="upcoming" active={section === "upcoming"} onClick={() => handleTab("upcoming")} count={buckets.upcoming.length} icon={<CalendarDays size={13} />} label="Próximos" />
          <Tab id="results" active={section === "results"} onClick={() => handleTab("results")} count={buckets.results.length} icon={<Tv2 size={13} />} label="Resultados" />
        </div>
      </section>

      {/* Error / empty */}
      {error && (
        <div className="container-app pb-4">
          <div className="glass rounded-2xl p-4 flex items-center gap-3 text-sm">
            <AlertCircle size={16} className="text-[var(--accent-coral)]" />
            <span><strong>ESPN no respondió:</strong> {error}</span>
          </div>
        </div>
      )}

      {/* List */}
      <section className="container-app pb-20">
        {loading && !data ? (
          <SkeletonGrid />
        ) : list.length === 0 ? (
          <EmptyState section={section} hint={fetchedAt ? new Date(fetchedAt).toLocaleTimeString() : undefined} />
        ) : (
          <div className="grid lg:grid-cols-2 gap-3">
            <AnimatePresence mode="popLayout">
              {list.map((e, idx) => {
                const fxId = resolveFixtureId(e);
                const entry = fxId ? fxProbs[fxId] : undefined;
                return (
                  <MatchCard
                    key={e.id}
                    event={e}
                    delay={idx * 0.03}
                    probs={entry?.probs ?? null}
                    probsLoading={probsLoading && !entry}
                    fixtureId={fxId}
                  />
                );
              })}
            </AnimatePresence>
          </div>
        )}
      </section>
    </div>
  );
}

function Tab({ active, onClick, label, count, icon }: {
  id: string; active: boolean; onClick: () => void; label: string; count: number; icon: React.ReactNode;
}) {
  return (
    <button onClick={onClick} className={`shrink-0 whitespace-nowrap px-2.5 sm:px-3 py-1.5 rounded-full text-xs sm:text-sm font-semibold transition-colors flex items-center gap-1 sm:gap-1.5 ${active ? "bg-[var(--ink)] text-[var(--bg)] shadow-sm font-bold" : "text-[var(--ink-soft)] hover:text-[var(--ink)]"}`}>
      <span className="hidden sm:inline-flex">{icon}</span> {label}
      {count > 0 && (
        <span className={`hidden sm:inline-flex text-[10px] tabular-nums rounded-full px-1.5 py-0.5 ${active ? "bg-[var(--bg)] text-[var(--ink)]" : "bg-[var(--bg-tint)] text-[var(--ink)]"}`}>
          {count}
        </span>
      )}
    </button>
  );
}

function MatchCard({ event, delay, probs, probsLoading, fixtureId }: {
  event: EspnEvent;
  delay: number;
  probs?: { H: number; D: number; A: number } | null;
  probsLoading?: boolean;
  fixtureId?: string;
}) {
  const comp = event.competitions[0];
  const home = comp.competitors.find(c => c.homeAway === "home")!;
  const away = comp.competitors.find(c => c.homeAway === "away")!;
  const live = event.status.type.state === "in";
  const finished = event.status.type.state === "post";
  const upcoming = event.status.type.state === "pre";

  const hTeam = TEAMS.find(t => t.code === home.team.abbreviation);
  const aTeam = TEAMS.find(t => t.code === away.team.abbreviation);

  const date = new Date(event.date);
  const dateLabel = date.toLocaleDateString("es-MX", { weekday: "short", day: "numeric", month: "short" });
  const timeLabel = date.toLocaleTimeString("es-MX", { hour: "2-digit", minute: "2-digit" });
  const broadcast = comp.broadcasts?.[0]?.names?.join(" · ");

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
      transition={{ duration: .25, delay }}
      className={`glass rounded-3xl p-4 relative overflow-hidden ${live ? "ring-2 ring-[#FF3B82]" : ""}`}
    >
      {live && (
        <div className="absolute -top-px left-4 right-4 h-0.5 bg-gradient-to-r from-transparent via-[#FF3B82] to-transparent" />
      )}

      <div className="flex items-center justify-between text-xs text-[var(--ink-soft)] mb-3">
        <div className="flex items-center gap-2 flex-wrap">
          {live && (
            <span className="chip chip-live tabular-nums">
              <span className="w-1.5 h-1.5 rounded-full bg-white animate-pulse" />
              {event.status.displayClock || "EN VIVO"}
            </span>
          )}
          {finished && <span className="chip">Final</span>}
          {upcoming && <span className="chip">{dateLabel} · {timeLabel}</span>}
          {upcoming && <KickoffCountdown kickoff={date} />}
          {event.competition === "friendly" && (
            <span className="chip bg-[var(--accent-violet)]/10 text-[var(--accent-violet)] font-semibold">
              Amistoso · no cuenta
            </span>
          )}
        </div>
        {comp.venue?.fullName && (
          <span className="flex items-center gap-1 truncate max-w-[180px]"><MapPin size={11} />{comp.venue.fullName}</span>
        )}
      </div>

      <div className="grid grid-cols-[1fr_auto_1fr] items-center gap-3">
        <TeamSide competitor={home} fallback={hTeam} side="home" winner={!!home.winner} />
        <div className="text-center min-w-[80px]">
          {live || finished ? (
            <div className="flex items-center gap-1.5">
              <ScoreBox value={home.score} winner={!!home.winner} live={live} />
              <span className="font-display text-base text-[var(--ink-muted)]">·</span>
              <ScoreBox value={away.score} winner={!!away.winner} live={live} />
            </div>
          ) : (
            <div className="font-display text-2xl text-[var(--ink-muted)] font-bold">vs</div>
          )}
        </div>
        <TeamSide competitor={away} fallback={aTeam} side="away" winner={!!away.winner} />
      </div>

      <div className="mt-3 pt-3 border-t border-[var(--line)] flex items-center justify-between text-[11px] text-[var(--ink-soft)]">
        <span>{event.status.type.detail}</span>
        {broadcast && (
          <span className="flex items-center gap-1"><Tv2 size={10} />{broadcast}</span>
        )}
      </div>

      {upcoming && (
        <div className="mt-3">
          <ProbabilityBar
            probs={probs}
            loading={probsLoading}
            homeCode={home.team.abbreviation}
            awayCode={away.team.abbreviation}
          />
        </div>
      )}

      {upcoming && fixtureId && (
        <QuickPicker
          fixtureId={fixtureId}
          homeCode={hTeam?.code ?? normalizeAbbr(home.team.abbreviation)}
          awayCode={aTeam?.code ?? normalizeAbbr(away.team.abbreviation)}
          probs={probs}
        />
      )}
    </motion.div>
  );
}

function ScoreBox({ value, winner, live }: { value: string; winner: boolean; live: boolean }) {
  return (
    <motion.div
      key={value}
      initial={{ scale: 1.2, opacity: 0.6 }}
      animate={{ scale: 1, opacity: 1 }}
      transition={{ duration: 0.25 }}
      className={`w-12 h-12 rounded-2xl grid place-items-center font-display font-extrabold text-2xl tabular-nums ${
        winner ? "bg-[var(--ink)] text-[var(--bg)] shadow-md" : "bg-[var(--bg-tint)] text-[var(--ink)]"
      } ${live ? "ring-1 ring-[#FF3B82]/40" : ""}`}
    >
      {value}
    </motion.div>
  );
}

function TeamSide({ competitor, fallback, side, winner }: {
  competitor: EspnEvent["competitions"][0]["competitors"][0];
  fallback?: typeof TEAMS[number];
  side: "home" | "away";
  winner: boolean;
}) {
  const align = side === "home" ? "items-end text-right" : "items-start text-left";
  const reverse = side === "home" ? "flex-row-reverse" : "flex-row";
  const teamCode = fallback?.code ?? normalizeAbbr(competitor.team.abbreviation);
  const inner = (
    <>
      <div className="relative w-10 h-10 rounded-xl overflow-hidden ring-1 ring-[var(--line)] shrink-0">
        {fallback ? (
          <Image src={flagUrl(fallback.iso2, 64)} alt={fallback.name} fill sizes="40px" className="object-cover" unoptimized />
        ) : (
          <Image src={competitor.team.logo} alt={competitor.team.displayName} fill sizes="40px" className="object-cover bg-white p-1" unoptimized />
        )}
      </div>
      <div className={`min-w-0 flex flex-col ${align}`}>
        <div className={`font-display font-bold leading-none ${winner ? "text-[var(--ink)]" : "text-[var(--ink-soft)]"}`}>{competitor.team.abbreviation}</div>
        <div className="text-[11px] text-[var(--ink-soft)] truncate max-w-[140px]">{competitor.team.shortDisplayName}</div>
      </div>
    </>
  );
  return (
    <Link href={`/equipos/${teamCode}`} className={`flex ${reverse} items-center gap-2.5 min-w-0 hover:opacity-80 transition-opacity`}>
      {inner}
    </Link>
  );
}

function EmptyState({ section, hint }: { section: Section; hint?: string }) {
  const phaseMeta = getTournamentPhase();
  const map: Record<Section, { title: string; sub: string }> = {
    live: { title: "Nada en juego ahora mismo", sub: "Cuando comience un partido aparecerá aquí en tiempo real." },
    today: { title: "Hoy no hay partidos", sub: "Cambia a Próximos o Resultados para ver el calendario." },
    upcoming: {
      title: "Sin partidos próximos en esta sección",
      sub: phaseMeta.phase === "FINAL_STAGE" || phaseMeta.phase === "KNOCKOUTS"
        ? "El torneo está en su fase eliminatoria/final. Revisa el bracket y los marcadores."
        : "Sigue el calendario del torneo en tiempo real."
    },
    results: { title: "Resultados del torneo", sub: "Partidos disputados y marcadores finales de la Copa Mundial." },
  };
  const m = map[section];

  const ctaHref = phaseMeta.isGroupPredictionsOpen ? "/quiniela" : phaseMeta.primaryCtaHref;
  const ctaText = phaseMeta.isGroupPredictionsOpen ? "Mientras tanto, llena tu quiniela" : phaseMeta.primaryCtaText;
  const CtaIcon = phaseMeta.isGroupPredictionsOpen ? Sparkles : phaseMeta.phase === "ENDED" ? Trophy : Swords;

  return (
    <div className="glass-strong rounded-3xl p-10 md:p-14 text-center max-w-xl mx-auto">
      <div className="w-14 h-14 rounded-2xl bg-[var(--bg-tint)] grid place-items-center mx-auto mb-4">
        <Sparkles size={22} className="text-[var(--accent-violet)]" />
      </div>
      <div className="font-display text-2xl font-bold mb-1">{m.title}</div>
      <p className="text-[var(--ink-soft)]">{m.sub}</p>
      {hint && <div className="mt-4 text-xs text-[var(--ink-muted)]">Última actualización · {hint}</div>}
      <Link href={ctaHref} className="mt-6 btn btn-primary flex items-center justify-center gap-2 mx-auto">
        <CtaIcon size={16} /> {ctaText}
      </Link>
    </div>
  );
}

function QuickPicker({
  fixtureId, homeCode, awayCode, probs,
}: {
  fixtureId: string;
  homeCode: string;
  awayCode: string;
  probs?: { H: number; D: number; A: number } | null;
}) {
  const { currentPlayer } = usePlayer();
  const [pick, setPick] = useState<Pick1X2 | undefined>(undefined);
  const [flash, setFlash] = useState<Pick1X2 | null>(null);

  useEffect(() => {
    if (!currentPlayer) return;
    const refresh = () => {
      const p = loadPredictions(currentPlayer.id);
      setPick(p.group[fixtureId]?.pick);
    };
    refresh();
    const onUpd = (e: Event) => {
      const ce = e as CustomEvent<string>;
      if (ce.detail === currentPlayer.id) refresh();
    };
    window.addEventListener("q26:predictions-updated", onUpd as EventListener);
    return () => window.removeEventListener("q26:predictions-updated", onUpd as EventListener);
  }, [currentPlayer, fixtureId]);

  if (!currentPlayer) return null;

  function commit(e: React.MouseEvent, next: Pick1X2) {
    e.preventDefault();
    e.stopPropagation();
    const all = loadPredictions(currentPlayer!.id);
    const prev = all.group[fixtureId] ?? { pick: next };
    all.group[fixtureId] = { ...prev, pick: next, source: "manual" };
    savePredictions(all);
    setPick(next);
    setFlash(next);
    setTimeout(() => setFlash(f => (f === next ? null : f)), 600);
    firePickToServer(currentPlayer!.id, fixtureId, next).then(result => {
      if (result.error === "locked") setPick(prev.pick as Pick1X2 | undefined);
    });
  }

  const labelFor = (k: Pick1X2) => k === "H" ? homeCode : k === "A" ? awayCode : "X";
  const probFor  = (k: Pick1X2) => probs ? (k === "H" ? probs.H : k === "A" ? probs.A : probs.D) : null;
  const accentFor = (k: Pick1X2) => k === "H" ? "#047857" : k === "A" ? "#BE123C" : "#64748B";

  return (
    <div className="mt-3 pt-3 border-t border-[var(--line)] flex items-center gap-1.5">
      {(["H", "D", "A"] as const).map(k => {
        const active = pick === k;
        const isFlashing = flash === k;
        const prob = probFor(k);
        return (
          <button
            key={k}
            type="button"
            onClick={e => commit(e, k)}
            className={`flex-1 relative py-2.5 rounded-xl text-[11px] font-extrabold uppercase tracking-wider overflow-hidden transition-all active:scale-95 ${
              active ? "text-[var(--bg)] font-extrabold shadow-md" : "text-[var(--ink-soft)] hover:text-[var(--ink)]"
            } ${isFlashing ? "ring-2 ring-[var(--accent-mint)]" : ""}`}
            style={{
              background: active ? "var(--ink)" : "var(--bg-tint)",
              boxShadow: active ? "0 4px 12px -4px rgba(0,0,0,0.3)" : "none",
            }}
          >
            {!active && prob !== null && (
              <span
                className="absolute bottom-0 left-0 h-[3px] rounded-full transition-all duration-700"
                style={{ width: `${prob * 100}%`, background: accentFor(k) }}
              />
            )}
            <span className="relative z-10 block text-center leading-none">{labelFor(k)}</span>
            {prob !== null && (
              <span className="relative z-10 block text-center text-[9px] opacity-75 leading-none mt-0.5">{Math.round(prob * 100)}%</span>
            )}
          </button>
        );
      })}
    </div>
  );
}

function SkeletonGrid() {
  return (
    <div className="grid lg:grid-cols-2 gap-3">
      {Array.from({ length: 6 }).map((_, i) => (
        <div key={i} className="glass cyber-skeleton rounded-3xl p-4 h-36" />
      ))}
    </div>
  );
}
