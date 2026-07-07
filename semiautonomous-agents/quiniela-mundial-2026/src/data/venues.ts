// Mundial FIFA 2026 - Las 16 sedes oficiales
export type Venue = {
  city: string;
  country: "USA" | "México" | "Canadá";
  stadium: string;
  capacity: number;
  iso2: string;
};

export const VENUES: Venue[] = [
  { city: "Dallas",                       country: "USA",     stadium: "AT&T Stadium",           capacity: 94000, iso2: "us" },
  { city: "Ciudad de México",             country: "México",  stadium: "Estadio Azteca",         capacity: 83000, iso2: "mx" },
  { city: "Nueva York / Nueva Jersey",    country: "USA",     stadium: "MetLife Stadium",        capacity: 82500, iso2: "us" },
  { city: "Atlanta",                      country: "USA",     stadium: "Mercedes-Benz Stadium",  capacity: 75000, iso2: "us" },
  { city: "Kansas City",                  country: "USA",     stadium: "Arrowhead Stadium",      capacity: 73000, iso2: "us" },
  { city: "Houston",                      country: "USA",     stadium: "NRG Stadium",            capacity: 72000, iso2: "us" },
  { city: "Bahía de San Francisco",       country: "USA",     stadium: "Levi's Stadium",         capacity: 71000, iso2: "us" },
  { city: "Los Angeles",                  country: "USA",     stadium: "SoFi Stadium",           capacity: 70000, iso2: "us" },
  { city: "Filadelfia",                   country: "USA",     stadium: "Lincoln Financial Field",capacity: 69000, iso2: "us" },
  { city: "Seattle",                      country: "USA",     stadium: "Lumen Field",            capacity: 69000, iso2: "us" },
  { city: "Boston",                       country: "USA",     stadium: "Gillette Stadium",       capacity: 65000, iso2: "us" },
  { city: "Miami",                        country: "USA",     stadium: "Hard Rock Stadium",      capacity: 65000, iso2: "us" },
  { city: "Vancouver",                    country: "Canadá",  stadium: "BC Place",               capacity: 54000, iso2: "ca" },
  { city: "Monterrey",                    country: "México",  stadium: "Estadio BBVA",           capacity: 53500, iso2: "mx" },
  { city: "Guadalajara",                  country: "México",  stadium: "Estadio Akron",          capacity: 48000, iso2: "mx" },
  { city: "Toronto",                      country: "Canadá",  stadium: "BMO Field",              capacity: 45000, iso2: "ca" },
];
