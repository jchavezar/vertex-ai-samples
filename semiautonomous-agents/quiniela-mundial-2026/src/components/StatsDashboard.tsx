"use client";

// Owner-only analytics dashboard. Renders the payload from /api/admin/stats.
// All charts are inline SVG so we don't pull a charting library. Refresh +
// auto-polling every 60s. Sortable per-player table.

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import Link from "next/link";
import {
  ArrowLeft, RefreshCcw, Loader2, TrendingUp, Camera, Sparkles, MessageSquare,
  Bell, Activity, Image as ImageIcon, Trophy, Users, Download, Share2, X,
} from "lucide-react";
import { PLAYERS } from "@/data/players";
import { TEAMS_BY_CODE } from "@/data/teams";
import { UsageTab } from "./UsageTab";

// PWA beforeinstallprompt event. Not in lib.dom for non-Chromium runtimes.
type BeforeInstallPromptEvent = Event & {
  prompt: () => Promise<void>;
  userChoice: Promise<{ outcome: "accepted" | "dismissed" }>;
};

type PerPlayer = {
  id: string; name: string; isBot: boolean;
  picks: { groupTotal: number; groupWithScore: number; bracketRounds: number; champion: string | null; runnerUp: string | null; updatedAt: number | null };
  photo: { activeSource: "uploaded" | "generated" | "original" | null; activeUrl: string | null; activeUpdatedAt: number | null; historyTotal: number; historyUploaded: number; historyGenerated: number; lastHistoryAt: number | null };
  cromo: { total: number; lastDate: string | null };
  push: { devices: number; lastDeviceAt: number | null };
  chat: { messages: number; lastMessageAt: number | null };
  activity: { total7d: number; pickEvents7d: number };
};

type DailyBucket = { date: string; total: number; byType: Record<string, number>; byPlayer: Record<string, number> };
type CromoBucket = { date: string; total: number; byPlayer: Record<string, number> };
type PhotoBucket = { date: string; uploaded: number; generated: number; byPlayer: Record<string, number> };
type ChatBucket = { date: string; total: number; byPlayer: Record<string, number> };
type ConsensusRow = { fixtureId: string; home: string; away: string; date: string; h: number; d: number; a: number; scoreCount: number; voters: string[] };

type StatsPayload = {
  generatedAt: number;
  totals: {
    players: number; humanPlayers: number; picksTotal: number;
    photosGeneratedTotal: number; photosUploadedTotal: number; cromosTotal: number;
    chatMessagesTotal: number; pushDevicesTotal: number; activityTotal7d: number;
  };
  players: PerPlayer[];
  activityByDay: DailyBucket[];
  cromosByDay: CromoBucket[];
  chatByDay: ChatBucket[];
  photosByDay: PhotoBucket[];
  fixturesConsensus: ConsensusRow[];
};

type SortKey = "name" | "picks" | "bracket" | "photos" | "cromos" | "chat" | "push" | "activity" | "updated";

const ACTIVITY_COLORS: Record<string, string> = {
  pick_made: "var(--accent-violet)",
  leader_change: "var(--accent-gold)",
  streak: "var(--accent-mint)",
  exact_score: "var(--accent-coral)",
  unknown: "var(--ink-muted)",
};

function teamName(code: string): string {
  return TEAMS_BY_CODE[code]?.name ?? code;
}

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

function KpiCard({
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

function StackedBars({
  buckets, types, height = 120,
}: {
  buckets: { date: string; byType: Record<string, number> }[];
  types: string[];
  height?: number;
}) {
  const max = Math.max(1, ...buckets.map(b => Object.values(b.byType).reduce((a, c) => a + c, 0)));
  const barW = 100 / Math.max(1, buckets.length);
  return (
    <svg viewBox={`0 0 100 ${height}`} preserveAspectRatio="none" className="w-full" style={{ height }}>
      {buckets.map((b, i) => {
        let y = height;
        const x = i * barW + barW * 0.15;
        const w = barW * 0.7;
        return (
          <g key={b.date}>
            {types.map(t => {
              const v = b.byType[t] ?? 0;
              if (v === 0) return null;
              const h = (v / max) * (height - 14);
              y -= h;
              return <rect key={t} x={x} y={y} width={w} height={h} fill={ACTIVITY_COLORS[t] ?? "var(--ink-muted)"} opacity={0.92} />;
            })}
            <text x={x + w / 2} y={height - 1} fontSize="3.2" textAnchor="middle" fill="var(--ink-muted)">
              {shortDay(b.date)}
            </text>
          </g>
        );
      })}
    </svg>
  );
}

function SimpleBars({
  buckets, valueOf, color = "var(--accent-violet)", height = 110, format,
}: {
  buckets: { date: string }[];
  valueOf: (b: { date: string }) => number;
  color?: string;
  height?: number;
  format?: (v: number) => string;
}) {
  const values = buckets.map(valueOf);
  const max = Math.max(1, ...values);
  const barW = 100 / Math.max(1, buckets.length);
  return (
    <svg viewBox={`0 0 100 ${height}`} preserveAspectRatio="none" className="w-full" style={{ height }}>
      {buckets.map((b, i) => {
        const v = values[i];
        const h = (v / max) * (height - 14);
        const x = i * barW + barW * 0.18;
        const w = barW * 0.64;
        const y = height - 6 - h;
        return (
          <g key={b.date}>
            <rect x={x} y={y} width={w} height={h} fill={color} opacity={v === 0 ? 0.18 : 0.92} rx="0.6" />
            {v > 0 ? (
              <text x={x + w / 2} y={y - 1} fontSize="2.8" textAnchor="middle" fill="var(--ink)">
                {format ? format(v) : v}
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

function StackedPhotos({ buckets, height = 110 }: { buckets: PhotoBucket[]; height?: number }) {
  const max = Math.max(1, ...buckets.map(b => b.uploaded + b.generated));
  const barW = 100 / Math.max(1, buckets.length);
  return (
    <svg viewBox={`0 0 100 ${height}`} preserveAspectRatio="none" className="w-full" style={{ height }}>
      {buckets.map((b, i) => {
        const total = b.uploaded + b.generated;
        const totalH = (total / max) * (height - 14);
        const x = i * barW + barW * 0.18;
        const w = barW * 0.64;
        const upH = total > 0 ? (b.uploaded / total) * totalH : 0;
        const genH = totalH - upH;
        const yGen = height - 6 - totalH;
        const yUp = yGen + genH;
        return (
          <g key={b.date}>
            {genH > 0 ? <rect x={x} y={yGen} width={w} height={genH} fill="var(--accent-violet)" opacity="0.9" rx="0.6" /> : null}
            {upH > 0 ? <rect x={x} y={yUp} width={w} height={upH} fill="var(--accent-mint)" opacity="0.9" rx="0.6" /> : null}
            {total > 0 ? (
              <text x={x + w / 2} y={yGen - 1} fontSize="2.8" textAnchor="middle" fill="var(--ink)">{total}</text>
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

function ConsensusBar({ h, d, a }: { h: number; d: number; a: number }) {
  const total = Math.max(1, h + d + a);
  const hPct = (h / total) * 100;
  const dPct = (d / total) * 100;
  const aPct = (a / total) * 100;
  return (
    <div className="flex w-full h-4 rounded-md overflow-hidden text-[10px] font-semibold">
      {hPct > 0 ? (
        <div style={{ width: `${hPct}%`, background: "var(--accent-mint)", color: "#06281a" }} className="flex items-center justify-center">
          {h > 0 ? h : ""}
        </div>
      ) : null}
      {dPct > 0 ? (
        <div style={{ width: `${dPct}%`, background: "var(--accent-gold)", color: "#3a2a02" }} className="flex items-center justify-center">
          {d > 0 ? d : ""}
        </div>
      ) : null}
      {aPct > 0 ? (
        <div style={{ width: `${aPct}%`, background: "var(--accent-coral)", color: "#3a0a14" }} className="flex items-center justify-center">
          {a > 0 ? a : ""}
        </div>
      ) : null}
    </div>
  );
}

export function StatsDashboard() {
  const [data, setData] = useState<StatsPayload | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sortKey, setSortKey] = useState<SortKey>("activity");
  const [sortDir, setSortDir] = useState<"asc" | "desc">("desc");
  const [tab, setTab] = useState<"picks" | "uso">("picks");
  const [installEvt, setInstallEvt] = useState<BeforeInstallPromptEvent | null>(null);
  const [installed, setInstalled] = useState(false);
  const [showIosHint, setShowIosHint] = useState(false);
  const isIosRef = useRef(false);

  useEffect(() => {
    if (typeof window === "undefined") return;
    const ua = window.navigator.userAgent || "";
    const standalone =
      window.matchMedia?.("(display-mode: standalone)").matches ||
      (window.navigator as Navigator & { standalone?: boolean }).standalone === true;
    isIosRef.current = /iPad|iPhone|iPod/.test(ua) && !("MSStream" in window);
    setInstalled(!!standalone);
    const onBip = (e: Event) => { e.preventDefault(); setInstallEvt(e as BeforeInstallPromptEvent); };
    const onInstalled = () => { setInstalled(true); setInstallEvt(null); };
    window.addEventListener("beforeinstallprompt", onBip);
    window.addEventListener("appinstalled", onInstalled);
    return () => {
      window.removeEventListener("beforeinstallprompt", onBip);
      window.removeEventListener("appinstalled", onInstalled);
    };
  }, []);

  async function onInstallClick() {
    if (installEvt) {
      try {
        await installEvt.prompt();
        const choice = await installEvt.userChoice;
        if (choice.outcome === "accepted") setInstalled(true);
      } finally {
        setInstallEvt(null);
      }
      return;
    }
    if (isIosRef.current) setShowIosHint(true);
  }

  const load = useCallback(async (silent = false) => {
    if (silent) setRefreshing(true); else setLoading(true);
    setError(null);
    try {
      const r = await fetch("/api/admin/stats", { cache: "no-store" });
      if (!r.ok) {
        setError(r.status === 403 ? "forbidden" : `error_${r.status}`);
        return;
      }
      const j = (await r.json()) as StatsPayload;
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

  const players = useMemo(() => {
    if (!data) return [];
    const arr = [...data.players];
    const dir = sortDir === "asc" ? 1 : -1;
    arr.sort((a, b) => {
      switch (sortKey) {
        case "name": return a.name.localeCompare(b.name) * dir;
        case "picks": return (a.picks.groupTotal - b.picks.groupTotal) * dir;
        case "bracket": return (a.picks.bracketRounds - b.picks.bracketRounds) * dir;
        case "photos": return (a.photo.historyTotal - b.photo.historyTotal) * dir;
        case "cromos": return (a.cromo.total - b.cromo.total) * dir;
        case "chat": return (a.chat.messages - b.chat.messages) * dir;
        case "push": return (a.push.devices - b.push.devices) * dir;
        case "activity": return (a.activity.total7d - b.activity.total7d) * dir;
        case "updated": return ((a.picks.updatedAt ?? 0) - (b.picks.updatedAt ?? 0)) * dir;
        default: return 0;
      }
    });
    return arr;
  }, [data, sortKey, sortDir]);

  function sortBy(k: SortKey) {
    if (sortKey === k) setSortDir(d => d === "asc" ? "desc" : "asc");
    else { setSortKey(k); setSortDir("desc"); }
  }

  function sortArrow(k: SortKey): string {
    if (sortKey !== k) return "";
    return sortDir === "asc" ? "↑" : "↓";
  }

  if (loading && !data) {
    return (
      <main className="container-app py-10 flex items-center justify-center text-[var(--ink-muted)] text-sm gap-2">
        <Loader2 size={16} className="animate-spin" /> Cargando stats…
      </main>
    );
  }

  if (error === "forbidden") {
    return (
      <main className="container-app py-16 text-center text-[var(--ink-muted)]">
        Esta página es solo para Jesús.
      </main>
    );
  }

  if (!data) {
    return (
      <main className="container-app py-10 text-center text-[var(--ink-muted)] text-sm">
        No hay datos {error ? <>· <span className="text-red-400">{error}</span></> : null}
      </main>
    );
  }

  const { totals, activityByDay, cromosByDay, photosByDay, chatByDay, fixturesConsensus } = data;
  const activityTypes = ["pick_made", "leader_change", "streak", "exact_score", "unknown"];

  return (
    <main className="container-app pt-4 pb-20 space-y-5">
      <header className="flex items-center justify-between gap-3 pt-2 flex-wrap">
        <Link href="/" className="chip gap-1.5 text-[var(--ink-muted)]">
          <ArrowLeft size={12} /> Volver
        </Link>
        <div className="flex items-center gap-2 flex-wrap">
          <span className="text-[10px] uppercase tracking-wider text-[var(--ink-muted)] tabular-nums">
            generado {relative(data.generatedAt)}
          </span>
          {!installed && (installEvt || isIosRef.current) ? (
            <button
              type="button"
              onClick={onInstallClick}
              className="chip gap-1.5"
              style={{ color: "var(--accent-mint)" }}
            >
              <Download size={11} /> Instalar como app
            </button>
          ) : null}
          <button
            type="button"
            onClick={() => load(true)}
            disabled={refreshing}
            className="chip gap-1.5"
            style={{ color: "var(--accent-violet)" }}
          >
            {refreshing ? <Loader2 size={11} className="animate-spin" /> : <RefreshCcw size={11} />}
            Refrescar
          </button>
        </div>
      </header>

      {showIosHint ? (
        <div
          className="glass-strong rounded-2xl p-3 flex items-start gap-3 text-xs"
          style={{ borderColor: "color-mix(in srgb, var(--accent-mint) 35%, transparent)" }}
        >
          <Share2 size={14} className="mt-0.5 shrink-0" style={{ color: "var(--accent-mint)" }} />
          <div className="flex-1">
            <div className="font-semibold text-[var(--ink)]">Añade Quiniela a tu pantalla de inicio</div>
            <div className="text-[var(--ink-muted)] mt-0.5">
              En Safari toca <strong>Compartir</strong> y luego <strong>Añadir a pantalla de inicio</strong>.
            </div>
          </div>
          <button
            type="button"
            onClick={() => setShowIosHint(false)}
            className="w-7 h-7 rounded-full flex items-center justify-center text-[var(--ink-muted)] shrink-0"
            aria-label="Cerrar"
          >
            <X size={14} />
          </button>
        </div>
      ) : null}

      <div className="flex items-center gap-2">
        <button
          type="button"
          onClick={() => setTab("picks")}
          className="chip gap-1.5"
          style={{
            color: tab === "picks" ? "#0a0a0c" : "var(--ink-muted)",
            background: tab === "picks" ? "var(--accent-violet)" : undefined,
            borderColor: tab === "picks" ? "var(--accent-violet)" : undefined,
          }}
        >
          <Trophy size={12} /> Picks & Cromos
        </button>
        <button
          type="button"
          onClick={() => setTab("uso")}
          className="chip gap-1.5"
          style={{
            color: tab === "uso" ? "#0a0a0c" : "var(--ink-muted)",
            background: tab === "uso" ? "var(--accent-violet)" : undefined,
            borderColor: tab === "uso" ? "var(--accent-violet)" : undefined,
          }}
        >
          <Activity size={12} /> Uso
        </button>
      </div>

      {tab === "uso" ? <UsageTab /> : null}

      {tab === "picks" ? (
      <>
      <section className="glass-strong rounded-3xl p-5 md:p-6 relative overflow-hidden">
        <div
          className="absolute -top-16 -right-16 w-72 h-72 rounded-full blur-3xl opacity-25 pointer-events-none"
          style={{ background: "radial-gradient(closest-side, var(--accent-violet), transparent)" }}
        />
        <div className="relative">
          <div className="text-[10px] uppercase tracking-wider text-[var(--ink-muted)] font-semibold">Privado · solo Jesús</div>
          <h1 className="text-2xl md:text-3xl font-black text-[var(--ink)]">Stats de los charales</h1>
          <p className="text-sm text-[var(--ink-muted)] mt-1">Granular. Auto-refresca cada 60s.</p>
        </div>
      </section>

      <section className="grid grid-cols-2 md:grid-cols-3 gap-3">
        <KpiCard icon={<Users size={18} />} accent="var(--accent-violet)"
          label="Charales activos" value={`${totals.humanPlayers}`} sub={`+ 1 bot · ${totals.players} total`} />
        <KpiCard icon={<TrendingUp size={18} />} accent="var(--accent-mint)"
          label="Picks (group)" value={`${totals.picksTotal}`} sub="suma de todos" />
        <KpiCard icon={<Sparkles size={18} />} accent="var(--accent-gold)"
          label="Fotos AI" value={`${totals.photosGeneratedTotal}`} sub={`${totals.photosUploadedTotal} subidas`} />
        <KpiCard icon={<ImageIcon size={18} />} accent="var(--accent-coral)"
          label="Cromos generados" value={`${totals.cromosTotal}`} sub="histórico total" />
        <KpiCard icon={<MessageSquare size={18} />} accent="#0EA5E9"
          label="Mensajes a Ava" value={`${totals.chatMessagesTotal}`} sub="histórico total" />
        <KpiCard icon={<Bell size={18} />} accent="#14B8A6"
          label="Push devices" value={`${totals.pushDevicesTotal}`} sub={`${totals.activityTotal7d} eventos / 7d`} />
      </section>

      <section className="glass-strong rounded-3xl p-5">
        <div className="flex items-center justify-between gap-2 mb-3">
          <h2 className="font-bold text-[var(--ink)] flex items-center gap-2">
            <Activity size={16} /> Actividad últimos 7 días
          </h2>
          <div className="flex items-center gap-3 text-[10px] uppercase tracking-wider text-[var(--ink-muted)]">
            {activityTypes.slice(0, 4).map(t => (
              <span key={t} className="flex items-center gap-1">
                <span className="w-2 h-2 rounded-full" style={{ background: ACTIVITY_COLORS[t] }} />
                {t.replace("_", " ")}
              </span>
            ))}
          </div>
        </div>
        <StackedBars buckets={activityByDay} types={activityTypes} height={130} />
      </section>

      <section className="grid grid-cols-1 md:grid-cols-3 gap-3">
        <div className="glass-strong rounded-3xl p-5">
          <h2 className="font-bold text-[var(--ink)] flex items-center gap-2 mb-2">
            <ImageIcon size={16} /> Cromos · 14d
          </h2>
          <SimpleBars buckets={cromosByDay} valueOf={(b) => (b as CromoBucket).total} color="var(--accent-coral)" />
        </div>
        <div className="glass-strong rounded-3xl p-5">
          <h2 className="font-bold text-[var(--ink)] flex items-center gap-2 mb-2">
            <Camera size={16} /> Fotos · 14d
          </h2>
          <StackedPhotos buckets={photosByDay} />
          <div className="flex gap-3 text-[10px] uppercase tracking-wider text-[var(--ink-muted)] mt-2">
            <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full" style={{ background: "var(--accent-violet)" }} /> AI</span>
            <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full" style={{ background: "var(--accent-mint)" }} /> Subida</span>
          </div>
        </div>
        <div className="glass-strong rounded-3xl p-5">
          <h2 className="font-bold text-[var(--ink)] flex items-center gap-2 mb-2">
            <MessageSquare size={16} /> Chat con Ava · 14d
          </h2>
          <SimpleBars buckets={chatByDay} valueOf={(b) => (b as ChatBucket).total} color="#0EA5E9" />
        </div>
      </section>

      <section className="glass-strong rounded-3xl p-4 md:p-5 overflow-x-auto">
        <div className="flex items-center justify-between gap-2 mb-3">
          <h2 className="font-bold text-[var(--ink)] flex items-center gap-2">
            <Trophy size={16} /> Charales · tabla granular
          </h2>
          <span className="text-[10px] uppercase tracking-wider text-[var(--ink-muted)]">click columna p/ordenar</span>
        </div>
        <table className="w-full min-w-[820px] text-sm">
          <thead>
            <tr className="text-[10px] uppercase tracking-wider text-[var(--ink-muted)] border-b border-white/10">
              <th onClick={() => sortBy("name")} className="text-left py-2 pr-2 cursor-pointer select-none">Charal {sortArrow("name")}</th>
              <th onClick={() => sortBy("picks")} className="text-right py-2 px-2 cursor-pointer select-none">Picks {sortArrow("picks")}</th>
              <th onClick={() => sortBy("bracket")} className="text-right py-2 px-2 cursor-pointer select-none">Bracket {sortArrow("bracket")}</th>
              <th className="text-left py-2 px-2">Campeón / sub</th>
              <th onClick={() => sortBy("photos")} className="text-right py-2 px-2 cursor-pointer select-none">Fotos {sortArrow("photos")}</th>
              <th className="text-left py-2 px-2">Foto activa</th>
              <th onClick={() => sortBy("cromos")} className="text-right py-2 px-2 cursor-pointer select-none">Cromos {sortArrow("cromos")}</th>
              <th onClick={() => sortBy("chat")} className="text-right py-2 px-2 cursor-pointer select-none">Chat {sortArrow("chat")}</th>
              <th onClick={() => sortBy("push")} className="text-right py-2 px-2 cursor-pointer select-none">Push {sortArrow("push")}</th>
              <th onClick={() => sortBy("activity")} className="text-right py-2 px-2 cursor-pointer select-none">Acts 7d {sortArrow("activity")}</th>
              <th onClick={() => sortBy("updated")} className="text-right py-2 pl-2 cursor-pointer select-none">Últ. pick {sortArrow("updated")}</th>
            </tr>
          </thead>
          <tbody>
            {players.map(p => (
              <tr key={p.id} className="border-b border-white/5 hover:bg-white/5 transition">
                <td className="py-2 pr-2">
                  <div className="flex items-center gap-2 font-semibold text-[var(--ink)]">
                    <span>{PLAYERS.find(pl => pl.id === p.id)?.emoji}</span>
                    <span>{p.name}</span>
                    {p.isBot ? <span className="chip text-[9px]" style={{ color: "var(--accent-violet)" }}>BOT</span> : null}
                  </div>
                </td>
                <td className="py-2 px-2 text-right tabular-nums">
                  <div className="font-semibold text-[var(--ink)]">{p.picks.groupTotal}</div>
                  <div className="text-[10px] text-[var(--ink-muted)]">{p.picks.groupWithScore} c/score</div>
                </td>
                <td className="py-2 px-2 text-right tabular-nums">{p.picks.bracketRounds}<span className="text-[var(--ink-muted)]">/6</span></td>
                <td className="py-2 px-2 text-[var(--ink-muted)] text-xs">
                  {p.picks.champion ? teamName(p.picks.champion) : "—"}
                  {p.picks.runnerUp ? <span className="text-[var(--ink-muted)]"> / {teamName(p.picks.runnerUp)}</span> : null}
                </td>
                <td className="py-2 px-2 text-right tabular-nums">
                  <div className="font-semibold">{p.photo.historyTotal}</div>
                  <div className="text-[10px] text-[var(--ink-muted)]">{p.photo.historyGenerated}AI · {p.photo.historyUploaded}up</div>
                </td>
                <td className="py-2 px-2">
                  {p.photo.activeSource ? (
                    <span
                      className="chip text-[10px]"
                      style={{
                        color: p.photo.activeSource === "generated" ? "var(--accent-violet)"
                          : p.photo.activeSource === "uploaded" ? "var(--accent-mint)" : "var(--ink-muted)",
                      }}
                    >
                      {p.photo.activeSource}
                    </span>
                  ) : <span className="text-[var(--ink-muted)] text-xs">—</span>}
                </td>
                <td className="py-2 px-2 text-right tabular-nums">
                  <div className="font-semibold">{p.cromo.total}</div>
                  <div className="text-[10px] text-[var(--ink-muted)]">{p.cromo.lastDate ?? "—"}</div>
                </td>
                <td className="py-2 px-2 text-right tabular-nums">
                  <div className="font-semibold">{p.chat.messages}</div>
                  <div className="text-[10px] text-[var(--ink-muted)]">{relative(p.chat.lastMessageAt)}</div>
                </td>
                <td className="py-2 px-2 text-right tabular-nums">
                  <div className="font-semibold">{p.push.devices}</div>
                  <div className="text-[10px] text-[var(--ink-muted)]">{relative(p.push.lastDeviceAt)}</div>
                </td>
                <td className="py-2 px-2 text-right tabular-nums">
                  <div className="font-semibold">{p.activity.total7d}</div>
                  <div className="text-[10px] text-[var(--ink-muted)]">{p.activity.pickEvents7d} picks</div>
                </td>
                <td className="py-2 pl-2 text-right text-[var(--ink-muted)] tabular-nums text-xs">
                  {relative(p.picks.updatedAt)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      {fixturesConsensus.length > 0 ? (
        <section className="glass-strong rounded-3xl p-4 md:p-5">
          <div className="flex items-center justify-between gap-2 mb-3">
            <h2 className="font-bold text-[var(--ink)] flex items-center gap-2">
              <TrendingUp size={16} /> Consenso · próximos partidos
            </h2>
            <div className="flex items-center gap-3 text-[10px] uppercase tracking-wider text-[var(--ink-muted)]">
              <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full" style={{ background: "var(--accent-mint)" }} /> Local</span>
              <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full" style={{ background: "var(--accent-gold)" }} /> Empate</span>
              <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full" style={{ background: "var(--accent-coral)" }} /> Visita</span>
            </div>
          </div>
          <div className="space-y-2">
            {fixturesConsensus.map(fx => {
              const total = fx.h + fx.d + fx.a;
              return (
                <div key={fx.fixtureId} className="grid grid-cols-[1fr,3fr,auto] items-center gap-3 text-xs">
                  <div className="text-[var(--ink)] font-semibold truncate">
                    <span>{teamName(fx.home)}</span>
                    <span className="text-[var(--ink-muted)] mx-1">vs</span>
                    <span>{teamName(fx.away)}</span>
                    <div className="text-[10px] text-[var(--ink-muted)] tabular-nums">{fx.date}</div>
                  </div>
                  <ConsensusBar h={fx.h} d={fx.d} a={fx.a} />
                  <div className="text-[10px] uppercase tracking-wider text-[var(--ink-muted)] tabular-nums whitespace-nowrap">
                    {total}/10 · {fx.scoreCount} scores
                  </div>
                </div>
              );
            })}
          </div>
        </section>
      ) : null}
      </>
      ) : null}

      <footer className="text-[10px] uppercase tracking-wider text-[var(--ink-muted)] text-center">
        Eyes only · /admin/stats
      </footer>
    </main>
  );
}
