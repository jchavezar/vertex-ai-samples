"use client";

import { useEffect, useMemo, useState } from "react";
import { useLocale } from "@/lib/i18n";
import { etDate } from "@/lib/daily-streak";
import { useHomeSnapshot } from "@/lib/home-snapshot";

type MvpEntry = {
  date: string;        // YYYY-MM-DD (ET)
  playerId: string;
  name: string;
  points: number;
  pickedExact?: number;
  computedAt: number;
};

const STALE_MS = 24 * 60 * 60 * 1000;

function pickFreshEntry(entries: MvpEntry[]): { entry: MvpEntry; label: "today" | "yesterday" } | null {
  if (!Array.isArray(entries) || entries.length === 0) return null;
  const today = etDate();
  const yesterday = etDate(new Date(Date.now() - 86_400_000));
  const now = Date.now();
  const todayDoc = entries.find(e => e.date === today && now - (e.computedAt ?? 0) < STALE_MS);
  const yDoc = entries.find(e => e.date === yesterday && now - (e.computedAt ?? 0) < STALE_MS);
  const pick = todayDoc ?? yDoc ?? null;
  if (!pick) return null;
  return { entry: pick, label: pick.date === today ? "today" : "yesterday" };
}

export function CharalDelDiaChip() {
  const { t } = useLocale();
  const snapshot = useHomeSnapshot();
  const snapshotEntries = snapshot?.data?.dailyMvp?.entries ?? null;
  const [fallback, setFallback] = useState<MvpEntry[] | null>(null);

  // Fallback fetch only when no snapshot provider is mounted (e.g. this
  // component renders on a different page in the future).
  useEffect(() => {
    if (snapshot) return;
    let cancelled = false;
    fetch("/api/daily-mvp")
      .then(r => r.ok ? r.json() : null)
      .then((j: { ok?: boolean; entries?: MvpEntry[] } | null) => {
        if (cancelled) return;
        if (j?.ok && Array.isArray(j.entries)) setFallback(j.entries);
      })
      .catch(() => {});
    return () => { cancelled = true; };
  }, [snapshot]);

  const picked = useMemo(() => {
    const source = snapshotEntries ?? fallback;
    if (!source) return null;
    return pickFreshEntry(source);
  }, [snapshotEntries, fallback]);

  const entry = picked?.entry ?? null;
  const label = picked?.label ?? null;

  if (!entry || !label) return null;

  const labelText = label === "today" ? t("mvp.today") : t("mvp.yesterday");

  return (
    <span
      className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider ring-1 ring-[#b8860b]/40 shadow-sm"
      style={{
        background: "linear-gradient(135deg, #FFE07A 0%, #D4AF37 60%, #B8860B 100%)",
        color: "#3b2a05",
      }}
      title={`${t("mvp.label")} · ${labelText}: ${entry.name} +${entry.points}`}
    >
      <span aria-hidden>👑</span>
      <span className="hidden sm:inline">{t("mvp.label")}</span>
      <span className="opacity-70">·</span>
      <span>{labelText}</span>
      <span className="opacity-70">·</span>
      <span className="normal-case tracking-normal">{entry.name}</span>
      <span className="tabular-nums">+{entry.points}</span>
    </span>
  );
}
