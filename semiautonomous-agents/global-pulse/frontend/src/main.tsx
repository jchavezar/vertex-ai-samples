import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";

const globalStyles = `
:root {
  --bg-primary: #0a0e1a;
  --bg-surface: #141927;
  --bg-elevated: #1a2035;
  --border: #1e2a45;
  --border-hover: #2d3f66;
  --accent-cyan: #00d4ff;
  --accent-blue: #3b82f6;
  --accent-green: #22c55e;
  --accent-amber: #f59e0b;
  --accent-red: #ef4444;
  --accent-orange: #f97316;
  --accent-purple: #8b5cf6;
  --accent-gray: #6b7280;
  --text-primary: #f0f4ff;
  --text-secondary: #8892b0;
  --text-muted: #4a5568;
  --font-sans: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  --font-mono: 'SF Mono', 'Fira Code', 'JetBrains Mono', monospace;
}

*, *::before, *::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

html, body {
  background: var(--bg-primary);
  color: var(--text-primary);
  font-family: var(--font-sans);
  line-height: 1.6;
  -webkit-font-smoothing: antialiased;
  overflow-x: hidden;
}

#root {
  min-height: 100vh;
}

::-webkit-scrollbar {
  width: 8px;
}
::-webkit-scrollbar-track {
  background: var(--bg-primary);
}
::-webkit-scrollbar-thumb {
  background: var(--border);
  border-radius: 4px;
}
::-webkit-scrollbar-thumb:hover {
  background: var(--border-hover);
}

@keyframes pulse-glow {
  0%, 100% { opacity: 1; box-shadow: 0 0 8px var(--accent-cyan); }
  50% { opacity: 0.6; box-shadow: 0 0 20px var(--accent-cyan); }
}

@keyframes fade-in {
  from { opacity: 0; transform: translateY(12px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes slide-up {
  from { opacity: 0; transform: translateY(24px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}

.fade-in {
  animation: fade-in 0.4s ease-out both;
}

.slide-up {
  animation: slide-up 0.5s ease-out both;
}
`;

const styleEl = document.createElement("style");
styleEl.textContent = globalStyles;
document.head.appendChild(styleEl);

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
