import { useState, useCallback } from "react";
import { Radio } from "lucide-react";
import SearchBar from "./SearchBar";
import ConciseAnswer from "./ConciseAnswer";
import VeracityGauge from "./VeracityGauge";
import SignalBadge from "./SignalBadge";
import SourceCard from "./SourceCard";
import ReportPanel from "./ReportPanel";
import SourceMap from "./SourceMap";

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

interface Signal {
  type: string;
  confidence: number;
  evidence: string;
  color: string;
  icon: string;
}

interface InvestigationResult {
  query: string;
  concise_answer: string;
  report: string;
  sources: Source[];
  veracity: {
    score: number;
    confidence: string;
    breakdown: Record<string, number>;
    bias_distribution: Record<string, number>;
  };
  radar: {
    geographic_reach: number;
    source_quality: number;
    temporal_coverage: number;
    perspective_balance: number;
    depth: number;
  };
  signals: Signal[];
  metadata: {
    total_sources: number;
    countries_covered: number;
    languages: string[];
    search_iterations: number;
  };
}

const LOADING_MESSAGES = [
  "Searching international sources...",
  "Scanning Reuters, BBC, NHK, Al Jazeera...",
  "Translating non-English sources...",
  "Cross-referencing 15+ outlets...",
  "Analyzing source veracity...",
  "Computing bias distribution...",
  "Generating intelligence report...",
];

export default function App() {
  const [result, setResult] = useState<InvestigationResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [reportExpanded, setReportExpanded] = useState(false);
  const [loadingMsg, setLoadingMsg] = useState(LOADING_MESSAGES[0]);

  const handleSearch = useCallback(async (query: string) => {
    setIsLoading(true);
    setError(null);
    setResult(null);
    setReportExpanded(false);

    // Cycle loading messages
    let msgIdx = 0;
    const msgInterval = setInterval(() => {
      msgIdx = (msgIdx + 1) % LOADING_MESSAGES.length;
      setLoadingMsg(LOADING_MESSAGES[msgIdx]);
    }, 2500);

    try {
      const resp = await fetch("/api/investigate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query, max_iterations: 3 }),
      });
      if (!resp.ok) throw new Error(`Server error: ${resp.status}`);
      const data: InvestigationResult = await resp.json();
      setResult(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Investigation failed");
    } finally {
      clearInterval(msgInterval);
      setIsLoading(false);
    }
  }, []);

  return (
    <div style={{ minHeight: "100vh", display: "flex", flexDirection: "column" }}>
      {/* Header */}
      <header style={{
        padding: "24px 32px 20px",
        borderBottom: "1px solid var(--border)",
        background: "var(--bg-surface)",
      }}>
        <div style={{ maxWidth: 1200, margin: "0 auto", display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: 12 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
            <div style={{
              width: 10,
              height: 10,
              borderRadius: "50%",
              background: "var(--accent-cyan)",
              animation: "pulse-glow 2s ease-in-out infinite",
            }} />
            <h1 style={{
              fontSize: 22,
              fontWeight: 700,
              letterSpacing: 2,
              background: "linear-gradient(135deg, var(--accent-cyan), var(--accent-blue))",
              WebkitBackgroundClip: "text",
              WebkitTextFillColor: "transparent",
            }}>
              GLOBAL PULSE
            </h1>
            <span style={{ fontSize: 13, color: "var(--text-muted)", marginLeft: 4 }}>
              International News Intelligence
            </span>
          </div>

          {/* Stats bar */}
          {result && (
            <div style={{ display: "flex", gap: 16, fontSize: 12, fontFamily: "var(--font-mono)", color: "var(--text-secondary)" }}>
              <span><Radio size={12} style={{ marginRight: 4 }} />{result.metadata.total_sources} sources</span>
              <span>{result.metadata.countries_covered} countries</span>
              <span>{result.metadata.languages.length} languages</span>
            </div>
          )}
        </div>
      </header>

      {/* Main content */}
      <main style={{ flex: 1, maxWidth: 1200, margin: "0 auto", width: "100%", padding: "32px 20px" }}>
        {/* Search */}
        <div style={{ marginBottom: result ? 32 : 120, transition: "margin 0.3s" }}>
          {!result && !isLoading && (
            <div style={{ textAlign: "center", marginBottom: 40 }}>
              <h2 style={{ fontSize: 32, fontWeight: 300, color: "var(--text-primary)", marginBottom: 8 }}>
                What's happening in the world?
              </h2>
              <p style={{ fontSize: 16, color: "var(--text-secondary)" }}>
                Ask any question. We'll search 15+ international sources across multiple languages.
              </p>
            </div>
          )}
          <SearchBar onSearch={handleSearch} isLoading={isLoading} />
        </div>

        {/* Loading */}
        {isLoading && (
          <div style={{ textAlign: "center", padding: "60px 0" }}>
            <div style={{
              width: 48,
              height: 48,
              margin: "0 auto 20px",
              border: "3px solid var(--border)",
              borderTop: "3px solid var(--accent-cyan)",
              borderRadius: "50%",
              animation: "spin 1s linear infinite",
            }} />
            <p style={{
              fontSize: 15,
              color: "var(--accent-cyan)",
              fontFamily: "var(--font-mono)",
              animation: "fade-in 0.3s ease-out",
            }}>
              {loadingMsg}
            </p>
            <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
          </div>
        )}

        {/* Error */}
        {error && (
          <div style={{
            textAlign: "center",
            padding: 24,
            background: "var(--accent-red)10",
            border: "1px solid var(--accent-red)30",
            borderRadius: 12,
            color: "var(--accent-red)",
            fontSize: 15,
          }}>
            {error}
          </div>
        )}

        {/* Results */}
        {result && (
          <div style={{ display: "flex", flexDirection: "column", gap: 24 }}>
            {/* Top row: Answer + Gauge */}
            <div style={{ display: "flex", gap: 20, flexWrap: "wrap" }}>
              <div style={{ flex: "1 1 500px", minWidth: 0 }}>
                <ConciseAnswer answer={result.concise_answer} metadata={result.metadata} />
              </div>
              <div style={{ flex: "0 0 auto" }}>
                <VeracityGauge
                  score={result.veracity.score}
                  confidence={result.veracity.confidence}
                  breakdown={result.veracity.breakdown}
                  radar={result.radar}
                />
              </div>
            </div>

            {/* Signals */}
            <SignalBadge signals={result.signals} />

            {/* Source Map */}
            <div>
              <div style={{
                fontSize: 12,
                fontFamily: "var(--font-mono)",
                color: "var(--text-muted)",
                textTransform: "uppercase",
                letterSpacing: 1.5,
                marginBottom: 10,
                paddingLeft: 4,
              }}>
                Source Origins
              </div>
              <SourceMap sources={result.sources} />
            </div>

            {/* Source grid */}
            <div>
              <div style={{
                fontSize: 12,
                fontFamily: "var(--font-mono)",
                color: "var(--text-muted)",
                textTransform: "uppercase",
                letterSpacing: 1.5,
                marginBottom: 12,
                paddingLeft: 4,
              }}>
                {result.sources.length} International Sources
              </div>
              <div style={{
                display: "grid",
                gridTemplateColumns: "repeat(auto-fill, minmax(340px, 1fr))",
                gap: 16,
              }}>
                {result.sources.map((source, i) => (
                  <SourceCard key={`${source.source_name}-${i}`} source={source} index={i} />
                ))}
              </div>
            </div>

            {/* Full report */}
            <ReportPanel
              report={result.report}
              isExpanded={reportExpanded}
              onToggle={() => setReportExpanded(!reportExpanded)}
            />
          </div>
        )}
      </main>

      {/* Footer */}
      <footer style={{
        padding: "16px 32px",
        borderTop: "1px solid var(--border)",
        textAlign: "center",
        fontSize: 12,
        color: "var(--text-muted)",
        fontFamily: "var(--font-mono)",
      }}>
        Global Pulse — Impartial International News Intelligence — Powered by Gemini + Google Search
      </footer>
    </div>
  );
}
