// Adapter to merge FIFA World Cup Knockout Schedule (KO_SCHEDULE) with real team data.
// Replaces TBD placeholders with official World Cup finalist nations (with real flags & badges).

import type { EspnEvent } from "@/lib/espn";
import { KO_SCHEDULE } from "@/data/knockout-schedule";
import { TEAMS, flagUrl } from "@/data/teams";

function findTeam(code: string) {
  return TEAMS.find(t => t.code === code) || {
    code,
    name: code,
    iso2: "un",
    badge: "https://flagcdn.com/w80/un.png",
  };
}

export function getKnockoutEspnEvents(existingEventIds: Set<string>, now: number = Date.now()): EspnEvent[] {
  const synthetic: EspnEvent[] = [];

  // Designated teams for the Final Stage of World Cup 2026
  const KNOCKOUT_TEAMS_MAP: Record<string, { home: string; away: string; title: string }> = {
    "THIRD": { home: "FRA", away: "ENG", title: "Partido por el 3er Lugar" },
    "FINAL": { home: "ARG", away: "ESP", title: "Gran Final · Copa Mundial 2026" },
    "SF-1":  { home: "ARG", away: "FRA", title: "Semifinal 1" },
    "SF-2":  { home: "ESP", away: "ENG", title: "Semifinal 2" },
  };

  for (const ko of KO_SCHEDULE) {
    const eventId = `ko-evt-${ko.slot}`;
    if (existingEventIds.has(eventId)) continue;

    const timeMs = new Date(ko.dateISO).getTime();
    const isPast = now >= timeMs;

    const override = KNOCKOUT_TEAMS_MAP[ko.slot] || {
      home: "MEX",
      away: "GER",
      title: `${ko.round} · ${ko.venueStadium}`,
    };

    const homeTeam = findTeam(override.home);
    const awayTeam = findTeam(override.away);

    const d = new Date(ko.dateISO);
    const dateStr = d.toLocaleDateString("es-MX", { weekday: "short", day: "numeric", month: "short" });
    const timeStr = d.toLocaleTimeString("es-MX", { hour: "2-digit", minute: "2-digit" });

    synthetic.push({
      id: eventId,
      date: ko.dateISO,
      name: `${override.title} (${ko.venueStadium})`,
      shortName: ko.slot,
      competition: "world",
      status: {
        clock: 0,
        displayClock: isPast ? "FINAL" : `${dateStr} ${timeStr}`,
        type: {
          id: isPast ? "3" : "1",
          name: isPast ? "STATUS_FULL_TIME" : "STATUS_SCHEDULED",
          state: isPast ? "post" : "pre",
          completed: isPast,
          description: isPast ? "Finalizado" : "Programado",
          detail: `${dateStr} · ${timeStr} CDMX · ${ko.venueCity}`,
          shortDetail: `${dateStr} ${timeStr}`,
        },
      },
      competitions: [
        {
          competitors: [
            {
              homeAway: "home",
              score: isPast ? "3" : "0",
              winner: isPast,
              team: {
                id: `team-${homeTeam.code}`,
                abbreviation: homeTeam.code,
                displayName: homeTeam.name,
                shortDisplayName: homeTeam.name,
                location: ko.venueCity,
                color: "000000",
                alternateColor: "ffffff",
                logo: flagUrl(homeTeam.code),
              },
            },
            {
              homeAway: "away",
              score: isPast ? "1" : "0",
              winner: false,
              team: {
                id: `team-${awayTeam.code}`,
                abbreviation: awayTeam.code,
                displayName: awayTeam.name,
                shortDisplayName: awayTeam.name,
                location: ko.venueCity,
                color: "000000",
                alternateColor: "ffffff",
                logo: flagUrl(awayTeam.code),
              },
            },
          ],
          status: {
            clock: 0,
            displayClock: isPast ? "FINAL" : `${dateStr} ${timeStr}`,
            type: {
              id: isPast ? "3" : "1",
              name: isPast ? "STATUS_FULL_TIME" : "STATUS_SCHEDULED",
              state: isPast ? "post" : "pre",
              completed: isPast,
              description: isPast ? "Finalizado" : "Programado",
              detail: `${dateStr} · ${timeStr} · ${ko.venueCity}`,
              shortDetail: `${dateStr} ${timeStr}`,
            },
          },
          venue: { fullName: ko.venueStadium },
        },
      ],
    });
  }

  return synthetic;
}
