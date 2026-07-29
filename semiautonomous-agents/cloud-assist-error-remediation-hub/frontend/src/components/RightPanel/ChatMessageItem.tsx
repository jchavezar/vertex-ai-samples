import React from 'react';
import { ChatMessage } from '../../types';
import { RichTextRenderer } from '../RichTextRenderer';
import {
  Bot,
  User,
  ExternalLink,
  Globe,
  Zap,
  Network,
  Key,
  TrendingUp,
  Database,
  HelpCircle,
  Sparkles
} from 'lucide-react';

interface ChatMessageItemProps {
  message: ChatMessage;
  onRunSandboxCommand?: (cmd: string) => void;
  onOpenAnalyticalOverlay?: () => void;
  onQuickQuery?: (query: string) => void;
  isLightMode?: boolean;
}

// Helper to extract REAL executable gcloud commands (excludes plain text references like "request gcloud fix commands")
const extractExecutableGcloudCommand = (text: string): string | null => {
  if (!text) return null;

  // 1. Prioritize fenced code blocks containing valid gcloud subcommands
  const codeBlockMatch = text.match(/```(?:bash|sh|terminal|zsh)?\s*\n?[\s\S]*?(gcloud\s+(?:run|sql|container|compute|secrets|iam|logging|services|config|alpha|beta|storage|auth|projects)\s+[^\n`]+)[\s\S]*?```/i);
  if (codeBlockMatch && codeBlockMatch[1]) {
    return codeBlockMatch[1].trim();
  }

  // 2. Match standalone CLI invocations with valid gcloud subcommands
  const standaloneMatch = text.match(/\b(gcloud\s+(?:run|sql|container|compute|secrets|iam|logging|services|config|alpha|beta|storage|auth|projects)\s+[^\n`]+)/i);
  if (standaloneMatch && standaloneMatch[1]) {
    const cmd = standaloneMatch[1].trim();
    if (!cmd.toLowerCase().includes('gcloud fix') && !cmd.toLowerCase().includes('request gcloud')) {
      return cmd;
    }
  }

  return null;
};

export const ChatMessageItem: React.FC<ChatMessageItemProps> = ({
  message,
  onRunSandboxCommand,
  onOpenAnalyticalOverlay,
  onQuickQuery,
  isLightMode = false
}) => {
  const isAgent = message.sender === 'agent';

  // Smart Content-Aware Action Button Generator
  const generateSmartButtons = () => {
    const text = message.text || '';
    const lower = text.toLowerCase();
    const buttons: { label: string; icon: React.ReactNode; action: () => void; bgStyle: string }[] = [];

    // 1. Extract gcloud command ONLY if a real executable CLI command is present
    const executableCmd = extractExecutableGcloudCommand(text);
    if (executableCmd && onRunSandboxCommand) {
      buttons.push({
        label: `⚡ Run: ${executableCmd.length > 25 ? executableCmd.substring(0, 25) + '...' : executableCmd}`,
        icon: <Zap className="w-3 h-3 text-amber-300 fill-amber-300" />,
        action: () => onRunSandboxCommand(executableCmd),
        bgStyle: isLightMode
          ? 'bg-emerald-700 hover:bg-emerald-800 text-white border-emerald-800 shadow-sm'
          : 'bg-emerald-950/60 hover:bg-emerald-900/80 border-emerald-500/40 text-emerald-300'
      });
    }

    // 2. Secret Manager / IAM / Credentials context
    if (lower.includes('secret') || lower.includes('iam') || lower.includes('jwt') || lower.includes('key')) {
      if (onQuickQuery) {
        buttons.push({
          label: '🔑 Audit Secret & IAM Bindings',
          icon: <Key className="w-3 h-3 text-amber-400" />,
          action: () => onQuickQuery('Show step-by-step gcloud commands to grant Secret Accessor role to service account'),
          bgStyle: isLightMode
            ? 'bg-slate-950 hover:bg-slate-800 text-white border-slate-900 shadow-sm'
            : 'bg-amber-950/40 hover:bg-amber-900/60 border-amber-500/30 text-amber-300'
        });
      }
    }

    // 3. Memory / OOM / Heap Limit context
    if (lower.includes('memory') || lower.includes('oom') || lower.includes('heap') || lower.includes('512')) {
      if (onQuickQuery) {
        buttons.push({
          label: '📈 Scale Memory Ceiling to 1024MB',
          icon: <TrendingUp className="w-3 h-3 text-cyan-400" />,
          action: () => onQuickQuery('Provide gcloud command to scale Cloud Run memory limit to 1024MiB'),
          bgStyle: isLightMode
            ? 'bg-slate-950 hover:bg-slate-800 text-white border-slate-900 shadow-sm'
            : 'bg-cyan-950/40 hover:bg-cyan-900/60 border-cyan-500/30 text-cyan-300'
        });
      }
    }

    // 4. Cloud SQL / Database context
    if (lower.includes('sql') || lower.includes('database') || lower.includes('postgres') || lower.includes('pool')) {
      if (onQuickQuery) {
        buttons.push({
          label: '🗄️ Inspect DB Pool & Maintenance',
          icon: <Database className="w-3 h-3 text-purple-400" />,
          action: () => onQuickQuery('How do I check Cloud SQL maintenance status and expand connection pool capacity?'),
          bgStyle: isLightMode
            ? 'bg-purple-900 hover:bg-purple-950 text-white border-purple-950 shadow-sm'
            : 'bg-purple-950/40 hover:bg-purple-900/60 border-purple-500/30 text-purple-300'
        });
      }
    }

    const isGreetingOrIntro = lower.includes('how can i assist') ||
      lower.includes('how can i help') ||
      lower.includes('welcome') ||
      lower.includes('active context set to') ||
      lower.startsWith('hello') ||
      text.length < 25;

    const isIncidentContext = !isGreetingOrIntro && (
      lower.includes('zerodivision') || lower.includes('oom') || lower.includes('jwt') ||
      lower.includes('stacktrace') || lower.includes('traceback') || lower.includes('root cause') ||
      lower.includes('exception') || lower.includes('remediation') || lower.includes('cause:') ||
      lower.includes('500 internal server error')
    );

    // 5. Tailored Deep Search Button (ONLY when discussing a specific incident/error)
    if (onQuickQuery && isIncidentContext) {
      const topic = lower.includes('jwt') ? 'JWT_SECRET_KEY'
        : lower.includes('zerodivision') ? 'ZeroDivisionError'
        : lower.includes('oom') ? 'OOMKilled'
        : 'Cloud Run Error';

      buttons.push({
        label: `🌐 Deep Search: ${topic}`,
        icon: <Globe className="w-3 h-3 text-cyan-400" />,
        action: () => onQuickQuery(`Search Google and Reddit for: ${topic} fix`),
        bgStyle: isLightMode
          ? 'bg-slate-900 hover:bg-slate-800 text-white border-slate-900 shadow-sm'
          : 'bg-slate-800 hover:bg-slate-700 border-slate-700 text-cyan-300'
      });
    }

    // 6. Interactive Mindmap Engine Button (ONLY when discussing a specific incident/error)
    if (onOpenAnalyticalOverlay && isIncidentContext) {
      buttons.push({
        label: '🧠 Root Cause Mindmap',
        icon: <Network className="w-3 h-3 text-purple-300" />,
        action: onOpenAnalyticalOverlay,
        bgStyle: isLightMode
          ? 'bg-slate-950 hover:bg-slate-800 text-white border-slate-900 shadow-sm'
          : 'bg-purple-950/50 hover:bg-purple-900/80 border-purple-500/40 text-purple-300'
      });
    }

    return buttons.slice(0, 3); // Top 3 most relevant buttons per bubble
  };

  const smartButtons = isAgent ? generateSmartButtons() : [];

  return (
    <div className={`flex items-start space-x-3 ${isAgent ? '' : 'flex-row-reverse space-x-reverse'}`}>
      {/* Avatar */}
      <div
        className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 shadow-md ${
          isAgent
            ? isLightMode
              ? 'bg-slate-950 text-white shadow-slate-900/20'
              : 'bg-gradient-to-br from-cyan-600 to-blue-700 text-white ring-1 ring-cyan-400/30 shadow-cyan-500/20'
            : isLightMode
              ? 'bg-slate-800 text-white'
              : 'bg-slate-800 text-slate-300 border border-slate-700'
        }`}
      >
        {isAgent ? <Bot className="w-4 h-4" /> : <User className="w-4 h-4" />}
      </div>

      {/* Bubble */}
      <div
        className={`rounded-2xl p-4 max-w-[92%] text-xs leading-relaxed transition-all ${
          isAgent
            ? isLightMode
              ? 'bg-white border border-slate-300 text-slate-950 font-medium shadow-md'
              : 'bg-slate-900/95 border border-slate-800/90 text-slate-200 shadow-xl'
            : isLightMode
              ? 'bg-slate-950 text-white font-bold shadow-md'
              : 'bg-blue-600 text-white shadow-md'
        }`}
      >
        {isAgent ? (
          <RichTextRenderer text={message.text} onRunSandboxCommand={onRunSandboxCommand} isLightMode={isLightMode} />
        ) : (
          <div className="whitespace-pre-line break-words">{message.text}</div>
        )}

        {/* Antigravity Interactive Remediation Tool Execution Card */}
        {isAgent && onRunSandboxCommand && (() => {
          const cmd = extractExecutableGcloudCommand(message.text);
          if (!cmd) return null;
          return (
            <div className={`mt-3 p-3.5 rounded-xl border flex flex-col gap-2.5 shadow-lg transition-all ${
              isLightMode
                ? 'bg-slate-100 border-purple-300 text-slate-950 font-medium'
                : 'bg-gradient-to-r from-purple-950/60 via-slate-950 to-cyan-950/60 border-purple-500/40 text-slate-100'
            }`}>
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-1.5 text-xs font-mono font-bold text-cyan-300">
                  <Zap className="w-3.5 h-3.5 text-amber-300 fill-amber-300 animate-pulse" />
                  <span>Antigravity Agent • Interactive Sandbox Tool</span>
                </div>
                <span className="text-[9px] font-mono px-2 py-0.5 rounded border bg-purple-500/20 text-purple-300 border-purple-500/30 font-bold">
                  Executable Command
                </span>
              </div>

              <p className="text-[11px] font-semibold leading-relaxed text-slate-200">
                Would you like me to execute this fix for you in the GCP Sandbox?
              </p>

              <button
                onClick={() => onRunSandboxCommand(cmd)}
                className="w-full py-2 px-3.5 rounded-xl bg-gradient-to-r from-purple-600 via-blue-600 to-cyan-600 hover:from-purple-500 hover:to-cyan-500 text-white font-mono text-xs font-bold flex items-center justify-center gap-2 shadow-md cursor-pointer transition-all hover:scale-[1.01]"
              >
                <Zap className="w-3.5 h-3.5 text-amber-300 fill-amber-300" />
                <span>⚡ Execute Fix Command in GCP Sandbox</span>
              </button>
            </div>
          );
        })()}

        {/* Intelligent Content-Aware Action Buttons */}
        {isAgent && smartButtons.length > 0 && (
          <div className={`mt-3 pt-2.5 border-t flex flex-wrap gap-1.5 ${
            isLightMode ? 'border-slate-200' : 'border-slate-800/80'
          }`}>
            {smartButtons.map((btn, idx) => (
              <button
                key={idx}
                onClick={btn.action}
                className={`px-2.5 py-1 rounded-lg border text-[10px] font-mono font-bold flex items-center gap-1.5 cursor-pointer transition-all ${btn.bgStyle}`}
              >
                {btn.icon}
                <span>{btn.label}</span>
              </button>
            ))}
          </div>
        )}

        {/* Cited Web / Doc Sources */}
        {isAgent && message.sourcesCited && message.sourcesCited.length > 0 && (
          <div className={`mt-3 pt-2.5 border-t space-y-1.5 ${
            isLightMode ? 'border-slate-200' : 'border-slate-800/80'
          }`}>
            <div className={`flex items-center space-x-1 text-[10px] font-bold uppercase ${
              isLightMode ? 'text-slate-950 font-mono' : 'text-cyan-400'
            }`}>
              <Globe className="w-3 h-3" />
              <span>Google Search & Official Sources</span>
            </div>
            <div className="flex flex-wrap gap-1.5">
              {message.sourcesCited.map((src, idx) => {
                const isUrl = src.startsWith('http');
                return isUrl ? (
                  <a
                    key={idx}
                    href={src}
                    target="_blank"
                    rel="noopener noreferrer"
                    className={`inline-flex items-center gap-1 text-[10px] px-2 py-0.5 rounded transition-colors font-mono font-bold ${
                      isLightMode
                        ? 'bg-slate-100 hover:bg-slate-200 border border-slate-300 text-slate-950'
                        : 'text-cyan-300 bg-cyan-950/40 hover:bg-cyan-900/60 border border-cyan-800/50'
                    }`}
                  >
                    <span>{src.replace(/https?:\/\/(www\.)?/, '').split('/')[0]}</span>
                    <ExternalLink className="w-2.5 h-2.5" />
                  </a>
                ) : (
                  <span
                    key={idx}
                    className={`text-[10px] px-2 py-0.5 rounded border font-mono ${
                      isLightMode ? 'bg-slate-100 border-slate-300 text-slate-900 font-bold' : 'text-slate-300 bg-slate-800 border-slate-700'
                    }`}
                  >
                    {src}
                  </span>
                );
              })}
            </div>
          </div>
        )}

        {/* Agent Metadata Footer with Source Origin Tag & Dynamic Latency Counter */}
        {isAgent && (
          <div className={`mt-2.5 pt-2 border-t flex flex-wrap items-center justify-between gap-2 text-[9px] font-mono ${
            isLightMode ? 'border-slate-200 text-slate-700 font-bold' : 'border-slate-800/60 text-slate-500'
          }`}>
            <span className={`px-2 py-0.5 rounded border font-bold ${
              isLightMode
                ? 'bg-purple-100 text-purple-950 border-purple-300'
                : 'bg-purple-500/20 text-purple-300 border-purple-500/40'
            }`}>
              🏷️ {message.sourceTag || "ADK Agent (gemini-3.5-flash)"}
            </span>
            <span className={`px-2 py-0.5 rounded font-mono font-extrabold border ${
              isLightMode
                ? 'bg-emerald-100 text-emerald-950 border-emerald-300'
                : 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40'
            }`}>
              ⚡ {message.latencyMs !== undefined ? `${message.latencyMs}ms Execution` : 'Fast Direct Route'}
            </span>
          </div>
        )}
      </div>
    </div>
  );
};
