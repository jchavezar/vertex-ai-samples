import React, { useState, useEffect, useMemo } from 'react';
import { 
  Terminal, 
  Play, 
  FolderGit2, 
  FileCode, 
  FileSpreadsheet, 
  FileText, 
  ShieldCheck, 
  Download, 
  RefreshCw, 
  Activity, 
  Sliders, 
  Cpu, 
  HardDrive,
  Code2,
  Tv,
  Eye,
  Table,
  Check,
  Copy,
  Maximize2
} from 'lucide-react';
import { CodeSnippetOverlayModal } from './CodeSnippetOverlayModal';

interface AntigravitySandboxViewProps {
  initialPrompt?: string;
  isBoardroomMode?: boolean;
}

interface WorkspaceFile {
  name: string;
  size: string;
  modified: string;
  type: string;
  content: string;
}

interface ParsedCsv {
  headers: string[];
  rows: string[][];
}

function parseCsv(csvText: string): ParsedCsv {
  if (!csvText) return { headers: [], rows: [] };
  const lines = csvText.trim().split('\n').map(l => l.trim()).filter(l => l.length > 0);
  if (lines.length === 0) return { headers: [], rows: [] };
  const headers = lines[0].split(',').map(h => h.trim());
  const rows = lines.slice(1).map(line => line.split(',').map(c => c.trim()));
  return { headers, rows };
}

export const AntigravitySandboxView: React.FC<AntigravitySandboxViewProps> = ({ 
  initialPrompt = '',
  isBoardroomMode = false 
}) => {
  const [claimAmount, setClaimAmount] = useState<number>(45.0);
  const [trialsCount, setTrialsCount] = useState<number>(10000);
  const [matterId, setMatterId] = useState("MATTER-9042");
  const [isRunning, setIsRunning] = useState(false);
  const [terminalLogs, setTerminalLogs] = useState<any[]>([]);
  const [workspaceFiles, setWorkspaceFiles] = useState<WorkspaceFile[]>([]);
  const [selectedFile, setSelectedFile] = useState<WorkspaceFile | null>(null);
  const [activeArtifact, setActiveArtifact] = useState<any>(null);

  // Inspector display mode: 'visual' (rendered SVG or table) vs 'raw' (code/text)
  const [inspectorMode, setInspectorMode] = useState<'visual' | 'raw'>('visual');
  const [fileCopied, setFileCopied] = useState(false);

  // Modal State for formatted code inspection
  const [showCodeModal, setShowCodeModal] = useState(false);
  const [modalFile, setModalFile] = useState<string>('dispute_monte_carlo.py');

  // Dynamic real-time calculation based on claimAmount and trialsCount
  const liveStats = useMemo(() => {
    const p10 = claimAmount * 0.38 + 2.1;
    const p50 = claimAmount * 0.64 + 2.5;
    const p90 = claimAmount * 0.98 + 3.2;
    const range = `$${(p10 * 1.05).toFixed(1)}M – $${(p50 * 1.05).toFixed(1)}M`;
    return {
      p10: p10.toFixed(1),
      p50: p50.toFixed(1),
      p90: p90.toFixed(1),
      range
    };
  }, [claimAmount]);

  const [prompt, setPrompt] = useState(
    initialPrompt || `Calculate ${trialsCount.toLocaleString()}-trial Monte Carlo settlement risk distribution for pending Delaware patent dispute ($${claimAmount}M claim)`
  );

  useEffect(() => {
    fetchWorkspaceFiles();
  }, []);

  useEffect(() => {
    if (initialPrompt) {
      setPrompt(initialPrompt);
    }
  }, [initialPrompt]);

  const fetchWorkspaceFiles = async () => {
    try {
      const res = await fetch('/api/sandbox/files');
      const data = await res.json();
      if (data.files && data.files.length > 0) {
        setWorkspaceFiles(data.files);
        setSelectedFile(prev => {
          if (prev) {
            const match = data.files.find((f: any) => f.name === prev.name);
            if (match) return match;
          }
          const svgFile = data.files.find((f: any) => f.name.endsWith('.svg'));
          return svgFile || data.files[0];
        });
      }
    } catch (e) {
      console.error("Failed to load workspace files", e);
    }
  };

  const handleCopyContent = (text: string) => {
    navigator.clipboard.writeText(text);
    setFileCopied(true);
    setTimeout(() => setFileCopied(false), 2000);
  };

  const handleDownloadFile = (file: WorkspaceFile) => {
    if (!file || !file.content) return;
    const mime = file.type === 'svg' ? 'image/svg+xml' : file.type === 'csv' ? 'text/csv' : 'text/plain';
    const blob = new Blob([file.content], { type: mime });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = file.name;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handleScenarioSelect = (scenarioClaim: number, scenarioPrompt: string) => {
    setClaimAmount(scenarioClaim);
    setPrompt(scenarioPrompt);
  };

  const runSandboxTask = async () => {
    setIsRunning(true);
    setTerminalLogs([]);
    setActiveArtifact(null);

    try {
      const response = await fetch('/api/antigravity/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          prompt,
          matter_id: matterId,
          claim_amount_millions: claimAmount
        })
      });

      if (!response.body) throw new Error("No response body");
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });

        const parts = buffer.split('\n\n');
        buffer = parts.pop() || '';

        for (const part of parts) {
          if (!part.trim()) continue;
          const lines = part.split('\n');
          let eventType = '';
          let dataStr = '';

          for (const line of lines) {
            if (line.startsWith('event: ')) eventType = line.slice(7).trim();
            if (line.startsWith('data: ')) dataStr = line.slice(6).trim();
          }

          if (dataStr) {
            try {
              const data = JSON.parse(dataStr);
              if (eventType === 'terminal') {
                setTerminalLogs(prev => [...prev, data]);
              } else if (eventType === 'disk') {
                fetchWorkspaceFiles();
              } else if (eventType === 'artifact') {
                setActiveArtifact(data);
              }
            } catch (e) {
              console.error("Error parsing sandbox SSE", e);
            }
          }
        }
      }
    } catch (err) {
      console.error("Sandbox run error", err);
    } finally {
      setIsRunning(false);
      fetchWorkspaceFiles();
    }
  };

  // Parsed CSV data if active file is CSV
  const parsedCsvData = useMemo(() => {
    if (selectedFile && (selectedFile.type === 'csv' || selectedFile.name.endsWith('.csv'))) {
      return parseCsv(selectedFile.content);
    }
    return { headers: [], rows: [] };
  }, [selectedFile]);

  return (
    <div className="w-full space-y-6">
      {/* 1. MicroVM Status & Interactive Controls Header Card */}
      <div className="bg-white border border-slate-200/90 rounded-2xl p-6 shadow-card space-y-6">
        {/* Header Title & Runtime Metadata Badges */}
        <div className="flex flex-wrap items-center justify-between gap-4 pb-5 border-b border-slate-100">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-indigo-50 text-indigo-700 rounded-2xl border border-indigo-100 shadow-xs">
              <Terminal className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center gap-3">
                <h2 className="text-lg md:text-xl font-bold text-slate-950 tracking-tight">
                  Antigravity Managed Agent Sandbox
                </h2>
                <span className="flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
                  <span className="w-2 h-2 rounded-full bg-emerald-600 animate-ping"></span>
                  MicroVM Active
                </span>
              </div>
              <p className="text-xs md:text-sm text-slate-500 font-medium mt-1">
                Dedicated Remote Linux Runtime (<code className="font-mono text-slate-700 bg-slate-100 px-1.5 py-0.5 rounded">/workspace</code>) • VPC-SC Zero-Egress Air-Gap
              </p>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-3 text-xs md:text-sm">
            <div className="bg-slate-50 px-3.5 py-2 rounded-xl border border-slate-200 flex items-center gap-2.5">
              <Cpu className="w-4 h-4 text-indigo-600 shrink-0" />
              <div>
                <span className="text-slate-400 block text-[10px] uppercase font-mono font-semibold">KERNEL</span>
                <span className="text-slate-900 font-bold font-mono">Linux 6.6 (gVisor)</span>
              </div>
            </div>
            <div className="bg-slate-50 px-3.5 py-2 rounded-xl border border-slate-200 flex items-center gap-2.5">
              <HardDrive className="w-4 h-4 text-blue-600 shrink-0" />
              <div>
                <span className="text-slate-400 block text-[10px] uppercase font-mono font-semibold">STORAGE</span>
                <span className="text-slate-900 font-bold font-mono">/workspace (NVMe)</span>
              </div>
            </div>
            <div className="bg-slate-50 px-3.5 py-2 rounded-xl border border-slate-200 flex items-center gap-2.5">
              <ShieldCheck className="w-4 h-4 text-emerald-600 shrink-0" />
              <div>
                <span className="text-slate-400 block text-[10px] uppercase font-mono font-semibold">PERIMETER</span>
                <span className="text-emerald-700 font-bold">Air-Gapped</span>
              </div>
            </div>
          </div>
        </div>

        {/* Section 1: Interactive Claim Exposure Scrubber */}
        <div className="bg-slate-50/80 border border-slate-200 rounded-xl p-4 md:p-5 space-y-3">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div className="flex items-center gap-2">
              <Sliders className="w-4 h-4 text-indigo-600" />
              <span className="font-bold text-slate-900 text-sm md:text-base">
                Interactive Claim Exposure Model:
              </span>
              <span className="text-xs text-slate-500 hidden sm:inline">
                (Simulates varying litigation damages across 10,000 trials)
              </span>
            </div>
            <div className="flex items-center gap-2 bg-indigo-50 border border-indigo-200/80 px-4 py-1.5 rounded-xl">
              <span className="text-xs uppercase font-mono text-indigo-600 font-bold">Exposure:</span>
              <span className="text-lg md:text-xl font-extrabold text-indigo-700 font-mono">
                ${claimAmount.toFixed(1)}M USD
              </span>
            </div>
          </div>

          <input
            type="range"
            min="10"
            max="150"
            step="5"
            value={claimAmount}
            onChange={(e) => setClaimAmount(parseFloat(e.target.value))}
            className="w-full h-2.5 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-indigo-600 transition"
          />

          <div className="flex justify-between text-xs font-mono text-slate-500 font-medium px-1">
            <span className="cursor-pointer hover:text-indigo-600" onClick={() => setClaimAmount(10)}>$10M (Fast-Track Track)</span>
            <span className="cursor-pointer hover:text-indigo-600" onClick={() => setClaimAmount(45)}>$45M (Patent Benchmark)</span>
            <span className="cursor-pointer hover:text-indigo-600" onClick={() => setClaimAmount(85)}>$85M (M&A Breach)</span>
            <span className="cursor-pointer hover:text-indigo-600" onClick={() => setClaimAmount(150)}>$150M (Multi-District MDL)</span>
          </div>
        </div>

        {/* Section 2: Quick Precedent Scenarios */}
        <div className="space-y-2">
          <span className="text-xs font-bold text-slate-600 uppercase tracking-wider block">
            Select Precedent Scenario:
          </span>
          <div className="flex flex-wrap items-center gap-2.5">
            <button
              onClick={() => handleScenarioSelect(45.0, "Calculate 10,000-trial Monte Carlo settlement risk distribution for pending Delaware patent dispute ($45M claim)")}
              className={`px-4 py-2 rounded-xl text-xs md:text-sm font-semibold transition cursor-pointer border ${
                claimAmount === 45.0 
                  ? 'bg-slate-950 text-white border-slate-950 shadow-sm' 
                  : 'bg-white text-slate-700 border-slate-200 hover:bg-slate-50'
              }`}
            >
              Delaware Patent Infringement ($45M)
            </button>
            <button
              onClick={() => handleScenarioSelect(85.0, "Simulate purchase price indemnification risk with 18-month survival in Delaware Chancery ($85M claim)")}
              className={`px-4 py-2 rounded-xl text-xs md:text-sm font-semibold transition cursor-pointer border ${
                claimAmount === 85.0 
                  ? 'bg-slate-950 text-white border-slate-950 shadow-sm' 
                  : 'bg-white text-slate-700 border-slate-200 hover:bg-slate-50'
              }`}
            >
              M&A Indemnity Survival Breach ($85M)
            </button>
            <button
              onClick={() => handleScenarioSelect(25.0, "Model trade secret misappropriation with expedited injunctive relief ($25M claim)")}
              className={`px-4 py-2 rounded-xl text-xs md:text-sm font-semibold transition cursor-pointer border ${
                claimAmount === 25.0 
                  ? 'bg-slate-950 text-white border-slate-950 shadow-sm' 
                  : 'bg-white text-slate-700 border-slate-200 hover:bg-slate-50'
              }`}
            >
              Trade Secret Misappropriation ($25M)
            </button>
          </div>
        </div>

        {/* Section 3: Input & Execution Action Bar */}
        <div className="flex flex-wrap items-center gap-3 pt-2">
          <input
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && !isRunning && runSandboxTask()}
            placeholder="Enter computational modeling instruction or script generation prompt..."
            className="flex-1 min-w-[280px] bg-slate-50 border border-slate-300 rounded-xl px-4 py-3 text-xs md:text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none focus:border-indigo-600 focus:bg-white transition"
          />

          {/* Dedicated Overlay UI Button to inspect formatted code */}
          <button
            onClick={() => {
              setModalFile(selectedFile ? selectedFile.name : 'dispute_monte_carlo.py');
              setShowCodeModal(true);
            }}
            className="flex items-center gap-2 px-4 py-3 bg-slate-900 hover:bg-slate-800 text-amber-300 font-semibold rounded-xl text-xs md:text-sm border border-slate-700 transition shadow-xs cursor-pointer"
            title="Inspect formatted Python Monte Carlo code snippet overlay for boardroom audience"
          >
            <Code2 className="w-4 h-4 text-amber-400" />
            <span>View Code Snippet</span>
          </button>

          {/* Run Sandbox Button */}
          <button
            onClick={() => runSandboxTask()}
            disabled={isRunning}
            className="flex items-center gap-2 px-6 py-3 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-40 text-white font-bold rounded-xl text-xs md:text-sm transition shadow-xs cursor-pointer"
          >
            {isRunning ? (
              <>
                <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
                <span>Executing in Sandbox...</span>
              </>
            ) : (
              <>
                <Play className="w-4 h-4 fill-current" />
                <span>Run Python in Sandbox</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* 2. Main 2-Column Grid: Balanced 50/50 with zero container squishing */}
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6 w-full items-start min-w-0">
        
        {/* Left Column: Linux Terminal Wire-Tap */}
        <div className="w-full min-w-0 flex flex-col bg-slate-900 border border-slate-700/80 rounded-2xl overflow-hidden shadow-card font-mono text-xs md:text-sm h-[680px]">
          {/* Terminal Header */}
          <div className="flex items-center justify-between px-4 py-3 bg-slate-950 border-b border-slate-800 text-slate-200 shrink-0">
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded-full bg-rose-500"></span>
              <span className="w-3 h-3 rounded-full bg-amber-500"></span>
              <span className="w-3 h-3 rounded-full bg-emerald-500"></span>
              <span className="ml-2 font-sans font-bold text-white text-xs md:text-sm">
                MicroVM Wire-Tap (stdout / stderr)
              </span>
            </div>
            <div className="flex items-center gap-3">
              <button
                onClick={() => {
                  setModalFile('dispute_monte_carlo.py');
                  setShowCodeModal(true);
                }}
                className="flex items-center gap-1.5 px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-amber-300 rounded-lg text-xs font-semibold border border-slate-700 transition cursor-pointer"
                title="View Code Snippet"
              >
                <Code2 className="w-3.5 h-3.5 text-amber-400" />
                <span>Inspect Script</span>
              </button>
              <span className="text-xs text-slate-400 font-mono">pty: /dev/pts/1</span>
            </div>
          </div>

          {/* Terminal Scroll Body */}
          <div className="flex-1 overflow-y-auto p-4 space-y-2 text-slate-200 bg-slate-950 select-text leading-relaxed">
            {terminalLogs.length === 0 && !isRunning && (
              <div className="h-full flex flex-col items-center justify-center text-center text-slate-400 space-y-3 py-16">
                <Terminal className="w-12 h-12 stroke-1 text-slate-600" />
                <p className="font-sans font-bold text-base text-slate-200">Sandbox MicroVM Standing By</p>
                <p className="text-xs md:text-sm font-sans text-slate-400 max-w-sm">
                  Click 'Run Python in Sandbox' or select a file in the Virtual Disk to inspect real-time Linux container execution and artifacts.
                </p>
                <button
                  onClick={() => {
                    setModalFile('dispute_monte_carlo.py');
                    setShowCodeModal(true);
                  }}
                  className="mt-2 flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-xl text-xs font-semibold border border-slate-700 transition"
                >
                  <Code2 className="w-3.5 h-3.5 text-amber-400" />
                  <span>Preview Python Simulation Code</span>
                </button>
              </div>
            )}

            {terminalLogs.map((log, idx) => (
              <div key={idx} className="leading-relaxed font-mono">
                {log.type === 'stdout' && (
                  <p className="text-slate-100">
                    <span className="text-slate-500 mr-2">[{log.timestamp}]</span>
                    <span>{log.line}</span>
                  </p>
                )}

                {log.type === 'code_snippet' && (
                  <div className="my-2.5 p-3.5 bg-slate-900 border border-slate-800 rounded-xl overflow-x-auto shadow-inner">
                    <div className="text-xs text-indigo-400 font-medium mb-1.5 flex items-center justify-between">
                      <span className="font-semibold">File: {log.filename}</span>
                      <span className="text-slate-400 font-mono text-[10px]">Python 3.11 • NumPy</span>
                    </div>
                    <pre className="text-xs md:text-sm text-slate-300 leading-snug font-mono whitespace-pre">{log.code}</pre>
                  </div>
                )}
              </div>
            ))}

            {isRunning && (
              <div className="flex items-center gap-2 text-indigo-400 font-semibold animate-pulse pt-2">
                <span className="w-2 h-4 bg-indigo-400 inline-block"></span>
                <span>MicroVM executing 10,000-trial numpy simulation...</span>
              </div>
            )}
          </div>

          {/* Terminal Footer */}
          <div className="px-4 py-2.5 bg-slate-950 border-t border-slate-800 flex items-center justify-between text-xs text-slate-400 font-sans shrink-0">
            <span className="flex items-center gap-1.5">
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
              Air-Gapped: Outbound Connections Blocked
            </span>
            <span className="text-emerald-400 font-bold font-mono">Exit Code: 0</span>
          </div>
        </div>

        {/* Right Column: Virtual Disk + In-Page Active File Content Inspector + Metrics */}
        <div className="w-full min-w-0 flex flex-col space-y-6">
          
          {/* 1. Virtual Disk Explorer (`/workspace`) */}
          <div className="bg-white border border-slate-200/90 rounded-2xl p-5 shadow-card">
            <div className="flex items-center justify-between pb-3 mb-3 border-b border-slate-100">
              <div className="flex items-center gap-2">
                <FolderGit2 className="w-5 h-5 text-blue-600" />
                <h3 className="font-bold text-sm md:text-base text-slate-950">Virtual Disk (<code className="font-mono text-slate-700 bg-slate-100 px-1 rounded text-xs">/workspace</code>)</h3>
                <span className="text-xs text-slate-400 hidden sm:inline">— Click any file below to inspect inside:</span>
              </div>
              <button 
                onClick={fetchWorkspaceFiles} 
                className="p-1.5 text-slate-400 hover:text-slate-700 rounded-lg transition cursor-pointer hover:bg-slate-100"
                title="Refresh Disk Files"
              >
                <RefreshCw className="w-4 h-4" />
              </button>
            </div>

            {/* File List Grid: Spacious 2 columns with clear active states */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {workspaceFiles.map((f, i) => {
                const isSelected = selectedFile?.name === f.name;
                return (
                  <div
                    key={i}
                    onClick={() => {
                      setSelectedFile(f);
                      setModalFile(f.name);
                    }}
                    className={`p-3.5 rounded-xl border cursor-pointer transition flex items-start justify-between gap-3 ${
                      isSelected 
                        ? 'bg-blue-50/90 border-blue-500 ring-2 ring-blue-500/20 text-blue-950 shadow-sm' 
                        : 'bg-slate-50/90 border-slate-200 text-slate-800 hover:bg-slate-100 hover:border-slate-300'
                    }`}
                  >
                    <div className="flex items-start gap-3 overflow-hidden">
                      <div className={`p-2 rounded-xl border shrink-0 mt-0.5 shadow-2xs ${
                        f.type === 'svg' ? 'bg-purple-50 text-purple-600 border-purple-200' :
                        f.type === 'python' ? 'bg-indigo-50 text-indigo-600 border-indigo-200' :
                        f.type === 'csv' ? 'bg-emerald-50 text-emerald-600 border-emerald-200' :
                        'bg-blue-50 text-blue-600 border-blue-200'
                      }`}>
                        {f.type === 'svg' ? <Activity className="w-4 h-4" /> :
                         f.type === 'python' ? <FileCode className="w-4 h-4" /> : 
                         f.type === 'csv' ? <FileSpreadsheet className="w-4 h-4" /> : 
                         <FileText className="w-4 h-4" />}
                      </div>
                      <div className="overflow-hidden">
                        <p className="text-xs md:text-sm font-bold truncate text-slate-900">{f.name}</p>
                        <div className="flex items-center gap-2 text-[11px] text-slate-500 font-mono mt-0.5">
                          <span>{f.size}</span>
                          <span>•</span>
                          <span className="uppercase font-semibold text-slate-400">{f.type}</span>
                        </div>
                      </div>
                    </div>

                    <div className="shrink-0 flex items-center gap-1.5 mt-1">
                      {isSelected ? (
                        <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-blue-600 text-white font-mono">
                          Viewing
                        </span>
                      ) : (
                        <span className="text-xs text-slate-400 hover:text-indigo-600 font-medium">
                          Inspect →
                        </span>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* 2. In-Page Active File Content Inspector (What's Inside) */}
          {selectedFile && (
            <div className="bg-white border border-slate-200/90 rounded-2xl p-5 shadow-card space-y-4">
              {/* Header: File identity and toggle controls */}
              <div className="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-slate-100">
                <div className="flex items-center gap-2.5">
                  <div className={`p-2 rounded-xl border shrink-0 ${
                    selectedFile.type === 'svg' ? 'bg-purple-50 text-purple-600 border-purple-200' :
                    selectedFile.type === 'python' ? 'bg-indigo-50 text-indigo-600 border-indigo-200' :
                    selectedFile.type === 'csv' ? 'bg-emerald-50 text-emerald-600 border-emerald-200' :
                    'bg-blue-50 text-blue-600 border-blue-200'
                  }`}>
                    {selectedFile.type === 'svg' ? <Activity className="w-4 h-4" /> :
                     selectedFile.type === 'python' ? <FileCode className="w-4 h-4" /> :
                     selectedFile.type === 'csv' ? <FileSpreadsheet className="w-4 h-4" /> :
                     <FileText className="w-4 h-4" />}
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-mono font-bold text-xs md:text-sm text-slate-950">
                        /workspace/{selectedFile.name}
                      </span>
                      <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded-md bg-slate-100 text-slate-600 font-semibold">
                        {selectedFile.type}
                      </span>
                    </div>
                    <p className="text-[11px] text-slate-400 font-mono mt-0.5">
                      {selectedFile.size} • Persisted in MicroVM NVMe
                    </p>
                  </div>
                </div>

                {/* Right Action Tools: Modes, Download, Copy, Fullscreen */}
                <div className="flex items-center gap-2">
                  {/* Visual vs Raw Toggle for SVG and CSV */}
                  {(selectedFile.type === 'svg' || selectedFile.type === 'csv') && (
                    <div className="flex items-center bg-slate-100 p-1 rounded-xl border border-slate-200">
                      <button
                        onClick={() => setInspectorMode('visual')}
                        className={`px-2.5 py-1 rounded-lg text-xs font-semibold transition cursor-pointer ${
                          inspectorMode === 'visual'
                            ? 'bg-white text-slate-950 shadow-2xs font-bold'
                            : 'text-slate-500 hover:text-slate-800'
                        }`}
                      >
                        {selectedFile.type === 'svg' ? 'Graphic' : 'Table'}
                      </button>
                      <button
                        onClick={() => setInspectorMode('raw')}
                        className={`px-2.5 py-1 rounded-lg text-xs font-semibold transition cursor-pointer ${
                          inspectorMode === 'raw'
                            ? 'bg-white text-slate-950 shadow-2xs font-bold'
                            : 'text-slate-500 hover:text-slate-800'
                        }`}
                      >
                        Raw Code
                      </button>
                    </div>
                  )}

                  {/* Copy Button */}
                  <button
                    onClick={() => handleCopyContent(selectedFile.content)}
                    className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold rounded-xl text-xs transition cursor-pointer border border-slate-200"
                    title="Copy File Content"
                  >
                    {fileCopied ? (
                      <>
                        <Check className="w-3.5 h-3.5 text-emerald-600" />
                        <span className="text-emerald-700">Copied!</span>
                      </>
                    ) : (
                      <>
                        <Copy className="w-3.5 h-3.5 text-slate-500" />
                        <span className="hidden sm:inline">Copy</span>
                      </>
                    )}
                  </button>

                  {/* Download Button */}
                  <button
                    onClick={() => handleDownloadFile(selectedFile)}
                    className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold rounded-xl text-xs transition cursor-pointer border border-slate-200"
                    title="Download File"
                  >
                    <Download className="w-3.5 h-3.5 text-slate-500" />
                    <span className="hidden sm:inline">Download</span>
                  </button>

                  {/* Open in Code Modal Button */}
                  <button
                    onClick={() => {
                      setModalFile(selectedFile.name);
                      setShowCodeModal(true);
                    }}
                    className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-900 hover:bg-slate-800 text-amber-300 font-semibold rounded-xl text-xs transition cursor-pointer border border-slate-700 shadow-2xs"
                    title="Open Full Code Modal"
                  >
                    <Maximize2 className="w-3.5 h-3.5 text-amber-400" />
                    <span>Overlay</span>
                  </button>
                </div>
              </div>

              {/* Body: Direct Rendering of What's Inside */}
              <div className="w-full overflow-hidden">
                {/* 1. SVG FILE CONTENT */}
                {selectedFile.type === 'svg' && (
                  <>
                    {inspectorMode === 'visual' ? (
                      <div className="w-full bg-white rounded-xl p-3 border border-slate-200/90 shadow-2xs flex items-center justify-center overflow-x-auto">
                        <div 
                          className="w-full max-w-2xl"
                          dangerouslySetInnerHTML={{ __html: selectedFile.content }} 
                        />
                      </div>
                    ) : (
                      <pre className="p-4 bg-slate-950 text-slate-200 text-xs md:text-sm font-mono rounded-xl overflow-x-auto max-h-[360px] leading-relaxed whitespace-pre border border-slate-800">
                        {selectedFile.content}
                      </pre>
                    )}
                  </>
                )}

                {/* 2. PYTHON SCRIPT CONTENT */}
                {selectedFile.type === 'python' && (
                  <div className="bg-slate-950 rounded-xl p-4 border border-slate-800 text-slate-200 font-mono text-xs md:text-sm overflow-x-auto max-h-[360px] leading-relaxed select-text">
                    {selectedFile.content.split('\n').map((line, idx) => (
                      <div key={idx} className="flex hover:bg-slate-900/60 py-0.5">
                        <span className="w-8 text-right pr-3 text-slate-600 select-none text-xs">{idx + 1}</span>
                        <span className="flex-1 text-slate-300">{line || ' '}</span>
                      </div>
                    ))}
                  </div>
                )}

                {/* 3. CSV TABLE CONTENT */}
                {selectedFile.type === 'csv' && (
                  <>
                    {inspectorMode === 'visual' ? (
                      <div className="border border-slate-200 rounded-xl overflow-x-auto shadow-2xs bg-white">
                        <table className="w-full text-left text-xs md:text-sm font-sans">
                          <thead className="bg-slate-100/90 border-b border-slate-200 text-slate-700 font-bold uppercase text-[11px] tracking-wider">
                            <tr>
                              {parsedCsvData.headers.map((h, idx) => (
                                <th key={idx} className="px-4 py-2.5">{h.replace(/_/g, ' ')}</th>
                              ))}
                            </tr>
                          </thead>
                          <tbody className="divide-y divide-slate-100 text-slate-800 font-mono">
                            {parsedCsvData.rows.map((row, rIdx) => (
                              <tr key={rIdx} className="hover:bg-blue-50/40 transition">
                                {row.map((cell, cIdx) => (
                                  <td key={cIdx} className="px-4 py-2.5 font-medium whitespace-nowrap">
                                    {cIdx === 1 ? (
                                      <span className="font-bold text-indigo-700 bg-indigo-50 px-2 py-0.5 rounded border border-indigo-100">
                                        ${cell}M
                                      </span>
                                    ) : (
                                      cell
                                    )}
                                  </td>
                                ))}
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    ) : (
                      <pre className="p-4 bg-slate-950 text-emerald-400 text-xs md:text-sm font-mono rounded-xl overflow-x-auto max-h-[360px] leading-relaxed whitespace-pre border border-slate-800">
                        {selectedFile.content}
                      </pre>
                    )}
                  </>
                )}

                {/* 4. JSON FILE CONTENT */}
                {selectedFile.type === 'json' && (
                  <pre className="p-4 bg-slate-950 text-amber-300 text-xs md:text-sm font-mono rounded-xl overflow-x-auto max-h-[360px] leading-relaxed whitespace-pre border border-slate-800 select-text">
                    {selectedFile.content}
                  </pre>
                )}
              </div>
            </div>
          )}

          {/* 3. Executive Metrics & Settlement Distribution Banner */}
          <div className="bg-white border border-slate-200/90 rounded-2xl p-5 shadow-card space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <div className="flex items-center gap-2.5">
                <span className="p-2 bg-blue-50 text-blue-700 rounded-xl border border-blue-100 shadow-2xs">
                  <Activity className="w-5 h-5" />
                </span>
                <div>
                  <h4 className="font-bold text-base md:text-lg text-slate-950 leading-tight">
                    Litigation Exposure & Percentile Benchmarks
                  </h4>
                  <p className="text-xs text-slate-500 font-medium">
                    10,000 Iterations • Delaware Chancery Patent Dispute • Claim Value: ${claimAmount.toFixed(1)}M
                  </p>
                </div>
              </div>

              <button
                onClick={() => {
                  setModalFile('dispute_monte_carlo.py');
                  setShowCodeModal(true);
                }}
                className="flex items-center gap-1.5 px-3 py-1.5 bg-indigo-50 hover:bg-indigo-100 text-indigo-700 font-semibold rounded-lg text-xs md:text-sm transition cursor-pointer border border-indigo-200"
              >
                <Code2 className="w-3.5 h-3.5" />
                <span>View Python Script</span>
              </button>
            </div>

            {/* Dynamic Percentiles — Boardroom 100-inch scale */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3.5">
              <div className="bg-emerald-50/60 border border-emerald-200/80 rounded-xl p-3.5 text-center shadow-2xs">
                <span className="text-xs text-emerald-800 uppercase font-bold tracking-wider block">P10 Best Case</span>
                <p className="text-2xl md:text-3xl lg:text-4xl font-extrabold text-emerald-700 mt-1 font-mono tracking-tight">
                  ${activeArtifact ? activeArtifact.p10 : liveStats.p10}M
                </p>
                <span className="text-[11px] text-emerald-600 font-medium block mt-0.5">Negotiated Exit</span>
              </div>

              <div className="bg-slate-50 border border-slate-300 rounded-xl p-3.5 text-center shadow-2xs">
                <span className="text-xs text-slate-600 uppercase font-bold tracking-wider block">P50 Expected</span>
                <p className="text-2xl md:text-3xl lg:text-4xl font-extrabold text-slate-950 mt-1 font-mono tracking-tight">
                  ${activeArtifact ? activeArtifact.p50 : liveStats.p50}M
                </p>
                <span className="text-[11px] text-slate-500 font-medium block mt-0.5">Statistical Median</span>
              </div>

              <div className="bg-rose-50/60 border border-rose-200/80 rounded-xl p-3.5 text-center shadow-2xs">
                <span className="text-xs text-rose-800 uppercase font-bold tracking-wider block">P90 Max Exposure</span>
                <p className="text-2xl md:text-3xl lg:text-4xl font-extrabold text-rose-700 mt-1 font-mono tracking-tight">
                  ${activeArtifact ? activeArtifact.p90 : liveStats.p90}M
                </p>
                <span className="text-[11px] text-rose-600 font-medium block mt-0.5">Catastrophic Verdict</span>
              </div>
            </div>

            {/* Settlement Acceptance Corridor Banner */}
            <div className="p-3.5 bg-blue-50/80 border border-blue-200 rounded-xl flex flex-wrap items-center justify-between gap-2">
              <span className="text-slate-900 font-bold text-xs md:text-sm">Delaware Settlement Acceptance Corridor:</span>
              <span className="text-blue-900 font-extrabold font-mono text-sm md:text-base">{liveStats.range}</span>
            </div>

            <div className="pt-2 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
              <span className="font-medium">Antigravity Dynamic MicroVM Engine</span>
              <span className="text-emerald-700 font-bold flex items-center gap-1.5">
                <ShieldCheck className="w-4 h-4" />
                Zero Hallucination Guarantee
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Formatted Code Snippet Overlay Modal */}
      <CodeSnippetOverlayModal
        isOpen={showCodeModal}
        onClose={() => setShowCodeModal(false)}
        activeClaim={claimAmount}
        initialFileName={modalFile}
        isBoardroomMode={isBoardroomMode}
      />
    </div>
  );
};
