"use client";

import Image from "next/image";
import Link from "next/link";
import { motion } from "framer-motion";
import { useState } from "react";
import { Trophy, Users, Star, ChevronDown, Target } from "lucide-react";
import { GROUP_LETTERS, groupFixtures, teamsInGroup, type GroupLetter } from "@/data/groups";
import { TEAMS, flagUrl, CONFEDERATION_COLORS } from "@/data/teams";

export default function GroupsPage() {
  const [filter, setFilter] = useState<"all" | "favorites">("all");
  const [openTeam, setOpenTeam] = useState<string | null>(null);

  return (
    <div className="bg-canvas">
      {/* Header */}
      <section className="container-app pt-10 md:pt-14 pb-6">
        <div className="flex flex-col md:flex-row md:items-end gap-6 md:justify-between">
          <div>
            <span className="chip mb-3"><Trophy size={12} /> Sorteo · Washington DC · 5 dic 2025</span>
            <h1 className="font-display text-4xl md:text-6xl font-bold leading-tight">
              <span className="grad-text">12 grupos.</span><br />48 selecciones.
            </h1>
            <p className="mt-3 text-[var(--ink-soft)] max-w-xl">
              Cada grupo juega 6 partidos. Avanzan los dos primeros + los 8 mejores terceros a dieciseisavos.
            </p>
          </div>
          <div className="flex gap-1 glass rounded-full p-1 self-start">
            {(["all", "favorites"] as const).map(k => (
              <button
                key={k}
                onClick={() => setFilter(k)}
                className={`px-4 py-2 rounded-full text-sm font-semibold transition-colors ${filter === k ? "bg-[var(--ink)] text-white" : "text-[var(--ink-soft)]"}`}
              >
                {k === "all" ? "Todos los grupos" : "Solo top FIFA"}
              </button>
            ))}
          </div>
        </div>
      </section>

      {/* Confederation legend */}
      <section className="container-app pb-6">
        <div className="flex flex-wrap gap-2 text-xs">
          {Object.entries(CONFEDERATION_COLORS).map(([conf, color]) => (
            <span key={conf} className="inline-flex items-center gap-1.5 chip" style={{ background: `${color}1F`, color: color as string }}>
              <span className="w-1.5 h-1.5 rounded-full" style={{ background: color as string }} /> {conf}
            </span>
          ))}
        </div>
      </section>

      {/* Groups grid */}
      <section className="container-app pb-20">
        <div className="grid md:grid-cols-2 xl:grid-cols-3 gap-5">
          {GROUP_LETTERS.map((letter, idx) => (
            <GroupCard
              key={letter}
              letter={letter}
              filter={filter}
              openTeam={openTeam}
              setOpenTeam={setOpenTeam}
              delay={idx * 0.04}
            />
          ))}
        </div>

        <div className="mt-12 glass rounded-3xl p-6 md:p-8 flex flex-col md:flex-row items-center gap-4 md:gap-8 text-center md:text-left">
          <div className="w-14 h-14 rounded-2xl grid place-items-center bg-[var(--ink)] text-white shrink-0">
            <Target size={24} />
          </div>
          <div className="flex-1">
            <div className="font-display text-xl font-semibold">¿Listo para llenar tus marcadores?</div>
            <p className="text-sm text-[var(--ink-soft)]">Son 72 partidos de grupos. Predice cada uno y suma puntos por acertar 1X2.</p>
          </div>
          <Link href="/quiniela" className="btn btn-primary">Ir a mi quiniela</Link>
        </div>
      </section>
    </div>
  );
}

function GroupCard({
  letter, filter, openTeam, setOpenTeam, delay,
}: {
  letter: GroupLetter;
  filter: "all" | "favorites";
  openTeam: string | null;
  setOpenTeam: (s: string | null) => void;
  delay: number;
}) {
  const teams = teamsInGroup(letter);
  const fixtures = groupFixtures(letter);
  const visible = filter === "favorites" ? teams.filter(t => t.ranking !== null && t.ranking <= 20) : teams;

  if (filter === "favorites" && visible.length === 0) return null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 14 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}
      transition={{ duration: .4, delay }}
      id={letter}
      className="glass rounded-3xl p-5 relative overflow-hidden"
    >
      {/* Group letter watermark */}
      <div className="absolute -top-6 -right-2 font-display text-[110px] font-bold text-[var(--bg-tint)] leading-none select-none pointer-events-none">
        {letter}
      </div>

      <div className="relative">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <div className="w-9 h-9 rounded-xl bg-[var(--ink)] text-white grid place-items-center font-display font-bold">
              {letter}
            </div>
            <div>
              <div className="text-xs uppercase tracking-[0.18em] text-[var(--ink-muted)]">Grupo</div>
              <div className="font-display font-semibold">4 selecciones</div>
            </div>
          </div>
          <span className="chip"><Users size={11} /> 6 partidos</span>
        </div>

        {/* Teams list */}
        <ul className="space-y-1.5">
          {teams.map(t => {
            const conf = CONFEDERATION_COLORS[t.confederation];
            const isOpen = openTeam === t.code;
            return (
              <li key={t.code}>
                <button
                  onClick={() => setOpenTeam(isOpen ? null : t.code)}
                  className={`w-full flex items-center gap-3 p-2 rounded-2xl transition-colors text-left ${isOpen ? "bg-[var(--bg-tint)]" : "hover:bg-[var(--bg-tint)]"}`}
                >
                  <Link
                    href={`/equipos/${t.code}`}
                    onClick={e => e.stopPropagation()}
                    className="relative w-9 h-9 rounded-lg overflow-hidden ring-1 ring-[var(--line)] shrink-0 hover:ring-2 hover:ring-[var(--ink)] transition-all"
                  >
                    <Image src={flagUrl(t.iso2, 64)} alt={t.name} fill sizes="36px" className="object-cover" unoptimized />
                  </Link>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-baseline gap-2">
                      <span className="font-display font-bold">{t.code}</span>
                      <span className="text-sm truncate">{t.name}</span>
                    </div>
                    <div className="flex items-center gap-2 mt-0.5">
                      <span className="text-[10px] uppercase tracking-wider" style={{ color: conf }}>{t.confederation}</span>
                      {t.ranking && (
                        <>
                          <span className="text-[10px] text-[var(--ink-muted)]">·</span>
                          <span className="text-[10px] text-[var(--ink-muted)] flex items-center gap-0.5">
                            <Star size={9} /> #{t.ranking} FIFA
                          </span>
                        </>
                      )}
                    </div>
                  </div>
                  <ChevronDown size={14} className={`text-[var(--ink-muted)] transition-transform ${isOpen ? "rotate-180" : ""}`} />
                </button>

                {/* Expandable detail */}
                {isOpen && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: "auto" }}
                    className="px-3 pt-2 pb-3"
                  >
                    <p className="text-xs text-[var(--ink-soft)] leading-relaxed mb-2.5">{t.summary}</p>
                    <div className="grid grid-cols-2 gap-2 text-[11px]">
                      <Pill label="DT" value={t.coach} />
                      <Pill label="Estrella" value={t.stars[0]} />
                    </div>
                    <div className="mt-2 space-y-1">
                      {t.stats.map((s, i) => (
                        <div key={i} className="text-[11px] text-[var(--ink-soft)] flex items-start gap-1.5">
                          <span className="text-[var(--accent-violet)] mt-0.5">▸</span>{s}
                        </div>
                      ))}
                    </div>
                  </motion.div>
                )}
              </li>
            );
          })}
        </ul>

        {/* Fixtures */}
        <div className="mt-4 pt-4 border-t border-[var(--line)]">
          <div className="text-[10px] uppercase tracking-[0.18em] text-[var(--ink-muted)] mb-2">Partidos del grupo</div>
          <div className="grid grid-cols-3 gap-1.5">
            {fixtures.map(fx => {
              const h = TEAMS.find(t => t.code === fx.home)!;
              const a = TEAMS.find(t => t.code === fx.away)!;
              return (
                <Link key={fx.id} href={`/partido/${fx.id}`} className="rounded-xl bg-[var(--bg-tint)] hover:bg-[var(--line)] p-2 flex items-center gap-1 text-[10px] font-semibold transition-colors">
                  <Link href={`/equipos/${h.code}`} onClick={e => e.stopPropagation()} className="relative w-4 h-4 rounded-full overflow-hidden ring-1 ring-white/70 hover:ring-[var(--ink)] transition-all shrink-0">
                    <Image src={flagUrl(h.iso2, 32)} alt={h.name} fill sizes="16px" className="object-cover" unoptimized />
                  </Link>
                  <span>{h.code}</span>
                  <span className="text-[var(--ink-muted)] mx-0.5">vs</span>
                  <span>{a.code}</span>
                  <Link href={`/equipos/${a.code}`} onClick={e => e.stopPropagation()} className="relative w-4 h-4 rounded-full overflow-hidden ring-1 ring-white/70 hover:ring-[var(--ink)] transition-all shrink-0">
                    <Image src={flagUrl(a.iso2, 32)} alt={a.name} fill sizes="16px" className="object-cover" unoptimized />
                  </Link>
                </Link>
              );
            })}
          </div>
        </div>
      </div>
    </motion.div>
  );
}

function Pill({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg bg-white border border-[var(--line)] px-2 py-1.5">
      <div className="text-[9px] uppercase tracking-wider text-[var(--ink-muted)]">{label}</div>
      <div className="text-[11px] font-semibold truncate">{value}</div>
    </div>
  );
}

