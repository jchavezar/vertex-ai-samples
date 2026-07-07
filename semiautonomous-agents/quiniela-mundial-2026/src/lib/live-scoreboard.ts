"use client";

import { useMemo } from "react";
import { allGroupFixtures } from "@/data/groups";
import { normalizeAbbr, type EspnEvent } from "@/lib/espn";
import type { RealResults } from "@/lib/standings";
import { useScoreboard } from "@/lib/scoreboard-cache";

export type LivePhase = "pre" | "live" | "final";

export type LiveFixture = {
  fixtureId: string;
  phase: LivePhase;
  minute?: string;
  homeGoals?: number;
  awayGoals?: number;
  statusText?: string;
};

export type LiveScoreboard = {
  byId: Record<string, LiveFixture>;
  finals: RealResults;
  loading: boolean;
};

function phaseFor(state: string): LivePhase {
  if (state === "post") return "final";
  if (state === "in") return "live";
  return "pre";
}

export function useLiveScoreboard(): LiveScoreboard {
  const { data, loading } = useScoreboard();

  return useMemo(() => {
    if (!data?.events) return { byId: {}, finals: {}, loading: loading && !data };

    const fixtures = allGroupFixtures();
    const fxByPair = new Map<string, typeof fixtures[number]>();
    for (const fx of fixtures) {
      fxByPair.set(`${fx.home}-${fx.away}-${fx.date}`, fx);
      fxByPair.set(`${fx.away}-${fx.home}-${fx.date}`, fx);
    }

    const byId: Record<string, LiveFixture> = {};
    const finals: RealResults = {};
    const events: EspnEvent[] = data.events;
    for (const e of events) {
      const state = e.status.type.state;
      const c = e.competitions[0];
      const h = c.competitors.find((cp) => cp.homeAway === "home");
      const a = c.competitors.find((cp) => cp.homeAway === "away");
      if (!h || !a) continue;
      const hCode = normalizeAbbr(h.team.abbreviation);
      const aCode = normalizeAbbr(a.team.abbreviation);
      const cdmxDate = new Date(e.date).toLocaleDateString("en-CA", { timeZone: "America/Mexico_City" });
      const fx = fxByPair.get(`${hCode}-${aCode}-${cdmxDate}`) ?? fxByPair.get(`${hCode}-${aCode}-${e.date.slice(0, 10)}`);
      if (!fx) continue;
      const ourHomeIsEspnHome = fx.home === hCode;
      const hgRaw = Number(h.score);
      const agRaw = Number(a.score);
      const hg = Number.isFinite(hgRaw) ? hgRaw : undefined;
      const ag = Number.isFinite(agRaw) ? agRaw : undefined;
      const ourHome = hg !== undefined && ag !== undefined ? (ourHomeIsEspnHome ? hg : ag) : undefined;
      const ourAway = hg !== undefined && ag !== undefined ? (ourHomeIsEspnHome ? ag : hg) : undefined;

      const phase = phaseFor(state);
      byId[fx.id] = {
        fixtureId: fx.id,
        phase,
        minute: e.status.displayClock || undefined,
        homeGoals: ourHome,
        awayGoals: ourAway,
        statusText: e.status.type.shortDetail || e.status.type.detail,
      };
      if (phase === "final" && ourHome !== undefined && ourAway !== undefined) {
        finals[fx.id] = { homeGoals: ourHome, awayGoals: ourAway };
      }
    }
    return { byId, finals, loading: false };
  }, [data, loading]);
}
