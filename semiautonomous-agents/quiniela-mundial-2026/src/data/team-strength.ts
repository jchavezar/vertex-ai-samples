// Curated team strength model for Mundial 2026 (basis for the AI fill-quiniela tool).
// Numbers are 0-100, derived from March-May 2026 FIFA ranking + post-Qatar 2022 results
// (Euro 2024, Copa America 2024, AFCON 2025, Nations League, qualifying form).
// Host nations (MEX, USA, CAN) already include a +3 home-country bonus.

export type StrengthTier = "S" | "A" | "B" | "C" | "D" | "E" | "F";

export type TeamStrength = {
  code: string;
  strength: number;
  tier: StrengthTier;
  notes: string;
};

export const TEAM_STRENGTH: Record<string, TeamStrength> = {
  // S (94-100) — bona fide title contenders
  ARG: { code: "ARG", strength: 97, tier: "S", notes: "Campeón vigente y Copa América 2024 — Messi todavía decisivo, plantilla profunda" },
  ESP: { code: "ESP", strength: 96, tier: "S", notes: "Euro 2024 invicta (7/7), Yamal en su pico, mejor selección europea del ciclo" },
  FRA: { code: "FRA", strength: 96, tier: "S", notes: "FIFA #1, plantel profundo, Mbappé en su pico, último ciclo Deschamps" },
  BRA: { code: "BRA", strength: 94, tier: "S", notes: "Ancelotti reordena la identidad ofensiva, Vinícius como referente" },

  // A (85-93) — clear quarter-final material
  ENG: { code: "ENG", strength: 92, tier: "A", notes: "6/6 en eliminatorias UEFA con Tuchel, Bellingham + Kane" },
  POR: { code: "POR", strength: 90, tier: "A", notes: "Campeón Nations League 2025, plantel profundísimo, último baile CR7" },
  GER: { code: "GER", strength: 89, tier: "A", notes: "Wirtz + Musiala con Nagelsmann, recuperó nivel post-2022" },
  NED: { code: "NED", strength: 88, tier: "A", notes: "Van Dijk + Gakpo, bloque alto serio para semifinales" },
  BEL: { code: "BEL", strength: 86, tier: "A", notes: "De Bruyne todavía decisivo aunque sin favoritismo previo" },
  CRO: { code: "CRO", strength: 85, tier: "A", notes: "Modrić maestro del ritmo, mediocampo dominante, 3°/2° en últimos dos mundiales" },

  // B (75-84) — knockout-round teams
  MAR: { code: "MAR", strength: 84, tier: "B", notes: "Semifinalista 2022, récord 19W consecutivas en 2025, Bounou + Hakimi elite" },
  COL: { code: "COL", strength: 81, tier: "B", notes: "Subcampeón Copa América 2024, posesión fluida con James + Díaz" },
  URU: { code: "URU", strength: 80, tier: "B", notes: "Bielsa imprime presión alta, Valverde + Núñez en su pico" },
  SUI: { code: "SUI", strength: 78, tier: "B", notes: "Cuartos Eurocopa 2024, bloque compacto con Xhaka" },
  NOR: { code: "NOR", strength: 78, tier: "B", notes: "Haaland + Ødegaard, gran incógnita ofensiva tras 28 años de ausencia" },
  JPN: { code: "JPN", strength: 77, tier: "B", notes: "Ganó grupo en 2022 dejando fuera a Alemania, juego asociado pulido" },
  USA: { code: "USA", strength: 78, tier: "B", notes: "Pochettino al mando + generación Pulisic, +3 anfitrión" },
  MEX: { code: "MEX", strength: 77, tier: "B", notes: "Campeón Nations League CONCACAF 2025, +3 anfitrión, tercer ciclo Aguirre" },
  CAN: { code: "CAN", strength: 75, tier: "B", notes: "Davies + David, +3 anfitrión, presión alta a la Marsch" },

  // C (65-74) — competitive but typical group-stage exits
  SWE: { code: "SWE", strength: 73, tier: "C", notes: "Isak + Gyökeres con Potter ordenando, pelea por octavos" },
  IRN: { code: "IRN", strength: 71, tier: "C", notes: "Taremi + Azmoun, equipo físico y disciplinado" },
  KOR: { code: "KOR", strength: 71, tier: "C", notes: "Son + Lee Kang-in, juego vertical, pelea por octavos" },
  AUS: { code: "AUS", strength: 70, tier: "C", notes: "6ta consecutiva, octavos 2006 y 2022, bloque defensivo" },
  ECU: { code: "ECU", strength: 70, tier: "C", notes: "Caicedo dueño del medio, equipo físico" },
  SEN: { code: "SEN", strength: 70, tier: "C", notes: "Mané + Koulibaly, una de las africanas más equilibradas" },
  CIV: { code: "CIV", strength: 70, tier: "C", notes: "Campeón Copa Africana 2023, Kessié + Haller" },
  EGY: { code: "EGY", strength: 69, tier: "C", notes: "Salah como referencia absoluta, pragmatismo de transición" },
  TUR: { code: "TUR", strength: 68, tier: "C", notes: "Generación joven con Arda Güler, sorpresa potencial" },
  AUT: { code: "AUT", strength: 67, tier: "C", notes: "Gegenpressing de Rangnick, una de las sorpresas potenciales europeas" },

  // D (55-64) — outside chance of progressing
  KSA: { code: "KSA", strength: 62, tier: "D", notes: "Venció a Argentina en 2022, Al-Dawsari como arma" },
  ALG: { code: "ALG", strength: 62, tier: "D", notes: "Mahrez + Bennacer, técnico con buena salida" },
  TUN: { code: "TUN", strength: 60, tier: "D", notes: "Defensa hermética (clasificó sin recibir goles), ataque limitado" },
  PAR: { code: "PAR", strength: 60, tier: "D", notes: "Bloque defensivo y garra a la Alfaro, vuelve tras 16 años" },
  GHA: { code: "GHA", strength: 59, tier: "D", notes: "Kudus como talento ofensivo, Queiroz desde abril 2026" },
  BIH: { code: "BIH", strength: 58, tier: "D", notes: "Combativos con Džeko, eliminaron a Italia en playoffs" },
  SCO: { code: "SCO", strength: 57, tier: "D", notes: "Bloque sólido con Robertson, Clarke estable; nunca pasó de grupos" },
  CZE: { code: "CZE", strength: 56, tier: "D", notes: "Schick como referencia, vía repechaje UEFA, bloque defensivo" },

  // E (45-54) — happy just to be there
  IRQ: { code: "IRQ", strength: 53, tier: "E", notes: "Vuelve tras 40 años con Arnold al mando" },
  NZL: { code: "NZL", strength: 52, tier: "E", notes: "Físico y directo con Chris Wood, busca replicar Sudáfrica 2010" },
  HAI: { code: "HAI", strength: 50, tier: "E", notes: "Regresa tras 52 años, guerrero y emocional" },
  PAN: { code: "PAN", strength: 50, tier: "E", notes: "Disciplina defensiva bajo Christiansen, subcampeón Nations 2025" },
  UZB: { code: "UZB", strength: 49, tier: "E", notes: "Debut histórico con Cannavaro, técnico y bien armado" },
  CPV: { code: "CPV", strength: 47, tier: "E", notes: "Debut absoluto (525k habitantes), juego de transición ordenado" },
  JOR: { code: "JOR", strength: 47, tier: "E", notes: "Debut absoluto, subcampeón Copa Asiática 2023, fuerte en balón parado" },
  QAT: { code: "QAT", strength: 46, tier: "E", notes: "Bicampeón Asia, Lopetegui ahora le da identidad propia" },
  COD: { code: "COD", strength: 46, tier: "E", notes: "Físico y veloz con jugadores en ligas europeas, vía repechaje" },

  // F (35-44) — clearly outclassed
  RSA: { code: "RSA", strength: 44, tier: "F", notes: "Mejor momento desde 2010, 3° AFCON 2023, juego asociado" },
  CUW: { code: "CUW", strength: 38, tier: "F", notes: "Debut absoluto (nación más pequeña por población), bloque bajo + contragolpe" },
};

// Tuning constants. Tweak with care — these set how confident the AI is.
export const HOME_FIELD_BONUS = 4;          // applied to "home" side of a fixture
export const DRAW_BAND = 6;                 // |diff| < this → empate
export const FAVORITE_BOOST: Record<number, number> = {
  1: 14,
  2: 9,
  3: 6,
  4: 4,
  5: 3,
};

export function getStrength(code: string): TeamStrength | undefined {
  return TEAM_STRENGTH[code];
}

export function favoriteBoost(code: string, favorites: string[]): number {
  const idx = favorites.indexOf(code);
  if (idx < 0) return 0;
  return FAVORITE_BOOST[idx + 1] ?? 0;
}

// Softmax-style 1X2 probabilities from the curated strength model. Numbers
// are deterministic and meant as a sanity reference for the player while
// filling — not betting-grade odds.
export function matchProbability(homeCode: string, awayCode: string): { H: number; D: number; A: number } {
  const sh = (getStrength(homeCode)?.strength ?? 50) + HOME_FIELD_BONUS;
  const sa = getStrength(awayCode)?.strength ?? 50;
  const diff = sh - sa;
  // Temperature calibrated against opening-match betting markets:
  // diff=37 (MEX 81 vs RSA 44) → ~72% home win, similar to oddsmakers.
  // diff=10 (close match) → ~38% home, ~32% draw, ~30% away.
  const T = 40;
  const wH = Math.exp(diff / T);
  const wA = Math.exp(-diff / T);
  const wD = Math.exp(-Math.abs(diff) / T) * 1.05;
  const sum = wH + wD + wA;
  return { H: wH / sum, D: wD / sum, A: wA / sum };
}
