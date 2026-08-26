import React, { useState, useEffect, useRef } from 'react';
import {
  Square,
  ArrowUp,
  AlertCircle
} from 'lucide-react';
import type {
  ChatMessage as ChatMessageType,
  ToolDefinition,
  HealthStatus,
  ArtifactData,
  ToolExecution
} from './types';
import { fetchHealth, fetchTools, initSession, streamChat } from './services/api';
import { Header } from './components/Header';
import { Sidebar } from './components/Sidebar';
import { ChatMessage } from './components/ChatMessage';
import { ArtifactPanel } from './components/ArtifactPanel';
import { PresetPrompts } from './components/PresetPrompts';

export function App() {
  const [messages, setMessages] = useState<ChatMessageType[]>([]);
  const [inputPrompt, setInputPrompt] = useState<string>('');
  const [isStreaming, setIsStreaming] = useState<boolean>(false);
  const [sessionId, setSessionId] = useState<string>(() => `sess_${Math.random().toString(36).substring(2, 10)}`);
  const [userId] = useState<string>('enterprise_analyst_1');
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [tools, setTools] = useState<ToolDefinition[]>([]);
  const [artifacts, setArtifacts] = useState<ArtifactData[]>([]);
  const [selectedArtifactId, setSelectedArtifactId] = useState<string | null>(null);
  const [isArtifactPanelOpen, setIsArtifactPanelOpen] = useState<boolean>(false);
  const [isSidebarOpen] = useState<boolean>(true);
  const [errorBanner, setErrorBanner] = useState<string | null>(null);

  const abortControllerRef = useRef<AbortController | null>(null);
  const chatBottomRef = useRef<HTMLDivElement | null>(null);
  const textareaRef = useRef<HTMLTextAreaElement | null>(null);

  // Initialize on mount
  useEffect(() => {
    async function loadData() {
      try {
        const [h, t] = await Promise.all([fetchHealth(), fetchTools()]);
        setHealth(h);
        setTools(t);
        await initSession(sessionId, userId);
      } catch (err) {
        console.error('Initialization error:', err);
      }
    }
    loadData();
  }, [sessionId, userId]);

  // Auto-scroll chat on messages change
  useEffect(() => {
    chatBottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isStreaming]);

  // Auto-resize textarea dynamically on text changes and newlines
  useEffect(() => {
    const textarea = textareaRef.current;
    if (!textarea) return;

    // Reset height temporarily to accurately calculate scrollHeight
    textarea.style.height = 'auto';
    const maxHeight = 180;
    const scrollHeight = textarea.scrollHeight;
    
    // Auto-grow height up to maxHeight
    textarea.style.height = `${Math.min(scrollHeight, maxHeight)}px`;
    // Only show scrollbar when content exceeds maxHeight
    textarea.style.overflowY = scrollHeight > maxHeight ? 'auto' : 'hidden';
  }, [inputPrompt]);

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInputPrompt(e.target.value);
  };

  const handleNewSession = async () => {
    const newSid = `sess_${Math.random().toString(36).substring(2, 10)}`;
    setSessionId(newSid);
    setMessages([]);
    setArtifacts([]);
    setSelectedArtifactId(null);
    setErrorBanner(null);
    try {
      await initSession(newSid, userId);
    } catch (err) {
      console.warn('Session reset notice:', err);
    }
  };

  const handleStopStream = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
      setIsStreaming(false);
    }
  };

  const handleSendMessage = async (promptToSend?: string) => {
    const text = (promptToSend || inputPrompt).trim();
    if (!text || isStreaming) return;

    setInputPrompt('');
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
    setErrorBanner(null);

    const userMessageId = `msg_user_${Date.now()}`;
    const assistantMessageId = `msg_asst_${Date.now()}`;

    const userMsg: ChatMessageType = {
      id: userMessageId,
      role: 'user',
      content: text,
      thoughts: [],
      tools: [],
      artifacts: [],
      timestamp: Date.now(),
    };

    const asstMsg: ChatMessageType = {
      id: assistantMessageId,
      role: 'assistant',
      content: '',
      thoughts: [],
      tools: [],
      artifacts: [],
      timestamp: Date.now(),
      isStreaming: true,
    };

    setMessages((prev) => [...prev, userMsg, asstMsg]);
    setIsStreaming(true);

    const controller = new AbortController();
    abortControllerRef.current = controller;

    try {
      await streamChat(
        text,
        sessionId,
        userId,
        {
          onThinking: (thought: string) => {
            setMessages((prev) =>
              prev.map((msg) => {
                if (msg.id !== assistantMessageId) return msg;
                return {
                  ...msg,
                  thoughts: [...msg.thoughts, thought],
                };
              })
            );
          },
          onToolStart: (toolData) => {
            const toolExec: ToolExecution = {
              tool_call_id: toolData.tool_call_id,
              tool_name: toolData.tool_name,
              category: toolData.category,
              icon: toolData.icon,
              label: toolData.label,
              arguments: toolData.arguments,
              status: 'running',
              startTime: Date.now(),
            };
            setMessages((prev) =>
              prev.map((msg) => {
                if (msg.id !== assistantMessageId) return msg;
                return {
                  ...msg,
                  tools: [...msg.tools, toolExec],
                };
              })
            );
          },
          onToolEnd: (toolData) => {
            setMessages((prev) =>
              prev.map((msg) => {
                if (msg.id !== assistantMessageId) return msg;
                const updatedTools = msg.tools.map((t) => {
                  if (t.tool_call_id === toolData.tool_call_id || t.tool_name === toolData.tool_name) {
                    return {
                      ...t,
                      status: toolData.status,
                      output: toolData.output,
                      endTime: Date.now(),
                      durationMs: Date.now() - t.startTime,
                    };
                  }
                  return t;
                });
                return {
                  ...msg,
                  tools: updatedTools,
                };
              })
            );
          },
          onContent: (delta: string) => {
            setMessages((prev) =>
              prev.map((msg) => {
                if (msg.id !== assistantMessageId) return msg;
                return {
                  ...msg,
                  content: msg.content + delta,
                };
              })
            );
          },
          onArtifact: (art: ArtifactData) => {
            setArtifacts((prev) => [...prev, art]);
            setSelectedArtifactId(art.artifact_id);
            setIsArtifactPanelOpen(true);
            setMessages((prev) =>
              prev.map((msg) => {
                if (msg.id !== assistantMessageId) return msg;
                return {
                  ...msg,
                  artifacts: [...msg.artifacts, art],
                };
              })
            );
          },
          onDone: (doneData) => {
            setMessages((prev) =>
              prev.map((msg) => {
                if (msg.id !== assistantMessageId) return msg;
                return {
                  ...msg,
                  isStreaming: false,
                  elapsedSeconds: doneData.elapsed_seconds,
                  usage: doneData.usage,
                };
              })
            );
            setIsStreaming(false);
          },
          onError: (errMsg: string) => {
            setErrorBanner(errMsg);
            setIsStreaming(false);
            setMessages((prev) =>
              prev.map((msg) => {
                if (msg.id !== assistantMessageId) return msg;
                return {
                  ...msg,
                  isStreaming: false,
                };
              })
            );
          },
        },
        controller.signal
      );
    } catch (err: any) {
      if (err.name !== 'AbortError') {
        console.error('Chat execution failed:', err);
        setErrorBanner(err.message || 'Stream connection interrupted.');
      }
      setIsStreaming(false);
      setMessages((prev) =>
        prev.map((msg) => (msg.id === assistantMessageId ? { ...msg, isStreaming: false } : msg))
      );
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleOpenArtifact = (art: ArtifactData) => {
    setSelectedArtifactId(art.artifact_id);
    setIsArtifactPanelOpen(true);
  };

  return (
    <div className="flex flex-col h-screen w-screen overflow-hidden bg-slate-50 text-slate-900 font-sans">
      {/* Global Header */}
      <Header
        health={health}
        sessionId={sessionId}
        isStreaming={isStreaming}
        artifactCount={artifacts.length}
        isArtifactPanelOpen={isArtifactPanelOpen}
        onToggleArtifactPanel={() => setIsArtifactPanelOpen(!isArtifactPanelOpen)}
        onNewSession={handleNewSession}
      />

      {/* Main Workspace Layout */}
      <div className="flex flex-1 overflow-hidden relative">
        {/* Left Sidebar */}
        <Sidebar
          tools={tools}
          onSelectPrompt={(p) => handleSendMessage(p)}
          isOpen={isSidebarOpen}
        />

        {/* Center Chat & Reasoning Viewport */}
        <main className="flex-1 flex flex-col h-[calc(100vh-3.5rem)] bg-white/70 overflow-hidden relative">
          {/* Optional Error Notice */}
          {errorBanner && (
            <div className="m-3 p-3 rounded-lg bg-rose-50 border border-rose-200 text-rose-800 text-xs flex items-center justify-between shadow-2xs">
              <div className="flex items-center space-x-2">
                <AlertCircle className="w-4 h-4 text-rose-600 shrink-0" />
                <span>{errorBanner}</span>
              </div>
              <button
                onClick={() => setErrorBanner(null)}
                className="text-rose-600 hover:text-rose-900 font-bold px-1 cursor-pointer"
              >
                ✕
              </button>
            </div>
          )}

          {/* Messages Scroll Area */}
          <div className="flex-1 overflow-y-auto">
            {messages.length === 0 ? (
              <PresetPrompts onSelect={(prompt) => handleSendMessage(prompt)} />
            ) : (
              <div className="divide-y divide-slate-100">
                {messages.map((msg) => (
                  <ChatMessage
                    key={msg.id}
                    message={msg}
                    onOpenArtifact={handleOpenArtifact}
                  />
                ))}
                <div ref={chatBottomRef} className="h-4" />
              </div>
            )}
          </div>

          {/* Bottom Prompt Input Dock */}
          <div className="p-3 sm:p-4 bg-white/90 border-t border-slate-200 backdrop-blur-md">
            <div className="max-w-4xl mx-auto">
              <div className="relative rounded-xl border border-slate-300 bg-white shadow-xs focus-within:border-cyan-500 focus-within:ring-2 focus-within:ring-cyan-500/20 transition-all">
                <textarea
                  ref={textareaRef}
                  value={inputPrompt}
                  onChange={handleInputChange}
                  onKeyDown={handleKeyDown}
                  placeholder="Ask ADK Enterprise Assistant to run telemetry, query metrics, or model capital scenarios..."
                  rows={1}
                  disabled={isStreaming}
                  className="w-full resize-none bg-transparent px-4 pt-3.5 pb-2 text-xs sm:text-sm leading-relaxed text-slate-800 placeholder-slate-400 focus:outline-hidden disabled:opacity-60 overflow-hidden block"
                  style={{ minHeight: '46px', maxHeight: '180px' }}
                />

                {/* Bottom Input Controls */}
                <div className="px-3 pb-2.5 flex items-center justify-between">
                  <div className="flex items-center space-x-1.5 text-[11px] text-slate-500 font-mono">
                    <span className="hidden sm:inline">Autonomous Execution</span>
                    <span className="text-slate-300">•</span>
                    <span>Gemini 3.7 Flash</span>
                  </div>

                  <div className="flex items-center space-x-1.5">
                    {isStreaming ? (
                      <button
                        onClick={handleStopStream}
                        className="px-3 py-1.5 rounded-lg bg-rose-50 hover:bg-rose-100 border border-rose-200 text-rose-700 text-xs font-semibold flex items-center space-x-1.5 transition-colors cursor-pointer"
                      >
                        <Square className="w-3 h-3 fill-current" />
                        <span>Cancel</span>
                      </button>
                    ) : (
                      <button
                        onClick={() => handleSendMessage()}
                        disabled={!inputPrompt.trim()}
                        className="p-2 rounded-lg bg-slate-900 hover:bg-cyan-700 text-white transition-all disabled:opacity-30 disabled:pointer-events-none cursor-pointer shadow-2xs"
                        title="Send prompt"
                      >
                        <ArrowUp className="w-4 h-4" />
                      </button>
                    )}
                  </div>
                </div>
              </div>

              {/* Input Footer Helper */}
              <div className="mt-1.5 flex items-center justify-between text-[11px] text-slate-600 px-1 select-none">
                <span>Press <kbd className="px-1 py-0.2 bg-slate-100 border border-slate-300 rounded text-[10px] font-mono">Enter</kbd> to execute • <kbd className="px-1 py-0.2 bg-slate-100 border border-slate-300 rounded text-[10px] font-mono">Shift+Enter</kbd> for newline</span>
                <span className="font-mono">Port: 8090 (Backend) / 5174 (UI)</span>
              </div>
            </div>
          </div>
        </main>

        {/* Right Artifact Panel */}
        {isArtifactPanelOpen && (
          <ArtifactPanel
            artifacts={artifacts}
            selectedArtifactId={selectedArtifactId}
            onSelectArtifact={(id) => setSelectedArtifactId(id)}
            onClose={() => setIsArtifactPanelOpen(false)}
          />
        )}
      </div>
    </div>
  );
}

export default App;
