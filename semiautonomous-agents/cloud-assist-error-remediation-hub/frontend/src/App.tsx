import React, { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { TimeFilterBar } from './components/LeftPanel/TimeFilterBar';
import { ErrorList } from './components/LeftPanel/ErrorList';
import { DiagnosticContainer } from './components/MiddlePanel/DiagnosticContainer';
import { ObservabilityDashboardTab } from './components/MiddlePanel/ObservabilityDashboardTab';
import { WestworldWhiteSolomonTab } from './components/MiddlePanel/WestworldWhiteSolomonTab';
import { RemediationBitacoraTab } from './components/MiddlePanel/RemediationBitacoraTab';
import { ChaosStressTestModal } from './components/MiddlePanel/ChaosStressTestModal';
import { PostMortemReportModal } from './components/MiddlePanel/PostMortemReportModal';
import { ChatbotDrawer } from './components/RightPanel/ChatbotDrawer';
import { GcpErrorItem, CloudAssistDiagnostic, ChatMessage } from './types';
import { Layers, Radio, Sparkles, Activity, Eye, Flame, FileText, RotateCcw } from 'lucide-react';

const API_BASE = 'http://127.0.0.1:8088/api';

export function App() {
  const [errors, setErrors] = useState<GcpErrorItem[]>([]);
  const [selectedRange, setSelectedRange] = useState<string>('1h');
  const [selectedError, setSelectedError] = useState<GcpErrorItem | null>(null);
  const [diagnostic, setDiagnostic] = useState<CloudAssistDiagnostic | null>(null);
  const [activeMainTab, setActiveMainTab] = useState<'remediation' | 'observability' | 'solomon' | 'bitacora'>('remediation');
  const [themeMode, setThemeMode] = useState<'light' | 'dark'>('light');
  
  const [isChaosOpen, setIsChaosOpen] = useState<boolean>(false);
  const [isReportOpen, setIsReportOpen] = useState<boolean>(false);

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

  const fetchErrors = async (timeRange: string) => {
    setIsErrorsLoading(true);
    try {
      const res = await fetch(`${API_BASE}/errors?time_range=${timeRange}`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data: GcpErrorItem[] = await res.json();
      setErrors(data);
      if (data.length > 0 && !selectedError) {
        handleSelectError(data[0]);
      }
    } catch (err) {
      console.error("Failed to fetch GCP errors:", err);
    } finally {
      setIsErrorsLoading(false);
    }
  };

  useEffect(() => {
    fetchErrors(selectedRange);
  }, [selectedRange]);

  const handleSelectError = async (item: GcpErrorItem) => {
    setSelectedError(item);
    setIsDiagnosing(true);
    try {
      const res = await fetch(`${API_BASE}/diagnose`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ errorItem: item })
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data: CloudAssistDiagnostic = await res.json();
      setDiagnostic(data);
    } catch (err) {
      console.error("Failed to diagnose GCP error:", err);
    } finally {
      setIsDiagnosing(false);
    }
  };

  const handleSendMessage = async (text: string) => {
    if (!text.trim()) return;

    const userMsg: ChatMessage = {
      id: `user-${Date.now()}`,
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
          contextDiagnostic: diagnostic,
          conversationHistory: chatMessages.map(m => ({ sender: m.sender, text: m.text }))
        })
      });

      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      const agentMsg: ChatMessage = {
        id: `agent-${Date.now()}`,
        sender: 'agent',
        text: data.reply || "No response generated.",
        sourcesCited: data.sourcesCited || [],
        timestamp: new Date().toISOString()
      };
      setChatMessages((prev) => [...prev, agentMsg]);
    } catch (err) {
      console.error("Failed to process chatbot query:", err);
      setChatMessages((prev) => [
        ...prev,
        {
          id: `err-${Date.now()}`,
          sender: 'agent',
          text: "I encountered an error connecting to the ADK agent. Please verify backend service on port 8088.",
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
            onClick={() => setActiveMainTab('bitacora')}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-2 cursor-pointer ${
              activeMainTab === 'bitacora'
                ? 'bg-emerald-950/60 text-emerald-300 border border-emerald-500/40 shadow-lg'
                : isLight
                  ? 'text-slate-600 hover:text-slate-950 hover:bg-slate-100 font-bold'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
            }`}
          >
            <RotateCcw className="w-3.5 h-3.5 text-emerald-400" />
            <span>📜 Remediation Bitácora & Rollback</span>
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

        {/* Right Feature Controls */}
        <div className="flex items-center space-x-3">
          <button
            onClick={() => setIsChaosOpen(true)}
            className="px-3.5 py-1.5 rounded-xl bg-rose-600 hover:bg-rose-700 text-white text-xs font-bold font-mono flex items-center gap-1.5 shadow-md cursor-pointer"
            title="Launch Automated Chaos Stress Test across all 4 Cloud Run microservices"
          >
            <Flame className="w-3.5 h-3.5 fill-current" />
            <span>🚀 Chaos Stress Test</span>
          </button>

          <button
            onClick={() => setIsReportOpen(true)}
            className={`px-3.5 py-1.5 rounded-xl text-xs font-bold font-mono flex items-center gap-1.5 shadow-sm cursor-pointer border ${
              isLight
                ? 'bg-white hover:bg-slate-100 border-slate-300 text-slate-950 font-bold'
                : 'bg-slate-900 hover:bg-slate-800 border-slate-700 text-slate-200'
            }`}
            title="Export Executive Incident Post-Mortem Report"
          >
            <FileText className="w-3.5 h-3.5 text-blue-500" />
            <span>📄 Post-Mortem Report</span>
          </button>
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
          isLight ? 'bg-[#fafafa]' : 'bg-[#0a0d14]'
        }`}>
          {activeMainTab === 'remediation' ? (
            <DiagnosticContainer
              selectedError={selectedError}
              diagnostic={diagnostic}
              isLoading={isDiagnosing}
              isLightMode={isLight}
            />
          ) : activeMainTab === 'observability' ? (
            <ObservabilityDashboardTab />
          ) : activeMainTab === 'bitacora' ? (
            <RemediationBitacoraTab isLightMode={isLight} />
          ) : (
            <WestworldWhiteSolomonTab />
          )}
        </main>

        {/* Right Drawer: ADK Chatbot Agent */}
        <ChatbotDrawer
          selectedError={selectedError}
          diagnostic={diagnostic}
          messages={chatMessages}
          onSendMessage={handleSendMessage}
          isSending={isChatSending}
          isLightMode={isLight}
        />
      </div>

      {/* Modals */}
      <ChaosStressTestModal isOpen={isChaosOpen} onClose={() => setIsChaosOpen(false)} isLightMode={isLight} />
      <PostMortemReportModal isOpen={isReportOpen} onClose={() => setIsReportOpen(false)} selectedError={selectedError} diagnostic={diagnostic} isLightMode={isLight} />
    </div>
  );
}

export default App;
