import { useEffect, useState } from 'react';
import { ExternalLink } from 'lucide-react';

interface LocalEvent {
  name: string;
  date: string;
  time?: string | null;
  venue: string;
  neighborhood: string;
  description: string;
  category: string;
  url?: string | null;
  source?: string;
}

const CATEGORY_EMOJI: Record<string, string> = {
  art: '🎨',
  food: '🍽️',
  music: '🎵',
  community: '🤝',
  film: '🎬',
  'pop-up': '✨',
};

function EventCard({ event }: { event: LocalEvent }) {
  const emoji = CATEGORY_EMOJI[event.category] ?? '📍';

  const inner = (
    <div className="event-card">
      <div className="event-card-top">
        <span className="event-emoji">{emoji}</span>
        <span className="event-category">{event.category}</span>
      </div>
      <div className="event-card-name">{event.name}</div>
      <div className="event-card-meta">
        <span>{event.date}</span>
        {event.time && <span> · {event.time}</span>}
      </div>
      <div className="event-card-venue">{event.venue}</div>
      <div className="event-card-desc">{event.description}</div>
      {event.url && (
        <div className="event-card-link">
          <ExternalLink size={12} />
          <span>{event.source ?? 'Details'}</span>
        </div>
      )}
    </div>
  );

  if (event.url) {
    return (
      <a href={event.url} target="_blank" rel="noopener noreferrer" className="event-card-anchor">
        {inner}
      </a>
    );
  }
  return inner;
}

function ShimmerCards() {
  return (
    <div className="events-scroll">
      {[1, 2, 3, 4].map(i => (
        <div key={i} className="event-card event-shimmer">
          <div className="shimmer-line short" />
          <div className="shimmer-line medium" />
          <div className="shimmer-line" />
          <div className="shimmer-line short" />
        </div>
      ))}
    </div>
  );
}

export default function EventsBanner({ location }: { location: string }) {
  const [events, setEvents] = useState<LocalEvent[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    fetch(`/api/events?location=${encodeURIComponent(location)}`)
      .then(r => r.json())
      .then(data => setEvents(data.events ?? []))
      .catch(() => setEvents([]))
      .finally(() => setLoading(false));
  }, [location]);

  // Hide entirely if nothing to show
  if (!loading && events.length === 0) return null;

  return (
    <div className="events-banner">
      <div className="events-banner-header">
        <span className="events-banner-title">Happening Nearby</span>
        <span className="events-banner-subtitle">Next 5 days</span>
      </div>
      {loading ? (
        <ShimmerCards />
      ) : (
        <div className="events-scroll">
          {events.map((e, i) => (
            <EventCard key={i} event={e} />
          ))}
        </div>
      )}
    </div>
  );
}
