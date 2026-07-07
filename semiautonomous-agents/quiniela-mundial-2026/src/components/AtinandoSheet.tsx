"use client";

// Mobile-first bottom sheet that lists the charales whose pick is currently
// winning a fixture. Tapped from the live card's "Van bien" avatar stack.
// Renders via createPortal so it escapes any transformed ancestors.

import { useEffect, useState } from "react";
import { createPortal } from "react-dom";
import { X } from "lucide-react";
import { PlayerAvatar } from "@/components/PlayerAvatar";
import type { PlayerLite } from "@/lib/all-picks";
import { track } from "@/lib/track";

type Props = {
  open: boolean;
  onClose: () => void;
  title: string;        // e.g. "Van bien · 6"
  subtitle?: string;    // e.g. "USA 3-0 PAR · Pickearon Local"
  players: PlayerLite[];
  accent?: string;      // bar/glow color, defaults to magenta-pink (live)
};

export function AtinandoSheet({ open, onClose, title, subtitle, players, accent = "#FF3B82" }: Props) {
  const [mounted, setMounted] = useState(false);
  useEffect(() => {
    setMounted(true);
  }, []);

  useEffect(() => {
    if (!open) return;
    track("atinando_opened");
    const onKey = (e: KeyboardEvent) => { if (e.key === "Escape") onClose(); };
    document.addEventListener("keydown", onKey);
    const prev = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => {
      document.removeEventListener("keydown", onKey);
      document.body.style.overflow = prev;
    };
  }, [open, onClose]);

  if (!mounted || typeof document === "undefined" || !open) return null;

  return createPortal(
    <div
      role="dialog"
      aria-modal="true"
      aria-label={title}
      className="fixed inset-0 z-[1000] flex items-end sm:items-center justify-center bg-black/55 backdrop-blur-sm animate-[fadeIn_.15s_ease-out]"
      onClick={onClose}
    >
      <div
        onClick={(e) => e.stopPropagation()}
        className="relative w-full sm:max-w-md bg-white rounded-t-3xl sm:rounded-3xl shadow-2xl overflow-hidden animate-[atinandoIn_.22s_cubic-bezier(.2,.8,.2,1)] mx-0 sm:mx-4"
        style={{ boxShadow: `0 -10px 40px -10px rgba(0,0,0,0.4), 0 0 0 1px ${accent}33` }}
      >
        {/* Drag handle (mobile) */}
        <div className="pt-2 pb-1 sm:hidden flex justify-center">
          <div className="w-10 h-1.5 rounded-full bg-[var(--line-strong)]" />
        </div>

        {/* Header */}
        <div className="px-5 pt-3 pb-4 flex items-start gap-3" style={{ background: `linear-gradient(180deg, ${accent}14, transparent)` }}>
          <div className="flex-1 min-w-0">
            <div className="font-display text-xl font-bold text-[var(--ink)] leading-tight">{title}</div>
            {subtitle && (
              <div className="text-xs text-[var(--ink-soft)] mt-1 uppercase tracking-[0.12em]">{subtitle}</div>
            )}
          </div>
          <button
            type="button"
            onClick={onClose}
            aria-label="Cerrar"
            className="shrink-0 w-9 h-9 rounded-full bg-[var(--bg-tint)] hover:bg-[var(--line)] grid place-items-center text-[var(--ink-soft)] transition-colors"
          >
            <X size={16} />
          </button>
        </div>

        {/* Player list */}
        <div className="max-h-[55vh] sm:max-h-[60vh] overflow-y-auto px-3 pb-4">
          {players.length === 0 ? (
            <div className="text-center py-8 text-[var(--ink-muted)] text-sm">Aún nadie.</div>
          ) : (
            <ul className="divide-y divide-[var(--line)]">
              {players.map((p, idx) => (
                <li key={p.id} className="flex items-center gap-3 py-2.5 px-2">
                  <div className="w-6 text-center text-[11px] font-bold text-[var(--ink-muted)] tabular-nums">{idx + 1}</div>
                  <PlayerAvatar player={p} size={40} rounded="rounded-full" textClass="text-base" tint={0.22} enableLightbox />
                  <div className="flex-1 min-w-0">
                    <div className="font-display font-bold text-[var(--ink)] truncate">{p.name}</div>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>

        {/* Safe-area bottom inset (iOS) */}
        <div className="h-[max(env(safe-area-inset-bottom),8px)] bg-white" />
      </div>

      <style jsx>{`
        @keyframes atinandoIn {
          from { transform: translateY(24px); opacity: 0; }
          to   { transform: translateY(0);    opacity: 1; }
        }
      `}</style>
    </div>,
    document.body,
  );
}
