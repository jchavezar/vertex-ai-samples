"use client";

// Client-side hooks for reading the latest fixture + bracket probabilities.
// Both endpoints are cached on the server (Firestore `current` doc) so the
// network round-trip is cheap. We hold the result in module-level memo so
// every component mount in the same session shares the same fetch.

import { useEffect, useState, useMemo } from "react";
import type { FixtureProbsEntry, BracketTeamProbs } from "@/lib/probability-snapshots";
import { matchProbability } from "@/data/team-strength";
import type { HDA } from "@/components/ProbabilityBar";

type FixtureProbsCache = {
  byFixture: Record<string, FixtureProbsEntry>;
  updatedAt: number;
};

let _fixtureCache: FixtureProbsCache | null = null;
let _fixturePromise: Promise<FixtureProbsCache> | null = null;
const FRESH_MS = 5 * 60 * 1000;

async function fetchFixtureProbs(): Promise<FixtureProbsCache> {
  const r = await fetch("/api/probabilities", { cache: "no-store" });
  const j = await r.json();
  if (!j?.ok) throw new Error(j?.error || "probabilities_failed");
  return {
    byFixture: j.fixtures as Record<string, FixtureProbsEntry>,
    updatedAt: j.updatedAt ?? Date.now(),
  };
}

export function useFixtureProbs(): { byFixture: Record<string, FixtureProbsEntry>; loading: boolean } {
  const [state, setState] = useState<FixtureProbsCache | null>(_fixtureCache);
  const [loading, setLoading] = useState<boolean>(!_fixtureCache);

  useEffect(() => {
    const fresh = _fixtureCache && Date.now() - _fixtureCache.updatedAt < FRESH_MS;
    if (fresh) return;
    if (!_fixturePromise) {
      _fixturePromise = fetchFixtureProbs()
        .then(c => { _fixtureCache = c; return c; })
        .finally(() => { _fixturePromise = null; });
    }
    setLoading(true);
    _fixturePromise.then(c => { setState(c); setLoading(false); }).catch(() => setLoading(false));
  }, []);

  return { byFixture: state?.byFixture ?? {}, loading };
}

type BracketProbsCache = {
  teams: Record<string, BracketTeamProbs>;
  updatedAt: number;
};

let _bracketCache: BracketProbsCache | null = null;
let _bracketPromise: Promise<BracketProbsCache> | null = null;

async function fetchBracketProbs(): Promise<BracketProbsCache> {
  const r = await fetch("/api/probabilities/bracket", { cache: "no-store" });
  const j = await r.json();
  if (!j?.ok) throw new Error(j?.error || "bracket_probs_failed");
  return {
    teams: j.teams as Record<string, BracketTeamProbs>,
    updatedAt: j.updatedAt ?? Date.now(),
  };
}

export function useBracketProbs(): { teams: Record<string, BracketTeamProbs>; loading: boolean } {
  const [state, setState] = useState<BracketProbsCache | null>(_bracketCache);
  const [loading, setLoading] = useState<boolean>(!_bracketCache);

  useEffect(() => {
    const fresh = _bracketCache && Date.now() - _bracketCache.updatedAt < FRESH_MS;
    if (fresh) return;
    if (!_bracketPromise) {
      _bracketPromise = fetchBracketProbs()
        .then(c => { _bracketCache = c; return c; })
        .finally(() => { _bracketPromise = null; });
    }
    setLoading(true);
    _bracketPromise.then(c => { setState(c); setLoading(false); }).catch(() => setLoading(false));
  }, []);

  return { teams: state?.teams ?? {}, loading };
}

// Hook for KO match probability: no draw possible, pure H vs A from ELO.
// Returns null when either team is unknown ("???").
export function useKOProbs(homeCode: string, awayCode: string): HDA | null {
  return useMemo(() => {
    if (!homeCode || !awayCode || homeCode === "???" || awayCode === "???") return null;
    try {
      const o = matchProbability(homeCode, awayCode);
      // In KO there's no draw — redistribute D proportionally between H and A
      const total = o.H + o.A;
      if (total <= 0) return null;
      return { H: o.H / total, D: 0, A: o.A / total };
    } catch {
      return null;
    }
  }, [homeCode, awayCode]);
}
