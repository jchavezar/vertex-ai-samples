import React, { useState, useEffect, useCallback } from 'react';
import { GcpErrorItem, CloudAssistDiagnostic, ChatMessage } from './types';
import { Header } from './components/Header';
import { TimeFilterBar } from './components/LeftPanel/TimeFilterBar';
import { ErrorList } from './components/LeftPanel/ErrorList';
import { DiagnosticContainer } from './components/MiddlePanel/DiagnosticContainer';
import { ObservabilityDashboardTab } from './components/MiddlePanel/ObservabilityDashboardTab';
import { WestworldWhiteSolomonTab } from './components/MiddlePanel/WestworldWhiteSolomonTab';
import { ChatbotDrawer } from './components/RightPanel/ChatbotDrawer';
import { Layers, Radio, Sparkles, Activity, Eye } from 'lucide-react';

const API_BASE = 'http://127.0.0.1:8088/api';

export function App() {
  const [errors, setErrors] = useState<GcpErrorItem[]>([]);
  const [selectedRange, setSelectedRange] = useState<string>('1h');
  const [selectedError, setSelectedError] = useState<GcpErrorItem | null>(null);
  const [diagnostic, setDiagnostic] = useState<CloudAssistDiagnostic | null>(null);
  const [activeMainTab, setActiveMainTab] = useState<'remediation' | 'observability' | 'solomon'>('remediation');
  const [themeMode, setThemeMode] = useState<'light' | 'dark'>('light');
  
  const [isErrorsLoading, setIsErrorsLoading] = useState<boolean>(true);
  const [isDiagnosing, setIsDiagnosing] = useState<boolean>(false);
  const [isChatSending, setIsChatSending] = useState<boolean>(false);

  const handleToggleTheme = () => {
    setThemeMode((prev) => (prev === 'light' ? 'dark' : 'light'));
  };

  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([
    {
      id: 'welcome-1',
      sender: 'agent',
      text: "Hello! I am your Google ADK Error Remediation Assistant equipped with Google Search. Select any Google Cloud platform error on the left to inspect its autonomous Gemini Cloud Assist diagnosis and ask me anything!",
      timestamp: new Date().toISOString()
    }
  ]);

  const fetchErrors = useCallback(async (range: string) => {
    setIsErrorsLoading(true);
    try {
      const res = await fetch(`${API_BASE}/errors?time_range=${range}`);
      if (res.ok) {
        const data: GcpErrorItem[] = await res.json();
        setErrors(data);
        if (data.length > 0 && !selectedError) {
          handleSelectError(data[0]);
        }
      }
    } catch (err) {
      console.error("Failed to fetch GCP errors:", err);
    } finally {
      setIsErrorsLoading(false);
    }
  }, [selectedError]);

  useEffect(() => {
    fetchErrors(selectedRange);
  }, [selectedRange, fetchErrors]);

  const handleSelectError = async (errItem: GcpErrorItem) => {
    setSelectedError(errItem);
    setIsDiagnosing(true);
    setDiagnostic(null);

    // Dynamic Agent Context Switch: Reset chat messages with proactive incident notification
    setChatMessages([
      {
        id: `sys-${Date.now()}`,
        sender: 'agent',
        text: `📡 **Active Incident Context Loaded**: \`${errItem.serviceName}\` — **${errItem.summary}**\n\nI have ingested the log traces, service metadata, and Cloud Assist findings into my prompt context. Ask me anything about this issue (e.g., *"What is causing this error?"*, *"Provide step-by-step gcloud fix commands"*).`,
        timestamp: new Date().toISOString()
      }
    ]);

    try {
      const res = await fetch(`${API_BASE}/diagnose`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ errorItem: errItem })
      });
      if (res.ok) {
        const data: CloudAssistDiagnostic = await res.json();
        setDiagnostic(data);
      }
    } catch (err) {
      console.error("Diagnosis request failed:", err);
    } finally {
      setIsDiagnosing(false);
    }
  };

  const handleSendMessage = async (text: string) => {
    const userMsg: ChatMessage = {
      id: `usr-${Date.now()}`,
      sender: 'user',
      text,
      timestamp: new Date().toISOString()
    };
    setChatMessages((prev) => [...prev, userMsg]);
    setIsChatSending(true);

    try {
      const res = await fetch(`${API_BASE}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: text,
          contextError: selectedError,
          contextDiagnostic: diagnostic
        })
      });

      if (res.ok) {
        const data = await res.json();
        const agentMsg: ChatMessage = {
          id: `agt-${Date.now()}`,
          sender: 'agent',
          text: data.reply,
          timestamp: new Date().toISOString(),
          sourcesCited: data.sourcesCited
        };
        setChatMessages((prev) => [...prev, agentMsg]);
      } else {
        throw new Error(`Chat API status ${res.status}`);
      }
    } catch (err) {
      setChatMessages((prev) => [
        ...prev,
        {
          id: `err-${Date.now()}`,
          sender: 'agent',
          text: "Could not connect to ADK backend or search service. Ensure local FastAPI server is active on port 8088.",
          timestamp: new Date().toISOString()
        }
      ]);
    } finally {
      setIsChatSending(false);
    }
  };

  const [activeRemediationMessage, setActiveRemediationMessage] = useState<string | null>(null);

  const isLight = themeMode === 'light';

  return (
    <div className={`h-screen w-screen flex flex-col overflow-hidden transition-colors duration-300 ${
      isLight ? 'bg-[#fafafa] text-slate-900' : 'bg-[#0a0d14] text-white'
    }`}>
      {/* Top Glassmorphic Header */}
      <Header
        totalErrors={errors.length}
        onRefreshAll={() => fetchErrors(selectedRange)}
        isLoading={isErrorsLoading}
        activeRemediationMessage={activeRemediationMessage}
        themeMode={themeMode}
        onToggleTheme={handleToggleTheme}
        onSelectActiveRemediation={() => {
          setActiveMainTab('remediation');
          const cloudRunErr = errors.find(e => e.resourceType === 'cloud_run_revision');
          if (cloudRunErr) {
            handleSelectError(cloudRunErr);
          }
        }}
      />

      {/* Main Navigation Tab Bar */}
      <div className={`flex items-center justify-between border-b px-6 py-2 transition-colors duration-300 ${
        isLight ? 'bg-white border-slate-200' : 'bg-slate-950 border-slate-800'
      }`}>
        <div className="flex items-center space-x-2">
          <button
            onClick={() => setActiveMainTab('remediation')}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-2 cursor-pointer ${
              activeMainTab === 'remediation'
                ? 'bg-cyan-950/60 text-cyan-300 border border-cyan-500/40 shadow-lg shadow-cyan-500/10'
                : isLight
                  ? 'text-slate-600 hover:text-slate-950 hover:bg-slate-100'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
            }`}
          >
            <Activity className="w-3.5 h-3.5 text-cyan-400" />
            <span>📡 Incident Remediation Hub</span>
          </button>
          <button
            onClick={() => setActiveMainTab('observability')}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-2 cursor-pointer ${
              activeMainTab === 'observability'
                ? 'bg-purple-950/60 text-purple-300 border border-purple-500/40 shadow-lg shadow-purple-500/10'
                : isLight
                  ? 'text-slate-600 hover:text-slate-950 hover:bg-slate-100'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
            }`}
          >
            <Radio className="w-3.5 h-3.5 text-purple-400" />
            <span>🌌 Observability & Constellation Analytics</span>
          </button>
          <button
            onClick={() => setActiveMainTab('solomon')}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-2 cursor-pointer ${
              activeMainTab === 'solomon'
                ? 'bg-slate-950 text-white font-mono font-bold border border-slate-950 shadow-lg'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
            }`}
          >
            <Eye className="w-3.5 h-3.5 text-slate-300" />
            <span>⚪ Solomon White Edition</span>
          </button>
        </div>

        <div className={`text-[11px] font-mono ${isLight ? 'text-slate-600 font-bold' : 'text-slate-400'}`}>
          Antigravity Multi-Agent Orchestrator • Vertex AI
        </div>
      </div>

      {/* Main Multi-Panel Layout */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Sidebar: Time Filter + GCP Errors List */}
        <aside className={`w-80 border-r flex flex-col z-20 transition-colors duration-300 ${
          isLight ? 'bg-white border-slate-200' : 'bg-[#0c101a]/90 border-slate-800/80'
        }`}>
          <TimeFilterBar
            selectedRange={selectedRange}
            onSelectRange={setSelectedRange}
            isLoading={isErrorsLoading}
            isLightMode={isLight}
          />
          <ErrorList
            errors={errors}
            selectedErrorId={selectedError?.id || null}
            onSelectError={handleSelectError}
            isLoading={isErrorsLoading}
            isLightMode={isLight}
          />
        </aside>

        {/* Center Main Tab View */}
        <main className={`flex-1 flex flex-col overflow-y-auto relative p-4 transition-colors duration-300 ${
          isLight ? 'bg-slate-100' : 'bg-[#0a0d14]'
        }`}>
          {activeMainTab === 'remediation' ? (
            <DiagnosticContainer
              selectedError={selectedError}
              diagnostic={diagnostic}
              isLoading={isDiagnosing}
            />
          ) : activeMainTab === 'observability' ? (
            <ObservabilityDashboardTab />
          ) : (
            <WestworldWhiteSolomonTab />
          )}
        </main>

        {/* Right Panel: ADK Chatbot */}
        <ChatbotDrawer
          selectedError={selectedError}
          diagnostic={diagnostic}
          messages={chatMessages}
          onSendMessage={handleSendMessage}
          isSending={isChatSending}
          isLightMode={isLight}
        />
      </div>
    </div>
  );
}

export default App;
