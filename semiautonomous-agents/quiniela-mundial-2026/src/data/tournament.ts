// Mundial FIFA 2026 - Datos del torneo (fechas, formato, premios)

export const TOURNAMENT = {
  name: "Copa Mundial de la FIFA 2026",
  hosts: ["México", "Estados Unidos", "Canadá"] as const,
  startDate: "2026-06-11T16:00:00-06:00",   // 11 jun, Azteca CDMX
  endDate:   "2026-07-19T15:00:00-04:00",   // 19 jul, MetLife NJ
  totalTeams: 48,
  totalMatches: 104,
  groupStageMatches: 72,
  knockoutMatches: 32,
  opener: {
    date: "2026-06-11",
    venue: "Estadio Azteca",
    city: "Ciudad de México",
    home: "MEX",
    away: "RSA",
  },
  final: {
    date: "2026-07-19",
    venue: "MetLife Stadium",
    city: "East Rutherford, NJ",
  },
  draw: {
    date: "2025-12-05",
    city: "Washington, D.C.",
  },
};

// Sistema de puntos de la quiniela
//
// Reglas (decisión 2026-06-10, actualizada 2026-06-28):
//   • Fase de grupos da puntos SOLO por 1X2.
//   • El marcador exacto se sigue capturando como dinámica decorativa
//     (sirve de desempate informativo y para mostrar "exactos" en UI),
//     pero NO suma puntos extra.
//   • Las rondas eliminatorias (R32 → Final) dan puntos por acertar el ganador
//     de cada partido. Los puntos aumentan conforme avanza el torneo.
//   • Bonus adicional por atinarle al CAMPEÓN del Mundial,
//     con un bonus que decae según qué tan tarde se fija (CHAMPION_BONUS_MULTIPLIER).
//   • Subcampeón ya no da puntos — se sigue mostrando como pick "de a foto",
//     pero el único bonus serio es el del campeón.
export const SCORING = {
  pickWinner:        3,   // Acertar 1X2 (Local / Empate / Visitante)
  exactScoreBonus:   0,   // Sin ponderación — el marcador es decorativo
  knockoutWinner:    {    // Mismo valor que fase de grupos — todas las fases cuentan igual
    R32:   3,
    R16:   3,
    QF:    3,
    SF:    3,
    THIRD: 3,
    FINAL: 3,
  },
  bonusChampion:     30,  // Bonus adicional por el campeón — decae por fase
  bonusRunnerUp:     0,   // Sin puntos (queda como pick decorativo)
  bonusTopScorer:    0,   // Reservado a futuro
};

// Fases del bracket
export const KNOCKOUT_ROUNDS = [
  { key: "R32",    label: "Dieciseisavos", matches: 16 },
  { key: "R16",    label: "Octavos",       matches: 8  },
  { key: "QF",     label: "Cuartos",       matches: 4  },
  { key: "SF",     label: "Semifinales",   matches: 2  },
  { key: "THIRD",  label: "3er lugar",     matches: 1  },
  { key: "FINAL",  label: "Final",         matches: 1  },
] as const;

// Ventanas de lock para el bonus de campeón/subcampeón.
// Si el usuario cambia su pick DESPUÉS de que comience la fase indicada,
// el bonus se multiplica por el factor correspondiente.
export type ChampionLockRound = "PRE" | "R32" | "R16" | "QF" | "SF" | "FINAL";

export const CHAMPION_PHASE_STARTS: Record<Exclude<ChampionLockRound, "PRE">, string> = {
  R32:   "2026-06-28T00:00:00-06:00",
  R16:   "2026-07-04T00:00:00-06:00",
  QF:    "2026-07-09T00:00:00-06:00",
  SF:    "2026-07-14T00:00:00-06:00",
  FINAL: "2026-07-19T00:00:00-04:00",
};

// Multiplicador aplicado al bonus según la fase en la que el jugador FIJÓ (o cambió) su pick.
export const CHAMPION_BONUS_MULTIPLIER: Record<ChampionLockRound, number> = {
  PRE:   1.00,   // 30 / 15
  R32:   0.80,   // 24 / 12
  R16:   0.60,   // 18 /  9
  QF:    0.40,   // 12 /  6
  SF:    0.20,   //  6 /  3
  FINAL: 0,      // Ya empezó la final, no cuenta
};

// Devuelve la fase actual del torneo en términos de "cuál es la ventana abierta para cambiar campeón".
export function currentChampionLockRound(now: Date = new Date()): ChampionLockRound {
  const ts = now.getTime();
  if (ts >= new Date(CHAMPION_PHASE_STARTS.FINAL).getTime()) return "FINAL";
  if (ts >= new Date(CHAMPION_PHASE_STARTS.SF).getTime())    return "SF";
  if (ts >= new Date(CHAMPION_PHASE_STARTS.QF).getTime())    return "QF";
  if (ts >= new Date(CHAMPION_PHASE_STARTS.R16).getTime())   return "R16";
  if (ts >= new Date(CHAMPION_PHASE_STARTS.R32).getTime())   return "R32";
  return "PRE";
}

export const CHAMPION_PHASE_LABEL: Record<ChampionLockRound, string> = {
  PRE:   "Pre-torneo",
  R32:   "Dieciseisavos",
  R16:   "Octavos",
  QF:    "Cuartos",
  SF:    "Semifinales",
  FINAL: "Final",
};
