/* Client-side amortization math (sistema francés / cuota fija) used to
 * power the slider's instant recompute after the agent's first turn.
 *
 * The agent (BuiltInCodeExecutor) does the canonical first computation and
 * cites the published tasa de interés. Subsequent slider changes recompute
 * locally — keeps interaction at 0ms latency without round-tripping. */

export interface AmortizationParams {
  /** Principal in CLP (e.g. 6_000_000). */
  monto: number;
  /** Annual nominal rate in % (e.g. 17.5 for 17.5% CMR). */
  tasaAnual: number;
  /** Term in months (e.g. 48). */
  plazoMeses: number;
  /** Optional monthly desgravamen as a fraction of balance (e.g. 0.0007). */
  seguroMensualPct?: number;
  /** Optional one-shot comisión de apertura in CLP. */
  comisionApertura?: number;
}

export interface AmortizationRow {
  mes: number;
  cuota: number;
  interes: number;
  capital: number;
  seguro: number;
  saldo: number;
}

export interface AmortizationResult {
  cuotaMensual: number;
  totalPagado: number;
  totalInteres: number;
  totalSeguro: number;
  cae: number;
  schedule: AmortizationRow[];
}

/** Standard French amortization. Returns the full schedule + summary. */
export function amortize(p: AmortizationParams): AmortizationResult {
  const { monto, tasaAnual, plazoMeses } = p;
  const seguroPct = p.seguroMensualPct ?? 0;
  const comision = p.comisionApertura ?? 0;
  const r = tasaAnual / 100 / 12;
  // Cuota base sin seguro (capital + interés). Seguro se suma aparte mes a mes.
  const cuotaBase =
    r === 0 ? monto / plazoMeses : (monto * r) / (1 - Math.pow(1 + r, -plazoMeses));

  let saldo = monto;
  let totalInteres = 0;
  let totalSeguro = 0;
  const schedule: AmortizationRow[] = [];
  for (let m = 1; m <= plazoMeses; m++) {
    const interes = saldo * r;
    const capital = cuotaBase - interes;
    const seguro = saldo * seguroPct;
    saldo = Math.max(0, saldo - capital);
    totalInteres += interes;
    totalSeguro += seguro;
    schedule.push({
      mes: m,
      cuota: cuotaBase + seguro,
      interes,
      capital,
      seguro,
      saldo,
    });
  }
  const totalPagado = cuotaBase * plazoMeses + totalSeguro + comision;
  // Approx CAE: equivalent annual rate that explains total cost vs principal
  // over the term. Newton-Raphson for IRR is overkill for the slider — the
  // first call from the agent has the canonical CAE; locally we approximate.
  const cae = approxCAE(monto, schedule.map((r) => r.cuota), comision);
  return {
    cuotaMensual: cuotaBase + (schedule[0]?.seguro ?? 0),
    totalPagado,
    totalInteres,
    totalSeguro,
    cae,
    schedule,
  };
}

/** Approx CAE: rough effective annual % so the slider has a number to display.
 *  Not regulator-grade — the agent's published tasa is the source of truth. */
function approxCAE(p: number, flows: number[], comision: number): number {
  if (p <= 0 || flows.length === 0) return 0;
  // Solve for monthly i such that p = comision + sum(flow_t / (1+i)^t)
  // bisection over [0, 0.1] monthly (~ 0% to ~125% annual).
  const principal = p - comision;
  let lo = 0;
  let hi = 0.1;
  for (let iter = 0; iter < 60; iter++) {
    const mid = (lo + hi) / 2;
    let pv = 0;
    for (let t = 0; t < flows.length; t++) pv += flows[t] / Math.pow(1 + mid, t + 1);
    if (pv > principal) lo = mid;
    else hi = mid;
  }
  const monthly = (lo + hi) / 2;
  return (Math.pow(1 + monthly, 12) - 1) * 100;
}

/** What it would cost at a competing bank — uses a higher rate as proxy.
 *  The real comparison comes from the agent's grounding (engine cita la tasa).
 *  Default 22% mirrors a typical retail bank consumer rate in Chile. */
export function compareBank(monto: number, plazoMeses: number, bankAnual = 22): {
  cuota: number;
  totalPagado: number;
  diff: number;
} {
  const r = bankAnual / 100 / 12;
  const cuota = (monto * r) / (1 - Math.pow(1 + r, -plazoMeses));
  const totalPagado = cuota * plazoMeses;
  return { cuota, totalPagado, diff: totalPagado };
}

/** Long-term savings projection: if the user invests the difference between
 *  CCLA's monthly payment and the bank's, what does it grow to in 10y? */
export function projectSavings(
  monthlyDiff: number,
  years = 10,
  annualReturn = 5,
): { year: number; value: number }[] {
  const r = annualReturn / 100 / 12;
  let balance = 0;
  const out: { year: number; value: number }[] = [{ year: 0, value: 0 }];
  for (let m = 1; m <= years * 12; m++) {
    balance = balance * (1 + r) + monthlyDiff;
    if (m % 12 === 0) out.push({ year: m / 12, value: balance });
  }
  return out;
}

export function formatCLP(n: number): string {
  return new Intl.NumberFormat('es-CL', {
    style: 'currency',
    currency: 'CLP',
    maximumFractionDigits: 0,
  }).format(Math.round(n));
}
