import { useState } from 'react';
import { X, MapPin, Navigation } from 'lucide-react';

interface NeighborhoodPickerProps {
  value: string;
  onChange: (value: string) => void;
  isOpen: boolean;
  onClose: () => void;
}

const NEIGHBORHOODS = [
  'Williamsburg, Brooklyn',
  'Lower East Side, NYC',
  'Nolita, NYC',
  'West Village, NYC',
  'East Village, NYC',
  'Astoria, Queens',
  'Bed-Stuy, Brooklyn',
  'Carroll Gardens, Brooklyn',
  'Greenpoint, Brooklyn',
  'Bushwick, Brooklyn',
  'Harlem, NYC',
  'Chelsea, NYC',
  'Tribeca, NYC',
  'SoHo, NYC',
  'Fort Greene, Brooklyn',
  'Park Slope, Brooklyn',
  'DUMBO, Brooklyn',
  'Long Island City, Queens',
];

export default function NeighborhoodPicker({
  value,
  onChange,
  isOpen,
  onClose
}: NeighborhoodPickerProps) {
  const [search, setSearch] = useState('');
  const [isLocating, setIsLocating] = useState(false);

  const filteredNeighborhoods = NEIGHBORHOODS.filter(n =>
    n.toLowerCase().includes(search.toLowerCase())
  );

  const handleSelect = (neighborhood: string) => {
    onChange(neighborhood);
    onClose();
  };

  const handleUseLocation = () => {
    if (!navigator.geolocation) {
      alert('Geolocation is not supported by your browser');
      return;
    }

    setIsLocating(true);
    navigator.geolocation.getCurrentPosition(
      async (position) => {
        const { latitude, longitude } = position.coords;
        try {
          // Reverse geocode using Nominatim
          const resp = await fetch(
            `https://nominatim.openstreetmap.org/reverse?lat=${latitude}&lon=${longitude}&format=json`
          );
          const data = await resp.json();
          const neighborhood = data.address?.neighbourhood ||
                              data.address?.suburb ||
                              data.address?.city_district ||
                              'Current Location';
          const city = data.address?.city || data.address?.town || 'NYC';
          onChange(`${neighborhood}, ${city}`);
          onClose();
        } catch {
          onChange(`${latitude.toFixed(4)}, ${longitude.toFixed(4)}`);
          onClose();
        }
        setIsLocating(false);
      },
      () => {
        alert('Unable to retrieve your location');
        setIsLocating(false);
      }
    );
  };

  if (!isOpen) return null;

  return (
    <div className="neighborhood-modal-overlay" onClick={onClose}>
      <div className="neighborhood-modal" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <h3 className="modal-title">Choose Location</h3>
          <button className="modal-close" onClick={onClose}>
            <X size={20} />
          </button>
        </div>

        <input
          type="text"
          className="neighborhood-search"
          placeholder="Search neighborhoods..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          autoFocus
        />

        <div className="neighborhood-list">
          {filteredNeighborhoods.map(neighborhood => (
            <button
              key={neighborhood}
              className={`neighborhood-item ${value === neighborhood ? 'selected' : ''}`}
              onClick={() => handleSelect(neighborhood)}
            >
              <MapPin size={14} style={{ display: 'inline', marginRight: 8 }} />
              {neighborhood}
            </button>
          ))}
        </div>

        <button
          className="use-location-btn"
          onClick={handleUseLocation}
          disabled={isLocating}
        >
          <Navigation size={16} />
          {isLocating ? 'Getting location...' : 'Use my location'}
        </button>
      </div>
    </div>
  );
}
