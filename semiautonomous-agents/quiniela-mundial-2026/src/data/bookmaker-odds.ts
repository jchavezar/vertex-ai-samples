// Curated pre-Mundial 2026 bookmaker implied probabilities for the championship.
// Snapshot tomado de promedios de casas (Bet365, William Hill, Pinnacle, Caliente)
// en mayo 2026, despejando el overround (vig) y normalizando a sum = 1.
// Cifras en 0-1 (NO porcentajes). Sirve como ancla para "lo que dicen las casas".

export const BOOKMAKER_SNAPSHOT_DATE = "2026-05-25";

export const BOOKMAKER_CHAMPION_PROB: Record<string, number> = {
  // Favoritos
  ESP: 0.140,
  ARG: 0.125,
  FRA: 0.120,
  BRA: 0.105,
  ENG: 0.100,
  POR: 0.075,
  GER: 0.065,
  NED: 0.055,
  // Outsiders serios
  BEL: 0.030,
  CRO: 0.025,
  URU: 0.022,
  COL: 0.020,
  MAR: 0.018,
  // Anfitriones
  USA: 0.013,
  MEX: 0.012,
  CAN: 0.005,
  // Resto con chance no nula
  JPN: 0.010,
  NOR: 0.009,
  SUI: 0.008,
  SEN: 0.005,
  SWE: 0.005,
  ECU: 0.003,
  AUT: 0.003,
  CIV: 0.002,
  TUR: 0.002,
  KOR: 0.002,
  EGY: 0.002,
  AUS: 0.001,
  IRN: 0.001,
  PAR: 0.001,
  ALG: 0.001,
  // Resto debajo de 0.1% → se asigna piso simbólico
  KSA: 0.0005,
  TUN: 0.0005,
  GHA: 0.0005,
  PAN: 0.0005,
  QAT: 0.0005,
  BIH: 0.0005,
  SCO: 0.0005,
  CZE: 0.0005,
  RSA: 0.0003,
  COD: 0.0003,
  NZL: 0.0003,
  IRQ: 0.0003,
  JOR: 0.0003,
  UZB: 0.0003,
  CPV: 0.0002,
  CUW: 0.0002,
  HAI: 0.0002,
};

// Devuelve probabilidad implícita de campeón (0-1). Piso 0.0001 para que
// cualquier selección que no esté listada todavía se renderice.
export function bookmakerChampionProb(code: string): number {
  return BOOKMAKER_CHAMPION_PROB[code] ?? 0.0001;
}
