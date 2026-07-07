"use client";

import Image from "next/image";
import Link from "next/link";
import { useEffect, useState } from "react";
import { ArrowLeft, Trophy, Shield, Target, Clock, Swords } from "lucide-react";
import { TEAMS_BY_CODE, flagUrl } from "@/data/teams";
import { fixtureKickoffMs } from "@/lib/fixture-time";
import { allGroupFixtures } from "@/data/groups";
import type { TeamStatsResponse, PlayerStat } from "@/app/api/teams/[code]/route";

export default function EquiposPage({ params }: { params: Promise<{ code: string }> }) {
  const [code, setCode] = useState<string | null>(null);
  useEffect(() => {
    params.then(p => setCode(p.code.toUpperCase()));
  }, [params]);

  if (!code) return <PageShell><Skeleton /></PageShell>;
  return <TeamView code={code} />;
}

function TeamView({ code }: { code: string }) {
  const team = TEAMS_BY_CODE[code];
  const [data, setData] = useState<TeamStatsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    fetch(`/api/teams/${code}`, { cache: "no-store" })
      .then(r => r.json())
      .then(j => {
        if (j.ok) setData(j as TeamStatsResponse);
        else setError(j.error ?? "error");
      })
      .catch(() => setError("network"))
      .finally(() => setLoading(false));
  }, [code]);

  if (!team) return (
    <PageShell>
      <div className="text-center py-20 text-white/50">Equipo no encontrado</div>
    </PageShell>
  );

  return (
    <PageShell>
      {/* Header */}
      <div className="relative rounded-3xl overflow-hidden mb-4 p-6"
        style={{ background: "linear-gradient(135deg, rgba(30,34,55,0.98) 0%, rgba(20,24,42,0.98) 100%)", border: "1px solid rgba(255,255,255,0.08)" }}>
        <div className="flex items-center gap-4">
          <span className="relative w-20 h-20 rounded-2xl overflow-hidden ring-2 ring-white/20 flex-shrink-0">
            <Image src={flagUrl(team.iso2, 160)} alt={team.name} fill sizes="80px" className="object-cover" unoptimized />
          </span>
          <div className="min-w-0">
            <p className="text-white/50 text-xs uppercase tracking-widest font-bold mb-0.5">{team.confederation} · Grupo {team.group}</p>
            <h1 className="font-display font-black text-2xl text-white leading-tight">{team.name}</h1>
            {team.coach && <p className="text-white/60 text-sm mt-0.5">DT: {team.coach}</p>}
          </div>
        </div>
        {team.stars?.length > 0 && (
          <div className="mt-4 flex flex-wrap gap-2">
            {team.stars.map(s => (
              <span key={s} className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-white/10 text-white/80 text-xs font-semibold">
                ⭐ {s}
              </span>
            ))}
          </div>
        )}
      </div>

      {loading && <Skeleton />}
      {error && <p className="text-center text-white/40 py-12 text-sm">No se pudo cargar la información</p>}

      {data && !loading && (
        <>
          {/* Standing */}
          <Section icon={<Trophy size={14} />} title="Posición en grupo">
            <div className="grid grid-cols-4 gap-2 text-center">
              {[
                { label: "Pos", value: `${data.standing.position}°` },
                { label: "Pts", value: data.standing.pts },
                { label: "PJ",  value: data.standing.pj  },
                { label: "GD",  value: data.standing.gd >= 0 ? `+${data.standing.gd}` : data.standing.gd },
              ].map(({ label, value }) => (
                <div key={label} className="rounded-2xl bg-white/5 py-3">
                  <div className="font-display font-black text-xl text-white">{value}</div>
                  <div className="text-white/40 text-[11px] uppercase tracking-wider mt-0.5">{label}</div>
                </div>
              ))}
            </div>
            <div className="grid grid-cols-3 gap-2 text-center mt-2">
              {[
                { label: "Vic", value: data.standing.pg, color: "text-emerald-400" },
                { label: "Emp", value: data.standing.pe, color: "text-amber-400" },
                { label: "Der", value: data.standing.pp, color: "text-rose-400" },
              ].map(({ label, value, color }) => (
                <div key={label} className="rounded-2xl bg-white/5 py-3">
                  <div className={`font-display font-black text-xl ${color}`}>{value}</div>
                  <div className="text-white/40 text-[11px] uppercase tracking-wider mt-0.5">{label}</div>
                </div>
              ))}
            </div>
            <div className="flex justify-center gap-6 mt-2 rounded-2xl bg-white/5 py-3 text-center">
              <div>
                <span className="font-display font-black text-xl text-white">{data.standing.gf}</span>
                <span className="text-white/40 text-[11px] uppercase tracking-wider ml-1">GF</span>
              </div>
              <div className="text-white/20">·</div>
              <div>
                <span className="font-display font-black text-xl text-white">{data.standing.ga}</span>
                <span className="text-white/40 text-[11px] uppercase tracking-wider ml-1">GC</span>
              </div>
            </div>
          </Section>

          {/* Completed matches */}
          {data.completed.length > 0 && (
            <Section icon={<Shield size={14} />} title="Partidos jugados">
              <div className="flex flex-col gap-3">
                {data.completed.map(m => {
                  const opp = TEAMS_BY_CODE[m.opponent];
                  const myGoals = m.isHome ? m.homeGoals : m.awayGoals;
                  const oppGoals = m.isHome ? m.awayGoals : m.homeGoals;
                  const resultColor = m.result === "W" ? "bg-emerald-500" : m.result === "D" ? "bg-amber-500" : "bg-rose-600";
                  return (
                    <div key={m.fixtureId} className="rounded-2xl bg-white/5 p-4">
                      <div className="flex items-center gap-3 mb-2">
                        <span className={`w-6 h-6 rounded-full flex-shrink-0 grid place-items-center text-[10px] font-black text-white ${resultColor}`}>
                          {m.result}
                        </span>
                        <div className="flex items-center gap-2 flex-1 min-w-0">
                          {opp && (
                            <span className="relative w-5 h-5 rounded overflow-hidden flex-shrink-0">
                              <Image src={flagUrl(opp.iso2, 40)} alt={opp.name} fill sizes="20px" className="object-cover" unoptimized />
                            </span>
                          )}
                          <Link href={`/equipos/${m.opponent}`} className="text-white/80 font-semibold text-sm hover:text-white truncate">
                            {opp?.name ?? m.opponent}
                          </Link>
                        </div>
                        <span className="font-display font-black text-lg text-white tabular-nums flex-shrink-0">
                          {myGoals}–{oppGoals}
                        </span>
                      </div>
                      {m.goalscorers.length > 0 && (
                        <div className="flex flex-wrap gap-1.5 mt-1 pl-9">
                          {m.goalscorers.map((s, i) => (
                            <span key={i} className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-white/8 text-white/70 text-[11px]">
                              ⚽ {s}
                            </span>
                          ))}
                        </div>
                      )}
                      <p className="text-white/30 text-[11px] mt-1.5 pl-9">J{m.matchday} · {formatDate(m.date)}</p>
                    </div>
                  );
                })}
              </div>
            </Section>
          )}

          {/* Player stats: goalscorers + discipline */}
          {data.playerStats.length > 0 && (
            <Section icon={<Swords size={14} />} title="Estadísticas individuales">
              <div className="rounded-2xl overflow-hidden" style={{ border: "1px solid rgba(255,255,255,0.07)" }}>
                {/* Header row */}
                <div className="grid grid-cols-[1fr_auto_auto_auto] gap-x-3 px-4 py-2 bg-white/5 text-[10px] uppercase tracking-widest text-white/30 font-bold">
                  <span>Jugador</span>
                  <span className="text-center w-8">⚽</span>
                  <span className="text-center w-6">🟨</span>
                  <span className="text-center w-6">🟥</span>
                </div>
                {data.playerStats.map((ps, i) => (
                  <div
                    key={ps.name}
                    className="grid grid-cols-[1fr_auto_auto_auto] gap-x-3 px-4 py-3 items-center"
                    style={{ borderTop: i > 0 ? "1px solid rgba(255,255,255,0.04)" : undefined }}
                  >
                    <div className="flex items-center gap-2 min-w-0">
                      {i < 3 && ps.goals > 0 && (
                        <span className="text-[10px] font-black text-white/30 w-4 shrink-0">#{i + 1}</span>
                      )}
                      <span className="text-white/85 text-sm font-semibold truncate">{ps.name}</span>
                    </div>
                    <span className={`text-center w-8 font-display font-black text-sm tabular-nums ${ps.goals > 0 ? "text-emerald-400" : "text-white/20"}`}>
                      {ps.goals > 0 ? ps.goals : "–"}
                    </span>
                    <span className={`text-center w-6 font-display font-black text-sm tabular-nums ${ps.yellows > 0 ? "text-amber-400" : "text-white/20"}`}>
                      {ps.yellows > 0 ? ps.yellows : "–"}
                    </span>
                    <span className={`text-center w-6 font-display font-black text-sm tabular-nums ${ps.reds > 0 ? "text-rose-500" : "text-white/20"}`}>
                      {ps.reds > 0 ? ps.reds : "–"}
                    </span>
                  </div>
                ))}
              </div>
            </Section>
          )}

          {/* Upcoming */}
          {data.upcoming.length > 0 && (
            <Section icon={<Clock size={14} />} title="Próximos partidos">
              <div className="flex flex-col gap-2">
                {data.upcoming.map(m => {
                  const opp = TEAMS_BY_CODE[m.opponent];
                  const fx = allGroupFixtures().find(f => f.id === m.fixtureId);
                  const kickoffMs = fx ? fixtureKickoffMs(fx) : null;
                  return (
                    <div key={m.fixtureId} className="rounded-2xl bg-white/5 p-4 flex items-center gap-3 opacity-70">
                      {opp && (
                        <span className="relative w-6 h-6 rounded overflow-hidden flex-shrink-0">
                          <Image src={flagUrl(opp.iso2, 48)} alt={opp.name} fill sizes="24px" className="object-cover" unoptimized />
                        </span>
                      )}
                      <div className="flex-1 min-w-0">
                        <p className="text-white/80 font-semibold text-sm">{opp?.name ?? m.opponent}</p>
                        <p className="text-white/40 text-[11px] mt-0.5">
                          J{m.matchday} · {kickoffMs ? new Intl.DateTimeFormat("es-MX", { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" }).format(new Date(kickoffMs)) : formatDate(m.date)}
                        </p>
                      </div>
                    </div>
                  );
                })}
              </div>
            </Section>
          )}

          {/* Summary blurb */}
          {team.summary && (
            <Section icon={<Target size={14} />} title="Contexto">
              <p className="text-white/70 text-sm leading-relaxed">{team.summary}</p>
              {team.stats?.length > 0 && (
                <ul className="mt-3 flex flex-col gap-1">
                  {team.stats.map((s, i) => (
                    <li key={i} className="flex items-start gap-2 text-sm text-white/60">
                      <span className="mt-0.5 text-white/30">·</span>{s}
                    </li>
                  ))}
                </ul>
              )}
            </Section>
          )}
        </>
      )}
    </PageShell>
  );
}

function Section({ icon, title, children }: { icon: React.ReactNode; title: string; children: React.ReactNode }) {
  return (
    <div className="mb-4">
      <div className="flex items-center gap-2 mb-2 px-1">
        <span className="text-white/40">{icon}</span>
        <span className="text-white/50 text-xs uppercase tracking-widest font-bold">{title}</span>
      </div>
      {children}
    </div>
  );
}

function PageShell({ children }: { children: React.ReactNode }) {
  return (
    <main className="min-h-screen bg-[#0D1117] pb-28">
      <div className="max-w-lg mx-auto px-4 pt-4">
        <Link href="/partidos" className="inline-flex items-center gap-1.5 text-white/50 hover:text-white text-sm mb-4 transition-colors">
          <ArrowLeft size={14} /> Partidos
        </Link>
        {children}
      </div>
    </main>
  );
}

function Skeleton() {
  return (
    <div className="flex flex-col gap-3 animate-pulse">
      <div className="h-36 rounded-3xl bg-white/5" />
      <div className="h-24 rounded-3xl bg-white/5" />
      <div className="h-32 rounded-3xl bg-white/5" />
    </div>
  );
}

function formatDate(date: string): string {
  try {
    return new Intl.DateTimeFormat("es-MX", { month: "short", day: "numeric" }).format(new Date(date + "T12:00:00Z"));
  } catch { return date; }
}
