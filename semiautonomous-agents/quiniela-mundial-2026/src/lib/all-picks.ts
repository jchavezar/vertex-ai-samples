"use client";

import { useCallback, useEffect, useState } from "react";
import { loadAllPredictionsFromServer, type Pick1X2, type PlayerPredictions } from "@/lib/predictions";
import { PLAYERS, type Player } from "@/data/players";
import { loadOverrides, PROFILE_UPDATED_EVENT } from "@/lib/profile-overrides";

export type PlayerLite = {
  id: string;
  name: string;
  emoji: string;
  accent: string;
  photoDataUrl?: string;
};

export type FixturePicksIndex = Record<string, {
  H: PlayerLite[];
  D: PlayerLite[];
  A: PlayerLite[];
}>;

function mergedLite(p: Player, overrides: Record<string, { name?: string; emoji?: string; photoDataUrl?: string }>): PlayerLite {
  const o = overrides[p.id] ?? {};
  return {
    id: p.id,
    name: o.name || p.name,
    emoji: o.emoji || p.emoji,
    accent: p.accent,
    photoDataUrl: o.photoDataUrl,
  };
}

function indexPicks(all: PlayerPredictions[]): FixturePicksIndex {
  const overrides = loadOverrides();
  const idx: FixturePicksIndex = {};
  const byId = new Map<string, Player>();
  PLAYERS.forEach((p) => byId.set(p.id, p));
  for (const pp of all) {
    const meta = byId.get(pp.playerId);
    if (!meta) continue;
    const lite = mergedLite(meta, overrides);
    for (const [fixtureId, pred] of Object.entries(pp.group)) {
      if (!pred?.pick) continue;
      if (!idx[fixtureId]) idx[fixtureId] = { H: [], D: [], A: [] };
      idx[fixtureId][pred.pick as Pick1X2].push(lite);
    }
  }
  return idx;
}

export function useAllPicksByFixture(): {
  byFixture: FixturePicksIndex;
  loading: boolean;
  refresh: () => void;
} {
  const [byFixture, setByFixture] = useState<FixturePicksIndex>({});
  const [loading, setLoading] = useState(true);

  const reload = useCallback(async () => {
    try {
      const all = await loadAllPredictionsFromServer();
      setByFixture(indexPicks(all));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      const all = await loadAllPredictionsFromServer();
      if (!cancelled) {
        setByFixture(indexPicks(all));
        setLoading(false);
      }
    })();
    const onUpd = () => { reload(); };
    if (typeof window !== "undefined") {
      window.addEventListener("q26:predictions-updated", onUpd as EventListener);
      window.addEventListener(PROFILE_UPDATED_EVENT, onUpd as EventListener);
    }
    return () => {
      cancelled = true;
      if (typeof window !== "undefined") {
        window.removeEventListener("q26:predictions-updated", onUpd as EventListener);
        window.removeEventListener(PROFILE_UPDATED_EVENT, onUpd as EventListener);
      }
    };
  }, [reload]);

  return { byFixture, loading, refresh: reload };
}
