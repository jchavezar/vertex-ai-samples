import { useState, useEffect, useRef } from 'react';
import { X, MapPin, Navigation, Search } from 'lucide-react';

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

// NYC-area bounding box for Nominatim viewbox bias (lon,lat order, west,south,east,north)
const NYC_VIEWBOX = '-74.27,40.49,-73.69,40.91';

interface AddressSuggestion {
  display: string;        // what we show in the list
  short: string;          // what we save when selected (e.g. "515 W 38th St, Hudson Yards, NYC")
  fullDisplayName: string;
  lat: string;
  lon: string;
}

function shortFormat(item: any): { display: string; short: string } {
  const a = item.address || {};
  const houseNumber = a.house_number || '';
  const road = a.road || a.pedestrian || a.footway || '';
  const street = [houseNumber, road].filter(Boolean).join(' ');
  const neighborhood = a.neighbourhood || a.suburb || a.quarter || a.city_district || '';
  const borough = a.borough || a.county || '';
  const city = a.city || a.town || a.village || '';

  // For an address-like result, prefer street first
  if (street) {
    const tail = [neighborhood, borough || city].filter(Boolean).join(', ');
    const short = tail ? `${street}, ${tail}` : street;
    return { display: short, short };
  }
  // Otherwise neighborhood-style
  if (neighborhood) {
    const tail = [borough || city].filter(Boolean).join(', ');
    const short = tail ? `${neighborhood}, ${tail}` : neighborhood;
    return { display: short, short };
  }
  // Fallback to display name
  return { display: item.display_name, short: item.display_name };
}

export default function NeighborhoodPicker({
  value,
  onChange,
  isOpen,
  onClose
}: NeighborhoodPickerProps) {
  const [search, setSearch] = useState('');
  const [isLocating, setIsLocating] = useState(false);
  const [suggestions, setSuggestions] = useState<AddressSuggestion[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const lastSearchRef = useRef('');

  const filteredPresets = search
    ? NEIGHBORHOODS.filter(n => n.toLowerCase().includes(search.toLowerCase()))
    : NEIGHBORHOODS;

  // Debounced live search via Nominatim
  useEffect(() => {
    if (debounceRef.current) clearTimeout(debounceRef.current);
    const q = search.trim();
    if (q.length < 3) {
      setSuggestions([]);
      setIsSearching(false);
      return;
    }
    debounceRef.current = setTimeout(async () => {
      lastSearchRef.current = q;
      setIsSearching(true);
      try {
        const url = `https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(q)}` +
          `&format=jsonv2&limit=6&addressdetails=1&countrycodes=us` +
          `&viewbox=${NYC_VIEWBOX}&bounded=1`;
        const resp = await fetch(url, {
          headers: { 'Accept': 'application/json', 'Accept-Language': 'en' }
        });
        if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
        const items: any[] = await resp.json();
        // Skip stale responses
        if (lastSearchRef.current !== q) return;
        const formatted: AddressSuggestion[] = items.map(it => {
          const { display, short } = shortFormat(it);
          return { display, short, fullDisplayName: it.display_name, lat: it.lat, lon: it.lon };
        });
        setSuggestions(formatted);
      } catch {
        setSuggestions([]);
      } finally {
        setIsSearching(false);
      }
    }, 350);

    return () => {
      if (debounceRef.current) clearTimeout(debounceRef.current);
    };
  }, [search]);

  // Reset state when modal closes
  useEffect(() => {
    if (!isOpen) {
      setSearch('');
      setSuggestions([]);
    }
  }, [isOpen]);

  const handleSelect = (val: string) => {
    onChange(val);
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
          const resp = await fetch(
            `https://nominatim.openstreetmap.org/reverse?lat=${latitude}&lon=${longitude}&format=json&addressdetails=1`,
            { headers: { 'Accept-Language': 'en' } }
          );
          const data = await resp.json();
          const { short } = shortFormat(data);
          onChange(short || `${latitude.toFixed(4)}, ${longitude.toFixed(4)}`);
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

        <div style={{ position: 'relative' }}>
          <input
            type="text"
            className="neighborhood-search"
            placeholder="Type an address (e.g. 515 W 38th St) or neighborhood…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            autoFocus
          />
          {isSearching && (
            <span style={{
              position: 'absolute', right: 14, top: '50%', transform: 'translateY(-50%)',
              fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'uppercase',
              letterSpacing: '0.04em', fontWeight: 600
            }}>
              Searching…
            </span>
          )}
        </div>

        {/* Live address suggestions (Nominatim) */}
        {suggestions.length > 0 && (
          <>
            <div className="picker-section-header">Address Matches</div>
            <div className="neighborhood-list">
              {suggestions.map((s, i) => (
                <button
                  key={`addr-${i}`}
                  className={`neighborhood-item ${value === s.short ? 'selected' : ''}`}
                  onClick={() => handleSelect(s.short)}
                  title={s.fullDisplayName}
                >
                  <Search size={14} style={{ display: 'inline', marginRight: 8, opacity: 0.7 }} />
                  {s.display}
                </button>
              ))}
            </div>
          </>
        )}

        {/* Preset neighborhoods (always visible, filtered by typed text) */}
        {filteredPresets.length > 0 && (
          <>
            <div className="picker-section-header">
              {search ? 'Quick-Pick Neighborhoods' : 'Popular NYC Neighborhoods'}
            </div>
            <div className="neighborhood-list">
              {filteredPresets.map(neighborhood => (
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
          </>
        )}

        {search.length >= 3 && !isSearching && suggestions.length === 0 && filteredPresets.length === 0 && (
          <div style={{
            padding: '20px 16px', textAlign: 'center', color: 'var(--text-muted)',
            fontSize: '0.85rem'
          }}>
            No matches. Try a different street or neighborhood.
          </div>
        )}

        <button
          className="use-location-btn"
          onClick={handleUseLocation}
          disabled={isLocating}
        >
          <Navigation size={16} />
          {isLocating ? 'Getting location…' : 'Use my location'}
        </button>
      </div>
    </div>
  );
}
