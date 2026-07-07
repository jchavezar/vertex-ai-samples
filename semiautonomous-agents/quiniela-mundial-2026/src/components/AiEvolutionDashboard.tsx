"use client";

// Owner-only AI Evolution dashboard. Renders the timeline of how the AI bot's
// picks have churned across cron runs. Three panes:
//   1) Top stats band  — at-a-glance metrics.
//   2) Run timeline    — reverse-chrono buckets, each expandable to show the
//                        list of fixtures the bot changed in that run.
//   3) Per-fixture     — every fixture the bot has touched, sorted by
//                        # of pick flips (the noisiest first), each row
//                        collapses to show the full snapshot chain.
//
// All data comes from /api/admin/ai-evolution. The endpoint is server-gated
// to playerId === "jesus" so a 401/403 means "not signed in as admin".

import { useCallback, useEffect, useMemo, useState } from "react";
import Link from "next/link";
import {
  ArrowLeft, RefreshCcw, Loader2, History, Activity, Target, Flame,
  ChevronDown, ChevronRight, CheckCircle2, XCircle, Star, AlertTriangle,
} from "lucide-react";
import { AnimatePresence, motion } from "framer-motion";
import { TEAMS_BY_CODE } from "@/data/teams";

type Pick = "H" | "D" | "A";

type Snapshot = {
  fixtureId: string;
  ts: number;
  pick: Pick;
  homeGoals?: number;
  awayGoals?: number;
  confidence?: number;
  reasoning?: string;
  prevPick?: Pick | null;
  prevReasoning?: string | null;
  source?: string;
  blendedProbs?: { H: number; D: number; A: number };
  reasonerModel?: string;
};

type RunChange = {
  fixtureId: string;
  home: string;
  away: string;
  prevPick: Pick | null;
  newPick: Pick;
  prevScore: string | null;
  newScore: string;
  reasoning: string;
  confidence: number | null;
  source: string;
};

type RunBucket = { ts: number; changes: RunChange[]; total: number; initials: number };

type PerFixtureRow = {
  fixtureId: string;
  home: string;
  away: string;
  date: string;
  group: string;
  matchday: 1 | 2 | 3;
  snapshots: Snapshot[];
  currentPick?: Pick;
  currentScore?: string;
  changes: number;
  actual?: { pick: Pick; homeGoals: number; awayGoals: number; score: string };
  initialPick?: Pick;
  initialCorrect?: boolean;
  finalCorrect?: boolean;
  verdict?: "exact" | "hit" | "miss";
};

type Stats = {
  totalFixtures: number;
  fixturesWithChanges: number;
  avgChangesPerFixture: number;
  aggressivenessScore: number;
  accuracyAll: number | null;
  accuracyChanged: number | null;
  accuracyStable: number | null;
  finishedFixtures: number;
};

type Payload = {
  ok: true;
  generatedAt: number;
  runs: RunBucket[];
  perFixture: PerFixtureRow[];
  stats: Stats;
};

function fmtTs(ts: number): string {
  return new Intl.DateTimeFormat("es-MX", {
    timeZone: "America/Mexico_City",
    year: "numeric", month: "short", day: "2-digit",
    hour: "2-digit", minute: "2-digit",
  }).format(new Date(ts));
}

function fmtRelative(ts: number): string {
  const diffMs = Date.now() - ts;
  const mins = Math.round(diffMs / 60000);
  if (mins < 1) return "hace segundos";
  if (mins < 60) return `hace ${mins} min`;
  const hours = Math.round(mins / 60);
  if (hours < 24) return `hace ${hours} h`;
  const days = Math.round(hours / 24);
  return `hace ${days} d`;
}

function pickLabel(p: Pick | null | undefined): string {
  if (!p) return "—";
  return p === "H" ? "Local" : p === "A" ? "Visita" : "Empate";
}

function teamName(code: string): string {
  return TEAMS_BY_CODE[code]?.name ?? code;
}

function pickColor(p: Pick | null | undefined): string {
  if (!p) return "var(--ink-muted)";
  if (p === "H") return "#5E5BFF";
  if (p === "A") return "#E11D48";
  return "#0EA5E9";
}

function fmtPct(n: number | null | undefined): string {
  if (n == null || !Number.isFinite(n)) return "—";
  return `${Math.round(n * 100)}%`;
}

export function AiEvolutionDashboard() {
  const [data, setData] = useState<Payload | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [openRun, setOpenRun] = useState<number | null>(null);
  const [openFx, setOpenFx] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const r = await fetch("/api/admin/ai-evolution", { cache: "no-store" });
      if (r.status === 401 || r.status === 403) {
        setError("Solo admin");
        setData(null);
        return;
      }
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      const j = (await r.json()) as Payload | { ok: false; error?: string };
      if ("ok" in j && j.ok) {
        setData(j);
      } else {
        setError(("error" in j && j.error) || "Error desconocido");
      }
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  const hasHistory = !!data && (data.runs.length > 0 || data.perFixture.length > 0);

  // Auto-expand the most recent run on first load.
  useEffect(() => {
    if (data && data.runs.length > 0 && openRun === null) {
      setOpenRun(data.runs[0].ts);
    }
  }, [data, openRun]);

  return (
    <main className="min-h-screen bg-[var(--bg)] pb-16">
      <section className="max-w-6xl mx-auto px-4 pt-6">
        <div className="flex items-center justify-between gap-3 flex-wrap">
          <div>
            <div className="text-[10px] uppercase tracking-[0.25em] text-[var(--ink-muted)] font-bold">
              Admin · evolución del bot
            </div>
            <h1 className="font-display text-2xl sm:text-3xl font-black text-[var(--ink)] flex items-center gap-2">
              <Flame className="w-6 h-6 text-[#E11D48]" />
              AI Evolution
            </h1>
            <div className="text-sm text-[var(--ink-soft)] mt-1">
              Cada vez que el bot cambia su pick, queda registro. Aquí ves cómo lee el torneo en el tiempo.
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={load}
              disabled={loading}
              className="inline-flex items-center gap-1.5 px-3 py-2 rounded-full text-xs font-bold glass-strong text-[var(--ink)] hover:bg-white disabled:opacity-50"
            >
              {loading ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <RefreshCcw className="w-3.5 h-3.5" />}
              Refrescar
            </button>
            <Link
              href="/admin/stats"
              className="inline-flex items-center gap-1.5 text-xs font-semibold text-[var(--ink-soft)] hover:text-[var(--ink)]"
            >
              <ArrowLeft className="w-3.5 h-3.5" /> Stats
            </Link>
          </div>
        </div>

        {error && (
          <div className="mt-6 rounded-2xl glass-strong p-4 flex items-center gap-2 text-sm text-[var(--ink)]">
            <AlertTriangle className="w-4 h-4 text-amber-500" />
            <span className="font-bold">{error}</span>
          </div>
        )}

        {!error && !loading && !hasHistory && (
          <div className="mt-6 rounded-2xl glass-strong p-8 text-center">
            <History className="w-8 h-8 mx-auto text-[var(--ink-muted)]" />
            <div className="mt-2 text-sm font-bold text-[var(--ink)]">Sin historial todavía</div>
            <div className="mt-1 text-xs text-[var(--ink-soft)]">
              Cuando el cron `/api/cron/ai-refresh` corra, los cambios del bot empezarán a aparecer acá.
            </div>
          </div>
        )}

        {data && hasHistory && (
          <>
            <StatsBand stats={data.stats} />
            <RunsTimeline
              runs={data.runs}
              openRun={openRun}
              onToggle={(ts) => setOpenRun(prev => prev === ts ? null : ts)}
            />
            <PerFixturePane
              rows={data.perFixture}
              openFx={openFx}
              onToggle={(id) => setOpenFx(prev => prev === id ? null : id)}
            />
            <div className="mt-6 text-[10px] text-[var(--ink-muted)] text-right">
              Generado {fmtTs(data.generatedAt)} · {fmtRelative(data.generatedAt)}
            </div>
          </>
        )}
      </section>
    </main>
  );
}

/* ─────────────────────────────────────────────────────────────────────── */

function StatsBand({ stats }: { stats: Stats }) {
  const cards: Array<{ label: string; value: string; sub?: string; icon: React.ReactNode; tint?: string }> = [
    {
      label: "Fixtures pickeados",
      value: stats.totalFixtures.toString(),
      icon: <Target className="w-4 h-4" />,
    },
    {
      label: "Fixtures con cambios",
      value: stats.fixturesWithChanges.toString(),
      sub: `prom ${stats.avgChangesPerFixture.toFixed(2)}/fix`,
      icon: <History className="w-4 h-4" />,
      tint: "#5E5BFF",
    },
    {
      label: "Agresividad",
      value: fmtPct(stats.aggressivenessScore),
      sub: "vs argmax(blended)",
      icon: <Flame className="w-4 h-4" />,
      tint: "#E11D48",
    },
    {
      label: "Accuracy global",
      value: fmtPct(stats.accuracyAll),
      sub: `${stats.finishedFixtures} jugados`,
      icon: <Activity className="w-4 h-4" />,
      tint: "#22C55E",
    },
    {
      label: "Acc. cambiados",
      value: fmtPct(stats.accuracyChanged),
      sub: "pick flipeado",
      icon: <CheckCircle2 className="w-4 h-4" />,
      tint: "#0EA5E9",
    },
    {
      label: "Acc. estables",
      value: fmtPct(stats.accuracyStable),
      sub: "nunca cambió",
      icon: <CheckCircle2 className="w-4 h-4" />,
      tint: "#8B5CF6",
    },
  ];

  return (
    <div className="mt-5 grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2.5">
      {cards.map((c) => (
        <div key={c.label} className="rounded-2xl glass-strong p-3">
          <div className="flex items-center gap-1.5 text-[10px] uppercase tracking-wider text-[var(--ink-muted)] font-bold">
            <span style={{ color: c.tint ?? "var(--ink-soft)" }}>{c.icon}</span>
            <span>{c.label}</span>
          </div>
          <div className="mt-1.5 text-xl sm:text-2xl font-black text-[var(--ink)] tabular-nums">{c.value}</div>
          {c.sub && <div className="text-[10px] text-[var(--ink-muted)] mt-0.5">{c.sub}</div>}
        </div>
      ))}
    </div>
  );
}

/* ─────────────────────────────────────────────────────────────────────── */

function RunsTimeline({
  runs, openRun, onToggle,
}: {
  runs: RunBucket[];
  openRun: number | null;
  onToggle: (ts: number) => void;
}) {
  return (
    <section className="mt-8">
      <div className="flex items-baseline justify-between mb-2">
        <h2 className="font-display text-lg font-black text-[var(--ink)]">Timeline de corridas</h2>
        <div className="text-[10px] text-[var(--ink-muted)] uppercase tracking-wider">{runs.length} runs</div>
      </div>
      <div className="rounded-2xl glass-strong overflow-hidden divide-y divide-[var(--line)]">
        {runs.map((run) => {
          const isOpen = openRun === run.ts;
          const flips = run.changes.filter(c => c.source !== "initial").length;
          return (
            <div key={run.ts}>
              <button
                type="button"
                onClick={() => onToggle(run.ts)}
                className="w-full px-4 py-3 flex items-center justify-between gap-3 text-left hover:bg-white/40 transition-colors"
              >
                <div className="flex items-center gap-2 min-w-0">
                  {isOpen
                    ? <ChevronDown className="w-4 h-4 text-[var(--ink-soft)] shrink-0" />
                    : <ChevronRight className="w-4 h-4 text-[var(--ink-soft)] shrink-0" />}
                  <div className="min-w-0">
                    <div className="text-sm font-bold text-[var(--ink)] truncate">{fmtTs(run.ts)}</div>
                    <div className="text-[11px] text-[var(--ink-muted)]">{fmtRelative(run.ts)}</div>
                  </div>
                </div>
                <div className="flex items-center gap-2 text-[11px] font-bold shrink-0">
                  {flips > 0 && (
                    <span className="px-2 py-0.5 rounded-full" style={{ background: "rgba(225,29,72,0.12)", color: "#E11D48" }}>
                      {flips} flip{flips === 1 ? "" : "s"}
                    </span>
                  )}
                  {run.initials > 0 && (
                    <span className="px-2 py-0.5 rounded-full bg-[var(--ink)]/5 text-[var(--ink-soft)]">
                      {run.initials} init
                    </span>
                  )}
                  <span className="text-[var(--ink-muted)] tabular-nums">{run.total}</span>
                </div>
              </button>
              <AnimatePresence initial={false}>
                {isOpen && (
                  <motion.div
                    key="body"
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: "auto", opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.2, ease: "easeOut" }}
                    className="overflow-hidden"
                  >
                    <ul className="px-4 pb-3 space-y-2">
                      {run.changes.length === 0 && (
                        <li className="text-xs text-[var(--ink-muted)] italic">Sin cambios.</li>
                      )}
                      {run.changes.map((c, i) => (
                        <li key={`${c.fixtureId}-${i}`} className="rounded-xl bg-white/60 hairline-strong p-3">
                          <div className="flex items-center justify-between gap-2 text-xs">
                            <div className="font-bold text-[var(--ink)] truncate">
                              {c.fixtureId} · {teamName(c.home)} vs {teamName(c.away)}
                            </div>
                            <div className="flex items-center gap-1 shrink-0">
                              <span
                                className="px-2 py-0.5 rounded-full font-bold text-[10px]"
                                style={{ background: "rgba(0,0,0,0.06)", color: pickColor(c.prevPick) }}
                              >
                                {pickLabel(c.prevPick)}
                              </span>
                              <ChevronRight className="w-3 h-3 text-[var(--ink-muted)]" />
                              <span
                                className="px-2 py-0.5 rounded-full font-bold text-[10px]"
                                style={{ background: "rgba(0,0,0,0.06)", color: pickColor(c.newPick) }}
                              >
                                {pickLabel(c.newPick)} {c.newScore && `· ${c.newScore}`}
                              </span>
                            </div>
                          </div>
                          {c.reasoning && (
                            <div className="mt-1.5 text-[12px] text-[var(--ink-soft)] leading-snug">
                              {c.reasoning}
                            </div>
                          )}
                          <div className="mt-1 flex items-center gap-2 text-[10px] text-[var(--ink-muted)]">
                            <span>{c.source}</span>
                            {c.confidence != null && <span>· conf {Math.round(c.confidence * 100)}%</span>}
                          </div>
                        </li>
                      ))}
                    </ul>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          );
        })}
      </div>
    </section>
  );
}

/* ─────────────────────────────────────────────────────────────────────── */

function PerFixturePane({
  rows, openFx, onToggle,
}: {
  rows: PerFixtureRow[];
  openFx: string | null;
  onToggle: (id: string) => void;
}) {
  const [filter, setFilter] = useState<"all" | "changed" | "finished">("all");
  const filtered = useMemo(() => {
    if (filter === "changed") return rows.filter(r => r.changes > 0);
    if (filter === "finished") return rows.filter(r => !!r.actual);
    return rows;
  }, [rows, filter]);

  return (
    <section className="mt-8">
      <div className="flex items-baseline justify-between mb-2 gap-3 flex-wrap">
        <h2 className="font-display text-lg font-black text-[var(--ink)]">Por fixture</h2>
        <div className="inline-flex rounded-full hairline-strong bg-white p-0.5 text-[11px] font-bold">
          {(["all", "changed", "finished"] as const).map(k => (
            <button
              key={k}
              type="button"
              onClick={() => setFilter(k)}
              className={`px-3 py-1 rounded-full transition-colors ${
                filter === k ? "bg-[var(--ink)] text-white" : "text-[var(--ink-soft)] hover:text-[var(--ink)]"
              }`}
            >
              {k === "all" ? "Todos" : k === "changed" ? "Con cambios" : "Jugados"}
            </button>
          ))}
        </div>
      </div>
      <div className="rounded-2xl glass-strong overflow-hidden divide-y divide-[var(--line)]">
        {filtered.length === 0 && (
          <div className="p-6 text-center text-sm text-[var(--ink-muted)]">Sin filas.</div>
        )}
        {filtered.map((r) => {
          const isOpen = openFx === r.fixtureId;
          return (
            <div key={r.fixtureId}>
              <button
                type="button"
                onClick={() => onToggle(r.fixtureId)}
                className="w-full px-4 py-3 flex items-center justify-between gap-3 text-left hover:bg-white/40 transition-colors"
              >
                <div className="flex items-center gap-2 min-w-0">
                  {isOpen
                    ? <ChevronDown className="w-4 h-4 text-[var(--ink-soft)] shrink-0" />
                    : <ChevronRight className="w-4 h-4 text-[var(--ink-soft)] shrink-0" />}
                  <div className="min-w-0">
                    <div className="text-sm font-bold text-[var(--ink)] truncate">
                      {r.fixtureId} · {teamName(r.home)} vs {teamName(r.away)}
                    </div>
                    <div className="text-[11px] text-[var(--ink-muted)]">
                      Grupo {r.group} · J{r.matchday} · {r.date}
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-2 text-[11px] font-bold shrink-0">
                  <span className="px-2 py-0.5 rounded-full bg-[var(--ink)]/5 text-[var(--ink-soft)]">
                    {r.changes} cambio{r.changes === 1 ? "" : "s"}
                  </span>
                  {r.currentPick && (
                    <span
                      className="px-2 py-0.5 rounded-full font-bold"
                      style={{ background: "rgba(0,0,0,0.06)", color: pickColor(r.currentPick) }}
                    >
                      {pickLabel(r.currentPick)} {r.currentScore && `· ${r.currentScore}`}
                    </span>
                  )}
                  {r.verdict && <VerdictBadge v={r.verdict} />}
                </div>
              </button>
              <AnimatePresence initial={false}>
                {isOpen && (
                  <motion.div
                    key="body"
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: "auto", opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.2, ease: "easeOut" }}
                    className="overflow-hidden"
                  >
                    <FixtureChain row={r} />
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          );
        })}
      </div>
    </section>
  );
}

function VerdictBadge({ v }: { v: "exact" | "hit" | "miss" }) {
  if (v === "exact") {
    return (
      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold" style={{ background: "rgba(234,179,8,0.18)", color: "#A16207" }}>
        <Star className="w-3 h-3" /> exacto
      </span>
    );
  }
  if (v === "hit") {
    return (
      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold" style={{ background: "rgba(34,197,94,0.16)", color: "#15803D" }}>
        <CheckCircle2 className="w-3 h-3" /> acierto
      </span>
    );
  }
  return (
    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold" style={{ background: "rgba(225,29,72,0.14)", color: "#BE123C" }}>
      <XCircle className="w-3 h-3" /> falló
    </span>
  );
}

function FixtureChain({ row }: { row: PerFixtureRow }) {
  return (
    <div className="px-4 pb-4">
      {row.snapshots.length === 0 && (
        <div className="text-xs text-[var(--ink-muted)] italic">
          Sin snapshots — el bot tiene un pick actual pero todavía no hubo ningún cambio registrado.
        </div>
      )}
      {row.snapshots.length > 0 && (
        <ol className="relative pl-4 space-y-2.5 border-l-2 border-[var(--line)]">
          {row.snapshots.map((s, i) => {
            const isInitial = i === 0;
            const flipped = i > 0 && row.snapshots[i - 1].pick !== s.pick;
            return (
              <li key={`${s.fixtureId}-${s.ts}-${i}`} className="relative">
                <span
                  className="absolute -left-[21px] top-1.5 w-3 h-3 rounded-full border-2 border-white"
                  style={{ background: isInitial ? "var(--ink)" : flipped ? "#E11D48" : "var(--ink-muted)" }}
                />
                <div className="rounded-xl bg-white/60 hairline-strong p-2.5">
                  <div className="flex items-center justify-between gap-2 text-[11px]">
                    <div className="font-bold text-[var(--ink)]">
                      {fmtTs(s.ts)} <span className="font-normal text-[var(--ink-muted)]">· {isInitial ? "inicial" : flipped ? "FLIP" : "ajuste"}</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <span
                        className="px-2 py-0.5 rounded-full font-bold"
                        style={{ background: "rgba(0,0,0,0.06)", color: pickColor(s.pick) }}
                      >
                        {pickLabel(s.pick)}{typeof s.homeGoals === "number" && typeof s.awayGoals === "number" ? ` · ${s.homeGoals}-${s.awayGoals}` : ""}
                      </span>
                      {s.confidence != null && (
                        <span className="text-[10px] text-[var(--ink-muted)] tabular-nums">{Math.round(s.confidence * 100)}%</span>
                      )}
                    </div>
                  </div>
                  {s.reasoning && (
                    <div className="mt-1 text-[12px] text-[var(--ink-soft)] leading-snug">{s.reasoning}</div>
                  )}
                  {s.blendedProbs && (
                    <div className="mt-1 text-[10px] text-[var(--ink-muted)] tabular-nums">
                      blend H {Math.round(s.blendedProbs.H * 100)}% · D {Math.round(s.blendedProbs.D * 100)}% · A {Math.round(s.blendedProbs.A * 100)}%
                      {s.reasonerModel && ` · ${s.reasonerModel}`}
                    </div>
                  )}
                </div>
              </li>
            );
          })}
          {row.actual && (
            <li className="relative">
              <span className="absolute -left-[21px] top-1.5 w-3 h-3 rounded-full border-2 border-white bg-[#22C55E]" />
              <div className="rounded-xl p-2.5" style={{ background: "rgba(34,197,94,0.10)" }}>
                <div className="text-[11px] font-bold text-[#15803D]">
                  Resultado real · {row.actual.score} · ganador {pickLabel(row.actual.pick)}
                </div>
                {row.initialPick && row.currentPick && (
                  <div className="mt-1 text-[11px] text-[var(--ink-soft)]">
                    Pick inicial: <b style={{ color: pickColor(row.initialPick) }}>{pickLabel(row.initialPick)}</b>
                    {" "}({row.initialCorrect ? "✓" : "✗"}) · Pick final: <b style={{ color: pickColor(row.currentPick) }}>{pickLabel(row.currentPick)}</b>
                    {" "}({row.finalCorrect ? "✓" : "✗"})
                  </div>
                )}
              </div>
            </li>
          )}
        </ol>
      )}
    </div>
  );
}
