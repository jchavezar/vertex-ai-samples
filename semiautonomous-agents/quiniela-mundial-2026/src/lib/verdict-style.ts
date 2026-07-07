// Shared verdict badge styling. Used by /jugadores/[id] and the album cromo
// modal so the "exacto / acertaste / mamaste / no llenó" lozenges look identical
// everywhere a per-fixture row gets rendered.

import type { Verdict } from "@/lib/roast-cache";

// Map each verdict to the i18n key for its label. Pass through useLocale().t
// at the call site so EN/ES toggling reflects immediately. The leading star
// for "exact" is appended at the call site (kept here as a label prefix).
export function verdictLabelKey(v: Verdict): string {
  switch (v) {
    case "exact":   return "verdict.exact";
    case "hit":     return "verdict.hit";
    case "miss":    return "verdict.miss";
    case "skipped": return "verdict.empty";
  }
}

export function verdictStyles(v: Verdict): { label: string; bg: string; fg: string } {
  switch (v) {
    case "exact":   return { label: "★ EXACTO",   bg: "color-mix(in srgb, #D4AF37 28%, transparent)", fg: "#854D0E" };
    case "hit":     return { label: "ACERTASTE",  bg: "color-mix(in srgb, var(--accent-mint) 25%, transparent)", fg: "#059669" };
    case "miss":    return { label: "MAMASTE",    bg: "color-mix(in srgb, #FF3B82 18%, transparent)", fg: "#BE123C" };
    case "skipped": return { label: "NO LLENÓ",   bg: "var(--bg-tint)", fg: "var(--ink-muted)" };
  }
}
