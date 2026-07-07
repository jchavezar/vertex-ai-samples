"use client";

// /sobre — daily envelope reveal page. Renders the unopened envelope with a
// tear-open CTA, then animates into a full-screen reveal of whatever reward
// the open endpoint returns. Zero pts impact — this is a collectibles loop.

import { useEffect, useState } from "react";
import Link from "next/link";
import { motion, AnimatePresence } from "framer-motion";
import { Mail, Sparkles, BookImage, ArrowLeft, Loader2, Trophy, Crown, ExternalLink } from "lucide-react";
import { useLocale } from "@/lib/i18n";
import { usePlayer } from "@/lib/player-context";
import { findVisualUnlock, type VisualUnlock } from "@/lib/visual-unlocks";
import { TEAMS } from "@/data/teams";
import type { EnvelopeReward } from "@/lib/envelope";

type FetchState =
  | { kind: "loading" }
  | { kind: "anonymous" }
  | { kind: "sealed"; countdownUntilMs: number }
  | { kind: "opened"; reward: EnvelopeReward; openedAt: number };

export default function SobrePage() {
  const { t } = useLocale();
  const { currentPlayer } = usePlayer();
  const [state, setState] = useState<FetchState>({ kind: "loading" });
  const [tearing, setTearing] = useState(false);
  const [openError, setOpenError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    if (!currentPlayer) {
      setState({ kind: "anonymous" });
      return () => { cancelled = true; };
    }
    fetch("/api/envelope/today", { cache: "no-store" })
      .then(r => r.ok ? r.json() : null)
      .then(j => {
        if (cancelled || !j?.ok) return;
        if (j.opened) {
          setState({ kind: "opened", reward: j.reward, openedAt: j.openedAt ?? Date.now() });
        } else {
          setState({ kind: "sealed", countdownUntilMs: j.countdownUntilMs ?? 0 });
        }
      })
      .catch(() => { setState({ kind: "sealed", countdownUntilMs: 0 }); });
    return () => { cancelled = true; };
  }, [currentPlayer]);

  const tearOpen = async () => {
    if (state.kind !== "sealed" || tearing) return;
    setTearing(true);
    setOpenError(null);
    try {
      const r = await fetch("/api/envelope/open", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({}),
      });
      const j = await r.json();
      if (!j?.ok) throw new Error(j?.error ?? `HTTP ${r.status}`);
      // Small theatrical delay so the tear animation has time to play.
      setTimeout(() => {
        setState({ kind: "opened", reward: j.reward, openedAt: j.openedAt ?? Date.now() });
        setTearing(false);
      }, 900);
    } catch (e) {
      setOpenError(e instanceof Error ? e.message : "error");
      setTearing(false);
    }
  };

  return (
    <main className="min-h-screen bg-canvas pb-24">
      <div className="container-app pt-6">
        <div className="flex items-center justify-between mb-6">
          <Link href="/" className="inline-flex items-center gap-1.5 text-sm font-medium text-[var(--ink-soft)] hover:text-[var(--ink)]">
            <ArrowLeft size={14} /> {t("nav.back")}
          </Link>
          <Link href="/unlocks" className="inline-flex items-center gap-1.5 text-xs font-bold uppercase tracking-wider text-[var(--ink-soft)] hover:text-[var(--ink)]">
            <BookImage size={13} /> {t("envelope.collection")}
          </Link>
        </div>

        <header className="text-center mb-10">
          <div className="text-[10px] uppercase tracking-[0.3em] text-[var(--ink-muted)] font-bold">{t("envelope.title")}</div>
          <h1 className="font-display text-4xl sm:text-5xl font-black mt-1">{t("envelope.nav")}</h1>
        </header>

        <div className="max-w-xl mx-auto">
          {state.kind === "loading" && (
            <div className="py-16 text-center text-sm text-[var(--ink-muted)]">
              <Loader2 size={20} className="inline animate-spin" />
            </div>
          )}

          {state.kind === "anonymous" && (
            <div className="rounded-3xl border border-dashed border-[var(--line-strong)] py-12 px-6 text-center">
              <Mail size={28} className="mx-auto text-[var(--ink-muted)]" />
              <p className="mt-3 text-sm text-[var(--ink-soft)]">
                {t("envelope.anonymousCopy", "Identifícate primero para abrir tu sobre del día.")}
              </p>
              <Link href="/jugadores" className="btn btn-primary mt-5 inline-flex">
                {t("nav.session.choose")}
              </Link>
            </div>
          )}

          {state.kind === "sealed" && (
            <SealedEnvelope
              tearing={tearing}
              error={openError}
              onTear={tearOpen}
              countdownMs={state.countdownUntilMs}
            />
          )}

          {state.kind === "opened" && (
            <OpenedReward reward={state.reward} openedAt={state.openedAt} />
          )}
        </div>
      </div>
    </main>
  );
}

function SealedEnvelope({
  tearing, error, onTear, countdownMs,
}: { tearing: boolean; error: string | null; onTear: () => void; countdownMs: number }) {
  const { t } = useLocale();
  return (
    <div className="text-center">
      <motion.button
        type="button"
        onClick={onTear}
        disabled={tearing}
        whileTap={{ scale: 0.98 }}
        className="relative mx-auto block w-full max-w-sm aspect-[5/3] rounded-[28px] shadow-2xl overflow-hidden cursor-pointer disabled:cursor-not-allowed"
        style={{
          background: "linear-gradient(135deg, #4C1D95 0%, #7C3AED 50%, #C026D3 100%)",
        }}
      >
        {/* Envelope flap */}
        <motion.div
          className="absolute inset-x-0 top-0 origin-top"
          initial={false}
          animate={tearing ? { rotateX: 180, opacity: 0 } : { rotateX: 0, opacity: 1 }}
          transition={{ duration: 0.7, ease: "easeInOut" }}
          style={{
            height: "55%",
            background: "linear-gradient(180deg, rgba(255,255,255,0.18), rgba(0,0,0,0.25))",
            clipPath: "polygon(0 0, 100% 0, 50% 100%)",
          }}
        />
        {/* Wax seal */}
        <AnimatePresence>
          {!tearing && (
            <motion.div
              key="seal"
              initial={{ scale: 1 }}
              exit={{ scale: 0, rotate: -45 }}
              transition={{ duration: 0.3 }}
              className="absolute left-1/2 top-[44%] -translate-x-1/2 -translate-y-1/2 w-16 h-16 rounded-full grid place-items-center shadow-lg"
              style={{ background: "radial-gradient(circle at 30% 30%, #FBBF24, #B45309)" }}
            >
              <Mail size={26} className="text-[#3b2a05]" />
            </motion.div>
          )}
        </AnimatePresence>
        {/* Bottom label */}
        <div className="absolute inset-x-0 bottom-3 text-center text-white font-bold uppercase tracking-[0.25em] text-[10px] drop-shadow">
          {tearing ? t("envelope.tearing") : t("envelope.openBtn")}
        </div>
      </motion.button>

      {error && (
        <p className="mt-4 text-xs text-red-600 font-semibold">{error}</p>
      )}

      <p className="mt-6 text-xs text-[var(--ink-muted)]">
        {t("envelope.countdown")} ·{" "}
        <span className="tabular-nums font-bold">
          {formatHM(countdownMs)}
        </span>
      </p>
    </div>
  );
}

function formatHM(ms: number): string {
  if (ms <= 0) return "0h 0m";
  const totalMin = Math.floor(ms / 60_000);
  const h = Math.floor(totalMin / 60);
  const m = totalMin % 60;
  return `${h}h ${m}m`;
}

function OpenedReward({ reward, openedAt }: { reward: EnvelopeReward; openedAt: number }) {
  const { t } = useLocale();
  return (
    <motion.div
      initial={{ opacity: 0, y: 20, scale: 0.96 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ duration: 0.5, ease: "easeOut" }}
      className="rounded-3xl overflow-hidden shadow-2xl"
    >
      <div className="bg-white p-6">
        <div className="text-[10px] uppercase tracking-[0.25em] text-[var(--ink-muted)] font-bold">{t("envelope.youGot")}</div>
        <div className="mt-3"><RewardBody reward={reward} /></div>
        <div className="mt-6 text-[10px] text-[var(--ink-muted)]">
          {new Date(openedAt).toLocaleString()}
        </div>
      </div>
    </motion.div>
  );
}

function RewardBody({ reward }: { reward: EnvelopeReward }) {
  const { t } = useLocale();
  if (reward.type === "visual") {
    const meta = findVisualUnlock(reward.unlockId);
    if (!meta) return <p className="text-sm">Unlock visual desbloqueado.</p>;
    return <VisualReveal meta={meta} />;
  }
  if (reward.type === "insight") {
    return (
      <div>
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-wider text-white" style={{ background: "linear-gradient(135deg, #0F172A, #1E40AF)" }}>
          <Sparkles size={11} /> Insight de AVA
        </div>
        <p className="mt-4 font-display text-xl leading-snug">&ldquo;{reward.text}&rdquo;</p>
        <p className="mt-3 text-[11px] text-[var(--ink-muted)]">
          Basado en {reward.basedOn.decided} partidos decididos · {reward.basedOn.signHits + reward.basedOn.exactHits} aciertos
        </p>
      </div>
    );
  }
  if (reward.type === "spoiler") {
    const home = TEAMS.find(t => t.code === reward.home)?.name ?? reward.home;
    const away = TEAMS.find(t => t.code === reward.away)?.name ?? reward.away;
    return (
      <div>
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-wider text-white" style={{ background: "linear-gradient(135deg, #7C3AED, #A855F7)" }}>
          <Crown size={11} /> Spoiler del torneo
        </div>
        <p className="mt-4 font-display text-lg leading-snug">{home} vs {away}</p>
        <p className="mt-2 text-[11px] text-[var(--ink-muted)]">
          {new Date(reward.kickoffMs).toLocaleString()}
        </p>
        <div className="mt-4 grid grid-cols-3 gap-2 text-center">
          <ProbCell label="Local" value={reward.probabilities.home} />
          <ProbCell label="Empate" value={reward.probabilities.draw} />
          <ProbCell label="Visita" value={reward.probabilities.away} />
        </div>
        <p className="mt-5 text-sm italic text-[var(--ink-soft)]">&ldquo;{reward.hotTake}&rdquo;</p>
      </div>
    );
  }
  if (reward.type === "preview") {
    return (
      <div>
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-wider text-white" style={{ background: "linear-gradient(135deg, #C026D3, #EC4899)" }}>
          <BookImage size={11} /> Cromo preview
        </div>
        <p className="mt-4 font-display text-xl leading-snug">{reward.styleLabel}</p>
        <p className="mt-2 text-[11px] text-[var(--ink-muted)]">Tema del álbum del {reward.date}</p>
        <Link href="/album" className="mt-5 inline-flex items-center gap-1.5 text-xs font-bold text-[var(--ink)] underline">
          {t("nav.album")} <ExternalLink size={11} />
        </Link>
      </div>
    );
  }
  // reto
  const home = TEAMS.find(t => t.code === reward.home)?.name ?? reward.home;
  const away = TEAMS.find(t => t.code === reward.away)?.name ?? reward.away;
  const aiLabel = reward.aiPick === "H" ? home : reward.aiPick === "A" ? away : "Empate";
  return (
    <div>
      <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-wider text-white" style={{ background: "linear-gradient(135deg, #DC2626, #0F172A)" }}>
        <Trophy size={11} /> Reto vs AVA
      </div>
      <p className="mt-4 font-display text-lg leading-snug">{home} vs {away}</p>
      <p className="mt-2 text-[11px] text-[var(--ink-muted)]">
        {new Date(reward.kickoffMs).toLocaleString()}
      </p>
      <p className="mt-4 text-sm">
        AVA picó <span className="font-bold">{aiLabel}</span>. Si tu pick es distinto y aciertas, ganas el badge
        <span className="font-bold"> 🔱 Vencí a la IA</span>.
      </p>
      <Link href="/quiniela" className="mt-5 inline-flex items-center gap-1.5 text-xs font-bold text-[var(--ink)] underline">
        Tu quiniela <ExternalLink size={11} />
      </Link>
    </div>
  );
}

function ProbCell({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-2xl bg-[var(--bg-tint)] px-2 py-3">
      <div className="text-[10px] uppercase tracking-wider text-[var(--ink-muted)] font-bold">{label}</div>
      <div className="font-display text-2xl font-black tabular-nums">{value}%</div>
    </div>
  );
}

function VisualReveal({ meta }: { meta: VisualUnlock }) {
  if (meta.category === "frame") {
    return (
      <div>
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-wider text-white" style={{ background: "linear-gradient(135deg, #D4AF37, #B8860B)" }}>
          <Sparkles size={11} /> Marco · {meta.rarity}
        </div>
        <div className="mt-5 mx-auto w-56 aspect-square rounded-3xl p-1.5 shadow-lg" style={{ background: meta.border }}>
          <div className="w-full h-full rounded-[22px] bg-white grid place-items-center">
            <span className="font-display font-black text-3xl">26</span>
          </div>
        </div>
        <p className="mt-5 font-display text-lg font-bold text-center">{meta.name}</p>
      </div>
    );
  }
  if (meta.category === "background") {
    return (
      <div>
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-wider text-white" style={{ background: "linear-gradient(135deg, #14B8A6, #0F766E)" }}>
          <Sparkles size={11} /> Fondo · {meta.rarity}
        </div>
        <div className="mt-5 mx-auto w-56 aspect-square rounded-3xl shadow-lg overflow-hidden" style={{ background: meta.gradient }}>
          <div className="w-full h-full grid place-items-center">
            <span className="font-display font-black text-white text-3xl drop-shadow">26</span>
          </div>
        </div>
        <p className="mt-5 font-display text-lg font-bold text-center">{meta.name}</p>
      </div>
    );
  }
  // sticker
  return (
    <div>
      <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-wider text-white" style={{ background: "linear-gradient(135deg, #EC4899, #A855F7)" }}>
        <Sparkles size={11} /> Sticker · {meta.rarity}
      </div>
      <div className="mt-5 mx-auto w-56 aspect-square rounded-3xl shadow-lg grid place-items-center" style={{ background: "linear-gradient(135deg, #f8fafc, #e2e8f0)" }}>
        <span className="text-7xl">{meta.emoji}</span>
      </div>
      <p className="mt-5 font-display text-lg font-bold text-center">{meta.name}</p>
    </div>
  );
}
