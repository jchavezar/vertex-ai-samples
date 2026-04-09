interface Source {
  source_name: string;
  country: string;
  country_code: string;
  flag: string;
  language_original: string;
  headline: string;
  summary: string;
  url: string;
  image_url: string | null;
  published_date: string;
  signal_type: string;
  tier: number;
  trust_score: number;
  bias: string;
}

interface Props {
  source: Source;
  index: number;
}

const SIGNAL_COLORS: Record<string, string> = {
  BREAKING: "#ef4444",
  DEVELOPING: "#f59e0b",
  CONFIRMED: "#22c55e",
  DISPUTED: "#f97316",
  ANALYSIS: "#8b5cf6",
  RETRACTED: "#6b7280",
};

const TIER_META: Record<number, { label: string; color: string }> = {
  1: { label: "T1", color: "#f59e0b" },
  2: { label: "T2", color: "#94a3b8" },
  3: { label: "T3", color: "#b45309" },
};

export default function SourceCard({ source, index }: Props) {
  const sigColor = SIGNAL_COLORS[source.signal_type] || "#8b5cf6";
  const tierMeta = TIER_META[source.tier] || TIER_META[2];
  const trustColor =
    source.trust_score >= 75 ? "var(--accent-green)" :
    source.trust_score >= 50 ? "var(--accent-amber)" : "var(--accent-red)";

  return (
    <a
      href={source.url}
      target="_blank"
      rel="noopener noreferrer"
      className="slide-up"
      style={{
        animationDelay: `${index * 60}ms`,
        display: "block",
        background: "var(--bg-surface)",
        border: "1px solid var(--border)",
        borderRadius: 12,
        padding: 20,
        textDecoration: "none",
        color: "inherit",
        transition: "all 0.25s ease",
        cursor: "pointer",
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.borderColor = "var(--accent-cyan)";
        e.currentTarget.style.transform = "translateY(-2px)";
        e.currentTarget.style.boxShadow = "0 8px 24px rgba(0,212,255,0.08)";
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.borderColor = "var(--border)";
        e.currentTarget.style.transform = "translateY(0)";
        e.currentTarget.style.boxShadow = "none";
      }}
    >
      {/* Header: Flag + Source + Country */}
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 10 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <span style={{ fontSize: 20 }}>{source.flag}</span>
          <span style={{ fontWeight: 600, fontSize: 14, color: "var(--text-primary)" }}>
            {source.source_name}
          </span>
          <span style={{ fontSize: 12, color: "var(--text-muted)" }}>
            {source.country}
          </span>
        </div>
        <span style={{
          fontSize: 10,
          fontFamily: "var(--font-mono)",
          fontWeight: 700,
          padding: "2px 6px",
          borderRadius: 4,
          background: `${tierMeta.color}20`,
          color: tierMeta.color,
          border: `1px solid ${tierMeta.color}40`,
        }}>
          {tierMeta.label}
        </span>
      </div>

      {/* Signal badge */}
      <div style={{
        display: "inline-flex",
        alignItems: "center",
        gap: 6,
        marginBottom: 8,
        padding: "3px 10px",
        background: `${sigColor}15`,
        borderRadius: 12,
        fontSize: 11,
        fontWeight: 600,
        fontFamily: "var(--font-mono)",
        color: sigColor,
      }}>
        <span style={{ width: 6, height: 6, borderRadius: "50%", background: sigColor }} />
        {source.signal_type}
      </div>

      {/* Language tag */}
      {source.language_original !== "English" && (
        <span style={{
          marginLeft: 8,
          fontSize: 11,
          color: "var(--accent-blue)",
          fontFamily: "var(--font-mono)",
        }}>
          Translated from {source.language_original}
        </span>
      )}

      {/* Headline */}
      <h3 style={{
        fontSize: 15,
        fontWeight: 600,
        lineHeight: 1.4,
        color: "var(--text-primary)",
        marginBottom: 8,
      }}>
        {source.headline}
      </h3>

      {/* Summary */}
      <p style={{
        fontSize: 13,
        lineHeight: 1.6,
        color: "var(--text-secondary)",
        marginBottom: 14,
        display: "-webkit-box",
        WebkitLineClamp: 3,
        WebkitBoxOrient: "vertical",
        overflow: "hidden",
      }}>
        {source.summary}
      </p>

      {/* Bottom bar: Trust + Bias + Date */}
      <div style={{ display: "flex", alignItems: "center", gap: 12, flexWrap: "wrap" }}>
        {/* Trust bar */}
        <div style={{ display: "flex", alignItems: "center", gap: 6, flex: 1, minWidth: 120 }}>
          <span style={{ fontSize: 11, color: "var(--text-muted)", fontFamily: "var(--font-mono)" }}>Trust</span>
          <div style={{ flex: 1, height: 4, background: "var(--bg-primary)", borderRadius: 2, overflow: "hidden" }}>
            <div style={{ width: `${source.trust_score}%`, height: "100%", background: trustColor, borderRadius: 2 }} />
          </div>
          <span style={{ fontSize: 11, fontFamily: "var(--font-mono)", color: trustColor, fontWeight: 600 }}>
            {source.trust_score}
          </span>
        </div>

        {/* Bias pill */}
        <span style={{
          fontSize: 11,
          padding: "2px 8px",
          background: "var(--bg-elevated)",
          border: "1px solid var(--border)",
          borderRadius: 10,
          color: "var(--text-muted)",
          fontFamily: "var(--font-mono)",
        }}>
          {source.bias}
        </span>

        {/* Date */}
        <span style={{ fontSize: 11, color: "var(--text-muted)", fontFamily: "var(--font-mono)" }}>
          {source.published_date}
        </span>
      </div>
    </a>
  );
}
