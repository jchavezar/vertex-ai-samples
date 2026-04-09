interface RadarScores {
  geographic_reach: number;
  source_quality: number;
  temporal_coverage: number;
  perspective_balance: number;
  depth: number;
}

interface Props {
  score: number;
  confidence: string;
  breakdown: Record<string, number>;
  radar: RadarScores;
}

const RADAR_LABELS: Record<string, string> = {
  geographic_reach: "Geographic Reach",
  source_quality: "Source Quality",
  temporal_coverage: "Temporal Coverage",
  perspective_balance: "Perspective Balance",
  depth: "Analysis Depth",
};

export default function VeracityGauge({ score, confidence, radar }: Props) {
  const scoreColor =
    score >= 85 ? "#22c55e" :
    score >= 65 ? "#4ade80" :
    score >= 40 ? "#f59e0b" : "#ef4444";

  const confidenceColor =
    confidence === "high" ? "var(--accent-green)" :
    confidence === "medium" ? "var(--accent-amber)" : "var(--accent-red)";

  // SVG arc for the gauge
  const radius = 60;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (score / 100) * circumference * 0.75; // 270 degree arc
  const rotation = 135; // Start from bottom-left

  return (
    <div
      className="fade-in"
      style={{
        background: "var(--bg-surface)",
        border: "1px solid var(--border)",
        borderRadius: 12,
        padding: 24,
        minWidth: 280,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        gap: 20,
      }}
    >
      {/* Gauge header */}
      <div style={{
        fontSize: 12,
        fontFamily: "var(--font-mono)",
        color: "var(--text-muted)",
        textTransform: "uppercase",
        letterSpacing: 1.5,
      }}>
        Veracity Score
      </div>

      {/* SVG Gauge */}
      <div style={{ position: "relative", width: 160, height: 130 }}>
        <svg viewBox="0 0 160 130" style={{ width: "100%", height: "100%" }}>
          {/* Background arc */}
          <circle
            cx="80"
            cy="80"
            r={radius}
            fill="none"
            stroke="var(--border)"
            strokeWidth="10"
            strokeLinecap="round"
            strokeDasharray={`${circumference * 0.75} ${circumference * 0.25}`}
            transform={`rotate(${rotation} 80 80)`}
          />
          {/* Score arc */}
          <circle
            cx="80"
            cy="80"
            r={radius}
            fill="none"
            stroke={scoreColor}
            strokeWidth="10"
            strokeLinecap="round"
            strokeDasharray={`${circumference * 0.75} ${circumference * 0.25}`}
            strokeDashoffset={strokeDashoffset}
            transform={`rotate(${rotation} 80 80)`}
            style={{ transition: "stroke-dashoffset 1s ease-out, stroke 0.5s" }}
          />
        </svg>
        {/* Center number */}
        <div style={{
          position: "absolute",
          top: "45%",
          left: "50%",
          transform: "translate(-50%, -50%)",
          textAlign: "center",
        }}>
          <div style={{
            fontSize: 40,
            fontWeight: 700,
            fontFamily: "var(--font-mono)",
            color: scoreColor,
            lineHeight: 1,
          }}>
            {score}
          </div>
          <div style={{
            fontSize: 11,
            color: "var(--text-muted)",
            marginTop: 2,
          }}>
            / 100
          </div>
        </div>
      </div>

      {/* Confidence badge */}
      <div style={{
        padding: "4px 14px",
        background: `${confidenceColor}15`,
        border: `1px solid ${confidenceColor}40`,
        borderRadius: 20,
        fontSize: 12,
        fontWeight: 600,
        fontFamily: "var(--font-mono)",
        color: confidenceColor,
        textTransform: "uppercase",
        letterSpacing: 1,
      }}>
        {confidence} confidence
      </div>

      {/* Radar bars */}
      <div style={{ width: "100%", display: "flex", flexDirection: "column", gap: 10 }}>
        <div style={{
          fontSize: 11,
          fontFamily: "var(--font-mono)",
          color: "var(--text-muted)",
          textTransform: "uppercase",
          letterSpacing: 1,
          marginBottom: 4,
        }}>
          Analysis Dimensions
        </div>
        {Object.entries(radar).map(([key, value]) => (
          <div key={key} style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <span style={{
              fontSize: 11,
              color: "var(--text-secondary)",
              width: 130,
              flexShrink: 0,
            }}>
              {RADAR_LABELS[key] || key}
            </span>
            <div style={{
              flex: 1,
              height: 6,
              background: "var(--bg-primary)",
              borderRadius: 3,
              overflow: "hidden",
            }}>
              <div style={{
                width: `${value}%`,
                height: "100%",
                background: `linear-gradient(90deg, var(--accent-blue), var(--accent-cyan))`,
                borderRadius: 3,
                transition: "width 0.8s ease-out",
              }} />
            </div>
            <span style={{
              fontSize: 12,
              fontFamily: "var(--font-mono)",
              color: "var(--accent-cyan)",
              fontWeight: 600,
              width: 28,
              textAlign: "right",
            }}>
              {value}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
