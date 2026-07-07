"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { usePlayer } from "@/lib/player-context";
import { useLocale, type Locale } from "@/lib/i18n";
import { Trophy, Calendar, BarChart3, Target, Users, Activity, Swords, Home, ChevronLeft, BookImage, Sparkles, Wand2, Mail, MoreHorizontal } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { PlayerAvatar } from "@/components/PlayerAvatar";
import { DailyStreakChip } from "@/components/DailyStreakChip";

const OWNER_ID = "jesus";

// Desktop nav split into "always visible" + "overflow dropdown" so the bar
// never wraps on standard laptop widths. We were rendering 12 inline links +
// chips + 2 avatars which overflowed off-screen on 1440px and narrower.
const PRIMARY_LINKS = [
  { href: "/",            labelKey: "nav.home",      icon: Trophy   },
  { href: "/quiniela",    labelKey: "nav.myPool",    icon: Target   },
  { href: "/partidos",    labelKey: "nav.live",      icon: Calendar },
  { href: "/leaderboard", labelKey: "nav.standings", icon: BarChart3 },
  { href: "/album",       labelKey: "nav.album",     icon: BookImage },
] as const;
const SECONDARY_LINKS = [
  { href: "/grupos",    labelKey: "nav.groups",         icon: Users     },
  { href: "/bracket",   labelKey: "nav.bracket",        icon: Swords    },
  { href: "/ranking",   labelKey: "nav.teams",          icon: Activity  },
  { href: "/standings", labelKey: "nav.worldStandings", icon: BarChart3 },
  { href: "/sobre",     labelKey: "envelope.nav",       icon: Mail      },
] as const;
const ADMIN_LINKS = [
  { href: "/admin/cromos", labelKey: "nav.cards", icon: Wand2 },
  { href: "/admin/stats",  labelKey: "nav.stats", icon: Sparkles },
] as const;

type NavLink = { href: string; labelKey: string; icon: React.ComponentType<{ size?: number; className?: string }> };

function MoreMenu({ links, pathname, t }: { links: readonly NavLink[]; pathname: string; t: (k: string) => string }) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);
  const anyActive = links.some(l => pathname.startsWith(l.href));

  useEffect(() => {
    if (!open) return;
    const onDoc = (e: MouseEvent) => {
      if (!ref.current?.contains(e.target as Node)) setOpen(false);
    };
    const onEsc = (e: KeyboardEvent) => { if (e.key === "Escape") setOpen(false); };
    document.addEventListener("mousedown", onDoc);
    document.addEventListener("keydown", onEsc);
    return () => {
      document.removeEventListener("mousedown", onDoc);
      document.removeEventListener("keydown", onEsc);
    };
  }, [open]);

  return (
    <div ref={ref} className="relative">
      <button
        type="button"
        onClick={() => setOpen(v => !v)}
        aria-haspopup="menu"
        aria-expanded={open}
        className={`relative flex items-center gap-1.5 px-3 py-2 rounded-full text-sm font-medium transition-colors ${anyActive || open ? "text-[var(--ink)] bg-[var(--bg-tint)]" : "text-[var(--ink-soft)] hover:text-[var(--ink)]"}`}
      >
        <MoreHorizontal size={15} />
        <span>{t("nav.more")}</span>
      </button>
      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0, y: -4, scale: 0.96 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -4, scale: 0.96 }}
            transition={{ duration: 0.12, ease: "easeOut" }}
            role="menu"
            className="absolute right-0 top-[calc(100%+6px)] min-w-[200px] rounded-2xl bg-white shadow-xl ring-1 ring-black/10 p-1.5 z-50"
          >
            {links.map(({ href, labelKey, icon: Icon }) => {
              const active = pathname.startsWith(href);
              return (
                <Link
                  key={href}
                  href={href}
                  role="menuitem"
                  onClick={() => setOpen(false)}
                  className={`flex items-center gap-2 px-3 py-2 rounded-xl text-sm font-medium transition-colors ${active ? "bg-[var(--bg-tint)] text-[var(--ink)]" : "text-[var(--ink-soft)] hover:bg-[var(--bg-tint)] hover:text-[var(--ink)]"}`}
                >
                  <Icon size={15} />
                  <span>{t(labelKey)}</span>
                </Link>
              );
            })}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

function LocaleToggle({ className }: { className?: string }) {
  const { locale, setLocale, t } = useLocale();
  const opts: Locale[] = ["es", "en"];
  return (
    <div
      role="group"
      aria-label={t("nav.locale.switchTo")}
      className={`inline-flex items-center rounded-full hairline-strong bg-white p-0.5 ${className ?? ""}`}
    >
      {opts.map(opt => {
        const active = locale === opt;
        return (
          <button
            key={opt}
            type="button"
            onClick={() => setLocale(opt)}
            aria-pressed={active}
            className={`px-2 py-0.5 rounded-full text-[10px] font-extrabold uppercase tracking-wider transition-colors ${
              active
                ? "bg-[var(--ink)] text-white"
                : "text-[var(--ink-soft)] hover:text-[var(--ink)]"
            }`}
          >
            {opt}
          </button>
        );
      })}
    </div>
  );
}

export function Nav() {
  const pathname = usePathname();
  const router = useRouter();
  const { currentPlayer } = usePlayer();
  const { t } = useLocale();
  const isHome = pathname === "/";
  const isOwner = currentPlayer?.id === OWNER_ID;
  const moreLinks = isOwner ? [...SECONDARY_LINKS, ...ADMIN_LINKS] : SECONDARY_LINKS;

  const goBack = () => {
    if (typeof window !== "undefined" && window.history.length > 1) {
      router.back();
    } else {
      router.push("/");
    }
  };

  return (
    <header className="sticky top-0 z-50">
      <div className="container-app pt-4">
        <nav className="glass rounded-full px-3 py-2 flex items-center gap-2">
          {/* Logo + session indicator */}
          <div className="flex items-center gap-2 pl-2 pr-2">
            <div className="relative w-9 h-9">
              {currentPlayer ? (
                <>
                  <PlayerAvatar
                    player={currentPlayer}
                    size={36}
                    rounded="rounded-full"
                    textClass="text-base"
                    tint={0.2}
                    enableLightbox
                  />
                  <span
                    className="absolute -bottom-0.5 -right-0.5 w-3 h-3 rounded-full bg-[var(--accent-mint)] ring-2 ring-white pointer-events-none"
                    aria-hidden
                  />
                </>
              ) : (
                <Link
                  href="/jugadores"
                  aria-label={t("nav.session.aria.noSession")}
                  title={t("nav.session.title.noSession")}
                  className="relative w-9 h-9 rounded-full bg-[var(--ink)] grid place-items-center overflow-hidden"
                >
                  <span className="font-display text-white font-bold text-sm">26</span>
                  <span
                    className="absolute -bottom-0.5 -right-0.5 w-3 h-3 rounded-full bg-[#ef4444] ring-2 ring-white animate-pulse"
                    aria-hidden
                    title={t("nav.session.none")}
                  />
                </Link>
              )}
            </div>
            <Link
              href="/jugadores"
              aria-label={currentPlayer ? `${t("nav.session.aria.signedAs")}: ${currentPlayer.name}` : t("nav.session.aria.noSession")}
              title={currentPlayer ? `${t("nav.session.title.signedAs")} ${currentPlayer.name}` : t("nav.session.title.noSession")}
              className="hidden sm:flex flex-col leading-none"
            >
              <span className="text-[10px] font-medium uppercase tracking-[0.18em] text-[var(--ink-muted)]">
                {currentPlayer ? t("nav.session.signed") : t("nav.session.none")}
              </span>
              <span className="font-display text-sm font-bold">
                {currentPlayer ? currentPlayer.name : "Charales 2026"}
              </span>
            </Link>
          </div>

          {/* Mobile: back button (only on subpages) — sits next to avatar for thumb reach */}
          <AnimatePresence initial={false}>
            {!isHome && (
              <motion.button
                key="back-btn"
                onClick={goBack}
                aria-label={t("nav.back")}
                title={t("nav.back")}
                initial={{ opacity: 0, width: 0, marginLeft: 0 }}
                animate={{ opacity: 1, width: 40, marginLeft: 0 }}
                exit={{ opacity: 0, width: 0, marginLeft: 0 }}
                transition={{ duration: 0.18, ease: "easeOut" }}
                className="md:hidden h-10 rounded-full grid place-items-center hairline-strong bg-white overflow-hidden flex-shrink-0"
              >
                <ChevronLeft size={18} />
              </motion.button>
            )}
          </AnimatePresence>

          {/* Desktop primary links */}
          <ul className="hidden md:flex items-center gap-0.5 ml-2 flex-1">
            {PRIMARY_LINKS.map(({ href, labelKey, icon: Icon }) => {
              const active = href === "/" ? pathname === "/" : pathname.startsWith(href);
              return (
                <li key={href} className="relative">
                  <Link
                    href={href}
                    className={`relative flex items-center gap-1.5 px-3 py-2 rounded-full text-sm font-medium transition-colors ${active ? "text-[var(--ink)]" : "text-[var(--ink-soft)] hover:text-[var(--ink)]"}`}
                  >
                    {active && (
                      <motion.div
                        layoutId="nav-pill"
                        className="absolute inset-0 rounded-full bg-[var(--bg-tint)]"
                        transition={{ type: "spring", duration: 0.45 }}
                      />
                    )}
                    <Icon size={15} className="relative" />
                    <span className="relative">{t(labelKey)}</span>
                  </Link>
                </li>
              );
            })}
            <li className="relative">
              <MoreMenu links={moreLinks} pathname={pathname} t={t} />
            </li>
          </ul>

          {/* Player badge + locale toggle (desktop) */}
          <div className="ml-auto hidden md:flex items-center gap-2">
            <DailyStreakChip />
            <LocaleToggle />
            <Link href="/jugadores" className="flex items-center gap-2 px-2 py-1.5 rounded-full hairline-strong bg-white">
              {currentPlayer ? (
                <>
                  <PlayerAvatar player={currentPlayer} size={24} rounded="rounded-full" textClass="text-base" tint={0.2} enableLightbox />
                  <span className="text-sm font-semibold pr-1">{currentPlayer.name}</span>
                </>
              ) : (
                <span className="text-sm font-medium text-[var(--ink-soft)] px-2">{t("nav.session.choose")}</span>
              )}
            </Link>
          </div>

          {/* Mobile: streak + locale only — navigation handled by BottomNav */}
          <div className="md:hidden ml-auto flex items-center gap-1.5">
            <DailyStreakChip />
            <LocaleToggle />
          </div>
        </nav>

      </div>
    </header>
  );
}
