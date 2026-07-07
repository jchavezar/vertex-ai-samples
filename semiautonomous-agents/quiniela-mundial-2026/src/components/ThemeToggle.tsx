"use client";

import { useEffect, useState } from "react";
import { Sun, Moon, Sparkles } from "lucide-react";

export type ThemeMode = "light" | "cyberpunk-emerald";

export function ThemeToggle() {
  const [theme, setTheme] = useState<ThemeMode>("light");
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    try {
      const saved = localStorage.getItem("q26_theme") as ThemeMode | null;
      if (saved === "cyberpunk-emerald" || saved === "light") {
        setTheme(saved);
        document.documentElement.setAttribute("data-theme", saved);
      }
    } catch {}
  }, []);

  const toggleTheme = () => {
    const next: ThemeMode = theme === "light" ? "cyberpunk-emerald" : "light";
    setTheme(next);
    try {
      localStorage.setItem("q26_theme", next);
    } catch {}
    if (next === "light") {
      document.documentElement.removeAttribute("data-theme");
    } else {
      document.documentElement.setAttribute("data-theme", next);
    }
  };

  if (!mounted) return null;

  return (
    <button
      onClick={toggleTheme}
      type="button"
      className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium transition-all shadow-sm border focus:outline-none"
      style={{
        background: theme === "cyberpunk-emerald" ? "rgba(0, 245, 155, 0.12)" : "var(--bg-elev)",
        borderColor: theme === "cyberpunk-emerald" ? "rgba(0, 245, 155, 0.4)" : "var(--line)",
        color: theme === "cyberpunk-emerald" ? "#00F59B" : "var(--ink)",
      }}
      title={theme === "light" ? "Cambiar a Modo Cyberpunk" : "Cambiar a Modo Claro"}
      aria-label="Toggle Theme"
    >
      {theme === "light" ? (
        <>
          <Moon size={14} className="text-[var(--ink-soft)]" />
          <span>Modo Oscuro</span>
        </>
      ) : (
        <>
          <Sparkles size={14} className="text-[#00F59B] animate-pulse" />
          <span className="font-bold tracking-wide">Cyberpunk</span>
        </>
      )}
    </button>
  );
}
