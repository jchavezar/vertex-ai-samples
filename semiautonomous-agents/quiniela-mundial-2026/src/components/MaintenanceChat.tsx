"use client";

import { useEffect, useRef, useState } from "react";
import { Send, Loader2, Wrench, ShieldAlert, Check, X, Trash2, ChevronRight, FileCode, Terminal, Search } from "lucide-react";
import { ChatMarkdown } from "@/components/ChatMarkdown";

type ToolCall = {
  id: string;
  name: string;
  input: Record<string, unknown>;
  status: "running" | "pending-approval" | "approved" | "denied" | "done";
  requestId?: string;
  resultPreview?: string;
};

type MaintMsg =
  | { kind: "user"; text: string }
  | { kind: "assistant"; text: string; streaming?: boolean }
  | { kind: "tool"; tool: ToolCall }
  | { kind: "error"; text: string };

const SID_KEY = "q26:maint-sid";

const READ_ONLY_TOOLS = new Set(["Read", "Grep", "Glob", "WebFetch", "WebSearch", "TaskList", "TaskGet", "TaskCreate", "TaskUpdate", "Agent"]);

function previewInput(name: string, input: Record<string, unknown>): string {
  if (name === "Bash" && typeof input.command === "string") return input.command.slice(0, 200);
  if ((name === "Edit" || name === "Write") && typeof input.file_path === "string") return String(input.file_path);
  if (name === "Read" && typeof input.file_path === "string") return String(input.file_path);
  if ((name === "Grep" || name === "Glob") && typeof input.pattern === "string") return String(input.pattern);
  try { return JSON.stringify(input).slice(0, 200); } catch { return ""; }
}

function toolIcon(name: string) {
  if (name === "Bash") return <Terminal size={12} />;
  if (name === "Edit" || name === "Write") return <FileCode size={12} />;
  if (name === "Read" || name === "Grep" || name === "Glob") return <Search size={12} />;
  return <Wrench size={12} />;
}

export function MaintenanceChat({ onExit }: { onExit: () => void }) {
  const [messages, setMessages] = useState<MaintMsg[]>([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [bypass, setBypass] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages]);
  useEffect(() => {
    const el = inputRef.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = Math.min(el.scrollHeight, 160) + "px";
  }, [input]);

  function patchTool(id: string, patch: Partial<ToolCall>) {
    setMessages(prev => prev.map(m => (m.kind === "tool" && m.tool.id === id ? { ...m, tool: { ...m.tool, ...patch } } : m)));
  }

  async function decide(requestId: string, decision: "allow" | "deny") {
    try {
      await fetch("/api/maint/permission", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ requestId, decision }),
      });
      setMessages(prev => prev.map(m => {
        if (m.kind === "tool" && m.tool.requestId === requestId) {
          return { ...m, tool: { ...m.tool, status: decision === "allow" ? "approved" : "denied" } };
        }
        return m;
      }));
    } catch (e) {
      setMessages(prev => [...prev, { kind: "error", text: `Permiso fallo: ${(e as Error).message}` }]);
    }
  }

  async function resetSession() {
    if (!confirm("¿Nueva conversación? Claude Code olvidará todo lo previo.")) return;
    try {
      await fetch("/api/maint/reset", { method: "POST" });
    } catch {}
    localStorage.removeItem(SID_KEY);
    setMessages([]);
  }

  async function send(textOverride?: string) {
    const text = (textOverride ?? input).trim();
    if (!text || busy) return;
    setInput("");
    setBusy(true);
    setMessages(prev => [...prev, { kind: "user", text }, { kind: "assistant", text: "", streaming: true }]);

    let assistantBuffer = "";
    let pendingToolUseIds: Record<string, string> = {}; // sdk tool_use id → our local id

    function appendAssistantDelta(delta: string) {
      assistantBuffer += delta;
      setMessages(prev => {
        const copy = [...prev];
        for (let i = copy.length - 1; i >= 0; i--) {
          if (copy[i].kind === "assistant" && (copy[i] as Extract<MaintMsg, { kind: "assistant" }>).streaming) {
            copy[i] = { kind: "assistant", text: assistantBuffer, streaming: true };
            return copy;
          }
        }
        return copy;
      });
    }
    function closeAssistant() {
      setMessages(prev => {
        const copy = [...prev];
        for (let i = copy.length - 1; i >= 0; i--) {
          if (copy[i].kind === "assistant" && (copy[i] as Extract<MaintMsg, { kind: "assistant" }>).streaming) {
            const cur = copy[i] as Extract<MaintMsg, { kind: "assistant" }>;
            const finalText = cur.text || assistantBuffer;
            if (!finalText) {
              // Empty assistant block (e.g. went straight to tool_use) — drop it
              // so the UI doesn't render an orphan "pensando…" bubble.
              copy.splice(i, 1);
            } else {
              copy[i] = { kind: "assistant", text: finalText, streaming: false };
            }
            return copy;
          }
        }
        return copy;
      });
      assistantBuffer = "";
    }
    function startNewAssistantBlock() {
      // The current assistant block has emitted tool_use; close it and prepare a fresh one
      // for any post-tool text the model emits next.
      closeAssistant();
      setMessages(prev => [...prev, { kind: "assistant", text: "", streaming: true }]);
    }

    try {
      const res = await fetch("/api/maint/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text, bypass }),
      });
      if (!res.ok || !res.body) {
        const err = await res.text().catch(() => "");
        setMessages(prev => [...prev.slice(0, -1), { kind: "error", text: `Bridge ${res.status}: ${err.slice(0, 160)}` }]);
        return;
      }
      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buf = "";
      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        buf += decoder.decode(value, { stream: true });
        const lines = buf.split("\n");
        buf = lines.pop() || "";
        for (const line of lines) {
          if (!line.startsWith("data: ")) continue;
          let evt: { type: string; [k: string]: unknown };
          try { evt = JSON.parse(line.slice(6)); } catch { continue; }

          if (evt.type === "delta") {
            const e = evt.event as { type: string; delta?: { type: string; text?: string; partial_json?: string }; content_block?: { type: string; name?: string; input?: unknown; id?: string } };
            if (e?.type === "content_block_delta" && e.delta?.type === "text_delta" && typeof e.delta.text === "string") {
              appendAssistantDelta(e.delta.text);
            } else if (e?.type === "content_block_start" && e.content_block?.type === "tool_use") {
              // Tool call begins — close current assistant block.
              const sdkId = String(e.content_block.id || "");
              const name = String(e.content_block.name || "Tool");
              const localId = crypto.randomUUID();
              pendingToolUseIds[sdkId] = localId;
              const initialStatus: ToolCall["status"] = bypass || READ_ONLY_TOOLS.has(name) ? "running" : "pending-approval";
              closeAssistant();
              setMessages(prev => [...prev, {
                kind: "tool",
                tool: { id: localId, name, input: {}, status: initialStatus },
              }]);
            } else if (e?.type === "content_block_stop") {
              // no-op; the assistant frame later supplies final input shape
            }
          } else if (evt.type === "assistant") {
            const msg = evt.message as { content?: Array<{ type: string; text?: string; id?: string; name?: string; input?: Record<string, unknown> }> };
            const blocks = msg?.content || [];
            for (const b of blocks) {
              if (b.type === "tool_use" && b.id) {
                const localId = pendingToolUseIds[b.id];
                if (localId) patchTool(localId, { input: b.input || {}, name: b.name || "Tool" });
              }
            }
            // After tool_use blocks the assistant turn may continue with more text — prep a fresh stream.
            if (blocks.some(b => b.type === "tool_use")) startNewAssistantBlock();
          } else if (evt.type === "tool_request") {
            const { requestId, toolName, input } = evt as unknown as { requestId: string; toolName: string; input: Record<string, unknown> };
            // Pair with the most recent pending-approval tool of same name.
            setMessages(prev => {
              const copy = [...prev];
              for (let i = copy.length - 1; i >= 0; i--) {
                if (copy[i].kind === "tool") {
                  const t = (copy[i] as Extract<MaintMsg, { kind: "tool" }>).tool;
                  if (t.status === "pending-approval" && t.name === toolName && !t.requestId) {
                    copy[i] = { kind: "tool", tool: { ...t, input, requestId } };
                    return copy;
                  }
                }
              }
              // Fallback: append a new pending card.
              copy.push({ kind: "tool", tool: { id: crypto.randomUUID(), name: toolName, input, requestId, status: "pending-approval" } });
              return copy;
            });
          } else if (evt.type === "tool_result") {
            const msg = evt.message as { content?: Array<{ type: string; tool_use_id?: string; content?: unknown }> };
            const blocks = msg?.content || [];
            for (const b of blocks) {
              if (b.type === "tool_result" && b.tool_use_id) {
                const localId = pendingToolUseIds[b.tool_use_id];
                if (localId) {
                  const preview = typeof b.content === "string" ? b.content.slice(0, 400) : JSON.stringify(b.content ?? "").slice(0, 400);
                  patchTool(localId, { status: "done", resultPreview: preview });
                }
              }
            }
          } else if (evt.type === "permission_denied") {
            // already reflected via decide(); ignore
          } else if (evt.type === "done") {
            if (typeof evt.sessionId === "string") localStorage.setItem(SID_KEY, evt.sessionId);
            closeAssistant();
          } else if (evt.type === "error") {
            setMessages(prev => [...prev, { kind: "error", text: String(evt.error || "unknown") }]);
          }
        }
      }
      closeAssistant();
    } catch (e) {
      setMessages(prev => [...prev, { kind: "error", text: `Stream fallo: ${(e as Error).message}` }]);
    } finally {
      setBusy(false);
    }
  }

  function onKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      send();
    }
  }

  return (
    <div className="flex-1 min-h-0 flex flex-col bg-zinc-950 text-zinc-100">
      <div className="flex items-center gap-2 px-3 py-2 border-b border-zinc-800 text-xs">
        <Wrench size={14} className="text-orange-400" />
        <span className="font-display font-bold tracking-wide">MODO MANTENIMIENTO</span>
        <span className="text-zinc-500">·</span>
        <span className="text-zinc-400">Claude Code en la VM</span>
        <div className="ml-auto flex items-center gap-2">
          <button
            onClick={() => setBypass(b => !b)}
            title={bypass ? "Bypass total: tools se ejecutan sin preguntar" : "Default: tools peligrosos preguntan antes de ejecutar"}
            className={`px-2 py-1 rounded-full text-[10px] font-semibold uppercase tracking-wider inline-flex items-center gap-1 transition-colors ${bypass ? "bg-red-600 text-white" : "bg-zinc-800 text-zinc-300 hover:bg-zinc-700"}`}
          >
            {bypass ? <ShieldAlert size={11} /> : <Check size={11} />}
            {bypass ? "Bypass" : "Aprobar"}
          </button>
          <button onClick={resetSession} title="Borrar sesión y empezar de cero" className="p-1.5 rounded-full text-zinc-400 hover:bg-zinc-800 hover:text-zinc-100">
            <Trash2 size={12} />
          </button>
          <button onClick={onExit} className="px-2 py-1 rounded-full bg-zinc-800 hover:bg-zinc-700 text-[10px] font-semibold text-zinc-200">
            Salir
          </button>
        </div>
      </div>
      {bypass && (
        <div className="px-3 py-1.5 text-[10px] font-semibold text-red-200 bg-red-950/70 border-b border-red-900 inline-flex items-center gap-1.5">
          <ShieldAlert size={11} /> BYPASS ACTIVO — Claude Code edita y ejecuta sin confirmación.
        </div>
      )}

      <div ref={scrollRef} className="flex-1 overflow-y-auto p-3 space-y-2.5 text-sm">
        {messages.length === 0 && (
          <div className="text-center pt-10 px-4">
            <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-zinc-900 text-[10px] font-semibold uppercase tracking-wider text-zinc-400">
              <Wrench size={11} /> Sesión persistente
            </div>
            <p className="mt-3 text-xs text-zinc-400 leading-relaxed">
              Pídele a Claude Code lo que necesites del repo —<br />
              arreglar bugs, redeploy, agregar features, leer logs.
            </p>
            <p className="mt-2 text-[10px] text-zinc-500">cwd: quiniela-mundial-2026</p>
          </div>
        )}

        {messages.map((m, i) => {
          if (m.kind === "user") {
            return (
              <div key={i} className="flex justify-end">
                <div className="max-w-[85%] px-3 py-2 rounded-2xl bg-zinc-700 text-zinc-50 whitespace-pre-wrap text-[13px] leading-snug">{m.text}</div>
              </div>
            );
          }
          if (m.kind === "assistant") {
            if (!m.text && !m.streaming) return null;
            return (
              <div key={i} className="flex justify-start">
                <div className="max-w-[92%] px-3 py-2 rounded-2xl bg-zinc-900 border border-zinc-800 text-zinc-100 text-[13px] leading-relaxed">
                  {m.text ? <ChatMarkdown text={m.text} /> : <span className="inline-flex items-center gap-1.5 text-zinc-500"><Loader2 size={12} className="animate-spin" /> pensando…</span>}
                  {m.streaming && m.text && <span className="inline-block w-1 h-3 ml-1 bg-current animate-pulse align-middle" />}
                </div>
              </div>
            );
          }
          if (m.kind === "error") {
            return (
              <div key={i} className="px-3 py-2 rounded-2xl bg-red-950 border border-red-900 text-red-200 text-xs">{m.text}</div>
            );
          }
          // tool card
          const t = m.tool;
          const tone =
            t.status === "pending-approval" ? "border-amber-700 bg-amber-950/50 text-amber-100" :
            t.status === "denied" ? "border-red-900 bg-red-950/50 text-red-200" :
            t.status === "approved" || t.status === "running" ? "border-blue-900 bg-blue-950/40 text-blue-100" :
            "border-zinc-800 bg-zinc-900 text-zinc-200";
          return (
            <div key={i} className={`rounded-2xl border ${tone} text-[12px] overflow-hidden`}>
              <div className="px-3 py-1.5 flex items-center gap-2">
                <span className="text-zinc-300">{toolIcon(t.name)}</span>
                <span className="font-semibold uppercase tracking-wider text-[10px]">{t.name}</span>
                <span className="text-zinc-500">·</span>
                <span className="text-[10px] uppercase tracking-wider opacity-80">
                  {t.status === "pending-approval" ? "esperando aprobación" :
                   t.status === "running" ? "ejecutando" :
                   t.status === "approved" ? "aprobado" :
                   t.status === "denied" ? "denegado" :
                   "done"}
                </span>
                <ChevronRight size={11} className="ml-auto opacity-50" />
              </div>
              <div className="px-3 pb-2 font-mono text-[11px] text-zinc-300 break-all whitespace-pre-wrap">
                {previewInput(t.name, t.input)}
              </div>
              {t.status === "pending-approval" && t.requestId && (
                <div className="px-3 pb-2 flex gap-2">
                  <button
                    onClick={() => decide(t.requestId!, "allow")}
                    className="flex-1 px-3 py-1.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-[11px] font-bold inline-flex items-center justify-center gap-1"
                  >
                    <Check size={11} /> Aprobar
                  </button>
                  <button
                    onClick={() => decide(t.requestId!, "deny")}
                    className="flex-1 px-3 py-1.5 rounded-xl bg-zinc-700 hover:bg-zinc-600 text-white text-[11px] font-bold inline-flex items-center justify-center gap-1"
                  >
                    <X size={11} /> Denegar
                  </button>
                </div>
              )}
              {t.resultPreview && (
                <div className="px-3 pb-2 pt-1 border-t border-zinc-800/60 font-mono text-[10.5px] text-zinc-400 max-h-32 overflow-y-auto whitespace-pre-wrap break-all">
                  {t.resultPreview}
                </div>
              )}
            </div>
          );
        })}
      </div>

      <div className="p-2.5 border-t border-zinc-800 bg-zinc-950">
        <div className="flex items-end gap-2 rounded-3xl px-3 py-2 bg-zinc-900">
          <textarea
            ref={inputRef}
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={onKeyDown}
            rows={1}
            placeholder={bypass ? "Pídele lo que sea (sin pedir permiso)…" : "Pídele algo al repo (te pedirá permiso para tocar archivos)…"}
            style={{ WebkitTapHighlightColor: "transparent", outline: "none", boxShadow: "none" }}
            className="flex-1 bg-transparent text-base md:text-[13px] resize-none outline-none placeholder:text-zinc-500 text-zinc-100 py-1 max-h-40 leading-snug"
          />
          <button
            onClick={() => send()}
            disabled={!input.trim() || busy}
            aria-label="Enviar"
            className="w-9 h-9 rounded-full bg-orange-500 text-white grid place-items-center disabled:opacity-30 disabled:cursor-not-allowed shrink-0"
          >
            {busy ? <Loader2 size={16} className="animate-spin" /> : <Send size={16} />}
          </button>
        </div>
      </div>
    </div>
  );
}
