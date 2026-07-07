// FIFA 2026 knockout schedule (R32 → R16 → QF → SF → 3rd place → Final).
//
// Times encoded in CDMX local (UTC-06:00, no DST) because the owner's audience
// is in Mexico. The Date constructor will normalize each ISO into the user's
// real local zone via toLocaleString — so a New York user still sees their own
// clock — we just anchor the wall-clock origin to CDMX.
//
// 31 knockout matches total: 16 R32 + 8 R16 + 4 QF + 2 SF + 1 3rd + 1 Final.
//
// Source: ESPN scoreboard API (verified June 2026). Slot numbers align 1:1 with
// R32_TEMPLATE indices in src/lib/standings.ts (slot "R32-N" = template[N-1]).

export type KORound = "R32" | "R16" | "QF" | "SF" | "THIRD" | "FINAL";

export type KOMatch = {
  slot: string;            // e.g. "R32-1", "R16-3", "QF-1", "SF-1", "THIRD", "FINAL"
  round: KORound;
  dateISO: string;         // "2026-06-28T12:00:00-06:00" (CDMX wall-clock)
  venueCity: string;       // matches src/data/venues.ts city field
  venueStadium: string;    // copied from FIFA schedule (fallback if VENUES lookup fails)
};

export const KO_SCHEDULE: KOMatch[] = [
  // -------- ROUND OF 32 (16 matches, 28 jun – 3 jul 2026) --------
  // Slot numbers match R32_TEMPLATE[i] where slot = R32-(i+1)
  { slot: "R32-1",  round: "R32", dateISO: "2026-06-28T13:00:00-06:00", venueCity: "Los Angeles",                venueStadium: "SoFi Stadium" },           // 2A vs 2B  — 3pm EDT
  { slot: "R32-2",  round: "R32", dateISO: "2026-06-29T14:30:00-06:00", venueCity: "Boston",                    venueStadium: "Gillette Stadium" },        // 1E vs 3rd1 — 4:30pm EDT
  { slot: "R32-3",  round: "R32", dateISO: "2026-06-29T19:00:00-06:00", venueCity: "Monterrey",                 venueStadium: "Estadio BBVA" },            // 1F vs 2C  — 7pm CDMX
  { slot: "R32-4",  round: "R32", dateISO: "2026-06-29T11:00:00-06:00", venueCity: "Houston",                   venueStadium: "NRG Stadium" },             // 1C vs 2F  — 1pm EDT
  { slot: "R32-5",  round: "R32", dateISO: "2026-06-30T15:00:00-06:00", venueCity: "Nueva York / Nueva Jersey", venueStadium: "MetLife Stadium" },         // 1I vs 3rd2 — 5pm EDT ★
  { slot: "R32-6",  round: "R32", dateISO: "2026-06-30T11:00:00-06:00", venueCity: "Dallas",                    venueStadium: "AT&T Stadium" },            // 2E vs 2I  — 1pm EDT
  { slot: "R32-7",  round: "R32", dateISO: "2026-06-30T19:00:00-06:00", venueCity: "Ciudad de México",          venueStadium: "Estadio Azteca" },          // 1A vs 3rd3 — 7pm CDMX
  { slot: "R32-8",  round: "R32", dateISO: "2026-07-01T10:00:00-06:00", venueCity: "Atlanta",                   venueStadium: "Mercedes-Benz Stadium" },   // 1L vs 3rd4 — noon EDT
  { slot: "R32-9",  round: "R32", dateISO: "2026-07-01T18:00:00-06:00", venueCity: "Bahía de San Francisco",    venueStadium: "Levi's Stadium" },          // 1D vs 3rd5 — 8pm EDT
  { slot: "R32-10", round: "R32", dateISO: "2026-07-01T14:00:00-06:00", venueCity: "Seattle",                   venueStadium: "Lumen Field" },             // 1G vs 3rd6 — 4pm EDT
  { slot: "R32-11", round: "R32", dateISO: "2026-07-02T17:00:00-06:00", venueCity: "Toronto",                   venueStadium: "BMO Field" },               // 2K vs 2L  — 7pm EDT
  { slot: "R32-12", round: "R32", dateISO: "2026-07-02T13:00:00-06:00", venueCity: "Los Angeles",               venueStadium: "SoFi Stadium" },            // 1H vs 2J  — 3pm EDT
  { slot: "R32-13", round: "R32", dateISO: "2026-07-02T21:00:00-06:00", venueCity: "Vancouver",                 venueStadium: "BC Place" },                // 1B vs 3rd7 — 11pm EDT
  { slot: "R32-14", round: "R32", dateISO: "2026-07-03T16:00:00-06:00", venueCity: "Miami",                     venueStadium: "Hard Rock Stadium" },       // 1J vs 2H  — 6pm EDT
  { slot: "R32-15", round: "R32", dateISO: "2026-07-03T19:30:00-06:00", venueCity: "Kansas City",               venueStadium: "Arrowhead Stadium" },       // 1K vs 3rd8 — 9:30pm EDT
  { slot: "R32-16", round: "R32", dateISO: "2026-07-03T12:00:00-06:00", venueCity: "Dallas",                    venueStadium: "AT&T Stadium" },            // 2D vs 2G  — 2pm EDT

  // -------- ROUND OF 16 (8 matches, 4 – 7 jul 2026) --------
  { slot: "R16-1", round: "R16", dateISO: "2026-07-04T11:00:00-06:00", venueCity: "Houston",                   venueStadium: "NRG Stadium" },             // 1pm EDT
  { slot: "R16-2", round: "R16", dateISO: "2026-07-04T15:00:00-06:00", venueCity: "Filadelfia",                venueStadium: "Lincoln Financial Field" }, // 5pm EDT
  { slot: "R16-3", round: "R16", dateISO: "2026-07-05T14:00:00-06:00", venueCity: "Nueva York / Nueva Jersey", venueStadium: "MetLife Stadium" },         // 4pm EDT
  { slot: "R16-4", round: "R16", dateISO: "2026-07-05T18:00:00-06:00", venueCity: "Ciudad de México",          venueStadium: "Estadio Azteca" },          // 6pm CDMX
  { slot: "R16-5", round: "R16", dateISO: "2026-07-06T13:00:00-06:00", venueCity: "Dallas",                    venueStadium: "AT&T Stadium" },            // 3pm EDT
  { slot: "R16-6", round: "R16", dateISO: "2026-07-06T18:00:00-06:00", venueCity: "Seattle",                   venueStadium: "Lumen Field" },             // 8pm EDT
  { slot: "R16-7", round: "R16", dateISO: "2026-07-07T10:00:00-06:00", venueCity: "Atlanta",                   venueStadium: "Mercedes-Benz Stadium" },   // noon EDT
  { slot: "R16-8", round: "R16", dateISO: "2026-07-07T14:00:00-06:00", venueCity: "Vancouver",                 venueStadium: "BC Place" },                // 4pm EDT

  // -------- QUARTERFINALS (4 matches, 9 – 11 jul 2026) --------
  { slot: "QF-1", round: "QF", dateISO: "2026-07-09T14:00:00-06:00", venueCity: "Boston",      venueStadium: "Gillette Stadium" },      // 4pm EDT
  { slot: "QF-2", round: "QF", dateISO: "2026-07-10T13:00:00-06:00", venueCity: "Los Angeles", venueStadium: "SoFi Stadium" },          // 3pm EDT
  { slot: "QF-3", round: "QF", dateISO: "2026-07-11T15:00:00-06:00", venueCity: "Miami",       venueStadium: "Hard Rock Stadium" },     // 5pm EDT
  { slot: "QF-4", round: "QF", dateISO: "2026-07-11T19:00:00-06:00", venueCity: "Kansas City", venueStadium: "Arrowhead Stadium" },     // 9pm EDT

  // -------- SEMIFINALS (2 matches, 14 – 15 jul 2026) --------
  { slot: "SF-1", round: "SF", dateISO: "2026-07-14T13:00:00-06:00", venueCity: "Dallas",  venueStadium: "AT&T Stadium" },              // 3pm EDT
  { slot: "SF-2", round: "SF", dateISO: "2026-07-15T13:00:00-06:00", venueCity: "Atlanta", venueStadium: "Mercedes-Benz Stadium" },     // 3pm EDT

  // -------- THIRD PLACE (1 match, 18 jul 2026) --------
  { slot: "THIRD", round: "THIRD", dateISO: "2026-07-18T15:00:00-06:00", venueCity: "Miami", venueStadium: "Hard Rock Stadium" },       // 5pm EDT

  // -------- FINAL (1 match, 19 jul 2026) --------
  { slot: "FINAL", round: "FINAL", dateISO: "2026-07-19T13:00:00-06:00", venueCity: "Nueva York / Nueva Jersey", venueStadium: "MetLife Stadium" }, // 3pm EDT
];

const BY_SLOT: Record<string, KOMatch> = Object.fromEntries(
  KO_SCHEDULE.map(m => [m.slot, m]),
);

export function findKOMatch(slot: string): KOMatch | undefined {
  return BY_SLOT[slot];
}

export function matchesForRound(round: KORound): KOMatch[] {
  return KO_SCHEDULE.filter(m => m.round === round);
}
