"use client";

// Match detail. One page per fixture: hero matchup, status (pre/live/final),
// charales votos, modelo de probabilidad, comparativa de fuerza y forma
// reciente. Sin alineaciones (no hay feed gratuito pre-match).

import { use, useMemo } from "react";
import Link from "next/link";
import Image from "next/image";
import { motion } from "framer-motion";
import { notFound } from "next/navigation";
import { ChevronLeft, MapPin, CalendarDays, Trophy, Users, BarChart3, Sparkles } from "lucide-react";

import { allGroupFixtures } from "@/data/groups";
import { TEAMS_BY_CODE, flagUrl } from "@/data/teams";
import { TEAM_STRENGTH } from "@/data/team-strength";
import { fixtureKickoffMs } from "@/lib/fixture-time";
import { ViewerKickoffTime } from "@/components/ViewerKickoff";
import { useLiveScoreboard } from "@/lib/live-scoreboard";
import { useFixtureProbs } from "@/lib/probabilities-client";
import { useAllPicksByFixture } from "@/lib/all-picks";
import { usePlayer } from "@/lib/player-context";
import { PlayerAvatar } from "@/components/PlayerAvatar";
import { useNow } from "@/lib/use-now";

type Params = { fixtureId: string };

const PICK_LABEL: Record<"H" | "D" | "A", string> = { H: "Local", D: "Empate", A: "Visitante" };
const PICK_ACCENT: Record<"H" | "D" | "A", string> = {
  H: "#22c55e",
  D: "#a855f7",
  A: "#ef4444",
};

function pct(n: number): string {
  return `${Math.round(n * 100)}%`;
}

function spanishDate(iso: string): string {
  const [y, m, d] = iso.split("-").map(Number);
  const date = new Date(Date.UTC(y, m - 1, d));
  const fmt = new Intl.DateTimeFormat("es-MX", { weekday: "long", day: "numeric", month: "long", timeZone: "UTC" });
  return fmt.format(date).replace(/^\w/, c => c.toUpperCase());
}

function formatCountdown(ms: number): string {
  if (ms <= 0) return "Está por comenzar";
  const s = Math.floor(ms / 1000);
  const d = Math.floor(s / 86400);
  const h = Math.floor((s % 86400) / 3600);
  const m = Math.floor((s % 3600) / 60);
  if (d > 0) return `Faltan ${d}d ${h}h`;
  if (h > 0) return `Faltan ${h}h ${m}m`;
  return `Faltan ${m}m`;
}

export default function PartidoPage({ params }: { params: Promise<Params> }) {
  const { fixtureId } = use(params);
  const fx = useMemo(() => allGroupFixtures().find(f => f.id === fixtureId), [fixtureId]);
  if (!fx) notFound();

  const home = TEAMS_BY_CODE[fx.home];
  const away = TEAMS_BY_CODE[fx.away];
  const sH = TEAM_STRENGTH[fx.home];
  const sA = TEAM_STRENGTH[fx.away];

  const now = useNow(30_000);
  const { byId: liveById, finals } = useLiveScoreboard();
  const live = liveById[fx.id];
  const final = finals[fx.id];
  const phase: "pre" | "live" | "final" = final ? "final" : live?.phase === "live" ? "live" : "pre";

  const { byFixture: probsById, loading: probsLoading } = useFixtureProbs();
  const probEntry = probsById[fx.id];
  const probs = probEntry?.probs;

  const { byFixture: picksById, loading: picksLoading } = useAllPicksByFixture();
  const picks = picksById[fx.id] ?? { H: [], D: [], A: [] };
  const totalVotes = picks.H.length + picks.D.length + picks.A.length;

  const { currentPlayer } = usePlayer();
  const myPick: "H" | "D" | "A" | null = useMemo(() => {
    if (!currentPlayer) return null;
    for (const k of ["H", "D", "A"] as const) {
      if (picks[k].some(p => p.id === currentPlayer.id)) return k;
    }
    return null;
  }, [picks, currentPlayer]);

  const kickoffMs = fixtureKickoffMs(fx);
  const countdown = now ? formatCountdown(kickoffMs - now) : "";

  const homeName = home?.name ?? fx.home;
  const awayName = away?.name ?? fx.away;

  const status = phase === "final"
    ? `Final · ${final?.homeGoals ?? 0}–${final?.awayGoals ?? 0}`
    : phase === "live"
      ? `EN VIVO · ${live?.minute ?? ""} · ${live?.homeGoals ?? 0}–${live?.awayGoals ?? 0}`
      : countdown || "Próximamente";

  return (
    <main className="container-app pb-24 pt-2">
      <Link href="/" className="inline-flex items-center gap-1 text-xs uppercase tracking-wider text-[var(--ink-muted)] hover:text-[var(--ink)] py-2">
        <ChevronLeft size={14} /> Volver
      </Link>

      {/* HERO */}
      <motion.section
        initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4 }}
        className="relative rounded-[28px] overflow-hidden border border-[var(--hairline)] shadow-[0_18px_40px_-22px_rgba(15,23,42,0.35)]"
      >
        <div className="absolute inset-0 -z-10 bg-gradient-to-br from-[var(--bg-tint)] via-white to-[var(--bg-tint)]" />
        <div className="absolute inset-x-0 -top-24 h-48 -z-10 opacity-40 blur-3xl" style={{ background: "radial-gradient(closest-side, var(--accent-violet), transparent)" }} />

        <div className="px-5 md:px-8 pt-6 pb-7">
          <div className="flex items-center justify-between text-[10px] uppercase tracking-[0.22em] text-[var(--ink-muted)] mb-5">
            <span className="font-bold">Grupo {fx.group} · Jornada {fx.matchday}</span>
            <span className={`px-2.5 py-1 rounded-full ${phase === "live" ? "bg-[#FF3B82] text-white" : phase === "final" ? "bg-[var(--ink)] text-white" : "bg-white border border-[var(--hairline)]"} text-[10px]`}>
              {phase === "live" ? "EN VIVO" : phase === "final" ? "Finalizado" : "Programado"}
            </span>
          </div>

          <div className="grid grid-cols-[1fr_auto_1fr] gap-3 md:gap-5 items-center">
            <TeamColumn code={fx.home} name={homeName} iso2={home?.iso2 ?? ""} align="left" />
            <div className="flex flex-col items-center min-w-[88px]">
              <div className="font-display font-extrabold text-2xl md:text-3xl tabular-nums leading-none">
                {phase === "pre" ? "vs" : `${phase === "final" ? final?.homeGoals : live?.homeGoals ?? 0} – ${phase === "final" ? final?.awayGoals : live?.awayGoals ?? 0}`}
              </div>
              <div className="text-[10px] uppercase tracking-wider mt-2 text-[var(--ink-muted)] font-bold whitespace-nowrap">
                <ViewerKickoffTime fx={fx} /> · {fx.kickoffLocal} en estadio
              </div>
            </div>
            <TeamColumn code={fx.away} name={awayName} iso2={away?.iso2 ?? ""} align="right" />
          </div>

          <div className="mt-6 flex flex-col sm:flex-row gap-1.5 sm:gap-4 text-[11px] sm:text-xs text-[var(--ink-muted)]">
            <span className="inline-flex items-center gap-1.5">
              <CalendarDays size={13} /> {spanishDate(fx.date)}
            </span>
            <span className="inline-flex items-center gap-1.5">
              <MapPin size={13} /> {fx.venue} · {fx.city}
            </span>
          </div>

          <div className={`mt-4 text-center font-display font-bold text-sm ${phase === "live" ? "text-[#FF3B82]" : "text-[var(--ink)]"}`}>
            {status}
          </div>
        </div>
      </motion.section>

      {/* TU PICK (si hay sesión) */}
      {currentPlayer && (
        <motion.div
          initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4, delay: 0.05 }}
          className="mt-3 rounded-2xl border border-[var(--hairline)] bg-white px-4 py-3 flex items-center gap-3"
        >
          <PlayerAvatar player={currentPlayer} size={32} rounded="rounded-xl" textClass="text-sm" tint={0.18} />
          <div className="min-w-0 flex-1">
            {myPick ? (
              <div className="text-[12px]">
                Tu voto: <span className="font-bold" style={{ color: PICK_ACCENT[myPick] }}>
                  {myPick === "H" ? homeName : myPick === "A" ? awayName : "Empate"}
                </span>
              </div>
            ) : (
              <div className="text-[12px] text-[var(--ink-muted)]">No has votado este partido.</div>
            )}
          </div>
          <Link href={`/quiniela?fixture=${fx.id}`} className="text-[11px] uppercase tracking-wider font-bold underline underline-offset-2">
            {myPick ? "Cambiar" : "Votar"}
          </Link>
        </motion.div>
      )}

      {/* VOTO CHARALES */}
      <Section icon={Users} title="Cómo votaron los charales" subtitle={picksLoading ? "Cargando…" : totalVotes === 0 ? "Aún nadie vota este partido" : `${totalVotes} voto${totalVotes === 1 ? "" : "s"} contados`}>
        <VoteBar
          left={{ label: homeName, count: picks.H.length, pct: totalVotes ? picks.H.length / totalVotes : 0, color: PICK_ACCENT.H }}
          mid={{ label: "Empate", count: picks.D.length, pct: totalVotes ? picks.D.length / totalVotes : 0, color: PICK_ACCENT.D }}
          right={{ label: awayName, count: picks.A.length, pct: totalVotes ? picks.A.length / totalVotes : 0, color: PICK_ACCENT.A }}
        />
        <div className="mt-4 grid grid-cols-3 gap-2 md:gap-3">
          <VoteColumn label={homeName} pickKey="H" players={picks.H} accent={PICK_ACCENT.H} highlightedId={currentPlayer?.id} />
          <VoteColumn label="Empate" pickKey="D" players={picks.D} accent={PICK_ACCENT.D} highlightedId={currentPlayer?.id} />
          <VoteColumn label={awayName} pickKey="A" players={picks.A} accent={PICK_ACCENT.A} highlightedId={currentPlayer?.id} />
        </div>
      </Section>

      {/* PROBABILIDAD MODELO */}
      <Section icon={Sparkles} title="Probabilidad del modelo" subtitle={
        probsLoading ? "Calculando…" :
        !probs ? "Aún sin cálculo" :
        probEntry?.market ? "Modelo + casas de apuestas" : "Modelo de fuerza + forma"
      }>
        {probs ? (
          <ProbBars probs={probs} homeName={homeName} awayName={awayName} />
        ) : (
          <div className="text-xs text-[var(--ink-muted)] py-4">Las probabilidades aparecerán cuando el agente las publique.</div>
        )}
      </Section>

      {/* COMPARATIVA */}
      <Section icon={BarChart3} title="Comparativa de fuerza" subtitle="Tier + rating con notas del scouting interno">
        <StrengthRow code={fx.home} name={homeName} iso2={home?.iso2 ?? ""} s={sH} accent={PICK_ACCENT.H} />
        <StrengthRow code={fx.away} name={awayName} iso2={away?.iso2 ?? ""} s={sA} accent={PICK_ACCENT.A} />
      </Section>

      <div className="mt-6 text-center">
        <Link href="/partidos" className="inline-flex items-center gap-1.5 text-xs uppercase tracking-wider text-[var(--ink-muted)] hover:text-[var(--ink)]">
          <Trophy size={13} /> Ver todos los partidos
        </Link>
      </div>
    </main>
  );
}

function TeamColumn({ code, name, iso2, align }: { code: string; name: string; iso2: string; align: "left" | "right" }) {
  return (
    <Link href={`/equipos/${code}`} className={`flex flex-col ${align === "right" ? "items-end text-right" : "items-start text-left"} gap-2 min-w-0 hover:opacity-90 transition-opacity`}>
      {iso2 && (
        <div className="rounded-[14px] overflow-hidden border border-[var(--hairline)] shadow-sm">
          <Image src={flagUrl(iso2, 160)} alt="" width={84} height={56} className="object-cover" unoptimized />
        </div>
      )}
      <div className="min-w-0">
        <div className="font-display font-extrabold text-base md:text-lg leading-tight truncate">{name}</div>
        <div className="text-[10px] uppercase tracking-[0.2em] text-[var(--ink-muted)] font-bold mt-0.5">{code}</div>
      </div>
    </Link>
  );
}

function Section({ icon: Icon, title, subtitle, children }: {
  icon: React.ComponentType<{ size?: number; className?: string }>;
  title: string;
  subtitle?: string;
  children: React.ReactNode;
}) {
  return (
    <motion.section
      initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4 }}
      className="mt-5 rounded-3xl border border-[var(--hairline)] bg-white p-5 shadow-[0_10px_24px_-16px_rgba(15,23,42,0.25)]"
    >
      <div className="flex items-start gap-2.5 mb-3">
        <div className="mt-0.5 w-7 h-7 rounded-lg grid place-items-center bg-[var(--bg-tint)] text-[var(--ink)]">
          <Icon size={14} />
        </div>
        <div className="min-w-0 flex-1">
          <div className="font-display font-bold text-[15px] leading-tight">{title}</div>
          {subtitle && <div className="text-[11px] text-[var(--ink-muted)] mt-0.5">{subtitle}</div>}
        </div>
      </div>
      {children}
    </motion.section>
  );
}

function VoteBar({ left, mid, right }: {
  left: { label: string; count: number; pct: number; color: string };
  mid:  { label: string; count: number; pct: number; color: string };
  right: { label: string; count: number; pct: number; color: string };
}) {
  const total = left.pct + mid.pct + right.pct;
  if (total === 0) {
    return <div className="h-8 rounded-full bg-[var(--bg-tint)] border border-dashed border-[var(--hairline)]" />;
  }
  return (
    <div className="space-y-1.5">
      <div className="h-8 rounded-full flex overflow-hidden border border-[var(--hairline)] bg-white">
        {[left, mid, right].map((seg, i) => seg.pct > 0 && (
          <motion.div
            key={i}
            initial={{ width: 0 }}
            animate={{ width: `${seg.pct * 100}%` }}
            transition={{ duration: 0.6, delay: i * 0.05, ease: "easeOut" }}
            className="h-full flex items-center justify-center text-[10px] font-extrabold text-white tabular-nums"
            style={{ background: seg.color, minWidth: seg.pct > 0 ? 32 : 0 }}
          >
            {seg.pct >= 0.12 ? pct(seg.pct) : ""}
          </motion.div>
        ))}
      </div>
    </div>
  );
}

function VoteColumn({ label, pickKey, players, accent, highlightedId }: {
  label: string;
  pickKey: "H" | "D" | "A";
  players: Array<{ id: string; name: string; emoji: string; accent: string; photoDataUrl?: string }>;
  accent: string;
  highlightedId?: string;
}) {
  return (
    <div className="rounded-2xl border border-[var(--hairline)] bg-[var(--bg-tint)] p-2.5">
      <div className="flex items-center justify-between mb-2">
        <span className="text-[10px] uppercase tracking-wider font-extrabold" style={{ color: accent }}>{PICK_LABEL[pickKey]}</span>
        <span className="text-[11px] tabular-nums font-bold">{players.length}</span>
      </div>
      <div className="text-[11px] text-[var(--ink-soft)] font-medium leading-tight truncate mb-2">{label}</div>
      {players.length === 0 ? (
        <div className="text-[10px] text-[var(--ink-muted)] italic py-2">—</div>
      ) : (
        <div className="flex flex-wrap gap-1.5">
          {players.map(p => (
            <div key={p.id} title={p.name} className={`relative ${highlightedId === p.id ? "ring-2 ring-offset-1 rounded-full" : ""}`} style={highlightedId === p.id ? { boxShadow: `0 0 0 2px ${accent}` } : undefined}>
              <PlayerAvatar player={p} size={28} rounded="rounded-full" textClass="text-xs" tint={0.18} />
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function ProbBars({ probs, homeName, awayName }: { probs: { H: number; D: number; A: number }; homeName: string; awayName: string }) {
  const rows = ([
    { key: "H", label: homeName,  v: probs.H },
    { key: "D", label: "Empate",  v: probs.D },
    { key: "A", label: awayName,  v: probs.A },
  ] as Array<{ key: "H" | "D" | "A"; label: string; v: number }>).sort((a, b) => b.v - a.v);
  return (
    <div className="space-y-2.5">
      {rows.map((r, i) => (
        <div key={r.key} className="flex items-center gap-3">
          <div className="w-20 md:w-28 truncate text-[12px] font-semibold">{r.label}</div>
          <div className="flex-1 h-3 rounded-full bg-[var(--bg-tint)] overflow-hidden border border-[var(--hairline)]">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${Math.max(2, r.v * 100)}%` }}
              transition={{ duration: 0.7, delay: i * 0.06 }}
              className="h-full rounded-full"
              style={{ background: PICK_ACCENT[r.key] }}
            />
          </div>
          <div className="w-12 text-right text-[12px] font-extrabold tabular-nums">{pct(r.v)}</div>
        </div>
      ))}
    </div>
  );
}

function StrengthRow({ code, name, iso2, s, accent }: {
  code: string;
  name: string;
  iso2: string;
  s?: { tier: string; strength: number; notes: string };
  accent: string;
}) {
  return (
    <div className="flex items-start gap-3 py-3 first:pt-1 last:pb-1 border-b border-[var(--hairline)] last:border-0">
      {iso2 && (
        <Image src={flagUrl(iso2, 80)} alt="" width={40} height={28} className="rounded-sm object-cover shrink-0 mt-0.5" unoptimized />
      )}
      <div className="min-w-0 flex-1">
        <div className="flex items-center gap-2">
          <span className="font-display font-bold text-sm">{name}</span>
          <span className="text-[10px] uppercase tracking-wider text-[var(--ink-muted)]">{code}</span>
          {s && (
            <span
              className="ml-auto text-[10px] font-extrabold px-2 py-0.5 rounded-full text-white"
              style={{ background: accent }}
            >
              Tier {s.tier} · {s.strength}
            </span>
          )}
        </div>
        {s?.notes && (
          <div className="text-[11px] text-[var(--ink-soft)] mt-1 leading-snug">{s.notes}</div>
        )}
      </div>
    </div>
  );
}
