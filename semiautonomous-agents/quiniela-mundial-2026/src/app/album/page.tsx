"use client";

// Mundial 2026 sticker album. One spread per day, theme name in Spanish,
// all 10 charales' cromos for that date. Future days never appear — except
// for admin (cookie playerId === "jesus"), who sees every day up to the
// final and can generate any missing cromo per cell.

import { useCallback, useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { Album, Loader2, Sparkles, Lock } from "lucide-react";
import { PLAYERS, AI_PLAYER_ID } from "@/data/players";
import { CromoZoomModal, type CromoZoomTarget } from "@/components/CromoZoomModal";
import { useLiveScoreboard } from "@/lib/live-scoreboard";
import { prefetchRoast, type FinalsMap } from "@/lib/roast-cache";
import { intlLocale, useLocale, type Locale } from "@/lib/i18n";
import { allGroupFixtures, type GroupFixture } from "@/data/groups";
import { loadAllPredictionsFromServer, type PlayerPredictions, type Pick1X2 } from "@/lib/predictions";
import { TEAMS } from "@/data/teams";

type Cromo = { playerId: string; url: string; createdAt: number };
type Day = { date: string; style: string | null; cromos: Cromo[] };
type ApiResp = { ok: boolean; today: string; days: Day[]; admin?: boolean };

// Theme metadata mirrors STYLES + AI_STYLES in /api/cromos/portrait.
const THEME: Record<string, { label: string; accent: string; ink: string; pattern: string }> = {
  "ultimate-team":    { label: "Ultimate Team",  accent: "#D4AF37", ink: "#1a1208", pattern: "radial-gradient(circle at 1px 1px, #D4AF3722 1px, transparent 0)" },
  "lucha-libre":      { label: "Lucha Libre",    accent: "#DC2626", ink: "#3b0a0a", pattern: "repeating-linear-gradient(45deg, #DC262611 0 6px, transparent 6px 12px)" },
  "manga-shonen":     { label: "Manga Shōnen",   accent: "#7C3AED", ink: "#1a0b3a", pattern: "linear-gradient(135deg, #7C3AED11 25%, transparent 25%) 0 0/14px 14px" },
  "renaissance":      { label: "Renacimiento",   accent: "#A16207", ink: "#2a1c08", pattern: "radial-gradient(circle at 2px 2px, #A1620722 1.5px, transparent 0)" },
  "vaporwave":        { label: "Vaporwave",      accent: "#EC4899", ink: "#3a0a2a", pattern: "linear-gradient(180deg, #EC489911, transparent 70%)" },
  "comic-pop":        { label: "Comic Pop",      accent: "#FBBF24", ink: "#1a1408", pattern: "radial-gradient(circle at 2px 2px, #FBBF2433 2px, transparent 0)" },
  "studio-watercolor":{ label: "Acuarela",       accent: "#0EA5E9", ink: "#0a1a3a", pattern: "linear-gradient(120deg, #0EA5E911, transparent 80%)" },
  "ai-ultimate-team": { label: "AI · Ultimate",  accent: "#10B981", ink: "#08291f", pattern: "radial-gradient(circle at 1px 1px, #10B98122 1px, transparent 0)" },
  "ai-lucha-libre":   { label: "AI · Lucha",     accent: "#10B981", ink: "#08291f", pattern: "repeating-linear-gradient(45deg, #10B98111 0 6px, transparent 6px 12px)" },
  "ai-manga-shonen":  { label: "AI · Manga",     accent: "#10B981", ink: "#08291f", pattern: "linear-gradient(135deg, #10B98111 25%, transparent 25%) 0 0/14px 14px" },
  "ai-renaissance":   { label: "AI · Renacimiento", accent: "#10B981", ink: "#08291f", pattern: "radial-gradient(circle at 2px 2px, #10B98122 1.5px, transparent 0)" },
  "ai-vaporwave":     { label: "AI · Vaporwave", accent: "#10B981", ink: "#08291f", pattern: "linear-gradient(180deg, #10B98111, transparent 70%)" },
  "ai-comic-pop":     { label: "AI · Comic",     accent: "#10B981", ink: "#08291f", pattern: "radial-gradient(circle at 2px 2px, #10B98133 2px, transparent 0)" },
  "ai-cosmic-circuit":{ label: "AI · Cósmico",   accent: "#10B981", ink: "#08291f", pattern: "radial-gradient(circle at 1px 1px, #10B98122 1px, transparent 0)" },
  "azteca-codex":            { label: "Códice Azteca",    accent: "#14B8A6", ink: "#0a2924", pattern: "radial-gradient(circle at 2px 2px, #14B8A622 1.5px, transparent 0)" },
  "dia-muertos":             { label: "Día de Muertos",   accent: "#F97316", ink: "#3a1a08", pattern: "radial-gradient(circle at 2px 2px, #F9731633 2px, transparent 0)" },
  "mariachi-noche":          { label: "Mariachi de Noche",accent: "#1F2937", ink: "#0a0a14", pattern: "linear-gradient(135deg, #C0C0C022 25%, transparent 25%) 0 0/14px 14px" },
  "cyberpunk-cdmx":          { label: "Cyberpunk CDMX",   accent: "#EC4899", ink: "#0a0a2a", pattern: "linear-gradient(180deg, #06B6D411, #EC489911)" },
  "mural-rivera":            { label: "Mural · Rivera",   accent: "#C2410C", ink: "#2a1208", pattern: "linear-gradient(120deg, #C2410C11, transparent 80%)" },
  "loteria-card":            { label: "Lotería Mexicana", accent: "#DC2626", ink: "#2a0a0a", pattern: "radial-gradient(circle at 1px 1px, #DC262633 1.5px, transparent 0)" },
  "ukiyo-e":                 { label: "Ukiyo-e",          accent: "#1E40AF", ink: "#0a1029", pattern: "repeating-linear-gradient(90deg, #1E40AF11 0 8px, transparent 8px 16px)" },
  "art-deco":                { label: "Art Déco",         accent: "#B8860B", ink: "#1a1408", pattern: "linear-gradient(45deg, #B8860B22 25%, transparent 25%) 0 0/12px 12px" },
  "pixel-art-16bit":         { label: "Pixel Art 16-bit", accent: "#22C55E", ink: "#082a14", pattern: "repeating-linear-gradient(0deg, #22C55E11 0 4px, transparent 4px 8px), repeating-linear-gradient(90deg, #22C55E11 0 4px, transparent 4px 8px)" },
  "low-poly-3d":             { label: "Low Poly 3D",      accent: "#0EA5A5", ink: "#0a2424", pattern: "linear-gradient(135deg, #0EA5A511 25%, transparent 25%) 0 0/16px 16px" },
  "talavera-mosaic":         { label: "Talavera",         accent: "#1D4ED8", ink: "#0a1429", pattern: "radial-gradient(circle at 2px 2px, #1D4ED822 1.5px, transparent 0)" },
  "stained-glass":           { label: "Vitral",           accent: "#9F1239", ink: "#290a14", pattern: "linear-gradient(60deg, #9F123911 25%, transparent 25%) 0 0/14px 14px" },
  "sumi-e":                  { label: "Sumi-e",           accent: "#1F2937", ink: "#0a0a14", pattern: "radial-gradient(circle at 3px 3px, #DC262622 1px, transparent 0)" },
  "holographic-prizm":       { label: "Holográfico",      accent: "#A855F7", ink: "#1a0a2a", pattern: "linear-gradient(135deg, #A855F722, #06B6D422, #F472B622)" },
  "polaroid":                { label: "Polaroid",         accent: "#D97706", ink: "#2a1408", pattern: "radial-gradient(circle at 1px 1px, #D9770622 1px, transparent 0)" },
  "newspaper-vintage":       { label: "Periódico Vintage",accent: "#78716C", ink: "#1a1814", pattern: "radial-gradient(circle at 2px 2px, #78716C33 1.5px, transparent 0)" },
  "crayon-kids":             { label: "Crayón Infantil",  accent: "#EAB308", ink: "#2a2208", pattern: "linear-gradient(135deg, #EAB30822 25%, transparent 25%) 0 0/14px 14px" },
  "graffiti-mural":          { label: "Mural Graffiti",   accent: "#84CC16", ink: "#142a08", pattern: "linear-gradient(120deg, #EC489911, #84CC1611)" },
  "bauhaus":                 { label: "Bauhaus",          accent: "#DC2626", ink: "#2a0a0a", pattern: "linear-gradient(45deg, #DC262611 25%, transparent 25%, transparent 75%, #1D4ED811 75%) 0 0/16px 16px" },
  "retro-arcade-8bit":       { label: "Arcade 8-bit",     accent: "#F472B6", ink: "#2a0a1a", pattern: "repeating-linear-gradient(0deg, #F472B611 0 3px, transparent 3px 6px)" },
  "stencil-banksy":          { label: "Stencil",          accent: "#DC2626", ink: "#0a0a0a", pattern: "radial-gradient(circle at 1.5px 1.5px, #DC262633 1.5px, transparent 0)" },
  "velvet-painting":         { label: "Terciopelo",       accent: "#7F1D1D", ink: "#1a0808", pattern: "radial-gradient(ellipse at center, #F9731622, transparent 70%)" },
  "tarot-major":             { label: "Tarot Mayor",      accent: "#D4AF37", ink: "#0a0a2a", pattern: "radial-gradient(circle at 1px 1px, #D4AF3733 1px, transparent 0)" },
  "wpa-travel":              { label: "WPA Travel",       accent: "#0F766E", ink: "#0a2422", pattern: "linear-gradient(120deg, #0F766E11, transparent 80%)" },
  "cubism":                  { label: "Cubismo",          accent: "#A16207", ink: "#2a1c08", pattern: "linear-gradient(135deg, #A1620722 25%, transparent 25%) 0 0/16px 16px" },
  "saturday-cartoon-90s":    { label: "Saturday 90s",     accent: "#F472B6", ink: "#2a0a1a", pattern: "linear-gradient(180deg, #06B6D422, #F472B622)" },
  "neon-tube":               { label: "Neón",             accent: "#06B6D4", ink: "#0a2429", pattern: "linear-gradient(180deg, #06B6D422, transparent 70%)" },
  "embroidery-cross-stitch": { label: "Punto de Cruz",    accent: "#B91C1C", ink: "#290a0a", pattern: "repeating-linear-gradient(45deg, #B91C1C22 0 4px, transparent 4px 8px)" },
  "rotulista-mexico":        { label: "Rotulista MX",     accent: "#EAB308", ink: "#2a2208", pattern: "linear-gradient(135deg, #EAB30811, #DC262611, #16A34A11)" },
  "blueprint":               { label: "Blueprint",        accent: "#1D4ED8", ink: "#0a1429", pattern: "repeating-linear-gradient(0deg, #1D4ED822 0 1px, transparent 1px 14px), repeating-linear-gradient(90deg, #1D4ED822 0 1px, transparent 1px 14px)" },
  "alebrije":                { label: "Alebrije",         accent: "#D946EF", ink: "#290a2a", pattern: "radial-gradient(circle at 1.5px 1.5px, #D946EF33 1.5px, transparent 0)" },
  "papel-picado":            { label: "Papel Picado",     accent: "#F472B6", ink: "#2a0a1a", pattern: "linear-gradient(135deg, #F472B611 25%, #F9731611 25% 50%, #84CC1611 50% 75%, #06B6D411 75%) 0 0/20px 20px" },
  "art-nouveau":             { label: "Art Nouveau",      accent: "#D4A373", ink: "#2a1c08", pattern: "radial-gradient(ellipse at center, #D4A37322, transparent 70%)" },
  "ai-azteca-codex":         { label: "AI · Códice",      accent: "#10B981", ink: "#08291f", pattern: "radial-gradient(circle at 2px 2px, #10B98122 1.5px, transparent 0)" },
  "ai-dia-muertos":          { label: "AI · Día Muertos", accent: "#10B981", ink: "#08291f", pattern: "radial-gradient(circle at 2px 2px, #10B98133 2px, transparent 0)" },
  "ai-mariachi-noche":       { label: "AI · Mariachi",    accent: "#10B981", ink: "#08291f", pattern: "linear-gradient(135deg, #10B98111 25%, transparent 25%) 0 0/14px 14px" },
  "ai-cyberpunk-cdmx":       { label: "AI · Cyberpunk",   accent: "#10B981", ink: "#08291f", pattern: "linear-gradient(180deg, #10B98111, transparent 70%)" },
  "ai-mural-rivera":         { label: "AI · Mural Rivera",accent: "#10B981", ink: "#08291f", pattern: "linear-gradient(120deg, #10B98111, transparent 80%)" },
  "ai-loteria-card":         { label: "AI · Lotería",     accent: "#10B981", ink: "#08291f", pattern: "radial-gradient(circle at 1px 1px, #10B98133 1.5px, transparent 0)" },
  "ai-ukiyo-e":              { label: "AI · Ukiyo-e",     accent: "#10B981", ink: "#08291f", pattern: "repeating-linear-gradient(90deg, #10B98111 0 8px, transparent 8px 16px)" },
  "ai-art-deco":             { label: "AI · Art Déco",    accent: "#10B981", ink: "#08291f", pattern: "linear-gradient(45deg, #10B98122 25%, transparent 25%) 0 0/12px 12px" },
  "ai-pixel-art-16bit":      { label: "AI · Pixel 16-bit",accent: "#10B981", ink: "#08291f", pattern: "repeating-linear-gradient(0deg, #10B98111 0 4px, transparent 4px 8px)" },
  "ai-low-poly-3d":          { label: "AI · Low Poly",    accent: "#10B981", ink: "#08291f", pattern: "linear-gradient(135deg, #10B98111 25%, transparent 25%) 0 0/16px 16px" },
  "ai-talavera-mosaic":      { label: "AI · Talavera",    accent: "#10B981", ink: "#08291f", pattern: "radial-gradient(circle at 2px 2px, #10B98122 1.5px, transparent 0)" },
  "ai-stained-glass":        { label: "AI · Vitral",      accent: "#10B981", ink: "#08291f", pattern: "linear-gradient(60deg, #10B98111 25%, transparent 25%) 0 0/14px 14px" },
  "ai-sumi-e":               { label: "AI · Sumi-e",      accent: "#10B981", ink: "#08291f", pattern: "radial-gradient(circle at 3px 3px, #10B98122 1px, transparent 0)" },
  "ai-holographic-prizm":    { label: "AI · Holográfico", accent: "#10B981", ink: "#08291f", pattern: "linear-gradient(135deg, #10B98122, transparent 70%)" },
  "ai-polaroid":             { label: "AI · Polaroid",    accent: "#10B981", ink: "#08291f", pattern: "radial-gradient(circle at 1px 1px, #10B98122 1px, transparent 0)" },
  "ai-newspaper-vintage":    { label: "AI · Periódico",   accent: "#10B981", ink: "#08291f", pattern: "radial-gradient(circle at 2px 2px, #10B98133 1.5px, transparent 0)" },
  "ai-crayon-kids":          { label: "AI · Crayón",      accent: "#10B981", ink: "#08291f", pattern: "linear-gradient(135deg, #10B98122 25%, transparent 25%) 0 0/14px 14px" },
  "ai-graffiti-mural":       { label: "AI · Graffiti",    accent: "#10B981", ink: "#08291f", pattern: "linear-gradient(120deg, #10B98111, transparent 80%)" },
  "ai-bauhaus":              { label: "AI · Bauhaus",     accent: "#10B981", ink: "#08291f", pattern: "linear-gradient(45deg, #10B98111 25%, transparent 25%, transparent 75%, #10B98111 75%) 0 0/16px 16px" },
  "ai-retro-arcade-8bit":    { label: "AI · Arcade",      accent: "#10B981", ink: "#08291f", pattern: "repeating-linear-gradient(0deg, #10B98111 0 3px, transparent 3px 6px)" },
  "ai-stencil-banksy":       { label: "AI · Stencil",     accent: "#10B981", ink: "#08291f", pattern: "radial-gradient(circle at 1.5px 1.5px, #10B98133 1.5px, transparent 0)" },
  "ai-velvet-painting":      { label: "AI · Terciopelo",  accent: "#10B981", ink: "#08291f", pattern: "radial-gradient(ellipse at center, #10B98122, transparent 70%)" },
  "ai-tarot-major":          { label: "AI · Tarot",       accent: "#10B981", ink: "#08291f", pattern: "radial-gradient(circle at 1px 1px, #10B98133 1px, transparent 0)" },
  "ai-wpa-travel":           { label: "AI · WPA",         accent: "#10B981", ink: "#08291f", pattern: "linear-gradient(120deg, #10B98111, transparent 80%)" },
  "ai-cubism":               { label: "AI · Cubismo",     accent: "#10B981", ink: "#08291f", pattern: "linear-gradient(135deg, #10B98122 25%, transparent 25%) 0 0/16px 16px" },
  "ai-saturday-cartoon-90s": { label: "AI · Saturday 90s",accent: "#10B981", ink: "#08291f", pattern: "linear-gradient(180deg, #10B98122, transparent 70%)" },
  "ai-neon-tube":            { label: "AI · Neón",        accent: "#10B981", ink: "#08291f", pattern: "linear-gradient(180deg, #10B98122, transparent 70%)" },
  "ai-embroidery-cross-stitch":{label:"AI · Punto Cruz",  accent: "#10B981", ink: "#08291f", pattern: "repeating-linear-gradient(45deg, #10B98122 0 4px, transparent 4px 8px)" },
  "ai-rotulista-mexico":     { label: "AI · Rotulista",   accent: "#10B981", ink: "#08291f", pattern: "linear-gradient(135deg, #10B98111, #10B98122)" },
  "ai-blueprint":            { label: "AI · Blueprint",   accent: "#10B981", ink: "#08291f", pattern: "repeating-linear-gradient(0deg, #10B98122 0 1px, transparent 1px 14px)" },
  "ai-alebrije":             { label: "AI · Alebrije",    accent: "#10B981", ink: "#08291f", pattern: "radial-gradient(circle at 1.5px 1.5px, #10B98133 1.5px, transparent 0)" },
  "ai-papel-picado":         { label: "AI · Papel Picado",accent: "#10B981", ink: "#08291f", pattern: "linear-gradient(135deg, #10B98111 25%, transparent 25%) 0 0/20px 20px" },
  "ai-art-nouveau":          { label: "AI · Art Nouveau", accent: "#10B981", ink: "#08291f", pattern: "radial-gradient(ellipse at center, #10B98122, transparent 70%)" },
};

const DEFAULT_THEME = { label: "Sin tema", accent: "#64748B", ink: "#1a1a2a", pattern: "none" };

// Charales are stamped into ordered slots — keeps the album visually consistent
// page-to-page. AI takes the last slot like the "joker" sticker.
const SLOT_ORDER = PLAYERS.map(p => p.id);

function themeFor(style: string | null): { label: string; accent: string; ink: string; pattern: string } {
  if (!style) return DEFAULT_THEME;
  return THEME[style] ?? { ...DEFAULT_THEME, label: style };
}

function formatDateLong(dateStr: string, locale: Locale): string {
  // dateStr is "YYYY-MM-DD" already in ET; parse as that local date.
  const [y, m, d] = dateStr.split("-").map(n => parseInt(n, 10));
  const date = new Date(Date.UTC(y, m - 1, d));
  const intl = intlLocale(locale);
  const weekday = new Intl.DateTimeFormat(intl, { weekday: "long", timeZone: "UTC" }).format(date);
  const day = new Intl.DateTimeFormat(intl, { day: "numeric", timeZone: "UTC" }).format(date);
  const month = new Intl.DateTimeFormat(intl, { month: "long", timeZone: "UTC" }).format(date);
  return `${weekday.charAt(0).toUpperCase()}${weekday.slice(1)} · ${day} ${month}`;
}

function relativeLabel(dateStr: string, today: string, t: (k: string, f?: string) => string): string | null {
  if (dateStr === today) return t("album.relative.today");
  const todayMs = Date.UTC(...today.split("-").map((n, i) => i === 1 ? parseInt(n, 10) - 1 : parseInt(n, 10)) as [number, number, number]);
  const dateMs = Date.UTC(...dateStr.split("-").map((n, i) => i === 1 ? parseInt(n, 10) - 1 : parseInt(n, 10)) as [number, number, number]);
  const days = Math.round((todayMs - dateMs) / 86400000);
  if (days === 1) return t("album.relative.yesterday");
  if (days < 7) return t("album.relative.daysAgo").replace("{n}", String(days));
  return null;
}

export default function AlbumPage() {
  const [data, setData] = useState<ApiResp | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [lightbox, setLightbox] = useState<CromoZoomTarget | null>(null);
  const [generating, setGenerating] = useState<Set<string>>(new Set());
  const [genError, setGenError] = useState<string | null>(null);
  const { finals: liveFinals, loading: finalsLoading } = useLiveScoreboard();
  const { t, locale } = useLocale();
  // The roast cache expects a plain FinalsMap; useLiveScoreboard returns a
  // shape-compatible RealResults so we just retype it.
  const finalsForRoast = liveFinals as unknown as FinalsMap;

  const fetchAlbum = useCallback(async () => {
    const r = await fetch("/api/cromos/album", { cache: "no-store" });
    const j = (await r.json()) as ApiResp;
    setData(j);
    return j;
  }, []);

  useEffect(() => {
    let cancelled = false;
    fetch("/api/cromos/album", { cache: "no-store" })
      .then(r => r.json())
      .then((j: ApiResp) => { if (!cancelled) setData(j); })
      .catch(e => { if (!cancelled) setError(e instanceof Error ? e.message : "Error de red"); });
    return () => { cancelled = true; };
  }, []);

  const isAdmin = data?.admin === true;
  const days = data?.days ?? [];
  const today = data?.today ?? "";
  const totalPages = days.length;

  // Pre-warm Ava roasts for every charal once finals are ready so the modal
  // renders the analysis with zero latency on click. The cache is invalidated
  // by the finals hash so a new marker arrival re-fires automatically.
  useEffect(() => {
    if (finalsLoading || !data) return;
    const playerIds = new Set<string>();
    for (const d of data.days) for (const c of d.cromos) playerIds.add(c.playerId);
    for (const pid of playerIds) prefetchRoast(pid, finalsForRoast);
  }, [data, finalsLoading, finalsForRoast]);

  const generateCromo = useCallback(async (playerId: string, date: string) => {
    const key = `${playerId}_${date}`;
    setGenError(null);
    setGenerating(prev => { const next = new Set(prev); next.add(key); return next; });
    try {
      const r = await fetch("/api/cromos/portrait", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ playerId, date }),
      });
      const j = await r.json();
      if (!r.ok || !j.ok) throw new Error(j.error || j.reason || `HTTP ${r.status}`);
      await fetchAlbum();
    } catch (e) {
      setGenError(`${key}: ${e instanceof Error ? e.message : "error"}`);
    } finally {
      setGenerating(prev => { const next = new Set(prev); next.delete(key); return next; });
    }
  }, [fetchAlbum]);

  return (
    <main className="min-h-screen bg-[var(--bg)] pb-36">
      {/* Cover header */}
      <section className="max-w-3xl mx-auto px-4 pt-6">
        <div
          className="relative rounded-3xl overflow-hidden p-6 sm:p-8 text-white shadow-2xl border border-white/10"
          style={{
            background:
              "linear-gradient(135deg, #004d33 0%, #0f172a 50%, #881337 100%)",
          }}
        >
          {/* Gold accent line & mesh pattern */}
          <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-emerald-400 via-amber-300 to-rose-500" />
          <div className="absolute inset-0 pointer-events-none opacity-20" style={{ background: "radial-gradient(circle at 1.5px 1.5px, rgba(255,255,255,0.4) 1px, transparent 0) 0 0/14px 14px" }} />

          {/* Frosted card container for 100% contrast */}
          <div className="relative rounded-2xl bg-slate-950/50 backdrop-blur-md p-5 border border-white/10 shadow-inner">
            <div className="flex items-start justify-between gap-4">
              <div>
                <div className="text-[11px] uppercase tracking-[0.25em] text-amber-400 font-extrabold flex items-center gap-1.5">
                  <Sparkles size={12} className="text-amber-400" />
                  {t("album.cover.kicker")}
                </div>
                <h1 className="font-display text-3xl sm:text-4xl font-black leading-tight mt-1 text-white drop-shadow">
                  {t("album.cover.title")}
                </h1>
                <p className="text-sm mt-2 max-w-md text-slate-200 font-medium leading-relaxed">
                  {t("album.cover.subtitle")}
                </p>
              </div>
              <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-amber-400/20 to-emerald-400/20 border border-white/20 grid place-items-center shrink-0 shadow-lg">
                <Album size={28} className="text-amber-300" />
              </div>
            </div>

            <div className="mt-6 flex items-center justify-between gap-4 pt-4 border-t border-white/10">
              <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-500/20 border border-emerald-500/30 text-emerald-300 text-xs font-bold uppercase tracking-wider">
                {totalPages > 0 ? `${totalPages} ${totalPages === 1 ? t("album.cover.pages.one") : t("album.cover.pages.many")}` : t("album.cover.empty")}
              </span>
              <Link href="/" className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-full bg-white/10 hover:bg-white/20 text-white text-xs font-semibold transition-colors">
                ← {t("album.cover.home")}
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Spreads */}
      <div className="max-w-3xl mx-auto px-4 mt-6 space-y-6">
        {error && (
          <div className="rounded-2xl bg-red-50 border border-red-200 px-4 py-3 text-sm text-red-800">
            {error}
          </div>
        )}
        {!data && !error && (
          <div className="py-16 text-center text-sm text-[var(--ink-muted)]">{t("album.opening")}</div>
        )}
        {data && days.length === 0 && (
          <div className="rounded-3xl border-2 border-dashed border-[var(--line-strong)] py-16 text-center">
            <Album size={28} className="mx-auto text-[var(--ink-muted)]" />
            <div className="mt-3 font-display font-bold text-[var(--ink)]">{t("album.empty.title")}</div>
            <div className="text-xs text-[var(--ink-muted)] mt-1">{t("album.empty.copy")}</div>
          </div>
        )}

        {genError && (
          <div className="rounded-2xl bg-amber-50 border border-amber-200 px-4 py-3 text-sm text-amber-800">
            {genError}
          </div>
        )}

        {days.map((day, idx) => (
          <Spread
            key={day.date}
            day={day}
            pageNumber={idx + 1}
            isToday={day.date === today}
            isFuture={day.date > today}
            relative={relativeLabel(day.date, today, t)}
            isAdmin={isAdmin}
            generating={generating}
            onGenerate={generateCromo}
            locale={locale}
            onCromoClick={(c, theme) => setLightbox({ cromoUrl: c.url, playerId: c.playerId, date: day.date, theme })}
          />
        ))}

        {today && <MysteryCard today={today} />}

        <div className="pt-2 text-center text-[10px] uppercase tracking-[0.2em] text-[var(--ink-muted)]">
          {isAdmin
            ? t("album.footer.admin")
            : t("album.footer.public")}
        </div>
      </div>

      {/* Cromo zoom modal: big image + Ava analysis + verdicts table + download */}
      <CromoZoomModal
        target={lightbox}
        finals={finalsForRoast}
        finalsLoading={finalsLoading}
        onClose={() => setLightbox(null)}
      />
    </main>
  );
}

function Spread({
  day, pageNumber, isToday, isFuture, relative, isAdmin, generating, onGenerate, onCromoClick, locale,
}: {
  day: Day;
  pageNumber: number;
  isToday: boolean;
  isFuture: boolean;
  relative: string | null;
  isAdmin: boolean;
  generating: Set<string>;
  onGenerate: (playerId: string, date: string) => void;
  onCromoClick: (c: Cromo, t: { label: string; accent: string }) => void;
  locale: Locale;
}) {
  const { t } = useLocale();
  const theme = themeFor(day.style);
  const cromosByPlayer = useMemo(() => {
    const map = new Map<string, Cromo>();
    for (const c of day.cromos) map.set(c.playerId, c);
    return map;
  }, [day.cromos]);
  const missing = useMemo(() => SLOT_ORDER.filter(pid => !cromosByPlayer.has(pid)), [cromosByPlayer]);
  const allBusy = missing.length > 0 && missing.every(pid => generating.has(`${pid}_${day.date}`));
  const generateAll = useCallback(() => {
    for (const pid of missing) {
      if (!generating.has(`${pid}_${day.date}`)) onGenerate(pid, day.date);
    }
  }, [missing, generating, onGenerate, day.date]);

  return (
    <article
      className={`relative rounded-[28px] overflow-hidden border shadow-lg ${isFuture ? "border-dashed border-[var(--line-strong)]" : "border-[var(--line)]"}`}
      style={{
        background: `linear-gradient(180deg, #fffaf0 0%, #fff 12%, #fff 100%)`,
      }}
    >
      {/* Pattern band */}
      <div className="absolute inset-x-0 top-0 h-32 pointer-events-none opacity-70" style={{ background: theme.pattern }} />
      {/* Accent rail */}
      <div className="absolute left-0 top-0 bottom-0 w-1.5" style={{ background: theme.accent }} />

      <div className="relative p-5 sm:p-6">
        {/* Header */}
        <div className="flex items-start justify-between gap-3">
          <div className="min-w-0">
            <div className="flex items-center gap-2 text-[10px] uppercase tracking-[0.2em] text-[var(--ink-muted)] font-bold flex-wrap">
              <span>{t("album.spread.page")} {String(pageNumber).padStart(2, "0")}</span>
              {isToday && (
                <span className="px-2 py-0.5 rounded-full text-white font-black tracking-wider" style={{ background: theme.accent }}>
                  {t("album.spread.today")}
                </span>
              )}
              {!isToday && !isFuture && relative && (
                <span className="text-[var(--ink-soft)]">· {relative}</span>
              )}
              {isFuture && (
                <span className="px-2 py-0.5 rounded-full bg-[var(--bg-tint)] text-[var(--ink-soft)] font-black tracking-wider flex items-center gap-1">
                  <Sparkles size={9} /> {t("album.spread.upcoming")}
                </span>
              )}
            </div>
            <div className="font-display text-xl sm:text-2xl font-black mt-1 text-[var(--ink)] truncate">
              {formatDateLong(day.date, locale)}
            </div>
          </div>
          <div className="shrink-0 text-right">
            <div className="text-[10px] uppercase tracking-[0.18em] text-[var(--ink-muted)] font-bold">{t("album.spread.theme")}</div>
            <div
              className="mt-1 inline-flex items-center px-3 py-1.5 rounded-full text-white text-sm font-black font-display shadow-sm"
              style={{ background: theme.accent, color: "white" }}
            >
              {theme.label}
            </div>
          </div>
        </div>

        {/* Admin batch action */}
        {isAdmin && missing.length > 0 && (
          <div className="mt-4 flex items-center justify-between gap-3 rounded-2xl bg-[var(--bg-tint)] hairline-strong px-3 py-2">
            <div className="text-[11px] font-bold text-[var(--ink-soft)]">
              {missing.length} {missing.length === 1 ? t("album.spread.missing.one") : t("album.spread.missing.many")}
            </div>
            <button
              type="button"
              onClick={generateAll}
              disabled={allBusy}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-[var(--ink)] text-white text-xs font-bold disabled:opacity-50"
            >
              {allBusy ? <Loader2 size={12} className="animate-spin" /> : <Sparkles size={12} />}
              {t("album.spread.generateAll")}
            </button>
          </div>
        )}

        {/* Sticker grid */}
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-3 mt-5">
          {SLOT_ORDER.map(playerId => {
            const player = PLAYERS.find(p => p.id === playerId);
            if (!player) return null;
            const cromo = cromosByPlayer.get(playerId);
            const busy = generating.has(`${playerId}_${day.date}`);
            return (
              <CromoSlot
                key={playerId}
                playerId={playerId}
                date={day.date}
                playerName={player.name}
                accent={player.accent ?? theme.accent}
                cromo={cromo}
                isAdmin={isAdmin}
                busy={busy}
                onGenerate={onGenerate}
                onClick={() => cromo && onCromoClick(cromo, { label: theme.label, accent: theme.accent })}
              />
            );
          })}
        </div>

        {/* Corner ornaments */}
        <div className="absolute top-3 right-3 w-2 h-2 rounded-full" style={{ background: theme.accent, opacity: 0.4 }} />
        <div className="absolute bottom-3 left-3 w-2 h-2 rounded-full" style={{ background: theme.accent, opacity: 0.4 }} />
      </div>
    </article>
  );
}

function CromoSlot({
  playerId, date, playerName, accent, cromo, isAdmin, busy, onGenerate, onClick,
}: {
  playerId: string;
  date: string;
  playerName: string;
  accent: string;
  cromo?: Cromo;
  isAdmin: boolean;
  busy: boolean;
  onGenerate: (playerId: string, date: string) => void;
  onClick: () => void;
}) {
  const { t } = useLocale();
  const initial = playerName.charAt(0).toUpperCase();
  if (!cromo) {
    return (
      <div className="relative aspect-[3/4] rounded-xl border-2 border-dashed border-[var(--line-strong)] bg-[var(--bg-tint)] grid place-items-center p-2">
        <div className="text-center w-full">
          <div
            className="mx-auto w-8 h-8 rounded-full grid place-items-center font-display font-black text-white text-sm opacity-60"
            style={{ background: accent }}
          >
            {initial}
          </div>
          <div className="text-[9px] uppercase tracking-wider text-[var(--ink-muted)] font-bold mt-1.5">
            {playerName}
          </div>
          {isAdmin ? (
            <button
              type="button"
              onClick={() => !busy && onGenerate(playerId, date)}
              disabled={busy}
              className="mt-2 inline-flex items-center gap-1 px-2 py-1 rounded-full bg-[var(--ink)] text-white text-[9px] font-bold disabled:opacity-60"
            >
              {busy ? <Loader2 size={9} className="animate-spin" /> : <Sparkles size={9} />}
              {busy ? t("album.spread.generating") : t("album.spread.generate")}
            </button>
          ) : (
            <div className="text-[8px] text-[var(--ink-muted)] italic mt-1">{t("album.spread.pending")}</div>
          )}
        </div>
      </div>
    );
  }
  return (
    <button
      type="button"
      onClick={onClick}
      className="group relative aspect-[3/4] rounded-xl overflow-hidden ring-2 ring-white shadow-md transition-transform hover:-translate-y-0.5 active:scale-95"
      style={{ boxShadow: `0 8px 20px -6px ${accent}77` }}
      aria-label={`Ver cromo de ${playerName}`}
    >
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img src={cromo.url} alt={playerName} className="w-full h-full object-cover" />
      <div className="absolute inset-x-0 bottom-0 px-2 py-1.5 bg-gradient-to-t from-black/85 via-black/40 to-transparent">
        <div className="text-[10px] uppercase tracking-wider text-white font-black truncate">{playerName}</div>
      </div>
    </button>
  );
}

// Mystery card: shows below the spreads. Tracks tomorrow's fixtures; once
// every human charal has at least one pick for them, it reveals the pool's
// MAJORITY pick per fixture. Pure client-side computation — no album route
// change. Zero pts impact.
function MysteryCard({ today }: { today: string }) {
  const { t } = useLocale();
  const [picks, setPicks] = useState<PlayerPredictions[] | null>(null);

  // Tomorrow in ET (album's "today" already lives in ET).
  const tomorrow = useMemo(() => shiftDateStr(today, 1), [today]);
  const tomorrowFixtures = useMemo<GroupFixture[]>(
    () => allGroupFixtures().filter(fx => fx.date === tomorrow),
    [tomorrow],
  );

  useEffect(() => {
    if (tomorrowFixtures.length === 0) { setPicks([]); return; }
    let cancelled = false;
    loadAllPredictionsFromServer()
      .then(all => { if (!cancelled) setPicks(all); })
      .catch(() => { if (!cancelled) setPicks([]); });
    return () => { cancelled = true; };
  }, [tomorrowFixtures.length, tomorrow]);

  if (tomorrowFixtures.length === 0) return null;

  const humanIds = PLAYERS.filter(p => p.id !== AI_PLAYER_ID).map(p => p.id);
  const total = humanIds.length;
  const ready = picks !== null;

  // A human is "ready" for tomorrow if they have a pick on EVERY tomorrow fixture.
  const humansReady = ready
    ? humanIds.filter(pid => {
        const p = picks!.find(x => x.playerId === pid);
        if (!p) return false;
        return tomorrowFixtures.every(fx => !!p.group[fx.id]?.pick);
      })
    : [];
  const allPicked = ready && humansReady.length === total;

  return (
    <article
      className="relative rounded-[28px] overflow-hidden border-2 border-dashed border-[var(--line-strong)] shadow-sm bg-white"
    >
      <div className="absolute left-0 top-0 bottom-0 w-1.5" style={{ background: "#7C3AED" }} />
      <div className="p-5 sm:p-6">
        <div className="flex items-start justify-between gap-3">
          <div>
            <div className="flex items-center gap-2 text-[10px] uppercase tracking-[0.2em] text-[var(--ink-muted)] font-bold">
              <Lock size={11} />
              <span>{t("mystery.title")}</span>
            </div>
            <div className="font-display text-xl sm:text-2xl font-black mt-1 text-[var(--ink)]">
              {allPicked ? t("mystery.revealed") : "🔒 " + t("mystery.title")}
            </div>
            <div className="text-xs text-[var(--ink-soft)] mt-1">
              {tomorrow} · {tomorrowFixtures.length} {tomorrowFixtures.length === 1 ? "partido" : "partidos"}
            </div>
          </div>
          <span
            className="px-2 py-0.5 rounded-full text-white font-black tracking-wider text-[10px]"
            style={{ background: allPicked ? "#16A34A" : "#7C3AED" }}
          >
            {t("mystery.progress").replace("{done}", String(humansReady.length)).replace("{total}", String(total))}
          </span>
        </div>

        {!allPicked && (
          <p className="mt-4 text-sm text-[var(--ink-soft)]">
            {t("mystery.locked")}
          </p>
        )}

        <div className="mt-5 grid grid-cols-1 sm:grid-cols-2 gap-3">
          {tomorrowFixtures.map(fx => (
            <MysteryFixtureCell key={fx.id} fixture={fx} picks={picks} revealed={allPicked} />
          ))}
        </div>

        {/* Progress bar */}
        <div className="mt-5 h-1.5 rounded-full bg-[var(--bg-tint)] overflow-hidden">
          <div
            className="h-full rounded-full transition-all"
            style={{
              width: `${Math.round((humansReady.length / Math.max(1, total)) * 100)}%`,
              background: allPicked ? "#16A34A" : "#7C3AED",
            }}
          />
        </div>
      </div>
    </article>
  );
}

function MysteryFixtureCell({
  fixture, picks, revealed,
}: { fixture: GroupFixture; picks: PlayerPredictions[] | null; revealed: boolean }) {
  const home = TEAMS.find(t => t.code === fixture.home)?.name ?? fixture.home;
  const away = TEAMS.find(t => t.code === fixture.away)?.name ?? fixture.away;
  let majority: { pick: Pick1X2; count: number } | null = null;
  if (revealed && picks) {
    const tally: Record<Pick1X2, number> = { H: 0, D: 0, A: 0 };
    for (const p of picks) {
      if (p.playerId === AI_PLAYER_ID) continue;
      const v = p.group[fixture.id]?.pick;
      if (v === "H" || v === "D" || v === "A") tally[v] += 1;
    }
    const ordered: Pick1X2[] = ["H", "D", "A"];
    ordered.sort((a, b) => tally[b] - tally[a]);
    majority = { pick: ordered[0], count: tally[ordered[0]] };
  }
  const label = majority
    ? majority.pick === "H" ? home : majority.pick === "A" ? away : "Empate"
    : "—";
  return (
    <div className={`rounded-2xl px-3 py-3 ${revealed ? "bg-[var(--bg-tint)]" : "bg-[var(--bg-tint)] opacity-70"}`}>
      <div className="text-[10px] uppercase tracking-wider text-[var(--ink-muted)] font-bold">
        {fixture.group} · {fixture.kickoffLocal}
      </div>
      <div className="font-display font-black text-sm leading-tight mt-1">{home} vs {away}</div>
      <div className="mt-2 text-xs">
        {revealed && majority ? (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-white hairline font-bold">
            {label} · {majority.count}/10
          </span>
        ) : (
          <span className="text-[var(--ink-muted)] italic">esperando picks…</span>
        )}
      </div>
    </div>
  );
}

// Shift a YYYY-MM-DD ET-anchored date string by N days. We don't use the
// host TZ here — the album already keys everything in ET, so adding 86_400_000
// to the noon-UTC anchor is DST-safe.
function shiftDateStr(iso: string, days: number): string {
  const anchor = new Date(`${iso}T12:00:00Z`).getTime();
  const next = new Date(anchor + days * 86_400_000);
  return new Intl.DateTimeFormat("en-CA", {
    timeZone: "America/New_York",
    year: "numeric", month: "2-digit", day: "2-digit",
  }).format(next);
}
