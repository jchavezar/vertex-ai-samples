import React, { useState, useEffect, useRef } from 'react';
import { Sparkles, MessageSquare, ChevronDown, ChevronUp, ChevronRight, Maximize2, Minimize2, Terminal, AlertCircle, CheckCircle, X, Plus, Upload, Link, Cloud, HardDrive, Youtube, Mic, MicOff, Activity, Download } from 'lucide-react';
import { useLiveAPI } from '../contexts/LiveAPIContext';
import { AudioRecorder } from '../lib/audio-recorder';
import ReasoningChain from './ReasoningChain';
import ErrorBoundary from './ErrorBoundary';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import TraceLog from './TraceLog';
import { jsPDF } from 'jspdf';
import html2canvas from 'html2canvas';
import { saveAs } from 'file-saver';
import AgentGraph from './AgentGraph';

const RightSidebar = ({ dashboardData, chartOverride, setChartOverride, onUpdateWidget, isOpen, width }) => {
  const [aiSummary, setAiSummary] = useState(null);
  const [summaryLoading, setSummaryLoading] = useState(false);
  const { connected, connect, disconnect, volume, client, setConfig } = useLiveAPI();
  console.log("DEBUG: RightSidebar mounted. useLiveAPI result:", { connected, hasClient: !!client, hasSetConfig: !!setConfig });

  const [audioRecorder] = useState(() => new AudioRecorder());
  const [muted, setMuted] = useState(false);

  useEffect(() => {
    // Initialize the Live API session configuration
    // This is critical to prevent "auto-close" (Cannot extract voices from non-audio request)
    setConfig({
      model: "models/gemini-2.0-flash-exp",
      generationConfig: {
        responseModalities: "audio",
        speechConfig: {
          voiceConfig: { prebuiltVoiceConfig: { voiceName: "Aoede" } }
        }
      },
      systemInstruction: {
        parts: [{ text: "You are a professional financial assistant. Keep responses concise and focused." }]
      }
    });
  }, [setConfig]);

  useEffect(() => {
    const onData = (base64) => {
      client.sendRealtimeInput([{
        mimeType: 'audio/pcm;rate=16000',
        data: base64,
      }]);
    };
    if (connected && !muted && audioRecorder) {
      audioRecorder.on('data', onData).start();
    } else {
      audioRecorder.stop();
    }
    return () => {
      audioRecorder.off('data', onData);
    };
  }, [connected, client, muted, audioRecorder]);

  // Debug Logging to Trace
  useEffect(() => {
    if (!client) return;
    const onLog = (log) => {
      // log structure might be { type: 'audio_input', message: '...' } or { type: 'server.audio', ... }
      // Filter out noisy audio spam
      if (
        log.type === 'audio' ||
        log.type === 'audio_input' ||
        log.type === 'audio_vol' ||
        log.message === 'audio' ||
        log.message === 'turnComplete'
      ) return;

      addTraceLog(log.type === 'error' ? 'error' : 'debug', log.message);
    };
    client.on('log', onLog);
    return () => client.off('log', onLog);
  }, [client]);

  // Chat State
  const [selectedModel, setSelectedModel] = useState('gemini-2.5-flash-lite');
  const [selectedComplexModel, setSelectedComplexModel] = useState('gemini-3-flash-preview');
  const [messages, setMessages] = useState([
    { role: 'assistant', text: 'How can FactSet help?' }
  ]);
  const [chatInput, setChatInput] = useState('');
  const [chatLoading, setChatLoading] = useState(false);
  const [selectedImage, setSelectedImage] = useState(null); // base64 string
  const [selectedVideoUrl, setSelectedVideoUrl] = useState(null);
  const [isUploadDropdownOpen, setIsUploadDropdownOpen] = useState(false);
  const fileInputRef = useRef(null);
  const dropdownRef = useRef(null);

  // FactSet Auth State
  const [isFactSetConnected, setIsFactSetConnected] = useState(false);
  const [factsetExpiry, setFactsetExpiry] = useState(null);
  const [timeRemaining, setTimeRemaining] = useState(null);
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [authUrl, setAuthUrl] = useState('');
  const [authInput, setAuthInput] = useState('');
  const [hasRefreshToken, setHasRefreshToken] = useState(false);
  const [showAdvancedAuth, setShowAdvancedAuth] = useState(false);
  const [manualRefreshToken, setManualRefreshToken] = useState('');

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsUploadDropdownOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleDownloadPDF = async () => {
    // 1. Capture Agent Graph if visible
    let graphImgData = null;
    const graphElement = document.getElementById('printable-agent-graph');
    if (graphElement) {
      try {
        const graphCanvas = await html2canvas(graphElement, {
          scale: 1,
          useCORS: true,
          logging: false
        });
        graphImgData = graphCanvas.toDataURL('image/jpeg', 0.8);
      } catch (err) {
        console.warn("Failed to capture graph:", err);
      }
    }

    // Create a temporary container for the export text content
    const exportContainer = document.createElement('div');
    exportContainer.style.position = 'fixed'; // Changed from absolute
    exportContainer.style.top = '0';          // On screen
    exportContainer.style.left = '0';
    exportContainer.style.zIndex = '-9999';   // Hidden behind everything
    exportContainer.style.width = '800px'; 
    exportContainer.style.backgroundColor = '#ffffff';
    exportContainer.style.padding = '40px';
    exportContainer.style.boxSizing = 'border-box';
    document.body.appendChild(exportContainer);

    // Give the DOM a moment to calculate layout
    setTimeout(async () => {
      try {
        // ... (rest of content generation)

      // 1. Header
      const header = document.createElement('div');
      header.style.marginBottom = '30px';
      header.style.borderBottom = '2px solid #004b87';
      header.style.paddingBottom = '10px';
      header.innerHTML = `
        <h1 style="color: #004b87; font-family: sans-serif; margin: 0;">Session Export</h1>
        <div style="color: #666; font-size: 14px; margin-top: 5px;">${new Date().toLocaleString()}</div>
      `;
      exportContainer.appendChild(header);

      // 2. Chat History
      const chatSection = document.createElement('div');
      chatSection.style.marginBottom = '40px';
      chatSection.innerHTML = '<h2 style="color: #333; font-family: sans-serif; border-bottom: 1px solid #eee; padding-bottom: 8px;">Chat History</h2>';

      const chatContent = document.createElement('div');
      chatContent.style.fontFamily = 'sans-serif';

      messages.forEach(msg => {
        const msgDiv = document.createElement('div');
        const isUser = msg.role === 'user';
        msgDiv.style.marginBottom = '15px';
        msgDiv.style.padding = '10px 15px';
        msgDiv.style.borderRadius = '12px';
        msgDiv.style.backgroundColor = isUser ? '#f0f7ff' : '#f8f9fa';
        msgDiv.style.border = isUser ? '1px solid #cce0ff' : '1px solid #e9ecef';
        msgDiv.style.color = '#333';
        msgDiv.style.maxWidth = '90%';
        msgDiv.style.marginLeft = isUser ? 'auto' : '0';
        msgDiv.style.marginRight = isUser ? '0' : 'auto';

        const roleDiv = document.createElement('div');
        roleDiv.style.fontSize = '11px';
        roleDiv.style.fontWeight = 'bold';
        roleDiv.style.marginBottom = '4px';
        roleDiv.style.color = isUser ? '#004b87' : '#666';
        roleDiv.innerText = isUser ? 'User' : 'Assistant';

        const textDiv = document.createElement('div');
        textDiv.style.fontSize = '13px';
        textDiv.style.lineHeight = '1.5';
        textDiv.style.whiteSpace = 'pre-wrap';
        textDiv.innerText = msg.text;

        msgDiv.appendChild(roleDiv);
        msgDiv.appendChild(textDiv);

        if (msg.latency) {
          const latDiv = document.createElement('div');
          latDiv.style.fontSize = '10px';
          latDiv.style.color = '#888';
          latDiv.style.textAlign = 'right';
          latDiv.style.marginTop = '4px';
          latDiv.innerText = `${(msg.latency / 1000).toFixed(2)}s`;
          msgDiv.appendChild(latDiv);
        }

        chatContent.appendChild(msgDiv);
      });
      chatSection.appendChild(chatContent);
      exportContainer.appendChild(chatSection);

        // Helper for JSON formatting
        const deepParseJSON = (obj) => {
          if (typeof obj === 'string') {
            const trimmed = obj.trim();
            if (trimmed.startsWith('{') || trimmed.startsWith('[')) {
              try {
                return deepParseJSON(JSON.parse(trimmed));
              } catch (e) { return obj; }
            }
          }
          if (Array.isArray(obj)) {
            return obj.map(deepParseJSON);
          }
          if (obj !== null && typeof obj === 'object') {
            const newObj = {};
            for (const key in obj) {
              newObj[key] = deepParseJSON(obj[key]);
            }
            return newObj;
          }
          return obj;
        };

        // 3. Agent Configuration
        if (agentConfig) {
          const configSection = document.createElement('div');
          configSection.style.marginBottom = '40px';
          configSection.innerHTML = '<h2 style="color: #333; font-family: sans-serif; border-bottom: 1px solid #eee; padding-bottom: 8px;">Agent Configuration</h2>';

          const configContent = document.createElement('div');
          configContent.style.fontFamily = 'monospace';
          configContent.style.fontSize = '11px';
          configContent.style.background = '#f8f9fa'; // Light gray
          configContent.style.padding = '15px';
          configContent.style.borderRadius = '8px';
          configContent.style.whiteSpace = 'pre-wrap';
          configContent.innerText = JSON.stringify(agentConfig, null, 2);

          configSection.appendChild(configContent);
          exportContainer.appendChild(configSection);
        }

        // 4. Trace Logs
      if (traceLogs.length > 0) {
        const traceSection = document.createElement('div');
        traceSection.innerHTML = '<h2 style="color: #333; font-family: sans-serif; border-bottom: 1px solid #eee; padding-bottom: 8px;">Trace Logs</h2>';

        const traceContent = document.createElement('div');
        traceContent.style.fontFamily = 'monospace';
        traceContent.style.fontSize = '10px'; // Smaller font for logs
        traceContent.style.background = '#fafafa';
        traceContent.style.padding = '15px';
        traceContent.style.borderRadius = '8px';
        traceContent.style.border = '1px solid #eee';

        traceLogs.forEach(log => {
          const item = document.createElement('div');
          item.style.marginBottom = '12px';
          item.style.borderBottom = '1px solid #eee';
          item.style.paddingBottom = '8px';

          let color = '#333';
          if (log.type === 'tool_call') color = '#6f42c1';
          if (log.type === 'tool_result') color = '#28a745';
          if (log.type === 'error') color = '#dc3545';
          if (log.type === 'user') color = '#004b87';

          // Robust JSON Formatting
          let logContent = '';
          if (log.args) {
            const parsedArgs = deepParseJSON(log.args);
            logContent = `Args:\n${JSON.stringify(parsedArgs, null, 2)}`;
          } else if (log.result) {
            const parsedResult = deepParseJSON(log.result);
            logContent = `Result:\n${JSON.stringify(parsedResult, null, 2)}`;
          } else {
            logContent = log.content || '';
          }

          item.innerHTML = `
             <div style="display:flex; justify-content:space-between; color:${color}; font-weight:bold; margin-bottom:4px;">
               <span>${log.type.toUpperCase()} ${log.tool ? `(${log.tool})` : ''}</span>
               <span style="color:#999; font-weight:normal;">${log.timestamp}</span>
             </div>
             <div style="color:#555; white-space:pre-wrap; word-break:break-word;">${logContent}</div>
             ${log.duration ? `<div style="font-size:10px; color:#888; margin-top:2px;">Duration: ${log.duration}</div>` : ''}
           `;
          traceContent.appendChild(item);
        });

        traceSection.appendChild(traceContent);
        exportContainer.appendChild(traceSection);
      }

      // Generate PDF from Text Content
      const canvas = await html2canvas(exportContainer, {
        scale: 1, // Reduced for size
        useCORS: true,
        logging: false
      });

      const imgData = canvas.toDataURL('image/jpeg', 0.8);
      const pdf = new jsPDF('p', 'mm', 'a4');
      const pdfWidth = pdf.internal.pageSize.getWidth();
      const pdfHeight = pdf.internal.pageSize.getHeight();

      let imgWidth = pdfWidth;
      let imgHeight = (canvas.height * imgWidth) / canvas.width;

      let heightLeft = imgHeight;
      let position = 0;

      pdf.addImage(imgData, 'JPEG', 0, position, imgWidth, imgHeight);
      heightLeft -= pdfHeight;

      while (heightLeft > 0) {
        position = heightLeft - imgHeight;
        pdf.addPage();
        pdf.addImage(imgData, 'JPEG', 0, position, imgWidth, imgHeight);
        heightLeft -= pdfHeight;
      }

      // 4. Append Graph Image on a New Page (if captured)
      if (graphImgData) {
        pdf.addPage();
        pdf.setFontSize(16);
        pdf.text("Agent Workflow Graph", 10, 20);

        // Calculate dynamic dimensions for the graph
        // We know A4 width is ~210mm
        const graphProps = pdf.getImageProperties(graphImgData);
        const gWidth = pdfWidth - 20; // 10mm margin each side
        const gHeight = (graphProps.height * gWidth) / graphProps.width;

        pdf.addImage(graphImgData, 'JPEG', 10, 30, gWidth, gHeight);
      }

      // Save using file-saver
      const filename = `stock-terminal-session-${new Date().toISOString().slice(0, 10)}.pdf`;
      const blob = pdf.output('blob');
      saveAs(blob, filename);

    } catch (err) {
      console.error('PDF Export Error:', err);
    } finally {
      if (document.body.contains(exportContainer)) {
        document.body.removeChild(exportContainer);
      }
    }
    }, 100);
  };

  // UI State
  const [isPerformanceExpanded, setIsPerformanceExpanded] = useState(false);
  const [isChatMaximized, setIsChatMaximized] = useState(false);
  const [reasoningSteps, setReasoningSteps] = useState([]);
  const [isReasoningExpanded, setIsReasoningExpanded] = useState(false);
  const [isTraceExpanded, setIsTraceExpanded] = useState(false);

  // Graph Logic
  const [topology, setTopology] = useState(null);
  const [activeNode, setActiveNode] = useState(null);

  // Trace Log State
  const [traceLogs, setTraceLogs] = useState([]);
  const [activeTab, setActiveTab] = useState('summary'); // 'summary' | 'trace'
  const [agentConfig, setAgentConfig] = useState(null);
  const [maximizedTab, setMaximizedTab] = useState('chat'); // 'chat' | 'workflow' | 'trace'

  // Performance & Debug State
  const [totalTokens, setTotalTokens] = useState({ prompt: 0, candidates: 0, total: 0 });
  const [allErrors, setAllErrors] = useState([]);
  const [thinkingTime, setThinkingTime] = useState(0); // in ms
  const timerRef = useRef(null);
  const chatEndRef = useRef(null);
  const maximizedChatEndRef = useRef(null);

  // Fetch AI Summary on mount or data change
  useEffect(() => {
    const fetchSummary = async () => {
      if (!dashboardData) return;
      setSummaryLoading(true);
      try {
        const res = await fetch('http://localhost:8001/summarize', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            dashboard_data: dashboardData,
            session_id: "default_summary",
            model: selectedModel
          })
        });
        const data = await res.json();
        setAiSummary(data.summary);
      } catch (err) {
        console.error("Failed to fetch AI summary:", err);
      } finally {
        setSummaryLoading(false);
      }
    };

    fetchSummary();
  }, [dashboardData, selectedModel]); // Added selectedModel to dependencies

  // Fetch FactSet Status
  const checkFactSetStatus = async () => {
    try {
      const response = await fetch('http://localhost:8001/auth/factset/status');
      const data = await response.json();
      setIsFactSetConnected(data.connected);
      setHasRefreshToken(!!data.has_refresh_token);

      if (data.connected) {
        if (data.expires_in !== undefined && data.expires_in !== null) {
          const expiryDate = new Date(Date.now() + data.expires_in * 1000);
          setFactsetExpiry(expiryDate);

          // Initial calculation to avoid "null" flash
          const seconds = Math.max(0, Math.floor((expiryDate.getTime() - Date.now()) / 1000));
          const m = Math.floor(seconds / 60);
          const s = seconds % 60;
          setTimeRemaining(`${m}:${s.toString().padStart(2, '0')}`);
        } else {
          // Connected but no expiry (maybe persistent)
          setFactsetExpiry(null);
          // Don't clear timeRemaining if it's already "00:00" from a previous tick
          if (timeRemaining !== "00:00") setTimeRemaining(null);
        }
      } else {
        setFactsetExpiry(null);
        setTimeRemaining(null);
      }

    } catch (error) {
      console.error("Error checking FactSet status:", error);
    }
  };

  // Timer Effect
  useEffect(() => {
    if (!factsetExpiry || !isFactSetConnected) {
      setTimeRemaining(null);
      return;
    }

    const updateTimer = () => {
      const now = new Date();
      const diff = factsetExpiry - now;

      if (diff <= 0) {
        setTimeRemaining("00:00");
        return;
      }

      const minutes = Math.floor(diff / 60000);
      const seconds = Math.floor((diff % 60000) / 1000);
      setTimeRemaining(`${minutes}:${seconds.toString().padStart(2, '0')}`);
    };

    updateTimer(); // Initial call
    const timerId = setInterval(updateTimer, 1000);
    return () => clearInterval(timerId);
  }, [factsetExpiry, isFactSetConnected]);

  // Initial Data Fetch & Polling
  useEffect(() => {
    checkFactSetStatus();

    // Poll status frequently when not connected or authenticating to catch the redirect quickly
    // Poll less frequently (30s) when already connected
    const statusInterval = setInterval(checkFactSetStatus, isFactSetConnected ? 30000 : 3000);

    const fetchConfig = async () => {
      try {
        const res = await fetch('http://localhost:8001/agent-config');
        const data = await res.json();
        setAgentConfig(data);
      } catch (err) {
        console.error("Failed to fetch agent config:", err);
      }
    };
    fetchConfig();

    return () => clearInterval(statusInterval);
  }, [isFactSetConnected]); // Re-run effect when connection status changes to adjust interval

  // Auto-close modal when connected
  useEffect(() => {
    if (isFactSetConnected && showAuthModal) {
      setShowAuthModal(false);
      const msg = "FactSet connection detected! I can now access real-time market data.";
      setMessages(prev => [...prev, { role: 'assistant', text: msg }]);
      addTraceLog('system', msg);
    }
  }, [isFactSetConnected, showAuthModal]);

  // Thinking Timer Logic
  useEffect(() => {
    if (chatLoading) {
      setThinkingTime(0);
      const start = Date.now();
      timerRef.current = setInterval(() => {
        setThinkingTime(Date.now() - start);
      }, 50);
    } else {
      clearInterval(timerRef.current);
    }
    return () => clearInterval(timerRef.current);
  }, [chatLoading]);

  // Auto-scroll logic
  useEffect(() => {
    if (chatEndRef.current) {
      chatEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, chatLoading]);

  useEffect(() => {
    if (maximizedChatEndRef.current && isChatMaximized) {
      maximizedChatEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, chatLoading, isChatMaximized, maximizedTab]);

  // Helper to add trace logs
  const addTraceLog = (type, content, tool = null, args = null, result = null, duration = null) => {
    setTraceLogs(prev => [...prev, {
      type,
      content,
      tool,
      args,
      result,
      duration,
      timestamp: new Date().toLocaleTimeString()
    }]);
  };

  const handleSendChat = async (messageOverride = null, options = {}) => {
    const textToSend = messageOverride || chatInput;
    if (!textToSend.trim() || chatLoading) return;

    // Capture start time for latency tracking
    const startTime = Date.now();
    const toolsUsedSet = new Set(); // Track unique tools used in this turn

    const userText = textToSend;
    const userMsg = { role: 'user', text: userText };
    setMessages(prev => [...prev, userMsg]);

    addTraceLog('user', userText);

    if (!messageOverride) setChatInput('');
    setChatLoading(true);
    if (!options?.preserveChart) {
      setChartOverride(null); // Reset chart for new query to avoid stale data merging (unless preserving)
    }
    let recommendChart = false; // Initialize flag for chart recommendation token detection

    // Append an empty assistant message so it doesn't overwrite the user bubble
    const currentImage = selectedImage;
    const currentVideo = selectedVideoUrl;
    if (currentImage) {
      userMsg.image = currentImage;
    }
    if (currentVideo) {
      userMsg.video = currentVideo;
    }
    setMessages(prev => [...prev, { role: 'assistant', text: '' }]);

    if (!messageOverride) {
      setSelectedImage(null);
      setSelectedVideoUrl(null);
    }

    try {
      const response = await fetch('http://localhost:8001/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: userText,
          image: currentImage,
          video_url: currentVideo,
          session_id: "default_chat",
          model: selectedModel,
          complex_model: selectedComplexModel
        })
      });

      if (!response.ok) {
        throw new Error(`Server responded with ${response.status}: ${response.statusText}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';
      let accumulatedText = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop(); // Keep incomplete line

        for (const line of lines) {
          if (!line.trim()) continue;
          try {
            const event = JSON.parse(line);
            if (!window.__DEBUG_EVENTS) window.__DEBUG_EVENTS = [];
            window.__DEBUG_EVENTS.push(event);

            if (event.type === 'topology') {
              if (event.data) {
                setTopology(event.data);
              }
            } else if (event.type === 'text') {
              accumulatedText += event.content;

              // NEW: STREAMING CHART PARSING ([CHART]{...}[/CHART])
              const chartRegex = /\[CHART\]([\s\S]*?)\[\/CHART\]/g;
              let chartMatch;
              while ((chartMatch = chartRegex.exec(accumulatedText)) !== null) {
                try {
                  const chartData = JSON.parse(chartMatch[1]);
                  if (setChartOverride) setChartOverride(chartData);
                } catch (e) {
                  // Ignore parse errors while still streaming
                }
              }

              if (accumulatedText.includes('[CHART_RECOMMENDED]')) {
                accumulatedText = accumulatedText.replace('[CHART_RECOMMENDED]', '');
                recommendChart = true;
              }
              setMessages(prev => {
                const newMsgs = [...prev];
                const lastMsg = newMsgs[newMsgs.length - 1] || {};

                // STREAMING WIDGET PARSING - Flexible closing tag
                const widgetRegex = /\[WIDGET:(\w+)\]([\s\S]*?)\[\/WIDGET(:\w+)?\]/g;
                let match;
                while ((match = widgetRegex.exec(accumulatedText)) !== null) {
                  const section = match[1];
                  const content = match[2];
                  if (onUpdateWidget) {
                    onUpdateWidget(section, content.trim(), false);
                  }
                }

                // Detect source and update sources list
                const sources = new Set(lastMsg.sources || []);
                const agentName = event.sourceAgent?.toLowerCase() || '';
                if (agentName.includes('factset')) sources.add('FactSet');
                if (agentName.includes('google_search') || agentName.includes('search_agent')) sources.add('Google Search');

                newMsgs[newMsgs.length - 1] = {
                  ...lastMsg, // Preserve existing props like toolsUsed
                  role: 'assistant',
                  text: accumulatedText,
                  recommendChart: recommendChart || lastMsg.recommendChart,
                  sources: Array.from(sources)
                };
                return newMsgs;
              });
            } else if (event.type === 'tool_call') {
              // Track tool usage
              toolsUsedSet.add(event.tool);

              // Highlight the active tool in the graph (Restore Green Blinking/Animation)
              if (setActiveNode) setActiveNode(event.tool);

              // Optionally show which tool is being used in the thinking indicator
              // For now we just keep the loading state
              setReasoningSteps(prev => [...prev, {
                type: 'call',
                tool: event.tool,
                args: event.args,
                timestamp: new Date().toLocaleTimeString()
              }]);
              addTraceLog('tool_call', null, event.tool, event.args);
            } else if (event.type === 'tool_result') {
              setReasoningSteps(prev => [...prev, {
                type: 'result',
                tool: event.tool,
                result: event.result,
                timestamp: new Date().toLocaleTimeString()
              }]);
              addTraceLog('tool_result', null, event.tool, null, event.result, event.duration);

              // Stop graph animation/highlighting
              if (setActiveNode) {
                // Slight delay to ensure visibility of fast tools, but careful of race conditions
                // For now, immediate clear is safer to avoid clearing a SUBSEQUENT tool
                setActiveNode(null);
              }

              // Track sources for source bubbles
              setMessages(prev => {
                const newMsgs = [...prev];
                const lastMsg = newMsgs[newMsgs.length - 1];
                if (lastMsg && lastMsg.role === 'assistant') {
                  const sources = new Set(lastMsg.sources || []);
                  if (event.tool.startsWith('FactSet')) sources.add('FactSet');
                  if (event.tool.includes('google_search') || event.tool.includes('general_search')) sources.add('Google Search');
                  lastMsg.sources = Array.from(sources);
                }
                return newMsgs;
              });

              // Check for tool-level data errors to log in Audit Log
              const isError = event.result && (
                (typeof event.result === 'object' && (event.result.error || event.result.status === 'error')) ||
                (typeof event.result === 'string' && event.result.toLowerCase().includes('error'))
              );

              // Dynamic Chart Update Logic
              // Dynamic Chart Update Logic
              if (!isError && setChartOverride) {
                try {
                  const toolName = event.tool;
                  console.log("[RightSidebar] Received tool event:", toolName, event);
                  let resultData = event.result;

                  // Handle MCP Tool Result Structure
                  if (resultData && resultData.content && Array.isArray(resultData.content) && resultData.content[0] && resultData.content[0].text) {
                    try {
                      const extractedJson = resultData.content[0].text;
                      resultData = JSON.parse(extractedJson);
                    } catch (e) {
                      console.error("Failed to parse nested JSON in content[0].text:", e);
                    }
                  } else if (typeof resultData === 'string') {
                    try { resultData = JSON.parse(resultData); } catch (e) { /* ignore */ }
                  }

                  // 1. FACTSET_GLOBALPRICES (Line/Area Chart)
                  if (toolName === 'FactSet_GlobalPrices') {
                    console.log("[RightSidebar] Processing FactSet_GlobalPrices result:", { resultData });
                    let rawData = [];
                    if (Array.isArray(resultData)) {
                      rawData = resultData;
                    } else if (resultData && Array.isArray(resultData.data)) {
                      rawData = resultData.data;
                    } else if (resultData && typeof resultData === 'object') {
                      // Attempt to handle dictionary response { "TICKER": [...] }
                      Object.values(resultData).forEach(val => {
                        if (Array.isArray(val)) rawData.push(...val);
                      });
                    }
                    console.log("[RightSidebar] Extracted rawData length:", rawData.length);

                    if (rawData.length > 0) {
                      // Group by ticker to handle multi-series correctly
                      const groups = {};
                      rawData.forEach(item => {
                        const rawTicker = item.requestId || item.fsymId;
                        const ticker = rawTicker ? rawTicker.replace(/-US$/, '') : 'Unknown';
                        if (!groups[ticker]) groups[ticker] = [];
                        groups[ticker].push(item);
                      });
                      console.log("[RightSidebar] Grouped tickers:", Object.keys(groups));

                      // Batch chart updates to prevent duplicates and race conditions
                      const newSeriesData = [];
                      Object.entries(groups).forEach(([ticker, history]) => {
                        const formattedHistory = history.map(item => {
                          let priceVal = item.price || item.close || item.unadjustedPrice || item.totalReturn || item.cumulativeReturn || item.oneDayReturn || item.percentChange || item.Price || item.Close || item.Value;
                          return {
                            date: item.date || item.unadjustedDate || item.time || item.period || item.Date || item.Time,
                            close: priceVal !== undefined ? parseFloat(priceVal) : null
                          };
                        }).filter(item => item.date && item.close !== null && !isNaN(item.close));

                        if (formattedHistory.length > 0) {
                          newSeriesData.push({
                            ticker: ticker,
                            history: formattedHistory,
                            color: null
                          });
                        }
                      });

                      if (newSeriesData.length > 0) {
                        console.log("[RightSidebar] Calling setChartOverride with:", newSeriesData);
                        setChartOverride(prev => {
                          console.log("[RightSidebar] setChartOverride prev state:", prev);
                          let existingSeries = prev?.series ? [...prev.series] : [];

                          // Handle upgrade from single to multi if needed
                          if (!prev?.series && prev?.history && prev?.chartType !== 'bar') {
                            existingSeries.push({
                              ticker: prev.ticker || 'Primary',
                              history: prev.history
                            });
                          }

                          // Merge new series, avoiding duplicates
                          newSeriesData.forEach(newItem => {
                            if (!existingSeries.find(s => s.ticker === newItem.ticker)) {
                              existingSeries.push(newItem);
                            }
                          });

                          const newState = {
                            ...prev,
                            history: null,
                            series: existingSeries,
                            chartType: 'line',
                            title: existingSeries.length > 1 ? 'Performance Comparison' : `${existingSeries[0].ticker} Performance`
                          };
                          console.log("[RightSidebar] New chart state:", newState);
                          return newState;
                        });
                        addTraceLog('system', `Updated chart with ${newSeriesData.length} tickers: ${newSeriesData.map(s => s.ticker).join(', ')}`);
                      }
                    } else {
                      console.warn("[RightSidebar] rawData was empty for FactSet_GlobalPrices");
                    }
                  }

                  // 2. FACTSET_OWNERSHIP (Bar Chart)
                  else if (toolName === 'FactSet_Ownership') {
                    let holders = resultData;
                    if (!Array.isArray(holders) && resultData.data) holders = resultData.data;

                    if (Array.isArray(holders) && holders.length > 0) {
                      // Normalize logic: { label: 'Name', value: Number }
                      const chartData = holders.map(h => ({
                        label: h.holderName || h.entityName || h.name || 'Unknown',
                        value: parseFloat(h.position || h.marketValue || 0),
                        subValue: h.percentOutstanding // Optional tooltip info
                      })).slice(0, 10); // Limit to top 10

                      setChartOverride({
                        chartType: 'bar',
                        title: 'Top Institutional Holders',
                        data: chartData,
                        yAxisLabel: 'Position',
                        ticker: 'Ownership'
                      });
                      addTraceLog('system', `Updated main chart (Ownership) with ${chartData.length} records.`);
                    }
                  }

                  // 3. FACTSET_GEOREV (Bar/Pie Chart)
                  else if (toolName === 'FactSet_GeoRev') {
                    let regions = resultData;
                    if (!Array.isArray(regions) && resultData.data) regions = resultData.data;

                    if (Array.isArray(regions) && regions.length > 0) {
                      const chartData = regions.map(r => ({
                        label: r.countryName || r.regionName || r.name || 'Unknown',
                        value: parseFloat(r.revenue || r.percent || 0),
                      })).slice(0, 10);

                      setChartOverride({
                        chartType: 'pie',
                        title: 'Revenue by Geography',
                        data: chartData,
                        yAxisLabel: 'Revenue',
                        ticker: 'GeoRev'
                      });
                      addTraceLog('system', `Updated main chart (GeoRev Pie) with ${chartData.length} regions.`);
                    }
                  }

                } catch (err) {
                  console.error("Failed to update chart from tool result:", err);
                }
              }

              if (isError) {
                const errorMsg = typeof event.result === 'object' ? (event.result.error || event.result.message || 'Unknown tool error') : event.result;
                setAllErrors(prev => [...prev, {
                  message: `[Tool: ${event.tool}] ${errorMsg}`,
                  timestamp: new Date().toLocaleTimeString(),
                  userQuery: userText
                }]);
              }
            } else if (event.type === 'error') {
              addTraceLog('error', event.content);
              const errorText = `**Error:** ${event.content}`;
              setMessages(prev => {
                const newMsgs = [...prev];
                const last = newMsgs[newMsgs.length - 1];
                if (last && last.role === 'assistant') {
                  newMsgs[newMsgs.length - 1] = {
                    role: 'assistant',
                    text: (last.text ? last.text + "\n\n" : "") + errorText
                  };
                }
                return newMsgs;
              });
              setAllErrors(prev => [...prev, {
                message: event.content,
                timestamp: new Date().toLocaleTimeString(),
                userQuery: userText
              }]);
              setReasoningSteps(prev => [...prev, {
                type: 'error',
                content: event.content,
                timestamp: new Date().toLocaleTimeString()
              }]);
            } else if (event.type === 'usage') {
              setTotalTokens(prev => ({
                prompt: prev.prompt + (event.prompt_tokens || 0),
                candidates: prev.candidates + (event.candidates_tokens || 0),
                total: prev.total + (event.total_tokens || 0)
              }));
              addTraceLog('usage', `Tokens used: ${event.total_tokens} (Prompt: ${event.prompt_tokens}, Candidates: ${event.candidates_tokens})`);
            }
          } catch (e) {
            console.error("JSON Parse Error:", e, line);
          }
        }
      }

      if (accumulatedText) {
        addTraceLog('assistant', accumulatedText);

        // Final update with latency
        const totalTime = Date.now() - startTime;
        setMessages(prev => {
          const newMsgs = [...prev];
          const lastMsg = newMsgs[newMsgs.length - 1] || {};

          // Check regex one last time in case it came in the very last chunk although unlikely for streaming
          // But safer to just rely on what we accumulated
          if (accumulatedText.includes('[CHART_RECOMMENDED]')) {
            accumulatedText = accumulatedText.replace('[CHART_RECOMMENDED]', '');
            recommendChart = true;
          }

          // WIDGET PARSING
          // Regex to find [WIDGET:SectionName]content[/WIDGET]
          const widgetRegex = /\[WIDGET:(\w+)\]([\s\S]*?)\[\/WIDGET\]/g;
          let match;
          while ((match = widgetRegex.exec(accumulatedText)) !== null) {
            const section = match[1];
            const content = match[2];
            console.log("Parsed Widget Update:", section);
            if (onUpdateWidget) {
              onUpdateWidget(section, content.trim(), false);
            }
          }

          newMsgs[newMsgs.length - 1] = {
            ...lastMsg,
            role: 'assistant',
            text: accumulatedText,
            latency: totalTime,
            toolsUsed: Array.from(toolsUsedSet),
            recommendChart: recommendChart || lastMsg.recommendChart
          };
          return newMsgs;
        });
      }

    } catch (err) {
      console.error("Chat failed:", err);
      const errMsg = "Sorry, I encountered a connection error.";
      setMessages(prev => {
        const newMsgs = [...prev];
        newMsgs[newMsgs.length - 1] = { role: 'assistant', text: errMsg };
        return newMsgs;
      });
      addTraceLog('error', errMsg);
    } finally {
      setChatLoading(false);
      // Clear media state to prevent "1 youtube link" errors on next request
      setSelectedVideoUrl(null);
      setSelectedImage(null);
      if (fileInputRef.current) fileInputRef.current.value = '';

      // Safety check: specific widget expectation
      if (options?.expectedWidget) {
        // We can't easily know if it succeeded here without checking accumulatedText again or tracking it.
        // But we can check if the widget is still "loading" in the parent if we had access, but we don't.
        // Instead, we trust the parsing logic handled it. 
        // If we want to be safe, we could explicitly "finish" it if it's not done?
        // Actually, let's just leave it. If the AI didn't generate tags, the user will see a spinner forever.
        // Better: FORCE a stop if we didn't find tags? 
        // For now, let's just let the user re-try or we can add a timeout in App.jsx.
      }
    }
  };

  useEffect(() => {
    window.triggerAgent = handleSendChat;
    return () => { delete window.triggerAgent; };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [handleSendChat]);

  const handleYouTubeUrl = () => {
    const url = prompt("Please enter the YouTube video URL:");
    if (url) {
      setSelectedVideoUrl(url);
      setIsUploadDropdownOpen(false);
    }
  };

  const handleImageUpload = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    // Check if it's an image
    if (!file.type.startsWith('image/')) {
      alert("Please select an image file.");
      return;
    }

    const reader = new FileReader();
    reader.onloadend = () => {
      setSelectedImage(reader.result);
      setIsUploadDropdownOpen(false);
    };
    reader.readAsDataURL(file);
    // Reset file input
    e.target.value = '';
  };


  const handleCreateChart = async (tableProps = null) => {
    if (tableProps) {
      console.log("[handleCreateChart] Triggered with props:", tableProps);
      try {
        const getText = (children) => {
          if (!children) return '';
          return React.Children.toArray(children).map(child => {
            if (typeof child === 'string' || typeof child === 'number') return child;
            if (child.props && child.props.children) return getText(child.props.children);
            if (Array.isArray(child)) return getText(child);
            return '';
          }).join('').trim();
        };

        const findComp = (children, type) => {
          const arr = React.Children.toArray(children);
          return arr.find(c => c && c.type === type);
        };

        const thead = findComp(tableProps.children, 'thead');
        const tbody = findComp(tableProps.children, 'tbody');

        if (thead && tbody) {
          const headRow = React.Children.toArray(thead.props.children).find(c => c && c.type === 'tr');
          if (!headRow) throw new Error("Could not find table header row");

          const headers = React.Children.toArray(headRow.props.children)
            .filter(c => c && c.type === 'th')
            .map(th => getText(th.props.children));

          const rows = React.Children.toArray(tbody.props.children)
            .filter(c => c && c.type === 'tr')
            .map(tr =>
              React.Children.toArray(tr.props.children)
                .filter(c => c && c.type === 'td')
                .map(td => getText(td.props.children))
            );

          console.log("[handleCreateChart] Extracted headers:", headers);
          console.log("[handleCreateChart] Extracted rows count:", rows.length);

          // --- INSTANT DIRECT PLOT LOGIC (Bypass LLM for standard plottable data) ---
          try {
            const isNumeric = (str) => {
              if (str === null || str === undefined || str === '') return false;
              let cleaned = String(str).replace(/[$,%\s]/g, '');
              if (cleaned.startsWith('(') && cleaned.endsWith(')')) cleaned = '-' + cleaned.slice(1, -1);
              return cleaned !== '' && !isNaN(parseFloat(cleaned)) && isFinite(cleaned);
            };
            const parseNum = (str) => {
              let cleaned = String(str).replace(/[$,%\s]/g, '');
              if (cleaned.startsWith('(') && cleaned.endsWith(')')) cleaned = '-' + cleaned.slice(1, -1);
              return parseFloat(cleaned);
            };

            // Detect label column: usually the first non-numeric column
            let labelColIdx = 0;
            for (let i = 0; i < headers.length; i++) {
              const columnValues = rows.map(r => r[i]);
              const numericCount = columnValues.filter(isNumeric).length;
              if (numericCount < rows.length * 0.5) {
                labelColIdx = i;
                break;
              }
            }

            // Detect metric columns: excluding label column
            const numericColIndices = headers.map((h, i) => {
              if (i === labelColIdx) return -1;
              const numericCount = rows.filter(r => isNumeric(r[i])).length;
              return numericCount > rows.length * 0.8 ? i : -1;
            }).filter(idx => idx !== -1);

            if (numericColIndices.length > 0 && rows.length >= 2) {
              const labelHeader = headers[labelColIdx].toLowerCase();
              const isTimeSeries = labelHeader.includes('date') || labelHeader.includes('year') || labelHeader.includes('period') || labelHeader.includes('time');
              const title = numericColIndices.length === 1 ? headers[numericColIndices[0]] : "Table Data Chart";

              // Simple heuristic: Line for many points or time series, Bar otherwise
              const chartType = (isTimeSeries || rows.length > 12) ? 'line' : 'bar';

              if (chartType === 'line') {
                const series = numericColIndices.map(colIdx => ({
                  ticker: headers[colIdx],
                  history: rows.map(r => ({
                    date: r[labelColIdx],
                    close: parseNum(r[colIdx])
                  })).filter(pt => pt.date && !isNaN(pt.close))
                }));
                setChartOverride({ chartType: 'line', title, series });
                addTraceLog('system', `Fast direct chart generated (Line): ${title}`);
                return; // SUCCESS! Bypassed LLM
              } else {
                const data = rows.map(r => ({
                  label: r[labelColIdx],
                  value: parseNum(r[numericColIndices[0]])
                })).filter(pt => pt.label && !isNaN(pt.value));
                setChartOverride({ chartType: 'bar', title, data });
                addTraceLog('system', `Fast direct chart generated (Bar): ${title}`);
                return; // SUCCESS! Bypassed LLM
              }
            }
          } catch (fastErr) {
            console.warn("[handleCreateChart] Direct plotting attempt failed:", fastErr);
          }
          // --- END DIRECT PLOT LOGIC ---

          // Use the Backend Curator for intelligent plotting (Fallback)
          const response = await fetch('http://localhost:8001/curate-chart', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              headers,
              rows,
              context: [...messages].reverse().find(m => m.role === 'user')?.text || ""
            })
          });

          if (response.ok) {
            const chartConfig = await response.json();
            console.log("[handleCreateChart] Curation success:", chartConfig);
            setChartOverride(chartConfig);
            return;
          } else {
            const errBody = await response.text();
            console.error("[handleCreateChart] Curation backend error:", errBody);
          }
        } else {
          console.warn("[handleCreateChart] Missing head or body in props.children");
        }
      } catch (e) {
        console.error("Chart curation failed:", e);
      }
    }
    handleSendChat("Please visualize the data discussed above.");
  };

  const handleConnectFactSet = async () => {
    // Open window immediately to satisfy popup blockers
    const authWindow = window.open('', '_blank');
    if (authWindow) {
      authWindow.document.write('<div style="font-family: sans-serif; display: flex; align-items: center; justify-content: center; height: 100vh;">Loading FactSet Authentication...</div>');
    }

    try {
      // Pass session_id to ensure the backend maps the code correctly
      const res = await fetch('http://localhost:8001/auth/factset/url?session_id=default_chat');
      const data = await res.json();
      if (data.auth_url && authWindow) {
        setAuthUrl(data.auth_url);
        authWindow.location.href = data.auth_url;
        setShowAuthModal(true);
      } else {
        if (authWindow) authWindow.close();
        alert("Failed to generate authentication URL.");
      }
    } catch (e) {
      console.error("Failed to get auth url:", e);
      if (authWindow) authWindow.close();
    }
  };

  const handleAuthSubmit = async () => {
    try {
      if (showAdvancedAuth) {
        if (!manualRefreshToken.trim()) {
          alert("Please provide a Refresh Token.");
          return;
        }
        const res = await fetch('http://localhost:8001/auth/factset/manual', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ refresh_token: manualRefreshToken, session_id: "default_chat" })
        });
        if (res.ok) {
          setIsFactSetConnected(true);
          setShowAuthModal(false);
          setManualRefreshToken('');
          const msg = "Successfully connected to FactSet using Manual Refresh Token! session is now persistent.";
          setMessages(prev => [...prev, { role: 'assistant', text: msg }]);
          addTraceLog('system', msg);
        } else {
          const data = await res.json();
          alert("Manual Authentication failed: " + (data.detail || "Unknown error"));
        }
        return;
      }

      const res = await fetch('http://localhost:8001/auth/factset/callback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ redirect_url: authInput, session_id: "default_chat" })
      });
      if (res.ok) {
        setIsFactSetConnected(true);
        setShowAuthModal(false);
        const msg = "Successfully connected to FactSet! I can now access real-time market data.";
        setMessages(prev => [...prev, { role: 'assistant', text: msg }]);
        addTraceLog('system', msg);
      } else {
        alert("Authentication failed. Please check the URL.");
      }
    } catch (e) {
      alert("Error connecting: " + e.message);
    }
  };


  return (
    <aside className={`right-sidebar ${isChatMaximized ? 'maximized' : ''}`}>

      {/* Header and Controls */}
      <div className="right-sidebar-header">
        {isChatMaximized ? (
          /* Maximized Header with Tabs */
          <div style={{ display: 'flex', alignItems: 'center', gap: '20px', flex: 1 }}>
            <h3 style={{ fontSize: '18px', fontWeight: 'bold', color: '#004b87', margin: 0 }}>Stock Terminal Agent</h3>
            <div style={{ display: 'flex', background: '#f0f2f5', padding: '4px', borderRadius: '8px', gap: '4px' }}>
              {['chat', 'workflow', 'graph', 'trace', 'agent', 'errors'].map(tab => (
                <button
                  key={tab}
                  onClick={() => setMaximizedTab(tab)}
                  style={{
                    padding: '6px 12px',
                    border: 'none',
                    borderRadius: '6px',
                    background: maximizedTab === tab ? '#fff' : 'transparent',
                    color: maximizedTab === tab ? '#004b87' : '#666',
                    fontWeight: maximizedTab === tab ? 600 : 400,
                    fontSize: '12px',
                    cursor: 'pointer',
                    boxShadow: maximizedTab === tab ? '0 1px 3px rgba(0,0,0,0.1)' : 'none',
                    textTransform: 'capitalize'
                  }}
                >
                  {tab === 'workflow' ? 'Agent Workflow' : tab === 'agent' ? 'Agent Config' : tab}
                </button>
              ))}
            </div>
            <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <button
                onClick={handleDownloadPDF}
                title="Download Session as PDF"
                style={{
                  padding: '6px 12px',
                  borderRadius: '6px',
                  border: '1px solid #ddd',
                  background: '#fff',
                  color: '#5f6368',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                  fontSize: '12px',
                  fontWeight: 500
                }}
              >
                <Download size={16} />
                Save PDF
              </button>
              <button
                onClick={() => setIsChatMaximized(false)}
                style={{
                  marginLeft: 'auto',
                  background: 'none',
                  border: 'none',
                  cursor: 'pointer',
                  padding: '8px',
                  display: 'flex',
                  alignItems: 'center',
                  color: '#666'
                }}
                title="Minimize"
              >
                <Minimize2 size={20} />
              </button>
            </div>
          </div>
        ) : (
          /* Standard Sidebar Header - Simplified */
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', minWidth: 0, flex: 1, paddingBottom: '4px' }}>

              {/* Row 1: Session Actions - Professional Dashboard Grid */}


              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px', gap: '8px', padding: '0 2px' }}>
                <div style={{ display: 'flex', gap: '6px', alignItems: 'center' }}>
                  <button
                    onClick={handleDownloadPDF}
                    title="Download Session as PDF"
                    style={{
                      padding: '6px',
                      background: '#f8fafc',
                      border: '1px solid #e2e8f0',
                      borderRadius: '6px',
                      color: '#64748b',
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      transition: 'all 0.2s',
                      boxShadow: '0 1px 2px rgba(0,0,0,0.05)'
                    }}
                  >
                    <Download size={14} />
                  </button>
                  <span style={{ fontSize: '10px', fontWeight: '800', color: '#334155', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Terminal</span>
                </div>

                <button
                  onClick={handleConnectFactSet}
                  style={{
                    fontSize: '10px',
                    padding: '5px 12px',
                    borderRadius: '6px',
                    border: timeRemaining === "00:00" ? '1px solid #f59e0b' : (isFactSetConnected ? '1px solid #10b981' : '1px solid #3b82f6'),
                    background: timeRemaining === "00:00" ? '#fef3c7' : (isFactSetConnected ? '#ecfdf5' : '#3b82f6'),
                    color: timeRemaining === "00:00" ? '#b45309' : (isFactSetConnected ? '#059669' : 'white'),
                    cursor: (isFactSetConnected && timeRemaining !== "00:00") ? 'default' : 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '6px',
                    fontWeight: '600',
                    boxShadow: '0 1px 2px rgba(0,0,0,0.1)'
                  }}
                >
                  {isFactSetConnected ? (
                    <>
                      <div style={{ width: '6px', height: '6px', borderRadius: '50%', background: '#10b981', boxShadow: '0 0 4px rgba(16, 185, 129, 0.6)' }}></div>
                      <span>{timeRemaining ? timeRemaining : 'Connected'}</span>
                    </>
                  ) : (
                    <>
                      <Cloud size={12} />
                      <span>Connect</span>
                    </>
                  )}
                </button>
              </div>

              {/* Row 2: Config (Dual Models - Compact Grid) */}
              <div style={{
                display: 'grid',
                gridTemplateColumns: '1fr 1fr',
                gap: '8px',
                padding: '8px',
                background: '#f8fafc',
                borderRadius: '8px',
                border: '1px solid #e2e8f0',
                marginBottom: '4px'
              }}>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '3px' }}>
                  <label style={{ fontSize: '8px', fontWeight: '800', color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.025em' }}>Basic</label>
                  <select
                    value={selectedModel}
                    onChange={(e) => setSelectedModel(e.target.value)}
                    style={{
                      width: '100%',
                      background: 'white',
                      fontSize: '10px',
                      color: '#1e293b',
                      border: '1px solid #cbd5e1',
                      borderRadius: '4px',
                      padding: '4px 6px',
                      outline: 'none',
                      cursor: 'pointer',
                      appearance: 'none',
                      backgroundImage: 'url("data:image/svg+xml;charset=UTF-8,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' viewBox=\'0 0 24 24\' fill=\'none\' stroke=\'%2364748b\' stroke-width=\'2\' stroke-linecap=\'round\' stroke-linejoin=\'round\'%3E%3Cpolyline points=\'6 9 12 15 18 9\'%3E%3C/polyline%3E%3C/svg%3E")',
                      backgroundRepeat: 'no-repeat',
                      backgroundPosition: 'right 4px center',
                      backgroundSize: '10px'
                    }}
                  >
                    <option value="gemini-2.5-flash-lite">2.5 Lite</option>
                    <option value="gemini-2.5-flash">2.5 Flash</option>
                    <option value="gemini-2.5-pro">2.5 Pro</option>
                    <option value="gemini-3-flash-preview">3.0 Flash</option>
                    <option value="gemini-3-pro-preview">3.0 Pro</option>
                  </select>
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '3px' }}>
                  <label style={{ fontSize: '8px', fontWeight: '800', color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.025em' }}>Complex</label>
                  <select
                    value={selectedComplexModel}
                    onChange={(e) => setSelectedComplexModel(e.target.value)}
                    style={{
                      width: '100%',
                      background: 'white',
                      fontSize: '10px',
                      color: '#7c3aed',
                      border: '1px solid #cbd5e1',
                      borderRadius: '4px',
                      padding: '4px 6px',
                      outline: 'none',
                      cursor: 'pointer',
                      appearance: 'none',
                      backgroundImage: 'url("data:image/svg+xml;charset=UTF-8,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' viewBox=\'0 0 24 24\' fill=\'none\' stroke=\'%237c3aed\' stroke-width=\'2\' stroke-linecap=\'round\' stroke-linejoin=\'round\'%3E%3Cpolyline points=\'6 9 12 15 18 9\'%3E%3C/polyline%3E%3C/svg%3E")',
                      backgroundRepeat: 'no-repeat',
                      backgroundPosition: 'right 4px center',
                      backgroundSize: '10px'
                    }}
                  >
                    <option value="gemini-2.5-flash">2.5 Flash</option>
                    <option value="gemini-3-flash-preview">3.0 Flash</option>
                    <option value="gemini-3-pro-preview">3.0 Pro</option>
                  </select>
                </div>
              </div>

              {/* Row 3: Utility (Maximize) */}
              <div style={{ display: 'flex', justifyContent: 'flex-end', width: '100%', marginTop: '4px' }}>
                <button
                  title="Maximize Chat and Workflow View"
                  onClick={() => setIsChatMaximized(true)}
                  style={{
                    padding: '4px',
                    color: '#004b87',
                    borderRadius: '4px',
                    hover: { background: '#f0f4f8' }
                  }}
                >
                  <Maximize2 size={12} />
                </button>
              </div>
          </div>
        )}
      </div>

      <div className="right-content" style={{ display: 'flex', flexDirection: 'column', flex: 1, minHeight: 0 }}>

        {/* Render Logic based on Mode */}
        {isChatMaximized ? (
          <>
            {maximizedTab === 'chat' && (
              <>
                <div className="chat-messages maximized" style={{ flex: 1, overflowY: 'auto', padding: '20px' }}>
                  {messages.map((msg, idx) => {
                    if (msg.role === 'assistant' && !msg.image && (!msg.text || !msg.text.trim())) return null;
                    return (
                    <div key={idx} className={`msg ${msg.role}`} style={{
                      fontSize: '14px',
                      padding: '12px 16px',
                      borderRadius: '12px',
                      maxWidth: '70%',
                      marginBottom: '12px',
                      alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start',
                      background: msg.role === 'user' ? '#e6f0ff' : '#f0f2f5',
                      color: msg.role === 'user' ? '#004b87' : 'var(--text-primary)',
                      border: msg.role === 'user' ? '1px solid #cce0ff' : '1px solid #e6ebf1',
                      wordBreak: 'break-word',
                        overflow: 'visible',
                    }}>
                      {msg.image && (
                        <div style={{ marginBottom: '8px' }}>
                          <img src={msg.image} alt="Uploaded" style={{ maxWidth: '100%', borderRadius: '8px', border: '1px solid #ddd' }} />
                        </div>
                      )}
                        <div style={{ position: 'relative' }}>
                          <ReactMarkdown
                            remarkPlugins={[remarkGfm]}
                            components={{
                              table: ({ node, ...props }) => (
                                <div style={{ position: 'relative', margin: '16px 0' }}>
                                  <table {...props} />
                                  <div style={{
                                    position: 'absolute',
                                    top: '-8px',
                                    right: '-8px',
                                    zIndex: 10
                                  }}>
                                    <button
                                      onClick={() => handleCreateChart(props)}
                                      style={{
                                        background: 'linear-gradient(135deg, #7c3aed 0%, #3b82f6 100%)',
                                        color: 'white',
                                        border: 'none',
                                        borderRadius: '50%',
                                        width: '32px',
                                        height: '32px',
                                        display: 'flex',
                                        alignItems: 'center',
                                        justifyContent: 'center',
                                        cursor: 'pointer',
                                        boxShadow: '0 4px 12px rgba(124, 58, 237, 0.4)',
                                        transition: 'transform 0.2s'
                                      }}
                                      onMouseEnter={(e) => e.currentTarget.style.transform = 'scale(1.1)'}
                                      onMouseLeave={(e) => e.currentTarget.style.transform = 'scale(1)'}
                                      title="AI Generate Chart"
                                    >
                                      <Sparkles size={16} />
                                    </button>
                                  </div>
                                </div>
                              )
                            }}
                          >
                            {msg.text}
                          </ReactMarkdown>
                        </div>

                        {/* Maximized View Chart Suggestions */}
                        {msg.role === 'assistant' && msg.recommendChart && (
                          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginTop: '16px', padding: '16px', background: 'rgba(124, 58, 237, 0.05)', borderRadius: '12px', border: '1px solid rgba(124, 58, 237, 0.1)' }}>
                            <div style={{ fontSize: '13px', fontWeight: 600, color: '#4c1d95', display: 'flex', alignItems: 'center', gap: '8px' }}>
                              <Sparkles size={14} style={{ color: '#7c3aed' }} />
                              Recommended Visualizations:
                            </div>
                            <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
                              <button
                                onClick={() => handleSendChat("Generate a Line Chart for this data.")}
                                style={{ padding: '8px 16px', borderRadius: '20px', background: 'white', border: '1px solid #7c3aed', color: '#7c3aed', fontSize: '12px', fontWeight: 600, cursor: 'pointer', transition: 'all 0.2s' }}
                                onMouseEnter={(e) => e.currentTarget.style.background = '#f5f3ff'}
                                onMouseLeave={(e) => e.currentTarget.style.background = 'white'}
                              >
                                Line Chart
                              </button>
                              <button
                                onClick={() => handleSendChat("Generate a Bar Chart for this data.")}
                                style={{ padding: '8px 16px', borderRadius: '20px', background: 'white', border: '1px solid #3b82f6', color: '#3b82f6', fontSize: '12px', fontWeight: 600, cursor: 'pointer', transition: 'all 0.2s' }}
                                onMouseEnter={(e) => e.currentTarget.style.background = '#eff6ff'}
                                onMouseLeave={(e) => e.currentTarget.style.background = 'white'}
                              >
                                Bar Chart
                              </button>
                              <button
                                onClick={() => handleSendChat("Display as Comparison Chart.")}
                                style={{ padding: '8px 16px', borderRadius: '20px', background: '#f0f9ff', border: '1px solid #0369a1', color: '#0369a1', fontSize: '12px', fontWeight: 600, cursor: 'pointer', transition: 'all 0.2s' }}
                                onMouseEnter={(e) => e.currentTarget.style.background = '#e0f2fe'}
                                onMouseLeave={(e) => e.currentTarget.style.background = '#f0f9ff'}
                              >
                                Multi-Ticker Compare
                              </button>
                            </div>
                          </div>
                        )}
                        {msg.latency && (
                          <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '4px' }}>
                            <span style={{
                              fontSize: '10px',
                              background: 'rgba(0,0,0,0.05)',
                              padding: '2px 6px',
                              borderRadius: '10px',
                              color: '#666',
                              fontWeight: 500
                            }}>
                              {(msg.latency / 1000).toFixed(2)}s
                            </span>
                          </div>
                        )}
                        {msg.sources && msg.sources.length > 0 && (
                          <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap', marginTop: '8px' }}>
                            {msg.sources.map(source => (
                              <span key={source} style={{
                                fontSize: '10px',
                                padding: '2px 8px',
                                borderRadius: '12px',
                                fontWeight: 600,
                                background: source === 'FactSet' ? '#e1f5fe' : '#e8f5e9',
                                color: source === 'FactSet' ? '#01579b' : '#2e7d32',
                                border: source === 'FactSet' ? '1px solid #b3e5fc' : '1px solid #c8e6c9',
                              }}>
                                {source}
                              </span>
                            ))}
                          </div>
                        )}
                        {!chartOverride && msg.role === 'assistant' && idx === messages.length - 1 && (
                          <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '8px' }}>
                            <button
                              onClick={handleCreateChart}
                              style={{
                                background: '#e6f0ff',
                                color: '#004b87',
                                border: 'none',
                                padding: '6px 12px',
                                borderRadius: '16px',
                                fontSize: '12px',
                                cursor: 'pointer',
                                display: 'flex',
                                alignItems: 'center',
                                gap: '6px',
                                fontWeight: 500,
                                transition: 'background 0.2s',
                                boxShadow: '0 1px 2px rgba(0,0,0,0.05)'
                              }}
                              onMouseEnter={(e) => e.target.style.background = '#d0e1ff'}
                              onMouseLeave={(e) => e.target.style.background = '#e6f0ff'}
                            >
                              <Activity size={12} />
                              Need a chart?
                            </button>
                          </div>
                        )}
                      </div>
                    );
                  })}
                  {chatLoading && (messages[messages.length - 1]?.role !== 'assistant' || (messages[messages.length - 1]?.text && messages[messages.length - 1]?.text.trim() === '')) && (
                    <div className="small blinking" style={{ fontStyle: 'italic', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '8px' }}>
                      Assistant is thinking... <span>({(thinkingTime / 1000).toFixed(2)}s)</span>
                    </div>
                  )}
                  <div ref={maximizedChatEndRef} />
                </div>
                <div className="chat-input-container maximized" style={{ padding: '20px', borderTop: '1px solid #eee' }}>
                  <div style={{ maxWidth: '800px', margin: '0 auto', width: '100%', display: 'flex', gap: '12px', alignItems: 'center', background: '#f8f9fa', borderRadius: '24px', padding: '12px 20px', border: '1px solid #e0e0e0' }}>

                    <div style={{ position: 'relative' }} ref={dropdownRef}>
                      <button
                        onClick={() => setIsUploadDropdownOpen(!isUploadDropdownOpen)}
                        style={{ background: 'none', border: 'none', cursor: 'pointer', padding: '4px', display: 'flex', alignItems: 'center' }}>
                        <Plus size={20} color="#004b87" />
                      </button>

                      {isUploadDropdownOpen && (
                        <div style={{
                          position: 'absolute',
                          bottom: '100%',
                          left: 0,
                          marginBottom: '12px',
                          background: '#1a1c1e',
                          borderRadius: '12px',
                          boxShadow: '0 8px 32px rgba(0,0,0,0.4)',
                          width: '240px',
                          padding: '8px 0',
                          zIndex: 1000,
                          border: '1px solid #333'
                        }}>
                          <div
                            style={{
                              padding: '12px 16px',
                              cursor: 'pointer',
                              display: 'flex',
                              alignItems: 'center',
                              gap: '12px',
                              color: '#fff',
                              transition: 'background 0.2s',
                              borderRadius: '8px'
                            }}
                            onMouseEnter={(e) => e.currentTarget.style.background = '#333'}
                            onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
                            onClick={() => fileInputRef.current.click()}
                          >
                            <Upload size={18} color="#aaa" />
                            <div style={{ textAlign: 'left' }}>
                              <div style={{ fontSize: '14px', fontWeight: 500 }}>Upload</div>
                              <div style={{ fontSize: '12px', color: '#888' }}>Provide local files</div>
                            </div>
                          </div>

                          <div
                            style={{
                              padding: '12px 16px',
                              cursor: 'pointer',
                              display: 'flex',
                              alignItems: 'center',
                              gap: '12px',
                              color: '#fff',
                              transition: 'background 0.2s',
                              borderRadius: '8px'
                            }}
                            onMouseEnter={(e) => e.currentTarget.style.background = '#333'}
                            onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
                            onClick={handleYouTubeUrl}
                          >
                            <Youtube size={18} color="#aaa" />
                            <div style={{ textAlign: 'left' }}>
                              <div style={{ fontSize: '14px', fontWeight: 500 }}>YouTube video link</div>
                              <div style={{ fontSize: '12px', color: '#888' }}>Provide a link to a YouTube video</div>
                            </div>
                          </div>

                          <div style={{ padding: '8px 16px', display: 'flex', alignItems: 'center', gap: '12px', color: '#444', opacity: 0.5, cursor: 'not-allowed' }}>
                            <Link size={16} /> <span style={{ fontSize: '13px' }}>By URL</span>
                          </div>
                          <div style={{ padding: '8px 16px', display: 'flex', alignItems: 'center', gap: '12px', color: '#444', opacity: 0.5, cursor: 'not-allowed' }}>
                            <Cloud size={16} /> <span style={{ fontSize: '13px' }}>Google Drive</span>
                          </div>
                        </div>
                      )}
                    </div>

                    <textarea
                      placeholder={isFactSetConnected ? "Ask FactSet anything..." : "How can FactSet help?"}
                      value={chatInput}
                      onChange={(e) => setChatInput(e.target.value)}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter' && !e.shiftKey) {
                          e.preventDefault();
                          handleSendChat();
                        }
                      }}
                      rows={Math.min(Math.max(chatInput.split('\n').length, 1), 10)}
                      style={{
                        border: 'none',
                        background: 'transparent',
                        flex: 1,
                        fontSize: '14px',
                        outline: 'none',
                        resize: 'none',
                        paddingTop: '4px',
                        fontFamily: 'inherit'
                      }}
                    />
                    <input
                      type="file"
                      ref={fileInputRef}
                      onChange={handleImageUpload}
                      accept="image/*"
                      style={{ display: 'none' }}
                    />
                  </div>
                  {selectedImage && (
                    <div style={{ maxWidth: '800px', margin: '8px auto', position: 'relative', width: 'fit-content' }}>
                      <img src={selectedImage} style={{ height: '60px', borderRadius: '4px', border: '1px solid #ddd' }} alt="Preview" />
                      <button
                        onClick={() => setSelectedImage(null)}
                        style={{ position: 'absolute', top: '-8px', right: '-8px', background: '#dc3545', color: '#fff', border: 'none', borderRadius: '50%', width: '18px', height: '18px', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer', padding: 0 }}
                      >
                        <X size={12} />
                      </button>
                    </div>
                  )}
                  {selectedVideoUrl && (
                    <div style={{ maxWidth: '800px', margin: '8px auto', position: 'relative', width: 'fit-content', background: '#f8f9fa', padding: '6px 12px', borderRadius: '6px', border: '1px solid #dee2e6', display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <Youtube size={16} color="#ff0000" />
                      <span style={{ fontSize: '12px', color: '#004b87', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', maxWidth: '300px' }}>{selectedVideoUrl}</span>
                      <button
                        onClick={() => setSelectedVideoUrl(null)}
                        style={{ background: 'none', border: 'none', color: '#666', cursor: 'pointer', padding: 2, display: 'flex' }}
                      >
                        <X size={14} />
                      </button>
                    </div>
                  )}
                </div>
              </>
            )}
            {maximizedTab === 'workflow' && (
              <div style={{ flex: 1, overflowY: 'auto', padding: '20px', background: '#fafafa' }}>
                <ReasoningChain
                  steps={reasoningSteps}
                  isExpanded={true}
                  onToggleExpand={() => { }}
                  thinkingTime={thinkingTime}
                />
              </div>
            )}
            {maximizedTab === 'graph' && (
              <div id="printable-agent-graph" style={{ flex: 1, overflow: 'hidden', background: '#f8f9fa' }}>
                {topology ? (
                  <AgentGraph topology={topology} activeNodeId={activeNode} />
                ) : (
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: '#aaa' }}>
                    No active plan. Run a complex query to generate an agent graph.
                  </div>
                )}
              </div>
            )}
            {maximizedTab === 'trace' && (
              <div style={{ flex: 1, overflowY: 'auto', background: '#fff' }}>
                <TraceLog logs={traceLogs} isMaximized={true} />
              </div>
            )}
            {maximizedTab === 'agent' && (
              <div style={{ flex: 1, overflowY: 'auto', padding: '40px', background: '#fafafa' }}>
                <div style={{ maxWidth: '900px', margin: '0 auto' }}>
                  <h2 style={{ fontSize: '24px', color: '#004b87', marginBottom: '24px', borderBottom: '2px solid #004b87', paddingBottom: '8px', display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <Sparkles size={24} />
                    AI Agent Configuration
                  </h2>

                  {!agentConfig ? (
                    <div style={{ textAlign: 'center', padding: '40px', color: '#666' }}>Loading configuration...</div>
                  ) : (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '32px' }}>
                      {/* Standard Agent */}
                      <section style={{ background: '#fff', borderRadius: '12px', padding: '24px', boxShadow: '0 2px 8px rgba(0,0,0,0.05)', border: '1px solid #eee' }}>
                        <h3 style={{ fontSize: '18px', color: '#333', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                          <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#6c757d' }}></div>
                          Standard Assistant: <span style={{ color: '#004b87' }}>{agentConfig.standard_agent.name}</span>
                        </h3>
                        <div style={{ marginBottom: '20px' }}>
                          <h4 style={{ fontSize: '14px', color: '#666', marginBottom: '8px', fontWeight: 600 }}>System Instructions:</h4>
                          <div style={{ background: '#f8f9fa', padding: '16px', borderRadius: '8px', fontSize: '13px', color: '#444', lineHeight: '1.6', whiteSpace: 'pre-wrap', border: '1px solid #eee' }}>
                            {agentConfig.standard_agent.instruction}
                          </div>
                        </div>
                        <div>
                          <h4 style={{ fontSize: '14px', color: '#666', marginBottom: '8px', fontWeight: 600 }}>Tools & Capabilities:</h4>
                          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '12px' }}>
                            {agentConfig.standard_agent.tools.map((tool, i) => (
                              <div key={i} style={{ background: '#f0f4f8', padding: '12px', borderRadius: '8px', border: '1px solid #dce4ec' }}>
                                <div style={{ fontWeight: 600, color: '#004b87', fontSize: '12px', marginBottom: '4px' }}>{tool.name}</div>
                                <div style={{ fontSize: '11px', color: '#555' }}>{tool.description}</div>
                              </div>
                            ))}
                          </div>
                        </div>
                      </section>

                      {/* FactSet Agent */}
                      <section style={{ background: '#fff', borderRadius: '12px', padding: '24px', boxShadow: '0 2px 8px rgba(0,0,0,0.05)', border: '1px solid #eee' }}>
                        <h3 style={{ fontSize: '18px', color: '#333', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                          <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#28a745' }}></div>
                          FactSet Analyst: <span style={{ color: '#28a745' }}>{agentConfig.factset_agent.name}</span>
                        </h3>
                        <div style={{ marginBottom: '20px' }}>
                          <h4 style={{ fontSize: '14px', color: '#666', marginBottom: '8px', fontWeight: 600 }}>System Instructions:</h4>
                          <div style={{ background: '#f8f9fa', padding: '16px', borderRadius: '8px', fontSize: '13px', color: '#444', lineHeight: '1.6', whiteSpace: 'pre-wrap', border: '1px solid #eee' }}>
                            {agentConfig.factset_agent.instruction}
                          </div>
                        </div>
                        <div>
                          <h4 style={{ fontSize: '14px', color: '#666', marginBottom: '8px', fontWeight: 600 }}>Tools & Capabilities:</h4>
                          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '12px' }}>
                            {agentConfig.factset_agent.tools.map((tool, i) => (
                              <div key={i} style={{ background: '#e6ffea', padding: '12px', borderRadius: '8px', border: '1px solid #c3e6cb' }}>
                                <div style={{ fontWeight: 600, color: '#28a745', fontSize: '12px', marginBottom: '4px' }}>{tool.name}</div>
                                <div style={{ fontSize: '11px', color: '#155724' }}>{tool.description}</div>
                              </div>
                            ))}
                          </div>
                        </div>
                      </section>
                    </div>
                  )}
                </div>
              </div>
            )}
            {maximizedTab === 'errors' && (
              <div style={{ flex: 1, overflowY: 'auto', padding: '40px', background: '#fafafa' }}>
                <div style={{ maxWidth: '900px', margin: '0 auto' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px', borderBottom: '2px solid #dc3545', paddingBottom: '8px' }}>
                    <h2 style={{ fontSize: '24px', color: '#dc3545', margin: 0, display: 'flex', alignItems: 'center', gap: '12px' }}>
                      <AlertCircle size={24} />
                      System Error Audit Log
                    </h2>
                    <button
                      onClick={() => setAllErrors([])}
                      style={{ padding: '6px 12px', background: '#fff', border: '1px solid #ddd', borderRadius: '6px', fontSize: '12px', cursor: 'pointer' }}
                    >
                      Clear Log
                    </button>
                  </div>

                  {allErrors.length === 0 ? (
                    <div style={{ textAlign: 'center', padding: '60px', color: '#999', background: '#fff', borderRadius: '12px', border: '1px dashed #ccc' }}>
                      <CheckCircle size={48} style={{ color: '#28a745', marginBottom: '16px', opacity: 0.5 }} />
                      <p>No errors detected in this session.</p>
                    </div>
                  ) : (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                      {[...allErrors].reverse().map((err, i) => (
                        <div key={i} style={{ background: '#fff', borderRadius: '12px', padding: '20px', boxShadow: '0 2px 8px rgba(0,0,0,0.05)', borderLeft: '4px solid #dc3545' }}>
                          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px' }}>
                            <span style={{ fontSize: '11px', fontWeight: 600, color: '#dc3545', textTransform: 'uppercase' }}>Error Event</span>
                            <span style={{ fontSize: '11px', color: '#999' }}>{err.timestamp}</span>
                          </div>
                          <div style={{ background: '#fff5f5', padding: '12px', borderRadius: '8px', border: '1px solid #fed7d7', color: '#c53030', fontSize: '13px', fontFamily: 'monospace', marginBottom: '12px', whiteSpace: 'pre-wrap' }}>
                            {err.message}
                          </div>
                          {err.userQuery && (
                            <div style={{ fontSize: '12px', color: '#666', borderTop: '1px solid #eee', paddingTop: '10px' }}>
                              <span style={{ fontWeight: 600 }}>Originating Query:</span> "{err.userQuery}"
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            )}
          </>
        ) : (
          /* Standard Sidebar Content - Collapsible Widgets */
          <>
            {/* Summary Widget */}
            <div className="reasoning-chain-container" style={{ marginBottom: '12px' }}>
              <div
                className="reasoning-header"
                onClick={() => setIsPerformanceExpanded(!isPerformanceExpanded)}
              >
                <div className="reasoning-title">
                  <Sparkles size={14} className="icon-pulse" />
                  <span>Stock Performance & Summary</span>
                </div>
                {isPerformanceExpanded ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
              </div>
              {isPerformanceExpanded && (
                <div className="reasoning-body" style={{ padding: '12px' }}>
                  {summaryLoading ? (
                    <p className="small">Generating AI Summary...</p>
                  ) : aiSummary ? (
                    <div className="summary-section ai-powered">
                      <div className="markdown-content">
                        <ReactMarkdown remarkPlugins={[remarkGfm]}>{aiSummary}</ReactMarkdown>
                      </div>
                    </div>
                  ) : (
                    <p className="small">Select a ticker to generate real-time AI insights.</p>
                  )}
                </div>
              )}
            </div>

            {/* Trace Log Widget */}
            <div className="reasoning-chain-container" style={{ marginBottom: '12px' }}>
              <div
                className="reasoning-header"
                onClick={() => setIsTraceExpanded(!isTraceExpanded)}
              >
                <div className="reasoning-title">
                  <Terminal size={14} style={{ color: 'var(--brand)' }} />
                  <span>Session Trace Log <span className="step-count">({traceLogs.length})</span></span>
                    {allErrors.length > 0 && (
                      <div
                        onClick={(e) => {
                          e.stopPropagation();
                          setIsChatMaximized(true);
                          setMaximizedTab('errors');
                        }}
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          gap: '4px',
                          marginLeft: '8px',
                          padding: '2px 6px',
                          background: '#fff0f0',
                          border: '1px solid #ffcccb',
                          borderRadius: '4px',
                          color: '#dc3545',
                          fontSize: '10px',
                          cursor: 'pointer',
                          fontWeight: 600
                        }}
                      >
                        <AlertCircle size={10} />
                        {allErrors.length} Errors
                      </div>
                    )}
                </div>
                {isTraceExpanded ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
              </div>
              {isTraceExpanded && (
                  <div className="reasoning-body" style={{ padding: '0', borderTop: '1px solid #eee', maxHeight: '250px', overflowY: 'auto' }}>
                  <TraceLog logs={traceLogs} />
                </div>
              )}
            </div>

            <div className="divider" style={{ height: '1px', background: 'var(--border-light)', margin: '16px 0' }}></div>

            {/* Reasoning Visualization Component (Collapsible) */}
            <ErrorBoundary fallback={<div className="small error-msg" style={{ padding: '8px' }}>Unable to display reasoning chain.</div>}>
              <ReasoningChain
                steps={reasoningSteps}
                isExpanded={isReasoningExpanded}
                onToggleExpand={() => setIsReasoningExpanded(!isReasoningExpanded)}
                thinkingTime={thinkingTime}
              />
            </ErrorBoundary>

            {/* Chat Messages Area (Dynamic Height) */}
            <div className="chat-messages" style={{
              display: 'flex',
              flexDirection: 'column',
              gap: '12px',
              flex: 1,
              overflowY: 'auto',
              padding: '8px 4px',
              marginTop: '8px'
            }}>
              {messages.map((msg, idx) => (
                <div key={idx} className={`msg ${msg.role}`} style={{
                  fontSize: '13px',
                  lineHeight: '1.5',
                  padding: '10px 14px',
                  borderRadius: '12px',
                  maxWidth: '92%',
                  alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start',
                  background: msg.role === 'user' ? '#e6f0ff' : '#f0f2f5',
                  color: msg.role === 'user' ? '#004b87' : 'var(--text-primary)',
                  border: msg.role === 'user' ? '1px solid #cce0ff' : '1px solid #e6ebf1',
                  wordBreak: 'break-word',
                  overflow: 'visible',
                  boxShadow: '0 1px 2px rgba(0,0,0,0.05)',
                  display: (msg.role === 'assistant' && !msg.image && (!msg.text || !msg.text.trim())) ? 'none' : 'block'
                }}>
                  {msg.image && (
                    <div style={{ marginBottom: '6px' }}>
                      <img src={msg.image} alt="Uploaded" style={{ maxWidth: '100%', borderRadius: '6px', border: '1px solid #ddd' }} />
                    </div>
                  )}
                  <div style={{ position: 'relative' }}>
                    <ReactMarkdown
                      remarkPlugins={[remarkGfm]}
                      components={{
                        table: ({ node, ...props }) => (
                          <div style={{ position: 'relative', margin: '16px 0' }}>
                            <table {...props} />
                            <div style={{
                              position: 'absolute',
                              top: '-8px',
                              right: '-8px',
                              zIndex: 10
                            }}>
                              <button
                                onClick={() => handleCreateChart(props)}
                                style={{
                                  background: 'linear-gradient(135deg, #7c3aed 0%, #3b82f6 100%)',
                                  color: 'white',
                                  border: 'none',
                                  borderRadius: '50%',
                                  width: '28px',
                                  height: '28px',
                                  display: 'flex',
                                  alignItems: 'center',
                                  justifyContent: 'center',
                                  cursor: 'pointer',
                                  boxShadow: '0 4px 12px rgba(124, 58, 237, 0.3)',
                                  transition: 'transform 0.2s'
                                }}
                                onMouseEnter={(e) => e.currentTarget.style.transform = 'scale(1.1)'}
                                onMouseLeave={(e) => e.currentTarget.style.transform = 'scale(1)'}
                                title="AI Generate Chart"
                              >
                                <Sparkles size={14} />
                              </button>
                            </div>
                          </div>
                        )
                      }}
                    >
                      {msg.text}
                    </ReactMarkdown>
                  </div>

                  {/* Enhanced Chart Options if recommended */}
                  {msg.role === 'assistant' && msg.recommendChart && (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginTop: '12px', padding: '12px', background: '#f8fafc', borderRadius: '12px', border: '1px solid #e2e8f0' }}>
                      <div style={{ fontSize: '11px', fontWeight: 600, color: '#475569', display: 'flex', alignItems: 'center', gap: '6px' }}>
                        <Sparkles size={12} style={{ color: '#7c3aed' }} />
                        Visualize this data:
                      </div>
                      <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                        <button
                          onClick={() => handleSendChat("Generate a Line Chart for this data.")}
                          style={{ padding: '6px 12px', borderRadius: '16px', background: 'white', border: '1px solid #7c3aed', color: '#7c3aed', fontSize: '11px', fontWeight: 600, cursor: 'pointer' }}
                        >
                          Show Line Chart
                        </button>
                        <button
                          onClick={() => handleSendChat("Generate a Bar Chart for this data.")}
                          style={{ padding: '6px 12px', borderRadius: '16px', background: 'white', border: '1px solid #3b82f6', color: '#3b82f6', fontSize: '11px', fontWeight: 600, cursor: 'pointer' }}
                        >
                          Show Bar Chart
                        </button>
                        <button
                          onClick={() => handleSendChat("Display as Comparison Chart.")}
                          style={{ padding: '6px 12px', borderRadius: '16px', background: '#f0f9ff', border: '1px solid #0369a1', color: '#0369a1', fontSize: '11px', fontWeight: 600, cursor: 'pointer' }}
                        >
                          Multi-Series Compare
                        </button>
                      </div>
                    </div>
                  )}

                  {/* Source Badges for Standard View */}
                  {msg.sources && msg.sources.length > 0 && (
                    <div style={{ display: 'flex', gap: '4px', flexWrap: 'wrap', marginTop: '6px' }}>
                      {msg.sources.map(source => (
                        <span key={source} style={{
                          fontSize: '9px',
                          padding: '2px 6px',
                          borderRadius: '10px',
                          fontWeight: 600,
                          background: source === 'FactSet' ? '#e1f5fe' : '#e8f5e9',
                          color: source === 'FactSet' ? '#01579b' : '#2e7d32',
                          border: source === 'FactSet' ? '1px solid #b3e5fc' : '1px solid #c8e6c9',
                        }}>
                          {source}
                        </span>
                      ))}
                    </div>
                  )}

                  {msg.latency && (
                    <div style={{ display: 'flex', justifyContent: 'flex-end', alignItems: 'center', marginTop: '4px', gap: '6px' }}>
                      {/* Tool Usage Badges */}
                      {msg.toolsUsed && msg.toolsUsed.map((tool) => {
                        // Special Case: Google Search should be a specific darker green
                        const isSearch = tool === 'perform_google_search';

                        // Generate a consistent color for other tools
                        let colorHex = '#6c757d';
                        if (isSearch) {
                          colorHex = '#a3e635'; // Lime-ish green, but let's make it darker/more professional
                        } else {
                          let hash = 0;
                          for (let i = 0; i < tool.length; i++) {
                            hash = tool.charCodeAt(i) + ((hash << 5) - hash);
                          }
                          const c = (hash & 0x00FFFFFF).toString(16).toUpperCase();
                          colorHex = '#' + '00000'.substring(0, 6 - c.length) + c;
                        }

                        return (
                          <span key={tool} style={{
                            fontSize: '9px',
                            background: isSearch ? '#166534' : colorHex, // Dark green for search
                            color: '#fff',
                            padding: '2px 6px',
                            borderRadius: '12px', // Fully rounded/oval
                            fontWeight: 600,
                            textShadow: '0 1px 2px rgba(0,0,0,0.2)', // Better legibility
                            opacity: 0.9
                          }}>
                            {tool}
                          </span>
                        );
                      })}

                      {/* Fallback Badge for Pure Knowledge */}
                      {(!msg.toolsUsed || msg.toolsUsed.length === 0) && (!msg.sources || msg.sources.length === 0) && (
                        <span style={{
                          fontSize: '9px',
                          background: '#6c757d', // Neutral grey for internal knowledge
                          color: '#fff',
                          padding: '2px 6px',
                          borderRadius: '12px',
                          fontWeight: 600,
                          opacity: 0.9
                        }}>
                          Knowledge Base
                        </span>
                      )}

                      <span style={{
                        fontSize: '9px',
                        background: 'rgba(0,0,0,0.05)',
                        padding: '1px 5px',
                        borderRadius: '8px',
                        color: '#888',
                        fontWeight: 500
                      }}>
                        {(msg.latency / 1000).toFixed(2)}s
                      </span>
                    </div>
                  )}
                </div>
              ))}
              {chatLoading && (
                <div className="small blinking" style={{
                  fontStyle: 'italic',
                  color: 'var(--text-muted)',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  padding: '8px 12px',
                  fontSize: '12px',
                  background: '#fdfdfd',
                  borderRadius: '8px',
                  border: '1px dashed #eee',
                  alignSelf: 'flex-start'
                }}>
                  {messages[messages.length - 1]?.text ? 'Assistant is working...' : 'Assistant is thinking...'}
                  <span>({(thinkingTime / 1000).toFixed(2)}s)</span>
                </div>
              )}
                <div ref={chatEndRef} />
            </div>

              {/* Suggested Actions: Data Visualization */
                !chartOverride &&
                messages.length > 0 &&
                messages[messages.length - 1].role === 'assistant' &&
                messages[messages.length - 1].recommendChart && (
                  <div style={{ padding: '0 16px 8px 16px', display: 'flex', justifyContent: 'flex-end' }}>
                    <button
                      onClick={() => handleSendChat("Please visualize the above data as a chart.")}
                      style={{
                        background: '#e6f0ff', border: '1px solid #cce0ff', borderRadius: '16px',
                        padding: '6px 12px', fontSize: '11px', color: '#004b87', cursor: 'pointer',
                        display: 'flex', alignItems: 'center', gap: '6px', fontWeight: 500,
                        boxShadow: '0 1px 2px rgba(0,0,0,0.05)'
                      }}
                    >
                      <Activity size={12} />
                      Need a chart?
                    </button>
                  </div>
                )}

            {/* Input Area (Bottom) */}
              <div className="chat-input-container" style={{ marginTop: 8, gap: 12, display: 'flex', alignItems: 'center', background: '#fff', borderRadius: '12px', padding: '10px 14px', boxShadow: '0 2px 8px rgba(0,0,0,0.05)', flexWrap: 'wrap' }}>

              <div style={{ position: 'relative' }} ref={dropdownRef}>
                <button
                  onClick={() => setIsUploadDropdownOpen(!isUploadDropdownOpen)}
                  style={{ background: 'none', border: 'none', cursor: 'pointer', padding: '4px', display: 'flex', alignItems: 'center' }}>
                  <Plus size={16} color="#004b87" />
                </button>

                {isUploadDropdownOpen && (
                  <div style={{
                    position: 'absolute',
                    bottom: '100%',
                    left: 0,
                    marginBottom: '10px',
                    background: '#1a1c1e',
                    borderRadius: '8px',
                    boxShadow: '0 8px 32px rgba(0,0,0,0.4)',
                    width: '200px',
                    padding: '6px 0',
                    zIndex: 1000,
                    border: '1px solid #333'
                  }}>
                    <div
                      style={{
                        padding: '10px 14px',
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '10px',
                        color: '#fff',
                        transition: 'background 0.2s'
                      }}
                      onMouseEnter={(e) => e.currentTarget.style.background = '#333'}
                      onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
                      onClick={() => fileInputRef.current.click()}
                    >
                      <Upload size={16} color="#aaa" />
                      <div style={{ fontSize: '13px', fontWeight: 500 }}>Upload</div>
                    </div>

                    <div
                      style={{
                        padding: '10px 14px',
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '10px',
                        color: '#fff',
                        transition: 'background 0.2s'
                      }}
                      onMouseEnter={(e) => e.currentTarget.style.background = '#333'}
                      onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
                      onClick={handleYouTubeUrl}
                    >
                      <Youtube size={16} color="#aaa" />
                      <div style={{ fontSize: '13px', fontWeight: 500 }}>YouTube video link</div>
                    </div>
                  </div>
                )}
              </div>

                <textarea
                placeholder={isFactSetConnected ? "Ask FactSet anything..." : "How can FactSet help?"}
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                      e.preventDefault();
                      handleSendChat();
                    }
                  }}
                  rows={Math.min(Math.max(chatInput.split('\n').length, 1), 6)}
                  style={{
                    border: 'none',
                    background: 'transparent',
                    flex: 1,
                    fontSize: '13px',
                    outline: 'none',
                    resize: 'none',
                    paddingTop: '2px',
                    fontFamily: 'inherit'
                  }}
              />
              <input
                type="file"
                ref={fileInputRef}
                onChange={handleImageUpload}
                accept="image/*"
                style={{ display: 'none' }}
              />

                <button
                  onClick={() => handleSendChat("Create a chart based on the latest data.")}
                  title="Generate Chart"
                  style={{
                    background: '#f0f2f5', border: 'none', borderRadius: '50%',
                    width: '32px', height: '32px', display: 'flex', alignItems: 'center', justifyContent: 'center',
                    cursor: 'pointer', color: '#666'
                  }}
                >
                  <Activity size={16} />
                </button>
            </div>
            {selectedImage && (
              <div style={{ position: 'relative', width: 'fit-content', marginTop: '4px', marginLeft: '4px' }}>
                <img src={selectedImage} style={{ height: '40px', borderRadius: '4px', border: '1px solid #ddd' }} alt="Preview" />
                <button
                  onClick={() => setSelectedImage(null)}
                  style={{ position: 'absolute', top: '-6px', right: '-6px', background: '#dc3545', color: '#fff', border: 'none', borderRadius: '50%', width: '14px', height: '14px', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer', padding: 0 }}
                >
                  <X size={10} />
                </button>
              </div>
            )}
            {selectedVideoUrl && (
              <div style={{ position: 'relative', width: 'fit-content', marginTop: '4px', marginLeft: '4px', background: '#f8f9fa', padding: '4px 8px', borderRadius: '4px', border: '1px solid #dee2e6', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <Youtube size={14} color="#ff0000" />
                <span style={{ fontSize: '11px', color: '#004b87', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', maxWidth: '180px' }}>{selectedVideoUrl}</span>
                <button
                  onClick={() => setSelectedVideoUrl(null)}
                  style={{ background: 'none', border: 'none', color: '#666', cursor: 'pointer', padding: 1, display: 'flex' }}
                >
                  <X size={12} />
                </button>
              </div>
            )}
          </>
        )
        }

        {
          showAuthModal && (
            <div style={{
              position: 'absolute', top: 0, left: 0, right: 0, bottom: 0,
              background: 'rgba(255,255,255,0.98)', zIndex: 100,
              display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '30px',
              borderRadius: '12px'
            }}>
              <div style={{
                width: '48px', height: '48px', borderRadius: '50%', border: '3px solid #f0f7ff',
                borderTopColor: '#004b87', animation: 'spin 1s linear infinite', marginBottom: '20px'
              }} />

              <h3 style={{ color: '#004b87', marginBottom: '8px' }}>Authenticating with FactSet</h3>
              <p style={{ fontSize: '13px', color: '#4b5563', marginBottom: '24px', textAlign: 'center', lineHeight: '1.6' }}>
                Please complete the login in the new window.<br />
                <span className="blinking" style={{ fontWeight: 600, color: '#004b87' }}>Waiting for secure handshake...</span>
              </p>

              <div style={{ width: '100%', maxWidth: '300px', marginBottom: '24px' }}>
                <div
                  onClick={() => setShowAdvancedAuth(!showAdvancedAuth)}
                  style={{
                    display: 'flex', alignItems: 'center', gap: '8px',
                    cursor: 'pointer', fontSize: '12px', color: '#666', marginBottom: '12px',
                    padding: '8px', borderRadius: '6px', background: '#f8fafc', border: '1px solid #e2e8f0'
                  }}
                >
                  <div style={{
                    width: '32px', height: '16px', background: showAdvancedAuth ? '#10b981' : '#cbd5e1',
                    borderRadius: '8px', position: 'relative', transition: 'background 0.2s'
                  }}>
                    <div style={{
                      width: '12px', height: '12px', background: '#fff', borderRadius: '50%',
                      position: 'absolute', top: '2px', left: showAdvancedAuth ? '18px' : '2px',
                      transition: 'left 0.2s'
                    }} />
                  </div>
                  <span>Troubleshoot / Manual Entry</span>
                </div>

                {showAdvancedAuth && (
                  <div style={{ animation: 'fadeIn 0.3s ease-in-out' }}>
                    <p style={{ fontSize: '11px', color: '#64748b', marginBottom: '8px' }}>Manual Paste (Backup):</p>
                    <textarea
                      placeholder="Paste redirect URL or Refresh Token here..."
                      value={manualRefreshToken || authInput}
                      onChange={(e) => {
                        if (e.target.value.includes('code=')) setAuthInput(e.target.value);
                        else setManualRefreshToken(e.target.value);
                      }}
                      style={{
                        width: '100%', padding: '10px', border: '1px solid #e2e8f0',
                        borderRadius: '6px', height: '60px', fontSize: '11px', fontFamily: 'monospace',
                        background: '#fff', marginBottom: '12px'
                      }}
                    />
                    <button
                      onClick={handleAuthSubmit}
                      style={{
                        width: '100%', padding: '8px', borderRadius: '6px', border: 'none',
                        background: '#004b87', color: '#fff', cursor: 'pointer', fontWeight: 600, fontSize: '12px'
                      }}
                    >
                      Process Manual Token
                    </button>
                  </div>
                )}
              </div>

              <div style={{ display: 'flex', gap: '12px' }}>
                <button
                  onClick={() => setShowAuthModal(false)}
                  style={{ padding: '8px 20px', borderRadius: '6px', border: '1px solid #e2e8f0', background: '#fff', cursor: 'pointer', color: '#64748b', fontSize: '13px' }}
                >
                  Cancel
                </button>
                <a
                  href={authUrl}
                  target="_blank"
                  rel="noreferrer"
                  style={{ 
                    padding: '8px 20px', borderRadius: '6px', border: 'none',
                    background: '#f8fafc', color: '#004b87', cursor: 'pointer',
                    fontWeight: 600, fontSize: '13px', textDecoration: 'none'
                  }}
                >
                  Re-open Window
                </a>
              </div>
            </div>
          )
        }
      </div>

      <style jsx="true">{`
        @keyframes blink {
          0% { opacity: 1; }
          50% { opacity: 0.4; }
          100% { opacity: 1; }
        }
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(-5px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .blinking {
          animation: blink 1.5s linear infinite;
        }
        .right-sidebar {
          width: ${isOpen ? `${width}px` : '0'};
          padding: ${isOpen ? '16px' : '0'};
          opacity: ${isOpen ? '1' : '0'};
          background: #fff;
          border-left: ${isOpen ? '1px solid var(--border-light)' : 'none'};
          display: flex;
          flex-direction: column;
          transition: width 0.1s ease-out, padding 0.3s ease, opacity 0.2s ease, border-left 0.3s ease;
          height: 100vh; /* Ensure full height to enable internal scrolling */
          overflow: hidden; /* Prevent sidebar itself from scroll, let content handle it */
          pointer-events: ${isOpen ? 'auto' : 'none'};
        }
        .right-sidebar.maximized {
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            z-index: 1000;
            border-left: none;
            padding: 24px;
        }

        .right-sidebar-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 16px;
        }
        .tab {
          background: none;
          border: none;
          padding: 4px 0;
          font-size: 11px;
          font-weight: 600;
          color: #888;
          cursor: pointer;
          border-bottom: 2px solid transparent;
          display: flex;
          align-items: center;
          gap: 6px;
        }
        .tab.active {
          color: #004b87;
          border-bottom-color: #004b87;
        }
        
        .chat-input-container {
          display: flex;
          align-items: flex-end; /* Align to bottom for multiline */
          gap: 8px;
          padding: 8px 12px;
          background: #f8f9fa;
          border-radius: 20px;
          border: 1px solid #e9ecef;
        }
        .chat-input-container input, .chat-input-container textarea {
          border: none;
          background: transparent;
          flex: 1;
          font-size: 12px;
          outline: none;
          font-family: inherit;
        }
        .summary-section {
          margin-bottom: 16px;
        }
        .summary-section h3 {
          font-size: 12px;
          font-weight: 700;
          color: #495057;
          margin-bottom: 4px;
        }
        .summary-section p, .summary-section li {
          font-size: 11px;
          color: #666;
          line-height: 1.4;
        }
        .insights-list {
          padding-left: 16px;
          margin: 0;
        }
        .link {
          color: #004b87;
          text-decoration: underline;
          cursor: pointer;
        }
        .small { font-size: 10px; color: #888; }
        
        .markdown-content p { margin-bottom: 8px; }
        .markdown-content ul { padding-left: 16px; margin-bottom: 8px; }
        
        /* Table Styles for Chat */
        .msg table {
          border-collapse: collapse;
          width: 100%;
          margin: 8px 0;
          font-size: 10px;
          display: block;
          overflow-x: auto;
        }
        .msg th, .msg td {
          border: 1px solid #e9ecef;
          padding: 6px 8px;
          text-align: left;
          min-width: 80px;
        }
        .msg th {
          background-color: #f8f9fa;
          font-weight: 700;
          color: #004b87;
        }
        .msg tr:nth-child(even) {
          background-color: #fafbfc;
        }
      `}</style>
    </aside >
  );
};

export default RightSidebar;
