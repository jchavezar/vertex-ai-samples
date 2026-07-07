// Bracket scenario engine — drives the "live, intelligent bracket" experience
// at the top of /bracket. Three jobs:
//   1) Tell us, per R32 slot, whether the team there is CONFIRMADO (source
//      group(s) finished) or PROYECTADO (current standings, can still flip).
//   2) Simulate every remaining group fixture's possible outcomes and
//      surface the ones that would actually reshape the bracket — so AVA
//      can preview "if KOR wins and MEX loses, MEX falls to 2°".
//   3) Generate AVA-voiced Spanish narration (template-based, no LLM call).
//
// Everything is pure + deterministic so the parent component can call this
// inside a useMemo and re-render fast.
import { GROUP_LETTERS, allGroupFixtures, groupFixtures, type GroupLetter } from "@/data/groups";
import {
  R32_TEMPLATE,
  computeAllStandings,
  computeR32Pairings,
  computeThirdPlaceRanking,
  groupConfirmed,
  type RealResults,
} from "@/lib/standings";
import { blank, type PlayerPredictions } from "@/lib/predictions";

const EMPTY_PICKS: PlayerPredictions = blank("__scenarios__");

export type SlotStatus = "confirmed" | "projected";

export type SlotState = {
  /** R32 template token, e.g. "1A", "2B", "3rd1". */
  token: string;
  /** Resolved team code from current standings + real results, null if empty. */
  team: string | null;
  /** confirmed iff source group(s) finished all 6 matches. */
  status: SlotStatus;
  /** Letter of the source group for "1X" / "2X" tokens. Undefined for 3rdN. */
  groupLetter?: string;
};

export type ScenarioOutcome = {
  fixtureId: string;        // e.g. "A-M5"
  homeCode: string;
  awayCode: string;
  /** Which outcome this scenario simulates. */
  pick: "H" | "D" | "A";
  homeGoals: number;
  awayGoals: number;
  /** Slots that change vs the current projection if this scenario plays out. */
  changedSlots: Array<{
    token: string;          // slot affected (e.g. "1A")
    before: string | null;  // team currently in this slot
    after: string;          // team in this slot if scenario plays out
  }>;
};

export type SlotDelta = {
  token: string;
  before: string | null;
  after: string | null;
  groupLetter?: string;
};

// ---------------------------------------------------------------------------
//                       SLOT STATE (confirmed vs projected)
// ---------------------------------------------------------------------------

/** Letter(s) feeding a given R32 token. 3rdN draws from every group. */
function tokenSourceGroups(token: string): GroupLetter[] {
  if (token.startsWith("3rd")) return [...GROUP_LETTERS] as GroupLetter[];
  return [token.slice(1) as GroupLetter];
}

function tokenGroupLetter(token: string): string | undefined {
  if (token.startsWith("3rd")) return undefined;
  return token.slice(1);
}

/**
 * Returns the live state of every R32 template slot (24 group-derived slots
 * + 8 third-place slots = 32 entries in template order).
 *
 * A "1X" / "2X" slot is CONFIRMADO iff its single feeder group finished all
 * 6 matches in real life. A "3rdN" slot is CONFIRMADO only once every group
 * has closed — until then the third-place ranking can still reshuffle.
 */
export function bracketSlotStates(real: RealResults): SlotState[] {
  const pairings = computeR32Pairings(EMPTY_PICKS, real);
  const out: SlotState[] = [];
  for (let i = 0; i < R32_TEMPLATE.length; i++) {
    const [a, b] = R32_TEMPLATE[i];
    const [teamA, teamB] = pairings[i].teams;
    for (const [token, team] of [[a, teamA], [b, teamB]] as const) {
      const sources = tokenSourceGroups(token);
      const status: SlotStatus = sources.every(l => groupConfirmed(l, real))
        ? "confirmed"
        : "projected";
      out.push({
        token,
        team: team || null,
        status,
        groupLetter: tokenGroupLetter(token),
      });
    }
  }
  return out;
}

// ---------------------------------------------------------------------------
//                          WHAT-IF SCENARIOS
// ---------------------------------------------------------------------------

/** Build a baseline "team → token" map from the current real results. */
function slotsByToken(states: SlotState[]): Map<string, string | null> {
  const m = new Map<string, string | null>();
  for (const s of states) m.set(s.token, s.team);
  return m;
}

type Outcome = { pick: "H" | "D" | "A"; homeGoals: number; awayGoals: number };

const BASIC_OUTCOMES: Outcome[] = [
  { pick: "H", homeGoals: 1, awayGoals: 0 },
  { pick: "D", homeGoals: 0, awayGoals: 0 },
  { pick: "A", homeGoals: 0, awayGoals: 1 },
];

const BLOWOUT_OUTCOMES: Outcome[] = [
  { pick: "H", homeGoals: 3, awayGoals: 0 },
  { pick: "A", homeGoals: 0, awayGoals: 3 },
];

/**
 * Detects a "tight" group where multiple teams sit within 3 pts of each other —
 * goal-diff blowouts are interesting only in those.
 */
function isTightGroup(letter: GroupLetter, real: RealResults): boolean {
  const tbl = computeAllStandings(EMPTY_PICKS, real)[letter] ?? [];
  if (tbl.length < 2) return false;
  // Compare top 3 pts spread: if max - min(top3) <= 3, it's tight.
  const tops = tbl.slice(0, 3).map(s => s.pts);
  const spread = (tops[0] ?? 0) - (tops[tops.length - 1] ?? 0);
  return spread <= 3;
}

/**
 * Returns the bracket-reshaping outcomes for every still-pending group fixture.
 * For each fixture we try its three basic outcomes (1-0 / 0-0 / 0-1) and, in
 * tight groups, two blowout outcomes (3-0 / 0-3) so we surface GD swings too.
 * Only outcomes that actually move at least one slot are returned. The list
 * is capped at 10, sorted by (slots moved desc, fixture kickoff asc).
 */
export function whatIfScenarios(real: RealResults): ScenarioOutcome[] {
  const baseline = bracketSlotStates(real);
  const baseMap = slotsByToken(baseline);

  const pending = allGroupFixtures().filter(fx => !real[fx.id]);
  const candidates: ScenarioOutcome[] = [];

  for (const fx of pending) {
    const tight = isTightGroup(fx.group, real);
    const outcomes = tight ? [...BASIC_OUTCOMES, ...BLOWOUT_OUTCOMES] : BASIC_OUTCOMES;
    for (const o of outcomes) {
      const synthetic: RealResults = {
        ...real,
        [fx.id]: { homeGoals: o.homeGoals, awayGoals: o.awayGoals },
      };
      const projected = bracketSlotStates(synthetic);
      const changedSlots: ScenarioOutcome["changedSlots"] = [];
      // Track which tokens we already counted to avoid duplicates (each token
      // appears twice in template iteration — once per side of a pair).
      const seen = new Set<string>();
      for (const slot of projected) {
        if (seen.has(slot.token)) continue;
        seen.add(slot.token);
        const before = baseMap.get(slot.token) ?? null;
        if ((before ?? "") !== (slot.team ?? "") && slot.team) {
          changedSlots.push({ token: slot.token, before, after: slot.team });
        }
      }
      if (changedSlots.length > 0) {
        candidates.push({
          fixtureId: fx.id,
          homeCode: fx.home,
          awayCode: fx.away,
          pick: o.pick,
          homeGoals: o.homeGoals,
          awayGoals: o.awayGoals,
          changedSlots,
        });
      }
    }
  }

  // Sort: more impactful first (more slots moved), then by fixture imminence.
  // Imminence proxied by `date + kickoffLocal` lex order — works because both
  // fields are zero-padded.
  const fxOrder = new Map<string, string>();
  for (const fx of allGroupFixtures()) {
    fxOrder.set(fx.id, `${fx.date}T${fx.kickoffLocal}`);
  }
  candidates.sort((a, b) => {
    if (b.changedSlots.length !== a.changedSlots.length) {
      return b.changedSlots.length - a.changedSlots.length;
    }
    const ta = fxOrder.get(a.fixtureId) ?? "";
    const tb = fxOrder.get(b.fixtureId) ?? "";
    return ta.localeCompare(tb);
  });

  return candidates.slice(0, 10);
}

// ---------------------------------------------------------------------------
//                          DIFF (snapshot comparison)
// ---------------------------------------------------------------------------

/**
 * Compares a stored previous snapshot (token → team) against a freshly
 * computed slot-state list, returning every slot whose occupant changed.
 */
export function diffSnapshots(
  prev: Array<{ token: string; team: string | null }>,
  next: SlotState[],
): SlotDelta[] {
  const prevMap = new Map<string, string | null>();
  for (const p of prev) prevMap.set(p.token, p.team);
  const seen = new Set<string>();
  const out: SlotDelta[] = [];
  for (const slot of next) {
    if (seen.has(slot.token)) continue;
    seen.add(slot.token);
    if (!prevMap.has(slot.token)) continue; // first-render snapshot
    const before = prevMap.get(slot.token) ?? null;
    const after = slot.team;
    if ((before ?? "") !== (after ?? "")) {
      out.push({
        token: slot.token,
        before,
        after,
        groupLetter: slot.groupLetter,
      });
    }
  }
  return out;
}

// ---------------------------------------------------------------------------
//                          AVA NARRATION (template-only)
// ---------------------------------------------------------------------------

/**
 * Spanish label for an R32 template token, lower-case (drops into sentence
 * fragments — e.g. "el 1° del Grupo A", "el mejor 3° #5").
 */
function slotPhrase(token: string): string {
  if (token.startsWith("3rd")) {
    const n = parseInt(token.slice(3), 10);
    return `mejor 3° #${n}`;
  }
  const pos = token[0];
  const letter = token.slice(1);
  if (pos === "1") return `1° del Grupo ${letter}`;
  if (pos === "2") return `2° del Grupo ${letter}`;
  return token;
}

/** Token like "1A" → "1A". Token like "3rd5" → "3°-#5". Used in clipped chips. */
function slotTokenLabel(token: string): string {
  if (token.startsWith("3rd")) return `3°-#${token.slice(3)}`;
  return token;
}

function nowHHMM(): string {
  const fmt = new Intl.DateTimeFormat("es-MX", {
    timeZone: "America/Mexico_City",
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  });
  return fmt.format(new Date());
}

/**
 * One sentence per slot change. AVA's voice: analítica, fría, en español
 * neutro. No emojis, no exclamaciones, sin disculpas.
 */
export function avaNarrateDeltas(deltas: SlotDelta[]): string[] {
  if (deltas.length === 0) return [];
  const stamp = nowHHMM();
  return deltas.map(d => {
    const slot = slotPhrase(d.token);
    if (d.before && d.after) {
      return `${d.before} cedió el ${slot} a ${d.after}. La diferencia de goles inclinó la simulación a las ${stamp}.`;
    }
    if (!d.before && d.after) {
      return `${d.after} ocupa el ${slot}. Recalibré la proyección a las ${stamp}.`;
    }
    if (d.before && !d.after) {
      return `${d.before} salió del ${slot}. Quedó vacante en mi proyección a las ${stamp}.`;
    }
    return `Movimiento en el ${slot} a las ${stamp}.`;
  });
}

/**
 * One paragraph per scenario. Lists the moving slot(s) and the resulting
 * promote/demote chain — e.g. "MEX cae a 2° del Grupo A".
 */
export function avaNarrateScenario(s: ScenarioOutcome): string {
  const scoreText =
    s.pick === "D"
      ? `empata ${s.homeGoals}-${s.awayGoals} con`
      : s.pick === "H"
        ? `le gana ${s.homeGoals}-${s.awayGoals} a`
        : `pierde ${s.homeGoals}-${s.awayGoals} con`;

  // For each changed slot, also figure out where the team that lost the
  // slot landed (if anywhere in the changed set) — surfaces the
  // "promotion + demotion" chain in one line.
  const lines: string[] = [];
  const afterByBefore = new Map<string, string>();
  for (const c of s.changedSlots) {
    if (c.before) afterByBefore.set(c.before, c.token);
  }
  for (const c of s.changedSlots) {
    const slot = slotPhrase(c.token);
    if (c.before) {
      // Did `before` land in another changed slot? (i.e. demoted to 2° instead of 1°)
      let demoteText = "";
      // Look for the slot where `c.before` now sits (= a different changed slot
      // whose `after` equals c.before).
      const newSlotForBefore = s.changedSlots.find(x => x.after === c.before);
      if (newSlotForBefore) demoteText = ` y ${c.before} cae al ${slotPhrase(newSlotForBefore.token)}`;
      lines.push(`el ${slot} cambia: ${c.after} entra${demoteText}`);
    } else {
      lines.push(`el ${slot} se llena con ${c.after}`);
    }
  }

  return `Si ${s.homeCode} ${scoreText} ${s.awayCode} en ${s.fixtureId}, ${lines.join("; ")}.`;
}

/**
 * State explainer for the header — explains where each slot stands.
 * `confirmedGroups` is the list of letters whose 6 matches are all played.
 */
export function avaNarrateState(states: SlotState[], confirmedGroups: string[]): string {
  // Top/runner-up tokens come from confirmed group letters; 3rdN tokens are
  // CONFIRMADO only once every group has closed.
  const groupSlotsConfirmed = states.filter(
    s => !s.token.startsWith("3rd") && s.status === "confirmed",
  ).length;
  const groupSlotsProjected = states.filter(
    s => !s.token.startsWith("3rd") && s.status === "projected",
  ).length;
  const thirdsConfirmed = states.filter(
    s => s.token.startsWith("3rd") && s.status === "confirmed",
  ).length;
  const n = confirmedGroups.length;
  const m = 12 - n;
  return (
    `Los criterios para clasificar como tercero son: puntos → diferencia de goles → goles a favor → fair play. ` +
    `Actualmente ${n} grupos están confirmados, ${m} en proyección. ` +
    `${groupSlotsConfirmed} slots de líder/sublíder fijos · ${groupSlotsProjected} aún oscilando · ${thirdsConfirmed}/8 terceros sellados.`
  );
}

// ---------------------------------------------------------------------------
//                              EXTRA HELPERS
// ---------------------------------------------------------------------------

/**
 * Returns the list of group letters whose all six fixtures have a real result.
 * Convenience wrapper that the card uses for the header counter.
 */
export function confirmedGroupLetters(real: RealResults): string[] {
  return GROUP_LETTERS.filter(l => groupConfirmed(l, real));
}

/** Public re-export so the card can build the "token → state" lookup quickly. */
export function slotStateMap(real: RealResults): Map<string, SlotState> {
  const states = bracketSlotStates(real);
  const m = new Map<string, SlotState>();
  for (const s of states) {
    // Same token appears twice (one per side per pairing); keep the first.
    if (!m.has(s.token)) m.set(s.token, s);
  }
  return m;
}

// Re-export for tests that want to peek inside without re-deriving baseline.
export const __internal = {
  slotPhrase,
  slotTokenLabel,
  isTightGroup,
  computeThirdPlaceRanking,
  groupFixtures,
};
