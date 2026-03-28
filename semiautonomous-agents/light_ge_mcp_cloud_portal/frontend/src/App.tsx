import { useState, useRef, useEffect } from "react";
import { useMsal, useIsAuthenticated } from "@azure/msal-react";
import { loginRequest } from "./authConfig";
import { exchangeTokenForGcp, createSession, queryStream } from "./agentService";
import ReactMarkdown from "react-markdown";

interface Message {
  role: "user" | "assistant";
  content: string;
  latencyMs?: number;
  status?: string;
}

function App() {
  const { instance, accounts } = useMsal();
  const isAuthenticated = useIsAuthenticated();

  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [gcpToken, setGcpToken] = useState<string | null>(null);
  const [entraToken, setEntraToken] = useState<string | null>(null);

  // Timer state
  const [elapsedMs, setElapsedMs] = useState(0);
  const [currentStatus, setCurrentStatus] = useState("");
  const timerRef = useRef<number | null>(null);
  const startTimeRef = useRef<number>(0);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Timer effect
  useEffect(() => {
    if (loading) {
      startTimeRef.current = Date.now();
      timerRef.current = window.setInterval(() => {
        setElapsedMs(Date.now() - startTimeRef.current);
      }, 10); // Update every 10ms for smooth display
    } else {
      if (timerRef.current) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }
    }
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [loading]);

  // Login handler
  const handleLogin = async () => {
    try {
      setError(null);
      const response = await instance.loginPopup(loginRequest);
      console.log("MSAL login successful:", response.account?.username);

      // Get ID token for ServiceNow
      const idToken = response.idToken;
      setEntraToken(idToken);
      console.log("Got Entra ID token");

      // Exchange for GCP token
      console.log("Exchanging for GCP token...");
      const gcpAccessToken = await exchangeTokenForGcp(idToken);
      setGcpToken(gcpAccessToken);
      console.log("Got GCP token");

      // Create Agent Engine session - pass JWT for Discovery Engine WIF exchange
      console.log("Creating Agent Engine session...");
      const session = await createSession(
        gcpAccessToken,
        response.account?.username || "user",
        idToken  // Pass Entra ID JWT - agent will exchange via STS for Discovery Engine
      );
      setSessionId(session);
      console.log("Session created:", session);

      setMessages([
        {
          role: "assistant",
          content: `Welcome, ${response.account?.name}! I'm your Cloud Portal assistant. I can help you:\n\n- **Search documents** in SharePoint (financial reports, policies, etc.)\n- **Manage ServiceNow** tickets, incidents, and requests\n\nHow can I help you today?`,
        },
      ]);
    } catch (err) {
      console.error("Login error:", err);
      setError(err instanceof Error ? err.message : "Login failed");
    }
  };

  // Logout handler
  const handleLogout = () => {
    instance.logoutPopup();
    setSessionId(null);
    setGcpToken(null);
    setEntraToken(null);
    setMessages([]);
  };

  // Send message handler with streaming
  const handleSend = async () => {
    if (!input.trim() || !gcpToken || !sessionId) return;

    const userMessage = input.trim();
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: userMessage }]);
    setLoading(true);
    setError(null);
    setCurrentStatus("Classifying intent...");
    setElapsedMs(0);

    // Add placeholder for assistant response
    const assistantMsgIndex = messages.length + 1;
    setMessages((prev) => [...prev, { role: "assistant", content: "", status: "thinking" }]);

    const queryStartTime = Date.now();

    try {
      // Stream chunks and update UI progressively
      let lastContent = "";
      for await (const chunk of queryStream(
        gcpToken,
        sessionId,
        accounts[0]?.username || "user",
        userMessage
      )) {
        lastContent = chunk;

        // Update status based on content patterns
        if (chunk.includes("ServiceNow") || chunk.includes("ticket") || chunk.includes("incident")) {
          setCurrentStatus("Querying ServiceNow...");
        } else if (chunk.includes("SharePoint") || chunk.includes("document") || chunk.includes("Source")) {
          setCurrentStatus("Searching SharePoint...");
        } else if (chunk.length > 50) {
          setCurrentStatus("Generating response...");
        }

        setMessages((prev) => {
          const updated = [...prev];
          updated[assistantMsgIndex] = { role: "assistant", content: chunk };
          return updated;
        });
      }

      // Calculate final latency
      const finalLatencyMs = Date.now() - queryStartTime;
      setMessages((prev) => {
        const updated = [...prev];
        updated[assistantMsgIndex] = {
          role: "assistant",
          content: lastContent,
          latencyMs: finalLatencyMs
        };
        return updated;
      });

    } catch (err) {
      console.error("Query error:", err);
      setError(err instanceof Error ? err.message : "Query failed");
      setMessages((prev) => {
        const updated = [...prev];
        updated[assistantMsgIndex] = {
          role: "assistant",
          content: "Sorry, I encountered an error. Please try again."
        };
        return updated;
      });
    } finally {
      setLoading(false);
      setCurrentStatus("");
    }
  };

  // Handle Enter key
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  // Format milliseconds nicely
  const formatMs = (ms: number) => {
    if (ms < 1000) return `${ms}ms`;
    return `${(ms / 1000).toFixed(2)}s`;
  };

  return (
    <div className="app">
      <header className="header">
        <h1>Cloud Portal Assistant</h1>
        {isAuthenticated ? (
          <div className="user-info">
            <span>{accounts[0]?.name}</span>
            <button onClick={handleLogout} className="btn btn-secondary">
              Logout
            </button>
          </div>
        ) : (
          <button onClick={handleLogin} className="btn btn-primary">
            Sign in with Microsoft
          </button>
        )}
      </header>

      <main className="main">
        {!isAuthenticated ? (
          <div className="login-prompt">
            <h2>Welcome to Cloud Portal Assistant</h2>
            <p>Sign in with your Microsoft account to search SharePoint and manage ServiceNow.</p>
          </div>
        ) : (
          <div className="chat-container">
            <div className="messages">
              {messages.map((msg, idx) => (
                // Skip rendering empty placeholder messages
                msg.content ? (
                  <div key={idx} className={`message ${msg.role}`}>
                    <div className="message-content">
                      <ReactMarkdown>{msg.content}</ReactMarkdown>
                      {msg.latencyMs && (
                        <div className="latency-badge">
                          {formatMs(msg.latencyMs)}
                        </div>
                      )}
                    </div>
                  </div>
                ) : null
              ))}

              {/* Loading indicator with timer - inline, no separate bubble */}
              {loading && (
                <div className="thinking-indicator">
                  <div className="thinking-content">
                    <span className="thinking-dot"></span>
                    <span className="thinking-text">{currentStatus || "Processing..."}</span>
                    <span className="thinking-timer">{formatMs(elapsedMs)}</span>
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>

            {error && <div className="error">{error}</div>}

            <div className="input-area">
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Search SharePoint documents or manage ServiceNow tickets..."
                disabled={loading || !sessionId}
                rows={2}
              />
              <button
                onClick={handleSend}
                disabled={loading || !input.trim() || !sessionId}
                className="btn btn-primary"
              >
                Send
              </button>
            </div>
          </div>
        )}
      </main>

      <footer className="footer">
        <p>Powered by Google Agent Engine + Discovery Engine + ServiceNow MCP</p>
      </footer>
    </div>
  );
}

export default App;
