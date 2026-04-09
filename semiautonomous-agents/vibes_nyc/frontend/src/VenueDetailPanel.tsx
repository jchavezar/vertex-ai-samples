import { useEffect, useState } from 'react';
import { X, ExternalLink, Clock, Info } from 'lucide-react';
import { VenueResult } from './VenueCard';
import ExplainerOverlay from './ExplainerOverlay';

interface RadarScores {
  energy: number;
  sound: number;
  aesthetic: number;
  crowd: number;
  accessibility: number;
}

interface Archetype {
  emoji: string;
  title: string;
  description: string;
}

interface Signal {
  source: string;
  quote: string;
  score: string;
  url?: string;
  real?: boolean;
  platform?: 'reddit' | 'instagram';
  username?: string;
  verified?: boolean;
}

interface DeepVibe {
  radar: RadarScores;
  archetypes: Archetype[];
  neighborhood_signals: Signal[];
  signals_source?: 'live' | 'none';
  provenance?: Record<string, string>;
}

interface Props {
  venue: VenueResult | null;
  onClose: () => void;
}

// ─── Radar Chart ────────────────────────────────────────────────────────────

const AXES = [
  { key: 'energy',        label: 'Energy',       sublabel: 'calm → electric' },
  { key: 'sound',         label: 'Sound',        sublabel: 'silent → live'   },
  { key: 'aesthetic',     label: 'Aesthetic',    sublabel: 'bare → curated'  },
  { key: 'crowd',         label: 'Crowd',        sublabel: 'locals → scene'  },
  { key: 'accessibility', label: 'Walk-in',      sublabel: 'impossible → any time' },
];

const CX = 130, CY = 130, MAX_R = 95;
const N = AXES.length;

function axisPoint(i: number, r: number): [number, number] {
  const angle = (2 * Math.PI * i) / N - Math.PI / 2;
  return [CX + r * Math.cos(angle), CY + r * Math.sin(angle)];
}

function toPoints(scores: RadarScores): string {
  return AXES.map((ax, i) => {
    const v = (scores[ax.key as keyof RadarScores] ?? 50) / 100;
    const [x, y] = axisPoint(i, MAX_R * v);
    return `${x},${y}`;
  }).join(' ');
}

function GridPolygon({ fraction }: { fraction: number }) {
  const pts = Array.from({ length: N }, (_, i) => {
    const [x, y] = axisPoint(i, MAX_R * fraction);
    return `${x},${y}`;
  }).join(' ');
  return <polygon points={pts} fill="none" stroke="rgba(255,255,255,0.07)" strokeWidth="1" />;
}

function RadarChart({ scores }: { scores: RadarScores }) {
  return (
    <svg viewBox="0 0 260 260" className="radar-svg">
      {/* Grid */}
      {[0.2, 0.4, 0.6, 0.8, 1].map(f => <GridPolygon key={f} fraction={f} />)}
      {/* Axis lines */}
      {AXES.map((_, i) => {
        const [x, y] = axisPoint(i, MAX_R);
        return <line key={i} x1={CX} y1={CY} x2={x} y2={y} stroke="rgba(255,255,255,0.07)" strokeWidth="1" />;
      })}
      {/* Filled area */}
      <polygon
        points={toPoints(scores)}
        fill="rgba(245,158,11,0.18)"
        stroke="#F59E0B"
        strokeWidth="2"
        strokeLinejoin="round"
      />
      {/* Axis dots */}
      {AXES.map((ax, i) => {
        const v = (scores[ax.key as keyof RadarScores] ?? 50) / 100;
        const [x, y] = axisPoint(i, MAX_R * v);
        return <circle key={i} cx={x} cy={y} r="4" fill="#F59E0B" />;
      })}
      {/* Labels */}
      {AXES.map((ax, i) => {
        const [lx, ly] = axisPoint(i, MAX_R + 20);
        const anchor = lx < CX - 5 ? 'end' : lx > CX + 5 ? 'start' : 'middle';
        return (
          <text key={i} x={lx} y={ly} textAnchor={anchor} fontSize="11" fill="#9CA3AF" fontFamily="Inter, system-ui">
            {ax.label}
          </text>
        );
      })}
    </svg>
  );
}

// ─── Panel ───────────────────────────────────────────────────────────────────

export default function VenueDetailPanel({ venue, onClose }: Props) {
  const [deepVibe, setDeepVibe] = useState<DeepVibe | null>(null);
  const [loading, setLoading] = useState(false);
  const [showExplainer, setShowExplainer] = useState(false);

  useEffect(() => {
    if (!venue) return;
    setDeepVibe(null);
    setLoading(true);

    fetch('/api/venue/deep-vibe', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: venue.name,
        vibe_tags: venue.vibe_tags,
        vibe_summary: venue.vibe_summary,
        underground_score: venue.underground_score,
        categories: venue.categories ?? [],
        reviews: venue.reviews ?? [],
      }),
    })
      .then(r => r.json())
      .then(setDeepVibe)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [venue?.name]);

  // Close on Escape
  useEffect(() => {
    const handler = (e: KeyboardEvent) => { if (e.key === 'Escape') onClose(); };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [onClose]);

  if (!venue) return null;

  return (
    <div className="detail-overlay" onClick={onClose}>
      <div className="detail-panel" onClick={e => e.stopPropagation()}>

        {/* ── Sticky header ── */}
        <div className="detail-panel-header-fixed">
          <div className="detail-header">
            <div className="detail-title-group">
              <h2 className="detail-venue-name">{venue.name}</h2>
              <div className="detail-meta">
                <span className="underground-badge">
                  <span>⬡</span>
                  <span>{venue.underground_score}</span>
                </span>
                <span className="detail-address">{venue.address}</span>
                {venue.url && (
                  <a href={venue.url} target="_blank" rel="noopener noreferrer" className="detail-ext-link">
                    <ExternalLink size={14} /> Maps
                  </a>
                )}
              </div>
            </div>
            <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
              <button className="detail-info-btn" onClick={() => setShowExplainer(true)} title="How it works">
                <Info size={18} />
              </button>
              <button className="detail-close" onClick={onClose}>
                <X size={20} />
              </button>
            </div>
          </div>

          {/* Hours bar */}
          {venue.hours && (
            <div className={`detail-hours-bar ${venue.hours.is_holiday_closure ? 'holiday' : venue.hours.is_open_now ? 'open' : 'closed'}`}>
              {venue.hours.is_holiday_closure ? (
                <>
                  <span className="hours-dot" />
                  <span className="hours-status">{venue.hours.holiday_note ?? 'Closed for holiday'}</span>
                  <span className="hours-divider">·</span>
                  <Clock size={13} />
                  <span className="hours-detail">{venue.hours.display}</span>
                </>
              ) : (
                <>
                  <span className="hours-dot" />
                  <span className="hours-status">{venue.hours.status}</span>
                  {venue.hours.display && (
                    <>
                      <span className="hours-divider">·</span>
                      <Clock size={13} />
                      <span className="hours-detail">{venue.hours.display}</span>
                    </>
                  )}
                </>
              )}
            </div>
          )}

          {/* Vibe summary */}
          {venue.vibe_summary && (
            <p className="detail-summary">{venue.vibe_summary}</p>
          )}
        </div>

        {/* ── Scrollable body ── */}
        <div className="detail-panel-body">
          {loading ? (
            <div className="detail-loading">
              <div className="detail-spinner" />
              <span>Reading the room…</span>
            </div>
          ) : deepVibe ? (
            <div className="detail-content">
              {/* Radar */}
              <div className="detail-section">
                <h3 className="detail-section-title">Vibe Profile</h3>
                <div className="radar-wrapper">
                  <RadarChart scores={deepVibe.radar} />
                  <div className="radar-legend">
                    {AXES.map(ax => (
                      <div key={ax.key} className="radar-legend-row">
                        <span className="radar-legend-label">{ax.label}</span>
                        <div className="radar-bar-track">
                          <div
                            className="radar-bar-fill"
                            style={{ width: `${deepVibe.radar[ax.key as keyof RadarScores]}%` }}
                          />
                        </div>
                        <span className="radar-legend-value">
                          {deepVibe.radar[ax.key as keyof RadarScores]}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Who Goes Here */}
              <div className="detail-section">
                <h3 className="detail-section-title">Who Goes Here</h3>
                <div className="archetypes-list">
                  {deepVibe.archetypes.map((a, i) => (
                    <div key={i} className="archetype-card">
                      <span className="archetype-emoji">{a.emoji}</span>
                      <div>
                        <div className="archetype-title">{a.title}</div>
                        <div className="archetype-desc">{a.description}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Neighborhood Signals */}
              <div className="detail-section">
                <h3 className="detail-section-title">
                  Neighborhood Signals
                  {deepVibe.signals_source === 'live' ? (
                    <span className="detail-section-badge signals-badge-real">Live</span>
                  ) : deepVibe.signals_source === 'none' ? (
                    <span className="detail-section-badge">No signals found</span>
                  ) : null}
                </h3>
                <div className="signals-list">
                  {deepVibe.neighborhood_signals.map((s, i) => (
                    <div key={i} className={`signal-card ${s.platform === 'instagram' ? 'signal-instagram' : ''}`}>
                      <div className="signal-source">
                        {s.url ? (
                          <a href={s.url} target="_blank" rel="noopener noreferrer" className="signal-source-link">
                            {s.platform === 'instagram' ? (s.username || 'instagram') : s.source} ↗
                          </a>
                        ) : (s.platform === 'instagram' ? (s.username || 'instagram') : s.source)}
                        {s.verified && <span className="signal-verified" title="Verified: URL exists and venue name found in text">&#10003;</span>}
                      </div>
                      <blockquote className="signal-quote">"{s.quote}"</blockquote>
                      <div className="signal-score">▲ {s.score}</div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ) : null}
        </div>

      </div>
      {showExplainer && <ExplainerOverlay onClose={() => setShowExplainer(false)} />}
    </div>
  );
}
