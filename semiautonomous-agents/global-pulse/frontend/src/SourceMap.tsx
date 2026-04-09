import { useEffect, useRef } from "react";
import { MapContainer, TileLayer, CircleMarker, Popup, useMap } from "react-leaflet";
import type { LatLngBoundsExpression } from "leaflet";

interface Source {
  source_name: string;
  country: string;
  country_code: string;
  flag: string;
  headline: string;
  tier: number;
}

interface Props {
  sources: Source[];
}

const COUNTRY_COORDS: Record<string, [number, number]> = {
  US: [39.8, -98.5], GB: [51.5, -0.1], FR: [48.8, 2.3], DE: [52.5, 13.4],
  JP: [35.6, 139.7], IN: [20.5, 78.9], BR: [-14.2, -51.9], AU: [-25.2, 133.7],
  QA: [25.3, 51.5], IL: [31.0, 34.8], ES: [40.4, -3.7], CA: [56.1, -106.3],
  HK: [22.3, 114.1], SG: [1.3, 103.8], KE: [-0.02, 37.9], CN: [35.8, 104.1],
  RU: [61.5, 105.3], IR: [32.4, 53.6], ZA: [-30.5, 22.9], MX: [23.6, -102.5],
  KR: [35.9, 127.7], EG: [26.8, 30.8], NG: [9.0, 8.6], AR: [-38.4, -63.6],
  SE: [60.1, 18.6], NO: [60.4, 8.4], NL: [52.1, 5.2], IT: [41.8, 12.5],
  TR: [38.9, 35.2], SA: [23.8, 45.0], PL: [51.9, 19.1], CO: [4.5, -74.5],
  TH: [15.8, 100.9], PH: [12.8, 121.7], ID: [-0.7, 113.9], MY: [4.2, 101.9],
  PK: [30.3, 69.3], BD: [23.6, 90.3], VN: [14.0, 108.2], UA: [48.3, 31.1],
  TW: [23.7, 120.9], CL: [-35.6, -71.5], PE: [-9.2, -75.0], CZ: [49.8, 15.4],
};

const TIER_COLORS: Record<number, string> = {
  1: "#f59e0b", // gold
  2: "#94a3b8", // silver
  3: "#b45309", // bronze
};

function FitBounds({ coords }: { coords: [number, number][] }) {
  const map = useMap();
  const fitted = useRef(false);

  useEffect(() => {
    if (coords.length > 0 && !fitted.current) {
      fitted.current = true;
      const bounds: LatLngBoundsExpression = coords.map(([lat, lng]) => [lat, lng] as [number, number]);
      map.fitBounds(bounds, { padding: [30, 30], maxZoom: 4 });
    }
  }, [coords, map]);

  return null;
}

export default function SourceMap({ sources }: Props) {
  // Group by country to avoid overlapping markers
  const countryGroups: Record<string, Source[]> = {};
  for (const s of sources) {
    const code = s.country_code || "XX";
    if (!countryGroups[code]) countryGroups[code] = [];
    countryGroups[code].push(s);
  }

  const markers = Object.entries(countryGroups)
    .filter(([code]) => COUNTRY_COORDS[code])
    .map(([code, srcs]) => ({
      code,
      coords: COUNTRY_COORDS[code],
      sources: srcs,
      bestTier: Math.min(...srcs.map((s) => s.tier)),
    }));

  const allCoords = markers.map((m) => m.coords);

  return (
    <div
      className="fade-in"
      style={{
        borderRadius: 12,
        overflow: "hidden",
        border: "1px solid var(--border)",
        height: 350,
      }}
    >
      <MapContainer
        center={[20, 0]}
        zoom={2}
        scrollWheelZoom={false}
        style={{ width: "100%", height: "100%", background: "var(--bg-primary)" }}
        attributionControl={false}
      >
        <TileLayer
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
        />
        <FitBounds coords={allCoords} />
        {markers.map((m) => (
          <CircleMarker
            key={m.code}
            center={m.coords}
            radius={8 + m.sources.length * 2}
            pathOptions={{
              fillColor: TIER_COLORS[m.bestTier] || "#94a3b8",
              fillOpacity: 0.7,
              color: TIER_COLORS[m.bestTier] || "#94a3b8",
              weight: 2,
              opacity: 0.9,
            }}
          >
            <Popup>
              <div style={{ fontFamily: "system-ui", maxWidth: 240 }}>
                <strong>{m.sources[0]?.flag} {m.sources[0]?.country}</strong>
                <div style={{ fontSize: 12, color: "#666", marginTop: 4 }}>
                  {m.sources.length} source{m.sources.length > 1 ? "s" : ""}
                </div>
                {m.sources.map((s, i) => (
                  <div key={i} style={{ fontSize: 12, marginTop: 6, borderTop: i > 0 ? "1px solid #eee" : undefined, paddingTop: i > 0 ? 6 : 0 }}>
                    <strong>{s.source_name}</strong>
                    <div style={{ color: "#555" }}>{s.headline.slice(0, 80)}...</div>
                  </div>
                ))}
              </div>
            </Popup>
          </CircleMarker>
        ))}
      </MapContainer>
    </div>
  );
}
