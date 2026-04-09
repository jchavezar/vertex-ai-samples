import { useState } from "react";
import { Globe, Search, Loader2 } from "lucide-react";

interface Props {
  onSearch: (query: string) => void;
  isLoading: boolean;
}

const EXAMPLES = [
  "EU AI regulation impact worldwide",
  "Climate summit outcomes and commitments",
  "Global semiconductor supply chain disruptions",
  "Central bank interest rate decisions",
  "International space exploration milestones",
  "Global pandemic preparedness efforts",
];

export default function SearchBar({ onSearch, isLoading }: Props) {
  const [query, setQuery] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim() && !isLoading) onSearch(query.trim());
  };

  return (
    <div style={{ maxWidth: 720, margin: "0 auto", padding: "0 20px" }}>
      <form onSubmit={handleSubmit} style={{
        display: "flex",
        gap: 0,
        background: "var(--bg-surface)",
        border: "1px solid var(--border)",
        borderRadius: 16,
        overflow: "hidden",
        transition: "border-color 0.2s",
      }}>
        <div style={{
          display: "flex",
          alignItems: "center",
          paddingLeft: 20,
          color: "var(--accent-cyan)",
        }}>
          <Globe size={22} />
        </div>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Ask about any global topic..."
          disabled={isLoading}
          style={{
            flex: 1,
            padding: "18px 16px",
            background: "transparent",
            border: "none",
            outline: "none",
            color: "var(--text-primary)",
            fontSize: 16,
            fontFamily: "var(--font-sans)",
          }}
        />
        <button
          type="submit"
          disabled={isLoading || !query.trim()}
          style={{
            display: "flex",
            alignItems: "center",
            gap: 8,
            padding: "0 24px",
            background: isLoading ? "var(--border)" : "var(--accent-cyan)",
            border: "none",
            color: isLoading ? "var(--text-secondary)" : "#0a0e1a",
            fontWeight: 600,
            fontSize: 15,
            cursor: isLoading ? "not-allowed" : "pointer",
            transition: "background 0.2s",
          }}
        >
          {isLoading ? <Loader2 size={18} className="spin" /> : <Search size={18} />}
          {isLoading ? "Searching..." : "Investigate"}
        </button>
      </form>

      <div style={{
        display: "flex",
        flexWrap: "wrap",
        gap: 8,
        justifyContent: "center",
        marginTop: 16,
      }}>
        {EXAMPLES.map((ex) => (
          <button
            key={ex}
            onClick={() => { setQuery(ex); if (!isLoading) onSearch(ex); }}
            disabled={isLoading}
            style={{
              padding: "6px 14px",
              background: "var(--bg-elevated)",
              border: "1px solid var(--border)",
              borderRadius: 20,
              color: "var(--text-secondary)",
              fontSize: 13,
              cursor: isLoading ? "not-allowed" : "pointer",
              transition: "all 0.2s",
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.borderColor = "var(--accent-cyan)";
              e.currentTarget.style.color = "var(--accent-cyan)";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.borderColor = "var(--border)";
              e.currentTarget.style.color = "var(--text-secondary)";
            }}
          >
            {ex}
          </button>
        ))}
      </div>

      <style>{`
        @keyframes spin { to { transform: rotate(360deg); } }
        .spin { animation: spin 1s linear infinite; }
      `}</style>
    </div>
  );
}
