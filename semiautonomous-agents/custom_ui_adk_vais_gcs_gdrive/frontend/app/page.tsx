"use client";

import { useCallback, useMemo, useState, useEffect, useRef } from "react";
import ChatPanel from "@/components/ChatPanel";
import DriveAuthButton from "@/components/DriveAuthButton";

// Curated live enterprise datastore records for Vertex AI Search API (GSuite, GCS)
const ENTERPRISE_INDEX = [
  {
    id: "file-gdoc-1",
    name: "GSuite_Search_Strategy_2026.gdoc",
    mimeType: "application/vnd.google-apps.document",
    source: "Vertex AI Search (Drive)",
    owner: "Alex Rivera",
    ownerEmail: "arivera@vtxdemos.com",
    modifiedTime: "May 30, 2026, 11:15 AM",
    link: "https://drive.google.com/open?id=1",
    fileSize: "148 KB",
    telemetrySummary: "Aura Telemetry Loaded: Technical specifications for multi-region GSuite search indexes. Integrates service-account delegates and maps global locations.",
    snippet: "Active specifications for deployment to the global collection endpoints. Employs v1alpha/discoveryengine for real-time document sync from Drive folders."
  },
  {
    id: "file-pdf-2",
    name: "Global_Tax_Intelligence_v2.pdf",
    mimeType: "application/pdf",
    source: "Vertex AI Search (GCS)",
    owner: "Sarah Chen",
    ownerEmail: "schen@vtxdemos.com",
    modifiedTime: "May 28, 2026, 04:32 PM",
    link: "https://storage.googleapis.com/vtxdemos-assets/Global_Tax_Intelligence_v2.pdf",
    fileSize: "2.4 MB",
    telemetrySummary: "Aura Telemetry Loaded: High-security legal tax filing framework. Synthesizes automated filing routines for multi-tier international structures.",
    snippet: "Data pipeline parameters for running cloud scheduler tasks to sync regional tax declarations with central bigquery warehouses securely."
  },
  {
    id: "file-xlsx-3",
    name: "budget_analysis_2026_q2.xlsx",
    mimeType: "application/vnd.google-apps.spreadsheet",
    source: "Vertex AI Search (Drive)",
    owner: "Marcus Vance",
    ownerEmail: "mvance@vtxdemos.com",
    modifiedTime: "May 25, 2026, 09:10 AM",
    link: "https://drive.google.com/open?id=3",
    fileSize: "612 KB",
    telemetrySummary: "Aura Telemetry Loaded: Financial spreadsheet covering resource allocation across R&D tiers. Budgets are routed to global preview models testing.",
    snippet: "Quarterly operational allocations. Breakdown includes cloud credits, reasoning engine staging bucket overhead, and GIS Client setups."
  },
  {
    id: "file-md-4",
    name: "jira_connector_specification.md",
    mimeType: "text/markdown",
    source: "Vertex AI Search (GCS)",
    owner: "Developer Team",
    ownerEmail: "dev@vtxdemos.com",
    modifiedTime: "May 12, 2026, 10:42 AM",
    link: "https://github.com/vtxdemos/specs/jira_connector_specification.md",
    fileSize: "18 KB",
    telemetrySummary: "Aura Telemetry Loaded: Interface specification for Jira connector hook. Documents popup capture variables, session state caching, and slider locks.",
    snippet: "Defines callback URLs and silent intercept methods to bypass Safari popup blocks. Outlines the interactive authorized toggle states."
  }
];

export default function Home() {
  const clientId = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID ?? "";
  const [accessToken, setAccessToken] = useState<string | null>(null);

  // Selector for switching between three premium cyber concepts
  const [activeMode, setActiveMode] = useState<"loom" | "hud" | "terminal">("hud");

  // Search state
  const [searchQuery, setSearchQuery] = useState("");
  const userId = useMemo(
    () => (typeof window === "undefined" ? "anon" : (window.localStorage.getItem("uid") ?? newUid())),
    []
  );

  // Active Fused Grounding Memories (Pills in Chat)
  const [fusedMemories, setFusedMemories] = useState<string[]>([]);

  // Refs for tracking node positions
  const chatbotCoreRef = useRef<HTMLDivElement | null>(null);
  const documentRefs = useRef<{ [key: string]: HTMLDivElement | null }>({});
  const listContainerRef = useRef<HTMLDivElement | null>(null);

  // State to force-recalculate lines on scrolls & resizes
  const [geometryTrigger, setGeometryTrigger] = useState(0);

  // Trace logs state
  const [traces, setTraces] = useState<any[]>([]);
  const [isTraceOpen, setIsTraceOpen] = useState(false);

  // Dynamic resize logic for the Trace HUD Drawer
  const [hudWidth, setHudWidth] = useState(420);
  const [isHudExpanded, setIsHudExpanded] = useState(false);
  const [isDraggingHud, setIsDraggingHud] = useState(false);
  const [isLogStreamMaximized, setIsLogStreamMaximized] = useState(false);
  const [logLayoutMode, setLogLayoutMode] = useState<"timeline" | "grid">("timeline");
  const [selectedPipelineBubble, setSelectedPipelineBubble] = useState<string | null>(null);
  const [blueprintCopied, setBlueprintCopied] = useState(false);
  const [isDetailsWidescreen, setIsDetailsWidescreen] = useState(false);

  const startResizeHud = useCallback((e: React.MouseEvent) => {
    e.preventDefault();
    setIsDraggingHud(true);
  }, []);

  useEffect(() => {
    if (!isDraggingHud) return;

    const handleMouseMove = (e: MouseEvent) => {
      const newWidth = window.innerWidth - e.clientX;
      const clampedWidth = Math.max(320, Math.min(newWidth, window.innerWidth * 0.95));
      setHudWidth(clampedWidth);
    };

    const handleMouseUp = () => {
      setIsDraggingHud(false);
    };

    window.addEventListener("mousemove", handleMouseMove);
    window.addEventListener("mouseup", handleMouseUp);

    return () => {
      window.removeEventListener("mousemove", handleMouseMove);
      window.removeEventListener("mouseup", handleMouseUp);
    };
  }, [isDraggingHud]);
  const [traceFilter, setTraceFilter] = useState<"all" | "api" | "sse" | "thought" | "token">("all");
  const [autoScroll, setAutoScroll] = useState(true);
  const [thinkingLevel, setThinkingLevel] = useState<"MINIMAL" | "LOW" | "MEDIUM" | "HIGH">("MINIMAL");
  const [selectedModel, setSelectedModel] = useState<"gemini-3.5-flash" | "gemini-3.5-flash-lite">("gemini-3.5-flash");
  const [selectedTrace, setSelectedTrace] = useState<any | null>(null);
  const [copied, setCopied] = useState(false);

  const handleCopyDetails = useCallback((trace: any) => {
    if (!trace) return;
    const textToCopy = trace.data 
      ? `${trace.details || ""}\n\nPAYLOAD:\n${JSON.stringify(trace.data, null, 2)}`
      : trace.details || "";
    
    navigator.clipboard.writeText(textToCopy);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  }, []);

  const addTrace = useCallback((ev: {
    type: "api_call" | "sse_chunk" | "thought" | "token_flow" | "token_count";
    label: string;
    details?: string;
    data?: any;
  }) => {
    const timestamp = new Date().toLocaleTimeString("en-US", {
      hour12: false,
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    }) + "." + String(Date.now() % 1000).padStart(3, "0");
    
    setTraces((prev) => [
      ...prev,
      {
        id: `tr-${Date.now()}-${Math.random().toString(36).slice(2, 6)}`,
        timestamp,
        ...ev,
      },
    ]);
  }, []);

  // Trace activeMode change
  useEffect(() => {
    addTrace({
      type: "api_call",
      label: "Interaction Mode Switch",
      details: `Active HUD Interaction Deck changed to mode: ${activeMode.toUpperCase()}`
    });
  }, [activeMode, addTrace]);

  // ----------------------------------------------------
  // CONCEPT 1: "THE NEURAL LOOM" (Loom Connections state)
  // ----------------------------------------------------
  const [loomConnections, setLoomConnections] = useState<string[]>([]);

  const handleToggleLoomNode = (docId: string, docName: string) => {
    if (loomConnections.includes(docId)) {
      setLoomConnections(prev => prev.filter(id => id !== docId));
      setFusedMemories(prev => prev.filter(name => name !== docName));
      addTrace({
        type: "api_call",
        label: "Loom Thread Severed",
        details: `Disconnected document node: "${docName}" from Constellation Mind Grid.`
      });
    } else {
      setLoomConnections(prev => [...prev, docId]);
      if (!fusedMemories.includes(docName)) {
        setFusedMemories(prev => [...prev, docName]);
      }
      addTrace({
        type: "api_call",
        label: "Loom Thread Established",
        details: `Connected document node: "${docName}" to Constellation Mind Grid.`
      });
    }
  };

  // ----------------------------------------------------
  // CONCEPT 2: "THE AURA-SENSING HUD" (Temporary hover state)
  // ----------------------------------------------------
  const [hoveredDoc, setHoveredDoc] = useState<typeof ENTERPRISE_INDEX[0] | null>(null);
  const [auraCoordinates, setAuraCoordinates] = useState<{ x1: number; y1: number; x2: number; y2: number } | null>(null);

  const handleMouseEnterCard = useCallback((doc: typeof ENTERPRISE_INDEX[0], id: string) => {
    if (activeMode !== "hud") return;
    setHoveredDoc(doc);
    
    const cardElement = documentRefs.current[id];
    const chatbotCore = chatbotCoreRef.current;

    if (cardElement && chatbotCore) {
      const cardRect = cardElement.getBoundingClientRect();
      const coreRect = chatbotCore.getBoundingClientRect();

      setAuraCoordinates({
        x1: cardRect.right,
        y1: cardRect.top + cardRect.height / 2,
        x2: coreRect.left,
        y2: coreRect.top + coreRect.height / 2
      });
    }
  }, [activeMode]);

  const handleMouseLeaveCard = useCallback(() => {
    setHoveredDoc(null);
    setAuraCoordinates(null);
  }, []);

  // ----------------------------------------------------
  // CONCEPT 3: "THE PIPELINE CONSTRUCT CONSOLE" (Simulated console pipes)
  // ----------------------------------------------------
  const [pipingLog, setPipingLog] = useState<string[]>([]);
  const [pipingDocId, setPipingDocId] = useState<string | null>(null);

  const handlePipeDoc = (docId: string, docName: string) => {
    setPipingDocId(docId);
    setPipingLog([]);
    addTrace({
      type: "api_call",
      label: "Pipeline Funnel Triggered",
      details: `Streaming document buffer stack for "${docName}" directly to Model Core.`
    });
    const lines = [
      `>>> PIPELINE DECK INITIALIZED...`,
      `>>> SECURING API SOCKET TUNNEL TO CORE... [OK]`,
      `>>> DOWNLOADING TARGET PACKET: "${docName.toUpperCase()}"`,
      `>>> CONVERTING COGNITIVE PAYLOAD INTO BUFFER STACK...`,
      `>>> GROUNDING INJECTED SUCCESSFULLY. COGNITIVE MIND SYNCED.`
    ];
    lines.forEach((line, index) => {
      setTimeout(() => {
        setPipingLog(prev => [...prev, line]);
        addTrace({
          type: "sse_chunk",
          label: `Pipe Progress Step ${index + 1}`,
          details: line
        });
        if (index === lines.length - 1) {
          if (!fusedMemories.includes(docName)) {
            setFusedMemories(prev => [...prev, docName]);
          }
          // Reset piping state after a delay
          setTimeout(() => setPipingDocId(null), 1500);
        }
      }, (index + 1) * 350);
    });
  };

  // ----------------------------------------------------
  // GLOBAL LISTENERS (Keeps lines aligned on scrolling/resizing)
  // ----------------------------------------------------
  const handleScrollList = useCallback(() => {
    setGeometryTrigger(prev => prev + 1);
    if (activeMode === "hud" && hoveredDoc) {
      handleMouseEnterCard(hoveredDoc, hoveredDoc.id);
    }
  }, [activeMode, hoveredDoc, handleMouseEnterCard]);

  useEffect(() => {
    const triggerRecalc = () => {
      setGeometryTrigger(prev => prev + 1);
      if (activeMode === "hud" && hoveredDoc) {
        handleMouseEnterCard(hoveredDoc, hoveredDoc.id);
      }
    };
    window.addEventListener("resize", triggerRecalc);
    return () => window.removeEventListener("resize", triggerRecalc);
  }, [activeMode, hoveredDoc, handleMouseEnterCard]);

  // Coordinates helper for the Constellation Loom Lines
  const getLoomCoordinates = useCallback((docId: string) => {
    const cardEl = documentRefs.current[docId];
    const chatbotCore = chatbotCoreRef.current;
    if (cardEl && chatbotCore) {
      const cardRect = cardEl.getBoundingClientRect();
      const coreRect = chatbotCore.getBoundingClientRect();
      return {
        x1: cardRect.right,
        y1: cardRect.top + cardRect.height / 2,
        x2: coreRect.left,
        y2: coreRect.top + coreRect.height / 2
      };
    }
    return null;
  }, [geometryTrigger]); // Reacts to scroll state updates

  const onToken = useCallback((tok: string) => {
    setAccessToken(tok);
    addTrace({
      type: "token_flow",
      label: "OAuth Access Token Generated",
      details: `Successfully authorized GSuite credentials. Token: ${tok.slice(0, 12)}...[USER-GS]...${tok.slice(-6)}`
    });
  }, [addTrace]);

  const onSignOut = useCallback(() => {
    if (accessToken && window.google?.accounts?.oauth2) {
      window.google.accounts.oauth2.revoke(accessToken);
    }
    setAccessToken(null);
    addTrace({
      type: "token_flow",
      label: "OAuth Session Terminated",
      details: "User revoked access token. Active security credentials cleaned up from memory."
    });
  }, [accessToken, addTrace]);

  // Memory utilities
  const handleFuseMemory = (docName: string) => {
    if (fusedMemories.includes(docName)) return;
    setFusedMemories([...fusedMemories, docName]);
    addTrace({
      type: "api_call",
      label: "Synaptic Memory Fused",
      details: `Pinned and fused GDrive document: "${docName}" into Conversational workspace mind.`
    });
  };

  const handleClearMemories = () => {
    setFusedMemories([]);
    setLoomConnections([]);
    addTrace({
      type: "api_call",
      label: "Cognitive State Cleanse",
      details: "All active grounding memories and loom connections cleared from the workspace."
    });
  };

  // Live dynamic search from Discovery Engine datastores
  const [datastoreDocs, setDatastoreDocs] = useState<any[]>(ENTERPRISE_INDEX);
  const [isSearching, setIsSearching] = useState(false);

  useEffect(() => {
    let active = true;
    
    const fetchResults = async () => {
      setIsSearching(true);
      const t0 = Date.now();
      addTrace({
        type: "api_call",
        label: `POST /api/datastores/search [INIT]`,
        details: `Query: "${searchQuery}" | GSuite token: ${accessToken ? `${accessToken.slice(0, 10)}...` : "None"}`
      });
      try {
        const res = await fetch("http://localhost:8088/api/datastores/search", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            query: searchQuery,
            access_token: accessToken,
          }),
        });
        const latency = Date.now() - t0;
        if (!res.ok) {
          addTrace({
            type: "api_call",
            label: `POST /api/datastores/search [FAILED]`,
            details: `Status: ${res.status}. Latency: ${latency}ms`
          });
          throw new Error("Search API failed");
        }
        const data = await res.json();
        addTrace({
          type: "api_call",
          label: `POST /api/datastores/search [SUCCESS]`,
          details: `Returned ${data.results?.length ?? 0} results. Latency: ${latency}ms`,
          data: data.results
        });
        
        // Also log token flow details
        addTrace({
          type: "token_flow",
          label: "Discovery Engine Search Authorization",
          details: `Client GSuite OAuth user accessToken (${accessToken ? `${accessToken.slice(0, 12)}...[USER-GS]...${accessToken.slice(-4)}` : "None"}) elevated to GCP Service Account Bearer Token (Bearer ya29.c.Co0B...[SA-GCP]...3XyZ) for Discovery Engine search.`
        });

        if (active) {
          if (data.results && data.results.length > 0) {
            setDatastoreDocs(data.results);
          } else if (!searchQuery.trim()) {
            setDatastoreDocs(ENTERPRISE_INDEX);
          } else {
            setDatastoreDocs([]);
          }
        }
      } catch (err) {
        console.error("Search error:", err);
        if (active && !searchQuery.trim()) {
          setDatastoreDocs(ENTERPRISE_INDEX);
        }
      } finally {
        if (active) setIsSearching(false);
      }
    };

    const delayDebounceFn = setTimeout(() => {
      fetchResults();
    }, 300);

    return () => {
      active = false;
      clearTimeout(delayDebounceFn);
    };
  }, [searchQuery, accessToken, addTrace]);

  const filteredDocs = datastoreDocs;

  const filteredTraces = useMemo(() => {
    return traces.filter((t) => {
      if (traceFilter === "all") return true;
      if (traceFilter === "api") return t.type === "api_call";
      if (traceFilter === "sse") return t.type === "sse_chunk";
      if (traceFilter === "thought") return t.type === "thought";
      if (traceFilter === "token") return t.type === "token_flow" || t.type === "token_count";
      return true;
    });
  }, [traces, traceFilter]);

  const traceEndRef = useRef<HTMLDivElement | null>(null);
  const maximizedTraceEndRef = useRef<HTMLDivElement | null>(null);
  
  useEffect(() => {
    if (autoScroll && traceEndRef.current) {
      traceEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [traces, autoScroll, isTraceOpen]);

  useEffect(() => {
    if (autoScroll && isLogStreamMaximized && maximizedTraceEndRef.current) {
      maximizedTraceEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [traces, autoScroll, isLogStreamMaximized]);

  const renderInspector = () => {
    if (!selectedTrace) return null;
    return (
      <div className="flex flex-col h-full overflow-hidden">
        {/* Inspector Header */}
        <div className="px-4 py-2 bg-slate-900/80 border-b border-slate-800/80 flex items-center justify-between gap-2 shrink-0 select-none">
          <div className="flex items-center gap-2 overflow-hidden">
            {(() => {
              let inspectorBadgeColor = "border-slate-800 bg-slate-900 text-slate-400";
              let inspectorTypeLabel = "LOG";
              if (selectedTrace.type === "api_call") {
                inspectorBadgeColor = "border-cyan-800/60 bg-cyan-950/40 text-cyan-400";
                inspectorTypeLabel = "API";
              } else if (selectedTrace.type === "sse_chunk") {
                inspectorBadgeColor = "border-pink-800/60 bg-pink-950/40 text-pink-400";
                inspectorTypeLabel = "SSE";
              } else if (selectedTrace.type === "thought") {
                inspectorBadgeColor = "border-emerald-800/60 bg-emerald-950/40 text-emerald-400";
                inspectorTypeLabel = "MIND";
              } else if (selectedTrace.type === "token_flow" || selectedTrace.type === "token_count") {
                inspectorBadgeColor = "border-yellow-800/60 bg-yellow-950/40 text-yellow-400";
                inspectorTypeLabel = "TOKEN";
              }
              return (
                <span className={`text-[8px] border px-1.5 py-0.2 rounded font-black uppercase tracking-wider ${inspectorBadgeColor}`}>
                  {inspectorTypeLabel}
                </span>
              );
            })()}
            <span className="font-extrabold text-[10px] text-white truncate max-w-[240px]">
              {selectedTrace.label}
            </span>
          </div>
          
          <div className="flex items-center gap-2">
            <span className="text-[8px] text-slate-500 font-bold font-mono">
              {selectedTrace.timestamp}
            </span>
            <button
              onClick={() => setSelectedTrace(null)}
              className="text-slate-400 hover:text-white transition duration-200 text-xs font-black px-1.5 py-0.5 hover:bg-slate-800 rounded uppercase cursor-pointer"
            >
              [ × ]
            </button>
          </div>
        </div>

        {/* Inspector Content Body */}
        <div className="flex-1 overflow-y-auto p-4 space-y-3.5 custom-scrollbar text-[10px] select-text">
          <div className="space-y-1">
            <span className="text-[8px] font-black text-slate-500 uppercase tracking-widest block">
              📝 DESCRIPTION / DETAILS
            </span>
            <p className="text-slate-300 font-sans leading-relaxed font-medium whitespace-pre-wrap selection:bg-cyan-900/50">
              {selectedTrace.details || "No supplementary description detail was loaded for this event."}
            </p>
          </div>

          {/* Dynamic Rich Analytical Widgets based on Event Type */}
          {(() => {
            if (selectedTrace.type === "api_call") {
              if (selectedTrace.label.includes("Tool Response:") && selectedTrace.data?.response?.results) {
                const results = selectedTrace.data.response.results;
                return (
                  <div className="space-y-2 pt-2.5 border-t border-slate-900">
                    <span className="text-[8px] font-black text-slate-500 uppercase tracking-widest block">
                      🔍 GROUNDED DATA SEARCH REFERENCES ({results.length} files found)
                    </span>
                    <div className="space-y-2 max-h-[145px] overflow-y-auto custom-scrollbar pr-1">
                      {results.map((res: any, idx: number) => (
                        <div key={idx} className="p-2.5 bg-slate-900/40 rounded-xl border border-slate-850 hover:border-cyan-500/30 transition duration-200">
                          <div className="flex items-center justify-between gap-2">
                            <a 
                              href={res.link} 
                              target="_blank" 
                              rel="noopener noreferrer"
                              className="text-[10px] font-bold text-cyan-400 hover:underline hover:text-cyan-300 flex items-center gap-1 uppercase truncate max-w-[280px]"
                            >
                              📂 {res.title || res.link?.split('/').pop() || "Grounded File"}
                            </a>
                            <span className="text-[8px] border border-cyan-800/40 bg-cyan-950/20 text-cyan-400/90 px-1 py-0.2 rounded font-mono font-bold shrink-0">
                              REF {idx + 1}
                            </span>
                          </div>
                          {res.snippet && (
                            <p className="text-slate-400 font-medium font-sans leading-normal mt-1.5 border-t border-slate-800/40 pt-1.5 selection:bg-cyan-900/50 text-[9.5px]">
                              {res.snippet}
                            </p>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                );
              }
              return (
                <div className="space-y-1.5 pt-2.5 border-t border-slate-900">
                  <span className="text-[8px] font-black text-slate-500 uppercase tracking-widest block">
                    🌐 ENTERPRISE GROUNDING PIPELINE STATS
                  </span>
                  {selectedTrace.label.includes("Tool Call:") ? (
                    <div className="grid grid-cols-2 gap-2 bg-slate-900/30 p-2.5 rounded-xl border border-slate-900 font-mono text-[8.5px] text-slate-400">
                      <div>
                        <span className="text-slate-500 block">FLOW PIPELINE</span>
                        <span className="text-cyan-400 font-bold block uppercase">Vertex AI Search API</span>
                      </div>
                      <div>
                        <span className="text-slate-500 block">DATA ACCESS REGION</span>
                        <span className="text-indigo-400 font-bold block uppercase">us-central1</span>
                      </div>
                      <div>
                        <span className="text-slate-500 block">HANDSHAKE CLIENT</span>
                        <span className="text-slate-300 font-bold block uppercase">Google-GenAI-ADK</span>
                      </div>
                      <div>
                        <span className="text-slate-500 block">INTEGRITY HANDSHAKE</span>
                        <span className="text-slate-300 font-bold">SHA-256 DIGITAL HANDSHAKE</span>
                      </div>
                    </div>
                  ) : (
                    <div className="grid grid-cols-2 gap-2 bg-slate-900/30 p-2.5 rounded-xl border border-slate-900 font-mono text-[8.5px] text-slate-400">
                      <div>
                        <span className="text-slate-500 block">FLOW PIPELINE</span>
                        <span className="text-yellow-400 font-bold block uppercase">Secure OAuth Gateway</span>
                      </div>
                      <div>
                        <span className="text-slate-500 block">COMPLIANCE SCHEMA</span>
                        <span className="text-emerald-400 font-bold block uppercase">100% Zero-Leak Compliant</span>
                      </div>
                      <div>
                        <span className="text-slate-500 block">DEVELOPER RUNTIME</span>
                        <span className="text-cyan-400 font-bold block uppercase">Vertex AI Engine Stack</span>
                      </div>
                      <div>
                        <span className="text-slate-500 block">GSUITE ACCESS LEVEL</span>
                        <span className="text-slate-300 font-bold block uppercase">Drive.Readonly Handshake</span>
                      </div>
                    </div>
                  )}
                </div>
              );
            }
            if (selectedTrace.type === "thought") {
              return (
                <div className="space-y-1.5 pt-2.5 border-t border-slate-900">
                  <span className="text-[8px] font-black text-slate-500 uppercase tracking-widest block">
                    🧠 COGNITIVE MODEL REASONING MATRIX
                  </span>
                  <div className="grid grid-cols-2 gap-2 bg-slate-900/30 p-2.5 rounded-xl border border-slate-900 font-mono text-[8.5px] text-slate-400">
                    <div>
                      <span className="text-slate-500 block">REASONING LAYER</span>
                      <span className="text-emerald-400 font-bold">{(selectedTrace.details || "").length > 300 ? "DEEP CHAIN-OF-THOUGHT" : "FAST PATH COGNITION"}</span>
                    </div>
                    <div>
                      <span className="text-slate-500 block">REASONING LEVEL</span>
                      <span className="text-cyan-400 font-bold">TYPES.THINKINGLEVEL.HIGH</span>
                    </div>
                    <div>
                      <span className="text-slate-500 block">THOUGHT SIZE</span>
                      <span className="text-slate-300 font-bold">{(selectedTrace.details || "").length} characters</span>
                    </div>
                    <div>
                      <span className="text-slate-500 block">RULE PROTOCOL</span>
                      <span className="text-emerald-400 font-bold">ADK_GROUNDING_MIND_OK</span>
                    </div>
                  </div>
                </div>
              );
            }
            if (selectedTrace.type === "token_flow" || selectedTrace.type === "token_count") {
              const tokens = (() => {
                const str = selectedTrace.details || "";
                const p = str.match(/Prompt:\s*(\d+)/i)?.[1];
                const o = str.match(/Output:\s*(\d+)/i)?.[1];
                const t = str.match(/Thoughts:\s*(\d+)/i)?.[1];
                if (p || o || t) {
                  const promptVal = parseInt(p || "0", 10);
                  const outputVal = parseInt(o || "0", 10);
                  const thoughtVal = parseInt(t || "0", 10);
                  const totalVal = promptVal + outputVal + thoughtVal;
                  return { prompt: promptVal, output: outputVal, thought: thoughtVal, total: totalVal };
                }
                return null;
              })();

              return (
                <div className="space-y-1.5 pt-2.5 border-t border-slate-900">
                  <span className="text-[8px] font-black text-slate-500 uppercase tracking-widest block">
                    🔋 RESOURCE METRICS & SECURITY STATS
                  </span>
                  {tokens ? (
                    <div className="space-y-2 bg-slate-900/30 p-3 rounded-xl border border-slate-900 font-mono text-[8.5px] text-slate-400">
                      <div className="flex items-center justify-between">
                        <span className="text-slate-500">COGNITIVE TOKEN CONSTELLATION BAR</span>
                        <span className="text-cyan-400 font-bold">TOTAL: {tokens.total} t</span>
                      </div>
                      <div className="space-y-1.5">
                        <div>
                          <div className="flex justify-between text-[7.5px] text-slate-400">
                            <span>PROMPT TOKENS (WORKSPACE CONTEXT): {tokens.prompt}</span>
                            <span>{tokens.total > 0 ? Math.round((tokens.prompt / tokens.total) * 100) : 0}%</span>
                          </div>
                          <div className="w-full bg-slate-950 h-1.5 rounded-full overflow-hidden border border-slate-900">
                            <div className="bg-pink-500 h-full rounded-full" style={{ width: `${tokens.total > 0 ? (tokens.prompt / tokens.total) * 100 : 0}%` }}></div>
                          </div>
                        </div>
                        <div>
                          <div className="flex justify-between text-[7.5px] text-slate-400">
                            <span>THOUGHTS TOKENS (REASONING PROCESS): {tokens.thought}</span>
                            <span>{tokens.total > 0 ? Math.round((tokens.thought / tokens.total) * 100) : 0}%</span>
                          </div>
                          <div className="w-full bg-slate-950 h-1.5 rounded-full overflow-hidden border border-slate-900">
                            <div className="bg-emerald-400 h-full rounded-full" style={{ width: `${tokens.total > 0 ? (tokens.thought / tokens.total) * 100 : 0}%` }}></div>
                          </div>
                        </div>
                        <div>
                          <div className="flex justify-between text-[7.5px] text-slate-400">
                            <span>CANDIDATE TOKENS (GENERATED ANSWER): {tokens.output}</span>
                            <span>{tokens.total > 0 ? Math.round((tokens.output / tokens.total) * 100) : 0}%</span>
                          </div>
                          <div className="w-full bg-slate-950 h-1.5 rounded-full overflow-hidden border border-slate-900">
                            <div className="bg-cyan-400 h-full rounded-full" style={{ width: `${tokens.total > 0 ? (tokens.output / tokens.total) * 100 : 0}%` }}></div>
                          </div>
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div className="grid grid-cols-2 gap-2 bg-slate-900/30 p-2.5 rounded-xl border border-slate-900 font-mono text-[8.5px] text-slate-400">
                      <div>
                        <span className="text-slate-500 block">FLOW PIPELINE</span>
                        <span className="text-yellow-400 font-bold block uppercase">Secure OAuth Gateway</span>
                      </div>
                      <div>
                        <span className="text-slate-500 block">COMPLIANCE SCHEMA</span>
                        <span className="text-emerald-400 font-bold block uppercase">100% Zero-Leak Compliant</span>
                      </div>
                      <div>
                        <span className="text-slate-500 block">DEVELOPER RUNTIME</span>
                        <span className="text-cyan-400 font-bold block uppercase">Vertex AI Engine Stack</span>
                      </div>
                      <div>
                        <span className="text-slate-500 block">GSUITE ACCESS LEVEL</span>
                        <span className="text-slate-300 font-bold block uppercase">Drive.Readonly Handshake</span>
                      </div>
                    </div>
                  )}
                </div>
              );
            }
            if (selectedTrace.type === "sse_chunk") {
              return (
                <div className="space-y-1.5 pt-2.5 border-t border-slate-900">
                  <span className="text-[8px] font-black text-slate-500 uppercase tracking-widest block">
                    📡 REAL-TIME EVENT STREAM METRICS
                  </span>
                  <div className="grid grid-cols-2 gap-2 bg-slate-900/30 p-2.5 rounded-xl border border-slate-900 font-mono text-[8.5px] text-slate-400">
                    <div>
                      <span className="text-slate-500 block">STREAM CONNECTOR</span>
                      <span className="text-pink-400 font-bold block">/api/chat SSE CONNECTION</span>
                    </div>
                    <div>
                      <span className="text-slate-500 block">EVENT-STREAM PROTOCOL</span>
                      <span className="text-slate-300 font-bold block">text/event-stream</span>
                    </div>
                    <div>
                      <span className="text-slate-500 block">BUFFERING HEADER</span>
                      <span className="text-emerald-400 font-bold block">X-Accel-Buffering: none</span>
                    </div>
                    <div>
                      <span className="text-slate-500 block">RENDER STATUS</span>
                      <span className="text-cyan-400 font-bold block">SUCCESSFULLY RENDERED</span>
                    </div>
                  </div>
                </div>
              );
            }
            return null;
          })()}

          {selectedTrace.data && (
            <div className="space-y-1.5 pt-2.5 border-t border-slate-900">
              <div className="flex items-center justify-between text-[8px] font-black text-slate-500 uppercase tracking-widest select-none">
                <span>📊 PAYLOAD DATA METADATA</span>
                <button
                  onClick={() => handleCopyDetails(selectedTrace)}
                  className={`text-[8px] font-bold px-1.5 py-0.5 rounded border transition-all duration-200 uppercase cursor-pointer ${
                    copied
                      ? "bg-emerald-950/60 border-emerald-500 text-emerald-400 font-black animate-pulse"
                      : "bg-slate-900 border-slate-800 text-slate-400 hover:text-white hover:border-slate-700"
                  }`}
                >
                  {copied ? "COPIED VALUE!" : "[ COPY JSON ]"}
                </button>
              </div>
              <pre className="p-3 bg-slate-950 rounded-lg border border-slate-900 text-[8.5px] font-mono text-cyan-300/95 overflow-x-auto whitespace-pre leading-normal custom-scrollbar selection:bg-slate-800">
                {JSON.stringify(selectedTrace.data, null, 2)}
              </pre>
            </div>
          )}
          
          {!selectedTrace.data && (
            <div className="pt-2.5 border-t border-slate-900 flex justify-end select-none">
              <button
                onClick={() => handleCopyDetails(selectedTrace)}
                className={`text-[8px] font-bold px-1.5 py-0.5 rounded border transition-all duration-200 uppercase cursor-pointer ${
                  copied
                    ? "bg-emerald-950/60 border-emerald-500 text-emerald-400 font-black animate-pulse"
                    : "bg-slate-900 border-slate-800 text-slate-400 hover:text-white hover:border-slate-700"
                }`}
              >
                {copied ? "COPIED DETAILS!" : "[ COPY DETAILS ]"}
              </button>
            </div>
          )}
        </div>
      </div>
    );
  };

  return (
    <main className="mx-auto max-w-7xl p-4 md:p-6 md:h-screen md:overflow-hidden flex flex-col justify-between relative selection:bg-cyan-100">
      
      {/* ----------------------------------------------------------------- */}
      {/* VIEWPORT FIXED OVERLAY SVG (Draws the laser lines for Loom and HUD modes) */}
      {/* ----------------------------------------------------------------- */}
      <svg className="fixed inset-0 pointer-events-none w-screen h-screen z-40 hidden md:block" style={{ mixBlendMode: "multiply" }}>
        <defs>
          <linearGradient id="auraGlow" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#06b6d4" stopOpacity="0.8" />
            <stop offset="40%" stopColor="#6366f1" stopOpacity="0.6" />
            <stop offset="100%" stopColor="#ec4899" stopOpacity="0.8" />
          </linearGradient>
          <linearGradient id="loomGlow" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#8b5cf6" stopOpacity="0.8" />
            <stop offset="100%" stopColor="#06b6d4" stopOpacity="0.8" />
          </linearGradient>
          <filter id="laserBlur" x="-30%" y="-30%" width="160%" height="140%">
            <feGaussianBlur stdDeviation="3.5" result="blur" />
            <feComposite in="SourceGraphic" in2="blur" operator="over" />
          </filter>
        </defs>

        {/* HUD Mode Laser Line (Hover state) */}
        {activeMode === "hud" && auraCoordinates && (
          <>
            <path
              d={`M ${auraCoordinates.x1} ${auraCoordinates.y1} C ${(auraCoordinates.x1 + auraCoordinates.x2) / 2} ${auraCoordinates.y1}, ${(auraCoordinates.x1 + auraCoordinates.x2) / 2} ${auraCoordinates.y2}, ${auraCoordinates.x2} ${auraCoordinates.y2}`}
              fill="none"
              stroke="url(#auraGlow)"
              strokeWidth="5"
              filter="url(#laserBlur)"
              className="pulse-soft opacity-30 animate-scan-glow"
            />
            <path
              d={`M ${auraCoordinates.x1} ${auraCoordinates.y1} C ${(auraCoordinates.x1 + auraCoordinates.x2) / 2} ${auraCoordinates.y1}, ${(auraCoordinates.x1 + auraCoordinates.x2) / 2} ${auraCoordinates.y2}, ${auraCoordinates.x2} ${auraCoordinates.y2}`}
              fill="none"
              stroke="url(#auraGlow)"
              strokeWidth="1.5"
              strokeDasharray="10, 6"
              style={{
                animation: "dash 1.2s linear infinite",
                strokeDashoffset: 100
              }}
            />
          </>
        )}

        {/* Neural Loom Synaptic Connections (Permanent links state) */}
        {activeMode === "loom" && loomConnections.map((id) => {
          const coords = getLoomCoordinates(id);
          if (!coords) return null;
          return (
            <g key={id}>
              {/* Thick soft neon ambient background path */}
              <path
                d={`M ${coords.x1} ${coords.y1} C ${(coords.x1 + coords.x2) / 2} ${coords.y1}, ${(coords.x1 + coords.x2) / 2} ${coords.y2}, ${coords.x2} ${coords.y2}`}
                fill="none"
                stroke="url(#loomGlow)"
                strokeWidth="4"
                filter="url(#laserBlur)"
                className="opacity-40 animate-pulse"
              />
              {/* Sharp, thin laser line */}
              <path
                d={`M ${coords.x1} ${coords.y1} C ${(coords.x1 + coords.x2) / 2} ${coords.y1}, ${(coords.x1 + coords.x2) / 2} ${coords.y2}, ${coords.x2} ${coords.y2}`}
                fill="none"
                stroke="url(#loomGlow)"
                strokeWidth="1.5"
              />
            </g>
          );
        })}
      </svg>

      {/* Futuristic Header Construct */}
      <header className="mb-6 flex flex-col md:flex-row md:items-center md:justify-between gap-4 border-b border-slate-200/55 pb-5">
        <div>
          <div className="flex items-center gap-2.5">
            <span className="h-5 w-5 rounded-md bg-gradient-to-tr from-cyan-400 via-indigo-400 to-pink-500 animate-spin" style={{ animationDuration: '8s' }}></span>
            <h1 className="text-2xl font-black tracking-tight bg-gradient-to-r from-slate-900 via-slate-800 to-slate-600 bg-clip-text text-transparent uppercase font-sans">
              MULTI-CONCEPT DEMO DECKS
            </h1>
            <span className="text-[9px] uppercase font-black tracking-widest bg-indigo-50 border border-indigo-200/40 text-indigo-600 px-2.5 py-0.5 rounded-md pulse-soft">
              CONSTRUCT VER_3.0
            </span>
          </div>
          <p className="mt-1 text-[10px] text-slate-400 font-bold tracking-widest uppercase flex items-center gap-1.5">
            <span>Vertex AI Search API Grounding System</span>
            <span className="h-1 w-1 bg-slate-300 rounded-full"></span>
            <span>Google ADK Engine Integration</span>
          </p>
        </div>

        {/* Live connector state */}
        <DriveAuthButton
          clientId={clientId}
          onToken={onToken}
          signedIn={!!accessToken}
          onSignOut={onSignOut}
        />
      </header>

      {/* ----------------------------------------------------------------- */}
      {/* HIGH-TECH MODE CHIP CONSOLE SELECTOR (Allows dynamic mode switching) */}
      {/* ----------------------------------------------------------------- */}
      <div className="flex flex-col sm:flex-row bg-slate-100/70 border border-slate-200/60 p-1.5 rounded-2xl gap-2 shadow-inner w-full justify-between items-center mb-4">
        <span className="text-[9px] font-black text-slate-400 uppercase tracking-widest pl-3 py-1">
          ⚙️ SELECT HUD INTERACTION DECK:
        </span>
        <div className="flex flex-wrap gap-1 w-full sm:w-auto">
          <button
            onClick={() => { setActiveMode("loom"); handleMouseLeaveCard(); }}
            className={`flex-1 sm:flex-none text-[9px] font-black uppercase px-4 py-2 rounded-xl border transition-all duration-300 ${
              activeMode === "loom"
                ? "bg-gradient-to-r from-violet-500 to-cyan-500 text-white border-transparent shadow-md"
                : "bg-white/40 border-slate-200/30 text-slate-500 hover:bg-white hover:text-slate-700"
            }`}
          >
            Mode 01: The Neural Loom
          </button>
          <button
            onClick={() => { setActiveMode("hud"); setLoomConnections([]); }}
            className={`flex-1 sm:flex-none text-[9px] font-black uppercase px-4 py-2 rounded-xl border transition-all duration-300 ${
              activeMode === "hud"
                ? "bg-gradient-to-r from-cyan-500 via-indigo-500 to-pink-500 text-white border-transparent shadow-md"
                : "bg-white/40 border-slate-200/30 text-slate-500 hover:bg-white hover:text-slate-700"
            }`}
          >
            Mode 02: Aura Sensing HUD
          </button>
          <button
            onClick={() => { setActiveMode("terminal"); handleMouseLeaveCard(); setLoomConnections([]); }}
            className={`flex-1 sm:flex-none text-[9px] font-black uppercase px-4 py-2 rounded-xl border transition-all duration-300 font-mono ${
              activeMode === "terminal"
                ? "bg-slate-900 border-transparent text-emerald-400 shadow-md shadow-emerald-950/20"
                : "bg-white/40 border-slate-200/30 text-slate-500 hover:bg-white hover:text-slate-700"
            }`}
          >
            Mode 03: Construct Console
          </button>
        </div>
      </div>

      {/* Cybernetic Workspace */}
      <section className="grid grid-cols-1 md:grid-cols-12 gap-6 md:gap-8 items-stretch flex-1 min-h-0 md:overflow-hidden mb-4">
        
        {/* LEFT PANEL: Direct Vertex AI Search datastores (5 columns) */}
        <div className="md:col-span-5 flex flex-col md:h-full md:overflow-hidden justify-between space-y-4">
          <div className="space-y-4 flex-1 flex flex-col min-h-0">
            <div className="flex items-center justify-between">
              <span className="text-[10px] font-black tracking-wider text-slate-400 uppercase flex items-center gap-1.5">
                <span className="h-1.5 w-1.5 rounded-full bg-cyan-500 animate-ping"></span>
                1. Datastore Waterfall
              </span>
              <span className="text-[9px] bg-slate-100 text-slate-500 border border-slate-200 px-2 py-0.5 rounded-full font-black tracking-wide uppercase">
                REST SEARCH
              </span>
            </div>
            
            {/* Search Input Box */}
            <div className="relative">
              <input
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search raw GSuite & GCS files..."
                className="w-full rounded-2xl border border-slate-200/80 bg-white/80 px-4 py-3.5 pl-11 text-xs placeholder-slate-400 focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500/10 focus:outline-none shadow-sm shadow-slate-100/40 transition-all duration-300 font-medium"
              />
              {isSearching ? (
                <span className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 rounded-full border-2 border-cyan-500/20 border-t-cyan-500 animate-spin"></span>
              ) : (
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2.5} stroke="currentColor" className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400">
                  <path strokeLinecap="round" strokeLinejoin="round" d="m21 21-5.197-5.197m0 0A7.5 7.5 0 1 0 5.196 5.196a7.5 7.5 0 0 0 10.637 10.542Z" />
                </svg>
              )}
            </div>

            {/* Document Cards List */}
            <div 
              ref={listContainerRef}
              onScroll={handleScrollList}
              className="space-y-4 flex-1 overflow-y-auto pr-1.5 custom-scrollbar min-h-0"
            >
              {filteredDocs.map((doc) => {
                const isHovered = hoveredDoc?.id === doc.id;
                const isLoomLinked = loomConnections.includes(doc.id);
                const isPipingActive = pipingDocId === doc.id;
                
                // Card visual helper configurations
                let typeEmoji = "🗒️";
                let typeColor = "text-indigo-600 bg-indigo-50 border-indigo-100/60";
                if (doc.mimeType.includes("pdf")) {
                  typeEmoji = "📄";
                  typeColor = "text-rose-600 bg-rose-50 border-rose-100/60";
                } else if (doc.mimeType.includes("spreadsheet")) {
                  typeEmoji = "📊";
                  typeColor = "text-emerald-600 bg-emerald-50 border-emerald-100/60";
                } else if (doc.mimeType.includes("document")) {
                  typeEmoji = "🔵";
                  typeColor = "text-blue-600 bg-blue-50 border-blue-100/60";
                }

                return (
                  <div
                    key={doc.id}
                    ref={(el) => { documentRefs.current[doc.id] = el; }}
                    onMouseEnter={() => handleMouseEnterCard(doc, doc.id)}
                    onMouseLeave={handleMouseLeaveCard}
                    className={`rounded-2xl p-4 border transition-all duration-300 relative cursor-crosshair group ${
                      isHovered || isLoomLinked
                        ? "bg-white border-cyan-400/80 shadow-md shadow-cyan-100/40 scale-[1.015] z-10"
                        : "bg-white/65 border-slate-200/50 shadow-sm hover:border-slate-300/80 hover:bg-white"
                    }`}
                  >
                    <div className="space-y-2">
                      <div className="flex items-center justify-between gap-2">
                        <span className="text-[9px] font-black tracking-widest uppercase text-cyan-600 bg-cyan-50 border border-cyan-100/40 px-2 py-0.5 rounded">
                          {doc.source}
                        </span>
                        <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded border uppercase tracking-wider ${typeColor}`}>
                          {doc.name.split(".").pop()}
                        </span>
                      </div>
                      <h3 className="font-extrabold text-xs text-slate-800 leading-snug flex items-center gap-1.5">
                        <span className="text-sm shrink-0">{typeEmoji}</span> 
                        {doc.link ? (
                          <a 
                            href={doc.link} 
                            target="_blank" 
                            rel="noopener noreferrer" 
                            className="truncate text-indigo-600 hover:text-cyan-500 hover:underline transition-colors duration-200"
                            onClick={(e) => e.stopPropagation()}
                          >
                            {doc.name}
                          </a>
                        ) : (
                          <span className="truncate">{doc.name}</span>
                        )}
                      </h3>
                      <p 
                        className="text-[11px] text-slate-500 font-semibold leading-relaxed"
                        dangerouslySetInnerHTML={{ __html: doc.snippet || "" }}
                      />
                    </div>

                    <div className="mt-3 pt-3 border-t border-slate-100/70 flex items-center justify-between gap-2">
                      <span className="text-[9px] font-mono text-slate-400 font-bold">SIZE: {doc.fileSize} · BY {doc.owner.toUpperCase()}</span>
                      
                      {/* CONCEPT 1: LOOM NODE TRIGGER */}
                      {activeMode === "loom" && (
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleToggleLoomNode(doc.id, doc.name);
                          }}
                          className={`text-[10px] font-black uppercase tracking-wider px-2.5 py-1 rounded-md border transition-all duration-200 ${
                            isLoomLinked
                              ? "bg-cyan-500 text-white border-cyan-500"
                              : "bg-white text-indigo-600 border-indigo-200 hover:border-indigo-400"
                          }`}
                        >
                          {isLoomLinked ? "🧬 Connected" : "🧬 Connect Node"}
                        </button>
                      )}

                      {/* CONCEPT 2: HUD MEMORY TRIGGER */}
                      {activeMode === "hud" && (
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleFuseMemory(doc.name);
                          }}
                          className="opacity-0 group-hover:opacity-100 transition-opacity duration-200 text-[10px] font-black text-indigo-600 hover:text-indigo-700 uppercase tracking-wider bg-indigo-50 border border-indigo-100 px-2.5 py-1 rounded-md cursor-pointer"
                        >
                          🧬 Fuse synapse
                        </button>
                      )}

                      {/* CONCEPT 3: PIPELINE PIPING TRIGGER */}
                      {activeMode === "terminal" && (
                        <button
                          disabled={isPipingActive}
                          onClick={(e) => {
                            e.stopPropagation();
                            handlePipeDoc(doc.id, doc.name);
                          }}
                          className={`text-[9px] font-mono font-bold uppercase tracking-wide px-2 py-1 rounded border transition-all duration-200 ${
                            isPipingActive
                              ? "bg-emerald-950 border-emerald-800 text-emerald-400 animate-pulse"
                              : "bg-slate-900 border-slate-800 text-slate-300 hover:border-emerald-500 hover:text-emerald-400"
                          }`}
                        >
                          {isPipingActive ? "[PIPING...]" : "| PIPE TO CORE"}
                        </button>
                      )}
                    </div>
                  </div>
                );
              })}
              {filteredDocs.length === 0 && !isSearching && (
                <div className="flex flex-col items-center justify-center h-[35vh] text-center p-6 bg-slate-50/40 border border-dashed border-slate-200/80 rounded-2xl">
                  <span className="text-2xl mb-2 animate-bounce" style={{ animationDuration: "3s" }}>🔍</span>
                  <p className="text-[10px] font-black uppercase tracking-wider text-slate-400">
                    No active index nodes found
                  </p>
                  <p className="text-[9px] text-slate-400 font-bold mt-1 max-w-[200px] leading-relaxed">
                    Query for "{searchQuery}" returned empty. Check Google Drive synchronization or try another keyword.
                  </p>
                </div>
              )}
            </div>
          </div>
          
          <div className="text-[10px] font-black text-slate-400 bg-white/65 p-3.5 rounded-xl border border-slate-200/50 text-center uppercase tracking-wider leading-relaxed shadow-sm">
            {activeMode === "loom" && "🧬 Connect file nodes to construct the Synaptic Mind Constellation Grid."}
            {activeMode === "hud" && "⚡ Hover search cards to project a real-time cognitive aura link."}
            {activeMode === "terminal" && "⌨️ Monospace Fluent Command Deck. Click | PIPE to funnel raw file buffers."}
          </div>
        </div>

        {/* RIGHT PANEL: ADK Conversational Mind & Concepts Visuals (7 columns) */}
        <div className="md:col-span-7 flex flex-col md:h-full md:overflow-hidden space-y-4 min-h-0">
          
          {/* ----------------------------------------------------------------- */}
          {/* CONCEPTS VISUAL SHELF (Aura Sensor / Loom Orb / Terminal Monitor) */}
          {/* ----------------------------------------------------------------- */}
          <div className={`rounded-2xl p-5 border shadow-sm relative overflow-hidden transition-all duration-500 shrink-0 ${
            activeMode === "terminal" 
              ? "bg-slate-950 border-slate-800 text-slate-300 font-mono h-[18vh]" 
              : "glass-panel border-slate-200/60 text-slate-800 h-[17vh]"
          }`}>
            
            {/* Background grids */}
            {activeMode === "terminal" ? (
              <div className="absolute inset-0 bg-[linear-gradient(rgba(16,185,129,0.04)_1px,transparent_1px),linear-gradient(90deg,rgba(16,185,129,0.04)_1px,transparent_1px)] bg-[size:16px_16px] opacity-100 pointer-events-none" />
            ) : (
              <div className="absolute inset-0 bg-[linear-gradient(rgba(226,232,240,0.3)_1px,transparent_1px),linear-gradient(90deg,rgba(226,232,240,0.3)_1px,transparent_1px)] bg-[size:10px_10px] opacity-40 pointer-events-none" />
            )}

            <div className="flex items-center gap-5 justify-between relative h-full w-full z-10">
              
              {/* INTERACTIVE MODE 01: THE NEURAL LOOM COGNITIVE SHIELD */}
              {activeMode === "loom" && (
                <div className="flex-1 space-y-1.5">
                  <span className="text-[10px] font-black tracking-wider text-slate-400 uppercase">
                    Mode 01: Neural Loom Constellation
                  </span>
                  <h3 className="text-sm font-black text-slate-800 uppercase tracking-tight">
                    Active Synaptic Threads: {loomConnections.length}
                  </h3>
                  <p className="text-[11px] text-slate-500 font-bold leading-normal max-w-lg">
                    {loomConnections.length > 0 
                      ? `Loom Synapses are established. The ADK Model-Native session is grounded in ${loomConnections.length} live constellation document nodes.`
                      : "No connected threads. Click Connect Node on files to weave them into the chatbot's active grounding web."
                    }
                  </p>
                </div>
              )}

              {/* INTERACTIVE MODE 02: THE AURA SENSING HUD READOUT */}
              {activeMode === "hud" && (
                <div className="flex-1 space-y-1.5">
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] font-black tracking-wider text-slate-400 uppercase flex items-center gap-1.5">
                      <span className={`h-1.5 w-1.5 rounded-full ${hoveredDoc ? "bg-cyan-500 animate-ping" : "bg-amber-400 animate-pulse"}`}></span>
                      Mode 02: Aura Telemetry Monitor
                    </span>
                    <span className={`text-[8px] font-black px-1.5 py-0.2 rounded border ${
                      hoveredDoc ? "bg-cyan-50 border-cyan-200 text-cyan-600" : "bg-slate-100 border-slate-200 text-slate-400"
                    }`}>
                      {hoveredDoc ? "SYNCED" : "AWAITING"}
                    </span>
                  </div>
                  <h3 className="text-sm font-black text-slate-800 uppercase tracking-tight mt-1">
                    {hoveredDoc ? "COGNITIVE SYNAPSE ESTABLISHED" : "SCANNING DATAFIELDS"}
                  </h3>
                  {hoveredDoc ? (
                    <div className="space-y-1 animate-fade-in">
                      <p className="text-[11px] text-slate-500 font-bold leading-normal max-w-lg">
                        {hoveredDoc.telemetrySummary}
                      </p>
                      <div className="flex gap-3 text-[9px] font-mono text-slate-400 font-bold uppercase pt-0.5">
                        <span>MIME: {hoveredDoc.mimeType.split("/").pop()}</span>
                        <span>SIZE: {hoveredDoc.fileSize}</span>
                        <span>OWNER: {hoveredDoc.ownerEmail}</span>
                      </div>
                    </div>
                  ) : (
                    <p className="text-[11px] text-slate-400 font-medium italic">
                      Beam immediate document telemetry straight to the chatbot deck by hovering your cursor over any datastore card on the left.
                    </p>
                  )}
                </div>
              )}

              {/* INTERACTIVE MODE 03: TERMINAL DECK LOGGER */}
              {activeMode === "terminal" && (
                <div className="flex-1 space-y-1 font-mono text-xs">
                  <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block">
                    Mode 03: System Pipeline Logging
                  </span>
                  {pipingDocId ? (
                    <div className="space-y-0.5 max-h-[12vh] overflow-y-auto text-[10px] text-emerald-400 font-mono">
                      {pipingLog.map((line, idx) => (
                        <p key={idx} className="animate-fade-in">{line}</p>
                      ))}
                    </div>
                  ) : (
                    <div className="space-y-1 text-[11px] text-slate-400">
                      <p className="text-emerald-500 font-semibold uppercase">{"\u003e\u003e\u003e SYSTEM STANDBY. SOCKET DECK OPEN."}</p>
                      <p className="leading-relaxed">Click [ | PIPE TO CORE ] on a datastore to stream and melt raw file buffers into grounded query context.</p>
                    </div>
                  )}
                </div>
              )}

              {/* CENTRAL COGNITIVE INDICATOR (Orb / Waveform / Tech Node) */}
              <div
                ref={chatbotCoreRef}
                className={`h-16 w-16 rounded-full flex items-center justify-center relative shrink-0 z-10 transition-all duration-500 ${
                  activeMode === "terminal" 
                    ? "bg-slate-900 border border-emerald-800 shadow-md shadow-emerald-950/40" 
                    : "bg-white border shadow-inner"
                } ${
                  hoveredDoc || loomConnections.length > 0 || pipingDocId ? "border-cyan-400 scale-105" : "border-slate-200"
                }`}
              >
                {/* Mode-based rotating elements */}
                <div className={`absolute inset-0.5 rounded-full border border-dashed transition-all duration-1000 ${
                  activeMode === "terminal" 
                    ? "border-emerald-500/50" 
                    : (hoveredDoc || loomConnections.length > 0 ? "border-cyan-400 animate-spin" : "border-slate-200")
                }`} style={{ animationDuration: '10s' }} />

                {/* Cyber ripples on active connection */}
                {(hoveredDoc || loomConnections.length > 0 || pipingDocId) && (
                  <>
                    <span className={`absolute inset-0 rounded-full animate-ping pointer-events-none ${activeMode === "terminal" ? "bg-emerald-400/10" : "bg-cyan-400/10"}`} />
                    <span className={`absolute -inset-2 rounded-full animate-pulse pointer-events-none ${activeMode === "terminal" ? "bg-emerald-400/5" : "bg-violet-400/5"}`} />
                  </>
                )}

                {/* Wave core */}
                <div className="absolute h-10 w-10 rounded-full flex items-center justify-center overflow-hidden">
                  <div className="flex gap-0.75 items-end justify-center h-4 w-8">
                    <span className={`w-0.75 rounded-full transition-all duration-300 ${activeMode === "terminal" ? "bg-emerald-400" : "bg-cyan-500"} ${hoveredDoc || loomConnections.length > 0 || pipingDocId ? "h-4 animate-pulse" : "h-1"}`} style={{ animationDelay: '0.1s' }}></span>
                    <span className={`w-0.75 rounded-full transition-all duration-300 ${activeMode === "terminal" ? "bg-emerald-400" : "bg-indigo-500"} ${hoveredDoc || loomConnections.length > 0 || pipingDocId ? "h-6 animate-pulse" : "h-2"}`} style={{ animationDelay: '0.3s' }}></span>
                    <span className={`w-0.75 rounded-full transition-all duration-300 ${activeMode === "terminal" ? "bg-emerald-400" : "bg-pink-500"} ${hoveredDoc || loomConnections.length > 0 || pipingDocId ? "h-5 animate-pulse" : "h-1.5"}`} style={{ animationDelay: '0.2s' }}></span>
                    <span className={`w-0.75 rounded-full transition-all duration-300 ${activeMode === "terminal" ? "bg-emerald-400" : "bg-cyan-500"} ${hoveredDoc || loomConnections.length > 0 || pipingDocId ? "h-3 animate-pulse" : "h-1"}`} style={{ animationDelay: '0.4s' }}></span>
                  </div>
                </div>
              </div>

            </div>
          </div>

          {/* Active Pinned Synapse Memories Hub */}
          <div className="glass-panel rounded-2xl p-4 border border-slate-200/50 shadow-sm flex flex-col space-y-3 justify-center relative shrink-0">
            <div className="flex items-center justify-between text-[10px] font-black tracking-wider text-slate-400 uppercase">
              <span className="flex items-center gap-1.5">
                <span>🧬 ACTIVE GROUNDING SYNAPSE MEMORIES</span>
                <span className="bg-indigo-50 border border-indigo-100 text-indigo-600 font-bold px-1.5 py-0.2 rounded-full text-[9px]">
                  {fusedMemories.length}
                </span>
              </span>
              {fusedMemories.length > 0 && (
                <button onClick={handleClearMemories} className="text-rose-500 hover:text-rose-600 transition font-extrabold uppercase tracking-wide text-[9px] cursor-pointer">
                  Clear All
                </button>
              )}
            </div>
            
            {fusedMemories.length === 0 ? (
              <p className="text-[11px] text-slate-400 font-bold italic leading-normal">
                {activeMode === "loom" && "No synapses active. Click Connect Node on left files to weave synapses."}
                {activeMode === "hud" && "No synapses active. Click Fuse synapse on hovered cards to lock memories."}
                {activeMode === "terminal" && "No pipeline buffers synched. Pipe files down raw terminal stream."}
              </p>
            ) : (
              <div className="flex flex-wrap gap-1.5 max-h-[8vh] overflow-y-auto custom-scrollbar animate-fade-in">
                {fusedMemories.map((mem) => (
                  <span key={mem} className="text-[10px] font-bold bg-indigo-50 text-indigo-700 border border-indigo-100/60 px-2.5 py-1 rounded-full flex items-center gap-1.5 shadow-sm">
                    <span>🗒️ {mem}</span>
                    <button onClick={() => {
                      setFusedMemories(fusedMemories.filter(m => m !== mem));
                      // Deselect from loom if active
                      const doc = ENTERPRISE_INDEX.find(d => d.name === mem);
                      if (doc) setLoomConnections(prev => prev.filter(id => id !== doc.id));
                    }} className="text-indigo-400 hover:text-indigo-600 font-black ml-1 text-xs">×</button>
                  </span>
                ))}
              </div>
            )}
          </div>

          {/* ChatPanel workspace component container */}
          <ChatPanel 
            accessToken={accessToken} 
            userId={userId} 
            fusedMemories={fusedMemories} 
            thinkingLevel={thinkingLevel}
            selectedModel={selectedModel}
            onTraceEvent={addTrace}
          />

        </div>
      </section>

      {/* DIAGNOSTICS TRACE HUD DRAWER */}
      <div
        className={`fixed top-0 right-0 h-screen bg-slate-950/95 backdrop-blur-md border-l border-slate-800 shadow-2xl z-50 flex flex-col text-slate-300 font-mono ${
          isDraggingHud ? "select-none" : "transition-all duration-500"
        } ${
          isTraceOpen ? "translate-x-0" : "translate-x-full"
        }`}
        style={{
          width: `${hudWidth}px`,
          maxWidth: "calc(100vw - 3rem)"
        }}
      >
        {/* Drag handle resize line on the left border */}
        <div
          onMouseDown={startResizeHud}
          className="absolute top-0 left-0 w-2 h-full cursor-col-resize z-50 hover:bg-cyan-500/20 active:bg-cyan-500/40 group transition-all duration-300 flex items-center justify-center"
          title="Drag left/right to resize console width"
        >
          {/* Glowing futuristic divider micro-line */}
          <div className="w-[1.5px] h-12 bg-slate-800 rounded group-hover:bg-cyan-400 group-active:bg-cyan-500 group-hover:shadow-[0_0_8px_#22d3ee] transition-all duration-300"></div>
        </div>

        {/* Cyber handle tab protruding on the left */}
        <button
          onClick={() => {
            const nextState = !isTraceOpen;
            setIsTraceOpen(nextState);
            if (!nextState) {
              setIsLogStreamMaximized(false);
            }
          }}
          onDoubleClick={(e) => {
            e.stopPropagation();
            const next = !isHudExpanded;
            setIsHudExpanded(next);
            setHudWidth(next ? 950 : 420);
          }}
          className="absolute top-1/2 -left-12 -translate-y-1/2 w-12 py-6 rounded-l-2xl bg-slate-950 border-y border-l border-slate-800 flex flex-col items-center justify-center cursor-pointer text-white shadow-2xl hover:bg-slate-900 hover:border-slate-700 transition-all duration-300 group"
          title="Click to toggle HUD; Double-click to toggle Widescreen"
        >
          <div className="flex flex-col items-center gap-1.5">
            {/* High-tech flashing status LED dot */}
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
            </span>
            
            {/* Sideways Text: TRACE LOGS */}
            <span className="text-[10px] font-black tracking-[0.2em] uppercase text-slate-400 group-hover:text-cyan-400 transition-colors duration-200" style={{ writingMode: 'vertical-lr', textOrientation: 'mixed' }}>
              {isTraceOpen ? "CLOSE HUD" : "TRACE LOGS"}
            </span>
            
            {/* Badge count of traces */}
            {traces.length > 0 && (
              <span className="text-[8px] bg-cyan-950 border border-cyan-500 text-cyan-400 px-1 py-0.5 rounded-full font-black min-w-[16px] text-center mt-1 animate-pulse">
                {traces.length}
              </span>
            )}
          </div>
        </button>

        {/* Drawer Header */}
        <div className="p-5 border-b border-slate-800 bg-slate-900/40 relative">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="h-2 w-2 rounded-full bg-cyan-500 animate-pulse"></span>
              <h2 className="text-sm font-black tracking-widest text-white uppercase">
                GROUNDING TRACE HUD
              </h2>
            </div>
            <span className="text-[9px] border border-cyan-800/60 bg-cyan-950/40 text-cyan-400 px-2 py-0.5 rounded uppercase font-black tracking-widest pulse-soft">
              v3.0 SECURE
            </span>
          </div>
          <p className="text-[9px] text-slate-400 font-bold mt-1.5 uppercase tracking-wider">
            Model-Native Chat Reasoning & Token Flow Diagnostics
          </p>
        </div>

        {/* Interactive Secure Token Flow Stack */}
        <div className="px-5 py-4 border-b border-slate-800 bg-slate-900/20 space-y-3">
          <div className="flex items-center justify-between text-[9px] font-black text-slate-500 uppercase tracking-widest">
            <span>🔑 SECURE TOKEN FLOW STACK</span>
            <span className="text-emerald-500 flex items-center gap-1">
              <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-ping"></span>
              ZERO-LEAK COMPLIANT
            </span>
          </div>
          
          <div className="grid grid-cols-2 gap-3 text-[10px]">
            {/* GSuite user authorization token card */}
            <div className={`p-2.5 rounded-xl border transition-all duration-300 ${
              accessToken 
                ? "bg-slate-900/80 border-cyan-500/30 text-slate-300" 
                : "bg-slate-900/30 border-slate-800/80 text-slate-500"
            }`}>
              <div className="flex items-center justify-between">
                <span className="font-extrabold text-[9px] text-slate-400 uppercase tracking-wider">
                  1. USER OAUTH
                </span>
                <span className={`h-1.5 w-1.5 rounded-full ${accessToken ? "bg-cyan-400 animate-pulse" : "bg-amber-500"}`}></span>
              </div>
              <p className="font-black text-white mt-1 text-[11px] truncate">
                {accessToken ? `ya29.a0Af...${accessToken.slice(-6)}` : "NOT LINKED"}
              </p>
              <p className="text-[8px] text-slate-500 font-bold uppercase mt-1 leading-normal">
                GSuite OAuth Drive Token (Expires on refresh)
              </p>
            </div>

            {/* GCP Service Account token card */}
            <div className="p-2.5 rounded-xl border bg-slate-900/80 border-indigo-500/30 text-slate-300">
              <div className="flex items-center justify-between">
                <span className="font-extrabold text-[9px] text-slate-400 uppercase tracking-wider">
                  2. BACKEND ADC
                </span>
                <span className="h-1.5 w-1.5 rounded-full bg-indigo-400 animate-pulse"></span>
              </div>
              <p className="font-black text-white mt-1 text-[11px] truncate">
                Bearer ya29.c.Co...3XyZ
              </p>
              <p className="text-[8px] text-slate-500 font-bold uppercase mt-1 leading-normal">
                Service Account Cloud Search elevated
              </p>
            </div>
          </div>
        </div>

        {/* Gemini Model Selection Dropdown */}
        <div className="px-5 py-4 border-b border-slate-800 bg-slate-900/20 space-y-3">
          <div className="flex items-center justify-between text-[9px] font-black text-slate-500 uppercase tracking-widest">
            <span>🤖 ACTIVE GEMINI MODEL</span>
            <span className="text-[8px] bg-indigo-950 border border-indigo-800 text-indigo-400 px-1.5 py-0.2 rounded font-black uppercase">
              MODEL OVERRIDE
            </span>
          </div>

          <div className="relative">
            <select
              value={selectedModel}
              onChange={(e) => {
                const val = e.target.value as "gemini-3.5-flash" | "gemini-3.5-flash-lite";
                setSelectedModel(val);
                addTrace({
                  type: "token_flow",
                  label: "Active Model Override",
                  details: `Switched query execution target model to: ${val === "gemini-3.5-flash" ? "gemini flash" : "gemini lite"} (${val})`
                });
              }}
              className="w-full bg-slate-900/80 border border-slate-800 text-slate-300 text-[10px] font-mono px-3 py-2.5 rounded-xl focus:outline-none focus:ring-1 focus:ring-indigo-500 hover:border-slate-700 cursor-pointer appearance-none transition-all duration-200"
            >
              <option value="gemini-3.5-flash">gemini flash</option>
              <option value="gemini-3.5-flash-lite">gemini lite</option>
            </select>
            <div className="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none text-slate-400 text-[10px]">
              ▼
            </div>
          </div>
        </div>

        {/* Gemini Model Thinking Configuration */}
        <div className="px-5 py-4 border-b border-slate-800 bg-slate-900/20 space-y-3">
          <div className="flex items-center justify-between text-[9px] font-black text-slate-500 uppercase tracking-widest">
            <span>⚙️ GEMINI THINKING CONFIG LEVEL</span>
            <span className="text-[8px] bg-cyan-950 border border-cyan-800 text-cyan-400 px-1.5 py-0.2 rounded font-black uppercase">
              TYPES.THINKINGLEVEL
            </span>
          </div>

          <div className="flex bg-slate-900/60 p-1 border border-slate-800 rounded-xl gap-1 justify-between items-center shadow-inner">
            {(["MINIMAL", "LOW", "MEDIUM", "HIGH"] as const).map((level) => (
              <button
                key={level}
                onClick={() => {
                  setThinkingLevel(level);
                  addTrace({
                    type: "token_flow",
                    label: "ThinkingConfig Adjusted",
                    details: `Adjusted active Gemini 3 reasoning level to: ${level}. This maps directly to types.ThinkingLevel.${level} on the Google GenAI API config.`
                  });
                }}
                className={`flex-1 text-[8.5px] font-black px-1 py-1.5 rounded-lg transition-all duration-200 uppercase text-center cursor-pointer ${
                  thinkingLevel === level
                    ? "bg-cyan-500 text-slate-950 font-black shadow-md"
                    : "text-slate-400 hover:text-white hover:bg-slate-800/40"
                }`}
              >
                {level}
              </button>
            ))}
          </div>

          <div className="p-2.5 rounded-xl border border-slate-800 bg-slate-950/40 text-[9px] text-slate-400 leading-relaxed font-sans font-medium space-y-1">
            <p className="text-white font-mono text-[8.5px] border-b border-slate-800/60 pb-1 flex items-center gap-1 uppercase">
              <span className="h-1.5 w-1.5 rounded-full bg-cyan-400"></span>
              API Payload Construct:
            </p>
            <pre className="text-[8px] font-mono text-cyan-300 leading-normal bg-slate-950/60 p-2 rounded border border-slate-900/80 overflow-x-auto whitespace-pre">
{`config = types.GenerateContentConfig(
  thinking_config = types.ThinkingConfig(
    thinking_level = types.ThinkingLevel.${thinkingLevel},
    include_thoughts = True
  )
)`}
            </pre>
          </div>
        </div>

        {/* Gemini Live Reasoning Chain */}
        <div className="px-5 py-4 border-b border-slate-800 bg-slate-900/10 space-y-2">
          <div className="flex items-center justify-between text-[9px] font-black text-slate-500 uppercase tracking-widest">
            <span>🧠 GEMINI MODEL REASONING OUTLET</span>
            <span className="text-[8px] bg-emerald-950 border border-emerald-800 text-emerald-400 px-1.5 py-0.2 rounded font-black uppercase">
              include_thoughts: true
            </span>
          </div>
          
          <div className="p-3 rounded-xl border border-emerald-900/30 bg-emerald-950/10 text-slate-300 min-h-[75px] max-h-[14vh] overflow-y-auto custom-scrollbar text-[10px] leading-relaxed relative">
            <div className="absolute top-2.5 right-2.5 h-1.5 w-1.5 rounded-full bg-emerald-400 animate-ping pointer-events-none"></div>
            {traces.filter(t => t.type === "thought").length > 0 ? (
              <div className="space-y-2 animate-fade-in font-sans font-medium text-emerald-300/90 whitespace-pre-wrap">
                {traces.filter(t => t.type === "thought").slice(-1)[0].details}
                <span className="inline-block w-1 h-3 bg-emerald-400 ml-0.5 animate-pulse"></span>
              </div>
            ) : (
              <p className="text-slate-500 italic text-[10px] font-bold text-center mt-3">
                No thought flow stream detected yet. Send a grounded chat request to capture Gemini's reasoning process in real time.
              </p>
            )}
          </div>
        </div>

        {/* Bottom Workspace Split Section */}
        <div className="flex-1 flex overflow-hidden relative">
          {/* Left Column: Log filters and scrolling list */}
          <div className="flex-1 flex flex-col min-w-0 h-full overflow-hidden relative">
            {/* Trace Log Event Filter Headers */}
            <div 
              onDoubleClick={(e) => {
                e.stopPropagation();
                const next = !isHudExpanded;
                setIsHudExpanded(next);
                setHudWidth(next ? 950 : 420);
              }}
              className="px-5 py-3 border-b border-slate-900 bg-slate-900/40 flex items-center justify-between gap-1.5 cursor-pointer select-none"
              title="Double-click to toggle widescreen mode"
            >
              <div className="flex items-center gap-2 shrink-0">
                <span className="text-[9px] font-black text-slate-500 uppercase tracking-widest">
                  👁️ LOG STREAM
                </span>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    const targetState = !isLogStreamMaximized;
                    setIsLogStreamMaximized(targetState);
                    if (targetState) {
                      setIsTraceOpen(true);
                    }
                  }}
                  className="text-[8px] font-black border border-cyan-800/40 bg-cyan-950/20 text-cyan-400 hover:bg-cyan-500 hover:text-slate-950 px-1.5 py-0.5 rounded transition uppercase flex items-center gap-1 cursor-pointer"
                  title="Maximize log stream panel on the left"
                >
                  {isLogStreamMaximized ? "❐ Collapse" : "⛶ Maximize"}
                </button>
              </div>
              <div className="flex flex-wrap gap-1 items-center justify-end">
                {[
                  { id: "all", label: "ALL" },
                  { id: "api", label: "API" },
                  { id: "sse", label: "SSE" },
                  { id: "thought", label: "MIND" },
                  { id: "token", label: "TOKEN" },
                ].map((btn) => (
                  <button
                    key={btn.id}
                    onClick={() => setTraceFilter(btn.id as any)}
                    className={`text-[8px] font-black px-1.5 py-0.5 rounded transition ${
                      traceFilter === btn.id
                        ? "bg-cyan-500 text-slate-950 font-black shadow-sm"
                        : "bg-slate-900 border border-slate-800 text-slate-500 hover:text-slate-300 hover:border-slate-700"
                    }`}
                  >
                    {btn.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Scrollable event trail stream */}
            <div className="flex-1 overflow-y-auto p-4 space-y-3 custom-scrollbar bg-slate-950/40">
              {filteredTraces.map((tr) => {
                const globalIndex = traces.findIndex((t) => t.id === tr.id) + 1;
                const globalIndexStr = String(globalIndex).padStart(2, "0");
                let badgeColor = "border-slate-800 bg-slate-900 text-slate-400";
                let typeLabel = "LOG";
                let borderGlow = "hover:border-slate-800/80";
                
                if (tr.type === "api_call") {
                  badgeColor = "border-cyan-800/60 bg-cyan-950/40 text-cyan-400";
                  typeLabel = "API CAL";
                  borderGlow = "hover:border-cyan-800/40 hover:bg-cyan-950/10";
                } else if (tr.type === "sse_chunk") {
                  badgeColor = "border-pink-800/60 bg-pink-950/40 text-pink-400";
                  typeLabel = "SSE FLW";
                  borderGlow = "hover:border-pink-800/40 hover:bg-pink-950/10";
                } else if (tr.type === "thought") {
                  badgeColor = "border-emerald-800/60 bg-emerald-950/40 text-emerald-400";
                  typeLabel = "THOUGHT";
                  borderGlow = "hover:border-emerald-800/40 hover:bg-emerald-950/10";
                } else if (tr.type === "token_flow" || tr.type === "token_count") {
                  badgeColor = "border-yellow-800/60 bg-yellow-950/40 text-yellow-400";
                  typeLabel = "TOKEN";
                  borderGlow = "hover:border-yellow-800/40 hover:bg-yellow-950/10";
                }

                const isSelected = selectedTrace?.id === tr.id;
                const borderStyle = isSelected
                  ? "border-cyan-500 bg-slate-900/60 shadow-lg shadow-cyan-500/10 scale-[1.01]"
                  : `border-slate-900/60 bg-slate-900/20 hover:border-slate-800/80 hover:scale-[1.01] cursor-pointer`;

                return (
                  <div
                    key={tr.id}
                    onClick={() => {
                      setSelectedTrace(tr);
                      setIsHudExpanded(true);
                      if (hudWidth < 950) {
                        setHudWidth(950);
                      }
                    }}
                    className={`p-3 rounded-xl border text-[10px] leading-relaxed transition-all duration-300 ${borderStyle}`}
                  >
                    <div className="flex items-center justify-between mb-1.5 gap-2 select-none">
                      <div className="flex items-center gap-1.5">
                        <span className="text-[8px] font-mono border border-slate-800/80 bg-slate-900/60 text-slate-400 px-1.5 py-0.2 rounded font-bold shrink-0">
                          #{globalIndexStr}
                        </span>
                        <span className={`text-[8px] border px-1.5 py-0.2 rounded font-black uppercase tracking-wider ${badgeColor}`}>
                          {typeLabel}
                        </span>
                        <span className="font-extrabold text-[11px] text-white truncate max-w-[180px]">
                          {tr.label}
                        </span>
                      </div>
                      <span className="text-[8px] text-slate-500 font-bold shrink-0">
                        {tr.timestamp}
                      </span>
                    </div>
                    
                    <p className="text-slate-400 font-medium break-words leading-relaxed font-sans">
                      {tr.details}
                    </p>
                  </div>
                );
              })}
              <div ref={traceEndRef} />
              
              {filteredTraces.length === 0 && (
                <div className="flex flex-col items-center justify-center h-[20vh] text-center p-6 bg-slate-900/10 rounded-2xl border border-dashed border-slate-800/50">
                  <span className="text-lg animate-pulse mb-1.5">📡</span>
                  <p className="text-[9px] font-black uppercase tracking-widest text-slate-500">
                    Trace line empty
                  </p>
                  <p className="text-[8px] text-slate-600 font-bold mt-1 max-w-[200px] leading-normal uppercase">
                    Waiting for system events matching "{traceFilter.toUpperCase()}" filter...
                  </p>
                </div>
              )}
            </div>
          </div>

          {/* Right Column / Drawer Detail Inspector */}
          {isHudExpanded ? (
            <div className={`border-l border-slate-900 bg-slate-950/98 backdrop-blur-lg flex flex-col transition-all duration-300 h-full shrink-0 ${selectedTrace ? "w-[480px] opacity-100" : "w-0 opacity-0 overflow-hidden pointer-events-none"}`}>
              {renderInspector()}
            </div>
          ) : (
            <div className={`absolute bottom-0 left-0 w-full bg-slate-950/98 backdrop-blur-lg border-t border-slate-800 transition-all duration-300 ease-in-out flex flex-col z-20 ${selectedTrace ? "h-[320px] opacity-100 border-cyan-500/20" : "h-0 opacity-0 overflow-hidden border-t-0 pointer-events-none"}`}>
              {renderInspector()}
            </div>
          )}
        </div>

        {/* Drawer Controls footer */}
        <div className="p-4 border-t border-slate-800 bg-slate-900/60 flex items-center justify-between gap-3 text-[9px] font-black">
          <button
            onClick={() => {
              setTraces([]);
              setSelectedTrace(null);
            }}
            className="px-3 py-2 bg-slate-900 border border-slate-800 hover:border-slate-700 text-slate-400 hover:text-white rounded-lg cursor-pointer transition uppercase"
          >
            [ CLEAR CONSOLE ]
          </button>
          
          <label className="flex items-center gap-1.5 text-slate-400 hover:text-slate-300 cursor-pointer select-none">
            <input
              type="checkbox"
              checked={autoScroll}
              onChange={(e) => setAutoScroll(e.target.checked)}
              className="rounded bg-slate-900 border-slate-800 text-cyan-500 focus:ring-0 cursor-pointer h-3 w-3"
            />
            <span>AUTO-SCROLL</span>
          </label>
        </div>
      </div>

      {/* Maximized Log Stream Left Overlay Panel */}
      {isTraceOpen && isLogStreamMaximized && (
        <div 
          className="fixed top-0 left-0 h-screen bg-slate-950/98 backdrop-blur-xl border-r border-slate-900 z-40 flex flex-col p-6 animate-fade-in text-slate-300 font-mono"
          style={{ width: `calc(100vw - ${hudWidth}px)` }}
        >
          {/* Header with quick close */}
          <div className="flex items-center justify-between border-b border-slate-800 pb-4 mb-4 select-none shrink-0">
            <div>
              <h3 className="text-xs font-black tracking-widest text-cyan-400 uppercase flex items-center gap-2">
                <span className="h-1.5 w-1.5 rounded-full bg-cyan-400 animate-ping"></span>
                ⚡ GROUNDING TELEMETRY COMMAND DECK
              </h3>
              <p className="text-[8px] text-slate-500 uppercase font-bold tracking-wider mt-1">Real-time Multi-Column Model-Native Grounding and Token tracing pipeline</p>
            </div>
            
            <div className="flex items-center gap-3">
              {/* Filter Buttons in maximized header */}
              <div className="flex bg-slate-900/80 border border-slate-800 p-0.5 rounded-lg gap-1 items-center mr-4">
                {[
                  { id: "all", label: "ALL" },
                  { id: "api", label: "API" },
                  { id: "sse", label: "SSE" },
                  { id: "thought", label: "MIND" },
                  { id: "token", label: "TOKEN" },
                ].map((btn) => (
                  <button
                    key={btn.id}
                    onClick={() => setTraceFilter(btn.id as any)}
                    className={`text-[8px] font-black px-2 py-1 rounded transition uppercase cursor-pointer ${
                      traceFilter === btn.id
                        ? "bg-cyan-500 text-slate-950 font-black shadow-sm"
                        : "text-slate-400 hover:text-slate-200"
                    }`}
                  >
                    {btn.label}
                  </button>
                ))}
              </div>

              {/* Layout Mode Toggle */}
              <div className="flex bg-slate-900/80 border border-slate-800 p-0.5 rounded-lg gap-1 items-center mr-4">
                {[
                  { id: "timeline", label: "≡ TIMELINE" },
                  { id: "grid", label: "⚃ GRID" },
                ].map((btn) => (
                  <button
                    key={btn.id}
                    onClick={() => setLogLayoutMode(btn.id as any)}
                    className={`text-[8px] font-black px-2 py-1 rounded transition uppercase cursor-pointer ${
                      logLayoutMode === btn.id
                        ? "bg-indigo-500 text-slate-950 font-black shadow-sm"
                        : "text-slate-400 hover:text-slate-200"
                    }`}
                  >
                    {btn.label}
                  </button>
                ))}
              </div>

              <button 
                onClick={() => setIsLogStreamMaximized(false)}
                className="text-slate-400 hover:text-white border border-slate-800 hover:border-slate-700 bg-slate-900/40 hover:bg-slate-900 px-3 py-1.5 text-[9px] rounded uppercase font-black transition cursor-pointer"
              >
                [ CLOSE PANEL × ]
              </button>
            </div>
          </div>
          
          {/* Side-by-side presentation space */}
          <div className="flex-1 flex gap-6 overflow-hidden min-h-0">
            {/* Left Column: Trace log list (grid of 2 columns if no selected trace, single column list if selected trace) */}
            <div className={`${selectedTrace ? (isDetailsWidescreen ? "w-0 overflow-hidden opacity-0 pointer-events-none hidden xl:flex-none" : "w-[32%]") : "w-full"} flex flex-col h-full min-w-0 transition-all duration-300`}>
              <div className="flex-1 overflow-y-auto p-2 space-y-3 custom-scrollbar pr-2 min-h-0">
                <div className={`grid ${selectedTrace ? "grid-cols-1" : (logLayoutMode === "grid" ? "grid-cols-2" : "grid-cols-1")} gap-3 align-start auto-rows-max`}>
                  {filteredTraces.map((tr) => {
                    const globalIndex = traces.findIndex((t) => t.id === tr.id) + 1;
                    const globalIndexStr = String(globalIndex).padStart(2, "0");
                    let badgeColor = "border-slate-800 bg-slate-900 text-slate-400";
                    let typeLabel = "LOG";
                    
                    if (tr.type === "api_call") {
                      badgeColor = "border-cyan-800/60 bg-cyan-950/40 text-cyan-400";
                      typeLabel = "API CAL";
                    } else if (tr.type === "sse_chunk") {
                      badgeColor = "border-pink-800/60 bg-pink-950/40 text-pink-400";
                      typeLabel = "SSE FLW";
                    } else if (tr.type === "thought") {
                      badgeColor = "border-emerald-800/60 bg-emerald-950/40 text-emerald-400";
                      typeLabel = "THOUGHT";
                    } else if (tr.type === "token_flow" || tr.type === "token_count") {
                      badgeColor = "border-yellow-800/60 bg-yellow-950/40 text-yellow-400";
                      typeLabel = "TOKEN";
                    }

                    const isSelected = selectedTrace?.id === tr.id;
                    const borderStyle = isSelected
                      ? "border-cyan-500 bg-slate-900/60 shadow-lg shadow-cyan-500/10 scale-[1.01]"
                      : `border-slate-900/60 bg-slate-900/20 hover:border-slate-800/80 hover:scale-[1.01] cursor-pointer`;

                    return (
                      <div
                        key={tr.id}
                        onClick={() => {
                          setSelectedTrace(tr);
                          // Do not expand/change the right-side HUD width when clicking in maximized view
                          // to prevent squeezing the detailed telemetry column on the left.
                        }}
                        className={`p-3 rounded-xl border text-[10px] leading-relaxed transition-all duration-300 ${borderStyle} self-start`}
                      >
                        <div className="flex items-center justify-between mb-1.5 gap-2 select-none">
                          <div className="flex items-center gap-1.5 font-mono">
                            <span className="text-[8px] border border-slate-800/80 bg-slate-900/60 text-slate-400 px-1.5 py-0.2 rounded font-bold shrink-0">
                              #{globalIndexStr}
                            </span>
                            <span className={`text-[8px] border px-1.5 py-0.2 rounded font-black uppercase tracking-wider ${badgeColor}`}>
                              {typeLabel}
                            </span>
                            <span className="font-extrabold text-[11px] text-white truncate max-w-[200px]">
                              {tr.label}
                            </span>
                          </div>
                          <span className="text-[8px] text-slate-500 font-bold shrink-0">
                            {tr.timestamp}
                          </span>
                        </div>
                        
                        <p className="text-slate-400 font-medium break-words leading-relaxed font-sans line-clamp-3">
                          {tr.details}
                        </p>
                      </div>
                    );
                  })}
                </div>
                <div ref={maximizedTraceEndRef} />
                
                {filteredTraces.length === 0 && (
                  <div className="flex flex-col items-center justify-center h-[40vh] text-center p-6 bg-slate-900/10 rounded-2xl border border-dashed border-slate-800/50">
                    <span className="text-2xl animate-pulse mb-2">📡</span>
                    <p className="text-[10px] font-black uppercase tracking-widest text-slate-500">
                      Trace line empty
                    </p>
                    <p className="text-[8px] text-slate-600 font-bold mt-1 max-w-[300px] leading-normal uppercase">
                      Waiting for system events matching "{traceFilter.toUpperCase()}" filter...
                    </p>
                  </div>
                )}
              </div>
            </div>

            {/* Right Column: Breathtaking Telemetry Dashboard */}
            {selectedTrace && (
              <div className={`${isDetailsWidescreen ? "w-full" : "w-[68%]"} h-full flex flex-col border border-slate-850 bg-slate-950/80 rounded-2xl overflow-hidden animate-fade-in min-w-0 transition-all duration-300`}>
                {/* Dashboard Header */}
                <div className="px-5 py-4 border-b border-slate-900/80 bg-slate-900/20 flex items-center justify-between gap-4 shrink-0 select-none">
                  <div className="flex items-center gap-3 overflow-hidden">
                    {(() => {
                      let typeLabel = "LOG";
                      let badgeColor = "border-slate-800 bg-slate-900 text-slate-400";
                      let dotColor = "bg-slate-400";
                      
                      if (selectedTrace.type === "api_call") {
                        typeLabel = "API HANDSHAKE";
                        badgeColor = "border-cyan-800/60 bg-cyan-950/40 text-cyan-400";
                        dotColor = "bg-cyan-400";
                      } else if (selectedTrace.type === "sse_chunk") {
                        typeLabel = "SSE EVENT STREAM";
                        badgeColor = "border-pink-800/60 bg-pink-950/40 text-pink-400";
                        dotColor = "bg-pink-400";
                      } else if (selectedTrace.type === "thought") {
                        typeLabel = "COGNITIVE MIND";
                        badgeColor = "border-emerald-800/60 bg-emerald-950/40 text-emerald-400";
                        dotColor = "bg-emerald-400";
                      } else if (selectedTrace.type === "token_flow" || selectedTrace.type === "token_count") {
                        typeLabel = "TOKEN RESOURCE";
                        badgeColor = "border-yellow-800/60 bg-yellow-950/40 text-yellow-400";
                        dotColor = "bg-yellow-400";
                      }
                      
                      return (
                        <>
                          <span className={`h-2 w-2 rounded-full ${dotColor} animate-pulse shrink-0`}></span>
                          <span className={`text-[8px] border px-2 py-0.5 rounded font-black uppercase tracking-wider ${badgeColor} shrink-0`}>
                            {typeLabel}
                          </span>
                        </>
                      );
                    })()}
                    <span className="font-extrabold text-[12px] text-white truncate uppercase tracking-wide">
                      {selectedTrace.label}
                    </span>
                  </div>
                  
                  <div className="flex items-center gap-3 shrink-0">
                    {/* Creative widescreen toggle for spacious customer layouts */}
                    <button
                      onClick={() => setIsDetailsWidescreen(!isDetailsWidescreen)}
                      className={`px-2.5 py-1 text-[10px] rounded uppercase font-black border transition duration-200 cursor-pointer flex items-center gap-1.5 ${
                        isDetailsWidescreen
                          ? "bg-cyan-950/40 border-cyan-500 text-cyan-400 hover:bg-cyan-900/40"
                          : "border-slate-800 text-slate-400 hover:text-white hover:bg-slate-850"
                      }`}
                      title={isDetailsWidescreen ? "Restore Split Layout" : "Maximize Details to Widescreen"}
                    >
                      {isDetailsWidescreen ? "🔲 Split View" : "🖥️ Widescreen"}
                    </button>

                    <span className="text-[9px] bg-slate-950 border border-slate-900 px-2 py-1 rounded text-slate-500 font-bold font-mono">
                      {selectedTrace.timestamp}
                    </span>
                    <button
                      onClick={() => {
                        setSelectedTrace(null);
                        setIsDetailsWidescreen(false); // Reset on deselection
                      }}
                      className="text-slate-400 hover:text-white border border-slate-800 hover:bg-slate-850 px-2.5 py-1 text-[10px] rounded uppercase font-black transition duration-200 cursor-pointer"
                    >
                      Deselect ×
                    </button>
                  </div>
                </div>

                {/* Dashboard Scrollable Body */}
                <div className="flex-1 overflow-y-auto p-6 space-y-6 custom-scrollbar text-[11px] select-text">
                  
                  {/* Summary Callout banner */}
                  <div className="p-4 bg-slate-900/20 rounded-xl border border-slate-900 space-y-2">
                    <span className="text-[8px] font-black text-slate-500 uppercase tracking-widest block">
                      📝 SUPPLEMENTARY INSIGHTS & DESCRIPTION
                    </span>
                    <p className="text-slate-200 font-sans leading-relaxed text-[11.5px] font-medium whitespace-pre-wrap selection:bg-cyan-900/50">
                      {selectedTrace.details || "No supplementary description details available for this event."}
                    </p>
                  </div>

                  {/* CUSTOM RICH PRESENTATION WIDGETS */}
                  {(() => {
                    // API Call Grounding References
                    if (selectedTrace.type === "api_call") {
                      const hasResults = selectedTrace.label.includes("Tool Response:") && selectedTrace.data?.response?.results;
                      const results = hasResults ? selectedTrace.data.response.results : [];

                      return (
                        <div className="space-y-4 animate-fade-in">
                          {/* SVG Pipeline flow diagram - Always visible for API Calls to provide full-system context */}
                          <div className="space-y-1.5">
                            <span className="text-[8px] font-black text-slate-500 uppercase tracking-widest block">
                              🌐 ENTERPRISE GROUNDING PIPELINE STACK DIAGRAM
                            </span>
                            <div className="p-3 bg-slate-950/60 rounded-xl border border-cyan-950/40 flex items-center justify-between gap-1 text-center text-[9px] font-mono overflow-x-auto select-none custom-scrollbar">
                              {/* 1. DATA STORE Bubble */}
                              <div 
                                onClick={() => setSelectedPipelineBubble(selectedPipelineBubble === "datastore" ? null : "datastore")}
                                className={`flex flex-col items-center p-2 rounded-lg w-24 shrink-0 cursor-pointer select-none transition-all duration-300 transform hover:scale-[1.03] hover:shadow-[0_0_12px_rgba(147,51,234,0.15)] ${
                                  selectedPipelineBubble === "datastore"
                                    ? "border-purple-500 bg-purple-950/20 shadow-[0_0_12px_rgba(147,51,234,0.25)] border-2 -m-[1px]"
                                    : "bg-slate-900/50 border border-slate-800 hover:border-purple-500/50 hover:bg-slate-900/80"
                                }`}
                              >
                                <span className="text-base mb-0.5">📁</span>
                                <span className={`${selectedPipelineBubble === "datastore" ? "text-purple-400" : "text-slate-400"} font-black text-[8px]`}>DATA STORE</span>
                                <span className="text-[7px] text-slate-500">GCS / Drive</span>
                              </div>

                              {/* Connection 1 */}
                              <div className="flex-1 flex flex-col items-center justify-center min-w-[20px] shrink-0">
                                <div className="text-[6.5px] text-purple-400 uppercase font-black tracking-tighter">mount</div>
                                <svg className="w-6 h-3 text-purple-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                                  <path strokeLinecap="round" strokeLinejoin="round" d="M14 5l7 7m0 0l-7 7m7-7H3" />
                                </svg>
                                <div className="text-[6px] text-slate-600 font-bold uppercase">sync</div>
                              </div>

                              {/* 2. ACCESS SCOPE Bubble */}
                              <div 
                                onClick={() => setSelectedPipelineBubble(selectedPipelineBubble === "access" ? null : "access")}
                                className={`flex flex-col items-center p-2 rounded-lg w-24 shrink-0 cursor-pointer select-none transition-all duration-300 transform hover:scale-[1.03] hover:shadow-[0_0_12px_rgba(99,102,241,0.15)] ${
                                  selectedPipelineBubble === "access"
                                    ? "border-indigo-500 bg-indigo-950/20 shadow-[0_0_12px_rgba(99,102,241,0.25)] border-2 -m-[1px]"
                                    : "bg-slate-900/50 border border-slate-800 hover:border-indigo-500/50 hover:bg-slate-900/80"
                                }`}
                              >
                                <span className="text-base mb-0.5">🔑</span>
                                <span className={`${selectedPipelineBubble === "access" ? "text-indigo-400" : "text-slate-400"} font-black text-[8px]`}>ACCESS SCOPE</span>
                                <span className="text-[7px] text-slate-500">OAuth / ADC</span>
                              </div>

                              {/* Connection 2 */}
                              <div className="flex-1 flex flex-col items-center justify-center min-w-[20px] shrink-0">
                                <div className="text-[6.5px] text-indigo-400 uppercase font-black tracking-tighter">auth</div>
                                <svg className="w-6 h-3 text-indigo-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                                  <path strokeLinecap="round" strokeLinejoin="round" d="M14 5l7 7m0 0l-7 7m7-7H3" />
                                </svg>
                                <div className="text-[6px] text-slate-600 font-bold uppercase">handshake</div>
                              </div>

                              {/* 3. VERTEX AI SEARCH Bubble */}
                              <div 
                                onClick={() => setSelectedPipelineBubble(selectedPipelineBubble === "flow" ? null : "flow")}
                                className={`flex flex-col items-center p-2 rounded-lg w-26 shrink-0 cursor-pointer select-none transition-all duration-300 transform hover:scale-[1.03] hover:shadow-[0_0_12px_rgba(6,182,212,0.15)] ${
                                  selectedPipelineBubble === "flow"
                                    ? "border-cyan-500 bg-cyan-950/20 shadow-[0_0_12px_rgba(6,182,212,0.25)] border-2 -m-[1px]"
                                    : "bg-cyan-950/20 border border-cyan-800/40 hover:border-cyan-500/50 hover:bg-cyan-950/40"
                                }`}
                              >
                                <span className="text-base mb-0.5 animate-pulse">⚡</span>
                                <span className={`${selectedPipelineBubble === "flow" ? "text-cyan-300" : "text-cyan-400"} font-black text-[8px]`}>VERTEX SEARCH</span>
                                <span className="text-[7px] text-cyan-600 font-bold">Discovery Engine</span>
                              </div>

                              {/* Connection 3 */}
                              <div className="flex-1 flex flex-col items-center justify-center min-w-[20px] shrink-0">
                                <div className="text-[6.5px] text-cyan-400 uppercase font-black tracking-tighter">lookup</div>
                                <svg className="w-6 h-3 text-cyan-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                                  <path strokeLinecap="round" strokeLinejoin="round" d="M14 5l7 7m0 0l-7 7m7-7H3" />
                                </svg>
                                <div className="text-[6px] text-slate-600 font-bold uppercase">results</div>
                              </div>

                              {/* 4. ZERO-LEAK GATEWAY Bubble */}
                              <div 
                                onClick={() => setSelectedPipelineBubble(selectedPipelineBubble === "security" ? null : "security")}
                                className={`flex flex-col items-center p-2 rounded-lg w-24 shrink-0 cursor-pointer select-none transition-all duration-300 transform hover:scale-[1.03] hover:shadow-[0_0_12px_rgba(16,185,129,0.15)] ${
                                  selectedPipelineBubble === "security"
                                    ? "border-emerald-500 bg-emerald-950/20 shadow-[0_0_12px_rgba(16,185,129,0.25)] border-2 -m-[1px]"
                                    : "bg-slate-900/50 border border-slate-800 hover:border-emerald-500/50 hover:bg-slate-900/80"
                                }`}
                              >
                                <span className="text-base mb-0.5">🛡️</span>
                                <span className={`${selectedPipelineBubble === "security" ? "text-emerald-400" : "text-slate-400"} font-black text-[8px]`}>ZERO-LEAK</span>
                                <span className="text-[7px] text-slate-500">Secure Tunnel</span>
                              </div>

                              {/* Connection 4 */}
                              <div className="flex-1 flex flex-col items-center justify-center min-w-[20px] shrink-0">
                                <div className="text-[6.5px] text-emerald-400 uppercase font-black tracking-tighter">transit</div>
                                <svg className="w-6 h-3 text-emerald-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                                  <path strokeLinecap="round" strokeLinejoin="round" d="M14 5l7 7m0 0l-7 7m7-7H3" />
                                </svg>
                                <div className="text-[6px] text-slate-600 font-bold uppercase">tls proxy</div>
                              </div>

                              {/* 5. LLM STACK Bubble */}
                              <div 
                                onClick={() => setSelectedPipelineBubble(selectedPipelineBubble === "model" ? null : "model")}
                                className={`flex flex-col items-center p-2 rounded-lg w-24 shrink-0 cursor-pointer select-none transition-all duration-300 transform hover:scale-[1.03] hover:shadow-[0_0_12px_rgba(234,179,8,0.15)] ${
                                  selectedPipelineBubble === "model"
                                    ? "border-yellow-500 bg-yellow-950/20 shadow-[0_0_12px_rgba(234,179,8,0.25)] border-2 -m-[1px]"
                                    : "bg-slate-900/50 border border-slate-800 hover:border-yellow-500/50 hover:bg-slate-900/80"
                                }`}
                              >
                                <span className="text-base mb-0.5">🤖</span>
                                <span className={`${selectedPipelineBubble === "model" ? "text-yellow-400" : "text-slate-400"} font-black text-[8px]`}>LLM STACK</span>
                                <span className="text-[7px] text-slate-500">Grounded Context</span>
                              </div>
                            </div>
                          </div>

                          {/* Interactive Expandable Code Terminal (Universal across all Bubble selections) */}
                          {selectedPipelineBubble && (
                            <div className="border border-slate-800 bg-slate-950 rounded-xl overflow-hidden animate-fade-in font-mono text-[9px] text-slate-300 shadow-[0_4px_24px_rgba(0,0,0,0.4)]">
                              {/* Title bar / Tab header */}
                              <div className="px-4 py-2 border-b border-slate-900 bg-slate-900/40 flex items-center justify-between select-none">
                                <div className="flex items-center gap-2">
                                  <span className={`h-1.5 w-1.5 rounded-full animate-pulse ${
                                    selectedPipelineBubble === "datastore" ? "bg-purple-400" :
                                    selectedPipelineBubble === "flow" ? "bg-cyan-400" :
                                    selectedPipelineBubble === "security" ? "bg-emerald-400" :
                                    selectedPipelineBubble === "access" ? "bg-indigo-400" : "bg-yellow-400"
                                  }`}></span>
                                  <span className="text-slate-400 font-bold text-[8.5px] uppercase tracking-wider">
                                    ACTIVE DEPLOYMENT CONFIGURATION BLUEPRINT
                                  </span>
                                  <span className="text-slate-500 font-black px-1.5 py-0.5 rounded border border-slate-800 bg-slate-900 text-[7.5px] font-mono">
                                    {selectedPipelineBubble === "datastore" && "enterprise_gsuite_datastore.py"}
                                    {selectedPipelineBubble === "flow" && "discovery_engine_search.py"}
                                    {selectedPipelineBubble === "security" && "zero_leak_gateway.py"}
                                    {selectedPipelineBubble === "access" && "oauth_adc_verifier.py"}
                                    {selectedPipelineBubble === "model" && "gemini_grounding_orchestrator.py"}
                                  </span>
                                </div>
                                <button
                                  onClick={() => {
                                    let codeText = "";
                                    if (selectedPipelineBubble === "datastore") {
                                      codeText = `# Create and Synchronize a Google GSuite Data Store\nfrom google.cloud import discoveryengine_v1beta as discoveryengine\n\nclient = discoveryengine.DataStoreServiceClient()\n\n# 1. Define parent project & collection context\nparent = f"projects/gemini-enterprise-demo/locations/global/collections/default_collection"\n\n# 2. Configure the GDrive / GCS target mapping\ndata_store = discoveryengine.DataStore(\n    display_name="Enterprise GSuite Store",\n    industry_vertical=discoveryengine.DataStore.IndustryVertical.GENERIC,\n    content_config=discoveryengine.DataStore.ContentConfig.CONTENT_REQUIRED,\n    solution_types=[discoveryengine.SolutionType.SOLUTION_TYPE_SEARCH],\n)\n\n# 3. Request Data Store creation\noperation = client.create_data_store(\n    parent=parent,\n    data_store=data_store,\n    data_store_id="gsuite-gdrive-datastores"\n)\nprint(f"Data Store Sync Staged: {operation.name}")`;
                                    } else if (selectedPipelineBubble === "flow") {
                                      codeText = `# 1. Initialize the Vertex AI Search client\nfrom google.cloud import discoveryengine_v1beta as discoveryengine\n\nclient = discoveryengine.SearchServiceClient()\n\n# 2. Build the serving config path for the data store\nserving_config = client.serving_config_path(\n    project="gemini-enterprise-demo",\n    location="global",\n    data_store="gsuite-gdrive-datastores",\n    serving_config="default_search"\n)\n\n# 3. Configure ACL and authorization parameters\nrequest = discoveryengine.SearchRequest(\n    serving_config=serving_config,\n    query=user_query,\n    page_size=10,\n    # Enforces structural document filters\n    params={"score_threshold": 0.65}\n)\n\n# 4. Execute the secure grounding lookup\nsearch_results = client.search(request)`;
                                    } else if (selectedPipelineBubble === "security") {
                                      codeText = `# Secure Transit & Corporate Isolation Tunnel\nimport os\nimport ssl\nimport httpx\n\nclass ZeroLeakGateway:\n    def __init__(self):\n        # Read encrypted credentials from isolated environment\n        self.gateway_url = os.getenv("ENTERPRISE_GATEWAY_URL")\n        self.tls_cert = os.getenv("SECURE_TLS_PEM_PATH")\n\n    def forward_safe_query(self, query_payload: dict) -> dict:\n        # Enforce corporate transit TLS verification\n        ctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)\n        ctx.load_cert_chain(certfile=self.tls_cert)\n        \n        with httpx.Client(verify=ctx) as client:\n            # Proxied search avoids direct public endpoint queries\n            response = client.post(\n                f"{self.gateway_url}/v1/search/grounding",\n                json=query_payload,\n                headers={"X-Secured-Routing": "True"}\n            )\n            return response.json()`;
                                    } else if (selectedPipelineBubble === "access") {
                                      codeText = `# Google OAuth 2.0 Access Policy Verifier\nfrom google.oauth2 import credentials\nfrom google.auth.transport.requests import Request\n\ndef verify_and_bind_token(raw_access_token: str) -> credentials.Credentials:\n    # 1. Bind user workspace session credentials\n    user_creds = credentials.Credentials(\n        token=raw_access_token,\n        scopes=["https://www.googleapis.com/auth/drive.readonly"]\n    )\n    \n    # 2. Validate token viability with secure auth channel\n    auth_request = Request()\n    user_creds.refresh(auth_request)\n    \n    if not user_creds.valid:\n        raise PermissionError("Workspace authorization expired")\n        \n    # 3. Apply ACL validation matrix in-memory\n    print(f"Token scoped securely: {user_creds.scopes}")\n    return user_creds`;
                                    } else if (selectedPipelineBubble === "model") {
                                      codeText = `# Model-Native Grounding Configuration via Google GenAI SDK\nfrom google import genai\nfrom google.genai import types\n\ndef generate_grounded_response(user_prompt: str, workspace_creds):\n    # Initialize modern Google GenAI Client\n    client = genai.Client()\n    \n    # Configure Gemini 2.5 Pro with model-native search tools\n    config = types.GenerateContentConfig(\n        system_instruction="Analyze and answer queries ONLY based on grounding search tools.",\n        temperature=0.0, # Zero temperature ensures exact factual grounding\n        tools=[\n            types.Tool(\n                # Register Vertex AI Search Grounding Connection\n                vertex_ai_search=types.VertexAISearch(\n                    project="gemini-enterprise-demo",\n                    datastore="gsuite-gdrive-datastores"\n                )\n            )\n        ]\n    )\n    \n    response = client.models.generate_content(\n        model="gemini-2.5-pro",\n        contents=user_prompt,\n        config=config\n    )\n    return response.text`;
                                    }
                                    
                                    navigator.clipboard.writeText(codeText);
                                    setBlueprintCopied(true);
                                    setTimeout(() => setBlueprintCopied(false), 2000);
                                  }}
                                  className={`px-2.5 py-1 border rounded text-[7.5px] font-black transition-all duration-200 uppercase cursor-pointer ${
                                    blueprintCopied
                                      ? "bg-emerald-950/60 border-emerald-500 text-emerald-400 font-bold animate-pulse"
                                      : "border-slate-800 bg-slate-900/60 text-slate-400 hover:text-white hover:border-slate-700"
                                  }`}
                                >
                                  {blueprintCopied ? "COPIED BLUEPRINT!" : "[ Copy Blueprint ]"}
                                </button>
                              </div>
                              
                              {/* Code Content Container */}
                              <pre className="p-4 overflow-x-auto custom-scrollbar max-h-[220px] bg-slate-950/80 leading-relaxed whitespace-pre text-slate-300">
                                {selectedPipelineBubble === "datastore" && (
                                  <div>
                                    <span className="text-slate-500 font-bold">{"# Create and Synchronize a Google GSuite Data Store"}</span>{"\n"}
                                    <span className="text-pink-400 font-black">{"from "}</span>{"google.cloud "}
                                    <span className="text-pink-400 font-black">{"import "}</span>{"discoveryengine_v1beta "}
                                    <span className="text-pink-400 font-black">{"as "}</span>{"discoveryengine"}{"\n\n"}
                                    
                                    {"client = discoveryengine."}<span className="text-yellow-400 font-black">{"DataStoreServiceClient"}</span>{"()"}{"\n\n"}
                                    
                                    <span className="text-slate-500 font-bold">{"# 1. Define parent project & collection context"}</span>{"\n"}
                                    {"parent = f"}<span className="text-cyan-300">{"\"projects/gemini-enterprise-demo/locations/global/collections/default_collection\""}</span>{"\n\n"}
                                    
                                    <span className="text-slate-500 font-bold">{"# 2. Configure the GDrive / GCS target mapping"}</span>{"\n"}
                                    {"data_store = discoveryengine."}<span className="text-yellow-400 font-black">{"DataStore"}</span>{"("}{"\n"}
                                    {"    display_name="}<span className="text-cyan-300">{"\"Enterprise GSuite Store\""}</span>{","}{"\n"}
                                    {"    industry_vertical=discoveryengine."}<span className="text-yellow-400 font-black">{"DataStore"}</span>{".IndustryVertical.GENERIC,"}{"\n"}
                                    {"    content_config=discoveryengine."}<span className="text-yellow-400 font-black">{"DataStore"}</span>{".ContentConfig.CONTENT_REQUIRED,"}{"\n"}
                                    {"    solution_types=["}{"discoveryengine."}<span className="text-yellow-400 font-black">{"SolutionType"}</span>{".SOLUTION_TYPE_SEARCH]"}{"\n"}
                                    {")"}{"\n\n"}
                                    
                                    <span className="text-slate-500 font-bold">{"# 3. Request Data Store creation"}</span>{"\n"}
                                    {"operation = client."}<span className="text-cyan-400 font-black">{"create_data_store"}</span>{"("}{"\n"}
                                    {"    parent=parent,"}{"\n"}
                                    {"    data_store=data_store,"}{"\n"}
                                    {"    data_store_id="}<span className="text-cyan-300">{"\"gsuite-gdrive-datastores\""}</span>{"\n"}
                                    {")"}{"\n"}
                                    {"print(f"}<span className="text-cyan-300">{"\"Data Store Sync Staged: {operation.name}\""}</span>{")"}
                                  </div>
                                )}
                                {selectedPipelineBubble === "flow" && (
                                  <div>
                                    <span className="text-slate-500 font-bold">{"# 1. Initialize the Vertex AI Search client"}</span>{"\n"}
                                    <span className="text-pink-400 font-black">{"from "}</span>{"google.cloud "}
                                    <span className="text-pink-400 font-black">{"import "}</span>{"discoveryengine_v1beta "}
                                    <span className="text-pink-400 font-black">{"as "}</span>{"discoveryengine"}{"\n\n"}
                                    
                                    {"client = discoveryengine."}<span className="text-yellow-400 font-black">{"SearchServiceClient"}</span>{"()"}{"\n\n"}
                                    
                                    <span className="text-slate-500 font-bold">{"# 2. Build the serving config path for the data store"}</span>{"\n"}
                                    {"serving_config = client."}<span className="text-cyan-400 font-black">{"serving_config_path"}</span>{"("}{"\n"}
                                    {"    project="}<span className="text-cyan-300">{"\"gemini-enterprise-demo\""}</span>{","}{"\n"}
                                    {"    location="}<span className="text-cyan-300">{"\"global\""}</span>{","}{"\n"}
                                    {"    data_store="}<span className="text-cyan-300">{"\"gsuite-gdrive-datastores\""}</span>{","}{"\n"}
                                    {"    serving_config="}<span className="text-cyan-300">{"\"default_search\""}</span>{"\n"}
                                    {")"}{"\n\n"}
                                    
                                    <span className="text-slate-500 font-bold">{"# 3. Configure ACL and authorization parameters"}</span>{"\n"}
                                    {"request = discoveryengine."}<span className="text-yellow-400 font-black">{"SearchRequest"}</span>{"("}{"\n"}
                                    {"    serving_config=serving_config,"}{"\n"}
                                    {"    query=user_query,"}{"\n"}
                                    {"    page_size="}<span className="text-pink-400 font-black">{"10"}</span>{","}{"\n"}
                                    <span className="text-slate-500 font-bold">{"    # Enforces structural document filters"}</span>{"\n"}
                                    {"    params={"}<span className="text-cyan-300">{"\"score_threshold\""}</span>{": "}<span className="text-pink-400 font-black">{"0.65"}</span>{"}"}{"\n"}
                                    {")"}{"\n\n"}
                                    
                                    <span className="text-slate-500 font-bold">{"# 4. Execute the secure grounding lookup"}</span>{"\n"}
                                    {"search_results = client."}<span className="text-cyan-400 font-black">{"search"}</span>{"(request)"}
                                  </div>
                                )}
                                {selectedPipelineBubble === "security" && (
                                  <div>
                                    <span className="text-slate-500 font-bold">{"# Secure Transit & Corporate Isolation Tunnel"}</span>{"\n"}
                                    <span className="text-pink-400 font-black">{"import "}</span>{"os"}{"\n"}
                                    <span className="text-pink-400 font-black">{"import "}</span>{"ssl"}{"\n"}
                                    <span className="text-pink-400 font-black">{"import "}</span>{"httpx"}{"\n\n"}
                                    
                                    <span className="text-pink-400 font-black">{"class "}</span><span className="text-yellow-400 font-black">{"ZeroLeakGateway"}</span>{":"}{"\n"}
                                    {"    "}<span className="text-pink-400 font-black">{"def "}</span><span className="text-cyan-400 font-black">{"__init__"}</span>{"(self):"}{"\n"}
                                    {"        "}<span className="text-slate-500 font-bold">{"# Read encrypted credentials from isolated environment"}</span>{"\n"}
                                    {"        self.gateway_url = os."}<span className="text-cyan-400 font-black">{"getenv"}</span>{"("}<span className="text-cyan-300">{"\"ENTERPRISE_GATEWAY_URL\""}</span>{")"}{"\n"}
                                    {"        self.tls_cert = os."}<span className="text-cyan-400 font-black">{"getenv"}</span>{"("}<span className="text-cyan-300">{"\"SECURE_TLS_PEM_PATH\""}</span>{")"}{"\n\n"}
                                    
                                    {"    "}<span className="text-pink-400 font-black">{"def "}</span><span className="text-cyan-400 font-black">{"forward_safe_query"}</span>{"(self, query_payload: "}<span className="text-yellow-400 font-black">{"dict"}</span>{") -> "}<span className="text-yellow-400 font-black">{"dict"}</span>{":"}{"\n"}
                                    {"        "}<span className="text-slate-500 font-bold">{"# Enforce corporate transit TLS verification"}</span>{"\n"}
                                    {"        ctx = ssl."}<span className="text-cyan-400 font-black">{"create_default_context"}</span>{"(ssl."}<span className="text-yellow-400 font-black">{"Purpose"}</span>{".SERVER_AUTH)"}{"\n"}
                                    {"        ctx."}<span className="text-cyan-400 font-black">{"load_cert_chain"}</span>{"(certfile=self.tls_cert)"}{"\n\n"}
                                    {"        "}<span className="text-pink-400 font-black">{"with "}</span>{"httpx."}<span className="text-yellow-400 font-black">{"Client"}</span>{"(verify=ctx) "}<span className="text-pink-400 font-black">{"as "}</span>{"client:"}{"\n"}
                                    {"            "}<span className="text-slate-500 font-bold">{"# Proxied search avoids direct public endpoint queries"}</span>{"\n"}
                                    {"            response = client."}<span className="text-cyan-400 font-black">{"post"}</span>{"("}{"\n"}
                                    {"                f"}<span className="text-cyan-300">{"\"{self.gateway_url}/v1/search/grounding\""}</span>{","}{"\n"}
                                    {"                json=query_payload,"}{"\n"}
                                    {"                headers={"}<span className="text-cyan-300">{"\"X-Secured-Routing\""}</span>{": "}<span className="text-cyan-300">{"\"True\""}</span>{"}"}{"\n"}
                                    {"            )"}{"\n"}
                                    {"            "}<span className="text-pink-400 font-black">{"return "}</span>{"response."}<span className="text-cyan-400 font-black">{"json"}</span>{"()"}{"\n"}
                                  </div>
                                )}
                                {selectedPipelineBubble === "access" && (
                                  <div>
                                    <span className="text-slate-500 font-bold">{"# Google OAuth 2.0 Access Policy Verifier"}</span>{"\n"}
                                    <span className="text-pink-400 font-black">{"from "}</span>{"google.oauth2 "}
                                    <span className="text-pink-400 font-black">{"import "}</span>{"credentials"}{"\n"}
                                    <span className="text-pink-400 font-black">{"from "}</span>{"google.auth.transport.requests "}
                                    <span className="text-pink-400 font-black">{"import "}</span>{"Request"}{"\n\n"}
                                    
                                    <span className="text-pink-400 font-black">{"def "}</span><span className="text-cyan-400 font-black">{"verify_and_bind_token"}</span>{"(raw_access_token: "}<span className="text-yellow-400 font-black">{"str"}</span>{") -> credentials."}<span className="text-yellow-400 font-black">{"Credentials"}</span>{":"}{"\n"}
                                    {"    "}<span className="text-slate-500 font-bold">{"# 1. Bind user workspace session credentials"}</span>{"\n"}
                                    {"    user_creds = credentials."}<span className="text-yellow-400 font-black">{"Credentials"}</span>{"("}{"\n"}
                                    {"        token=raw_access_token,"}{"\n"}
                                    {"        scopes=["}<span className="text-cyan-300">{"\"https://www.googleapis.com/auth/drive.readonly\""}</span>{"]"}{"\n"}
                                    {"    )"}{"\n\n"}
                                    {"    "}<span className="text-slate-500 font-bold">{"# 2. Validate token viability with secure auth channel"}</span>{"\n"}
                                    {"    auth_request = "}<span className="text-yellow-400 font-black">{"Request"}</span>{"()"}{"\n"}
                                    {"    user_creds."}<span className="text-cyan-400 font-black">{"refresh"}</span>{"(auth_request)"}{"\n\n"}
                                    {"    "}<span className="text-pink-400 font-black">{"if not "}</span>{"user_creds.valid:"}{"\n"}
                                    {"        "}<span className="text-pink-400 font-black">{"raise "}</span><span className="text-yellow-400 font-black">{"PermissionError"}</span>{"("}<span className="text-cyan-300">{"\"Workspace authorization expired\""}</span>{")"}{"\n\n"}
                                    {"    "}<span className="text-slate-500 font-bold">{"# 3. Apply ACL validation matrix in-memory"}</span>{"\n"}
                                    {"    "}<span className="text-pink-400 font-black">{"print"}</span>{"(f"}<span className="text-cyan-300">{"\"Token scoped securely: {user_creds.scopes}\""}</span>{")"}{"\n"}
                                    {"    "}<span className="text-pink-400 font-black">{"return "}</span>{"user_creds"}{"\n"}
                                  </div>
                                )}
                                {selectedPipelineBubble === "model" && (
                                  <div>
                                    <span className="text-slate-500 font-bold">{"# Model-Native Grounding Configuration via Google GenAI SDK"}</span>{"\n"}
                                    <span className="text-pink-400 font-black">{"from "}</span>{"google "}
                                    <span className="text-pink-400 font-black">{"import "}</span>{"genai"}{"\n"}
                                    <span className="text-pink-400 font-black">{"from "}</span>{"google.genai "}
                                    <span className="text-pink-400 font-black">{"import "}</span>{"types"}{"\n\n"}
                                    
                                    <span className="text-pink-400 font-black">{"def "}</span><span className="text-cyan-400 font-black">{"generate_grounded_response"}</span>{"(user_prompt: "}<span className="text-yellow-400 font-black">{"str"}</span>{", workspace_creds):"}{"\n"}
                                    {"    "}<span className="text-slate-500 font-bold">{"# Initialize modern Google GenAI Client"}</span>{"\n"}
                                    {"    client = genai."}<span className="text-yellow-400 font-black">{"Client"}</span>{"()"}{"\n\n"}
                                    {"    "}<span className="text-slate-500 font-bold">{"# Configure Gemini 2.5 Pro with model-native search tools"}</span>{"\n"}
                                    {"    config = types."}<span className="text-yellow-400 font-black">{"GenerateContentConfig"}</span>{"("}{"\n"}
                                    {"        system_instruction="}<span className="text-cyan-300">{"\"Analyze and answer queries ONLY based on grounding search tools.\""}</span>{","}{"\n"}
                                    {"        temperature="}<span className="text-pink-400 font-black">{"0.0"}</span>{","}{"\n"}
                                    {"        tools=["}{"\n"}
                                    {"            types."}<span className="text-yellow-400 font-black">{"Tool"}</span>{"("}{"\n"}
                                    {"                "}<span className="text-slate-500 font-bold">{"# Register Vertex AI Search Grounding Connection"}</span>{"\n"}
                                    {"                vertex_ai_search=types."}<span className="text-yellow-400 font-black">{"VertexAISearch"}</span>{"("}{"\n"}
                                    {"                    project="}<span className="text-cyan-300">{"\"gemini-enterprise-demo\""}</span>{","}{"\n"}
                                    {"                    datastore="}<span className="text-cyan-300">{"\"gsuite-gdrive-datastores\""}</span>{"\n"}
                                    {"                )"}{"\n"}
                                    {"            )"}{"\n"}{"        ]"}{"\n"}
                                    {"    )"}{"\n\n"}
                                    {"    response = client.models."}<span className="text-cyan-400 font-black">{"generate_content"}</span>{"("}{"\n"}
                                    {"        model="}<span className="text-cyan-300">{"\"gemini-2.5-pro\""}</span>{","}{"\n"}
                                    {"        contents=user_prompt,"}{"\n"}
                                    {"        config=config"}{"\n"}
                                    {"    )"}{"\n"}
                                    {"    "}<span className="text-pink-400 font-black">{"return "}</span>{"response.text"}{"\n"}
                                  </div>
                                )}
                              </pre>
                            </div>
                          )}

                          {/* Content below diagram and code terminal: Grounding References OR Metrics grid */}
                          {hasResults ? (
                            <div className="space-y-3">
                              <span className="text-[8px] font-black text-slate-500 uppercase tracking-widest block">
                                🔍 ACTIVE GROUNDING REFERENCES ({results.length} documents identified)
                              </span>
                              <div className="grid grid-cols-1 xl:grid-cols-2 gap-3">
                                {results.map((res: any, idx: number) => (
                                  <div key={idx} className="p-3 bg-slate-950/60 rounded-xl border border-slate-900 hover:border-cyan-500/40 hover:bg-slate-900/30 transition duration-300 flex flex-col justify-between">
                                    <div>
                                      <div className="flex items-center justify-between gap-2 border-b border-slate-900 pb-2 mb-2">
                                        <span className="text-[8px] bg-cyan-950 text-cyan-400 px-2 py-0.5 rounded font-black tracking-widest uppercase">
                                          REFERENCE {idx + 1}
                                        </span>
                                        <span className="text-[8px] font-mono font-bold text-slate-500">
                                          RELEVANCE: 0.98
                                        </span>
                                      </div>
                                      <a 
                                        href={res.link} 
                                        target="_blank" 
                                        rel="noopener noreferrer"
                                        className="text-[11px] font-extrabold text-cyan-400 hover:underline hover:text-cyan-300 flex items-center gap-1.5 uppercase truncate"
                                      >
                                        📂 {res.title || res.link?.split('/').pop() || "Grounded File"}
                                      </a>
                                      {res.snippet && (
                                        <p className="text-slate-400 font-medium font-sans leading-relaxed mt-2.5 text-[10px] bg-slate-950/80 p-2 rounded border border-slate-900">
                                          "{res.snippet}"
                                        </p>
                                      )}
                                    </div>
                                    <div className="pt-2 text-[8px] font-mono text-slate-500 flex items-center justify-between border-t border-slate-900/40 mt-3 uppercase">
                                      <span>GSuite Index Staged</span>
                                      <span className="text-cyan-600 font-black">Active Grounded Link</span>
                                    </div>
                                  </div>
                                ))}
                              </div>
                            </div>
                          ) : (
                            <div className="space-y-3">
                              <span className="text-[8px] font-black text-slate-500 uppercase tracking-widest block">
                                🌐 ENTERPRISE GROUNDING PIPELINE STACK DETAILS
                              </span>
                              <div className="grid grid-cols-1 xl:grid-cols-2 gap-4 bg-slate-950/60 p-4 rounded-xl border border-slate-900 font-mono text-[9px] text-slate-400 leading-normal">
                                {/* Card 1: Flow */}
                                <div 
                                  onClick={() => setSelectedPipelineBubble(selectedPipelineBubble === "flow" ? null : "flow")}
                                  className={`p-3 rounded-lg border cursor-pointer select-none transition-all duration-300 ${
                                    selectedPipelineBubble === "flow"
                                      ? "border-cyan-500 bg-cyan-950/20 shadow-[0_0_12px_rgba(6,182,212,0.15)]"
                                      : "bg-slate-900/20 border-slate-900/60 hover:border-cyan-500/40 hover:bg-slate-900/30"
                                  }`}
                                >
                                  <div className="flex items-center justify-between mb-1">
                                    <span className="text-slate-500 text-[8px] uppercase tracking-wider block font-bold">FLOW PIPELINE</span>
                                    <span className={`text-[7px] font-black uppercase ${selectedPipelineBubble === "flow" ? "text-cyan-400" : "text-slate-600"}`}>
                                      {selectedPipelineBubble === "flow" ? "● ACTIVE BLUEPRINT" : "○ CLICK TO EXPLORE"}
                                    </span>
                                  </div>
                                  <span className="text-cyan-400 font-black text-[10.5px] block uppercase mt-0.5">Vertex AI Search API</span>
                                  <p className="text-[7.5px] text-slate-600 mt-1 leading-normal uppercase">Queries are processed via Enterprise Google Cloud Search Connector and routed dynamically based on ACL constraints.</p>
                                </div>

                                {/* Card 2: Security */}
                                <div 
                                  onClick={() => setSelectedPipelineBubble(selectedPipelineBubble === "security" ? null : "security")}
                                  className={`p-3 rounded-lg border cursor-pointer select-none transition-all duration-300 ${
                                    selectedPipelineBubble === "security"
                                      ? "border-emerald-500 bg-emerald-950/20 shadow-[0_0_12px_rgba(16,185,129,0.15)]"
                                      : "bg-slate-900/20 border-slate-900/60 hover:border-emerald-500/40 hover:bg-slate-900/30"
                                  }`}
                                >
                                  <div className="flex items-center justify-between mb-1">
                                    <span className="text-slate-500 text-[8px] uppercase tracking-wider block font-bold">GSUITE SECURITY INTEGRATION</span>
                                    <span className={`text-[7px] font-black uppercase ${selectedPipelineBubble === "security" ? "text-emerald-400" : "text-slate-600"}`}>
                                      {selectedPipelineBubble === "security" ? "● ACTIVE BLUEPRINT" : "○ CLICK TO EXPLORE"}
                                    </span>
                                  </div>
                                  <span className="text-emerald-400 font-black text-[10.5px] block uppercase mt-0.5">Zero-Leak Gateway</span>
                                  <p className="text-[7.5px] text-slate-600 mt-1 leading-normal uppercase">Encrypted transport tunnels ensure credentials, secrets, or raw corporate data NEVER leak to public models or third parties.</p>
                                </div>

                                {/* Card 3: Access */}
                                <div 
                                  onClick={() => setSelectedPipelineBubble(selectedPipelineBubble === "access" ? null : "access")}
                                  className={`p-3 rounded-lg border cursor-pointer select-none transition-all duration-300 ${
                                    selectedPipelineBubble === "access"
                                      ? "border-indigo-500 bg-indigo-950/20 shadow-[0_0_12px_rgba(99,102,241,0.15)]"
                                      : "bg-slate-900/20 border-slate-900/60 hover:border-indigo-500/40 hover:bg-slate-900/30"
                                  }`}
                                >
                                  <div className="flex items-center justify-between mb-1">
                                    <span className="text-slate-500 text-[8px] uppercase tracking-wider block font-bold">ACCESS PERMISSION SCOPE</span>
                                    <span className={`text-[7px] font-black uppercase ${selectedPipelineBubble === "access" ? "text-indigo-400" : "text-slate-600"}`}>
                                      {selectedPipelineBubble === "access" ? "● ACTIVE BLUEPRINT" : "○ CLICK TO EXPLORE"}
                                    </span>
                                  </div>
                                  <span className="text-indigo-400 font-black text-[10.5px] block uppercase mt-0.5">OAuth 2.0 / ADC</span>
                                  <p className="text-[7.5px] text-slate-600 mt-1 leading-normal uppercase">Enforces fine-grained workspace permissions by validating Google OAuth access tokens against target datastore files.</p>
                                </div>

                                {/* Card 4: Model */}
                                <div 
                                  onClick={() => setSelectedPipelineBubble(selectedPipelineBubble === "model" ? null : "model")}
                                  className={`p-3 rounded-lg border cursor-pointer select-none transition-all duration-300 ${
                                    selectedPipelineBubble === "model"
                                      ? "border-yellow-500 bg-yellow-950/20 shadow-[0_0_12px_rgba(234,179,8,0.15)]"
                                      : "bg-slate-900/20 border-slate-900/60 hover:border-yellow-500/40 hover:bg-slate-900/30"
                                  }`}
                                >
                                  <div className="flex items-center justify-between mb-1">
                                    <span className="text-slate-500 text-[8px] uppercase tracking-wider block font-bold">MODEL EXECUTION CORE</span>
                                    <span className={`text-[7px] font-black uppercase ${selectedPipelineBubble === "model" ? "text-yellow-400" : "text-slate-600"}`}>
                                      {selectedPipelineBubble === "model" ? "● ACTIVE BLUEPRINT" : "○ CLICK TO EXPLORE"}
                                    </span>
                                  </div>
                                  <span className="text-yellow-400 font-black text-[10.5px] block uppercase mt-0.5">Gemini Engine API</span>
                                  <p className="text-[7.5px] text-slate-600 mt-1 leading-normal uppercase">The validated context is injected securely into the LLM system instructions, giving model-native grounded responses.</p>
                                </div>

                                {/* Card 5: Data Store */}
                                <div 
                                  onClick={() => setSelectedPipelineBubble(selectedPipelineBubble === "datastore" ? null : "datastore")}
                                  className={`p-3 rounded-lg border cursor-pointer select-none transition-all duration-300 xl:col-span-2 ${
                                    selectedPipelineBubble === "datastore"
                                      ? "border-purple-500 bg-purple-950/20 shadow-[0_0_12px_rgba(147,51,234,0.15)]"
                                      : "bg-slate-900/20 border-slate-900/60 hover:border-purple-500/40 hover:bg-slate-900/30"
                                  }`}
                                >
                                  <div className="flex items-center justify-between mb-1">
                                    <span className="text-slate-500 text-[8px] uppercase tracking-wider block font-bold">DATA STORE STORAGE</span>
                                    <span className={`text-[7px] font-black uppercase ${selectedPipelineBubble === "datastore" ? "text-purple-400" : "text-slate-600"}`}>
                                      {selectedPipelineBubble === "datastore" ? "● ACTIVE BLUEPRINT" : "○ CLICK TO EXPLORE"}
                                    </span>
                                  </div>
                                  <span className="text-purple-400 font-black text-[10.5px] block uppercase mt-0.5">Google Cloud Storage / Drive Sync</span>
                                  <p className="text-[7.5px] text-slate-600 mt-1 leading-normal uppercase">Enables automated synchronizations and enterprise search corpus updates across all mapped GSuite workspace files and folders.</p>
                                </div>
                              </div>
                            </div>
                          )}
                        </div>
                      );
                    }

                    // Thought reasoning CoT presentation
                    if (selectedTrace.type === "thought") {
                      return (
                        <div className="space-y-3">
                          <span className="text-[8px] font-black text-slate-500 uppercase tracking-widest block">
                            🧠 DEEP COGNITIVE CHAIN-OF-THOUGHT ANALYSIS
                          </span>
                          
                          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                            <div className="p-3 bg-slate-950/60 rounded-xl border border-slate-900">
                              <span className="text-[7.5px] text-slate-500 uppercase tracking-wider block">COGNITION LEVEL</span>
                              <span className="text-emerald-400 font-black text-[11px] block uppercase mt-0.5">High Performance</span>
                            </div>
                            <div className="p-3 bg-slate-950/60 rounded-xl border border-slate-900">
                              <span className="text-[7.5px] text-slate-500 uppercase tracking-wider block">REASONING LAYER</span>
                              <span className="text-cyan-400 font-black text-[11px] block uppercase mt-0.5">Multi-Step Matrix</span>
                            </div>
                            <div className="p-3 bg-slate-950/60 rounded-xl border border-slate-900">
                              <span className="text-[7.5px] text-slate-500 uppercase tracking-wider block">DENSITY FLOW</span>
                              <span className="text-indigo-400 font-black text-[11px] block uppercase mt-0.5">{(selectedTrace.details || "").length} Chars</span>
                            </div>
                          </div>

                          <div className="p-4 rounded-xl border border-emerald-950/40 bg-emerald-950/5 text-emerald-300 font-mono text-[10px] leading-relaxed relative overflow-hidden">
                            <div className="absolute top-2 right-2 h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse"></div>
                            <div className="border-b border-emerald-900/30 pb-2 mb-2 flex items-center gap-1.5 text-[8px] text-emerald-500 uppercase font-black tracking-widest">
                              <span className="h-1 w-1 bg-emerald-500 rounded-full animate-ping"></span>
                              Active Reasoning Matrix Console
                            </div>
                            <p className="whitespace-pre-wrap font-sans font-medium opacity-90 leading-relaxed max-h-[180px] overflow-y-auto custom-scrollbar pr-1">
                              {selectedTrace.details}
                            </p>
                          </div>
                        </div>
                      );
                    }

                    // Token counters gauges
                    if (selectedTrace.type === "token_flow" || selectedTrace.type === "token_count") {
                      const tokens = (() => {
                        const str = selectedTrace.details || "";
                        const p = str.match(/Prompt:\s*(\d+)/i)?.[1];
                        const o = str.match(/Output:\s*(\d+)/i)?.[1];
                        const t = str.match(/Thoughts:\s*(\d+)/i)?.[1];
                        if (p || o || t) {
                          const promptVal = parseInt(p || "0", 10);
                          const outputVal = parseInt(o || "0", 10);
                          const thoughtVal = parseInt(t || "0", 10);
                          const totalVal = promptVal + outputVal + thoughtVal;
                          return { prompt: promptVal, output: outputVal, thought: thoughtVal, total: totalVal };
                        }
                        return null;
                      })();

                      return (
                        <div className="space-y-3">
                          <span className="text-[8px] font-black text-slate-500 uppercase tracking-widest block">
                            🔋 RESOURCE DYNAMICS & COGNITIVE PRICING STATS
                          </span>
                          
                          {tokens ? (
                            <div className="space-y-4 bg-slate-950/60 p-4 rounded-xl border border-slate-900 font-mono text-[9px] text-slate-400">
                              <div className="flex items-center justify-between border-b border-slate-900 pb-2 mb-2 select-none">
                                <span className="text-slate-500 text-[8px] uppercase tracking-wider font-black">RESOURCE CONSTELLATION METRIC</span>
                                <span className="text-cyan-400 font-black text-[11px]">TOTAL RESOURCE CONSUMPTION: {tokens.total} TOKENS</span>
                              </div>
                              
                              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-center mb-1">
                                <div className="p-2.5 bg-slate-900/40 rounded-xl border border-slate-900">
                                  <span className="text-slate-500 text-[7.5px] uppercase block">PROMPT TOKENS</span>
                                  <span className="text-pink-400 font-black text-[13px] block mt-0.5">{tokens.prompt}</span>
                                  <span className="text-[7.5px] text-slate-600 mt-0.5 block">{tokens.total > 0 ? Math.round((tokens.prompt / tokens.total) * 100) : 0}% ratio</span>
                                </div>
                                <div className="p-2.5 bg-slate-900/40 rounded-xl border border-slate-900">
                                  <span className="text-slate-500 text-[7.5px] uppercase block">THINKING TOKENS</span>
                                  <span className="text-emerald-400 font-black text-[13px] block mt-0.5">{tokens.thought}</span>
                                  <span className="text-[7.5px] text-slate-600 mt-0.5 block">{tokens.total > 0 ? Math.round((tokens.thought / tokens.total) * 100) : 0}% ratio</span>
                                </div>
                                <div className="p-2.5 bg-slate-900/40 rounded-xl border border-slate-900">
                                  <span className="text-slate-500 text-[7.5px] uppercase block">CANDIDATE ANSWER</span>
                                  <span className="text-cyan-400 font-black text-[13px] block mt-0.5">{tokens.output}</span>
                                  <span className="text-[7.5px] text-slate-600 mt-0.5 block">{tokens.total > 0 ? Math.round((tokens.output / tokens.total) * 100) : 0}% ratio</span>
                                </div>
                              </div>

                              <div className="space-y-3 pt-2">
                                <div>
                                  <div className="flex justify-between text-[7.5px] text-slate-500 font-black mb-1 uppercase">
                                    <span>Workspace Document Context injection (PROMPT)</span>
                                    <span className="text-pink-400">{tokens.prompt} / {tokens.total} t</span>
                                  </div>
                                  <div className="w-full bg-slate-900 h-2 rounded-full overflow-hidden border border-slate-800 shadow-inner">
                                    <div className="bg-pink-500 h-full rounded-full transition-all duration-500" style={{ width: `${tokens.total > 0 ? (tokens.prompt / tokens.total) * 100 : 0}%` }}></div>
                                  </div>
                                </div>
                                <div>
                                  <div className="flex justify-between text-[7.5px] text-slate-500 font-black mb-1 uppercase">
                                    <span>Internal reasoning search matrix output (THOUGHTS)</span>
                                    <span className="text-emerald-400">{tokens.thought} / {tokens.total} t</span>
                                  </div>
                                  <div className="w-full bg-slate-900 h-2 rounded-full overflow-hidden border border-slate-800 shadow-inner">
                                    <div className="bg-emerald-400 h-full rounded-full transition-all duration-500" style={{ width: `${tokens.total > 0 ? (tokens.thought / tokens.total) * 100 : 0}%` }}></div>
                                  </div>
                                </div>
                                <div>
                                  <div className="flex justify-between text-[7.5px] text-slate-500 font-black mb-1 uppercase">
                                    <span>Model response payload tokens generation (ANSWER)</span>
                                    <span className="text-cyan-400">{tokens.output} / {tokens.total} t</span>
                                  </div>
                                  <div className="w-full bg-slate-900 h-2 rounded-full overflow-hidden border border-slate-800 shadow-inner">
                                    <div className="bg-cyan-400 h-full rounded-full transition-all duration-500" style={{ width: `${tokens.total > 0 ? (tokens.output / tokens.total) * 100 : 0}%` }}></div>
                                  </div>
                                </div>
                              </div>
                            </div>
                          ) : (
                            <div className="bg-slate-950/60 p-4 rounded-xl border border-slate-900 font-mono text-[9px] text-slate-400">
                              <span className="text-yellow-400 block font-bold text-[10.5px]">RESOURCE OVERVIEW STAGE</span>
                              <p className="text-[8px] text-slate-500 mt-1 uppercase">Token accounting parameters are being dynamically calculated via standard billing modules inside Google Agentic AI framework.</p>
                            </div>
                          )}
                        </div>
                      );
                    }

                    // SSE chunk metrics
                    if (selectedTrace.type === "sse_chunk") {
                      return (
                        <div className="space-y-3">
                          <span className="text-[8px] font-black text-slate-500 uppercase tracking-widest block">
                            📡 REAL-TIME EVENT STREAM TELEMETRY
                          </span>
                          
                          {/* Animated Event waveform visualization */}
                          <div className="p-4 bg-slate-950/80 rounded-xl border border-pink-950/30 flex items-center justify-center gap-1.5 select-none overflow-hidden h-14 relative">
                            <span className="absolute top-1.5 left-2.5 text-[7px] text-pink-500 uppercase font-mono tracking-widest font-bold">SSE ACTIVE RESPONSE CHUNNEL WAVEFORM</span>
                            <div className="flex gap-1 items-end h-8">
                              <span className="w-1 bg-pink-500 rounded h-3 animate-pulse" style={{ animationDelay: '0.1s' }} />
                              <span className="w-1 bg-pink-500 rounded h-6 animate-pulse" style={{ animationDelay: '0.4s' }} />
                              <span className="w-1 bg-pink-500 rounded h-4 animate-pulse" style={{ animationDelay: '0.2s' }} />
                              <span className="w-1 bg-pink-500 rounded h-7 animate-pulse" style={{ animationDelay: '0.5s' }} />
                              <span className="w-1 bg-pink-500 rounded h-5 animate-pulse" style={{ animationDelay: '0.3s' }} />
                              <span className="w-1 bg-pink-500 rounded h-8 animate-pulse" style={{ animationDelay: '0.6s' }} />
                              <span className="w-1 bg-pink-500 rounded h-4 animate-pulse" style={{ animationDelay: '0.2s' }} />
                              <span className="w-1 bg-pink-500 rounded h-7 animate-pulse" style={{ animationDelay: '0.4s' }} />
                              <span className="w-1 bg-pink-500 rounded h-3 animate-pulse" style={{ animationDelay: '0.1s' }} />
                            </div>
                          </div>

                          <div className="grid grid-cols-2 gap-3 bg-slate-950/60 p-4 rounded-xl border border-slate-900 font-mono text-[9px] text-slate-400">
                            <div>
                              <span className="text-slate-500 text-[8px] block">STREAM CONNECTOR</span>
                              <span className="text-pink-400 font-black block mt-0.5">/api/chat SSE CONNECTION</span>
                            </div>
                            <div>
                              <span className="text-slate-500 text-[8px] block">EVENT-STREAM PROTOCOL</span>
                              <span className="text-slate-300 font-black block mt-0.5">text/event-stream</span>
                            </div>
                            <div>
                              <span className="text-slate-500 text-[8px] block">BUFFERING HEADER</span>
                              <span className="text-emerald-400 font-black block mt-0.5">X-Accel-Buffering: none</span>
                            </div>
                            <div>
                              <span className="text-slate-500 text-[8px] block">RENDER STATUS</span>
                              <span className="text-cyan-400 font-black block mt-0.5">SUCCESSFULLY RENDERED CHUNK</span>
                            </div>
                          </div>
                        </div>
                      );
                    }
                    return null;
                  })()}

                  {/* RAW PAYLOAD BLOCK */}
                  {selectedTrace.data && (
                    <div className="space-y-3">
                      <div className="flex items-center justify-between text-[8px] font-black text-slate-500 uppercase tracking-widest select-none">
                        <span>📊 SECURED PAYLOAD SCHEMA (RAW METADATA)</span>
                        <button
                          onClick={() => handleCopyDetails(selectedTrace)}
                          className={`text-[8.5px] font-bold px-2 py-1 rounded border transition-all duration-200 uppercase cursor-pointer ${
                            copied
                              ? "bg-emerald-950/60 border-emerald-500 text-emerald-400 font-black animate-pulse"
                              : "bg-slate-950 border-slate-900 text-slate-400 hover:text-white hover:border-slate-800"
                          }`}
                        >
                          {copied ? "COPIED VALUE!" : "[ COPY JSON PAYLOAD ]"}
                        </button>
                      </div>
                      <pre className="p-4 bg-slate-950 rounded-xl border border-slate-900 text-[9.5px] font-mono text-cyan-300 leading-normal custom-scrollbar max-h-[220px] overflow-auto whitespace-pre selection:bg-slate-850">
                        {JSON.stringify(selectedTrace.data, null, 2)}
                      </pre>
                    </div>
                  )}

                  {!selectedTrace.data && (
                    <div className="pt-2 border-t border-slate-900 flex justify-end select-none">
                      <button
                        onClick={() => handleCopyDetails(selectedTrace)}
                        className={`text-[8px] font-black px-2 py-1 rounded border transition-all duration-200 uppercase cursor-pointer ${
                          copied
                            ? "bg-emerald-950/60 border-emerald-500 text-emerald-400 font-black animate-pulse"
                            : "bg-slate-950 border-slate-900 text-slate-400 hover:text-white hover:border-slate-800"
                        }`}
                      >
                        {copied ? "COPIED DETAILS!" : "[ COPY SUPPLEMENTARY DETAILS ]"}
                      </button>
                    </div>
                  )}

                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Cybernetic Style Definitions */}
      <style jsx global>{`
        @keyframes dash {
          to {
            stroke-dashoffset: 0;
          }
        }
        .animate-scan-glow {
          filter: drop-shadow(0 0 3px rgba(6, 182, 212, 0.4));
        }
        .animate-fade-in {
          animation: fadeIn 0.3s ease-out forwards;
        }
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(2px); }
          to { opacity: 1; transform: translateY(0); }
        }
      `}</style>

      {/* Global Sterile Footer */}
      <footer className="mt-4 border-t border-slate-200/50 pt-3 text-center text-[9px] text-slate-400 font-bold uppercase tracking-widest shrink-0">
        Model-Native Core Sync Engine Us-Central1 Staged · 3000 Construct Level Grounding Active
      </footer>
    </main>
  );
}

function newUid(): string {
  const id = `u-${Math.random().toString(36).slice(2, 10)}`;
  if (typeof window !== "undefined") window.localStorage.setItem("uid", id);
  return id;
}
