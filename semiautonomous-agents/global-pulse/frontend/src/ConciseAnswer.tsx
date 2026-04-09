interface Metadata {
  total_sources: number;
  countries_covered: number;
  languages: string[];
}

interface Props {
  answer: string;
  metadata: Metadata;
}

export default function ConciseAnswer({ answer, metadata }: Props) {
  const pills = [
    { label: `${metadata.total_sources} sources`, icon: "📰" },
    { label: `${metadata.countries_covered} countries`, icon: "🌍" },
    { label: `${metadata.languages.length} languages`, icon: "🗣️" },
  ];

  return (
    <div
      className="fade-in"
      style={{
        background: "var(--bg-surface)",
        border: "1px solid var(--border)",
        borderLeft: "4px solid var(--accent-cyan)",
        borderRadius: 12,
        padding: 24,
        flex: 1,
      }}
    >
      <div style={{
        fontSize: 12,
        fontFamily: "var(--font-mono)",
        color: "var(--accent-cyan)",
        textTransform: "uppercase",
        letterSpacing: 1.5,
        marginBottom: 12,
      }}>
        Intelligence Summary
      </div>
      <p style={{
        fontSize: 17,
        lineHeight: 1.7,
        color: "var(--text-primary)",
      }}>
        {answer}
      </p>
      <div style={{
        display: "flex",
        gap: 12,
        marginTop: 16,
        flexWrap: "wrap",
      }}>
        {pills.map((p) => (
          <span
            key={p.label}
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: 6,
              padding: "4px 12px",
              background: "var(--bg-elevated)",
              border: "1px solid var(--border)",
              borderRadius: 20,
              fontSize: 13,
              color: "var(--text-secondary)",
              fontFamily: "var(--font-mono)",
            }}
          >
            {p.icon} {p.label}
          </span>
        ))}
      </div>
    </div>
  );
}
