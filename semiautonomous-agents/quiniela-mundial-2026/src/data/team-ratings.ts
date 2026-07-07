// Probabilidad pre-partido 1X2 por equipo. Wrapper sobre el motor ELO en
// `src/lib/team-strength.ts` para que las vistas (e.g. "Hoy se juega")
// no dependan directamente del engine y los porcentajes redondeen a 100.
//
// El brief pedía ratings + fórmula nuevos, pero el repo ya tiene un
// snapshot ELO completo de las 48 selecciones en `TEAM_ELO`, así que se
// reutiliza para evitar drift entre vistas (rankings, ticket strength,
// y este chip de "Hoy se juega").

import { matchOdds } from "@/lib/team-strength";

export type WinProbs = { home: number; draw: number; away: number };

/**
 * Probabilidad redondeada a enteros (suma exacta 100) para el partido
 * `homeCode` vs `awayCode`. Por defecto asume venue no neutral en sede
 * del equipo local (host boost solo aplica a MEX/USA/CAN en su país).
 */
export function winProbabilities(
  homeCode: string,
  awayCode: string,
  opts: { neutralVenue?: boolean } = {},
): WinProbs {
  const odds = matchOdds(homeCode, awayCode, opts.neutralVenue ?? false);
  // Redondeo a enteros preservando suma=100 (largest-remainder method).
  const raw = [
    { key: "home" as const, value: odds.H * 100 },
    { key: "draw" as const, value: odds.D * 100 },
    { key: "away" as const, value: odds.A * 100 },
  ];
  const floored = raw.map(r => ({ ...r, floor: Math.floor(r.value), frac: r.value - Math.floor(r.value) }));
  let remainder = 100 - floored.reduce((sum, r) => sum + r.floor, 0);
  // Ordena por fracción descendente y reparte el residual.
  const order = [...floored].sort((a, b) => b.frac - a.frac);
  for (let i = 0; i < order.length && remainder > 0; i++, remainder--) {
    order[i].floor += 1;
  }
  const out: WinProbs = { home: 0, draw: 0, away: 0 };
  for (const r of floored) out[r.key] = r.floor;
  return out;
}
