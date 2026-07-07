"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { AnimatePresence, motion } from "framer-motion";
import { useState } from "react";
import {
  Home, Calendar, BarChart3, Target, MoreHorizontal,
  Users, Swords, Activity, BookImage, Trophy, Mail, X,
} from "lucide-react";

const PRIMARY_TABS = [
  { href: "/",          icon: Home,           label: "Inicio"   },
  { href: "/partidos",  icon: Calendar,       label: "Partidos" },
  { href: "/standings", icon: BarChart3,      label: "Tabla"    },
  { href: "/quiniela",  icon: Target,         label: "Quiniela" },
  { href: null,         icon: MoreHorizontal, label: "Más"      },
] as const;

const MORE_LINKS = [
  { href: "/grupos",      icon: Users,     label: "Grupos"   },
  { href: "/bracket",     icon: Swords,    label: "Bracket"  },
  { href: "/leaderboard", icon: Trophy,    label: "Ranking"  },
  { href: "/ranking",     icon: Activity,  label: "Equipos"  },
  { href: "/album",       icon: BookImage, label: "Álbum"    },
  { href: "/sobre",       icon: Mail,      label: "Sobre"    },
];

export function BottomNav() {
  const pathname = usePathname();
  const [moreOpen, setMoreOpen] = useState(false);

  return (
    <>
      {/* Backdrop */}
      <AnimatePresence>
        {moreOpen && (
          <motion.div
            key="backdrop"
            initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            className="fixed inset-0 z-40 bg-black/50 md:hidden"
            onClick={() => setMoreOpen(false)}
          />
        )}
      </AnimatePresence>

      {/* More sheet */}
      <AnimatePresence>
        {moreOpen && (
          <motion.div
            key="sheet"
            initial={{ y: "100%" }}
            animate={{ y: 0 }}
            exit={{ y: "100%" }}
            transition={{ type: "spring", damping: 32, stiffness: 320 }}
            className="fixed bottom-0 left-0 right-0 z-50 md:hidden glass rounded-t-3xl px-4 pt-5 pb-[calc(env(safe-area-inset-bottom,0px)+88px)]"
          >
            <div className="flex items-center justify-between mb-4">
              <span className="font-display font-bold text-base">Más secciones</span>
              <button
                onClick={() => setMoreOpen(false)}
                className="w-8 h-8 rounded-full bg-[var(--bg-tint)] grid place-items-center"
              >
                <X size={16} />
              </button>
            </div>
            <div className="grid grid-cols-3 gap-3">
              {MORE_LINKS.map(({ href, icon: Icon, label }) => {
                const active = pathname.startsWith(href);
                return (
                  <Link
                    key={href}
                    href={href}
                    onClick={() => setMoreOpen(false)}
                    className={`flex flex-col items-center gap-2 py-4 rounded-2xl transition-colors ${
                      active
                        ? "bg-[var(--ink)] text-white"
                        : "bg-[var(--bg-tint)] text-[var(--ink-soft)]"
                    }`}
                  >
                    <Icon size={22} />
                    <span className="text-xs font-semibold">{label}</span>
                  </Link>
                );
              })}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Bottom tab bar */}
      <nav
        className="fixed bottom-0 left-0 right-0 z-50 md:hidden"
        style={{ willChange: "transform", transform: "translateZ(0)" }}
      >
        <div
          className="glass mx-3 mb-3 rounded-2xl flex items-stretch gap-0.5 p-1"
          style={{ paddingBottom: "max(4px, env(safe-area-inset-bottom, 0px))" }}
        >
          {PRIMARY_TABS.map(({ href, icon: Icon, label }) => {
            if (!href) {
              return (
                <button
                  key="more"
                  onClick={() => setMoreOpen(o => !o)}
                  className={`flex-1 relative flex flex-col items-center justify-center gap-0.5 py-2 rounded-xl transition-colors ${
                    moreOpen
                      ? "text-[var(--ink)]"
                      : "text-[var(--ink-muted)]"
                  }`}
                >
                  {moreOpen && (
                    <span className="absolute inset-0 rounded-xl bg-[var(--bg-tint)]" />
                  )}
                  <Icon size={20} className="relative" />
                  <span className="text-[10px] font-semibold tracking-wide relative">{label}</span>
                </button>
              );
            }
            const active = href === "/" ? pathname === "/" : pathname.startsWith(href);
            return (
              <Link
                key={href}
                href={href}
                className={`flex-1 relative flex flex-col items-center justify-center gap-0.5 py-2 rounded-xl transition-colors ${
                  active ? "text-[var(--ink)]" : "text-[var(--ink-muted)]"
                }`}
              >
                {active && (
                  <motion.span
                    layoutId="tab-bg"
                    className="absolute inset-0 rounded-xl bg-[var(--bg-tint)]"
                    transition={{ type: "spring", stiffness: 400, damping: 35 }}
                  />
                )}
                <Icon size={20} className="relative z-10" />
                <span className="text-[10px] font-semibold tracking-wide relative z-10">{label}</span>
              </Link>
            );
          })}
        </div>
      </nav>
    </>
  );
}
