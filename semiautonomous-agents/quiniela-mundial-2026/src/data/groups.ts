// Mundial FIFA 2026 - Los 12 grupos del sorteo oficial (5 dic 2025, Washington DC)
// Fixtures verificados contra Wikipedia (en.wikipedia.org/wiki/2026_FIFA_World_Cup_Group_*)
import { TEAMS } from "./teams";

export const GROUP_LETTERS = ["A","B","C","D","E","F","G","H","I","J","K","L"] as const;
export type GroupLetter = typeof GROUP_LETTERS[number];

export const GROUPS: Record<GroupLetter, string[]> = {
  A: ["MEX","KOR","CZE","RSA"],
  B: ["CAN","SUI","QAT","BIH"],
  C: ["BRA","MAR","HAI","SCO"],
  D: ["USA","PAR","AUS","TUR"],
  E: ["GER","ECU","CUW","CIV"],
  F: ["NED","JPN","SWE","TUN"],
  G: ["BEL","EGY","IRN","NZL"],
  H: ["ESP","URU","KSA","CPV"],
  I: ["FRA","SEN","NOR","IRQ"],
  J: ["ARG","ALG","AUT","JOR"],
  K: ["POR","COL","COD","UZB"],
  L: ["ENG","CRO","GHA","PAN"],
};

export function teamsInGroup(letter: GroupLetter) {
  return GROUPS[letter].map(code => TEAMS.find(t => t.code === code)!);
}

export type GroupFixture = {
  id: string;
  group: GroupLetter;
  matchday: 1 | 2 | 3;
  home: string;
  away: string;
  date: string;        // YYYY-MM-DD
  kickoffLocal: string; // HH:MM (24h, local stadium time)
  venue: string;
  city: string;
};

// Calendario oficial FIFA 2026 - Fase de grupos (72 partidos)
// Orden: matchday 1 → 2 → 3, dentro de cada matchday por fecha y hora
export const GROUP_FIXTURES: GroupFixture[] = [
  // ---------- GROUP A ----------
  { id: "A-M1", group: "A", matchday: 1, date: "2026-06-11", kickoffLocal: "13:00", home: "MEX", away: "RSA", venue: "Estadio Azteca", city: "Ciudad de México" },
  { id: "A-M2", group: "A", matchday: 1, date: "2026-06-11", kickoffLocal: "20:00", home: "KOR", away: "CZE", venue: "Estadio Akron", city: "Zapopan" },
  { id: "A-M3", group: "A", matchday: 2, date: "2026-06-18", kickoffLocal: "12:00", home: "CZE", away: "RSA", venue: "Mercedes-Benz Stadium", city: "Atlanta" },
  { id: "A-M4", group: "A", matchday: 2, date: "2026-06-18", kickoffLocal: "19:00", home: "MEX", away: "KOR", venue: "Estadio Akron", city: "Zapopan" },
  { id: "A-M5", group: "A", matchday: 3, date: "2026-06-24", kickoffLocal: "19:00", home: "CZE", away: "MEX", venue: "Estadio Azteca", city: "Ciudad de México" },
  { id: "A-M6", group: "A", matchday: 3, date: "2026-06-24", kickoffLocal: "19:00", home: "RSA", away: "KOR", venue: "Estadio BBVA", city: "Guadalupe" },

  // ---------- GROUP B ----------
  { id: "B-M1", group: "B", matchday: 1, date: "2026-06-12", kickoffLocal: "15:00", home: "CAN", away: "BIH", venue: "BMO Field", city: "Toronto" },
  { id: "B-M2", group: "B", matchday: 1, date: "2026-06-13", kickoffLocal: "12:00", home: "QAT", away: "SUI", venue: "Levi's Stadium", city: "Santa Clara" },
  { id: "B-M3", group: "B", matchday: 2, date: "2026-06-18", kickoffLocal: "12:00", home: "SUI", away: "BIH", venue: "SoFi Stadium", city: "Inglewood" },
  { id: "B-M4", group: "B", matchday: 2, date: "2026-06-18", kickoffLocal: "15:00", home: "CAN", away: "QAT", venue: "BC Place", city: "Vancouver" },
  { id: "B-M5", group: "B", matchday: 3, date: "2026-06-24", kickoffLocal: "12:00", home: "SUI", away: "CAN", venue: "BC Place", city: "Vancouver" },
  { id: "B-M6", group: "B", matchday: 3, date: "2026-06-24", kickoffLocal: "12:00", home: "BIH", away: "QAT", venue: "Lumen Field", city: "Seattle" },

  // ---------- GROUP C ----------
  { id: "C-M1", group: "C", matchday: 1, date: "2026-06-13", kickoffLocal: "18:00", home: "BRA", away: "MAR", venue: "MetLife Stadium", city: "East Rutherford" },
  { id: "C-M2", group: "C", matchday: 1, date: "2026-06-13", kickoffLocal: "21:00", home: "HAI", away: "SCO", venue: "Gillette Stadium", city: "Foxborough" },
  { id: "C-M3", group: "C", matchday: 2, date: "2026-06-19", kickoffLocal: "18:00", home: "SCO", away: "MAR", venue: "Gillette Stadium", city: "Foxborough" },
  { id: "C-M4", group: "C", matchday: 2, date: "2026-06-19", kickoffLocal: "20:30", home: "BRA", away: "HAI", venue: "Lincoln Financial Field", city: "Philadelphia" },
  { id: "C-M5", group: "C", matchday: 3, date: "2026-06-24", kickoffLocal: "18:00", home: "SCO", away: "BRA", venue: "Hard Rock Stadium", city: "Miami Gardens" },
  { id: "C-M6", group: "C", matchday: 3, date: "2026-06-24", kickoffLocal: "18:00", home: "MAR", away: "HAI", venue: "Mercedes-Benz Stadium", city: "Atlanta" },

  // ---------- GROUP D ----------
  { id: "D-M1", group: "D", matchday: 1, date: "2026-06-12", kickoffLocal: "18:00", home: "USA", away: "PAR", venue: "SoFi Stadium", city: "Inglewood" },
  { id: "D-M2", group: "D", matchday: 1, date: "2026-06-13", kickoffLocal: "21:00", home: "AUS", away: "TUR", venue: "BC Place", city: "Vancouver" },
  { id: "D-M3", group: "D", matchday: 2, date: "2026-06-19", kickoffLocal: "12:00", home: "USA", away: "AUS", venue: "Lumen Field", city: "Seattle" },
  { id: "D-M4", group: "D", matchday: 2, date: "2026-06-19", kickoffLocal: "20:00", home: "TUR", away: "PAR", venue: "Levi's Stadium", city: "Santa Clara" },
  { id: "D-M5", group: "D", matchday: 3, date: "2026-06-25", kickoffLocal: "19:00", home: "TUR", away: "USA", venue: "SoFi Stadium", city: "Inglewood" },
  { id: "D-M6", group: "D", matchday: 3, date: "2026-06-25", kickoffLocal: "19:00", home: "PAR", away: "AUS", venue: "Levi's Stadium", city: "Santa Clara" },

  // ---------- GROUP E ----------
  { id: "E-M1", group: "E", matchday: 1, date: "2026-06-14", kickoffLocal: "12:00", home: "GER", away: "CUW", venue: "NRG Stadium", city: "Houston" },
  { id: "E-M2", group: "E", matchday: 1, date: "2026-06-14", kickoffLocal: "19:00", home: "CIV", away: "ECU", venue: "Lincoln Financial Field", city: "Philadelphia" },
  { id: "E-M3", group: "E", matchday: 2, date: "2026-06-20", kickoffLocal: "16:00", home: "GER", away: "CIV", venue: "BMO Field", city: "Toronto" },
  { id: "E-M4", group: "E", matchday: 2, date: "2026-06-20", kickoffLocal: "19:00", home: "ECU", away: "CUW", venue: "Arrowhead Stadium", city: "Kansas City" },
  { id: "E-M5", group: "E", matchday: 3, date: "2026-06-25", kickoffLocal: "16:00", home: "CUW", away: "CIV", venue: "Lincoln Financial Field", city: "Philadelphia" },
  { id: "E-M6", group: "E", matchday: 3, date: "2026-06-25", kickoffLocal: "16:00", home: "ECU", away: "GER", venue: "MetLife Stadium", city: "East Rutherford" },

  // ---------- GROUP F ----------
  { id: "F-M1", group: "F", matchday: 1, date: "2026-06-14", kickoffLocal: "15:00", home: "NED", away: "JPN", venue: "AT&T Stadium", city: "Arlington" },
  { id: "F-M2", group: "F", matchday: 1, date: "2026-06-14", kickoffLocal: "20:00", home: "SWE", away: "TUN", venue: "Estadio BBVA", city: "Guadalupe" },
  { id: "F-M3", group: "F", matchday: 2, date: "2026-06-20", kickoffLocal: "12:00", home: "NED", away: "SWE", venue: "NRG Stadium", city: "Houston" },
  { id: "F-M4", group: "F", matchday: 2, date: "2026-06-20", kickoffLocal: "22:00", home: "TUN", away: "JPN", venue: "Estadio BBVA", city: "Guadalupe" },
  { id: "F-M5", group: "F", matchday: 3, date: "2026-06-25", kickoffLocal: "18:00", home: "JPN", away: "SWE", venue: "AT&T Stadium", city: "Arlington" },
  { id: "F-M6", group: "F", matchday: 3, date: "2026-06-25", kickoffLocal: "18:00", home: "TUN", away: "NED", venue: "Arrowhead Stadium", city: "Kansas City" },

  // ---------- GROUP G ----------
  { id: "G-M1", group: "G", matchday: 1, date: "2026-06-15", kickoffLocal: "12:00", home: "BEL", away: "EGY", venue: "Lumen Field", city: "Seattle" },
  { id: "G-M2", group: "G", matchday: 1, date: "2026-06-15", kickoffLocal: "18:00", home: "IRN", away: "NZL", venue: "SoFi Stadium", city: "Inglewood" },
  { id: "G-M3", group: "G", matchday: 2, date: "2026-06-21", kickoffLocal: "12:00", home: "BEL", away: "IRN", venue: "SoFi Stadium", city: "Inglewood" },
  { id: "G-M4", group: "G", matchday: 2, date: "2026-06-21", kickoffLocal: "18:00", home: "NZL", away: "EGY", venue: "BC Place", city: "Vancouver" },
  { id: "G-M5", group: "G", matchday: 3, date: "2026-06-26", kickoffLocal: "20:00", home: "EGY", away: "IRN", venue: "Lumen Field", city: "Seattle" },
  { id: "G-M6", group: "G", matchday: 3, date: "2026-06-26", kickoffLocal: "20:00", home: "NZL", away: "BEL", venue: "BC Place", city: "Vancouver" },

  // ---------- GROUP H ----------
  { id: "H-M1", group: "H", matchday: 1, date: "2026-06-15", kickoffLocal: "12:00", home: "ESP", away: "CPV", venue: "Mercedes-Benz Stadium", city: "Atlanta" },
  { id: "H-M2", group: "H", matchday: 1, date: "2026-06-15", kickoffLocal: "18:00", home: "KSA", away: "URU", venue: "Hard Rock Stadium", city: "Miami Gardens" },
  { id: "H-M3", group: "H", matchday: 2, date: "2026-06-21", kickoffLocal: "12:00", home: "ESP", away: "KSA", venue: "Mercedes-Benz Stadium", city: "Atlanta" },
  { id: "H-M4", group: "H", matchday: 2, date: "2026-06-21", kickoffLocal: "18:00", home: "URU", away: "CPV", venue: "Hard Rock Stadium", city: "Miami Gardens" },
  { id: "H-M5", group: "H", matchday: 3, date: "2026-06-26", kickoffLocal: "19:00", home: "CPV", away: "KSA", venue: "NRG Stadium", city: "Houston" },
  { id: "H-M6", group: "H", matchday: 3, date: "2026-06-26", kickoffLocal: "18:00", home: "URU", away: "ESP", venue: "Estadio Akron", city: "Zapopan" },

  // ---------- GROUP I ----------
  { id: "I-M1", group: "I", matchday: 1, date: "2026-06-16", kickoffLocal: "15:00", home: "FRA", away: "SEN", venue: "MetLife Stadium", city: "East Rutherford" },
  { id: "I-M2", group: "I", matchday: 1, date: "2026-06-16", kickoffLocal: "18:00", home: "IRQ", away: "NOR", venue: "Gillette Stadium", city: "Foxborough" },
  { id: "I-M3", group: "I", matchday: 2, date: "2026-06-22", kickoffLocal: "17:00", home: "FRA", away: "IRQ", venue: "Lincoln Financial Field", city: "Philadelphia" },
  { id: "I-M4", group: "I", matchday: 2, date: "2026-06-22", kickoffLocal: "20:00", home: "NOR", away: "SEN", venue: "MetLife Stadium", city: "East Rutherford" },
  { id: "I-M5", group: "I", matchday: 3, date: "2026-06-26", kickoffLocal: "15:00", home: "NOR", away: "FRA", venue: "Gillette Stadium", city: "Foxborough" },
  { id: "I-M6", group: "I", matchday: 3, date: "2026-06-26", kickoffLocal: "15:00", home: "SEN", away: "IRQ", venue: "BMO Field", city: "Toronto" },

  // ---------- GROUP J ----------
  { id: "J-M1", group: "J", matchday: 1, date: "2026-06-16", kickoffLocal: "20:00", home: "ARG", away: "ALG", venue: "Arrowhead Stadium", city: "Kansas City" },
  { id: "J-M2", group: "J", matchday: 1, date: "2026-06-16", kickoffLocal: "21:00", home: "AUT", away: "JOR", venue: "Levi's Stadium", city: "Santa Clara" },
  { id: "J-M3", group: "J", matchday: 2, date: "2026-06-22", kickoffLocal: "12:00", home: "ARG", away: "AUT", venue: "AT&T Stadium", city: "Arlington" },
  { id: "J-M4", group: "J", matchday: 2, date: "2026-06-22", kickoffLocal: "20:00", home: "JOR", away: "ALG", venue: "Levi's Stadium", city: "Santa Clara" },
  { id: "J-M5", group: "J", matchday: 3, date: "2026-06-27", kickoffLocal: "21:00", home: "ALG", away: "AUT", venue: "Arrowhead Stadium", city: "Kansas City" },
  { id: "J-M6", group: "J", matchday: 3, date: "2026-06-27", kickoffLocal: "21:00", home: "JOR", away: "ARG", venue: "AT&T Stadium", city: "Arlington" },

  // ---------- GROUP K ----------
  { id: "K-M1", group: "K", matchday: 1, date: "2026-06-17", kickoffLocal: "12:00", home: "POR", away: "COD", venue: "NRG Stadium", city: "Houston" },
  { id: "K-M2", group: "K", matchday: 1, date: "2026-06-17", kickoffLocal: "20:00", home: "UZB", away: "COL", venue: "Estadio Azteca", city: "Ciudad de México" },
  { id: "K-M3", group: "K", matchday: 2, date: "2026-06-23", kickoffLocal: "12:00", home: "POR", away: "UZB", venue: "NRG Stadium", city: "Houston" },
  { id: "K-M4", group: "K", matchday: 2, date: "2026-06-23", kickoffLocal: "20:00", home: "COL", away: "COD", venue: "Estadio Akron", city: "Zapopan" },
  { id: "K-M5", group: "K", matchday: 3, date: "2026-06-27", kickoffLocal: "19:30", home: "COL", away: "POR", venue: "Hard Rock Stadium", city: "Miami Gardens" },
  { id: "K-M6", group: "K", matchday: 3, date: "2026-06-27", kickoffLocal: "19:30", home: "COD", away: "UZB", venue: "Mercedes-Benz Stadium", city: "Atlanta" },

  // ---------- GROUP L ----------
  { id: "L-M1", group: "L", matchday: 1, date: "2026-06-17", kickoffLocal: "15:00", home: "ENG", away: "CRO", venue: "AT&T Stadium", city: "Arlington" },
  { id: "L-M2", group: "L", matchday: 1, date: "2026-06-17", kickoffLocal: "19:00", home: "GHA", away: "PAN", venue: "BMO Field", city: "Toronto" },
  { id: "L-M3", group: "L", matchday: 2, date: "2026-06-23", kickoffLocal: "16:00", home: "ENG", away: "GHA", venue: "Gillette Stadium", city: "Foxborough" },
  { id: "L-M4", group: "L", matchday: 2, date: "2026-06-23", kickoffLocal: "19:00", home: "PAN", away: "CRO", venue: "BMO Field", city: "Toronto" },
  { id: "L-M5", group: "L", matchday: 3, date: "2026-06-27", kickoffLocal: "17:00", home: "PAN", away: "ENG", venue: "MetLife Stadium", city: "East Rutherford" },
  { id: "L-M6", group: "L", matchday: 3, date: "2026-06-27", kickoffLocal: "17:00", home: "CRO", away: "GHA", venue: "Lincoln Financial Field", city: "Philadelphia" },
];

export function groupFixtures(letter: GroupLetter): GroupFixture[] {
  return GROUP_FIXTURES.filter(f => f.group === letter);
}

export function allGroupFixtures(): GroupFixture[] {
  return GROUP_FIXTURES;
}
