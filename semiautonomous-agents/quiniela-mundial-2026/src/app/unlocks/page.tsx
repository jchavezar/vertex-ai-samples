"use client";

// /unlocks — read-only gallery of every reward the player has unlocked via
// the daily envelope. Tab filter by category. Newest first.

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { ArrowLeft, BookImage, Sparkles, Crown, Trophy, Mail } from "lucide-react";
import { useLocale } from "@/lib/i18n";
import { usePlayer } from "@/lib/player-context";
import { findVisualUnlock } from "@/lib/visual-unlocks";
import { TEAMS } from "@/data/teams";
import type { UnlockEntry, EnvelopeReward, BadgePayload } from "@/lib/envelope";

type TabKey = "all" | "visual" | "insight" | "spoiler" | "preview" | "badge";

export default function UnlocksPage() {
  const { t } = useLocale();
  const { currentPlayer } = usePlayer();
  const [entries, setEntries] = useState<UnlockEntry[] | null>(null);
  const [tab, setTab] = useState<TabKey>("all");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!currentPlayer) { setEntries([]); return; }
    let cancelled = false;
    fetch("/api/envelope/unlocks", { cache: "no-store" })
      .then(r => r.ok ? r.json() : Promise.reject(new Error(`HTTP ${r.status}`)))
      .then(j => {
        if (cancelled) return;
        if (!j?.ok) throw new Error(j?.error ?? "error");
        setEntries(j.entries as UnlockEntry[]);
      })
      .catch(e => { if (!cancelled) setError(e instanceof Error ? e.message : "error"); });
    return () => { cancelled = true; };
  }, [currentPlayer]);

  const filtered = useMemo(() => {
    const list = entries ?? [];
    if (tab === "all") return list;
    return list.filter(e => e.type === tab);
  }, [entries, tab]);

  const counts = useMemo(() => {
    const c: Record<TabKey, number> = { all: 0, visual: 0, insight: 0, spoiler: 0, preview: 0, badge: 0 };
    for (const e of entries ?? []) {
      c.all += 1;
      if (e.type === "visual" || e.type === "insight" || e.type === "spoiler" || e.type === "preview" || e.type === "badge") {
        c[e.type] += 1;
      }
    }
    return c;
  }, [entries]);

  return (
    <main className="min-h-screen bg-canvas pb-24">
      <div className="container-app pt-6">
        <div className="flex items-center justify-between mb-6">
          <Link href="/" className="inline-flex items-center gap-1.5 text-sm font-medium text-[var(--ink-soft)] hover:text-[var(--ink)]">
            <ArrowLeft size={14} /> {t("nav.back")}
          </Link>
          <Link href="/sobre" className="inline-flex items-center gap-1.5 text-xs font-bold uppercase tracking-wider text-[var(--ink-soft)] hover:text-[var(--ink)]">
            <Mail size={13} /> {t("envelope.nav")}
          </Link>
        </div>

        <header className="text-center mb-6">
          <div className="text-[10px] uppercase tracking-[0.3em] text-[var(--ink-muted)] font-bold">{t("envelope.collection")}</div>
          <h1 className="font-display text-4xl sm:text-5xl font-black mt-1">{t("unlocks.title")}</h1>
        </header>

        <Tabs tab={tab} setTab={setTab} counts={counts} />

        {error && (
          <div className="mt-6 rounded-2xl bg-red-50 border border-red-200 px-4 py-3 text-sm text-red-800">{error}</div>
        )}

        {!entries && !error && (
          <div className="mt-12 text-center text-sm text-[var(--ink-muted)]">{t("envelope.title")}…</div>
        )}

        {entries && filtered.length === 0 && (
          <div className="mt-10 rounded-3xl border-2 border-dashed border-[var(--line-strong)] py-12 text-center">
            <BookImage size={28} className="mx-auto text-[var(--ink-muted)]" />
            <p className="mt-3 text-sm text-[var(--ink-soft)]">
              {t("unlocks.empty", "Aún no has abierto sobres. Vuelve mañana.")}
            </p>
            <Link href="/sobre" className="btn btn-primary mt-5 inline-flex">
              <Mail size={14} /> {t("envelope.nav")}
            </Link>
          </div>
        )}

        <div className="mt-6 grid grid-cols-1 sm:grid-cols-2 gap-3">
          {filtered.map(entry => (
            <UnlockCard key={`${entry.type}_${entry.id}_${entry.awardedAt}`} entry={entry} />
          ))}
        </div>
      </div>
    </main>
  );
}

function Tabs({ tab, setTab, counts }: { tab: TabKey; setTab: (k: TabKey) => void; counts: Record<TabKey, number> }) {
  const { t } = useLocale();
  const opts: Array<{ key: TabKey; label: string }> = [
    { key: "all",     label: `Todo (${counts.all})` },
    { key: "visual",  label: `${t("unlocks.tabVisuals")} (${counts.visual})` },
    { key: "insight", label: `${t("unlocks.tabInsights")} (${counts.insight})` },
    { key: "spoiler", label: `${t("unlocks.tabSpoilers")} (${counts.spoiler})` },
    { key: "preview", label: `${t("unlocks.tabPreviews")} (${counts.preview})` },
    { key: "badge",   label: `${t("unlocks.tabBadges")} (${counts.badge})` },
  ];
  return (
    <div className="flex flex-wrap gap-1.5 justify-center">
      {opts.map(o => {
        const active = tab === o.key;
        return (
          <button
            key={o.key}
            type="button"
            onClick={() => setTab(o.key)}
            className={`px-3 py-1.5 rounded-full text-xs font-bold uppercase tracking-wider transition-colors ${
              active ? "bg-[var(--ink)] text-white" : "bg-white hairline text-[var(--ink-soft)] hover:text-[var(--ink)]"
            }`}
          >
            {o.label}
          </button>
        );
      })}
    </div>
  );
}

function UnlockCard({ entry }: { entry: UnlockEntry }) {
  if (entry.type === "visual") return <VisualCard entry={entry} />;
  if (entry.type === "insight") return <InsightCard entry={entry} />;
  if (entry.type === "spoiler") return <SpoilerCard entry={entry} />;
  if (entry.type === "preview") return <PreviewCard entry={entry} />;
  if (entry.type === "reto")    return <RetoCard entry={entry} />;
  if (entry.type === "badge")   return <BadgeCard entry={entry} />;
  return null;
}

function CardChrome({
  title, kicker, accent, children,
}: { title: string; kicker: string; accent: string; children?: React.ReactNode }) {
  return (
    <article className="rounded-2xl bg-white hairline shadow-sm overflow-hidden">
      <div className="px-4 py-2 text-[10px] uppercase tracking-[0.2em] font-black text-white" style={{ background: accent }}>
        {kicker}
      </div>
      <div className="p-4">
        <div className="font-display font-black text-lg leading-snug">{title}</div>
        {children && <div className="mt-3 text-sm text-[var(--ink-soft)]">{children}</div>}
      </div>
    </article>
  );
}

function VisualCard({ entry }: { entry: UnlockEntry }) {
  const payload = entry.payload as EnvelopeReward;
  if (payload.type !== "visual") return null;
  const meta = findVisualUnlock(payload.unlockId);
  if (!meta) return null;
  const accent = meta.accent ?? "#7C3AED";
  const preview =
    meta.category === "frame"
      ? <div className="w-20 h-20 rounded-2xl p-1.5" style={{ background: meta.border }}><div className="w-full h-full rounded-xl bg-white" /></div>
      : meta.category === "background"
      ? <div className="w-20 h-20 rounded-2xl" style={{ background: meta.gradient }} />
      : <div className="w-20 h-20 rounded-2xl grid place-items-center text-3xl" style={{ background: "#f1f5f9" }}>{meta.emoji}</div>;
  return (
    <article className="rounded-2xl bg-white hairline shadow-sm overflow-hidden">
      <div className="px-4 py-2 text-[10px] uppercase tracking-[0.2em] font-black text-white" style={{ background: accent }}>
        Visual · {meta.rarity}
      </div>
      <div className="p-4 flex items-center gap-4">
        {preview}
        <div className="min-w-0">
          <div className="font-display font-black text-lg leading-snug truncate">{meta.name}</div>
          <div className="text-[10px] text-[var(--ink-muted)] uppercase tracking-wider mt-1">{meta.category}</div>
        </div>
      </div>
    </article>
  );
}

function InsightCard({ entry }: { entry: UnlockEntry }) {
  const payload = entry.payload as EnvelopeReward;
  if (payload.type !== "insight") return null;
  return (
    <CardChrome title="Insight de AVA" kicker="Insight" accent="#0F172A">
      <p className="italic">&ldquo;{payload.text}&rdquo;</p>
      <p className="mt-2 text-[10px] text-[var(--ink-muted)]">
        {new Date(entry.awardedAt).toLocaleDateString()} · {payload.basedOn.decided} partidos
      </p>
    </CardChrome>
  );
}

function SpoilerCard({ entry }: { entry: UnlockEntry }) {
  const payload = entry.payload as EnvelopeReward;
  if (payload.type !== "spoiler") return null;
  const home = TEAMS.find(t => t.code === payload.home)?.name ?? payload.home;
  const away = TEAMS.find(t => t.code === payload.away)?.name ?? payload.away;
  return (
    <CardChrome title={`${home} vs ${away}`} kicker="Spoiler" accent="#7C3AED">
      <div className="flex items-center gap-2 text-xs">
        <span className="px-1.5 py-0.5 rounded-full bg-[var(--bg-tint)]">L {payload.probabilities.home}%</span>
        <span className="px-1.5 py-0.5 rounded-full bg-[var(--bg-tint)]">E {payload.probabilities.draw}%</span>
        <span className="px-1.5 py-0.5 rounded-full bg-[var(--bg-tint)]">V {payload.probabilities.away}%</span>
      </div>
      <p className="mt-2 italic">&ldquo;{payload.hotTake}&rdquo;</p>
    </CardChrome>
  );
}

function PreviewCard({ entry }: { entry: UnlockEntry }) {
  const payload = entry.payload as EnvelopeReward;
  if (payload.type !== "preview") return null;
  return (
    <CardChrome title={payload.styleLabel} kicker="Cromo Preview" accent="#C026D3">
      <p>Tema del álbum del {payload.date}.</p>
      <Link href="/album" className="mt-2 inline-flex items-center gap-1 text-xs font-bold underline">
        Abrir álbum
      </Link>
    </CardChrome>
  );
}

function RetoCard({ entry }: { entry: UnlockEntry }) {
  const payload = entry.payload as EnvelopeReward;
  if (payload.type !== "reto") return null;
  const home = TEAMS.find(t => t.code === payload.home)?.name ?? payload.home;
  const away = TEAMS.find(t => t.code === payload.away)?.name ?? payload.away;
  const status = payload.status;
  const accent = status === "won" ? "#16A34A" : status === "lost" ? "#7F1D1D" : "#DC2626";
  return (
    <CardChrome title={`${home} vs ${away}`} kicker={`Reto · ${status}`} accent={accent}>
      <p>AVA picó <strong>{payload.aiPick}</strong>. Resultado: {status === "pending" ? "pendiente" : status}.</p>
    </CardChrome>
  );
}

function BadgeCard({ entry }: { entry: UnlockEntry }) {
  const payload = entry.payload as BadgePayload;
  return (
    <CardChrome title={payload.label} kicker="Badge" accent="#0F172A">
      {payload.description && <p>{payload.description}</p>}
    </CardChrome>
  );
}
