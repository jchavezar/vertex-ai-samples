"use client";

import { useEffect, useState } from "react";
import { createPortal } from "react-dom";
import type { Player } from "@/data/players";
import { useProfileAvatar } from "@/lib/profile-avatar";

type Props = {
  player: Pick<Player, "id" | "name" | "emoji" | "accent" | "photoDataUrl" | "defaultPhoto">;
  size?: number;
  rounded?: string;
  textClass?: string;
  className?: string;
  tint?: number;
  // Skip the Mexico-edition profile avatar lookup. Use this when the caller
  // provides its own photo (e.g. CromoCard supplies the manga-shonen portrait
  // via player.photoDataUrl and wants that to win).
  bypassProfileAvatar?: boolean;
  // Open a fullscreen lightbox when the avatar is clicked.
  enableLightbox?: boolean;
};

function withAlpha(hex: string, alpha: number) {
  const a = Math.max(0, Math.min(1, alpha));
  const aa = Math.round(a * 255).toString(16).padStart(2, "0").toUpperCase();
  return `${hex}${aa}`;
}

export function PlayerAvatar({
  player, size = 40, rounded = "rounded-2xl", textClass, className = "", tint = 0.12,
  bypassProfileAvatar = false, enableLightbox = false,
}: Props) {
  const aiUrl = useProfileAvatar(bypassProfileAvatar ? undefined : player.id);
  const src = (bypassProfileAvatar ? null : aiUrl) || player.photoDataUrl || player.defaultPhoto;
  const [open, setOpen] = useState(false);
  const style: React.CSSProperties = {
    width: size,
    height: size,
    background: src ? undefined : withAlpha(player.accent, tint),
    color: player.accent,
  };

  const interactive = enableLightbox && !!src;
  const interactiveProps = interactive
    ? {
        role: "button" as const,
        tabIndex: 0,
        onClick: (e: React.MouseEvent) => { e.stopPropagation(); e.preventDefault(); setOpen(true); },
        onKeyDown: (e: React.KeyboardEvent) => {
          if (e.key === "Enter" || e.key === " ") { e.preventDefault(); setOpen(true); }
        },
        "aria-label": `Ver foto de ${player.name}`,
        title: `Ver foto de ${player.name}`,
      }
    : {};
  const cursorClass = interactive ? "cursor-zoom-in" : "";

  if (src) {
    return (
      <>
        <div
          className={`${rounded} overflow-hidden shrink-0 ring-1 ring-black/5 ${cursorClass} ${className}`}
          style={{ width: size, height: size }}
          {...interactiveProps}
        >
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src={src} alt={player.name} className="w-full h-full object-cover" />
        </div>
        {interactive && open && (
          <AvatarLightbox src={src} alt={player.name} accent={player.accent} onClose={() => setOpen(false)} />
        )}
      </>
    );
  }
  const fontSize = textClass ? undefined : Math.round(size * 0.5);
  return (
    <div className={`${rounded} grid place-items-center shrink-0 ${textClass ?? ""} ${className}`} style={{ ...style, fontSize }}>
      <span aria-hidden="true">{player.emoji}</span>
    </div>
  );
}

function AvatarLightbox({ src, alt, accent, onClose }: { src: string; alt: string; accent: string; onClose: () => void }) {
  const [mounted, setMounted] = useState(false);
  useEffect(() => {
    setMounted(true);
    const onKey = (e: KeyboardEvent) => { if (e.key === "Escape") onClose(); };
    document.addEventListener("keydown", onKey);
    const prev = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => {
      document.removeEventListener("keydown", onKey);
      document.body.style.overflow = prev;
    };
  }, [onClose]);

  if (!mounted || typeof document === "undefined") return null;

  return createPortal(
    <div
      className="fixed inset-0 z-[1000] grid place-items-center bg-black/90 backdrop-blur-sm p-4 animate-[fadeIn_.15s_ease-out]"
      onClick={onClose}
      role="dialog"
      aria-modal="true"
    >
      <button
        type="button"
        onClick={onClose}
        aria-label="Cerrar"
        className="absolute top-4 right-4 w-11 h-11 rounded-full bg-white/15 hover:bg-white/25 text-white grid place-items-center text-xl font-bold transition-colors z-10"
      >
        ×
      </button>
      <div
        className="relative max-w-[92vw] max-h-[88vh] rounded-3xl overflow-hidden shadow-2xl"
        style={{ boxShadow: `0 25px 60px -10px rgba(0,0,0,0.6), 0 0 0 2px ${accent}88` }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img src={src} alt={alt} className="max-w-[92vw] max-h-[88vh] object-contain block" />
      </div>
      <div className="absolute bottom-5 left-1/2 -translate-x-1/2 text-white/70 text-xs uppercase tracking-[0.2em] pointer-events-none">
        Toca fuera o ESC para cerrar
      </div>
    </div>,
    document.body,
  );
}
