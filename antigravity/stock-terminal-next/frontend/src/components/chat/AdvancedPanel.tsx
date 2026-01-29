import React, { useState, useEffect } from 'react';
import { Send, MessageSquare, Share2, Activity, Terminal, Maximize2, Minimize2, ChevronsRight, Clock, Brain, Square, Trash2, Image as ImageIcon, X } from 'lucide-react';
import { clsx } from "clsx";
import { useDashboardStore } from '../../store/dashboardStore';
import AgentGraph from './AgentGraph';
import TraceLog from './TraceLog';
import { ReasoningTab } from './ReasoningTab';
import { StreamingMarkdown } from './StreamingMarkdown';
import { useWorkstationChat } from '../../hooks/useWorkstationChat';

interface AdvancedPanelProps {
  onClose?: () => void;
  onDragStart?: (e: React.PointerEvent) => void;
  dashboardData?: any;
}

const ThinkingTimer = ({ startTime }: { startTime: number }) => {
  const [ms, setMs] = useState(0);
  useEffect(() => {
    // Initialize immediately to avoid 0.00 flash if possible, or just start interval
    setMs(Date.now() - startTime);
    const interval = setInterval(() => setMs(Date.now() - startTime), 50);
    return () => clearInterval(interval);
  }, [startTime]);
  return <span className="font-mono text-[var(--brand)] font-bold">{(ms / 1000).toFixed(2)}s</span>;
};

const MetricsFooter: React.FC<{ metrics: any }> = ({ metrics }) => {
  // Try to find reasoning metric from Agent node
  const agentMetrics = metrics?.['agent'] || metrics?.['Smart Agent'];
  const reasoning = agentMetrics?.reasoning;

  if (!reasoning) return null;

  return (
    <span className="flex items-center gap-2 text-[10px] text-[var(--text-muted)] opacity-80 mt-1">
      Reasoning: <b className="text-[var(--brand)]">{reasoning}s</b>
    </span>
  );
};

const DynamicStatusText: React.FC<{ logs: any[] }> = ({ logs }) => {
  if (!logs || logs.length === 0) return <span>Thinking...</span>;

  // Find interesting last event
  // We prioritize system_status if it's the most recent meaningful event
  for (let i = logs.length - 1; i >= 0; i--) {
    const log = logs[i];
    if (log.type === 'system_status') return <span className="animate-pulse font-medium text-[var(--brand)]">{log.content}</span>;
    if (log.type === 'tool_call') return <span>Calling <b className="text-[var(--text-primary)]">{log.tool}</b>...</span>;
    if (log.type === 'tool_result') return <span>Analyzing Data...</span>;
  }

  return <span>Thinking...</span>;
};

const AdvancedPanel: React.FC<AdvancedPanelProps> = ({ onDragStart }) => {
  const [activeTab, setActiveTab] = useState<'chat' | 'graph' | 'trace' | 'reasoning'>('chat');
  const { messages, input, handleInputChange, handleSubmit, isLoading, traceLogs, topology, executionPath, nodeDurations, nodeMetrics, lastLatency, startTime, selectedModel, sessionId, stop, resetChat, image, handleImageSelect, clearImage } = useWorkstationChat();
  const { isChatMaximized, toggleChatMaximized, chatDockPosition, theme } = useDashboardStore();
  const fileInputRef = React.useRef<HTMLInputElement>(null);
  const textareaRef = React.useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea
  React.useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'; // Reset to shrink
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 200)}px`; // Grow up to 200px
    }
  }, [input]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleImageSelect(e.target.files[0]);
    }
    // Reset value so same file can be selected again if needed
    if (fileInputRef.current) fileInputRef.current.value = '';
  };
  const isDark = theme === 'dark';
  const scrollContainerRef = React.useRef<HTMLDivElement>(null);
  const messagesEndRef = React.useRef<HTMLDivElement>(null);
  const isAutoScrollEnabled = React.useRef(true);

  // Monitor user scroll to toggle auto-scroll
  const handleScroll = () => {
    if (!scrollContainerRef.current) return;
    const { scrollTop, scrollHeight, clientHeight } = scrollContainerRef.current;

    // Calculate distance to bottom
    const distanceToBottom = scrollHeight - scrollTop - clientHeight;

    // If user interacts/scrolls up, disable auto-scroll
    // Tolerance: 50px
    if (distanceToBottom > 50) {
      if (isAutoScrollEnabled.current) isAutoScrollEnabled.current = false;
    } else {
      // If user manually scrolls to bottom, re-enable
      if (!isAutoScrollEnabled.current) isAutoScrollEnabled.current = true;
    }
  };

  // Robust Auto-scroll
  React.useEffect(() => {
    // If we are loading, we mostly want to auto-scroll unless user explicitly moved UP far away.
    // Actually, for a terminal feel, we usually ALWAYS want to see the latest output.

    const container = scrollContainerRef.current;
    if (!container) return;

    const scroll = () => {
      container.scrollTo({ top: container.scrollHeight, behavior: isLoading ? 'instant' : 'smooth' });
    };

    if (isLoading) {
      // While loading, if auto-scroll is enabled OR we are close to bottom, force it.
      // If user scrolled way up to read history, we respect that (isAutoScrollEnabled would be false).
      // But if they are just reading the stream, we keep scrolling.
      if (isAutoScrollEnabled.current) {
        scroll();
      }
    } else {
      // Not loading (idle or new message arrived)
      // If enabled, scroll to bottom
      if (isAutoScrollEnabled.current) {
        scroll();
      }
    }
  }, [messages, traceLogs, isLoading]);

  // Force enable auto-scroll on new submission (User pressed Enter)
  // We can hook into messages length change if last message is user?
  React.useEffect(() => {
    if (messages.length > 0 && messages[messages.length - 1].role === 'user') {
      isAutoScrollEnabled.current = true;
      if (scrollContainerRef.current) {
        scrollContainerRef.current.scrollTo({ top: scrollContainerRef.current.scrollHeight, behavior: 'smooth' });
      }
    }
  }, [messages.length]);

  // Initial Scroll
  React.useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'instant' });
    }
  }, [messages.length]);

  return (
    <div className="flex flex-col h-full bg-transparent border-l-0 rounded-l-2xl w-full">
      {/* Header */}
      <div
        className={clsx(
          "flex flex-wrap items-center justify-between p-1.5 sm:p-2 pl-4 pr-10 border-b shrink-0 bg-transparent cursor-grab active:cursor-grabbing select-none transition-all duration-300 group/header relative overflow-hidden gap-y-1",
          isDark ? "border-white/10" : "border-gray-100"
        )}
        onPointerDown={onDragStart}
        onDoubleClick={() => {
          const current = useDashboardStore.getState().chatDockPosition;
          useDashboardStore.getState().setChatDockPosition(current === 'right' ? 'floating' : 'right');
        }}
      >
        {/* Left Section: Icon and Title */}
        <div className="flex items-center gap-1.5 sm:gap-2.5 min-w-max transition-all">
          <button
            onClick={() => setActiveTab('chat')}
            className={clsx(
              "p-1.5 rounded-lg shrink-0 transition-all cursor-pointer",
              isDark ? "bg-white/5 text-white hover:bg-white/10" : "bg-slate-100 text-slate-900 hover:bg-slate-200"
            )}
            title="Workstation home"
          >
            <Terminal size={14} className="sm:w-[16px] sm:h-[16px]" />
          </button>

          <div className="flex flex-col min-w-0 shrink transition-all">
            <h1 className={clsx(
              "text-[10px] sm:text-xs md:text-sm font-black tracking-tighter leading-none transition-all duration-300 uppercase",
              isDark ? "text-white" : "text-slate-900"
            )}>
              WORKSTATION
            </h1>
          </div>
        </div>

        {/* Right Section: Tabs & Window Controls */}
        <div className="flex items-center gap-1 sm:gap-2 shrink-0 transition-all ml-auto">
          {/* Tabs - Label visibility is strictly controlled */}
          <div className={clsx(
            "flex items-center gap-0.5 sm:gap-1 rounded-lg p-0.5 border transition-all",
            isDark ? "bg-black/30 border-white/5" : "bg-slate-100/50 border-slate-200/50"
          )}>
            <TabButton
              active={activeTab === 'chat'}
              onClick={() => setActiveTab('chat')}
              icon={<MessageSquare className="w-3.5 h-3.5" />}
              label="Chat"
              isDark={isDark}
              isChatMaximized={isChatMaximized}
            />
            <TabButton
              active={activeTab === 'graph'}
              onClick={() => setActiveTab('graph')}
              icon={<Share2 className="w-3.5 h-3.5" />}
              label="Graph"
              isDark={isDark}
              isChatMaximized={isChatMaximized}
            />
            <TabButton
              active={activeTab === 'trace'}
              onClick={() => setActiveTab('trace')}
              icon={<Activity className="w-3.5 h-3.5" />}
              label="Trace"
              isDark={isDark}
              isChatMaximized={isChatMaximized}
            />
            <TabButton
              active={activeTab === 'reasoning'}
              onClick={() => setActiveTab('reasoning')}
              icon={<Brain className="w-3.5 h-3.5" />}
              label="Reason"
              isDark={isDark}
              isChatMaximized={isChatMaximized}
            />
          </div>

          {/* Window Control Cluster */}
          <div className="flex items-center gap-0 sm:gap-0.5 pl-1 sm:pl-2 border-l border-white/10 shrink-0 transition-all">
            {isLoading ? (
              <button
                onClick={stop}
                className="p-1 px-1.5 rounded-md text-amber-500 hover:text-amber-600 hover:bg-amber-500/10 transition-colors shrink-0"
                title="Stop"
              >
                <Square size={14} className="sm:w-[15px] sm:h-[15px]" fill="currentColor" />
              </button>
            ) : (
              messages.length > 0 && (
                <button
                  onClick={resetChat}
                    className="p-1 px-1.5 rounded-md text-red-500/70 hover:text-red-500 hover:bg-red-500/10 transition-colors shrink-0"
                    title="Reset"
                >
                    <Trash2 size={14} className="sm:w-[15px] sm:h-[15px]" />
                </button>
              )
            )}
            <button
              onClick={toggleChatMaximized}
              className={clsx(
                "p-1 px-1.5 rounded-md transition-colors shrink-0",
                isDark ? "text-white/40 hover:text-white hover:bg-white/10" : "text-slate-500 hover:text-slate-800 hover:bg-slate-100"
              )}
              title={isChatMaximized ? "Restore" : "Maximize"}
            >
              {isChatMaximized ? <Minimize2 size={14} className="sm:w-[15px] sm:h-[15px]" /> : <Maximize2 size={14} className="sm:w-[15px] sm:h-[15px]" />}
            </button>
            <button
              onClick={() => {
                const current = useDashboardStore.getState().chatDockPosition;
                useDashboardStore.getState().setChatDockPosition(current === 'right' ? 'floating' : 'right');
              }}
              className={clsx(
                "p-1 px-1.5 rounded-md transition-colors shrink-0",
                isDark ? "text-white/40 hover:text-white hover:bg-white/10" : "text-slate-500 hover:text-slate-800 hover:bg-slate-100"
              )}
              title={chatDockPosition === 'right' ? "Undock" : "Dock"}
            >
              {chatDockPosition === 'right' ? <Minimize2 size={14} className="sm:w-[15px] sm:h-[15px] rotate-45" /> : <Maximize2 size={14} className="sm:w-[15px] sm:h-[15px] -rotate-45" />}
            </button>
            <button
              onClick={() => useDashboardStore.getState().setChatOpen(false)}
              className="p-1 px-1.5 text-white/40 hover:text-red-500 hover:bg-red-500/10 rounded-md transition-colors flex items-center gap-1 shrink-0"
              title="Hide"
            >
              <ChevronsRight size={14} className="sm:w-[15px] sm:h-[15px]" />
            </button>
          </div>
        </div>

        {/* Safety Gutter Absolute Element (Fixed dead zone) */}
        <div className="absolute top-0 right-0 w-8 h-full bg-transparent pointer-events-none group-active/header:bg-red-500/5 transition-colors" aria-hidden="true" />
      </div>

      {/* Content Area */}
      <div className="flex-1 overflow-hidden relative">

        {/* CHAT TAB */}
        <div className={`absolute inset-0 flex flex-col ${activeTab === 'chat' ? 'z-10' : 'hidden'}`}>
          <div
            ref={scrollContainerRef}
            onScroll={handleScroll}
            className="flex-1 overflow-y-auto p-4 space-y-4 scroll-smooth"
          >
            {messages.length === 0 && (
              <div className={clsx("h-full flex flex-col items-center justify-center opacity-60", isDark ? "text-[var(--text-muted)]" : "text-slate-400")}>
                <div className={clsx("p-6 rounded-full mb-6", isDark ? "bg-[var(--bg-app)]" : "bg-slate-100")}><Terminal size={48} /></div>
                <p className="text-xl">How can I help you today?</p>
              </div>
            )}
            {messages.map((m: any, i: number) => {
              const isAssistant = m.role === 'assistant';
              const isStreaming = isAssistant && i === messages.length - 1 && isLoading;


              // Typewriter Class Logic
              const messageClass = isAssistant ? 'text-sm leading-relaxed' : 'text-sm leading-relaxed';


              // Identify if this is the latest user message to attach the active/final timer
              // This ensures the timer persists even after the assistant responds (which makes isLastMessage false)
              const lastUserIndex = messages.reduce((acc: number, m: any, idx: number) => m.role === 'user' ? idx : acc, -1);
              const isLatestUserMessage = m.role === 'user' && i === lastUserIndex;

              return (
                <div key={i} className={`flex flex-col ${m.role === 'user' ? 'items-end' : 'items-start'}`}>
                  {/* Only render bubble if there is content */}
                  {m.content && m.content.trim() !== '' && (
                    <div className={clsx(
                      "max-w-[85%] rounded-3xl p-3 px-4 text-sm shadow-sm",
                      m.role === 'user' ? "bg-[var(--brand)] text-white rounded-br-none" :
                      isDark ? "bg-[var(--bg-app)] border border-[var(--border)] text-[var(--text-primary)] rounded-bl-none" :
                      "bg-white border border-gray-100 text-slate-800 rounded-bl-none shadow-sm"
                    )}>
                      {m.role === 'user' ? (
                        <div>{m.content}</div>
                      ) : (
                        <div className={`relative`}>
                          <StreamingMarkdown
                            content={m.content}
                            isStreaming={isStreaming}
                            className={messageClass}
                          />
                        </div>
                      )}
                    </div>
                  )}

                  {
                    m.role === 'assistant' && (
                      <div className="mt-2 flex items-center gap-3 pl-1">
                        {/* Topology/Graph shortcut */}
                        <button
                          onClick={() => {
                            useDashboardStore.getState().setGraphOverlayOpen(true);
                          }}
                          className="text-xs text-[var(--brand)] hover:underline flex items-center gap-1.5 opacity-70 hover:opacity-100 transition-opacity"
                          title="View Execution Graph"
                        >
                          <Share2 size={13} /> View Graph
                        </button>
                      </div>
                    )
                  }

                  {/* Latency Evidence (Steady Counter or Active Timer) - Attaches to User Message or Assistant? */}
                  {/* User wants it "from the moment I click send". It makes sense on the User Message or right after it. */}
                  {/* Architecture: We attach it to the User Message for visibility, OR strictly to the Assistant if we want "Response Time" */}
                  {/* The previous code had it in the loop but unrelated to role? No, the loop renders ONE div per message. */}
                  {/* We need to place this Latency block specifically for the User message if we want it there. */}
                  {/* BUT the previous code had it inside `m.role === 'assistant'` check? Let's check the context lines. */}
                  {/* The context lines show: `m.role === 'assistant' && ( ... Latency Evidence ... )` */}
                  {/* Wait, the previous code block was inside `m.role === 'assistant'`. */}
                  {/* If I want it to persist, I should move it to the USER message, OR keep it on the Assistant message. */}
                  {/* If I keep it on the Assistant: `isLastMessage` is true. */}
                  {/* Why did it vanish? */}
                  {/* "The View Graph area... matches the moment I click send". */}
                  {/* If I move it to the User Message, it's visible immediately. */}
                  {/* If I leave it on the Assistant, it only appears when Assistant appears. */}
                  {/* User said "from the moment I click send". So it MUST be on the User Message (or a temporary "Thinking" bubble). */}
                  {/* The screenshot shows it separate? The "Status Indicator" is separate. */}
                  {/* I will move the Latency Evidence to the USER message block, specifically for the latest user message. */}

                  {isLatestUserMessage && (isLoading || lastLatency) && (
                    <div className="mt-1 flex items-center gap-1.5 justify-end opacity-80">
                      {/* Optional "View Graph" if we want it here too? No, View Graph is usually for the Result. */}
                      {/* But the user said "View Graph area... where it should remain steady". */}
                      {/* Maybe they mean the status bubble at the bottom? */}
                      {/* "Observe the 'View Graph' area...". */}
                      {/* If "View Graph" is on the assistant message, it shouldn't vanish unless `isLastMessage` check removed it. */}
                      {/* `isLastMessage` checked if *Assistant* was last. It usually IS last. */}
                      {/* Why did it vanish? Maybe `isLoading || lastLatency` became false? No, `lastLatency` is set. */}
                      {/* Maybe `isLastMessage` became false because a NEW empty message appeared? Unlikely. */}
                      {/* I will move the timer to the User Message to be safe and "start from send". */}
                      <div className="flex items-center gap-1.5 text-xs text-[var(--text-muted)] bg-[var(--bg-card)] px-3 py-1 rounded-full border border-[var(--border)]">
                        <Clock size={12} />
                        {isLoading && startTime ? (
                          <ThinkingTimer startTime={startTime} />
                        ) : (
                          <span className="font-mono font-medium">{lastLatency}s</span>
                        )}
                      </div>
                    </div>
                  )}

                  {/* Status Indicator (Generating...) */}

                  {isStreaming && (
                    <div className="text-xs text-[var(--text-muted)] mt-1 animate-pulse flex items-center gap-1 pl-1">
                      <Activity size={12} />
                      <DynamicStatusText logs={traceLogs} />
                    </div>
                  )}
                  {/* Result Footer for Last Assistant Message */}
                  {m.role === 'assistant' && !isLoading && i === messages.length - 1 && (
                    <div className="mt-1 pl-1 flex items-center gap-2">
                      <MetricsFooter metrics={nodeMetrics} />
                    </div>
                  )}
                </div>
              );
            })}

            {/* Thinking Bubble */}

            {/* Smart Status Bubble */}
            {isLoading && (
              <div className="flex flex-col items-start animate-in fade-in slide-in-from-bottom-2 duration-300 mb-4">
                <div className={clsx(
                  "border rounded-2xl rounded-bl-none p-4 px-6 shadow-sm flex items-center gap-3",
                  isDark ? "bg-[var(--bg-app)] border-[var(--border)] text-[var(--text-primary)]" : "bg-white border-gray-100 text-slate-800"
                )}>
                  <div className="flex gap-1">
                    <span className="w-2 h-2 bg-[var(--brand)] rounded-full animate-bounce [animation-delay:-0.3s]"></span>
                    <span className="w-2 h-2 bg-[var(--brand)] rounded-full animate-bounce [animation-delay:-0.15s]"></span>
                    <span className="w-2 h-2 bg-[var(--brand)] rounded-full animate-bounce"></span>
                  </div>
                  <span className="text-sm text-[var(--text-muted)] font-medium flex items-center gap-2">
                    <DynamicStatusText logs={traceLogs} />
                    <span className="opacity-50">|</span>
                    {startTime && <ThinkingTimer startTime={startTime} />}
                  </span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input Area - REVERTED TO COMPACT */}
          <div className={clsx("p-4 border-t bg-transparent shrink-0", isDark ? "border-white/10" : "border-gray-100")}>
            {/* Image Preview */}
            {image && (
              <div className="relative inline-block mb-2 group">
                <img src={`data:image/png;base64,${image}`} alt="Preview" className="h-20 w-20 object-cover rounded-lg border border-white/20" />
                <button
                  onClick={clearImage}
                  className="absolute -top-1 -right-1 bg-black/50 text-white rounded-full p-1 hover:bg-black/80 transition-colors"
                >
                  <X size={14} />
                </button>
              </div>
            )}
            <div className="relative w-full min-w-0">
              <form onSubmit={handleSubmit} className="flex items-end gap-2 bg-[var(--bg-app)] border border-[var(--border)] rounded-xl p-1.5 focus-within:border-[var(--brand)]/30 transition-all">
                <input
                  type="file"
                  ref={fileInputRef}
                  className="hidden"
                  accept="image/*"
                  onChange={handleFileChange}
                />
                <button
                  type="button"
                  onClick={() => fileInputRef.current?.click()}
                  disabled={isLoading}
                  className={clsx(
                    "p-2 rounded-lg transition-colors shrink-0",
                    isDark ? "text-gray-500 hover:text-gray-300" : "text-slate-400 hover:text-slate-600"
                  )}
                >
                  <ImageIcon size={18} />
                </button>
                <textarea
                  ref={textareaRef}
                  value={input}
                  onChange={handleInputChange}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                      e.preventDefault();
                      e.currentTarget.form?.requestSubmit();
                    }
                  }}
                  placeholder="Ask anything..."
                  rows={1}
                  className={clsx(
                    "w-full py-2 px-1 outline-none transition-all text-sm min-w-0 flex-1 resize-none overflow-y-auto no-scrollbar bg-transparent",
                    isDark ? "placeholder:text-gray-600 text-gray-200" :
                      "placeholder:text-slate-400 text-slate-800"
                  )}
                />
                <button
                  disabled={isLoading || !input.trim()}
                  type="submit"
                  className="w-10 h-10 flex items-center justify-center bg-white text-black rounded-lg hover:bg-zinc-200 disabled:opacity-20 disabled:hover:bg-white transition-all shrink-0 self-center"
                >
                  <Send size={18} />
                </button>
              </form>
            </div>
          </div>
        </div>

        {/* GRAPH TAB */}
        <div className={`absolute inset-0 bg-[var(--bg-app)] ${activeTab === 'graph' ? 'z-10' : 'hidden'}`}>
          <AgentGraph
            topology={topology}
            executionPath={executionPath}
            activeNodeId={executionPath[executionPath.length - 1]}
            nodeDurations={nodeDurations}
            nodeMetrics={nodeMetrics}
          />
        </div>

        {/* TRACE TAB */}
        <div className={`absolute inset-0 bg-[var(--bg-app)] overflow-y-auto ${activeTab === 'trace' ? 'z-10' : 'hidden'}`}>
          <TraceLog logs={traceLogs} selectedModel={selectedModel} isLoading={isLoading} />
        </div>

        {/* REASONING TAB */}
        <div className={`absolute inset-0 bg-[var(--bg-app)] ${activeTab === 'reasoning' ? 'z-10' : 'hidden'}`}>
          <ReasoningTab sessionId={sessionId} isActive={activeTab === 'reasoning'} />
        </div>

        {/* REPORTS TAB - REMOVED */}


      </div>
    </div>
  );
};

// UI Helper
const TabButton = ({ active, onClick, icon, label, isDark, isChatMaximized }: any) => (
  <button
    onClick={onClick}
    className={clsx(
      "flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-bold transition-all duration-200",
      active
        ? "bg-[var(--brand)] text-white shadow-lg"
        : isDark
          ? "text-gray-400 hover:bg-white/5 hover:text-white"
          : "text-slate-500 hover:bg-slate-200 hover:text-slate-800"
    )}
  >
    {icon}
    <span className={clsx(
      "leading-none truncate",
      isChatMaximized ? "inline-block max-w-[80px]" : "hidden"
    )}>{label}</span>
  </button>
);

export default AdvancedPanel;
