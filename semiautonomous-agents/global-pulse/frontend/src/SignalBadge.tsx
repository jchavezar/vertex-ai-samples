interface Signal {
  type: string;
  confidence: number;
  evidence: string;
  color: string;
  icon: string;
  description?: string;
}

interface Props {
  signals: Signal[];
}

export default function SignalBadge({ signals }: Props) {
  if (!signals.length) return null;

  return (
    <div
      className="fade-in"
      style={{
        display: "flex",
        gap: 10,
        flexWrap: "wrap",
        padding: "0 20px",
      }}
    >
      <span style={{
        fontSize: 12,
        fontFamily: "var(--font-mono)",
        color: "var(--text-muted)",
        textTransform: "uppercase",
        letterSpacing: 1,
        alignSelf: "center",
      }}>
        Signals:
      </span>
      {signals.map((sig) => (
        <div
          key={sig.type}
          title={sig.evidence}
          style={{
            display: "inline-flex",
            alignItems: "center",
            gap: 8,
            padding: "6px 14px",
            background: `${sig.color}15`,
            border: `1px solid ${sig.color}40`,
            borderRadius: 20,
            fontSize: 13,
            fontWeight: 600,
            fontFamily: "var(--font-mono)",
            color: sig.color,
            animation: sig.type === "BREAKING" ? "pulse-glow 2s ease-in-out infinite" : undefined,
          }}
        >
          <span style={{
            width: 8,
            height: 8,
            borderRadius: "50%",
            background: sig.color,
            display: "inline-block",
          }} />
          {sig.type}
          <span style={{
            fontSize: 11,
            color: `${sig.color}aa`,
            fontWeight: 400,
          }}>
            {sig.confidence}%
          </span>
        </div>
      ))}
    </div>
  );
}
