"use client";

import { useEffect, useState } from "react";
import { Sparkles, Sun } from "lucide-react";

export function ThemeToggle() {
  const [theme, setTheme] = useState<"light" | "cyberpunk-emerald">("cyberpunk-emerald");
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    const saved = localStorage.getItem("q26_theme") as "light" | "cyberpunk-emerald" | null;
    if (saved === "light") {
      setTheme("light");
      document.documentElement.removeAttribute("data-theme");
    } else {
      setTheme("cyberpunk-emerald");
      document.documentElement.setAttribute("data-theme", "cyberpunk-emerald");
    }
  }, []);

  const toggleTheme = () => {
    const next = theme === "light" ? "cyberpunk-emerald" : "light";
    setTheme(next);
    if (next === "cyberpunk-emerald") {
      localStorage.setItem("q26_theme", "cyberpunk-emerald");
      document.documentElement.setAttribute("data-theme", "cyberpunk-emerald");
    } else {
      localStorage.setItem("q26_theme", "light");
      document.documentElement.removeAttribute("data-theme");
    }
  };

  if (!mounted) return null;

  return (
    <button
      type="button"
      onClick={toggleTheme}
      className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-bold transition-all cursor-pointer ${
        theme === "cyberpunk-emerald"
          ? "bg-[#00F59B] text-[#0A0B0E] shadow-[0_0_12px_rgba(0,245,155,0.4)] hover:bg-[#26FFAC]"
          : "bg-slate-900 text-white shadow-sm hover:bg-slate-800"
      }`}
      title="Cambiar tema de la Quiniela"
    >
      {theme === "cyberpunk-emerald" ? (
        <>
          <Sparkles className="w-3.5 h-3.5 text-[#0A0B0E]" />
          <span>Cyberpunk</span>
        </>
      ) : (
        <>
          <Sun className="w-3.5 h-3.5 text-amber-400" />
          <span>Modo Claro</span>
        </>
      )}
    </button>
  );
}
