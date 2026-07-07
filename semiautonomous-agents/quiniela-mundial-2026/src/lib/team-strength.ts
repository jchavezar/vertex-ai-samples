// ELO ratings para las 48 selecciones del Mundial 2026.
// Snapshot manual basado en eloratings.net + FIFA ranking ~ mayo 2026,
// con ajustes para selecciones sin ELO histórico (debutantes / repechaje).
// Rango típico: 1500-2100. Más alto = más fuerte.

export const TEAM_ELO: Record<string, number> = {
  // Top tier (favoritos al título)
  "ARG": 2120, "FRA": 2090, "ESP": 2075, "BRA": 2050, "ENG": 2040,
  "POR": 2025, "NED": 2010, "GER": 2005, "BEL": 1985, "ITA": 1980,
  // Strong (candidatos a cuartos/semis)
  "CRO": 1960, "URU": 1955, "COL": 1940, "MAR": 1935, "SUI": 1920,
  "DEN": 1915, "USA": 1900, "MEX": 1895, "SEN": 1885, "JPN": 1880,
  "AUT": 1875, "EGY": 1865, "KOR": 1855, "AUS": 1850, "ECU": 1840,
  "CIV": 1830, "POL": 1825, "PAR": 1820, "WAL": 1810, "SCO": 1805,
  // Mid (suelen pasar a octavos peleando)
  "TUN": 1790, "GHA": 1785, "TUR": 1780, "ALG": 1775, "NGA": 1770,
  "CZE": 1760, "BIH": 1755, "QAT": 1745, "RSA": 1740, "JOR": 1735,
  "CAN": 1730, "PAN": 1720, "UZB": 1710, "CRC": 1705, "IRN": 1700,
  // Lower (debutantes / sorpresas)
  "CPV": 1680, "CUW": 1670, "HAI": 1660, "JAM": 1655, "NZL": 1650,
  "SUR": 1640, "BOL": 1630,
};

export function eloOf(code: string): number {
  return TEAM_ELO[code] ?? 1700; // default conservador para códigos no mapeados
}

// Convierte una diferencia de ELO en probabilidad de victoria del equipo "home"
// usando la fórmula estándar: P = 1 / (1 + 10^(-D/400))
// Añadimos un "home advantage" pequeño para anfitriones y un factor de empate.
function rawWinProb(eloDiff: number): number {
  return 1 / (1 + Math.pow(10, -eloDiff / 400));
}

const HOST_CODES = new Set(["MEX", "USA", "CAN"]);
function hostBoost(code: string, isHome: boolean): number {
  // +50 ELO si el equipo juega en su país (proxy para venue exacto)
  return HOST_CODES.has(code) && isHome ? 50 : 0;
}

// Probabilidad 1X2 para un partido entre `home` y `away`.
// Devuelve [P(H), P(D), P(A)] que suma 1.
export function matchOdds(home: string, away: string, neutralVenue: boolean = true): {
  H: number; D: number; A: number;
} {
  const eHome = eloOf(home) + (neutralVenue ? 0 : hostBoost(home, true));
  const eAway = eloOf(away) + (neutralVenue ? 0 : hostBoost(away, false));
  const diff = eHome - eAway;
  // P(home win) sin empate
  const pHomeRaw = rawWinProb(diff);
  // Probabilidad de empate decae con la diferencia de fuerza.
  // Para |diff|=0 → ~28% empate. Para |diff|=400 → ~12%.
  const drawFactor = 0.28 * Math.exp(-Math.abs(diff) / 600);
  const remaining = 1 - drawFactor;
  return {
    H: pHomeRaw * remaining,
    D: drawFactor,
    A: (1 - pHomeRaw) * remaining,
  };
}

// Probabilidad de que `winner` venza a `opponent` en un partido knockout
// (sin empate — penales y prórroga colapsan al ganador esperado).
export function knockoutWinProb(winner: string, opponent: string): number {
  return rawWinProb(eloOf(winner) - eloOf(opponent));
}

// Probabilidad de avanzar de grupo (top 2 de 4).
// Aproximación: el rank esperado del equipo en un grupo de 4 se computa
// vía expected points contra cada rival; tomar los top 2 con monte-carlo cerrado.
// Para MVP usamos una heurística: P(top2) = softmax(ELO) → top-2 share.
export function groupAdvanceProb(team: string, groupTeams: string[]): number {
  const ratings = groupTeams.map(t => eloOf(t));
  // Convertir ELO a "fuerza" relativa con softmax (temperatura 200).
  const weights = ratings.map(r => Math.exp(r / 200));
  const total = weights.reduce((a, b) => a + b, 0);
  const teamW = Math.exp(eloOf(team) / 200);
  const share = teamW / total;
  // P(top2 de 4) ≈ 1 - (1 - share)^2 → no es exacto pero da una intuición decente.
  // Mejor: prob aproximada = share * 2 capped to 0.95.
  return Math.min(0.95, Math.max(0.05, share * 2));
}

// Probabilidad simplificada de llegar a cada ronda eliminatoria asumiendo
// avance pareado contra el ELO promedio de la siguiente ronda.
// (MVP — el bracket real requeriría simular toda la llave.)
export function probReachRound(
  team: string,
  round: "R32" | "R16" | "QF" | "SF" | "FINAL" | "CHAMP",
  groupTeams: string[],
): number {
  const pGroup = groupAdvanceProb(team, groupTeams);
  // ELO promedio aproximado de oponentes por ronda (mundial 2026):
  // R32 ~ 1820 (mezcla), R16 ~ 1870, QF ~ 1920, SF ~ 1970, FINAL ~ 2010
  const oppElo: Record<string, number> = {
    R32: 1820, R16: 1870, QF: 1920, SF: 1970, FINAL: 2010, CHAMP: 2010,
  };
  const ePerRound = (target: number) => rawWinProb(eloOf(team) - target);
  switch (round) {
    case "R32": return pGroup;
    case "R16": return pGroup * ePerRound(oppElo.R32);
    case "QF":  return pGroup * ePerRound(oppElo.R32) * ePerRound(oppElo.R16);
    case "SF":  return pGroup * ePerRound(oppElo.R32) * ePerRound(oppElo.R16) * ePerRound(oppElo.QF);
    case "FINAL":
    case "CHAMP":
      const base = pGroup * ePerRound(oppElo.R32) * ePerRound(oppElo.R16) * ePerRound(oppElo.QF) * ePerRound(oppElo.SF);
      return round === "FINAL" ? base : base * ePerRound(oppElo.FINAL);
  }
}
