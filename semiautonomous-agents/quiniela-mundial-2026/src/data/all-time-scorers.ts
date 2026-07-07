// All-time top scorers in FIFA Men's World Cup history (pre-2026 totals).
// The component merges these with live 2026 goals from /api/scorers and
// re-ranks dynamically, so ranks here are approximate starting points.
//
// Source: https://en.wikipedia.org/wiki/List_of_FIFA_World_Cup_goalscorers
//         https://www.fifa.com/fifaplus/en/articles/all-time-top-scorers-world-cup

export type HistoricScorer = {
  rank: number;
  name: string;
  country: string;     // English country name
  countryIso2: string; // ISO 3166-1 alpha-2 (lowercase, for flagcdn)
  goals: number;
  worldCups: string;   // Editions when goals were scored
  photo?: string;      // Optional canonical portrait; omit to render initials
};

export const ALL_TIME_TOP_SCORERS: HistoricScorer[] = [
  { rank: 1,  name: "Miroslav Klose",    country: "Germany",   countryIso2: "de", goals: 16, worldCups: "2002 · 2006 · 2010 · 2014" },
  { rank: 2,  name: "Ronaldo Nazário",   country: "Brazil",    countryIso2: "br", goals: 15, worldCups: "1994 · 1998 · 2002 · 2006" },
  { rank: 3,  name: "Gerd Müller",       country: "Germany",   countryIso2: "de", goals: 14, worldCups: "1970 · 1974" },
  { rank: 4,  name: "Just Fontaine",     country: "France",    countryIso2: "fr", goals: 13, worldCups: "1958" },
  { rank: 4,  name: "Lionel Messi",      country: "Argentina", countryIso2: "ar", goals: 13, worldCups: "2006 · 2010 · 2014 · 2018 · 2022" },
  { rank: 6,  name: "Pelé",              country: "Brazil",    countryIso2: "br", goals: 12, worldCups: "1958 · 1962 · 1966 · 1970" },
  { rank: 6,  name: "Kylian Mbappé",     country: "France",    countryIso2: "fr", goals: 12, worldCups: "2018 · 2022" },
  { rank: 8,  name: "Sándor Kocsis",     country: "Hungary",   countryIso2: "hu", goals: 11, worldCups: "1954" },
  { rank: 9,  name: "Helmut Rahn",       country: "Germany",   countryIso2: "de", goals: 10, worldCups: "1954 · 1958" },
  { rank: 9,  name: "Teófilo Cubillas",  country: "Peru",      countryIso2: "pe", goals: 10, worldCups: "1970 · 1978" },
  { rank: 9,  name: "Grzegorz Lato",     country: "Poland",    countryIso2: "pl", goals: 10, worldCups: "1974 · 1978 · 1982" },
  { rank: 9,  name: "Gary Lineker",      country: "England",   countryIso2: "gb", goals: 10, worldCups: "1986 · 1990" },
  { rank: 9,  name: "Gabriel Batistuta", country: "Argentina", countryIso2: "ar", goals: 10, worldCups: "1994 · 1998 · 2002" },
  { rank: 14, name: "Eusébio",           country: "Portugal",  countryIso2: "pt", goals: 9,  worldCups: "1966" },
  { rank: 14, name: "Roberto Baggio",    country: "Italy",     countryIso2: "it", goals: 9,  worldCups: "1990 · 1994 · 1998" },
  { rank: 16, name: "Cristiano Ronaldo", country: "Portugal",  countryIso2: "pt", goals: 8,  worldCups: "2006 · 2010 · 2014 · 2018 · 2022" },
];
