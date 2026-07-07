"use client";

// Announcement banner shown on the home page when the R32 knockout bracket opens.
// Dismissible per-player (localStorage key includes playerId). Auto-hides after
// 2026-07-06 (after R32 ends). Clicking "Ver bracket" also marks it dismissed.

import Link from "next/link";
import { useEffect, useState } from "react";
import { X, Trophy } from "lucide-react";
import { usePlayer } from "@/lib/player-context";

const DISMISS_KEY = (playerId: string) => `q26:ko-open-banner-dismissed:${playerId}`;
const HIDE_AFTER = new Date("2026-07-07T00:00:00Z").getTime();

export function KOOpenBanner() {
  const { currentPlayer, ready } = usePlayer();
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    if (!ready) return;
    if (Date.now() >= HIDE_AFTER) return;
    if (!currentPlayer) return;
    try {
      if (localStorage.getItem(DISMISS_KEY(currentPlayer.id))) return;
    } catch {}
    setVisible(true);
  }, [ready, currentPlayer]);

  const dismiss = () => {
    if (currentPlayer) {
      try { localStorage.setItem(DISMISS_KEY(currentPlayer.id), "1"); } catch {}
    }
    setVisible(false);
  };

  if (!visible) return null;

  return (
    <div
      className="relative overflow-hidden rounded-3xl px-4 py-4"
      style={{
        background: "linear-gradient(135deg, rgba(94,91,255,0.18) 0%, rgba(20,241,149,0.14) 100%)",
        border: "1px solid rgba(94,91,255,0.35)",
        boxShadow: "0 0 0 1px rgba(20,241,149,0.12), 0 8px 32px -8px rgba(94,91,255,0.2)",
      }}
    >
      {/* dismiss */}
      <button
        type="button"
        onClick={dismiss}
        className="absolute top-3 right-3 w-6 h-6 grid place-items-center rounded-full opacity-50 hover:opacity-100 transition-opacity"
        style={{ background: "rgba(0,0,0,0.08)" }}
        aria-label="Cerrar"
      >
        <X size={12} />
      </button>

      <div className="flex items-start gap-3">
        {/* icon */}
        <div
          className="shrink-0 w-11 h-11 rounded-2xl grid place-items-center"
          style={{ background: "linear-gradient(135deg, rgba(94,91,255,0.25), rgba(20,241,149,0.22))" }}
        >
          <Trophy size={20} style={{ color: "rgb(94,91,255)" }} />
        </div>

        <div className="min-w-0 flex-1 pr-6">
          <div
            className="text-[10px] font-display font-black uppercase tracking-[0.22em] mb-0.5"
            style={{ color: "rgb(94,91,255)" }}
          >
            ¡Fase eliminatoria abierta!
          </div>
          <div className="font-display font-bold text-[15px] leading-snug mb-1">
            Ya puedes elegir tus picks de dieciseisavos
          </div>
          <p className="text-[11px] leading-relaxed mb-3" style={{ color: "var(--ink-soft)" }}>
            16 partidos, elige el ganador de cada uno antes de que arranquen.
            Usa el botón <strong>🤖 Auto-pick con IA</strong> si quieres que Gemini te ayude.
          </p>

          <Link
            href="/bracket"
            onClick={dismiss}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-[11px] font-display font-bold transition-all"
            style={{
              background: "linear-gradient(135deg, rgba(94,91,255,0.9), rgba(20,200,120,0.85))",
              color: "white",
              boxShadow: "0 4px 14px rgba(94,91,255,0.3)",
            }}
          >
            <Trophy size={12} />
            Ver bracket →
          </Link>
        </div>
      </div>

      {/* animated shimmer line at the bottom */}
      <div
        className="absolute bottom-0 left-0 right-0 h-[2px] rounded-b-3xl"
        style={{
          background: "linear-gradient(90deg, rgba(94,91,255,0), rgba(20,241,149,0.7), rgba(94,91,255,0))",
          animation: "shimmer 2.5s ease-in-out infinite",
        }}
      />
      <style jsx>{`
        @keyframes shimmer {
          0%, 100% { opacity: 0.4; transform: scaleX(0.6); }
          50%       { opacity: 1;   transform: scaleX(1); }
        }
      `}</style>
    </div>
  );
}
