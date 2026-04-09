import { MapPin, Check, Clock, AlertCircle, ExternalLink } from 'lucide-react';

export interface VenueHours {
  is_open_now: boolean;
  status: string;           // "Open until 6:00 PM" | "Opens at 7:00 AM" | "Closed today"
  open_until?: string | null;
  is_holiday_closure?: boolean;
  holiday_note?: string | null;
  display?: string;         // "Mon 7:00 AM–6:00 PM  ·  Tue 7:00 AM–6:00 PM  ·  ..."
}

export interface VenueResult {
  name: string;
  yelp_id: string;
  rating: number;
  review_count: number;
  price: string;
  address: string;
  distance?: number;
  photos: string[];
  underground_score: number;
  vibe_tags: string[];
  accessibility: string;
  best_time?: string;
  vibe_summary: string;
  url?: string;
  coordinates?: { latitude: number; longitude: number };
  categories?: string[];
  hours?: VenueHours;
  reviews?: string[];
}

interface VenueCardProps {
  venue: VenueResult;
  onClick?: () => void;
  isSelected?: boolean;
}

// Get emoji for category
function getCategoryEmoji(categories?: string[]): string {
  if (!categories || categories.length === 0) return '🍽️';
  const cat = categories[0].toLowerCase();
  if (cat.includes('coffee') || cat.includes('cafe')) return '☕';
  if (cat.includes('cocktail') || cat.includes('bar')) return '🍸';
  if (cat.includes('wine')) return '🍷';
  if (cat.includes('beer') || cat.includes('brewery')) return '🍺';
  if (cat.includes('bakery') || cat.includes('pastry')) return '🥐';
  if (cat.includes('pizza')) return '🍕';
  if (cat.includes('sushi') || cat.includes('japanese')) return '🍣';
  if (cat.includes('mexican') || cat.includes('taco')) return '🌮';
  if (cat.includes('burger')) return '🍔';
  if (cat.includes('breakfast') || cat.includes('brunch')) return '🥞';
  return '🍽️';
}

// Format distance
function formatDistance(meters?: number): string {
  if (!meters) return '';
  const miles = meters / 1609.34;
  return `${miles.toFixed(1)} mi`;
}

export default function VenueCard({ venue, onClick, isSelected }: VenueCardProps) {
  const hasPhoto = venue.photos && venue.photos.length > 0 && venue.photos[0];

  const accessibilityConfig: Record<string, { icon: React.ReactNode; className: string }> = {
    'walk-in': { icon: <Check size={14} />, className: 'walk-in' },
    'usually available': { icon: <Check size={14} />, className: 'walk-in' },
    'book ahead': { icon: <Clock size={14} />, className: 'book-ahead' },
    'impossible to get in': { icon: <AlertCircle size={14} />, className: 'impossible' },
  };

  const accessConfig = accessibilityConfig[venue.accessibility] || accessibilityConfig['walk-in'];

  return (
    <div className={`venue-card ${isSelected ? 'selected' : ''}`} onClick={onClick}>
      {hasPhoto ? (
        <img
          src={venue.photos[0]}
          alt={venue.name}
          className="venue-photo"
          loading="lazy"
        />
      ) : (
        <div className="venue-photo-placeholder">
          {getCategoryEmoji(venue.categories)}
        </div>
      )}

      <div className="venue-content">
        <div className="venue-header">
          <h3 className="venue-name">{venue.name}</h3>
          <div className="underground-badge">
            <span>⬡</span>
            <span>{venue.underground_score}</span>
          </div>
        </div>

        <div className="vibe-tags">
          {venue.vibe_tags.slice(0, 4).map((tag, i) => (
            <span key={i} className="vibe-tag">{tag}</span>
          ))}
        </div>

        <div className="venue-meta">
          <div className={`accessibility-badge ${accessConfig.className}`}>
            {accessConfig.icon}
            <span>{venue.accessibility}</span>
          </div>
          {venue.price && <span>{venue.price}</span>}
        </div>

        {venue.vibe_summary && (
          <p className="venue-summary">{venue.vibe_summary}</p>
        )}

        <div className="venue-footer">
          <div className="venue-distance">
            <MapPin size={14} style={{ display: 'inline', marginRight: 4, verticalAlign: 'middle' }} />
            {formatDistance(venue.distance) || venue.address.split(',')[0]}
          </div>
          {venue.best_time && (
            <div className="venue-best-time">Best: {venue.best_time}</div>
          )}
          {venue.url && (
            <a
              href={venue.url}
              target="_blank"
              rel="noopener noreferrer"
              onClick={(e) => e.stopPropagation()}
              style={{ color: 'var(--text-muted)' }}
            >
              <ExternalLink size={16} />
            </a>
          )}
        </div>
      </div>
    </div>
  );
}
