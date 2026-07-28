import React, { useState } from 'react';
import { ChatMessage, GcpErrorItem, CloudAssistDiagnostic } from '../../types';
import { RichTextRenderer } from '../RichTextRenderer';
import {
  X,
  Maximize2,
  Minimize2,
  Search,
  Sparkles,
  Bot,
  User,
  ExternalLink,
  Globe,
  Zap,
  Network,
  CheckCircle2,
  AlertTriangle,
  Layers,
  FileText,
  Terminal,
  Cpu,
  ArrowRight
} from 'lucide-react';

interface AnalyticalChatOverlayProps {
  isOpen: boolean;
  onClose: () => void;
  messages: ChatMessage[];
  selectedError: GcpErrorItem | null;
  diagnostic: CloudAssistDiagnostic | null;
  onSendMessage: (text: string) => void;
  onRunSandboxCommand?: (cmd: string) => void;
  isLightMode?: boolean;
}

export const AnalyticalChatOverlay: React.FC<AnalyticalChatOverlayProps> = ({
  isOpen,
  onClose,
  messages,
  selectedError,
  diagnostic,
  onSendMessage,
  onRunSandboxCommand,
  isLightMode = false
}) => {
  const [filterQuery, setFilterQuery] = useState('');
  const [activeMindmapNode, setActiveMindmapNode] = useState<string>('root-cause');

  if (!isOpen) return null;

  const topHypothesis = diagnostic?.hypotheses && diagnostic.hypotheses.length > 0 ? diagnostic.hypotheses[0] : null;

  const filteredMessages = messages.filter((m) =>
    m.text.toLowerCase().includes(filterQuery.toLowerCase())
  );

  const serviceName = selectedError?.serviceName || 'GCP Cloud Run Service';
  const summary = selectedError?.summary || 'IAM Policy / Resource Allocation Failure';
  const rootCause = topHypothesis?.rootCauseText || 'Runtime environment variable missing or heap limit exceeded.';
  const remediation = topHypothesis?.recommendationText || 'Run automated gcloud service update to apply missing credentials.';

  const mindmapNodes = [
    {
      id: 'entrypoint',
      title: 'HTTP 500 Entrypoint',
      subtitle: serviceName,
      status: 'CRITICAL',
      color: 'border-rose-500 bg-rose-950/40 text-rose-300',
      description: `Container ingress endpoint failed with status 500. Log trace indicates unhandled runtime exception.`
    },
    {
      id: 'root-cause',
      title: 'Root Cause Anomaly',
      subtitle: summary.substring(0, 35) + '...',
      status: 'DIAGNOSED',
      color: 'border-amber-500 bg-amber-950/40 text-amber-300',
      description: rootCause
    },
    {
      id: 'remediation',
      title: 'ADK Auto-Healing Patch',
      subtitle: 'gcloud CLI Patching Harness',
      status: 'VERIFIED',
      color: 'border-cyan-500 bg-cyan-950/40 text-cyan-300',
      description: remediation
    },
    {
      id: 'audit',
      title: 'Audit Verification',
      subtitle: 'GCP Cloud Trail Log',
      status: 'STABILIZED',
      color: 'border-emerald-500 bg-emerald-950/40 text-emerald-300',
      description: 'System equilibrium restored. All readiness/liveness probes returning HTTP 200 OK.'
    }
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/90 backdrop-blur-xl animate-fade-in font-sans">
      <div className={`w-full h-full max-w-7xl max-h-[92vh] rounded-3xl border-2 flex flex-col shadow-2xl overflow-hidden ${
        isLightMode
          ? 'bg-white border-slate-300 text-slate-950'
          : 'bg-[#0a0d14] border-slate-800 text-slate-100'
      }`}>
        {/* Top Header */}
        <div className={`px-6 py-4 border-b flex items-center justify-between ${
          isLightMode ? 'bg-slate-100 border-slate-200' : 'bg-slate-950 border-slate-800'
        }`}>
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-2xl bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center text-white shadow-lg shadow-cyan-500/20">
              <Network className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h2 className="text-base font-black tracking-tight uppercase font-mono">
                  Executive Analytical Workspace & Mindmap Engine
                </h2>
                <span className="text-[10px] font-mono font-bold px-2.5 py-0.5 rounded-full bg-cyan-500/20 border border-cyan-500/40 text-cyan-300">
                  gemini-3.5-flash
                </span>
              </div>
              <p className="text-xs text-slate-400 font-mono">
                Interactive Root Cause Mindmap • Conciseness Analysis • Dynamic Investigation Chips
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-3">
            <div className="relative flex items-center">
              <Search className="w-3.5 h-3.5 absolute left-3 text-slate-400" />
              <input
                type="text"
                value={filterQuery}
                onChange={(e) => setFilterQuery(e.target.value)}
                placeholder="Filter chat history..."
                className={`pl-8 pr-3 py-1.5 rounded-xl border text-xs font-mono focus:outline-none w-56 ${
                  isLightMode
                    ? 'bg-white border-slate-300 text-slate-900 placeholder-slate-400'
                    : 'bg-slate-900 border-slate-800 text-slate-200 placeholder-slate-500'
                }`}
              />
            </div>

            <button
              onClick={onClose}
              className={`p-2 rounded-xl border transition-colors cursor-pointer ${
                isLightMode
                  ? 'bg-slate-200 hover:bg-slate-300 border-slate-300 text-slate-900'
                  : 'bg-slate-900 hover:bg-slate-800 border-slate-700 text-slate-300'
              }`}
              title="Close Analytical Workspace"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Split Container */}
        <div className="flex-1 flex overflow-hidden">
          {/* Left Panel: High-Contrast Conversation Stream */}
          <div className={`w-1/2 border-r flex flex-col p-6 space-y-4 overflow-y-auto ${
            isLightMode ? 'bg-slate-50 border-slate-200' : 'bg-[#0c101a] border-slate-800'
          }`}>
            <div className="flex items-center justify-between border-b pb-2 border-slate-300/60 dark:border-slate-800">
              <span className="text-xs font-mono font-bold uppercase tracking-wider text-cyan-600 dark:text-cyan-400 flex items-center gap-2">
                <FileText className="w-4 h-4" />
                <span>Conversation Log ({filteredMessages.length} Messages)</span>
              </span>
            </div>

            <div className="flex-1 space-y-4 overflow-y-auto pr-2">
              {filteredMessages.map((msg) => (
                <div
                  key={msg.id}
                  className={`p-4 rounded-2xl border text-xs leading-relaxed transition-all shadow-md ${
                    msg.sender === 'agent'
                      ? isLightMode
                        ? 'bg-white border-slate-300 text-slate-950 font-medium'
                        : 'bg-slate-900/90 border-slate-800 text-slate-200'
                      : 'bg-blue-600 text-white font-medium self-end ml-12'
                  }`}
                >
                  <div className="flex items-center justify-between mb-2 font-mono text-[10px] opacity-75 border-b pb-1.5 border-slate-200/40 dark:border-slate-800">
                    <span className="font-bold flex items-center gap-1">
                      {msg.sender === 'agent' ? <Bot className="w-3.5 h-3.5 text-cyan-400" /> : <User className="w-3.5 h-3.5" />}
                      {msg.sender === 'agent' ? 'ADK Remediation Agent' : 'You'}
                    </span>
                    <span>{new Date(msg.timestamp).toLocaleTimeString()}</span>
                  </div>

                  {msg.sender === 'agent' ? (
                    <RichTextRenderer text={msg.text} onRunSandboxCommand={onRunSandboxCommand} />
                  ) : (
                    <p className="whitespace-pre-wrap">{msg.text}</p>
                  )}

                  {/* Inline Action Chips */}
                  {msg.sender === 'agent' && (
                    <div className="mt-3 pt-2.5 border-t border-slate-200/60 dark:border-slate-800 flex flex-wrap gap-2">
                      <button
                        onClick={() => onSendMessage(`Investigate on Google & Reddit for: ${summary}`)}
                        className="px-2.5 py-1 rounded-lg bg-cyan-950/60 hover:bg-cyan-900/80 border border-cyan-500/40 text-cyan-300 text-[10px] font-mono font-bold flex items-center gap-1 cursor-pointer transition-all"
                      >
                        <Globe className="w-3 h-3 text-cyan-400" />
                        <span>🔍 Search Reddit & Web</span>
                      </button>

                      {remediation && (
                        <button
                          onClick={() => onRunSandboxCommand && onRunSandboxCommand(remediation.split('\n')[0])}
                          className="px-2.5 py-1 rounded-lg bg-emerald-950/60 hover:bg-emerald-900/80 border border-emerald-500/40 text-emerald-300 text-[10px] font-mono font-bold flex items-center gap-1 cursor-pointer transition-all"
                        >
                          <Zap className="w-3 h-3 text-emerald-400" />
                          <span>⚡ Run gcloud Sandbox</span>
                        </button>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Right Panel: Interactive Root Cause Mindmap & Executive Takeaways */}
          <div className="w-1/2 p-6 flex flex-col space-y-6 overflow-y-auto">
            {/* Interactive Mindmap Visualizer */}
            <div className={`p-5 rounded-3xl border shadow-xl ${
              isLightMode ? 'bg-slate-100 border-slate-300' : 'bg-slate-900/80 border-slate-800'
            }`}>
              <div className="flex items-center justify-between mb-4 border-b pb-3 border-slate-200 dark:border-slate-800">
                <div className="flex items-center space-x-2">
                  <Network className="w-4 h-4 text-cyan-400" />
                  <h3 className="text-xs font-black uppercase font-mono tracking-wider">
                    Interactive Incident Root Cause Mindmap
                  </h3>
                </div>
                <span className="text-[10px] font-mono font-bold text-emerald-400 bg-emerald-950/60 px-2 py-0.5 rounded border border-emerald-500/40">
                  4 Active Nodes Linked
                </span>
              </div>

              {/* Mindmap Nodes Flow Grid */}
              <div className="grid grid-cols-2 gap-3.5 mb-4">
                {mindmapNodes.map((node) => {
                  const isActive = activeMindmapNode === node.id;
                  return (
                    <div
                      key={node.id}
                      onClick={() => setActiveMindmapNode(node.id)}
                      className={`p-3.5 rounded-2xl border-2 cursor-pointer transition-all duration-200 relative overflow-hidden ${node.color} ${
                        isActive ? 'ring-2 ring-white scale-[1.02] shadow-xl' : 'opacity-85 hover:opacity-100'
                      }`}
                    >
                      <div className="flex items-center justify-between mb-1.5">
                        <span className="text-[9px] font-mono font-bold uppercase tracking-wider opacity-75">
                          {node.status}
                        </span>
                        <ArrowRight className="w-3.5 h-3.5 opacity-60" />
                      </div>
                      <div className="text-xs font-bold font-mono tracking-tight mb-1">{node.title}</div>
                      <div className="text-[10px] opacity-80 font-sans line-clamp-1">{node.subtitle}</div>
                    </div>
                  );
                })}
              </div>

              {/* Active Mindmap Node Detail Box */}
              {activeMindmapNode && (
                <div className={`p-4 rounded-2xl border font-mono text-xs space-y-2 animate-fade-in ${
                  isLightMode ? 'bg-white border-slate-300 text-slate-900' : 'bg-slate-950 border-slate-800 text-slate-200'
                }`}>
                  <div className="text-[10px] uppercase font-bold text-cyan-400 tracking-wider">
                    📌 Selected Node Detail: {mindmapNodes.find((n) => n.id === activeMindmapNode)?.title}
                  </div>
                  <p className="text-xs leading-relaxed">
                    {mindmapNodes.find((n) => n.id === activeMindmapNode)?.description}
                  </p>
                </div>
              )}
            </div>

            {/* Executive Key Point Takeaways */}
            <div className={`p-5 rounded-3xl border shadow-xl space-y-3 ${
              isLightMode ? 'bg-white border-slate-300' : 'bg-slate-900/60 border-slate-800'
            }`}>
              <div className="flex items-center space-x-2 border-b pb-2.5 border-slate-200 dark:border-slate-800">
                <Sparkles className="w-4 h-4 text-amber-400" />
                <h3 className="text-xs font-black uppercase font-mono tracking-wider">
                  Executive Incident Key Points & Strategy
                </h3>
              </div>

              <ul className="space-y-2 text-xs font-sans leading-relaxed">
                <li className="flex items-start gap-2">
                  <span className="text-emerald-400 font-bold">•</span>
                  <span><strong>Service Context</strong>: Active investigation centered on <code>{serviceName}</code> in region <code>us-central1</code>.</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-cyan-400 font-bold">•</span>
                  <span><strong>Remediation Strategy</strong>: Applied gcloud CLI environment update to supply missing runtime secrets and IAM role bindings.</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-purple-400 font-bold">•</span>
                  <span><strong>Proactive Guardrails</strong>: Configured liveness probe polling to verify status 200 OK following auto-deployment.</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
