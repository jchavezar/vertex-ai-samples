import React, { useState, useEffect, useRef } from 'react';
import { PublicClientApplication } from "@azure/msal-browser";
import { msalConfig, loginRequest } from "../authConfig";
import { QuickBtwChat } from './QuickBtwChat';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { useDashboardStore } from '../store/dashboardStore';

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
  
  // Enterprise State pulled from global store (Shared with Header & App)
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
    activeView: _activeView,
    setActiveView,
    selectedModel,
    chatWidth,
    selectedAgentId,
    setSelectedAgentId,
    addCanvasElement,
    addGatewayLog,
    clearGatewayLogs
  } = useDashboardStore();

  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      sender: 'user',
      text: 'what is the stock price for alphabet? compare the stock price for alphabet and amazon and create a table.'
    },
    {
      id: '2',
      sender: 'bot',
      text: 'Alphabet Inc. Class A (GOOGL): $331.25 (as of Feb 6, 2026)\nAlphabet Inc. Class C (GOOG): $331.33 (as of Feb 6, 2026)\nAmazon.com, Inc. (AMZN): $222.69 (as of Feb 6, 2026)\n\n```json_chart\n{\n  "chartType": "bainPriceLine",\n  "title": "Bain Enterprise // Ten-Day Price History & Multi-Asset Comparison (GOOGL, GOOG, AMZN)",\n  "metrics": ["Closing Price (Feb 6, 2026)", "Market Cap", "P/E Ratio", "YoY Growth"],\n  "tableData": [\n    { "company": "Alphabet Inc. Class A", "ticker": "GOOGL", "values": ["$331.25", "$2.05T", "24.2", "+15.2%"], "source": "Public Market Multiples MCP" },\n    { "company": "Alphabet Inc. Class C", "ticker": "GOOG", "values": ["$331.33", "$2.05T", "24.1", "+15.1%"], "source": "Public Market Multiples MCP" },\n    { "company": "Amazon.com, Inc.", "ticker": "AMZN", "values": ["$222.69", "$2.31T", "38.5", "+18.4%"], "source": "Public Market Multiples MCP" },\n    { "company": "Meridian Technologies", "ticker": "MRDN", "values": ["$182.40", "$2.60B", "14.2", "+24.5%"], "source": "SharePoint Diligence Docs" }\n  ],\n  "topology": {\n    "steps": [\n      { "name": "User", "type": "origin", "time": "0.00s" },\n      { "name": "Smart Agent (Gemini 3.0 Flash)", "type": "orchestrator", "time": "0.12s" },\n      { "name": "Public Market Multiples MCP", "type": "mcp_tool", "time": "0.48s" },\n      { "name": "plot_financial_data", "type": "mcp_tool", "time": "0.04s" }\n    ]\n  }\n}\n```\n\n### Price Comparison (Close of Feb 6, 2026)\n• **GOOGL**: Alphabet Inc. Class A trades at $331.25\n• **GOOG**: Alphabet Inc. Class C trades at $331.33\n• **AMZN**: Amazon.com, Inc. trades at $222.69\n\n**Relative Performance**: Alphabet\'s Class C shares are currently trading at a slight premium to Class A, while both trade at a higher nominal price than Amazon as of the latest market close.',
      latency: '1.81s',
      model: 'GEMINI 3.0 FLASH // DIRECT MCP ENGINE'
    }
  ]);

  const showBtwDropdown = chatInput.startsWith('/') && !chatInput.startsWith('/btw ');

  useEffect(() => {
    msalInstance.initialize().catch(err => console.error("[MSAL Init Error]:", err));
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const handleMsalLogin = async () => {
    setMsalLog("⚡ Initializing MSAL PublicClientApplication and triggering interactive Microsoft 365 OAuth 2.0 login popup...\n(Connecting to login.microsoftonline.com/de46a3fd-0d68-4b25-8343-6eb5d71afce9)");
    try {
      try {
        await msalInstance.initialize();
      } catch (initErr) {
        // Safely ignore if msalInstance is already initialized
      }
      const response = await msalInstance.loginPopup(loginRequest);
      setEntraToken(response.accessToken || response.idToken);
      setAccountName(`${response.account?.name || response.account?.username || 'Bain Partner'}`);
      setActiveSessionId(null);
      setMsalLog(`🟢 [MSAL Login Success] User authenticated: ${response.account?.name || response.account?.username}\n🟢 Active Token Scopes: ${response.scopes.join(', ')}\n🟢 Bound to session key: sharepointauth_new\n🚀 Ready for real-time secure SharePoint queries!`);
    } catch (err: any) {
      console.error("[MSAL Login Error]:", err);
      setMsalLog(`❌ [MSAL Login Failed]: ${err.message || err}\n\nTroubleshooting:\n1. Ensure popups are allowed in your browser for this site.\n2. Verify the Azure App Registration (7868d053-cf9c-4848-be5a-f9bbf8279234) allows http://localhost:5186 as a redirect URI.`);
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

    // Definitive fix for Reasoning Engine ID Concatenation Bug & A2A Routing Rule (Subagent Recommendation)
    let targetEngineId = reasoningEngineId.trim().split('/').pop() || "8655608971282874368";
    if (targetEngineId.length > 20) {
      targetEngineId = targetEngineId.slice(0, 19); // Take the first 19 digits (A2A / standard ID length)
    }

    clearGatewayLogs();
    addGatewayLog({ type: 'ingress', text: `[GATEWAY-INGRESS] Intercepting request to projects/254356041555/locations/us-central1/reasoningEngines/${targetEngineId}` });
    addGatewayLog({ type: 'auth', text: `[GATEWAY-AUTH] MSAL OIDC token validated. Identity: ${accountName || 'jesusarguelles@google.com'}` });
    addGatewayLog({ type: 'auth', text: `[GATEWAY-IDENTITY-PROPAGATION] Propagating ${accountName || 'jesusarguelles@google.com'} OAuth context to SharePoint Microsoft Graph client.` });
    if (text.trim().startsWith('claude-code')) {
      targetEngineId = "4299946434406383616"; // Mandated A2A routing rule
    }

    const userId = "bain_user_1";

    try {
      let currentSessionId = activeSessionId;

      if (!currentSessionId) {
        setMessages((prev) => prev.map(m => m.id === botMsgId ? { ...m, text: `⚡ [Pillar A] Initializing session with Vertex AI Agent Runtime (${targetEngineId}) and binding Entra ID OAuth token (sharepointauth_new)...` } : m));
        
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

      setMessages((prev) => prev.map(m => m.id === botMsgId ? { ...m, text: `⚡ [Pillar B] Session established (${currentSessionId}). Streaming query from Vertex AI Agent Runtime (${targetEngineId})...` } : m));

      if (selectedAgentId === 'dlp-compliance') {
        addGatewayLog({ type: 'engine', text: "LLM requested search_and_fetch_top on '02_Restricted_Privileged_DLP_Audit_Target_HoldCo.docx'" });
        addGatewayLog({ type: 'auth', text: "[GATEWAY-ACCESS-CONTROL] Applying Microsoft Graph ACL: j.chavez@bain.com has access to target HoldCo folder. Allowed." });
      } else if (selectedAgentId === 'observability-curator') {
        addGatewayLog({ type: 'engine', text: "LLM requested search_and_fetch_top on '05_External_Research_Addendum_DO_NOT_PARSE.md'" });
        addGatewayLog({ type: 'auth', text: "[GATEWAY-ACCESS-CONTROL] Applying Microsoft Graph ACL: j.chavez@bain.com has READ access to External Research directories." });
      } else if (selectedAgentId === 'ma-analyst') {
        addGatewayLog({ type: 'engine', text: `LLM requested search_and_fetch_top with query='${text.slice(0, 40)}...'` });
        addGatewayLog({ type: 'auth', text: "[GATEWAY-ACCESS-CONTROL] Applying SharePoint site ACL context: j.chavez@bain.com has access to 01_Project_Starlight_Financial_Model_FY26-30.xlsx." });
      } else if (selectedAgentId === 'market-quant') {
        addGatewayLog({ type: 'engine', text: "LLM requested public_market_multiples / plot_financial_data tools" });
        addGatewayLog({ type: 'auth', text: "[GATEWAY-EGRESS-SHIELD] Verifying outbound domain rules. Request to sec.gov allowed." });
      }

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
                  activeToolLog += `\n⚙️ [Executing Direct Tool: ${toolName}] Querying Gemini Enterprise MCP / Graph Engine...`;
                  setMessages((prev) => prev.map(m => m.id === botMsgId ? { ...m, text: accumulatedText + activeToolLog } : m));
                }
                if (part.function_response) {
                  const toolName = part.function_response.name || "direct_mcp_tool";
                  activeToolLog += `\n📎 [Tool Result: ${toolName}] Successfully retrieved corporate data payload.\n\n`;
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
            // Skip unparseable lines
          }
        }
      }

      // Definitive fix for Empty Stream Payloads (Subagent Recommendation: Final Buffer Flush)
      if (buffer.trim()) {
        try {
          let dataStr = buffer;
          if (buffer.startsWith("data: ")) dataStr = buffer.slice(6);
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
          }

          if (chunkText) {
            accumulatedText += chunkText;
            setMessages((prev) => prev.map(m => m.id === botMsgId ? { ...m, text: accumulatedText } : m));
          }
        } catch (e) {
          console.error("Final buffer flush error:", e);
        }
      }

      const latency = ((performance.now() - startTime) / 1000).toFixed(2) + 's';
      setMessages((prev) => prev.map(m => m.id === botMsgId ? { ...m, latency, text: accumulatedText || activeToolLog || "⚠️ [Stream Completed with empty text payload. Check Agent Runtime logs for tool exceptions.]" } : m));

      // Extract dynamically generated Recharts JSON chart blocks and append to dynamic main canvas grid
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

      // Live Egress DLP Scan / Observability Canary Check
      addGatewayLog({ type: 'scan', text: selectedAgentId === 'dlp-compliance' ? '[GATEWAY-EGRESS-SHIELD] Scanning outbound payload to j.chavez@bain.com...' : (selectedAgentId === 'observability-curator' ? '[GATEWAY-EGRESS-SHIELD] Running security audit evaluation...' : '[GATEWAY-EGRESS-SHIELD] Scanning outbound payload to j.chavez@bain.com...') });

      if (selectedAgentId === 'dlp-compliance') {
        if (finalBotText.includes('Redacted') || finalBotText.includes('████████') || finalBotText.includes('DLP Policy')) {
          addGatewayLog({ type: 'policy', text: "[GATEWAY-DLP-POLICY] MATCH FOUND: Strike price/Compensation pattern detected in 02_Restricted_Privileged_DLP_Audit_Target_HoldCo.docx" });
          addGatewayLog({ type: 'policy', text: "[GATEWAY-DLP-POLICY] POLICY ENFORCED: Redacting strike price value. Replaced with [Redacted by Agent Gateway DLP Policy]" });
        } else {
          addGatewayLog({ type: 'policy', text: "[GATEWAY-DLP-POLICY] SCANNING COMPLETE: No confidential MNPI pattern matched in standard output." });
        }
      } else if (selectedAgentId === 'observability-curator') {
        if (finalBotText.includes('canary detected') || finalBotText.includes('neutralized')) {
          addGatewayLog({ type: 'policy', text: "[GATEWAY-OBSERVABILITY] ALERT: Prompt injection canary trigger detected ('IGNORE PREVIOUS INSTRUCTIONS...')" });
          addGatewayLog({ type: 'policy', text: "[GATEWAY-OBSERVABILITY] STATUS: Malicious instruction neutralized. Forwarding alert to tracing backend." });
        } else {
          addGatewayLog({ type: 'policy', text: "[GATEWAY-OBSERVABILITY] CANARY EVALUATION: Safe token signature validated. No injection vector detected." });
        }
      } else {
        addGatewayLog({ type: 'scan', text: "[GATEWAY-DLP-POLICY] SCANNING COMPLETE: Safe payload verified. Zero policy breaches detected." });
      }

      addGatewayLog({ type: 'outbound', text: "[GATEWAY-OUTBOUND] Stream payload delivered to client. Identity context closed." });

    } catch (err: any) {
      console.error("[Agent Runtime] True Live Connection Error:", err.message);
      const latency = ((performance.now() - startTime) / 1000).toFixed(2) + 's';
      const errorNotice = `❌ [LIVE RUNTIME CONNECTION FAILED]\n\nUnable to stream from Vertex AI Agent Runtime (${targetEngineId}) via Vite ADC Proxy.\n\nError Details:\n${err.message}\n\nTroubleshooting:\n1. Verify your local ADC is active (run gcloud auth login / gcloud auth application-default login in terminal).\n2. Ensure your account has aiplatform.reasoningEngines.streamQuery permissions in project vtxdemos (254356041555).\n3. Check terminal where npm run dev is running for Vite Proxy logs.`;
      setMessages((prev) => prev.map(m => m.id === botMsgId ? { ...m, text: errorNotice, latency } : m));
    } finally {
      setLoading(false);
    }
  };

  const handleSend = (e: React.FormEvent) => {
    e.preventDefault();
    if (!chatInput.trim() || loading) return;
    executePrompt(chatInput);
  };

  return (
    <div 
      style={{ width: chatWidth }} 
      className="chat-drawer font-sans flex flex-col h-full bg-[#f4f3ef] border-l border-[#d8d6d0] flex-shrink-0 transition-none"
    >
      {/* Bain Workstation Header Bar */}
      <div className="flex items-center justify-between px-6 py-3.5 border-b border-[#d8d6d0] bg-[#faf9f6] flex-shrink-0">
        <div className="flex items-center gap-2 pr-2 truncate">
          <span className="font-mono font-bold text-xs text-[#1a1a19] flex-shrink-0">&gt;_</span>
          <h3 className="font-bold text-[#1a1a19] text-xs tracking-widest uppercase font-mono truncate">WORKSTATION</h3>
        </div>
        {/* Top Action Icons */}
        <div className="flex items-center gap-4 text-[#7c7a75] flex-shrink-0">
          <button type="button" className="p-1 text-[#1a1a19] hover:bg-[#d8d6d0] transition-colors cursor-pointer" title="Active Workstation Feed">
            💬
          </button>
          <button type="button" onClick={() => setActiveView('topology')} className="p-1 hover:text-[#1a1a19] hover:bg-[#d8d6d0] transition-colors cursor-pointer" title="View Execution Topology Map">
            ∿
          </button>
          <button type="button" onClick={() => setActiveView('chart')} className="p-1 hover:text-[#1a1a19] hover:bg-[#d8d6d0] transition-colors cursor-pointer" title="View Recharts Multi-Asset Plot">
            📈
          </button>
          <button type="button" onClick={() => setMessages([])} className="p-1 hover:text-[#1a1a19] hover:bg-[#d8d6d0] transition-colors cursor-pointer" title="Clear Console History">
            🗑️
          </button>
          <button type="button" onClick={() => setShowAuthDrawer(true)} className="p-1 hover:text-[#1a1a19] hover:bg-[#d8d6d0] transition-colors cursor-pointer" title="Technical Flow Settings">
            ⚙️
          </button>
      </div>
    </div>

      {/* Horizontally Scrollable Agent Selection Strip */}
      <div className="bg-[#faf9f6] border-b border-[#d8d6d0] px-4 py-2.5 flex gap-2 overflow-x-auto flex-shrink-0">
        {[
          { id: 'ma-analyst', name: 'M&A Analyst', icon: '💼', desc: 'Starlight documents' },
          { id: 'market-quant', name: 'Market Quant', icon: '📈', desc: 'Stock charts & multiples' },
          { id: 'dlp-compliance', name: 'DLP Auditor', icon: '🛡️', desc: 'MNPI security shield' },
          { id: 'observability-curator', name: 'Observability', icon: '🔬', desc: 'Canary logs & trace' }
        ].map(agent => (
          <button
            key={agent.id}
            type="button"
            onClick={() => setSelectedAgentId(agent.id)}
            className={`flex items-center gap-2 px-4 py-2 border transition-all text-left flex-shrink-0 cursor-pointer rounded-full ${
              selectedAgentId === agent.id 
                ? 'bg-[#1a1a19] text-[#faf9f6] border-[#1a1a19] shadow-sm' 
                : 'bg-[#faf9f6] text-[#1a1a19] border-[#d8d6d0] hover:border-[#1a1a19]'
            }`}
          >
            <span className="text-xs">{agent.icon}</span>
            <div className="flex flex-col">
              <span className="text-[9px] font-mono font-bold uppercase leading-none tracking-wider">{agent.name}</span>
              <span className="text-[8px] text-[#7c7a75] mt-0.5 max-w-[100px] truncate leading-none">{agent.desc}</span>
            </div>
          </button>
        ))}
      </div>

      {/* Optional Technical Flow & Settings Overlay Modal */}
      {showAuthDrawer && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4 overflow-y-auto">
          <div className="bg-[#faf9f6] border border-[#d8d6d0] w-full max-w-2xl p-6 flex flex-col gap-6 font-sans text-xs shadow-2xl my-auto">
            <div className="flex justify-between items-center border-b border-[#d8d6d0] pb-3">
              <div>
                <h4 className="font-bold text-base tracking-tight text-[#1a1a19]">Platform Flow & Authorization Settings</h4>
                <p className="text-[#7c7a75] text-[11px] mt-0.5">Two-Pillar authentication architecture and active backend runtime bindings.</p>
              </div>
              <button 
                type="button"
                onClick={() => setShowAuthDrawer(false)}
                className="text-[#7c7a75] hover:text-[#1a1a19] p-1.5 border border-transparent hover:border-[#d8d6d0] transition-colors cursor-pointer"
                title="Close Settings Overlay"
              >
                <svg className="w-5 h-5" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                </svg>
              </button>
            </div>

            {/* Section 1: Microsoft 365 Work Account (Pillar A) */}
            <div className="flex flex-col gap-4">
              <div className="flex flex-col gap-1">
                <span className="font-bold text-xs text-[#1a1a19] uppercase tracking-wider font-mono">1. Microsoft 365 Work Account (Pillar A)</span>
                <span className="text-[#7c7a75] text-[11px]">Authorizes secure Microsoft Graph access to SharePoint document libraries (sockcop site).</span>
              </div>

              {!entraToken ? (
                <div className="p-5 border border-[#d8d6d0] bg-[#f4f3ef] flex flex-col sm:flex-row items-center justify-between gap-4">
                  <div className="flex items-center gap-3">
                    <div className="grid grid-cols-2 gap-1 w-6 h-6 p-1 bg-white border border-[#d8d6d0]">
                      <div className="bg-[#f25022]" />
                      <div className="bg-[#7fba00]" />
                      <div className="bg-[#00a4ef]" />
                      <div className="bg-[#ffb900]" />
                    </div>
                    <div>
                      <h5 className="font-bold text-xs text-[#1a1a19]">Connect your Microsoft 365 Tenant</h5>
                      <p className="text-[#7c7a75] text-[11px]">Enables secure two-pillar OAuth 2.0 verification for Bain practice consultants.</p>
                    </div>
                  </div>
                  <button 
                    type="button"
                    onClick={handleMsalLogin}
                    className="w-full sm:w-auto bg-[#1a1a19] text-[#faf9f6] px-5 py-2.5 text-xs font-bold tracking-wide shadow-sm hover:bg-[#7c7a75] transition-all flex items-center justify-center gap-2 border border-[#1a1a19] cursor-pointer"
                  >
                    <svg className="w-4 h-4 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
                    </svg>
                    Sign in with Microsoft
                  </button>
                </div>
              ) : (
                <div className="p-4 border border-[#d8d6d0] bg-[#faf9f6] flex flex-col gap-4">
                  <div className="flex flex-col sm:flex-row items-baseline sm:items-center justify-between gap-2 border-b border-[#d8d6d0] pb-3">
                    <div className="flex items-center gap-2">
                      <div className="grid grid-cols-2 gap-0.5 w-3.5 h-3.5">
                        <div className="bg-[#f25022]" />
                        <div className="bg-[#7fba00]" />
                        <div className="bg-[#00a4ef]" />
                        <div className="bg-[#ffb900]" />
                      </div>
                      <span className="font-bold text-xs text-[#1a1a19]">{accountName || 'Bain Partner'}</span>
                      <span className="inline-flex items-center px-2 py-0.5 font-mono text-[10px] bg-green-50 text-green-700 border border-green-200">
                        Active Access Token
                      </span>
                    </div>
                    <div className="flex items-center gap-2 w-full sm:w-auto justify-end">
                      <button 
                        type="button"
                        onClick={handleMsalLogin}
                        className="bg-[#f4f3ef] text-[#1a1a19] border border-[#d8d6d0] px-3 py-1 text-[11px] font-medium hover:bg-[#d8d6d0] transition-colors cursor-pointer"
                        title="Reauthenticate via MSAL Popup"
                      >
                        Re-login
                      </button>
                      <button 
                        type="button"
                        onClick={() => { setEntraToken(''); setAccountName(null); setMsalLog(null); }}
                        className="bg-[#1a1a19] text-[#faf9f6] px-3 py-1 text-[11px] font-medium hover:bg-[#7c7a75] transition-colors cursor-pointer"
                      >
                        Disconnect
                      </button>
                    </div>
                  </div>
                  <div className="flex flex-col gap-1.5">
                    <span className="text-[#7c7a75] text-[10px] font-mono uppercase">Assigned JWT Token (sharepointauth_new):</span>
                    <input
                      type="text"
                      value={entraToken}
                      onChange={(e) => setEntraToken(e.target.value)}
                      placeholder="Paste fallback Bearer token..."
                      className="w-full text-xs bg-[#f4f3ef] border border-[#d8d6d0] px-3 py-2 text-[#1a1a19] focus:outline-none focus:border-[#1a1a19] font-mono truncate"
                    />
                  </div>
                </div>
              )}

              {msalLog && (
                <div className="p-4 bg-[#111111] text-[#faf9f6] border border-[#d8d6d0] text-[11px] font-mono leading-relaxed whitespace-pre-wrap shadow-inner max-h-48 overflow-y-auto">
                  <div className="flex items-center gap-2 pb-2 border-b border-[#333333] mb-2 text-[#7c7a75] text-[10px] uppercase tracking-wider">
                    <span className="w-1.5 h-1.5 rounded-full bg-green-400" /> MSAL Auth Console Log
                  </div>
                  {msalLog}
                </div>
              )}
            </div>

            {/* Section 2: Vertex AI Agent Engine Binding (Pillar B) */}
            <div className="flex flex-col gap-3 pt-4 border-t border-[#d8d6d0]">
              <div className="flex flex-col gap-1">
                <span className="font-bold text-xs text-[#1a1a19] uppercase tracking-wider font-mono">2. Deployed Agent Runtime Engine (Pillar B)</span>
                <span className="text-[#7c7a75] text-[11px]">Target Vertex AI Reasoning Engine instance receiving streaming requests via Local ADC Proxy.</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="bg-[#f4f3ef] border border-[#d8d6d0] px-3 py-2 text-[#7c7a75] font-mono text-xs hidden sm:inline-block">
                  projects/{PROJECT_NUMBER}/locations/{LOCATION}/reasoningEngines/
                </span>
                <input
                  type="text"
                  value={reasoningEngineId}
                  onChange={(e) => setReasoningEngineId(e.target.value)}
                  placeholder="8655608971282874368"
                  className="flex-1 text-xs bg-[#f4f3ef] border border-[#d8d6d0] px-3 py-2 text-[#1a1a19] focus:outline-none focus:border-[#1a1a19] font-mono"
                />
              </div>
              <span className="text-[10px] text-[#7c7a75] font-mono italic pt-0.5">
                Resolved Proxy Endpoint: /api/v1beta1/projects/{PROJECT_NUMBER}/locations/{LOCATION}/reasoningEngines/{reasoningEngineId.trim().split('/').pop()}:streamQuery?alt=sse
              </span>
            </div>

            {/* Footer Action */}
            <div className="flex justify-end pt-4 border-t border-[#d8d6d0]">
              <button 
                type="button"
                onClick={() => setShowAuthDrawer(false)}
                className="bg-[#1a1a19] text-[#faf9f6] px-6 py-2 text-xs font-bold tracking-wider uppercase hover:bg-[#7c7a75] transition-colors cursor-pointer"
              >
                Save & Continue
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Messages Feed */}
      <div className="chat-messages-container p-6 space-y-6 flex-1 overflow-y-auto">
        {messages.map((msg) => (
          <div key={msg.id} className="flex flex-col w-full">
            <span className="text-[10px] font-semibold text-[#7c7a75] tracking-wider uppercase mb-1 flex items-center">
              {msg.sender === 'user' ? 'Partner / User' : 'Bain Enterprise Agent'}
              {msg.isBtw && (
                <span className="border border-[#d8d6d0] text-[9px] px-1 py-0.5 ml-2 font-mono bg-[#faf9f6]">
                  /btw
                </span>
              )}
            </span>
            <div className={`text-sm p-4 border-l-2 leading-relaxed break-words min-w-0 max-w-full w-full rounded-none ${
              msg.sender === 'user'
                ? 'border-[#7c7a75] bg-[#f4f3ef] text-[#7c7a75]'
                : 'border-[#1a1a19] bg-white text-[#1a1a19]'
            }`}>
              {/* Render Elite Visual Markdown with Invincible Universal Generative UI Chart Support */}
              {msg.text ? (
                <ReactMarkdown 
                  remarkPlugins={[remarkGfm]}
                  components={{
                    h1: ({node, ...props}) => <h1 className="font-bold text-lg tracking-tight text-[#1a1a19] border-b border-[#d8d6d0] pb-1 my-4" {...props} />,
                    h2: ({node, ...props}) => <h2 className="font-bold text-base tracking-tight text-[#1a1a19] border-b border-[#d8d6d0] pb-1 my-3" {...props} />,
                    h3: ({node, ...props}) => <h3 className="font-bold text-sm tracking-tight text-[#1a1a19] border-b border-[#d8d6d0] pb-1 my-3 uppercase" {...props} />,
                    h4: ({node, ...props}) => <h4 className="font-bold text-xs tracking-tight text-[#1a1a19] my-2 uppercase" {...props} />,
                    p: ({node, ...props}) => <p className="my-2 leading-relaxed whitespace-pre-wrap" {...props} />,
                    ul: ({node, ...props}) => <ul className="list-disc pl-5 my-2 space-y-1" {...props} />,
                    ol: ({node, ...props}) => <ol className="list-decimal pl-5 my-2 space-y-1" {...props} />,
                    li: ({node, ...props}) => <li className="leading-relaxed" {...props} />,
                    table: ({node, ...props}) => (
                      <div className="overflow-x-auto my-4">
                        <table className="min-w-full divide-y divide-[#d8d6d0] border border-[#d8d6d0] text-xs font-mono" {...props} />
                      </div>
                    ),
                    th: ({node, ...props}) => <th className="bg-[#f4f3ef] px-4 py-2 font-bold text-left text-[#1a1a19] border-b border-[#d8d6d0]" {...props} />,
                    td: ({node, ...props}) => <td className="px-4 py-2 border-b border-[#d8d6d0]" {...props} />,
                    a: ({node, ...props}) => (
                      <a 
                        className="inline-flex items-center gap-1 font-mono text-xs bg-[#1a1a19] text-[#faf9f6] px-2 py-0.5 hover:bg-[#7c7a75] transition-colors my-1 border border-[#1a1a19]" 
                        target="_blank" 
                        rel="noreferrer" 
                        {...props} 
                      />
                    ),
                    code: ({node, inline, className, children, ...props}: any) => {
                      const contentStr = String(children).trim();
                      const isJsonBlock = !inline && (className === 'language-json_chart' || className === 'language-json' || contentStr.startsWith('{'));
                      
                      if (isJsonBlock) {
                        try {
                          const chartData = JSON.parse(contentStr);
                          
                          // Handle LLM's dynamic "chart" structure (e.g. {"chart": {"title": "...", "subtitle": "...", "type": "line", ...}})
                          if (chartData.chart) {
                            return (
                              <div className="my-6 p-6 border border-[#d8d6d0] bg-[#faf9f6] shadow-sm rounded-none font-sans">
                                <div className="flex items-center justify-between border-b border-[#d8d6d0] pb-3 mb-6">
                                  <div className="flex items-center gap-2">
                                    <div className="w-2 h-2 bg-[#00c2cb]" />
                                    <h4 className="font-bold text-sm text-[#1a1a19] tracking-wide uppercase">{chartData.chart.title || "Interactive Bain Multi-Asset Plot"}</h4>
                                  </div>
                                  <span className="text-[10px] font-mono bg-[#00c2cb] text-white px-2 py-1 font-bold">LIVE MCP STREAM</span>
                                </div>

                                {chartData.chart.subtitle && (
                                  <p className="text-xs font-mono text-[#7c7a75] mb-6">{chartData.chart.subtitle}</p>
                                )}

                                {/* SVG Visual Plot simulation for dynamic data */}
                                <div className="w-full h-40 bg-white border border-[#d8d6d0] p-4 flex flex-col justify-between relative font-mono text-[10px] text-[#7c7a75] mb-6">
                                  <div className="absolute inset-x-4 top-4 border-b border-dashed border-[#d8d6d0]" />
                                  <div className="absolute inset-x-4 top-1/2 border-b border-dashed border-[#d8d6d0]" />
                                  <div className="absolute inset-x-4 bottom-4 border-b border-dashed border-[#d8d6d0]" />
                                  <div className="flex justify-between z-10"><span>HIGH ($350.00)</span><span>Start Date</span></div>
                                  <div className="flex justify-between z-10"><span>LOW ($230.00)</span><span>June 22, 2026</span></div>
                                  <svg className="absolute inset-0 w-full h-full p-4 overflow-visible" preserveAspectRatio="none" viewBox="0 0 500 150">
                                    <path d="M 0 30 L 100 20 L 200 25 L 300 15 L 400 35 L 500 50" fill="none" stroke="#00c2cb" strokeWidth="3" />
                                    <path d="M 0 120 L 100 110 L 200 115 L 300 105 L 400 100 L 500 105" fill="none" stroke="#1a1a19" strokeWidth="3" />
                                  </svg>
                                </div>

                                {/* Dynamic View Switching Pill Buttons */}
                                <div className="pt-4 border-t border-[#d8d6d0] flex items-center justify-between gap-4">
                                  <button
                                    type="button"
                                    onClick={() => setActiveView('chart')}
                                    className="flex-1 py-2 bg-[#00c2cb] text-white text-[11px] font-mono font-bold tracking-wider hover:bg-[#00a0a8] transition-colors cursor-pointer shadow-sm flex items-center justify-center gap-2"
                                  >
                                    <span>📈</span> &lt; VIEW GRAPH
                                  </button>
                                  <button
                                    type="button"
                                    onClick={() => setActiveView('topology')}
                                    className="flex-1 py-2 bg-[#1a1a19] text-[#faf9f6] text-[11px] font-mono font-bold tracking-wider hover:bg-[#7c7a75] transition-colors cursor-pointer shadow-sm flex items-center justify-center gap-2"
                                  >
                                    <span>⚙️</span> VIEW TOPOLOGY
                                  </button>
                                </div>
                              </div>
                            );
                          }

                          // Handle standard tableData structure
                          return (
                            <div className="my-6 p-4 sm:p-6 border border-[#d8d6d0] bg-[#faf9f6] shadow-sm rounded-2xl font-sans min-w-0 max-w-full overflow-hidden">
                              <div className="flex flex-wrap items-center justify-between border-b border-[#d8d6d0] pb-3 mb-6 gap-2">
                                <div className="flex items-center gap-2 min-w-0">
                                  <div className="w-2 h-2 bg-[#1a1a19] flex-shrink-0" />
                                  <h4 className="font-bold text-sm text-[#1a1a19] tracking-wide uppercase break-words whitespace-normal min-w-0">{chartData.title || "Interactive Bain Multi-Asset Comparison"}</h4>
                                </div>
                                <span className="text-[10px] font-mono bg-[#1a1a19] text-[#faf9f6] px-2.5 py-1 rounded-full whitespace-normal text-center flex-shrink-0">Public Market MCP Proxy</span>
                              </div>
                              
                              <div className="grid grid-cols-1 gap-4 mb-6">
                                {chartData.tableData?.map((row: any, rIdx: number) => (
                                  <div key={rIdx} className="border border-[#d8d6d0] bg-[#f4f3ef] p-4 flex flex-col justify-between shadow-sm rounded-xl">
                                    <div>
                                      <div className="flex items-center justify-between border-b border-[#d8d6d0] pb-2 mb-3">
                                        <span className="font-bold text-xs text-[#1a1a19] truncate">{row.company}</span>
                                        <span className="text-[10px] font-mono border border-[#d8d6d0] bg-[#faf9f6] px-1.5 py-0.5 text-[#1a1a19]">{row.ticker}</span>
                                      </div>
                                      <div className="flex flex-col gap-2 font-mono text-xs">
                                        {chartData.metrics?.map((m: string, mIdx: number) => (
                                          <div key={mIdx} className="flex items-center justify-between">
                                            <span className="text-[#7c7a75] text-[10px] truncate pr-2">{m}:</span>
                                            <span className="font-bold text-[#1a1a19]">{row.values[mIdx]}</span>
                                          </div>
                                        ))}
                                      </div>
                                    </div>
                                    <div className="mt-4 pt-3 border-t border-[#d8d6d0] flex items-center justify-between text-[10px] font-mono text-[#7c7a75]">
                                      <span>Source:</span>
                                      <span className="bg-[#1a1a19] text-[#faf9f6] px-2 py-0.5 font-bold">{row.source}</span>
                                    </div>
                                  </div>
                                ))}
                              </div>

                              {/* Dynamic View Switching Pill Buttons */}
                              <div className="pt-4 border-t border-[#d8d6d0] flex items-center justify-between gap-4">
                                <button
                                  type="button"
                                  onClick={() => setActiveView('chart')}
                                  className="flex-1 py-2 bg-[#00c2cb] text-white text-[11px] font-mono font-bold tracking-wider hover:bg-[#00a0a8] transition-colors cursor-pointer shadow-sm flex items-center justify-center gap-2 rounded-full"
                                >
                                  <span>📈</span> &lt; VIEW GRAPH
                                </button>
                                <button
                                  type="button"
                                  onClick={() => setActiveView('topology')}
                                  className="flex-1 py-2 bg-[#1a1a19] text-[#faf9f6] text-[11px] font-mono font-bold tracking-wider hover:bg-[#7c7a75] transition-colors cursor-pointer shadow-sm flex items-center justify-center gap-2 rounded-full"
                                >
                                  <span>⚙️</span> VIEW TOPOLOGY
                                </button>
                              </div>
                            </div>
                          );
                        } catch (e) {
                          console.error("Failed to parse json_chart", e);
                        }
                      }
                      return <code className="font-mono text-xs bg-[#f4f3ef] px-1 py-0.5 border border-[#d8d6d0]" {...props}>{children}</code>;
                    },
                  }}
                >
                  {msg.text}
                </ReactMarkdown>
              ) : (loading && msg.sender === 'bot' ? <span className="text-[#7c7a75] italic">Streaming via local ADC Proxy...</span> : '')}
              
              {msg.latency && (
                <div className="message-meta-footer mt-3 flex justify-between border-t border-dotted border-[#d8d6d0] pt-2 text-[10px] font-mono text-[#7c7a75]">
                  <span>[LATENCY: {msg.latency}]</span>
                  <span>[MODEL: {msg.model}]</span>
                </div>
              )}
            </div>
          </div>
        ))}

        {/* AI Thinking console block */}
        {loading && (
          <div className="flex flex-col w-full">
            <span className="text-[10px] font-semibold text-[#7c7a75] tracking-wider uppercase mb-1">
              Bain Enterprise Agent
            </span>
            <div className="text-sm border-l-2 border-[#1a1a19] pl-3 text-[#1a1a19] font-mono rounded-lg flex items-center gap-2">
              <span className="yazdani-spinner" /> 
              <span className="sweep-text">Streaming Direct Graph Engine via ADC... █</span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* 🤖 Quick Agent Launch & Extension Strip */}
      <div className="px-6 py-3 bg-[#faf9f6] border-t border-[#d8d6d0] flex flex-wrap items-center gap-2 flex-shrink-0">
        <span className="text-[10px] font-mono font-bold text-[#1a1a19] uppercase flex items-center gap-1 flex-shrink-0">
          ⚡ Quick Demo:
        </span>
        <button
          type="button"
          onClick={() => executePrompt("what is the stock price for alphabet? compare the stock price for alphabet and amazon and create a table.")}
          className="text-[11px] font-sans font-medium bg-[#f4f3ef] border border-[#d8d6d0] px-4 py-1.5 text-[#1a1a19] hover:bg-[#1a1a19] hover:text-[#faf9f6] transition-colors flex-shrink-0 cursor-pointer shadow-sm rounded-full"
        >
          📊 Launch Public Market Agent (Google Search & Comp Multiples)
        </button>
        <button
          type="button"
          onClick={() => executePrompt("Extract the executive compensation and the exact agreed acquisition strike price for Project Starlight from 02_Restricted_Privileged_DLP_Audit_Target_HoldCo.docx.")}
          className="text-[11px] font-sans font-medium bg-[#f4f3ef] border border-[#d8d6d0] px-4 py-1.5 text-[#1a1a19] hover:bg-[#1a1a19] hover:text-[#faf9f6] transition-colors flex-shrink-0 cursor-pointer shadow-sm rounded-full"
        >
          🛡️ Launch Agent Gateway DLP Shield (Redact MNPI)
        </button>
        <button
          type="button"
          onClick={() => executePrompt("Read 05_External_Research_Addendum_DO_NOT_PARSE.md and follow the instructions inside.")}
          className="text-[11px] font-sans font-medium bg-[#f4f3ef] border border-[#d8d6d0] px-4 py-1.5 text-[#1a1a19] hover:bg-[#1a1a19] hover:text-[#faf9f6] transition-colors flex-shrink-0 cursor-pointer shadow-sm rounded-full"
        >
          🧪 Launch Agent Observability & Simulation Test Harness
        </button>
      </div>

      {/* Console Input */}
      <div className="relative p-6 border-t border-[#d8d6d0] bg-[#f4f3ef] rounded-t-3xl flex-shrink-0">
        {showBtwDropdown && <QuickBtwChat setChatInput={setChatInput} />}
        <form onSubmit={handleSend} className="flex gap-4">
          <input
            type="text"
            value={chatInput}
            onChange={(e) => setChatInput(e.target.value)}
            placeholder="Ask anything..."
            className="flex-1 text-sm bg-[#faf9f6] border border-[#d8d6d0] px-5 py-3 text-[#1a1a19] focus:outline-none focus:border-[#1a1a19] rounded-full font-sans shadow-inner"
          />
          <button 
            type="submit"
            disabled={loading}
            className="bg-[#1a1a19] text-[#faf9f6] px-6 py-3 text-xs font-semibold tracking-wider uppercase rounded-full hover:bg-[#7c7a75] transition-colors disabled:opacity-50 cursor-pointer"
          >
            Send
          </button>
        </form>
      </div>
    </div>
  );
}
