import { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { VenueResult } from './VenueCard';

// Fix for default marker icons in webpack/vite
// @ts-ignore
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
});

// Custom venue marker
const venueIcon = new L.Icon({
  iconUrl: 'data:image/svg+xml;base64,' + btoa(`
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#F59E0B" width="32" height="32">
      <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/>
    </svg>
  `),
  iconSize: [32, 32],
  iconAnchor: [16, 32],
  popupAnchor: [0, -32],
});

// User location marker
const userIcon = new L.Icon({
  iconUrl: 'data:image/svg+xml;base64,' + btoa(`
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#14B8A6" width="24" height="24">
      <circle cx="12" cy="12" r="8" stroke="white" stroke-width="2"/>
    </svg>
  `),
  iconSize: [24, 24],
  iconAnchor: [12, 12],
});

interface VenueMapProps {
  venues: VenueResult[];
  selectedVenue: VenueResult | null;
  onVenueSelect: (venue: VenueResult) => void;
  userLocation: [number, number] | null;
}

// Component to fit map bounds to venues
function FitBounds({ venues, userLocation }: { venues: VenueResult[]; userLocation: [number, number] | null }) {
  const map = useMap();

  useEffect(() => {
    if (venues.length === 0) return;

    const points: [number, number][] = venues
      .filter((v): v is VenueResult & { coordinates: { latitude: number; longitude: number } } =>
        !!(v.coordinates?.latitude && v.coordinates?.longitude))
      .map(v => [v.coordinates.latitude, v.coordinates.longitude]);

    if (userLocation) {
      points.push(userLocation);
    }

    if (points.length > 0) {
      const bounds = L.latLngBounds(points);
      map.fitBounds(bounds, { padding: [50, 50] });
    }
  }, [venues, userLocation, map]);

  return null;
}

// Component to show route
function RouteLayer({ route }: { route: [number, number][] | null }) {
  if (!route || route.length === 0) return null;

  return (
    <Polyline
      positions={route}
      pathOptions={{
        color: '#F59E0B',
        weight: 4,
        opacity: 0.8,
        dashArray: '10, 10',
      }}
    />
  );
}

export default function VenueMap({ venues, selectedVenue, onVenueSelect, userLocation }: VenueMapProps) {
  const [route, setRoute] = useState<[number, number][] | null>(null);
  const [walkingTime, setWalkingTime] = useState<number | null>(null);

  // Fetch walking route when venue is selected
  useEffect(() => {
    if (!selectedVenue || !userLocation || !selectedVenue.coordinates) {
      setRoute(null);
      setWalkingTime(null);
      return;
    }

    const fetchRoute = async () => {
      try {
        const [userLat, userLng] = userLocation;
        const { latitude: venueLat, longitude: venueLng } = selectedVenue.coordinates!;

        const response = await fetch(
          `https://router.project-osrm.org/route/v1/walking/${userLng},${userLat};${venueLng},${venueLat}?overview=full&geometries=geojson`
        );
        const data = await response.json();

        if (data.routes && data.routes[0]) {
          const coords = data.routes[0].geometry.coordinates.map(
            ([lng, lat]: [number, number]) => [lat, lng] as [number, number]
          );
          setRoute(coords);
          setWalkingTime(Math.round(data.routes[0].duration / 60));
        }
      } catch (error) {
        console.error('Failed to fetch route:', error);
      }
    };

    fetchRoute();
  }, [selectedVenue, userLocation]);

  // Default center (Williamsburg)
  const defaultCenter: [number, number] = [40.7142, -73.9612];

  const center = venues.length > 0 && venues[0].coordinates
    ? [venues[0].coordinates.latitude, venues[0].coordinates.longitude] as [number, number]
    : defaultCenter;

  return (
    <div className="venue-map-container">
      {walkingTime && selectedVenue && (
        <div className="walking-time-badge">
          <span className="walk-icon">🚶</span>
          <span>{walkingTime} min walk to {selectedVenue.name}</span>
        </div>
      )}

      <MapContainer
        center={center}
        zoom={14}
        style={{ height: '400px', width: '100%', borderRadius: '12px' }}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
        />

        <FitBounds venues={venues} userLocation={userLocation} />
        <RouteLayer route={route} />

        {/* User location marker */}
        {userLocation && (
          <Marker position={userLocation} icon={userIcon}>
            <Popup>
              <div style={{ color: '#000' }}>
                <strong>You are here</strong>
              </div>
            </Popup>
          </Marker>
        )}

        {/* Venue markers */}
        {venues.map((venue, index) => {
          if (!venue.coordinates?.latitude || !venue.coordinates?.longitude) return null;

          const position: [number, number] = [
            venue.coordinates.latitude,
            venue.coordinates.longitude,
          ];

          return (
            <Marker
              key={`${venue.name}-${index}`}
              position={position}
              icon={venueIcon}
              eventHandlers={{
                click: () => onVenueSelect(venue),
              }}
            >
              <Popup>
                <div style={{ color: '#000', minWidth: '150px' }}>
                  <strong>{venue.name}</strong>
                  <div style={{ fontSize: '12px', color: '#666', marginTop: '4px' }}>
                    {venue.address}
                  </div>
                  <div style={{ marginTop: '8px', display: 'flex', gap: '4px', flexWrap: 'wrap' }}>
                    <span style={{
                      background: '#F59E0B',
                      color: '#000',
                      padding: '2px 6px',
                      borderRadius: '4px',
                      fontSize: '11px',
                      fontWeight: 'bold'
                    }}>
                      ⬡ {venue.underground_score}
                    </span>
                    {venue.vibe_tags?.slice(0, 2).map(tag => (
                      <span key={tag} style={{
                        background: '#333',
                        color: '#fff',
                        padding: '2px 6px',
                        borderRadius: '4px',
                        fontSize: '11px'
                      }}>
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>
              </Popup>
            </Marker>
          );
        })}
      </MapContainer>
    </div>
  );
}
