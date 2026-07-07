"use client";

// Ranking en vivo de las 48 selecciones del Mundial 2026.
// Score compuesto = baseStrength (modelo) * 0.35
//                 + bookmaker implied  * 0.35
//                 + people share       * 0.15
//                 + live results boost * 0.15
// Animación de reordenamiento via Framer Motion `layout`.

import Link from "next/link";
import Image from "next/image";
import { motion, AnimatePresence, LayoutGroup } from "framer-motion";
import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import {
  ArrowUp,
  ArrowDown,
  Minus,
  Sparkles,
  TrendingUp,
  Trophy,
  Users2,
  Coins,
  Activity,
  ArrowLeft,
  Info,
} from "lucide-react";
import { TEAMS, TEAMS_BY_CODE, flagUrl } from "@/data/teams";
import { TEAM_STRENGTH } from "@/data/team-strength";
import { BOOKMAKER_CHAMPION_PROB, BOOKMAKER_SNAPSHOT_DATE, bookmakerChampionProb } from "@/data/bookmaker-odds";
import { allGroupFixtures } from "@/data/groups";
import { useGroupRealResults } from "@/lib/real-results";
import { useBracketProbs } from "@/lib/probabilities-client";

// ---------------------------------------------------------------------------
// Tipos auxiliares
// ---------------------------------------------------------------------------

type SortKey = "composite" | "model" | "bookies" | "people" | "live";

type PeopleData = {
  championVotes: Record<string, number>;
  groupPickShare: Record<string, number>;
  totalPlayers: number;
};

type Form = ("W" | "D" | "L")[];

type RankRow = {
  code: string;
  name: string;
  flagIso: string;
  group: string;
  // 0-100 normalized scores per dimension
  modelScore: number;
  bookiesScore: number;
  peopleScore: number;
  liveScore: number;
  composite: number;
  // raw values for display
  bookiesPct: number;     // 0-100
  peoplePct: number;      // 0-100 share of group picks
  championVotes: number;  // raw votes count
  liveDelta: number;      // -inf..+inf, points moved by real results
  form: Form;             // last up to 3 results
};

// ---------------------------------------------------------------------------
// Página
// ---------------------------------------------------------------------------

export default function RankingPage() {
  const { results: realResults } = useGroupRealResults();
  const { teams: bracketTeams } = useBracketProbs();
  const [people, setPeople] = useState<PeopleData | null>(null);
  const [sortKey, setSortKey] = useState<SortKey>("composite");
  const [expanded, setExpanded] = useState<string | null>(null);
  const [prevOrder, setPrevOrder] = useState<Record<string, number>>({});

  // Cargar lo que dice la gente desde Firestore.
  useEffect(() => {
    let cancelled = false;
    fetch("/api/ranking/people", { cache: "no-store" })
      .then(r => r.ok ? r.json() : null)
      .then(j => {
        if (cancelled || !j?.ok) return;
        setPeople({
          championVotes: j.championVotes ?? {},
          groupPickShare: j.groupPickShare ?? {},
          totalPlayers: j.totalPlayers ?? 0,
        });
      })
      .catch(() => {});
    return () => { cancelled = true; };
  }, []);

  // Calcular forma + live boost por equipo a partir de los reales.
  const liveByTeam = useMemo(() => {
    const out: Record<string, { delta: number; form: Form }> = {};
    for (const t of TEAMS) out[t.code] = { delta: 0, form: [] };
    const fixtures = allGroupFixtures();
    // Recorre en orden cronológico para que `form` quede temporalmente ordenada.
    const ordered = [...fixtures].sort((a, b) => a.date.localeCompare(b.date));
    for (const fx of ordered) {
      const r = realResults[fx.id];
      if (!r) continue;
      const homeBucket = out[fx.home];
      const awayBucket = out[fx.away];
      if (!homeBucket || !awayBucket) continue;
      if (r.homeGoals > r.awayGoals) {
        homeBucket.delta += 5; awayBucket.delta -= 5;
        homeBucket.form.push("W"); awayBucket.form.push("L");
      } else if (r.homeGoals < r.awayGoals) {
        awayBucket.delta += 5; homeBucket.delta -= 5;
        awayBucket.form.push("W"); homeBucket.form.push("L");
      } else {
        homeBucket.form.push("D"); awayBucket.form.push("D");
      }
    }
    // Truncar form a últimos 3 partidos.
    for (const code of Object.keys(out)) {
      out[code].form = out[code].form.slice(-3);
    }
    return out;
  }, [realResults]);

  // Calcular rows base (sin orden todavía).
  const rows = useMemo<RankRow[]>(() => {
    // Normalizaciones:
    // - bookies: prob implícita 0-1 → escalar para que el favorito top quede en 100.
    const maxBookie = Math.max(...TEAMS.map(t => bookmakerChampionProb(t.code)));
    // - people: share de picks de grupos, max → 100 (no es lineal con %; lo escalamos al máximo observado).
    const peopleShares = TEAMS.map(t => people?.groupPickShare[t.code] ?? 0);
    const maxPeopleShare = Math.max(...peopleShares, 0.0001);
    // - live: delta ∈ [-15, +15] ish → mapear a 0-100 centrado en 50.
    const liveToScore = (d: number) => Math.max(0, Math.min(100, 50 + d * 3.33));

    return TEAMS.map(t => {
      const strength = TEAM_STRENGTH[t.code]?.strength ?? 50;
      const modelScore = strength; // ya está 0-100.
      const bookiesProb = bookmakerChampionProb(t.code);
      const bookiesScore = (bookiesProb / maxBookie) * 100;
      const peopleShare = people?.groupPickShare[t.code] ?? 0;
      const peopleScore = (peopleShare / maxPeopleShare) * 100;
      const liveBucket = liveByTeam[t.code] ?? { delta: 0, form: [] };
      const liveScore = liveToScore(liveBucket.delta);

      const composite =
        modelScore * 0.35 +
        bookiesScore * 0.35 +
        peopleScore * 0.15 +
        liveScore * 0.15;

      return {
        code: t.code,
        name: t.name,
        flagIso: t.iso2,
        group: t.group,
        modelScore,
        bookiesScore,
        peopleScore,
        liveScore,
        composite,
        bookiesPct: bookiesProb * 100,
        peoplePct: peopleShare * 100,
        championVotes: people?.championVotes[t.code] ?? 0,
        liveDelta: liveBucket.delta,
        form: liveBucket.form,
      };
    });
  }, [people, liveByTeam]);

  // Ordenamiento según el chip activo.
  const sortedRows = useMemo(() => {
    const get = (r: RankRow) => {
      switch (sortKey) {
        case "model": return r.modelScore;
        case "bookies": return r.bookiesScore;
        case "people": return r.peopleScore;
        case "live": return r.liveScore;
        default: return r.composite;
      }
    };
    return [...rows].sort((a, b) => get(b) - get(a));
  }, [rows, sortKey]);

  // Guardar el orden previo para mostrar flechas ▲ ▼ vs orden compuesto anterior.
  useEffect(() => {
    const next: Record<string, number> = {};
    sortedRows.forEach((r, idx) => { next[r.code] = idx; });
    setPrevOrder(prev => {
      // Solo actualizar después del primer render para detectar movimiento real.
      if (Object.keys(prev).length === 0) return next;
      return prev; // mantenemos el primer snapshot como baseline para mostrar movimiento
    });
  }, [sortedRows]);

  // Promedio composite para banda sutil de "arriba/abajo de la media".
  const avgComposite = useMemo(() => {
    if (!rows.length) return 50;
    return rows.reduce((a, b) => a + b.composite, 0) / rows.length;
  }, [rows]);

  return (
    <div className="bg-canvas min-h-screen">
      {/* HERO compacto */}
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 bg-grid opacity-50 [mask-image:radial-gradient(ellipse_at_center,black,transparent_70%)]" />
        <div className="absolute -top-40 -left-32 w-[420px] h-[420px] rounded-full blob opacity-30"
             style={{ background: "radial-gradient(closest-side, rgba(94,91,255,0.35), transparent)" }} />
        <div className="absolute -top-32 right-0 w-[420px] h-[420px] rounded-full blob opacity-30"
             style={{ background: "radial-gradient(closest-side, rgba(20,241,149,0.30), transparent)", animationDelay: "-4s" }} />

        <div className="container-app pt-8 md:pt-12 pb-6 relative">
          <Link href="/" className="inline-flex items-center gap-1.5 text-sm text-[var(--ink-soft)] hover:text-[var(--ink)] mb-4">
            <ArrowLeft size={14} /> Volver al inicio
          </Link>

          <div className="flex flex-wrap items-center gap-2 mb-4">
            <span className="chip"><span className="live-dot" /> Ranking en vivo</span>
            <span className="chip"><Sparkles size={11} /> 48 selecciones</span>
            <span className="chip">4 fuentes combinadas</span>
          </div>

          <h1 className="font-display text-[clamp(36px,7vw,84px)] font-bold leading-[0.95] tracking-tight">
            ¿Quién va arriba <span className="grad-text">de verdad?</span>
          </h1>
          <p className="mt-4 text-base md:text-lg text-[var(--ink-soft)] max-w-2xl leading-relaxed">
            Combinamos el modelo interno, lo que pagan las casas, lo que dicen los compas y lo que pasa
            en la cancha. Cada gol mueve la tabla — los <strong className="text-[var(--ink)]">▲ ▼</strong> marcan a quién le bailó el ranking.
          </p>
        </div>
      </section>

      {/* CHIPS DE ORDEN */}
      <section className="container-app pb-4">
        <div className="glass rounded-2xl p-2 flex flex-wrap gap-1.5">
          <SortChip k="composite" active={sortKey} setActive={setSortKey} label="Composite" icon={<Sparkles size={13} />} />
          <SortChip k="model" active={sortKey} setActive={setSortKey} label="Predicciones" icon={<TrendingUp size={13} />} />
          <SortChip k="bookies" active={sortKey} setActive={setSortKey} label="Casas de apuesta" icon={<Coins size={13} />} />
          <SortChip k="people" active={sortKey} setActive={setSortKey} label="Los compas" icon={<Users2 size={13} />} />
          <SortChip k="live" active={sortKey} setActive={setSortKey} label="En la cancha" icon={<Activity size={13} />} />
        </div>
        <p className="mt-3 text-xs text-[var(--ink-muted)] flex items-center gap-1.5">
          <Info size={11} />
          Casas: snapshot {BOOKMAKER_SNAPSHOT_DATE} ·
          {people ? ` ${people.totalPlayers} compas con picks` : " cargando picks…"} ·
          tap a una fila para ver el desglose.
        </p>
      </section>

      {/* HEADER FILA (desktop only) */}
      <section className="container-app pb-2 hidden md:block">
        <div className="grid grid-cols-[40px_minmax(160px,1.4fr)_88px_88px_88px_120px_70px] gap-3 px-4 text-[10px] uppercase tracking-[0.16em] text-[var(--ink-muted)] font-semibold">
          <div>#</div>
          <div>Selección</div>
          <div className="text-right">Composite</div>
          <div className="text-right">Casas</div>
          <div className="text-right">Compas</div>
          <div className="text-center">Forma</div>
          <div className="text-right">Movi.</div>
        </div>
      </section>

      {/* TABLA */}
      <section className="container-app pb-16">
        <LayoutGroup>
          <ul className="flex flex-col gap-1.5">
            {sortedRows.map((row, idx) => {
              const prev = prevOrder[row.code];
              const movement = prev === undefined ? 0 : prev - idx; // + = subió, - = bajó
              const isTop8 = idx < 8;
              const isBottom8 = idx >= sortedRows.length - 8;
              return (
                <RankItem
                  key={row.code}
                  rank={idx + 1}
                  row={row}
                  movement={movement}
                  isTop8={isTop8}
                  isBottom8={isBottom8}
                  expanded={expanded === row.code}
                  onToggle={() =>
                    setExpanded(prev => (prev === row.code ? null : row.code))
                  }
                  aboveAverage={row.composite >= avgComposite}
                  modelChampionPct={bracketTeams[row.code]?.pChampion}
                />
              );
            })}
          </ul>
        </LayoutGroup>

        {/* LEYENDA */}
        <div className="mt-8 glass rounded-3xl p-5">
          <div className="text-xs uppercase tracking-[0.18em] text-[var(--ink-muted)] font-semibold mb-3">
            Cómo se calcula
          </div>
          <ul className="grid sm:grid-cols-2 gap-3 text-sm text-[var(--ink-soft)]">
            <li className="flex items-start gap-2">
              <span className="mt-0.5 w-2 h-2 rounded-full shrink-0" style={{ background: "#5E5BFF" }} />
              <div><strong className="text-[var(--ink)]">Predicciones (35%):</strong> modelo interno (FIFA + Euro 2024 + Copa América + qualifying).</div>
            </li>
            <li className="flex items-start gap-2">
              <span className="mt-0.5 w-2 h-2 rounded-full shrink-0" style={{ background: "#F59E0B" }} />
              <div><strong className="text-[var(--ink)]">Casas (35%):</strong> probabilidad implícita de campeón (Bet365/Pinnacle/Caliente, mayo 2026).</div>
            </li>
            <li className="flex items-start gap-2">
              <span className="mt-0.5 w-2 h-2 rounded-full shrink-0" style={{ background: "#14F195" }} />
              <div><strong className="text-[var(--ink)]">Compas (15%):</strong> share de picks ganadores en grupos entre todos los jugadores.</div>
            </li>
            <li className="flex items-start gap-2">
              <span className="mt-0.5 w-2 h-2 rounded-full shrink-0" style={{ background: "#FF3B82" }} />
              <div><strong className="text-[var(--ink)]">En la cancha (15%):</strong> +5 por victoria real, -5 por derrota (vía ESPN).</div>
            </li>
          </ul>
        </div>
      </section>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Subcomponentes
// ---------------------------------------------------------------------------

function SortChip({
  k, active, setActive, label, icon,
}: {
  k: SortKey;
  active: SortKey;
  setActive: (k: SortKey) => void;
  label: string;
  icon: React.ReactNode;
}) {
  const isActive = active === k;
  return (
    <button
      type="button"
      onClick={() => setActive(k)}
      className={`relative px-3 py-1.5 rounded-full text-xs font-semibold inline-flex items-center gap-1.5 transition-colors ${
        isActive ? "text-white" : "text-[var(--ink-soft)] hover:text-[var(--ink)]"
      }`}
    >
      {isActive && (
        <motion.div
          layoutId="ranking-sort-pill"
          className="absolute inset-0 rounded-full"
          style={{ background: "var(--ink)" }}
          transition={{ type: "spring", duration: 0.4 }}
        />
      )}
      <span className="relative">{icon}</span>
      <span className="relative">{label}</span>
    </button>
  );
}

function RankItem({
  rank, row, movement, isTop8, isBottom8, expanded, onToggle, aboveAverage, modelChampionPct,
}: {
  rank: number;
  row: RankRow;
  movement: number;
  isTop8: boolean;
  isBottom8: boolean;
  expanded: boolean;
  onToggle: () => void;
  aboveAverage: boolean;
  modelChampionPct?: number;
}) {
  const team = TEAMS_BY_CODE[row.code];
  const router = useRouter();
  return (
    <motion.li
      layout
      transition={{ type: "spring", stiffness: 380, damping: 32 }}
      className={`relative rounded-2xl ${
        isTop8
          ? "bg-gradient-to-r from-[#FFF8E1]/70 via-white to-white ring-1 ring-[#D4AF37]/40"
          : isBottom8
            ? "bg-[var(--bg-tint)]/60 opacity-90"
            : "bg-white hairline"
      }`}
    >
      <button
        type="button"
        onClick={onToggle}
        aria-expanded={expanded}
        className="w-full text-left px-3 md:px-4 py-3 grid grid-cols-[40px_minmax(0,1fr)_70px] md:grid-cols-[40px_minmax(160px,1.4fr)_88px_88px_88px_120px_70px] items-center gap-2 md:gap-3"
      >
        {/* Rank */}
        <div className="flex items-center gap-1">
          <span className={`font-display text-lg md:text-xl font-bold tabular-nums leading-none ${
            isTop8 ? "text-[#B8860B]" : "text-[var(--ink)]"
          }`}>
            {rank}
          </span>
        </div>

        {/* Nombre + bandera */}
        <div className="flex items-center gap-3 min-w-0">
          <div
            className="relative w-9 h-9 md:w-10 md:h-10 rounded-xl overflow-hidden ring-1 ring-[var(--line)] shrink-0 cursor-pointer hover:ring-2 hover:ring-[var(--ink)] transition-all"
            onClick={(e) => { e.stopPropagation(); router.push(`/equipos/${row.code}`); }}
            title={`Ver ${row.name}`}
          >
            <Image src={flagUrl(row.flagIso, 80)} alt={row.name} fill sizes="40px" className="object-cover" unoptimized />
          </div>
          <div className="min-w-0">
            <div className="font-display text-sm md:text-base font-bold leading-none truncate">
              {row.name}
            </div>
            <div className="text-[10px] md:text-xs text-[var(--ink-muted)] mt-1 flex items-center gap-1.5">
              <span>{row.code}</span>
              <span>·</span>
              <span>Grupo {row.group}</span>
              {team?.confederation && (
                <>
                  <span className="hidden sm:inline">·</span>
                  <span className="hidden sm:inline">{team.confederation}</span>
                </>
              )}
              {typeof modelChampionPct === "number" && modelChampionPct > 0 && (
                <>
                  <span>·</span>
                  <span className="font-semibold text-[var(--ink-soft)] tabular-nums" title="Probabilidad de campeón según el modelo (Monte Carlo 10k)">
                    Modelo {(modelChampionPct * 100).toFixed(modelChampionPct >= 0.1 ? 0 : 1)}%
                  </span>
                </>
              )}
            </div>
          </div>
        </div>

        {/* Composite (mobile compact) */}
        <div className="md:hidden text-right">
          <div className="font-display text-base font-bold tabular-nums leading-none">
            {row.composite.toFixed(1)}
          </div>
          <MovementBadge movement={movement} compact />
        </div>

        {/* Composite (desktop) */}
        <div className="hidden md:flex flex-col items-end">
          <div className="font-display text-base font-bold tabular-nums">
            {row.composite.toFixed(1)}
          </div>
          <div className="w-16 h-1 rounded-full bg-[var(--bg-tint)] overflow-hidden mt-1">
            <div
              className="h-full rounded-full"
              style={{
                width: `${Math.min(100, row.composite)}%`,
                background: aboveAverage ? "var(--ink)" : "var(--line-strong)",
              }}
            />
          </div>
        </div>

        {/* Casas (desktop) */}
        <div className="hidden md:block text-right">
          <div className="text-sm font-semibold tabular-nums">{formatPct(row.bookiesPct)}</div>
          <div className="text-[10px] text-[var(--ink-muted)]">campeón</div>
        </div>

        {/* Compas (desktop) */}
        <div className="hidden md:block text-right">
          <div className="text-sm font-semibold tabular-nums">{formatPct(row.peoplePct)}</div>
          <div className="text-[10px] text-[var(--ink-muted)]">
            {row.championVotes > 0 ? `${row.championVotes} pa' campeón` : "share grupos"}
          </div>
        </div>

        {/* Forma (desktop) */}
        <div className="hidden md:flex items-center justify-center gap-1">
          {row.form.length === 0 ? (
            <span className="text-[10px] text-[var(--ink-muted)]">Sin partidos</span>
          ) : (
            row.form.map((f, i) => (
              <span
                key={i}
                className={`w-5 h-5 rounded-md text-[10px] font-bold grid place-items-center ${
                  f === "W" ? "bg-[#14F195]/25 text-[#0B7D4F]"
                  : f === "L" ? "bg-[#FF3B82]/20 text-[#A1144C]"
                  : "bg-[var(--bg-tint)] text-[var(--ink-soft)]"
                }`}
                title={f === "W" ? "Victoria" : f === "L" ? "Derrota" : "Empate"}
              >
                {f}
              </span>
            ))
          )}
        </div>

        {/* Movimiento (desktop) */}
        <div className="hidden md:flex justify-end">
          <MovementBadge movement={movement} />
        </div>
      </button>

      <AnimatePresence initial={false}>
        {expanded && (
          <motion.div
            key="details"
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.25, ease: "easeOut" }}
            className="overflow-hidden"
          >
            <div className="px-4 pb-4 pt-1">
              <div className="grid sm:grid-cols-2 gap-x-6 gap-y-2.5">
                <BreakdownBar label="Predicciones" value={row.modelScore} color="#5E5BFF" />
                <BreakdownBar label="Casas de apuesta" value={row.bookiesScore} color="#F59E0B" />
                <BreakdownBar label="Los compas" value={row.peopleScore} color="#14F195" />
                <BreakdownBar label="En la cancha" value={row.liveScore} color="#FF3B82" />
              </div>
              {TEAM_STRENGTH[row.code]?.notes && (
                <div className="mt-3 pt-3 border-t border-[var(--line)] text-xs text-[var(--ink-soft)] leading-relaxed">
                  <span className="font-semibold text-[var(--ink)]">Nota:</span> {TEAM_STRENGTH[row.code].notes}
                </div>
              )}
              <div className="mt-3 flex flex-wrap items-center gap-3 text-[10px] uppercase tracking-[0.14em] text-[var(--ink-muted)]">
                <span>Casas: <strong className="text-[var(--ink)] normal-case tracking-normal">{formatPct(row.bookiesPct)}</strong></span>
                <span>Compas (grupos): <strong className="text-[var(--ink)] normal-case tracking-normal">{formatPct(row.peoplePct)}</strong></span>
                <span>Votos campeón: <strong className="text-[var(--ink)] normal-case tracking-normal">{row.championVotes}</strong></span>
                <span>Δ cancha: <strong className="text-[var(--ink)] normal-case tracking-normal">{row.liveDelta > 0 ? `+${row.liveDelta.toFixed(0)}` : row.liveDelta.toFixed(0)}</strong></span>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.li>
  );
}

function BreakdownBar({ label, value, color }: { label: string; value: number; color: string }) {
  return (
    <div>
      <div className="flex items-center justify-between text-xs mb-1">
        <span className="text-[var(--ink-soft)]">{label}</span>
        <span className="font-semibold tabular-nums">{value.toFixed(0)}</span>
      </div>
      <div className="h-2 rounded-full bg-[var(--bg-tint)] overflow-hidden">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${Math.max(0, Math.min(100, value))}%` }}
          transition={{ duration: 0.5, ease: "easeOut" }}
          className="h-full rounded-full"
          style={{ background: color }}
        />
      </div>
    </div>
  );
}

function MovementBadge({ movement, compact }: { movement: number; compact?: boolean }) {
  if (movement === 0) {
    return (
      <span className={`inline-flex items-center gap-0.5 text-[10px] text-[var(--ink-muted)] ${compact ? "justify-end" : ""}`}>
        <Minus size={10} />
      </span>
    );
  }
  const up = movement > 0;
  return (
    <span
      className={`inline-flex items-center gap-0.5 text-[10px] font-bold ${
        up ? "text-[#0B7D4F]" : "text-[#A1144C]"
      } ${compact ? "justify-end" : ""}`}
    >
      {up ? <ArrowUp size={11} /> : <ArrowDown size={11} />}
      {Math.abs(movement)}
    </span>
  );
}

function formatPct(v: number): string {
  if (v >= 10) return `${v.toFixed(0)}%`;
  if (v >= 1) return `${v.toFixed(1)}%`;
  if (v > 0) return `${v.toFixed(2)}%`;
  return "0%";
}

// Marca a BOOKMAKER_CHAMPION_PROB como usada (helper export para uso futuro).
export const __snapshot_marker = BOOKMAKER_CHAMPION_PROB;
