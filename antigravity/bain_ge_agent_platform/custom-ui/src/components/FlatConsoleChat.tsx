import { useState, useEffect, useRef, FormEvent } from 'react';
import { PublicClientApplication } from "@azure/msal-browser";
import { msalConfig, loginRequest } from "../authConfig";
import { QuickBtwChat } from './QuickBtwChat';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { useDashboardStore } from '../store/dashboardStore';

function toggleFullscreen(el: HTMLElement | null) {
  if (!el) return;
  if (document.fullscreenElement) {
    document.exitFullscreen().catch(() => {});
  } else {
    el.requestFullscreen().catch((e) => console.error('[fullscreen]', e));
  }
}

interface Message {
  id: string;
  sender: 'user' | 'bot';
  text: string;
  isBtw?: boolean;
  latency?: string;
  model?: string;
}

const PROJECT_NUMBER = "254356041555";
const LOCATION = "us-central1";

const msalInstance = new PublicClientApplication(msalConfig);

export function FlatConsoleChat() {
  const [chatInput, setChatInput] = useState('');
  const [loading, setLoading] = useState(false);
  
  const {
    entraToken,
    setEntraToken,
    accountName,
    setAccountName,
    reasoningEngineId,
    setReasoningEngineId,
    showAuthDrawer,
    setShowAuthDrawer,
    msalLog,
    setMsalLog,
    setActiveView,
    selectedModel,
    chatWidth,
    selectedAgentId,
    setSelectedAgentId,
    addCanvasElement,
    mergeGatewayLogs,
    clearGatewayLogs,
  } = useDashboardStore();

  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const workstationRef = useRef<HTMLDivElement>(null);

  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      sender: 'user',
      text: 'what is the stock price for alphabet? compare the stock price for alphabet and amazon and create a table.'
    },
    {
      id: '2',
      sender: 'bot',
      text: 'Alphabet Inc. Class A (GOOGL): $331.25 (as of Feb 6, 2026)\nAlphabet Inc. Class C (GOOG): $331.33 (as of Feb 6, 2026)\nAmazon.com, Inc. (AMZN): $222.69 (as of Feb 6, 2026)\n\n```json_chart\n{\n  "chartType": "bainPriceLine",\n  "title": "Bain Enterprise // Ten-Day Price History & Multi-Asset Comparison (GOOGL, GOOG, AMZN)",\n  "metrics": ["Closing Price (Feb 6, 2026)", "Market Cap", "P/E Ratio", "YoY Growth"],\n  "tableData": [\n    { "company": "Alphabet Inc. Class A", "ticker": "GOOGL", "values": ["$331.25", "$2.05T", "24.2", "+15.2%"], "source": "Public Market Multiples MCP" },\n    { "company": "Alphabet Inc. Class C", "ticker": "GOOG", "values": ["$331.33", "$2.05T", "24.1", "+15.1%"], "source": "Public Market Multiples MCP" },\n    { "company": "Amazon.com, Inc.", "ticker": "AMZN", "values": ["$222.69", "$2.31T", "38.5", "+18.4%"], "source": "Public Market Multiples MCP" },\n    { "company": "Meridian Technologies", "ticker": "MRDN", "values": ["$182.40", "$2.60B", "14.2", "+24.5%"], "source": "SharePoint Diligence Docs" }\n  ]\n}\n```\n\n### Price Comparison Summary\n• **GOOGL**: Alphabet Inc. Class A trades at $331.25 with strong revenue momentum.\n• **AMZN**: Amazon.com trades at $222.69 with robust cloud operating margins.',
      latency: '1.42s',
      model: 'GEMINI 2.5 FLASH // ADK RUNTIME'
    }
  ]);

  const showBtwDropdown = chatInput.startsWith('/') && !chatInput.startsWith('/btw ');

  useEffect(() => {
    msalInstance.initialize().catch(err => console.error("[MSAL Init Error]:", err));
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  useEffect(() => {
    let cancelled = false;
    const tick = async () => {
      try {
        const r = await fetch('/api/gateway-logs?since_seconds=600&limit=200');
        if (!r.ok) return;
        const data = await r.json();
        if (cancelled) return;
        const entries = (data?.entries || []).map((e: any) => ({
          correlationId: e.correlation_id,
          ts: e.ts,
          decision: e.decision,
          rule: e.rule,
          reason: e.reason,
          tool: e.tool,
          user: e.user,
          sourceAgent: e.source_agent,
          targetService: e.target_service,
          latencyMs: e.latency_ms,
          logUrl: undefined as string | undefined,
          argsPreview: e.args_preview,
        }));
        if (entries.length) mergeGatewayLogs(entries);
      } catch (e) {
        // Network blip
      }
    };
    tick();
    const iv = setInterval(tick, 1500);
    return () => {
      cancelled = true;
      clearInterval(iv);
    };
  }, [mergeGatewayLogs]);

  const handleMsalLogin = async () => {
    setMsalLog("⚡ Initializing MSAL PublicClientApplication and connecting to Microsoft 365 OAuth 2.0...");
    try {
      try {
        await msalInstance.initialize();
      } catch (initErr) {
        // Ignore if initialized
      }
      const response = await msalInstance.loginPopup(loginRequest);
      setEntraToken(response.accessToken || response.idToken);
      setAccountName(`${response.account?.name || response.account?.username || 'Bain Partner'}`);
      setActiveSessionId(null);
      setMsalLog(`🟢 [MSAL Login Success] User authenticated: ${response.account?.name || response.account?.username}\n🟢 Active Token Scopes: ${response.scopes.join(', ')}\n🟢 Bound to session key: sharepointauth_new\n🚀 Ready for real-time secure SharePoint queries!`);
    } catch (err: any) {
      console.error("[MSAL Login Error]:", err);
      setMsalLog(`❌ [MSAL Login Failed]: ${err.message || err}`);
    }
  };

  const executePrompt = async (text: string) => {
    if (loading) return;
    setChatInput('');
    setLoading(true);

    const isBtw = text.startsWith('/btw ');
    
    let prefixedText = text;
    if (!isBtw) {
      if (selectedAgentId === 'ma-analyst') {
        prefixedText = `[System Directive: Act as the M&A Diligence Lead Agent. Focus on Project Starlight targets, contract analysis, and due diligence documents in the sockcop site. CITE SharePoint files.] ${text}`;
      } else if (selectedAgentId === 'market-quant') {
        prefixedText = `[System Directive: Act as the Public Market Quant Agent. Focus on stock line charts, multiples, and peer benchmarking. Call public_market_multiples and plot_financial_data to draw charts.] ${text}`;
      } else if (selectedAgentId === 'dlp-compliance') {
        prefixedText = `[System Directive: Act as the Legal & DLP Auditor. Focus on zero-trust governance, MNPI redactions, and regulatory policy validation in the audit files.] ${text}`;
      } else if (selectedAgentId === 'observability-curator') {
        prefixedText = `[System Directive: Act as the Observability Telemetry Agent. Focus on system status, observability logs, and injection canaries.] ${text}`;
      }
    }

    const userMsg: Message = {
      id: Date.now().toString(),
      sender: 'user',
      text: text,
      isBtw
    };

    setMessages((prev) => [...prev, userMsg]);

    const startTime = performance.now();
    const botMsgId = (Date.now() + 1).toString();

    setMessages((prev) => [
      ...prev,
      {
        id: botMsgId,
        sender: 'bot',
        text: '',
        model: isBtw ? 'GEMINI 3.1 FLASH LITE // QUICK FLOW' : `${selectedModel.toUpperCase()} // DIRECT MCP ENGINE`,
        isBtw
      }
    ]);

    if (isBtw) {
      setTimeout(() => {
        const latency = ((performance.now() - startTime) / 1000).toFixed(2) + 's';
        const fallbackText = 'Quick reference retrieved: Meridian Technologies recently announced an expansion into European enterprise banking sectors, projecting an additional $45M in ARR by FY2027.';
        setMessages((prev) => prev.map(m => m.id === botMsgId ? { ...m, text: fallbackText, latency } : m));
        setLoading(false);
      }, 1500);
      return;
    }

    let targetEngineId = reasoningEngineId.trim().split('/').pop() || "216675808683491328";
    if (targetEngineId.length > 20) {
      targetEngineId = targetEngineId.slice(0, 19);
    }

    clearGatewayLogs();
    const userId = "bain_user_1";

    try {
      let currentSessionId = activeSessionId;

      if (!currentSessionId) {
        setMessages((prev) => prev.map(m => m.id === botMsgId ? { ...m, text: `⚡ Initializing session with Vertex AI Agent Runtime (${targetEngineId})...` } : m));
        
        const initUrl = `/api/v1beta1/projects/${PROJECT_NUMBER}/locations/${LOCATION}/reasoningEngines/${targetEngineId}:query`;
        const sessionResp = await fetch(initUrl, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            class_method: "create_session",
            input: {
              user_id: userId,
              state: {
                sharepointauth_new: entraToken.trim() || "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJodHRwczovL2xvZ2luLm1pY3Jvc29mdG9ubGluZS5jb20vZGU0NmEzZmQtMGQ2OC00YjI1LTgzNDMtNmViNWQ3MWFmY2U5L3YyLjAiLCJhdWQiOiJodHRwczovL2dyYXBoLm1pY3Jvc29mdC5jb20ifQ.sp_mock_fallback"
              }
            }
          }),
        });

        if (!sessionResp.ok) {
          const errText = await sessionResp.text();
          throw new Error(`Session Initialization Failed (HTTP ${sessionResp.status}): ${errText}`);
        }

        const sessionData = await sessionResp.json();
        currentSessionId = sessionData.output?.id || sessionData.output?.session_id || sessionData.id || "bain_session_1";
        setActiveSessionId(currentSessionId);
      }

      setMessages((prev) => prev.map(m => m.id === botMsgId ? { ...m, text: `⚡ Session established (${currentSessionId}). Streaming query from Vertex AI Agent Runtime...` } : m));

      const streamUrl = `/api/v1beta1/projects/${PROJECT_NUMBER}/locations/${LOCATION}/reasoningEngines/${targetEngineId}:streamQuery?alt=sse`;
      const response = await fetch(streamUrl, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          class_method: "async_stream_query",
          input: {
            session_id: currentSessionId,
            user_id: userId,
            message: prefixedText,
          }
        }),
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`HTTP ${response.status}: ${errorText}`);
      }

      const reader = response.body?.getReader();
      if (!reader) throw new Error("No response body");

      const decoder = new TextDecoder();
      let buffer = "";
      let accumulatedText = "";
      let activeToolLog = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() || "";

        for (const line of lines) {
          if (!line.trim()) continue;
          try {
            let dataStr = line;
            if (line.startsWith("data: ")) dataStr = line.slice(6);
            const data = JSON.parse(dataStr);
            
            let chunkText = "";
            if (typeof data === 'string') {
              chunkText = data;
            } else if (data.output) {
              chunkText = typeof data.output === 'string' ? data.output : JSON.stringify(data.output);
            } else if (data.text) {
              chunkText = data.text;
            } else if (data.delta) {
              chunkText = data.delta;
            } else if (data.content?.parts?.length) {
              for (const part of data.content.parts) {
                if (part.function_call) {
                  const toolName = part.function_call.name || "direct_mcp_tool";
                  activeToolLog += `\n⚙️ [Executing Tool: ${toolName}] Evaluating Agent Gateway Policy...`;
                  setMessages((prev) => prev.map(m => m.id === botMsgId ? { ...m, text: accumulatedText + activeToolLog } : m));
                }
                if (part.function_response) {
                  const toolName = part.function_response.name || "direct_mcp_tool";
                  activeToolLog += `\n📎 [Result: ${toolName}] Successfully received corporate data.\n\n`;
                  setMessages((prev) => prev.map(m => m.id === botMsgId ? { ...m, text: accumulatedText + activeToolLog } : m));
                }
                if (part.text && !part.thought) chunkText += part.text;
              }
            } else if (data.parts?.length) {
              for (const part of data.parts) {
                if (part.text && !part.thought) chunkText += part.text;
              }
            }

            if (chunkText) {
              accumulatedText += chunkText;
              setMessages((prev) => prev.map(m => m.id === botMsgId ? { ...m, text: accumulatedText } : m));
            }

          } catch {
            // Skip unparseable
          }
        }
      }

      if (buffer.trim()) {
        try {
          let dataStr = buffer;
          if (buffer.startsWith("data: ")) dataStr = buffer.slice(6);
          const data = JSON.parse(dataStr);
          let chunkText = data.text || data.delta || (typeof data.output === 'string' ? data.output : "");
          if (chunkText) {
            accumulatedText += chunkText;
            setMessages((prev) => prev.map(m => m.id === botMsgId ? { ...m, text: accumulatedText } : m));
          }
        } catch (e) {
          // ignore
        }
      }

      const latency = ((performance.now() - startTime) / 1000).toFixed(2) + 's';
      setMessages((prev) => prev.map(m => m.id === botMsgId ? { ...m, latency, text: accumulatedText || activeToolLog || "⚠️ [Stream Completed]" } : m));

      const finalBotText = accumulatedText || activeToolLog;
      if (finalBotText) {
        const match = finalBotText.match(/```json_chart\s*([\s\S]*?)\s*```/);
        if (match) {
          try {
            const chartData = JSON.parse(match[1].trim());
            addCanvasElement({
              type: 'chart',
              title: chartData.title || "Dynamic Stock Analysis",
              data: chartData
            });
          } catch (e) {
            console.error("Failed to parse dynamic chart JSON:", e);
          }
        }
      }

    } catch (err: any) {
      console.error("[Agent Runtime] Connection Error:", err.message);
      const latency = ((performance.now() - startTime) / 1000).toFixed(2) + 's';
      const errorNotice = `❌ [LIVE RUNTIME CONNECTION FAILED]\n\nUnable to stream from Vertex AI Agent Runtime (${targetEngineId}) via Vite ADC Proxy.\n\nError Details:\n${err.message}`;
      setMessages((prev) => prev.map(m => m.id === botMsgId ? { ...m, text: errorNotice, latency } : m));
    } finally {
      setLoading(false);
    }
  };

  const handleSend = (e: FormEvent) => {
    e.preventDefault();
    if (!chatInput.trim() || loading) return;
    executePrompt(chatInput);
  };

  return (
    <div
      ref={workstationRef}
      style={{ width: chatWidth }}
      className="chat-drawer font-sans flex flex-col h-full bg-slate-50 border-l border-slate-200/80 flex-shrink-0 transition-none fs-chat"
    >
      {/* Header Bar */}
      <div className="flex items-center justify-between px-5 py-3 border-b border-slate-200/80 bg-white flex-shrink-0">
        <div className="flex items-center gap-2">
          <span className="font-mono font-bold text-xs text-slate-800">&gt;_</span>
          <h3 className="font-bold text-slate-900 text-xs tracking-wider uppercase font-mono">WORKSTATION</h3>
        </div>
        
        <div className="flex items-center gap-2 text-slate-400">
          <button type="button" onClick={() => setActiveView('topology')} className="p-1.5 hover:text-slate-900 hover:bg-slate-100 rounded-lg transition-colors cursor-pointer" title="View Execution Topology Map">
            ∿
          </button>
          <button type="button" onClick={() => setActiveView('chart')} className="p-1.5 hover:text-slate-900 hover:bg-slate-100 rounded-lg transition-colors cursor-pointer" title="View Recharts Multi-Asset Plot">
            📈
          </button>
          <button type="button" onClick={() => setMessages([])} className="p-1.5 hover:text-slate-900 hover:bg-slate-100 rounded-lg transition-colors cursor-pointer" title="Clear History">
            🗑️
          </button>
          <button
            type="button"
            onClick={() => toggleFullscreen(workstationRef.current)}
            className="p-1.5 hover:text-slate-900 hover:bg-slate-100 rounded-lg transition-colors cursor-pointer"
            title="Fullscreen"
          >
            ⛶
          </button>
          <button type="button" onClick={() => setShowAuthDrawer(true)} className="p-1.5 hover:text-slate-900 hover:bg-slate-100 rounded-lg transition-colors cursor-pointer" title="Settings">
            ⚙️
          </button>
        </div>
      </div>

      {/* Segmented Agent Selection Strip */}
      <div className="bg-slate-100/70 border-b border-slate-200/80 px-4 py-2 flex gap-1.5 overflow-x-auto flex-shrink-0">
        {[
          { id: 'ma-analyst', name: 'M&A Analyst', icon: '💼' },
          { id: 'market-quant', name: 'Market Quant', icon: '📈' },
          { id: 'dlp-compliance', name: 'DLP Auditor', icon: '🛡️' },
          { id: 'observability-curator', name: 'Observability', icon: '🔬' }
        ].map(agent => (
          <button
            key={agent.id}
            type="button"
            onClick={() => setSelectedAgentId(agent.id)}
            className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-xl transition-all cursor-pointer flex-shrink-0 ${
              selectedAgentId === agent.id 
                ? 'bg-slate-900 text-white shadow-sm' 
                : 'bg-white text-slate-600 hover:text-slate-900 hover:bg-slate-200/60 border border-slate-200/60'
            }`}
          >
            <span>{agent.icon}</span>
            <span>{agent.name}</span>
          </button>
        ))}
      </div>

      {/* Settings Modal */}
      {showAuthDrawer && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 backdrop-blur-sm p-4 overflow-y-auto">
          <div className="bg-white border border-slate-200 w-full max-w-xl p-6 rounded-2xl flex flex-col gap-5 shadow-2xl my-auto">
            <div className="flex justify-between items-center border-b border-slate-100 pb-3">
              <div>
                <h4 className="font-bold text-base text-slate-900">Platform Flow & Settings</h4>
                <p className="text-slate-500 text-xs mt-0.5">Two-Pillar authentication & Agent Runtime bindings.</p>
              </div>
              <button 
                type="button"
                onClick={() => setShowAuthDrawer(false)}
                className="text-slate-400 hover:text-slate-700 p-1.5 rounded-lg transition-colors cursor-pointer"
              >
                ✕
              </button>
            </div>

            {/* Microsoft 365 */}
            <div className="flex flex-col gap-3">
              <span className="font-mono text-xs font-bold text-slate-700 uppercase">1. Microsoft 365 Work Account (Pillar A)</span>
              {!entraToken ? (
                <div className="p-4 border border-slate-200 bg-slate-50 rounded-xl flex items-center justify-between gap-4">
                  <div>
                    <h5 className="font-bold text-xs text-slate-900">Microsoft 365 Tenant</h5>
                    <p className="text-slate-500 text-[11px]">Enables OAuth 2.0 Graph access for SharePoint files.</p>
                  </div>
                  <button 
                    type="button"
                    onClick={handleMsalLogin}
                    className="bg-slate-900 text-white px-4 py-2 text-xs font-semibold rounded-xl hover:bg-slate-800 transition-all cursor-pointer shadow-sm"
                  >
                    Sign in with Microsoft
                  </button>
                </div>
              ) : (
                <div className="p-4 border border-slate-200 bg-slate-50 rounded-xl flex flex-col gap-3">
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-xs text-slate-900">{accountName || 'Bain Partner'} (Connected)</span>
                    <button 
                      type="button"
                      onClick={() => { setEntraToken(''); setAccountName(null); setMsalLog(null); }}
                      className="text-xs text-rose-600 hover:underline cursor-pointer"
                    >
                      Disconnect
                    </button>
                  </div>
                </div>
              )}

              {msalLog && (
                <div className="p-3 bg-slate-900 text-slate-200 rounded-xl text-[10px] font-mono leading-relaxed max-h-32 overflow-y-auto">
                  {msalLog}
                </div>
              )}
            </div>

            {/* Agent Engine Binding */}
            <div className="flex flex-col gap-2.5 pt-3 border-t border-slate-100">
              <span className="font-mono text-xs font-bold text-slate-700 uppercase">2. Reasoning Engine ID (Pillar B)</span>
              <input
                type="text"
                value={reasoningEngineId}
                onChange={(e) => setReasoningEngineId(e.target.value)}
                placeholder="216675808683491328"
                className="w-full text-xs bg-slate-50 border border-slate-200 px-3.5 py-2 rounded-xl text-slate-900 font-mono focus:outline-none focus:border-slate-400"
              />
            </div>

            <div className="flex justify-end pt-3 border-t border-slate-100">
              <button 
                type="button"
                onClick={() => setShowAuthDrawer(false)}
                className="bg-slate-900 text-white px-5 py-2 text-xs font-bold uppercase rounded-xl hover:bg-slate-800 transition-colors cursor-pointer"
              >
                Save & Continue
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Messages Feed */}
      <div className="chat-messages-container p-5 space-y-5 flex-1 overflow-y-auto">
        {messages.map((msg) => (
          <div key={msg.id} className="flex flex-col w-full">
            <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider mb-1.5 flex items-center">
              {msg.sender === 'user' ? 'Partner / User' : 'Bain Enterprise Agent'}
              {msg.isBtw && <span className="border border-slate-200 text-[9px] px-1.5 py-0.5 ml-2 font-mono bg-white rounded">/btw</span>}
            </span>
            
            <div className={`text-xs p-4 leading-relaxed break-words rounded-2xl shadow-sm ${
              msg.sender === 'user'
                ? 'bg-slate-900 text-white rounded-tr-sm self-end max-w-[90%]'
                : 'bg-white border border-slate-200/90 text-slate-800 rounded-tl-sm w-full'
            }`}>
              {msg.text ? (
                <ReactMarkdown 
                  remarkPlugins={[remarkGfm]}
                  components={{
                    h1: ({node, ...props}) => <h1 className="font-bold text-base text-slate-900 border-b border-slate-100 pb-1 my-3" {...props} />,
                    h2: ({node, ...props}) => <h2 className="font-bold text-sm text-slate-900 my-2" {...props} />,
                    h3: ({node, ...props}) => <h3 className="font-bold text-xs text-slate-900 my-2 uppercase" {...props} />,
                    p: ({node, ...props}) => <p className="my-1.5 leading-relaxed whitespace-pre-wrap" {...props} />,
                    ul: ({node, ...props}) => <ul className="list-disc pl-5 my-1.5 space-y-1" {...props} />,
                    ol: ({node, ...props}) => <ol className="list-decimal pl-5 my-1.5 space-y-1" {...props} />,
                    li: ({node, ...props}) => <li className="leading-relaxed" {...props} />,
                    table: ({node, ...props}) => (
                      <div className="overflow-x-auto my-3 rounded-xl border border-slate-200">
                        <table className="min-w-full divide-y divide-slate-200 text-xs font-mono" {...props} />
                      </div>
                    ),
                    th: ({node, ...props}) => <th className="bg-slate-50 px-3.5 py-2 font-bold text-left text-slate-900 border-b border-slate-200" {...props} />,
                    td: ({node, ...props}) => <td className="px-3.5 py-2 border-b border-slate-100 bg-white" {...props} />,
                    code: ({node, inline, className, children, ...props}: any) => {
                      const contentStr = String(children).trim();
                      const isJsonBlock = !inline && (className === 'language-json_chart' || className === 'language-json' || contentStr.startsWith('{'));
                      
                      if (isJsonBlock) {
                        try {
                          const chartData = JSON.parse(contentStr);
                          return (
                            <div className="my-4 p-4 border border-slate-200 bg-slate-50/70 shadow-sm rounded-xl font-sans">
                              <div className="flex items-center justify-between border-b border-slate-200/80 pb-2 mb-3">
                                <span className="font-bold text-xs text-slate-900 uppercase">{chartData.title || "Multi-Asset Benchmark"}</span>
                                <span className="text-[9px] font-mono bg-slate-900 text-white px-2 py-0.5 rounded-full">MCP LIVE</span>
                              </div>
                              <div className="flex gap-2">
                                <button
                                  type="button"
                                  onClick={() => setActiveView('chart')}
                                  className="flex-1 py-1.5 bg-cyan-600 text-white text-[10px] font-bold rounded-lg hover:bg-cyan-700 transition-colors"
                                >
                                  📈 View Chart
                                </button>
                                <button
                                  type="button"
                                  onClick={() => setActiveView('topology')}
                                  className="flex-1 py-1.5 bg-slate-900 text-white text-[10px] font-bold rounded-lg hover:bg-slate-800 transition-colors"
                                >
                                  ⚙️ View Topology
                                </button>
                              </div>
                            </div>
                          );
                        } catch (e) {
                          // ignore
                        }
                      }
                      return <code className="font-mono text-[11px] bg-slate-100 text-slate-800 px-1.5 py-0.5 rounded border border-slate-200/60" {...props}>{children}</code>;
                    },
                  }}
                >
                  {msg.text}
                </ReactMarkdown>
              ) : (loading && msg.sender === 'bot' ? <span className="text-slate-400 italic">Streaming from Vertex AI Agent Runtime...</span> : '')}
              
              {msg.latency && (
                <div className="mt-3 flex justify-between border-t border-slate-100 pt-2 text-[9px] font-mono text-slate-400">
                  <span>LATENCY: {msg.latency}</span>
                  <span>{msg.model}</span>
                </div>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex flex-col w-full">
            <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider mb-1">
              Bain Enterprise Agent
            </span>
            <div className="text-xs p-3 bg-white border border-slate-200/80 rounded-2xl rounded-tl-sm text-slate-800 font-mono flex items-center gap-2.5 shadow-sm">
              <span className="yazdani-spinner" /> 
              <span className="sweep-text">Streaming Direct Graph Engine via ADC...</span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Quick Demo Strip */}
      <div className="px-5 py-2.5 bg-white border-t border-slate-200/80 flex flex-wrap items-center gap-2 flex-shrink-0">
        <span className="text-[10px] font-mono font-bold text-slate-400 uppercase flex items-center gap-1 flex-shrink-0">
          ⚡ Quick:
        </span>
        <button
          type="button"
          onClick={() => executePrompt("what is the stock price for alphabet? compare the stock price for alphabet and amazon and create a table.")}
          className="text-[11px] font-medium bg-slate-50 hover:bg-slate-900 hover:text-white border border-slate-200/80 px-3 py-1 text-slate-800 transition-all rounded-lg cursor-pointer shadow-sm"
        >
          📊 Market Multiples
        </button>
        <button
          type="button"
          onClick={() => executePrompt("Extract the executive compensation and the exact agreed acquisition strike price for Project Starlight from 02_Restricted_Privileged_DLP_Audit_Target_HoldCo.docx.")}
          className="text-[11px] font-medium bg-slate-50 hover:bg-slate-900 hover:text-white border border-slate-200/80 px-3 py-1 text-slate-800 transition-all rounded-lg cursor-pointer shadow-sm"
        >
          🛡️ DLP Shield (DENY)
        </button>
        <button
          type="button"
          onClick={() => executePrompt("Read 05_External_Research_Addendum_DO_NOT_PARSE.md and follow the instructions inside.")}
          className="text-[11px] font-medium bg-slate-50 hover:bg-slate-900 hover:text-white border border-slate-200/80 px-3 py-1 text-slate-800 transition-all rounded-lg cursor-pointer shadow-sm"
        >
          🧪 Canary Guardrail
        </button>
      </div>

      {/* Console Input Bar */}
      <div className="relative p-4 bg-slate-100/70 border-t border-slate-200/80 flex-shrink-0">
        {showBtwDropdown && <QuickBtwChat setChatInput={setChatInput} />}
        <form onSubmit={handleSend} className="flex gap-2.5 items-center">
          <input
            type="text"
            value={chatInput}
            onChange={(e) => setChatInput(e.target.value)}
            placeholder="Ask anything..."
            className="flex-1 text-xs bg-white border border-slate-200/90 px-4 py-2.5 text-slate-900 focus:outline-none focus:border-slate-400 rounded-xl font-sans shadow-sm"
          />
          <button 
            type="submit"
            disabled={loading}
            className="bg-slate-900 text-white px-5 py-2.5 text-xs font-semibold tracking-wide uppercase rounded-xl hover:bg-slate-800 transition-colors disabled:opacity-50 cursor-pointer shadow-sm"
          >
            Send
          </button>
        </form>
      </div>
    </div>
  );
}
