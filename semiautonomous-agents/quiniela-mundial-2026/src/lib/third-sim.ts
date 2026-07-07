import { groupFixtures, GROUP_LETTERS, type GroupLetter } from "@/data/groups";
import { computeAllStandings, type RealResults } from "@/lib/standings";
import { ANNEXE_C_MATRIX, THIRD_SLOT_ANCHORS, type ThirdSlotAnchor } from "@/data/annexe-c-thirds-matrix";
import { blank } from "@/lib/predictions";

export type ThirdSlotProb = { team: string; group: string; pct: number };

const EMPTY = blank("__sim__");
const N_SIMS = 3_000;

function sampleScore(outcome: "H" | "D" | "A"): { homeGoals: number; awayGoals: number } {
  const r = Math.random();
  if (outcome === "H") {
    if (r < 0.35) return { homeGoals: 1, awayGoals: 0 };
    if (r < 0.65) return { homeGoals: 2, awayGoals: 0 };
    if (r < 0.80) return { homeGoals: 2, awayGoals: 1 };
    if (r < 0.90) return { homeGoals: 3, awayGoals: 1 };
    return { homeGoals: 3, awayGoals: 0 };
  }
  if (outcome === "D") {
    if (r < 0.40) return { homeGoals: 1, awayGoals: 1 };
    if (r < 0.65) return { homeGoals: 0, awayGoals: 0 };
    return { homeGoals: 2, awayGoals: 2 };
  }
  if (r < 0.35) return { homeGoals: 0, awayGoals: 1 };
  if (r < 0.65) return { homeGoals: 0, awayGoals: 2 };
  if (r < 0.80) return { homeGoals: 1, awayGoals: 2 };
  if (r < 0.90) return { homeGoals: 0, awayGoals: 3 };
  return { homeGoals: 1, awayGoals: 3 };
}

function runSim(
  real: RealResults,
  teamToGroup: Map<string, GroupLetter>,
): Record<ThirdSlotAnchor, string> | null {
  const ext: RealResults = { ...real };

  for (const letter of GROUP_LETTERS) {
    for (const fx of groupFixtures(letter)) {
      if (!ext[fx.id]) {
        const r = Math.random();
        const outcome: "H" | "D" | "A" = r < 1 / 3 ? "H" : r < 2 / 3 ? "D" : "A";
        ext[fx.id] = sampleScore(outcome);
      }
    }
  }

  const all = computeAllStandings(EMPTY, ext);

  const thirds = GROUP_LETTERS.map(l => {
    const s = all[l]?.[2];
    return s?.team ? { group: l as GroupLetter, team: s.team, pts: s.pts, gd: s.gd, gf: s.gf } : null;
  }).filter((x): x is { group: GroupLetter; team: string; pts: number; gd: number; gf: number } => x !== null);

  if (thirds.length < 8) return null;

  thirds.sort((a, b) => b.pts - a.pts || b.gd - a.gd || b.gf - a.gf);
  const top8 = thirds.slice(0, 8);
  const key = top8.map(x => x.group).sort().join("");
  const row = ANNEXE_C_MATRIX[key];
  if (!row) return null;

  const result = {} as Record<ThirdSlotAnchor, string>;
  for (let i = 0; i < THIRD_SLOT_ANCHORS.length; i++) {
    const srcGroup = row[i] as GroupLetter;
    const info = thirds.find(x => x.group === srcGroup);
    result[THIRD_SLOT_ANCHORS[i]] = info?.team ?? "";
  }
  return result;
}

export function simulateThirdSlotProbabilities(
  real: RealResults,
): Record<ThirdSlotAnchor, ThirdSlotProb[]> {
  const teamToGroup = new Map<string, GroupLetter>();
  const snapshot = computeAllStandings(EMPTY, real);
  for (const l of GROUP_LETTERS) {
    for (const s of snapshot[l] ?? []) {
      if (s.team) teamToGroup.set(s.team, l as GroupLetter);
    }
  }

  const counts: Record<string, Record<string, number>> = {};
  for (const a of THIRD_SLOT_ANCHORS) counts[a] = {};
  let total = 0;

  for (let i = 0; i < N_SIMS; i++) {
    const sim = runSim(real, teamToGroup);
    if (!sim) continue;
    total++;
    for (const anchor of THIRD_SLOT_ANCHORS) {
      const team = sim[anchor];
      if (team) counts[anchor][team] = (counts[anchor][team] ?? 0) + 1;
    }
  }

  const result = {} as Record<ThirdSlotAnchor, ThirdSlotProb[]>;
  for (const anchor of THIRD_SLOT_ANCHORS) {
    result[anchor] = Object.entries(counts[anchor])
      .map(([team, c]) => ({
        team,
        group: teamToGroup.get(team) ?? "",
        pct: total > 0 ? c / total : 0,
      }))
      .sort((a, b) => b.pct - a.pct);
  }
  return result;
}
