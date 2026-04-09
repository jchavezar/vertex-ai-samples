import { ChevronDown, ChevronUp, FileText } from "lucide-react";
import Markdown from "react-markdown";

interface Props {
  report: string;
  isExpanded: boolean;
  onToggle: () => void;
}

export default function ReportPanel({ report, isExpanded, onToggle }: Props) {
  return (
    <div
      className="fade-in"
      style={{
        background: "var(--bg-surface)",
        border: "1px solid var(--border)",
        borderRadius: 12,
        overflow: "hidden",
      }}
    >
      {/* Header / Toggle */}
      <button
        onClick={onToggle}
        style={{
          display: "flex",
          alignItems: "center",
          gap: 10,
          width: "100%",
          padding: "18px 24px",
          background: "transparent",
          border: "none",
          borderBottom: isExpanded ? "1px solid var(--border)" : "none",
          color: "var(--text-primary)",
          cursor: "pointer",
          fontSize: 15,
          fontWeight: 600,
          fontFamily: "var(--font-sans)",
          textAlign: "left",
        }}
      >
        <FileText size={18} color="var(--accent-cyan)" />
        Full Intelligence Report
        <span style={{ marginLeft: "auto" }}>
          {isExpanded ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
        </span>
      </button>

      {/* Report content */}
      {isExpanded && (
        <div
          className="slide-up"
          style={{
            padding: "24px 32px",
            maxHeight: 600,
            overflowY: "auto",
          }}
        >
          <Markdown
            components={{
              h1: ({ children }) => (
                <h1 style={{ fontSize: 22, fontWeight: 700, color: "var(--accent-cyan)", margin: "24px 0 12px" }}>{children}</h1>
              ),
              h2: ({ children }) => (
                <h2 style={{ fontSize: 18, fontWeight: 600, color: "var(--accent-cyan)", margin: "20px 0 10px", borderBottom: "1px solid var(--border)", paddingBottom: 6 }}>{children}</h2>
              ),
              h3: ({ children }) => (
                <h3 style={{ fontSize: 15, fontWeight: 600, color: "var(--text-primary)", margin: "16px 0 8px" }}>{children}</h3>
              ),
              p: ({ children }) => (
                <p style={{ fontSize: 14, lineHeight: 1.7, color: "var(--text-secondary)", margin: "8px 0" }}>{children}</p>
              ),
              ul: ({ children }) => (
                <ul style={{ paddingLeft: 20, margin: "8px 0" }}>{children}</ul>
              ),
              li: ({ children }) => (
                <li style={{ fontSize: 14, lineHeight: 1.7, color: "var(--text-secondary)", marginBottom: 4 }}>{children}</li>
              ),
              strong: ({ children }) => (
                <strong style={{ color: "var(--text-primary)", fontWeight: 600 }}>{children}</strong>
              ),
              blockquote: ({ children }) => (
                <blockquote style={{
                  borderLeft: "3px solid var(--accent-cyan)",
                  paddingLeft: 16,
                  margin: "12px 0",
                  color: "var(--text-secondary)",
                  fontStyle: "italic",
                }}>{children}</blockquote>
              ),
            }}
          >
            {report}
          </Markdown>
        </div>
      )}
    </div>
  );
}
