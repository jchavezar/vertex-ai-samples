import React, { useState, useEffect } from 'react';
import { MessageSquare, Share2, Activity, Terminal, Maximize2, Minimize2, ChevronsRight, Clock } from 'lucide-react';
import { clsx } from "clsx";
import { useDashboardStore } from '../../store/dashboardStore';
import AgentGraph from './AgentGraph';
import TraceLog from './TraceLog';
import { StreamingMarkdown } from './StreamingMarkdown';
import { useTerminalChat } from '../../hooks/useTerminalChat';

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
  const [activeTab, setActiveTab] = useState<'chat' | 'graph' | 'trace'>('chat');
  const { messages, input, handleInputChange, handleSubmit, isLoading, traceLogs, topology, executionPath, nodeDurations, nodeMetrics, lastLatency, startTime, selectedModel } = useTerminalChat();
  const { isChatMaximized, toggleChatMaximized, chatDockPosition, theme } = useDashboardStore();
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
          "flex items-center justify-between p-2 pl-3 border-b shrink-0 bg-transparent cursor-grab active:cursor-grabbing select-none",
          isDark ? "border-white/10" : "border-gray-100"
        )}
        onPointerDown={onDragStart}
        onDoubleClick={() => {
          const current = useDashboardStore.getState().chatDockPosition;
          useDashboardStore.getState().setChatDockPosition(current === 'right' ? 'floating' : 'right');
        }}
      >
        <div className="flex items-center gap-2 overflow-hidden">
          <button
            onClick={() => setActiveTab('chat')} // "Home" action: Back to chat
            className={clsx(
              "p-1.5 rounded-lg shrink-0 transition-colors cursor-pointer",
              isDark ? "bg-[var(--brand)]/10 text-[var(--brand)] hover:bg-[var(--brand)]/20" : "bg-blue-50 text-blue-600 hover:bg-blue-100"
            )}
            title="Home / Reset View"
          >
            <Terminal size={16} />
          </button>
          <div className="min-w-0">
            <h2 className={clsx("text-sm font-bold truncate", isDark ? "text-[var(--text-primary)]" : "text-slate-800")}>Terminal</h2>
            <div className={clsx("flex items-center gap-1 text-[10px] shrink-0", isDark ? "text-[var(--text-muted)]" : "text-slate-500")}>
              <span className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse" />
              Online
            </div>
          </div>
        </div>

          <div className="flex items-center gap-1 shrink-0">
          {/* Tabs - Now more visible */}
          <div className={clsx(
            "flex rounded-lg p-0.5 border",
            isDark ? "bg-black/40 border-white/10" : "bg-slate-100 border-slate-200"
          )}>
            <TabButton
              active={activeTab === 'chat'}
              onClick={() => setActiveTab('chat')}
              icon={<MessageSquare size={13} />}
              label="Chat"
              isDark={isDark}
            />
            <TabButton
              active={activeTab === 'graph'}
              onClick={() => setActiveTab('graph')}
              icon={<Share2 size={13} />}
              label="Graph"
              isDark={isDark}
            />
            <TabButton
              active={activeTab === 'trace'}
              onClick={() => setActiveTab('trace')}
              icon={<Activity size={13} />}
              label="Trace"
              isDark={isDark}
            />
          </div>

          {/* Actions */}
          <div className="flex items-center gap-1 pl-2 border-l border-[var(--border)]">
            <button
              onClick={toggleChatMaximized}
              className={clsx(
                "p-1.5 rounded-md transition-colors",
                isDark ? "text-[var(--text-muted)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-app)]" : "text-slate-500 hover:text-slate-800 hover:bg-slate-100"
              )}
              title={isChatMaximized ? "Restore" : "Maximize"}
            >
              {isChatMaximized ? <Minimize2 size={14} /> : <Maximize2 size={14} />}
            </button>
            <button
              onClick={() => {
                const current = useDashboardStore.getState().chatDockPosition;
                useDashboardStore.getState().setChatDockPosition(current === 'right' ? 'floating' : 'right');
              }}
              className={clsx(
                "p-1.5 rounded-md transition-colors",
                isDark ? "text-[var(--text-muted)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-app)]" : "text-slate-500 hover:text-slate-800 hover:bg-slate-100"
              )}
              title={chatDockPosition === 'right' ? "Undock (Overlay)" : "Dock to Sidebar"}
            >
              {chatDockPosition === 'right' ? <Minimize2 size={14} className="rotate-45" /> : <Maximize2 size={14} className="-rotate-45" />}
            </button>
            <button
              onClick={() => useDashboardStore.getState().setChatOpen(false)}
              className="p-1.5 text-[var(--text-muted)] hover:text-red-500 hover:bg-red-500/10 rounded-md transition-colors flex items-center gap-1"
              title="Hide Sidebar"
            >
              <ChevronsRight size={14} />
            </button>
          </div>
        </div>
      </div>

      {/* Content Area */}
      <div className="flex-1 overflow-hidden relative">

        {/* CHAT TAB */}
        <div className={`absolute inset-0 flex flex-col transition-opacity duration-300 ${activeTab === 'chat' ? 'opacity-100 z-10' : 'opacity-0 z-0 pointer-events-none'}`}>
          <div
            ref={scrollContainerRef}
            onScroll={handleScroll}
            className="flex-1 overflow-y-auto p-4 space-y-4 scroll-smooth"
          >
            {messages.length === 0 && (
              <div className={clsx("h-full flex flex-col items-center justify-center opacity-60", isDark ? "text-[var(--text-muted)]" : "text-slate-400")}>
                <div className={clsx("p-4 rounded-full mb-4", isDark ? "bg-[var(--bg-app)]" : "bg-slate-100")}><Terminal size={32} /></div>
                <p>How can I help you today?</p>
              </div>
            )}
            {messages.map((m, i) => {
              const isAssistant = m.role === 'assistant';
              const isStreaming = isAssistant && i === messages.length - 1 && isLoading;


              // Typewriter Class Logic
              const messageClass = isAssistant ? 'text-[13px] leading-relaxed' : '';


              // Identify if this is the latest user message to attach the active/final timer
              // This ensures the timer persists even after the assistant responds (which makes isLastMessage false)
              const lastUserIndex = messages.reduce((acc, m, idx) => m.role === 'user' ? idx : acc, -1);
              const isLatestUserMessage = m.role === 'user' && i === lastUserIndex;

              return (
                <div key={i} className={`flex flex-col ${m.role === 'user' ? 'items-end' : 'items-start'}`}>
                  {/* Only render bubble if there is content */}
                  {m.content && m.content.trim() !== '' && (
                    <div className={clsx(
                      "max-w-[85%] rounded-2xl p-3 px-4 text-sm shadow-sm",
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
                          className="text-[10px] text-[var(--brand)] hover:underline flex items-center gap-1.5 opacity-70 hover:opacity-100 transition-opacity"
                          title="View Execution Graph"
                        >
                          <Share2 size={11} /> View Graph
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
                      <div className="flex items-center gap-1.5 text-[10px] text-[var(--text-muted)] bg-[var(--bg-card)] px-2 py-0.5 rounded-full border border-[var(--border)]">
                        <Clock size={10} />
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
                    <div className="text-[10px] text-[var(--text-muted)] mt-1 animate-pulse flex items-center gap-1 pl-1">
                      <Activity size={10} />
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
                  "border rounded-2xl rounded-bl-none p-3 px-4 shadow-sm flex items-center gap-3",
                  isDark ? "bg-[var(--bg-app)] border-[var(--border)] text-[var(--text-primary)]" : "bg-white border-gray-100 text-slate-800"
                )}>
                  <div className="flex gap-1">
                    <span className="w-1.5 h-1.5 bg-[var(--brand)] rounded-full animate-bounce [animation-delay:-0.3s]"></span>
                    <span className="w-1.5 h-1.5 bg-[var(--brand)] rounded-full animate-bounce [animation-delay:-0.15s]"></span>
                    <span className="w-1.5 h-1.5 bg-[var(--brand)] rounded-full animate-bounce"></span>
                  </div>
                  <span className="text-xs text-[var(--text-muted)] font-medium flex items-center gap-2">
                    <DynamicStatusText logs={traceLogs} />
                    <span className="opacity-50">|</span>
                    {startTime && <ThinkingTimer startTime={startTime} />}
                  </span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <div className={clsx("p-4 border-t bg-transparent", isDark ? "border-white/10" : "border-gray-100")}>
            <form onSubmit={handleSubmit} className="relative">
              <input
                value={input}
                onChange={handleInputChange}
                placeholder="Ask anything..."
                className={clsx(
                  "w-full rounded-xl py-3 px-4 pr-12 outline-none transition-all text-sm",
                  isDark ? "bg-[var(--bg-app)] border border-[var(--border)] focus:ring-2 focus:ring-[var(--brand)] focus:border-transparent placeholder:text-gray-400 text-gray-200" :
                  "bg-white border border-gray-200 focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 focus:shadow-md placeholder:text-slate-400 text-slate-800"
                )}
              />
              <button
                disabled={isLoading}
                type="submit"
                className="absolute right-2 top-1/2 -translate-y-1/2 p-1.5 bg-[var(--brand)] text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 transition-colors"
              >
                <MessageSquare size={16} />
              </button>
            </form>
          </div>
        </div>

        {/* GRAPH TAB */}
        <div className={`absolute inset-0 bg-[var(--bg-app)] transition-opacity duration-300 ${activeTab === 'graph' ? 'opacity-100 z-10' : 'opacity-0 z-0 pointer-events-none'}`}>
          <AgentGraph
            topology={topology}
            executionPath={executionPath}
            activeNodeId={executionPath[executionPath.length - 1]}
            nodeDurations={nodeDurations}
            nodeMetrics={nodeMetrics}
          />
        </div>

        {/* TRACE TAB */}
        <div className={`absolute inset-0 bg-[var(--bg-app)] transition-opacity duration-300 overflow-y-auto ${activeTab === 'trace' ? 'opacity-100 z-10' : 'opacity-0 z-0 pointer-events-none'}`}>
          <TraceLog logs={traceLogs} selectedModel={selectedModel} />
        </div>

        {/* REPORTS TAB - REMOVED */}


      </div>
    </div>
  );
};

// UI Helper
const TabButton = ({ active, onClick, icon, label, isDark }: any) => (
  <button
    onClick={onClick}
    className={clsx(
      "flex items-center gap-1.5 px-2 py-1 rounded-md text-[11px] font-medium transition-all duration-200",
      active
        ? "bg-[var(--brand)] text-white shadow-md"
        : isDark
          ? "text-[var(--text-muted)] hover:bg-[var(--bg-card)] hover:text-[var(--text-primary)]"
          : "text-slate-500 hover:bg-slate-200 hover:text-slate-800"
    )}
  >
    {icon}
    {/* Hide label on small screens unless active/maximized? No, always show for clarity per user request */}
    <span>{label}</span>
  </button>
);

export default AdvancedPanel;
