// FIFA Ultimate Team-style "cromo" for each charal.
// Stats SON pura performance — no recompensan velocidad de llenado.
// Cada stat mapea a un comportamiento real medible en la quiniela.

import type { PlayerPredictions, MatchResult, GroupPrediction } from "@/lib/predictions";
import { computePlayerScoreDetail, actualPick } from "@/lib/predictions";
import { allGroupFixtures } from "@/data/groups";
import { PLAYERS } from "@/data/players";

export type CromoTier = "debutante" | "bronce" | "plata" | "oro" | "oroRaro" | "especial";

export type CromoPosition = "DEL" | "MED" | "DEF" | "POR";

export type CromoStats = {
  pac: number; // RIT — racha de aciertos consecutivos
  sho: number; // TIR — % marcadores exactos
  pas: number; // PAS — % aciertos 1X2
  dri: number; // REG — diversidad de picks
  def: number; // OLF — % aciertos cuando elegiste minoría
  phy: number; // PRE — precisión (cercanía marcador real)
};

export type Cromo = {
  playerId: string;
  rating: number;
  tier: CromoTier;
  position: CromoPosition;
  stats: CromoStats;
  championPick?: string;
  statRows: Array<{ key: keyof CromoStats; label: string; value: number; meaning: string }>;
};

const clamp = (n: number, lo = 40, hi = 99) => Math.max(lo, Math.min(hi, Math.round(n)));

function entropy01(parts: number[]): number {
  const sum = parts.reduce((a, b) => a + b, 0);
  if (sum === 0) return 0;
  const probs = parts.map(p => p / sum).filter(p => p > 0);
  const h = -probs.reduce((acc, p) => acc + p * Math.log2(p), 0);
  const max = Math.log2(parts.filter(p => p > 0).length || 1);
  if (max === 0) return 0;
  return h / max;
}

// Compute max consecutive 1X2 hits ordered by fixture date.
function streakHits(p: PlayerPredictions, actuals: Record<string, MatchResult>): number {
  const fixtures = allGroupFixtures()
    .filter(fx => actuals[fx.id] && p.group[fx.id]?.pick)
    .sort((a, b) => +new Date(a.date) - +new Date(b.date));
  let best = 0, run = 0;
  for (const fx of fixtures) {
    const pred = p.group[fx.id];
    const act = actuals[fx.id];
    if (pred && act && pred.pick === actualPick(act)) {
      run += 1;
      if (run > best) best = run;
    } else {
      run = 0;
    }
  }
  return best;
}

// "Olfato" = de los aciertos que tuviste, qué % fueron contra la corriente
// (tu pick fue minoría entre todos los jugadores que ya pickearon ese partido).
function minorityHitRate(
  p: PlayerPredictions,
  actuals: Record<string, MatchResult>,
  allPicks: PlayerPredictions[],
): { rate: number; correct: number } {
  let correct = 0, minority = 0;
  for (const [fxId, pred] of Object.entries(p.group)) {
    const act = actuals[fxId];
    if (!pred || !act || pred.pick !== actualPick(act)) continue;
    correct += 1;
    let same = 0, total = 0;
    for (const other of allPicks) {
      if (other.playerId === p.playerId) continue;
      const op = other.group[fxId]?.pick;
      if (!op) continue;
      total += 1;
      if (op === pred.pick) same += 1;
    }
    if (total >= 2 && same / total < 0.5) minority += 1;
  }
  if (correct === 0) return { rate: 0, correct: 0 };
  return { rate: minority / correct, correct };
}

// "Precisión" = cercanía promedio del marcador propuesto al real.
// distance = |hP - hR| + |aP - aR|. 0 = perfecto.
function scorePrecision(p: PlayerPredictions, actuals: Record<string, MatchResult>): { avg: number; samples: number } {
  let totalDist = 0, samples = 0;
  for (const [fxId, pred] of Object.entries(p.group)) {
    const act = actuals[fxId];
    if (!pred || !act) continue;
    if (!Number.isFinite(pred.homeGoals) || !Number.isFinite(pred.awayGoals)) continue;
    const dist = Math.abs((pred.homeGoals as number) - act.homeGoals)
               + Math.abs((pred.awayGoals as number) - act.awayGoals);
    totalDist += Math.min(dist, 8); // cap distance to avoid one disaster dominating
    samples += 1;
  }
  if (samples === 0) return { avg: 0, samples: 0 };
  return { avg: totalDist / samples, samples };
}

function todayKeyET(): string {
  return new Intl.DateTimeFormat("en-CA", {
    timeZone: "America/New_York",
    year: "numeric", month: "2-digit", day: "2-digit",
  }).format(new Date());
}

export function computeCromo(
  p: PlayerPredictions,
  actuals: Record<string, MatchResult>,
  allPicks: PlayerPredictions[] = [],
  dateStr: string = todayKeyET(),
): Cromo {
  const detail = computePlayerScoreDetail(p, actuals);
  const totalActuals = Object.keys(actuals).length;
  const totalAciertos = detail.signHits + detail.exactHits;

  // RIT — racha máxima de 1X2 acertados (ordenado por fecha). Cap a 12.
  const streak = streakHits(p, actuals);
  const pac = totalActuals === 0
    ? 50 // pre-torneo: baseline neutral
    : clamp(45 + Math.min(streak, 12) * 4.5);

  // TIR — % marcadores exactos sobre lo jugado.
  const sho = totalActuals === 0
    ? 50
    : clamp(45 + (detail.exactHits / totalActuals) * 100 * 0.55);

  // PAS — % aciertos 1X2 sobre lo jugado.
  const pas = totalActuals === 0
    ? 50
    : clamp(45 + (totalAciertos / totalActuals) * 100 * 0.55);

  // REG — diversidad de picks (entropía sobre H/D/A). No requiere actuals.
  let countsH = 0, countsD = 0, countsA = 0;
  for (const pred of Object.values(p.group)) {
    if (!pred?.pick) continue;
    if (pred.pick === "H") countsH++;
    else if (pred.pick === "D") countsD++;
    else if (pred.pick === "A") countsA++;
  }
  const totalPicked = countsH + countsD + countsA;
  const div = entropy01([countsH, countsD, countsA]);
  const dri = totalPicked === 0 ? 50 : clamp(45 + div * 50);

  // OLF (DEF slot) — % de aciertos que fueron minoría entre los compas.
  const { rate: minRate, correct: correctCount } = minorityHitRate(p, actuals, allPicks);
  const def = correctCount === 0
    ? 50
    : clamp(45 + minRate * 100 * 0.55);

  // PRE (PHY slot) — precisión de marcador. 0 distancia = 100, distancia 6+ = ~45.
  const { avg: distAvg, samples: distSamples } = scorePrecision(p, actuals);
  const phy = distSamples === 0
    ? 50
    : clamp(98 - distAvg * 9);

  // Overall — pondera lo que más vale en la quiniela:
  // PAS (1X2) y TIR (exactos) pesan más; OLF y PRE pesan medio; RIT y REG pesan menos.
  const rating = clamp(
    pac * 0.10 +
    sho * 0.24 +
    pas * 0.26 +
    dri * 0.08 +
    def * 0.16 +
    phy * 0.16
  );

  // Posición decorativa, derivada del perfil de stats.
  const position: CromoPosition = (() => {
    if (sho >= pas && sho >= def) return "DEL";
    if (pas >= def && pas >= sho) return "MED";
    if (def >= pas && def >= sho) return "DEF";
    return "POR";
  })();

  // Tier rotates DAILY per charal via a 6-day cycle with oroRaro every 3rd
  // day and especial as the rarest. Decoupled from rating because with 10
  // friends in the same skill band a rating-derived tier would stick all of
  // them on the same MAYAB forever. Rating still shows numerically on the
  // card. A charal who never filled ANY pick gets the "debutante" tier — a
  // visually inert "waiting room" card so it doesn't pretend to be a competitor.
  const hasAnyPick = totalPicked > 0 || !!p.champion || !!p.runnerUp;
  const tier: CromoTier = !hasAnyPick ? "debutante" : dailyTierFor(p.playerId, dateStr);

  return {
    playerId: p.playerId,
    rating: hasAnyPick ? rating : 0,
    tier,
    position,
    stats: { pac, sho, pas, dri, def, phy },
    championPick: p.champion,
    statRows: [
      { key: "pac", label: "RIT", value: pac, meaning: "Racha de aciertos al hilo" },
      { key: "sho", label: "TIR", value: sho, meaning: "% marcadores exactos" },
      { key: "pas", label: "PAS", value: pas, meaning: "% aciertos 1X2" },
      { key: "dri", label: "REG", value: dri, meaning: "Diversidad de picks H/E/V" },
      { key: "def", label: "OLF", value: def, meaning: "Olfato: aciertos contra la corriente" },
      { key: "phy", label: "PRE", value: phy, meaning: "Precisión del marcador" },
    ],
  };
}

// Umbrales generosos por diseño: la quiniela existe para divertirse y queremos
// que la gente vea su cromo subir. Con baseline neutro de 50 todos arrancan en
// PLATA; un jugador competente alcanza ORO sin sufrir; los dominantes — con
// rachas, exactos y olfato — llegan a ORO RARO y ESPECIAL como debe ser.
export function tierForRating(r: number): CromoTier {
  if (r >= 82) return "especial";
  if (r >= 73) return "oroRaro";
  if (r >= 63) return "oro";
  if (r >= 50) return "plata";
  return "bronce";
}

// Daily tier assignment with "premium day every other day".
//
// Día sí, día no: today (anchor 2026-06-15) is a premium day → exactly 1 ORO
// RARO and 1 ESPECIAL handed out (rotating through the 10 humans). Tomorrow
// is a non-premium day → everyone gets BRONCE / PLATA / ORO. Day after,
// premium again. So premium frames hit every 2nd day and the wait builds
// anticipation.
//
// Rotation order pinned so jesus is at index 0 → he gets ORO RARO on the
// anchor day (today). Each premium player only sees ORO RARO once every 20
// days (10 players × every other day).
const HUMAN_ROTATION_IDS = [
  "jesus", "jochabe", "charal", "aldo", "tilapia",
  "mvictor", "xavi", "akyno", "darin", "emir",
] as const;
const NON_PREMIUM_CYCLE: CromoTier[] = ["bronce", "plata", "oro"];
// Anchor day for the "every other day" rotation. Day N counts as premium iff
// (N - ANCHOR_DAY_INDEX) % 2 === 0. ANCHOR is 2026-06-15 (jesus = ORO RARO).
const ANCHOR_DATE_STR = "2026-06-15";
function phaseFor(playerId: string): number {
  // djb2 hash (xor) — deterministic, no Date.now / Math.random dependency.
  let h = 5381;
  for (let i = 0; i < playerId.length; i++) h = ((h * 33) ^ playerId.charCodeAt(i)) >>> 0;
  return h % NON_PREMIUM_CYCLE.length;
}
function dayIndex(dateStr: string): number {
  // YYYY-MM-DD → days since epoch in UTC. Stable, no DST surprises.
  const [y, m, d] = dateStr.split("-").map(n => parseInt(n, 10));
  return Math.floor(Date.UTC(y, m - 1, d) / 86400000);
}
export function dailyTierFor(playerId: string, dateStr: string): CromoTier {
  const day = dayIndex(dateStr);
  const anchor = dayIndex(ANCHOR_DATE_STR);
  const offset = day - anchor;
  const isPremiumDay = ((offset % 2) + 2) % 2 === 0;
  if (isPremiumDay) {
    // Pair index increments every premium day (0, 1, 2, ...) so each premium
    // assignment rotates one slot forward through HUMAN_ROTATION_IDS.
    const pairIdx = Math.floor(offset / 2);
    const n = HUMAN_ROTATION_IDS.length;
    const oroRaroPlayer  = HUMAN_ROTATION_IDS[((pairIdx) % n + n) % n];
    const especialPlayer = HUMAN_ROTATION_IDS[((pairIdx + Math.floor(n / 2)) % n + n) % n];
    if (playerId === oroRaroPlayer)  return "oroRaro";
    if (playerId === especialPlayer) return "especial";
  }
  return NON_PREMIUM_CYCLE[((day + phaseFor(playerId)) % NON_PREMIUM_CYCLE.length + NON_PREMIUM_CYCLE.length) % NON_PREMIUM_CYCLE.length];
}

export type TierTheme = "tianguis" | "charro" | "mayab" | "obsidiana" | "quetzal";

export function tierMeta(t: CromoTier): {
  label: string;
  gradient: string;
  textColor: string;
  accent: string;
  shine: boolean;
  theme: TierTheme;
  glow?: string;        // halo RGBA color for premium tiers
  iridescent?: boolean; // animated hue cycle on shine + accents
  premium?: boolean;    // unlocks extra serigrafía layers in CromoCard
} {
  switch (t) {
    case "especial":
      // Edición QUETZAL — jade selvático, magenta cardenal, dorado solar y
      // obsidiana morada. Diseño tipo "super card holográfica": cuando esto
      // sale del sobre, debería sentirse como un Charizard 1st edition.
      return {
        label: "ESPECIAL · QUETZAL",
        gradient: "linear-gradient(155deg, #00695C 0%, #00897B 14%, #1DE9B6 28%, #FFD54F 48%, #C2185B 68%, #4A148C 90%, #1A0033 100%)",
        textColor: "#FFECB3",
        accent: "#FFD54F",
        shine: true,
        theme: "quetzal",
        glow: "#1DE9B6",
        iridescent: true,
        premium: true,
      };
    case "oroRaro":
      // Edición TENOCHTITLAN — oro líquido sobre obsidiana volcánica, con
      // brillo de foil ámbar. Metálico, denso, ceremonial.
      return {
        label: "ORO RARO · TENOCHTITLAN",
        gradient: "linear-gradient(155deg, #FFF59D 0%, #FFC107 18%, #FF8F00 38%, #6D4C0E 62%, #1A0E00 84%, #3D2200 100%)",
        textColor: "#FFE0A8",
        accent: "#FFB300",
        shine: true,
        theme: "obsidiana",
        glow: "#FFB300",
        premium: true,
      };
    case "oro":
      return {
        label: "ORO · MAYAB",
        gradient: "linear-gradient(155deg, #FFD54F 0%, #E65100 65%, #1B5E20 100%)",
        textColor: "#1A0D00",
        accent: "#FFECB3",
        shine: false,
        theme: "mayab",
      };
    case "plata":
      return {
        label: "PLATA · CHARRO",
        gradient: "linear-gradient(155deg, #ECEFF1 0%, #B0BEC5 55%, #006847 100%)",
        textColor: "#102027",
        accent: "#FAFAFA",
        shine: false,
        theme: "charro",
      };
    case "bronce":
      return {
        label: "BRONCE · TIANGUIS",
        gradient: "linear-gradient(155deg, #D2691E 0%, #8B4513 55%, #B71C1C 100%)",
        textColor: "#1A0500",
        accent: "#FFCC80",
        shine: false,
        theme: "tianguis",
      };
    case "debutante":
    default:
      // Empty cromo for charales who haven't filled any picks. Neutral steel
      // palette, no glow — visibly a "waiting room" card vs the active ones.
      return {
        label: "DEBUTANTE · APARTADO",
        gradient: "linear-gradient(155deg, #455A64 0%, #263238 60%, #1B262C 100%)",
        textColor: "#CFD8DC",
        accent: "#90A4AE",
        shine: false,
        theme: "tianguis",
      };
  }
}

const TIER_STORAGE_KEY = "q26:cromo-tier";

export function readStoredTier(playerId: string): CromoTier | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = localStorage.getItem(`${TIER_STORAGE_KEY}:${playerId}`);
    if (!raw) return null;
    const t = raw as CromoTier;
    if (t === "debutante" || t === "bronce" || t === "plata" || t === "oro" || t === "oroRaro" || t === "especial") return t;
  } catch {}
  return null;
}

export function writeStoredTier(playerId: string, tier: CromoTier): void {
  if (typeof window === "undefined") return;
  // Never demote in storage — the pack-opening animation fires on tier-up
  // diffs, and the underlying cromo rating can oscillate between two adjacent
  // tiers across scoreboard polls (live actuals → computeCromo re-evaluates).
  // If we wrote each new tier verbatim, an oroRaro → oro → oroRaro flap would
  // fire confetti every poll. Lock the high-water mark in localStorage.
  try {
    const prev = localStorage.getItem(`${TIER_STORAGE_KEY}:${playerId}`) as CromoTier | null;
    if (prev && TIER_ORDER.indexOf(tier) <= TIER_ORDER.indexOf(prev)) return;
    localStorage.setItem(`${TIER_STORAGE_KEY}:${playerId}`, tier);
  } catch {}
}

const TIER_ORDER: CromoTier[] = ["debutante", "bronce", "plata", "oro", "oroRaro", "especial"];

export function isTierPromotion(prev: CromoTier | null, next: CromoTier): boolean {
  if (!prev) return false;
  return TIER_ORDER.indexOf(next) > TIER_ORDER.indexOf(prev);
}

// Re-export so consumers can avoid an extra import line.
export type { GroupPrediction };
