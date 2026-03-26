import { useState, useRef, useEffect } from "react";
import { useMsal, useIsAuthenticated } from "@azure/msal-react";
import { loginRequest } from "./authConfig";
import { exchangeTokenForGcp, createSession, queryStream } from "./agentService";
import ReactMarkdown from "react-markdown";

interface Message {
  role: "user" | "assistant";
  content: string;
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

  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

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

      // Create Agent Engine session
      console.log("Creating Agent Engine session...");
      const session = await createSession(
        gcpAccessToken,
        response.account?.username || "user",
        idToken
      );
      setSessionId(session);
      console.log("Session created:", session);

      setMessages([
        {
          role: "assistant",
          content: `Welcome, ${response.account?.name}! I'm your ServiceNow assistant. How can I help you today?`,
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

    // Add placeholder for assistant response
    const assistantMsgIndex = messages.length + 1;
    setMessages((prev) => [...prev, { role: "assistant", content: "" }]);

    try {
      // Stream chunks and update UI progressively
      for await (const chunk of queryStream(
        gcpToken,
        sessionId,
        accounts[0]?.username || "user",
        userMessage
      )) {
        setMessages((prev) => {
          const updated = [...prev];
          updated[assistantMsgIndex] = { role: "assistant", content: chunk };
          return updated;
        });
      }
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
    }
  };

  // Handle Enter key
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="app">
      <header className="header">
        <h1>ServiceNow Agent Portal</h1>
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
            <h2>Welcome to ServiceNow Agent Portal</h2>
            <p>Sign in with your Microsoft account to get started.</p>
          </div>
        ) : (
          <div className="chat-container">
            <div className="messages">
              {messages.map((msg, idx) => (
                <div key={idx} className={`message ${msg.role}`}>
                  <div className="message-content">
                    <ReactMarkdown>{msg.content}</ReactMarkdown>
                  </div>
                </div>
              ))}
              {loading && (
                <div className="message assistant">
                  <div className="message-content loading">Thinking...</div>
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
                placeholder="Ask about incidents, problems, changes..."
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
        <p>Powered by Google Agent Engine + ServiceNow MCP</p>
      </footer>
    </div>
  );
}

export default App;
