"use client";

// "Uso" tab for the owner stats dashboard. Lives in its own file to keep
// StatsDashboard.tsx focused on its existing payload. Renders KPIs + bars +
// heatmap from /api/admin/usage with the same 60s auto-refresh cadence.

import { useCallback, useEffect, useMemo, useState } from "react";
import {
  Activity, Eye, Users, Loader2, RefreshCcw, MousePointerClick, Map as MapIcon,
} from "lucide-react";
import { PLAYERS } from "@/data/players";
import { PlayerAvatar } from "@/components/PlayerAvatar";

type PerPlayerUsage = {
  id: string;
  name: string;
  isBot: boolean;
  events: number;
  sessions: number;
  lastSeen: number | null;
  avgSessionSec: number;
  topFeatures: { event: string; count: number }[];
};

type PerDayUsage = { date: string; events: number; sessions: number; uniquePlayers: number };

type UsagePayload = {
  generatedAt: number;
  rangeDays: number;
  totalEvents: number;
  uniqueSessions: number;
  eventCountsGlobal: { event: string; count: number }[];
  perPlayer: PerPlayerUsage[];
  perDay: PerDayUsage[];
  heatmap: { players: string[]; features: string[]; matrix: number[][] };
  pageViews: { path: string; count: number }[];
};

type UsageSort = "events" | "sessions" | "duration" | "lastSeen" | "name";

function shortDay(d: string): string {
  const [, m, day] = d.split("-");
  return `${parseInt(day, 10)}/${parseInt(m, 10)}`;
}

function relative(ms: number | null): string {
  if (!ms) return "—";
  const diff = Date.now() - ms;
  if (diff < 60_000) return "ahora";
  const min = Math.floor(diff / 60_000);
  if (min < 60) return `${min} min`;
  const h = Math.floor(min / 60);
  if (h < 24) return `${h} h`;
  const days = Math.floor(h / 24);
  if (days < 30) return `${days} d`;
  return `${Math.floor(days / 30)} mes`;
}

function durationLabel(sec: number): string {
  if (sec <= 0) return "—";
  if (sec < 60) return `${sec}s`;
  const m = Math.floor(sec / 60);
  const rem = sec % 60;
  if (m < 60) return rem > 0 ? `${m}m ${rem}s` : `${m}m`;
  const h = Math.floor(m / 60);
  return `${h}h ${m % 60}m`;
}

function HorizontalBars({ rows }: { rows: { label: string; value: number }[] }) {
  const max = Math.max(1, ...rows.map((r) => r.value));
  return (
    <ul className="space-y-1.5">
      {rows.map((r) => {
        const pct = (r.value / max) * 100;
        return (
          <li key={r.label} className="grid grid-cols-[180px,1fr,40px] items-center gap-2 text-xs">
            <span className="truncate text-[var(--ink-soft)] font-medium">{r.label}</span>
            <div className="h-3 bg-[var(--bg-tint)] rounded-md overflow-hidden">
              <div
                className="h-full rounded-md"
                style={{ width: `${pct}%`, background: "var(--accent-violet)" }}
              />
            </div>
            <span className="text-right tabular-nums font-bold text-[var(--ink)]">{r.value}</span>
          </li>
        );
      })}
    </ul>
  );
}

function DayBars({ rows }: { rows: PerDayUsage[] }) {
  const height = 130;
  const max = Math.max(1, ...rows.map((r) => r.events));
  const barW = 100 / Math.max(1, rows.length);
  return (
    <svg viewBox={`0 0 100 ${height}`} preserveAspectRatio="none" className="w-full" style={{ height }}>
      {rows.map((b, i) => {
        const v = b.events;
        const h = (v / max) * (height - 18);
        const x = i * barW + barW * 0.18;
        const w = barW * 0.64;
        const y = height - 8 - h;
        return (
          <g key={b.date}>
            <rect x={x} y={y} width={w} height={h} fill="var(--accent-violet)" opacity={v === 0 ? 0.18 : 0.9} rx="0.6" />
            {v > 0 ? (
              <text x={x + w / 2} y={y - 1} fontSize="2.8" textAnchor="middle" fill="var(--ink)">
                {v}
              </text>
            ) : null}
            <text x={x + w / 2} y={height - 1} fontSize="3" textAnchor="middle" fill="var(--ink-muted)">
              {shortDay(b.date)}
            </text>
          </g>
        );
      })}
    </svg>
  );
}

function Heatmap({
  players, features, matrix,
}: { players: string[]; features: string[]; matrix: number[][] }) {
  // Log intensity so heavy users don't drown out light ones visually.
  const flat = matrix.flat();
  const maxV = Math.max(1, ...flat);
  const logMax = Math.log(1 + maxV);
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-[11px] border-separate" style={{ borderSpacing: 2 }}>
        <thead>
          <tr>
            <th className="text-left p-1 text-[10px] uppercase tracking-wider text-[var(--ink-muted)]"></th>
            {features.map((f) => (
              <th key={f} className="p-1 text-left text-[10px] uppercase tracking-wider text-[var(--ink-muted)] whitespace-nowrap">
                {f}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {players.map((p, pi) => (
            <tr key={p}>
              <td className="pr-2 text-[var(--ink)] font-semibold whitespace-nowrap">{p}</td>
              {features.map((f, fi) => {
                const v = matrix[pi]?.[fi] ?? 0;
                const intensity = v <= 0 ? 0 : Math.log(1 + v) / logMax;
                const bg =
                  v <= 0
                    ? "var(--bg-tint)"
                    : `color-mix(in srgb, var(--accent-violet) ${Math.round(intensity * 88)}%, transparent)`;
                const fg = intensity > 0.55 ? "#fff" : "var(--ink)";
                return (
                  <td
                    key={f}
                    className="text-center tabular-nums rounded-md font-bold"
                    style={{
                      background: bg,
                      color: fg,
                      padding: "6px 8px",
                      minWidth: 42,
                    }}
                    title={`${p} · ${f}: ${v}`}
                  >
                    {v > 0 ? v : ""}
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export function UsageTab() {
  const [data, setData] = useState<UsagePayload | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sortKey, setSortKey] = useState<UsageSort>("events");
  const [sortDir, setSortDir] = useState<"asc" | "desc">("desc");

  const load = useCallback(async (silent = false) => {
    if (silent) setRefreshing(true); else setLoading(true);
    setError(null);
    try {
      const r = await fetch("/api/admin/usage", { cache: "no-store" });
      if (!r.ok) {
        setError(r.status === 404 ? "forbidden" : `error_${r.status}`);
        return;
      }
      const j = (await r.json()) as UsagePayload;
      setData(j);
    } catch {
      setError("network");
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => { load(); }, [load]);
  useEffect(() => {
    const t = setInterval(() => load(true), 60_000);
    return () => clearInterval(t);
  }, [load]);

  const sortedPlayers = useMemo(() => {
    if (!data) return [];
    const arr = [...data.perPlayer];
    const dir = sortDir === "asc" ? 1 : -1;
    arr.sort((a, b) => {
      switch (sortKey) {
        case "name": return a.name.localeCompare(b.name) * dir;
        case "sessions": return (a.sessions - b.sessions) * dir;
        case "duration": return (a.avgSessionSec - b.avgSessionSec) * dir;
        case "lastSeen": return ((a.lastSeen ?? 0) - (b.lastSeen ?? 0)) * dir;
        case "events":
        default: return (a.events - b.events) * dir;
      }
    });
    return arr;
  }, [data, sortKey, sortDir]);

  function sortBy(k: UsageSort) {
    if (sortKey === k) setSortDir(d => d === "asc" ? "desc" : "asc");
    else { setSortKey(k); setSortDir("desc"); }
  }
  function sortArrow(k: UsageSort): string {
    if (sortKey !== k) return "";
    return sortDir === "asc" ? "↑" : "↓";
  }

  if (loading && !data) {
    return (
      <div className="py-10 flex items-center justify-center text-[var(--ink-muted)] text-sm gap-2">
        <Loader2 size={16} className="animate-spin" /> Cargando uso…
      </div>
    );
  }
  if (error || !data) {
    return (
      <div className="py-10 text-center text-[var(--ink-muted)] text-sm">
        No hay datos {error ? <>· <span className="text-red-400">{error}</span></> : null}
      </div>
    );
  }

  const activePlayers = data.perPlayer.filter((p) => p.events > 0).length;
  const featureRows = data.eventCountsGlobal.slice(0, 15).map((e) => ({ label: e.event, value: e.count }));
  const pageRows = data.pageViews.slice(0, 20).map((p) => ({ label: p.path, value: p.count }));

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-end">
        <button
          type="button"
          onClick={() => load(true)}
          disabled={refreshing}
          className="chip gap-1.5"
          style={{ color: "var(--accent-violet)" }}
        >
          {refreshing ? <Loader2 size={11} className="animate-spin" /> : <RefreshCcw size={11} />}
          Refrescar uso
        </button>
      </div>

      <section className="grid grid-cols-2 md:grid-cols-3 gap-3">
        <KpiUsage icon={<MousePointerClick size={18} />} accent="var(--accent-violet)"
          label="Eventos · 14d" value={`${data.totalEvents}`} sub={`${data.rangeDays}d ventana`} />
        <KpiUsage icon={<Activity size={18} />} accent="var(--accent-mint)"
          label="Sesiones únicas" value={`${data.uniqueSessions}`} sub="por tab" />
        <KpiUsage icon={<Users size={18} />} accent="var(--accent-gold)"
          label="Jugadores activos" value={`${activePlayers}`} sub={`${data.perPlayer.length} totales`} />
      </section>

      <section className="glass-strong rounded-3xl p-5">
        <div className="flex items-center justify-between mb-3">
          <h2 className="font-bold text-[var(--ink)] flex items-center gap-2">
            <Activity size={16} /> Eventos por día · {data.rangeDays}d
          </h2>
        </div>
        <DayBars rows={data.perDay} />
        <div className="mt-2 flex items-center gap-3 text-[10px] uppercase tracking-wider text-[var(--ink-muted)] tabular-nums">
          <span>{data.perDay.reduce((s, b) => s + b.sessions, 0)} sesiones suma</span>
          <span>·</span>
          <span>{data.perDay.reduce((s, b) => s + b.uniquePlayers, 0)} jugadores·día acumulados</span>
        </div>
      </section>

      <section className="grid grid-cols-1 md:grid-cols-2 gap-3">
        <div className="glass-strong rounded-3xl p-5">
          <h2 className="font-bold text-[var(--ink)] flex items-center gap-2 mb-3">
            <Activity size={16} /> Top features
          </h2>
          {featureRows.length > 0 ? <HorizontalBars rows={featureRows} /> : <Empty />}
        </div>
        <div className="glass-strong rounded-3xl p-5">
          <h2 className="font-bold text-[var(--ink)] flex items-center gap-2 mb-3">
            <Eye size={16} /> Top rutas
          </h2>
          {pageRows.length > 0 ? <HorizontalBars rows={pageRows} /> : <Empty />}
        </div>
      </section>

      <section className="glass-strong rounded-3xl p-4 md:p-5 overflow-x-auto">
        <div className="flex items-center justify-between gap-2 mb-3">
          <h2 className="font-bold text-[var(--ink)] flex items-center gap-2">
            <Users size={16} /> Engagement por jugador
          </h2>
          <span className="text-[10px] uppercase tracking-wider text-[var(--ink-muted)]">click columna p/ordenar</span>
        </div>
        <table className="w-full min-w-[720px] text-sm">
          <thead>
            <tr className="text-[10px] uppercase tracking-wider text-[var(--ink-muted)] border-b border-white/10">
              <th onClick={() => sortBy("name")} className="text-left py-2 pr-2 cursor-pointer select-none">Jugador {sortArrow("name")}</th>
              <th onClick={() => sortBy("events")} className="text-right py-2 px-2 cursor-pointer select-none">Eventos {sortArrow("events")}</th>
              <th onClick={() => sortBy("sessions")} className="text-right py-2 px-2 cursor-pointer select-none">Sesiones {sortArrow("sessions")}</th>
              <th onClick={() => sortBy("duration")} className="text-right py-2 px-2 cursor-pointer select-none">Dur. prom {sortArrow("duration")}</th>
              <th onClick={() => sortBy("lastSeen")} className="text-right py-2 px-2 cursor-pointer select-none">Últ. visto {sortArrow("lastSeen")}</th>
              <th className="text-left py-2 pl-2">Top features</th>
            </tr>
          </thead>
          <tbody>
            {sortedPlayers.map((p) => {
              const meta = PLAYERS.find((pl) => pl.id === p.id);
              return (
                <tr key={p.id} className="border-b border-white/5 hover:bg-white/5 transition">
                  <td className="py-2 pr-2">
                    <div className="flex items-center gap-2 font-semibold text-[var(--ink)]">
                      {meta ? (
                        <PlayerAvatar player={meta} size={28} rounded="rounded-full" tint={0.18} />
                      ) : (
                        <span className="w-7 h-7 rounded-full bg-[var(--bg-tint)] grid place-items-center text-[10px]">?</span>
                      )}
                      <span className="truncate">{p.name}</span>
                      {p.isBot ? <span className="chip text-[9px]" style={{ color: "var(--accent-violet)" }}>BOT</span> : null}
                      {p.id === "_anon" ? <span className="chip text-[9px]" style={{ color: "var(--ink-muted)" }}>anon</span> : null}
                    </div>
                  </td>
                  <td className="py-2 px-2 text-right tabular-nums font-bold">{p.events}</td>
                  <td className="py-2 px-2 text-right tabular-nums">{p.sessions}</td>
                  <td className="py-2 px-2 text-right tabular-nums text-[var(--ink-muted)]">{durationLabel(p.avgSessionSec)}</td>
                  <td className="py-2 px-2 text-right tabular-nums text-[var(--ink-muted)]">{relative(p.lastSeen)}</td>
                  <td className="py-2 pl-2">
                    <div className="flex flex-wrap gap-1">
                      {p.topFeatures.slice(0, 5).map((f) => (
                        <span key={f.event} className="chip text-[10px]">
                          {f.event} <span className="tabular-nums">{f.count}</span>
                        </span>
                      ))}
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </section>

      <section className="glass-strong rounded-3xl p-4 md:p-5 overflow-x-auto">
        <div className="flex items-center justify-between gap-2 mb-3">
          <h2 className="font-bold text-[var(--ink)] flex items-center gap-2">
            <MapIcon size={16} /> Heatmap · top jugadores × top features
          </h2>
          <span className="text-[10px] uppercase tracking-wider text-[var(--ink-muted)]">intensidad log</span>
        </div>
        {data.heatmap.players.length === 0 || data.heatmap.features.length === 0 ? (
          <Empty />
        ) : (
          <Heatmap
            players={data.heatmap.players}
            features={data.heatmap.features}
            matrix={data.heatmap.matrix}
          />
        )}
      </section>
    </div>
  );
}

function KpiUsage({
  icon, label, value, sub, accent,
}: {
  icon: React.ReactNode; label: string; value: string; sub?: string; accent: string;
}) {
  return (
    <div
      className="glass-strong rounded-2xl p-4 flex items-center gap-3"
      style={{ borderColor: `color-mix(in srgb, ${accent} 30%, transparent)` }}
    >
      <div
        className="w-10 h-10 rounded-xl flex items-center justify-center shrink-0"
        style={{ background: `color-mix(in srgb, ${accent} 18%, transparent)`, color: accent }}
      >
        {icon}
      </div>
      <div className="min-w-0">
        <div className="text-[10px] uppercase tracking-wider text-[var(--ink-muted)] font-semibold">{label}</div>
        <div className="text-xl font-bold text-[var(--ink)] tabular-nums leading-tight">{value}</div>
        {sub ? <div className="text-[11px] text-[var(--ink-muted)] tabular-nums">{sub}</div> : null}
      </div>
    </div>
  );
}

function Empty() {
  return (
    <div className="py-6 text-center text-[var(--ink-muted)] text-sm">
      Sin datos todavía.
    </div>
  );
}
