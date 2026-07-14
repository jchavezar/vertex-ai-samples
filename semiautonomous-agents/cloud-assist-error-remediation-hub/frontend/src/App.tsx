import React, { useState, useEffect, useCallback } from 'react';
import { GcpErrorItem, CloudAssistDiagnostic, ChatMessage } from './types';
import { Header } from './components/Header';
import { TimeFilterBar } from './components/LeftPanel/TimeFilterBar';
import { ErrorList } from './components/LeftPanel/ErrorList';
import { DiagnosticContainer } from './components/MiddlePanel/DiagnosticContainer';
import { ChatbotDrawer } from './components/RightPanel/ChatbotDrawer';

const API_BASE = 'http://127.0.0.1:8088/api';

export function App() {
  const [errors, setErrors] = useState<GcpErrorItem[]>([]);
  const [selectedRange, setSelectedRange] = useState<string>('1h');
  const [selectedError, setSelectedError] = useState<GcpErrorItem | null>(null);
  const [diagnostic, setDiagnostic] = useState<CloudAssistDiagnostic | null>(null);
  
  const [isErrorsLoading, setIsErrorsLoading] = useState<boolean>(true);
  const [isDiagnosing, setIsDiagnosing] = useState<boolean>(false);
  const [isChatSending, setIsChatSending] = useState<boolean>(false);

  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([
    {
      id: 'welcome-1',
      sender: 'agent',
      text: "Hello! I am your Google ADK Error Remediation Assistant equipped with Google Search. Select any Google Cloud platform error on the left to inspect its autonomous Gemini Cloud Assist diagnosis and ask me anything!",
      timestamp: new Date().toISOString()
    }
  ]);

  // Fetch Errors when range changes or on refresh
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
  }, [selectedRange]);

  // Handle Error Selection & Cloud Assist Diagnostic trigger
  const handleSelectError = async (err: GcpErrorItem) => {
    setSelectedError(err);
    setDiagnostic(null);
    setIsDiagnosing(true);

    try {
      const res = await fetch(`${API_BASE}/diagnose`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ errorItem: err })
      });
      if (res.ok) {
        const diag: CloudAssistDiagnostic = await res.json();
        setDiagnostic(diag);
      }
    } catch (e) {
      console.error("Diagnosis request failed:", e);
    } finally {
      setIsDiagnosing(false);
    }
  };

  // Handle Chatbot Query
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

  return (
    <div className="h-screen w-screen flex flex-col overflow-hidden bg-[#0a0d14]">
      {/* Top Glassmorphic Header */}
      <Header
        totalErrors={errors.length}
        onRefreshAll={() => fetchErrors(selectedRange)}
        isLoading={isErrorsLoading}
      />

      {/* Main Multi-Panel Layout */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Sidebar: Time Filter + GCP Errors List */}
        <aside className="w-80 border-r border-slate-800/80 bg-[#0c101a]/90 flex flex-col z-20">
          <TimeFilterBar
            selectedRange={selectedRange}
            onSelectRange={setSelectedRange}
            isLoading={isErrorsLoading}
          />
          <ErrorList
            errors={errors}
            selectedErrorId={selectedError?.id || null}
            onSelectError={handleSelectError}
            isLoading={isErrorsLoading}
          />
        </aside>

        {/* Center Main: Cloud Assist 4-Container Diagnostic Engine */}
        <main className="flex-1 flex flex-col overflow-hidden bg-[#0a0d14] relative">
          <DiagnosticContainer
            selectedError={selectedError}
            diagnostic={diagnostic}
            isLoading={isDiagnosing}
          />
        </main>

        {/* Way Right: Google ADK Chatbot + Google Search + Claude Ink Animation */}
        <ChatbotDrawer
          selectedError={selectedError}
          diagnostic={diagnostic}
          messages={chatMessages}
          onSendMessage={handleSendMessage}
          isSending={isChatSending}
        />
      </div>
    </div>
  );
}

export default App;
