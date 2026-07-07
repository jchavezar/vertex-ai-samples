// Maps fixture cities (as stored in `groups.ts:GROUP_FIXTURES.city`) to the
// host country. Used to apply a real home-crowd advantage when MEX/USA/CAN
// play at home in their own country.

export type HostCountry = "MEX" | "USA" | "CAN";

const CITY_COUNTRY: Record<string, HostCountry> = {
  // Mexico
  "Ciudad de México": "MEX",
  "Zapopan": "MEX",         // Estadio Akron (Guadalajara metro)
  "Guadalupe": "MEX",       // Estadio BBVA (Monterrey metro)
  // USA
  "Atlanta": "USA",
  "East Rutherford": "USA",
  "Foxborough": "USA",
  "Philadelphia": "USA",
  "Miami Gardens": "USA",
  "Houston": "USA",
  "Kansas City": "USA",
  "Arlington": "USA",
  "Dallas": "USA",
  "Santa Clara": "USA",
  "Inglewood": "USA",
  "Seattle": "USA",
  // Canada
  "Vancouver": "CAN",
  "Toronto": "CAN",
};

export function fixtureCityCountry(city: string): HostCountry | null {
  return CITY_COUNTRY[city] ?? null;
}

// Returns true if `teamCode` is the host nation of the city where it's playing.
// Used to apply the small "real home crowd" boost on top of the generic +4
// home-field bonus that every "home" fixture already gets.
export function isHomeNationAtHome(teamCode: string, city: string): boolean {
  const c = fixtureCityCountry(city);
  return c !== null && c === (teamCode as HostCountry);
}
