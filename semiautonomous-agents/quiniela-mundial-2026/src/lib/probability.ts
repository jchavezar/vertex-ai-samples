// Probability engine: dado un PlayerPredictions, computa expected points,
// probabilidad de acertar campeón/subcampeón, y una "fuerza relativa" para
// estimar si el jugador tiene un buen ticket.

import type { PlayerPredictions } from "@/lib/predictions";
import { allGroupFixtures, GROUPS } from "@/data/groups";
import { SCORING } from "@/data/tournament";
import { championBonusPoints, runnerUpBonusPoints } from "@/lib/predictions";
import { matchOdds, knockoutWinProb, probReachRound, eloOf } from "@/lib/team-strength";

export type PlayerOdds = {
  expectedGroupPoints: number;   // sum over 72 fixtures
  expectedBracketPoints: number; // sum over bracket picks (estimación)
  expectedChampionBonus: number; // P(campeón) × bonus
  expectedRunnerUpBonus: number; // P(subcampeón) × bonus
  expectedTotalPoints: number;
  championProb: number;          // 0-1
  runnerUpProb: number;          // 0-1
  // Rating estilo "qué tan bien armado está el ticket vs uno random"
  ticketStrength: number;        // 0-1 (1 = ticket óptimo según ELO)
  ready: boolean;                // true si está listo para mostrar
  missing: { groupPicks: number; champion: boolean; runnerUp: boolean };
};

const TOTAL_GROUP_FIXTURES = 72;

export function computePlayerOdds(p: PlayerPredictions): PlayerOdds {
  const fixtures = allGroupFixtures();
  const filledGroup = Object.values(p.group).filter(g => g?.pick).length;
  const missingGroup = TOTAL_GROUP_FIXTURES - filledGroup;
  const missingChamp = !p.champion;
  const missingRunner = !p.runnerUp;
  const ready = missingGroup === 0 && !missingChamp && !missingRunner;

  // === Expected points fase de grupos ===
  let expectedGroup = 0;
  let bestPossibleGroup = 0;
  for (const fx of fixtures) {
    const odds = matchOdds(fx.home, fx.away, false);
    const best = Math.max(odds.H, odds.D, odds.A);
    bestPossibleGroup += best * SCORING.pickWinner;
    const pred = p.group[fx.id];
    if (!pred?.pick) continue;
    const pPick = pred.pick === "H" ? odds.H : pred.pick === "D" ? odds.D : odds.A;
    expectedGroup += pPick * SCORING.pickWinner;
    // Bonus marcador exacto: aproximación grosera — 8% de los partidos con
    // marcador exacto correcto entre los que acertaron 1X2.
    if (Number.isFinite(pred.homeGoals) && Number.isFinite(pred.awayGoals)) {
      expectedGroup += pPick * 0.08 * SCORING.exactScoreBonus;
    }
  }

  // === Bracket (R32 + R16 + QF + SF + 3er + FINAL) ===
  // Para cada pick, multiplicamos la prob de que ese equipo realmente
  // gane su matchup contra el ELO promedio de oponentes en la ronda.
  // Es una heurística — el bracket real depende del seeding del usuario.
  let expectedBracket = 0;
  const ROUND_AVG_OPP_ELO: Record<string, number> = { R32: 1820, R16: 1870, QF: 1920, SF: 1970, THIRD: 1900, FINAL: 2010 };
  const ROUND_PTS = SCORING.knockoutWinner;
  const considerRound = (codes: string[] | undefined, round: keyof typeof ROUND_PTS) => {
    if (!codes || codes.length === 0) return;
    const opp = ROUND_AVG_OPP_ELO[round] ?? 1850;
    for (const code of codes) {
      if (!code) continue;
      const winP = 1 / (1 + Math.pow(10, -(eloOf(code) - opp) / 400));
      expectedBracket += winP * ROUND_PTS[round];
    }
  };
  considerRound(p.bracket.R32, "R32");
  considerRound(p.bracket.R16, "R16");
  considerRound(p.bracket.QF, "QF");
  considerRound(p.bracket.SF, "SF");
  if (p.bracket.THIRD) considerRound([p.bracket.THIRD], "THIRD");
  if (p.bracket.FINAL) considerRound([p.bracket.FINAL], "FINAL");

  // === Campeón / Subcampeón ===
  let championProb = 0;
  let runnerUpProb = 0;
  const findGroup = (code: string): string[] => {
    for (const teams of Object.values(GROUPS)) {
      if (teams.includes(code)) return teams;
    }
    return [];
  };
  if (p.champion) {
    championProb = probReachRound(p.champion, "CHAMP", findGroup(p.champion));
  }
  if (p.runnerUp) {
    // Sub: llega a final y pierde con el campeón. Simplificamos: P(llega a final) × ~50% (perder).
    runnerUpProb = probReachRound(p.runnerUp, "FINAL", findGroup(p.runnerUp)) * 0.5;
  }
  const expectedChampionBonus = championProb * championBonusPoints(p.championLockedAt);
  const expectedRunnerUpBonus = runnerUpProb * runnerUpBonusPoints(p.runnerUpLockedAt);

  const expectedTotalPoints = expectedGroup + expectedBracket + expectedChampionBonus + expectedRunnerUpBonus;

  // === Ticket strength relativo al "ticket óptimo" según ELO ===
  // Ticket óptimo de grupos = elegir siempre el outcome más probable.
  const ticketStrength = bestPossibleGroup > 0
    ? Math.min(1, expectedGroup / bestPossibleGroup)
    : 0;

  return {
    expectedGroupPoints: Math.round(expectedGroup * 10) / 10,
    expectedBracketPoints: Math.round(expectedBracket * 10) / 10,
    expectedChampionBonus: Math.round(expectedChampionBonus * 10) / 10,
    expectedRunnerUpBonus: Math.round(expectedRunnerUpBonus * 10) / 10,
    expectedTotalPoints: Math.round(expectedTotalPoints * 10) / 10,
    championProb,
    runnerUpProb,
    ticketStrength,
    ready,
    missing: { groupPicks: missingGroup, champion: missingChamp, runnerUp: missingRunner },
  };
}

// Convierte una probabilidad 0-1 en un emoji / etiqueta para la UI.
export function probLabel(p: number): { pct: string; label: string; tone: "good" | "mid" | "bad" } {
  const pct = (p * 100).toFixed(p < 0.01 ? 2 : 1) + "%";
  if (p >= 0.15) return { pct, label: "candidato real", tone: "good" };
  if (p >= 0.05) return { pct, label: "tiene chance",   tone: "mid"  };
  return                 { pct, label: "tiro al aire",  tone: "bad"  };
}
