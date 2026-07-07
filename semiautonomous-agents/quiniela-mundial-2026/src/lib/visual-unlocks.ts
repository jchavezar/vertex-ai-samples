// Curated pool of ~30 cosmetic-only visual unlocks awarded by the daily
// envelope. Each entry has a stable id, a category, a Spanish display name,
// and the data the UI needs to render it. NONE of these affect pool points —
// they exist purely to feel good in the collection gallery.
//
// Categories:
//   frame      — CSS gradient border for the user's profile/cromo frame
//   background — radial/linear pattern for an avatar backdrop
//   sticker    — emoji combo the user can "stamp" on their cards
//
// 12 frames + 10 backgrounds + 8 stickers = 30 total.

export type VisualUnlockCategory = "frame" | "background" | "sticker";

export type VisualUnlock = {
  id: string;
  category: VisualUnlockCategory;
  name: string;          // Spanish display label
  rarity: "comun" | "raro" | "epico";
  // Render hints — interpreted by the unlocks gallery UI.
  gradient?: string;     // CSS background (for frames + backgrounds)
  border?: string;       // CSS border (for frames)
  emoji?: string;        // for stickers (1-4 chars)
  accent?: string;       // hex accent for the card chrome
};

export const VISUAL_UNLOCKS: VisualUnlock[] = [
  // ----- FRAMES (12) -----
  { id: "frame_oro_solar",     category: "frame", name: "Marco Oro Solar",     rarity: "raro",  border: "linear-gradient(135deg, #FFE07A, #D4AF37, #B8860B)", accent: "#D4AF37" },
  { id: "frame_jade_azteca",   category: "frame", name: "Marco Jade Azteca",   rarity: "raro",  border: "linear-gradient(135deg, #14B8A6, #0F766E, #134E4A)", accent: "#14B8A6" },
  { id: "frame_neon_cdmx",     category: "frame", name: "Marco Neón CDMX",     rarity: "epico", border: "linear-gradient(135deg, #EC4899, #A855F7, #06B6D4)", accent: "#EC4899" },
  { id: "frame_plata_lunar",   category: "frame", name: "Marco Plata Lunar",   rarity: "comun", border: "linear-gradient(135deg, #E5E7EB, #9CA3AF, #6B7280)", accent: "#9CA3AF" },
  { id: "frame_bronce_charal", category: "frame", name: "Marco Bronce Charal", rarity: "comun", border: "linear-gradient(135deg, #FBBF24, #B45309, #78350F)", accent: "#B45309" },
  { id: "frame_obsidiana",     category: "frame", name: "Marco Obsidiana",     rarity: "raro",  border: "linear-gradient(135deg, #1F2937, #0F172A, #020617)", accent: "#0F172A" },
  { id: "frame_tequila_sunset",category: "frame", name: "Marco Tequila Sunset",rarity: "raro",  border: "linear-gradient(135deg, #F97316, #EA580C, #DC2626)", accent: "#F97316" },
  { id: "frame_holografico",   category: "frame", name: "Marco Holográfico",   rarity: "epico", border: "linear-gradient(135deg, #A855F7, #06B6D4, #84CC16, #F472B6)", accent: "#A855F7" },
  { id: "frame_papel_picado",  category: "frame", name: "Marco Papel Picado",  rarity: "comun", border: "linear-gradient(135deg, #F472B6, #F97316, #84CC16, #06B6D4)", accent: "#F472B6" },
  { id: "frame_mariachi",      category: "frame", name: "Marco Mariachi",      rarity: "raro",  border: "linear-gradient(135deg, #1F2937, #C0C0C0, #1F2937)", accent: "#C0C0C0" },
  { id: "frame_vampiro",       category: "frame", name: "Marco Vampiro",       rarity: "epico", border: "linear-gradient(135deg, #7F1D1D, #000000, #7F1D1D)", accent: "#7F1D1D" },
  { id: "frame_quetzal",       category: "frame", name: "Marco Quetzal",       rarity: "epico", border: "linear-gradient(135deg, #16A34A, #14B8A6, #DC2626)", accent: "#16A34A" },

  // ----- BACKGROUNDS (10) -----
  { id: "bg_grana_cochinilla", category: "background", name: "Fondo Grana Cochinilla", rarity: "comun", gradient: "radial-gradient(circle at 30% 20%, #DC2626 0%, #7F1D1D 70%)", accent: "#DC2626" },
  { id: "bg_amate_papel",      category: "background", name: "Fondo Amate Papel",      rarity: "comun", gradient: "linear-gradient(180deg, #FEF3C7, #FCD34D, #B45309)", accent: "#B45309" },
  { id: "bg_aztec_glifo",      category: "background", name: "Fondo Glifo Azteca",     rarity: "raro",  gradient: "radial-gradient(circle at 50% 50%, #14B8A6 0%, #0F172A 80%)", accent: "#14B8A6" },
  { id: "bg_estadio_noche",    category: "background", name: "Fondo Estadio Noche",    rarity: "raro",  gradient: "radial-gradient(ellipse at center, #1E40AF 0%, #0F172A 70%)", accent: "#1E40AF" },
  { id: "bg_amanecer_pacifico",category: "background", name: "Fondo Amanecer Pacífico",rarity: "comun", gradient: "linear-gradient(180deg, #F97316, #EC4899, #7C3AED)", accent: "#EC4899" },
  { id: "bg_cancha_verde",     category: "background", name: "Fondo Cancha Verde",     rarity: "comun", gradient: "linear-gradient(180deg, #16A34A, #166534)", accent: "#16A34A" },
  { id: "bg_holograma_charal", category: "background", name: "Fondo Holograma Charal", rarity: "epico", gradient: "conic-gradient(from 180deg at 50% 50%, #A855F7, #06B6D4, #84CC16, #F472B6, #A855F7)", accent: "#A855F7" },
  { id: "bg_tinta_sumi",       category: "background", name: "Fondo Tinta Sumi",       rarity: "raro",  gradient: "radial-gradient(circle at 50% 50%, #1F2937 0%, #FFFFFF 100%)", accent: "#1F2937" },
  { id: "bg_alebrije",         category: "background", name: "Fondo Alebrije",         rarity: "raro",  gradient: "linear-gradient(135deg, #D946EF, #F472B6, #FBBF24, #14B8A6)", accent: "#D946EF" },
  { id: "bg_cyber_zocalo",     category: "background", name: "Fondo Cyber-Zócalo",     rarity: "epico", gradient: "radial-gradient(circle at 70% 30%, #06B6D4 0%, #EC4899 40%, #0F172A 90%)", accent: "#EC4899" },

  // ----- STICKERS (8) -----
  { id: "st_charal_oro",   category: "sticker", name: "Charal de Oro",      rarity: "raro",  emoji: "🐟✨", accent: "#FBBF24" },
  { id: "st_fuego_picante",category: "sticker", name: "Fuego Picante",      rarity: "comun", emoji: "🌶️🔥", accent: "#DC2626" },
  { id: "st_corona_real",  category: "sticker", name: "Corona Real",        rarity: "epico", emoji: "👑🏆", accent: "#D4AF37" },
  { id: "st_rayo_ava",     category: "sticker", name: "Rayo de AVA",        rarity: "raro",  emoji: "🤖⚡", accent: "#0EA5E9" },
  { id: "st_tequila_shot", category: "sticker", name: "Tequila Shot",       rarity: "comun", emoji: "🥃🍋", accent: "#84CC16" },
  { id: "st_lucha_libre",  category: "sticker", name: "Máscara Lucha",      rarity: "raro",  emoji: "🤼‍♂️🇲🇽", accent: "#EC4899" },
  { id: "st_pulpo_oraculo",category: "sticker", name: "Pulpo Oráculo",      rarity: "epico", emoji: "🐙🔮", accent: "#7C3AED" },
  { id: "st_cohete_lunar", category: "sticker", name: "Cohete Lunar",       rarity: "comun", emoji: "🚀🌙", accent: "#06B6D4" },
];

export function unlocksByCategory(cat: VisualUnlockCategory): VisualUnlock[] {
  return VISUAL_UNLOCKS.filter(u => u.category === cat);
}

export function findVisualUnlock(id: string): VisualUnlock | undefined {
  return VISUAL_UNLOCKS.find(u => u.id === id);
}

// Pick a random visual unlock the user does NOT already own. Falls back to
// any random unlock once the user has collected everything (still rewarding,
// just a duplicate). Returns null only if the pool is empty (impossible).
export function pickRandomVisualUnlock(ownedIds: Set<string>): VisualUnlock | null {
  if (VISUAL_UNLOCKS.length === 0) return null;
  const available = VISUAL_UNLOCKS.filter(u => !ownedIds.has(u.id));
  const pool = available.length > 0 ? available : VISUAL_UNLOCKS;
  return pool[Math.floor(Math.random() * pool.length)];
}
