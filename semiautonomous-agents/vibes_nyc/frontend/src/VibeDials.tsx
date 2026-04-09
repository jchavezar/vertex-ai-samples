import { useState } from 'react';
import { ChevronDown, ChevronUp } from 'lucide-react';

export interface SearchParams {
  mood_query: string;
  location: string;
  time_of_day: string;
  open_now: boolean;
  vibe_dims?: Record<string, number>;
}

interface VibeDialsProps {
  onSearch: (params: SearchParams) => void;
  location: string;
  timeOfDay: string;
  isLoading: boolean;
}

const DIAL_CONFIG = [
  { id: 'energy', label: 'Energy', left: 'Calm', right: 'Buzzing' },
  { id: 'accessibility', label: 'Accessibility', left: 'Walk-in', right: 'Book ahead' },
  { id: 'crowd', label: 'Crowd vibe', left: 'Locals', right: 'Scene' },
  { id: 'aesthetic', label: 'Aesthetic', left: 'Minimal', right: 'Eclectic' },
  { id: 'sound', label: 'Sound', left: 'Silent', right: 'Live' },
];

export default function VibeDials({ onSearch, location, timeOfDay, isLoading }: VibeDialsProps) {
  const [moodQuery, setMoodQuery] = useState('');
  const [showDials, setShowDials] = useState(false);
  const [sliders, setSliders] = useState<Record<string, number>>({
    energy: 30,
    accessibility: 20,
    crowd: 40,
    aesthetic: 50,
    sound: 30,
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!moodQuery.trim()) return;

    onSearch({
      mood_query: moodQuery,
      location,
      time_of_day: timeOfDay,
      open_now: true,
      vibe_dims: sliders,
    });
  };

  const handleSliderChange = (id: string, value: number) => {
    setSliders(prev => ({ ...prev, [id]: value }));
  };

  return (
    <form onSubmit={handleSubmit} className="search-container">
      <div className="search-input-wrapper">
        <input
          type="text"
          className="search-input"
          placeholder="Describe your vibe... cozy, contemporary, good coffee, interesting crowd"
          value={moodQuery}
          onChange={(e) => setMoodQuery(e.target.value)}
        />
        <button
          type="submit"
          className="search-btn"
          disabled={!moodQuery.trim() || isLoading}
        >
          {isLoading ? 'Searching...' : 'Search'}
        </button>
      </div>

      <div className="vibe-dials">
        <button
          type="button"
          className="dials-toggle"
          onClick={() => setShowDials(!showDials)}
        >
          {showDials ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
          <span>Or dial it in</span>
        </button>

        {showDials && (
          <div className="dials-content">
            {DIAL_CONFIG.map(dial => (
              <div key={dial.id} className="dial-row">
                <span className="dial-label">{dial.label}</span>
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={sliders[dial.id]}
                  onChange={(e) => handleSliderChange(dial.id, parseInt(e.target.value))}
                  className="dial-slider"
                />
                <div className="dial-labels">
                  <span>{dial.left}</span>
                  <span>{dial.right}</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </form>
  );
}
