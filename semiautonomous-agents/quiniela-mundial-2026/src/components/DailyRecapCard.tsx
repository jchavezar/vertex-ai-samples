"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { Sparkles, ChevronDown, ChevronUp, Send, Loader2 } from "lucide-react";
import { PLAYERS, AI_PLAYER_ID } from "@/data/players";
import { PlayerAvatar } from "@/components/PlayerAvatar";
import { usePlayer } from "@/lib/player-context";
import { track } from "@/lib/track";
import { useLocale } from "@/lib/i18n";

type AvaMessage = { role: "user" | "ava"; text: string; ts: number };

type RecapEntry = {
  generatedAt: number;
  narration: string;
  fixtureIds: string[];
  scores: Record<string, string>;
  kind: "opening" | "update";
};

type RecapDoc = {
  date: string;
  narration: string;
  generatedAt: number;
  entries?: RecapEntry[];
  modelUsed?: string;
};

type Response = {
  ok: boolean;
  recap: RecapDoc | null;
  label?: "hoy" | "ayer";
};

const AI_PLAYER = PLAYERS.find(p => p.id === AI_PLAYER_ID)!;

function relativeFromNow(ms: number, t: (k: string, f?: string) => string): string {
  const diff = Date.now() - ms;
  if (diff < 60_000) return t("recap.relative.justNow");
  const minutes = Math.floor(diff / 60_000);
  if (minutes < 60) return t("recap.relative.minutes").replace("{n}", String(minutes));
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return t("recap.relative.hours").replace("{n}", String(hours));
  const days = Math.floor(hours / 24);
  if (days === 1) return t("recap.relative.yesterday");
  return t("recap.relative.days").replace("{n}", String(days));
}

export function DailyRecapCard() {
  const [data, setData] = useState<Response | null>(null);
  const [expanded, setExpanded] = useState(false);
  const { currentPlayer } = usePlayer();
  const { t } = useLocale();
  const [thread, setThread] = useState<AvaMessage[]>([]);
  const [draft, setDraft] = useState("");
  const [sending, setSending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const threadRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    let cancelled = false;
    fetch("/api/daily-recap", { cache: "no-store" })
      .then(r => (r.ok ? r.json() : null))
      .then(j => { if (!cancelled && j) setData(j as Response); })
      .catch(() => {});
    return () => { cancelled = true; };
  }, []);

  // Thread is EPHEMERAL — lives only in component state. Cleared whenever the
  // recap entries change (a new Ava comment ⇒ fresh conversation) or when the
  // player logs in/out. Refreshing the page also resets because state is
  // never persisted to localStorage or server.
  const latestRecapTs = data?.recap?.entries?.[data.recap.entries.length - 1]?.generatedAt
    ?? data?.recap?.generatedAt
    ?? 0;
  useEffect(() => {
    setThread([]);
    setDraft("");
  }, [currentPlayer?.id, latestRecapTs]);

  useEffect(() => {
    if (threadRef.current) threadRef.current.scrollTop = threadRef.current.scrollHeight;
  }, [thread.length]);

  const sendToAva = useCallback(async () => {
    const text = draft.trim();
    if (!text || sending) return;
    setSending(true);
    setError(null);
    try {
      // Honor the user's tone choice from the ChatBot toggle (same localStorage
       // key). Defaults to "suave" if nothing's stored yet.
      let tone: "picante" | "suave" | "ava" = "suave";
      if (typeof window !== "undefined") {
        const saved = window.localStorage.getItem("q26:chat-tone");
        if (saved === "picante" || saved === "suave" || saved === "ava") tone = saved;
        else if (saved === "agi") tone = "ava"; // legacy migration
      }
      const r = await fetch("/api/daily-recap/reply", {
        method: "POST",
        headers: { "content-type": "application/json" },
        // Send current ephemeral thread so Ava has context within this session
        // — the server doesn't store anything, the client owns the history.
        body: JSON.stringify({ text, history: thread, tone }),
      });
      const j = await r.json();
      if (!r.ok || !j.ok) throw new Error(j.error || `HTTP ${r.status}`);
      setThread(prev => [...prev, j.user, j.ava]);
      setDraft("");
      track("ava_reply", { length: text.length });
    } catch (e) {
      setError(e instanceof Error ? e.message : "error");
    } finally {
      setSending(false);
    }
  }, [draft, sending, thread]);

  const entries = useMemo<RecapEntry[]>(() => {
    const e = data?.recap?.entries;
    if (Array.isArray(e) && e.length > 0) return e;
    // Fallback for legacy docs.
    if (data?.recap?.narration) {
      return [{
        generatedAt: data.recap.generatedAt ?? 0,
        narration: data.recap.narration,
        fixtureIds: [],
        scores: {},
        kind: "opening",
      }];
    }
    return [];
  }, [data]);

  const seenRef = useRef(false);
  useEffect(() => {
    if (seenRef.current) return;
    if (entries.length === 0) return;
    seenRef.current = true;
    track("recap_viewed", { entries: entries.length });
  }, [entries]);

  if (entries.length === 0 || !data?.recap) return null;
  const { recap, label } = data;
  const latest = entries[entries.length - 1];
  const prior = entries.slice(0, -1);
  const hasPrior = prior.length > 0;

  return (
    <section className="container-app pt-4 pb-2">
      <div
        className="glass-strong rounded-3xl p-5 md:p-6 relative overflow-hidden"
        style={{ borderColor: "color-mix(in srgb, var(--accent-violet) 35%, transparent)" }}
      >
        <div
          className="absolute -top-16 -right-16 w-72 h-72 rounded-full blur-3xl opacity-25 pointer-events-none"
          style={{ background: "radial-gradient(closest-side, var(--accent-violet), transparent)" }}
        />
        <div className="relative flex items-start gap-4">
          <div className="shrink-0">
            <PlayerAvatar player={AI_PLAYER} size={40} rounded="rounded-2xl" tint={0.18} />
          </div>
          <div className="min-w-0 flex-1">
            <div className="flex items-center gap-2 flex-wrap mb-2">
              <span
                className="chip"
                style={{
                  background: "color-mix(in srgb, var(--accent-violet) 14%, transparent)",
                  color: "var(--accent-violet)",
                }}
              >
                <Sparkles size={11} /> {t("recap.chip")} {label === "ayer" ? t("recap.label.yesterday") : t("recap.label.today")}
              </span>
              <span className="text-[10px] uppercase tracking-wider text-[var(--ink-muted)] tabular-nums">
                {recap.date}
              </span>
              {hasPrior && (
                <span
                  className="text-[10px] uppercase tracking-wider tabular-nums px-2 py-0.5 rounded-full"
                  style={{
                    background: "color-mix(in srgb, var(--accent-violet) 10%, transparent)",
                    color: "var(--accent-violet)",
                  }}
                >
                  {entries.length} {t("recap.comments")}
                </span>
              )}
            </div>
            <p className="text-[var(--ink)] text-base md:text-lg leading-relaxed font-medium">
              {latest.narration}
            </p>
            <div className="mt-3 flex items-center gap-3 flex-wrap text-[10px] uppercase tracking-wider text-[var(--ink-muted)]">
              <span>
                {latest.kind === "update" && hasPrior ? t("recap.update") : t("recap.generated")}
                {relativeFromNow(latest.generatedAt, t)}
              </span>
              {hasPrior && (
                <button
                  type="button"
                  onClick={() => {
                    const next = !expanded;
                    setExpanded(next);
                    if (next) track("recap_prior_expanded", { count: prior.length });
                  }}
                  className="inline-flex items-center gap-1 text-[var(--accent-violet)] hover:underline"
                >
                  {expanded ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
                  {expanded ? t("recap.hidePrior") : (prior.length > 1 ? t("recap.viewPrior.many") : t("recap.viewPrior.one")).replace("{n}", String(prior.length))}
                </button>
              )}
            </div>
            {expanded && hasPrior && (
              <div className="mt-4 space-y-3 pl-3 border-l-2" style={{ borderColor: "color-mix(in srgb, var(--accent-violet) 30%, transparent)" }}>
                {[...prior].reverse().map((entry, idx) => (
                  <div key={`${entry.generatedAt}-${idx}`} className="opacity-85">
                    <div className="text-[10px] uppercase tracking-wider text-[var(--ink-muted)] mb-1">
                      {entry.kind === "opening" ? t("recap.prior.opening") : t("recap.prior.update")} · {relativeFromNow(entry.generatedAt, t)}
                    </div>
                    <p className="text-sm md:text-base leading-relaxed text-[var(--ink)]">
                      {entry.narration}
                    </p>
                  </div>
                ))}
              </div>
            )}

            {currentPlayer ? (
              <div className="mt-5 -mx-2 sm:mx-0 rounded-2xl bg-[var(--bg-tint)] p-3 sm:p-4" style={{ border: "1px solid color-mix(in srgb, var(--accent-violet) 18%, transparent)" }}>
                <div className="flex items-center justify-between mb-3 gap-2 flex-wrap">
                  <span className="text-[11px] sm:text-[10px] uppercase tracking-wider text-[var(--ink-muted)] font-semibold">
                    {t("recap.chat.title")}
                  </span>
                  <span className="text-[10px] text-[var(--ink-muted)]">{t("recap.chat.private")}</span>
                </div>
                {thread.length > 0 && (
                  <div
                    ref={threadRef}
                    className="mb-3 max-h-80 overflow-y-auto pr-1 space-y-2.5"
                  >
                    {thread.map((m, i) => (
                      <div
                        key={`${m.ts}-${i}`}
                        className={`flex gap-2 ${m.role === "user" ? "justify-end" : "justify-start"}`}
                      >
                        {m.role === "ava" && (
                          <div className="shrink-0 self-end">
                            <PlayerAvatar player={AI_PLAYER} size={26} rounded="rounded-lg" tint={0.18} />
                          </div>
                        )}
                        <div
                          className={`max-w-[85%] sm:max-w-[80%] rounded-2xl px-3.5 py-2.5 text-[15px] sm:text-sm leading-relaxed break-words ${
                            m.role === "user"
                              ? "bg-[var(--ink)] text-white rounded-br-md"
                              : "bg-white text-[var(--ink)] rounded-bl-md"
                          }`}
                          style={m.role === "ava" ? { border: "1px solid color-mix(in srgb, var(--accent-violet) 22%, transparent)" } : undefined}
                        >
                          {m.text}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
                <div className="flex items-end gap-2">
                  <textarea
                    value={draft}
                    onChange={(e) => setDraft(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === "Enter" && !e.shiftKey) {
                        e.preventDefault();
                        sendToAva();
                      }
                    }}
                    rows={1}
                    placeholder={t("recap.chat.placeholder")}
                    disabled={sending}
                    className="flex-1 min-w-0 resize-none rounded-xl border border-[var(--line)] bg-white px-3.5 py-2.5 text-[16px] sm:text-sm leading-relaxed focus:outline-none focus:ring-2 focus:ring-[var(--accent-violet)] disabled:opacity-60"
                    style={{ minHeight: 44, maxHeight: 160 }}
                  />
                  <button
                    type="button"
                    onClick={sendToAva}
                    disabled={sending || draft.trim().length === 0}
                    aria-label={t("recap.chat.send")}
                    className="shrink-0 inline-flex items-center justify-center w-11 h-11 rounded-xl bg-[var(--accent-violet)] text-white disabled:opacity-40"
                  >
                    {sending ? <Loader2 size={18} className="animate-spin" /> : <Send size={18} />}
                  </button>
                </div>
                {error && (
                  <div className="mt-2 text-[12px] text-red-600">{error}</div>
                )}
              </div>
            ) : (
              <div className="mt-5 text-[11px] text-[var(--ink-muted)] italic">
                {t("recap.chat.signedOut")}
              </div>
            )}
          </div>
        </div>
      </div>
    </section>
  );
}
