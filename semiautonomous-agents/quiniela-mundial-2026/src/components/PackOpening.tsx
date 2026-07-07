"use client";

// Sobre + carta. Cuando el cromo de currentPlayer sube de tier, este overlay
// aparece full-screen: cae el sobre, el usuario lo "rasga" tocándolo, sale la
// carta nueva con confetti y un botón de compartir.

import { useEffect, useMemo, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { X, Share2, Sparkles } from "lucide-react";
import { CromoCard } from "@/components/CromoCard";
import { tierMeta, type Cromo } from "@/lib/cromos";
import type { Player } from "@/data/players";

type Props = {
  open: boolean;
  onClose: () => void;
  cromo: Cromo;
  player: Pick<Player, "id" | "name" | "emoji" | "accent" | "photoDataUrl" | "defaultPhoto">;
};

export function PackOpening({ open, onClose, cromo, player }: Props) {
  // Stages: "envelope" → user tap → "reveal" (carta) → "celebrate"
  const [stage, setStage] = useState<"envelope" | "reveal">("envelope");
  const meta = tierMeta(cromo.tier);

  useEffect(() => {
    if (open) setStage("envelope");
  }, [open]);

  // Auto-reveal después de 1.6s si nadie toca (mobile UX).
  useEffect(() => {
    if (!open || stage !== "envelope") return;
    const t = setTimeout(() => setStage("reveal"), 1800);
    return () => clearTimeout(t);
  }, [open, stage]);

  const handleShare = async () => {
    const text = `¡Subí a ${meta.label} en la Quiniela Charales! ${cromo.rating} ovr — soy ${player.name}.`;
    const url = typeof window !== "undefined" ? window.location.origin : "";
    if (typeof navigator !== "undefined" && navigator.share) {
      try { await navigator.share({ title: "Quiniela Charales", text, url }); return; } catch {}
    }
    const waUrl = `https://wa.me/?text=${encodeURIComponent(`${text} ${url}`)}`;
    if (typeof window !== "undefined") window.open(waUrl, "_blank");
  };

  return (
    <AnimatePresence>
      {open && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.3 }}
          className="fixed inset-0 z-[1000] grid place-items-center px-4"
          style={{
            background: "radial-gradient(ellipse at center, rgba(10,10,15,0.96) 0%, rgba(0,0,0,1) 80%)",
            backdropFilter: "blur(8px)",
          }}
        >
          {/* Close button */}
          <button
            type="button"
            onClick={onClose}
            aria-label="Cerrar"
            className="absolute top-4 right-4 w-10 h-10 rounded-full grid place-items-center bg-white/10 text-white hover:bg-white/20 transition-colors z-10"
          >
            <X size={18} />
          </button>

          {/* Tier headline */}
          <div className="absolute top-8 left-1/2 -translate-x-1/2 text-center pointer-events-none">
            <div className="text-[10px] uppercase tracking-[0.4em] text-white/50">Subiste de nivel</div>
            <div
              className="font-display font-black text-2xl md:text-3xl tracking-widest mt-1"
              style={{ color: meta.accent, textShadow: `0 0 24px ${meta.accent}99` }}
            >
              {meta.label}
            </div>
          </div>

          <AnimatePresence mode="wait">
            {stage === "envelope" ? (
              <motion.button
                key="envelope"
                type="button"
                onClick={() => setStage("reveal")}
                aria-label="Abrir sobre"
                initial={{ y: -200, scale: 0.8, rotate: -8, opacity: 0 }}
                animate={{ y: 0, scale: 1, rotate: 0, opacity: 1 }}
                exit={{ scale: 1.1, opacity: 0, transition: { duration: 0.2 } }}
                transition={{ type: "spring", stiffness: 110, damping: 14, mass: 0.9 }}
                className="relative w-[240px] h-[340px] md:w-[280px] md:h-[400px] rounded-[28px] cursor-pointer"
                style={{
                  background: meta.gradient,
                  boxShadow: `0 30px 80px -10px ${meta.accent}88, 0 0 0 1px ${meta.accent}66`,
                }}
              >
                {/* Sobre flap */}
                <div
                  aria-hidden
                  className="absolute inset-x-0 top-0 h-1/2 rounded-t-[28px]"
                  style={{
                    background: `linear-gradient(180deg, ${meta.accent}33, transparent)`,
                    clipPath: "polygon(0 0, 100% 0, 50% 90%)",
                  }}
                />
                <div
                  className="absolute inset-0 grid place-items-center"
                  style={{ color: meta.textColor }}
                >
                  <Sparkles size={56} className="animate-pulse" />
                </div>
                <div
                  className="absolute bottom-5 left-0 right-0 text-center font-display font-bold tracking-[0.3em] text-xs"
                  style={{ color: meta.textColor, opacity: 0.7 }}
                >
                  TAP PARA ABRIR
                </div>
              </motion.button>
            ) : (
              <motion.div
                key="card"
                initial={{ scale: 0.4, rotateY: 180, opacity: 0 }}
                animate={{ scale: 1, rotateY: 0, opacity: 1 }}
                transition={{ type: "spring", stiffness: 90, damping: 14, delay: 0.1 }}
                className="relative"
                style={{ perspective: 1200 }}
              >
                <CromoCard cromo={cromo} player={player} size="md" />
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 1.0 }}
                  className="mt-6 flex justify-center"
                >
                  <button
                    type="button"
                    onClick={handleShare}
                    className="flex items-center gap-2 px-5 h-11 rounded-full bg-white text-black font-bold text-sm shadow-2xl active:scale-95 transition-transform"
                  >
                    <Share2 size={14} /> Compartir mi cromo
                  </button>
                </motion.div>
                {/* Confetti */}
                <Confetti accent={meta.accent} />
              </motion.div>
            )}
          </AnimatePresence>
        </motion.div>
      )}
    </AnimatePresence>
  );
}

function Confetti({ accent }: { accent: string }) {
  const pieces = useMemo(() => {
    const colors = [accent, "#FFFFFF", "#FFE07A", "#14F195", "#5E5BFF"];
    return Array.from({ length: 28 }, (_, i) => ({
      id: i,
      left: Math.random() * 100,
      delay: Math.random() * 0.6,
      duration: 1.8 + Math.random() * 1.6,
      cx: `${(Math.random() * 60 - 30).toFixed(0)}px`,
      cr: `${Math.round(360 + Math.random() * 720)}deg`,
      color: colors[i % colors.length],
      size: 6 + Math.round(Math.random() * 8),
    }));
  }, [accent]);

  return (
    <div aria-hidden className="pointer-events-none absolute inset-0 overflow-visible">
      {pieces.map(p => (
        <span
          key={p.id}
          className="cromo-confetti-piece absolute top-0 rounded-sm"
          style={{
            left: `${p.left}%`,
            width: p.size,
            height: p.size * 0.4,
            background: p.color,
            animationDelay: `${p.delay}s`,
            ["--cd" as string]: `${p.duration}s`,
            ["--cx" as string]: p.cx,
            ["--cr" as string]: p.cr,
          } as React.CSSProperties}
        />
      ))}
    </div>
  );
}
