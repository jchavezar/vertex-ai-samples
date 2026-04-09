import { useState } from 'react';
import { Sparkles, MapPin, Search, ChevronRight, Map, Navigation } from 'lucide-react';
import VenueCard, { VenueResult } from './VenueCard';
import VibeDials, { SearchParams } from './VibeDials';
import NeighborhoodPicker from './NeighborhoodPicker';
import VenueMap from './VenueMap';
import VenueDetailPanel from './VenueDetailPanel';
import EventsBanner from './EventsBanner';

const TIME_OPTIONS = [
  { id: 'morning', label: 'Morning', icon: '🌅' },
  { id: 'afternoon', label: 'Afternoon', icon: '☀️' },
  { id: 'evening', label: 'Evening', icon: '🌆' },
  { id: 'night', label: 'Night', icon: '🌙' },
];

const SAMPLE_PROMPTS = [
  'Cozy morning spot, contemporary interior, good coffee, walk-in friendly',
  'Late night cocktails, moody lighting, interesting crowd, not touristy',
  'Quiet afternoon cafe, minimal design, laptop-friendly, locals only',
  'Sunday brunch vibes, bright and airy, neighborhood regulars',
];

export default function App() {
  const [venues, setVenues] = useState<VenueResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [location, setLocation] = useState('Williamsburg, Brooklyn');
  const [timeOfDay, setTimeOfDay] = useState('morning');
  const [showLocationPicker, setShowLocationPicker] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);
  const [showMap, setShowMap] = useState(true);
  const [selectedVenue, setSelectedVenue] = useState<VenueResult | null>(null);
  const [detailVenue, setDetailVenue] = useState<VenueResult | null>(null);
  const [userLocation, setUserLocation] = useState<[number, number] | null>(null);

  const handleLocateMe = () => {
    if (!navigator.geolocation) {
      alert('Geolocation is not supported by your browser');
      return;
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        setUserLocation([position.coords.latitude, position.coords.longitude]);
      },
      (error) => {
        console.error('Geolocation error:', error);
        alert('Unable to get your location');
      }
    );
  };

  const handleSearch = async (params: SearchParams) => {
    setIsLoading(true);
    setError(null);
    setHasSearched(true);

    try {
      const response = await fetch('/api/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(params),
      });

      if (!response.ok) {
        throw new Error(`Search failed: ${response.status}`);
      }

      const data = await response.json();
      setVenues(data.venues || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Search failed');
      setVenues([]);
    } finally {
      setIsLoading(false);
    }
  };

  const handlePromptClick = (prompt: string) => {
    handleSearch({
      mood_query: prompt,
      location,
      time_of_day: timeOfDay,
      open_now: true,
    });
  };

  return (
    <div className="app-container">
      {/* Header */}
      <header className="app-header">
        <div className="logo">
          <Sparkles className="logo-icon" size={24} />
          <span>VIBES</span>
        </div>

        <div className="header-controls">
          <button
            className="location-picker"
            onClick={() => setShowLocationPicker(true)}
          >
            <MapPin size={16} />
            <span>{location}</span>
          </button>

          <div className="time-tabs">
            {TIME_OPTIONS.map(opt => (
              <button
                key={opt.id}
                className={`time-tab ${timeOfDay === opt.id ? 'active' : ''}`}
                onClick={() => setTimeOfDay(opt.id)}
              >
                {opt.icon} {opt.label}
              </button>
            ))}
          </div>
        </div>
      </header>

      {/* Local Events Banner — async, independent */}
      <EventsBanner location={location} />

      {/* Search Section */}
      <section className="search-section">
        <VibeDials
          onSearch={handleSearch}
          location={location}
          timeOfDay={timeOfDay}
          isLoading={isLoading}
        />
      </section>

      {/* Results Section */}
      <section className="results-section">
        {!hasSearched && !isLoading && (
          <div className="welcome-screen">
            <h1 className="welcome-title">Find Your Vibe</h1>
            <p className="welcome-subtitle">
              No star ratings. No tourist traps. Just the right place for how you feel.
            </p>
            <div className="welcome-prompts">
              {SAMPLE_PROMPTS.map((prompt, i) => (
                <button
                  key={i}
                  className="welcome-prompt"
                  onClick={() => handlePromptClick(prompt)}
                >
                  <ChevronRight size={16} className="prompt-icon" />
                  <span>{prompt}</span>
                </button>
              ))}
            </div>
          </div>
        )}

        {isLoading && (
          <div className="results-grid">
            {[1, 2, 3, 4, 5, 6].map(i => (
              <div key={i} className="skeleton-card">
                <div className="skeleton-photo" />
                <div className="skeleton-content">
                  <div className="skeleton-line medium" />
                  <div className="skeleton-line short" />
                  <div className="skeleton-line" />
                </div>
              </div>
            ))}
          </div>
        )}

        {error && (
          <div className="error-state">
            <p className="error-message">{error}</p>
            <button
              className="retry-btn"
              onClick={() => setError(null)}
            >
              Try Again
            </button>
          </div>
        )}

        {!isLoading && !error && hasSearched && venues.length === 0 && (
          <div className="empty-state">
            <Search size={64} className="empty-icon" />
            <h3 className="empty-title">No spots found</h3>
            <p className="empty-message">
              Try broadening your search or exploring a different neighborhood.
            </p>
          </div>
        )}

        {!isLoading && !error && venues.length > 0 && (
          <>
            <div className="results-header">
              <span className="results-count">
                {venues.length} spot{venues.length !== 1 ? 's' : ''} matching your vibe
              </span>
              <div className="results-filters">
                <button
                  className={`map-toggle ${showMap ? 'active' : ''}`}
                  onClick={() => setShowMap(!showMap)}
                >
                  <Map size={16} />
                  {showMap ? 'Hide Map' : 'Show Map'}
                </button>
                <button
                  className={`map-toggle ${userLocation ? 'active' : ''}`}
                  onClick={handleLocateMe}
                >
                  <Navigation size={16} />
                  {userLocation ? 'Located' : 'Find Me'}
                </button>
              </div>
            </div>

            {showMap && (
              <VenueMap
                venues={venues}
                selectedVenue={selectedVenue}
                onVenueSelect={setSelectedVenue}
                userLocation={userLocation}
              />
            )}

            <div className="results-grid">
              {venues.map((venue, i) => (
                <VenueCard
                  key={venue.yelp_id || i}
                  venue={venue}
                  isSelected={selectedVenue?.name === venue.name}
                  onClick={() => { setSelectedVenue(venue); setDetailVenue(venue); }}
                />
              ))}
            </div>
          </>
        )}
      </section>

      {/* Venue Detail Panel */}
      <VenueDetailPanel
        venue={detailVenue}
        onClose={() => setDetailVenue(null)}
      />

      {/* Neighborhood Picker Modal */}
      <NeighborhoodPicker
        value={location}
        onChange={setLocation}
        isOpen={showLocationPicker}
        onClose={() => setShowLocationPicker(false)}
      />
    </div>
  );
}
