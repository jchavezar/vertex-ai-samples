// Dynamic Tournament Phase Detection & Contextual CTA Utility
// FIFA World Cup 2026 Schedule:
// - Pre-tournament: < June 11, 2026 16:00 CDMX
// - Group Stage: June 11, 2026 - June 27, 2026
// - Knockouts Stage: June 28, 2026 - July 17, 2026
// - Final Stage: July 18, 2026 - July 19, 2026
// - Post-Tournament: > July 19, 2026 23:59

import { TOURNAMENT } from "@/data/tournament";

export type TournamentPhase = "PRE" | "GROUP_STAGE" | "KNOCKOUTS" | "FINAL_STAGE" | "ENDED";

export type PhaseMeta = {
  phase: TournamentPhase;
  label: string;
  sublabel: string;
  primaryCtaText: string;
  primaryCtaHref: string;
  isGroupPredictionsOpen: boolean;
  isKnockoutActive: boolean;
};

export function getTournamentPhase(now: Date = new Date()): PhaseMeta {
  const ts = now.getTime();
  const startMs = new Date(TOURNAMENT.startDate).getTime();
  const groupEndMs = new Date("2026-06-27T23:59:59-06:00").getTime();
  const finalStartMs = new Date("2026-07-18T00:00:00-04:00").getTime();
  const endMs = new Date(TOURNAMENT.endDate).getTime() + (6 * 3600 * 1000); // end of final day

  if (ts < startMs) {
    return {
      phase: "PRE",
      label: "Pre-torneo",
      sublabel: "Faltan días para el partido inaugural en el Estadio Azteca.",
      primaryCtaText: "Llenar mi quiniela",
      primaryCtaHref: "/quiniela",
      isGroupPredictionsOpen: true,
      isKnockoutActive: false,
    };
  }

  if (ts >= startMs && ts <= groupEndMs) {
    return {
      phase: "GROUP_STAGE",
      label: "Fase de Grupos",
      sublabel: "Partidos de la fase de grupos en juego.",
      primaryCtaText: "Llenar quiniela de hoy",
      primaryCtaHref: "/quiniela",
      isGroupPredictionsOpen: true,
      isKnockoutActive: false,
    };
  }

  if (ts > groupEndMs && ts < finalStartMs) {
    return {
      phase: "KNOCKOUTS",
      label: "Fase Eliminatoria",
      sublabel: "Fase de grupos concluida. Rondas eliminatorias en juego.",
      primaryCtaText: "Ver Bracket de Eliminatorias",
      primaryCtaHref: "/bracket",
      isGroupPredictionsOpen: false,
      isKnockoutActive: true,
    };
  }

  if (ts >= finalStartMs && ts <= endMs) {
    return {
      phase: "FINAL_STAGE",
      label: "La Gran Final",
      sublabel: "¡Se define el Campeón del Mundo 2026 y de la Quiniela!",
      primaryCtaText: "Ver Bracket de la Final",
      primaryCtaHref: "/bracket",
      isGroupPredictionsOpen: false,
      isKnockoutActive: true,
    };
  }

  return {
    phase: "ENDED",
    label: "Torneo Concluido",
    sublabel: "Copa Mundial 2026 finalizada. Revisa a los ganadores.",
    primaryCtaText: "Ver Ranking Final",
    primaryCtaHref: "/leaderboard",
    isGroupPredictionsOpen: false,
    isKnockoutActive: false,
  };
}
