"use client";

import { useCallback, useRef, useState, useEffect } from "react";
import { createSession, streamChat, type StreamChunk } from "@/lib/api";

type Msg =
  | { id: string; role: "user"; text: string }
  | {
      id: string;
      role: "assistant";
      text: string;
      tools: { name: string; args?: unknown; preview?: string }[];
      streaming: boolean;
      groundingActive?: boolean;
      latencyMs?: number;
      firstTokenMs?: number;
    };

type Props = {
  accessToken: string | null;
  userId: string;
  fusedMemories: string[];
  thinkingLevel?: string;
  selectedModel?: string;
  onTraceEvent?: (ev: {
    type: "api_call" | "sse_chunk" | "thought" | "token_flow" | "token_count";
    label: string;
    details?: string;
    timestamp?: string;
    data?: any;
  }) => void;
};

const SAMPLE_PROMPTS = [
  "Search my Drive for documents about envato",
  "Show recently modified files",
  "Find information about the Workspace GSuite datastore project",
];

export default function ChatPanel({ accessToken, userId, fusedMemories, onTraceEvent, thinkingLevel, selectedModel }: Props) {
  const [messages, setMessages] = useState<Msg[]>([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const sessionIdRef = useRef<string | null>(null);
  const scrollRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const ensureSession = useCallback(async () => {
    if (!accessToken) throw new Error("Not signed in");
    if (sessionIdRef.current) return sessionIdRef.current;
    
    if (onTraceEvent) {
      onTraceEvent({
        type: "api_call",
        label: "POST /api/session",
        details: "Initializing or loading existing Agent Engine session thread state"
      });
    }
    const t0 = Date.now();
    const sid = await createSession(accessToken, userId);
    const latency = Date.now() - t0;
    
    if (onTraceEvent) {
      onTraceEvent({
        type: "api_call",
        label: "POST /api/session [SUCCESS]",
        details: `Created session ${sid.slice(0, 15)}... Latency: ${latency}ms`
      });
      // Fire token flow details
      onTraceEvent({
        type: "token_flow",
        label: "GSuite User OAuth Access Token",
        details: accessToken ? `${accessToken.slice(0, 12)}...[masked]...${accessToken.slice(-6)}` : "No active token available"
      });
    }
    
    sessionIdRef.current = sid;
    return sid;
  }, [accessToken, userId, onTraceEvent]);

  const send = useCallback(
    async (text: string) => {
      if (!text.trim() || !accessToken || busy) return;
      setError(null);
      setBusy(true);

      const userMsg: Msg = { id: `u-${Date.now()}`, role: "user", text };
      const assistantId = `a-${Date.now()}`;
      const assistantMsg: Msg = {
        id: assistantId,
        role: "assistant",
        text: "",
        tools: [],
        streaming: true,
        groundingActive: true, // Show grounding search state first
      };
      setMessages((m) => [...m, userMsg, assistantMsg]);
      setInput("");

      if (onTraceEvent) {
        onTraceEvent({
          type: "api_call",
          label: "User Message Submitted",
          details: `Query text length: ${text.length} chars. Active fused memories context count: ${fusedMemories.length}`
        });
      }

      let responseReceived = false;
      let currentError: string | null = null;

      const startTime = Date.now();
      let firstTokenTime: number | null = null;

      try {
        const sid = await ensureSession();
        
        // Ground the prompt dynamically with active fused memories context
        let promptText = text;
        if (fusedMemories.length > 0) {
          promptText = `[Grounded Fused Memories Context: The user has pinned/fused the following search documents into the active workspace session: ${fusedMemories.join(", ")}. Please prioritize these references when answering the query. If needed, perform a search to locate details about them.]\n\n${text}`;
        }

        if (onTraceEvent) {
          onTraceEvent({
            type: "api_call",
            label: "SSE /api/chat Connect",
            details: `Streaming chat request with grounded payload initialized for session: ${sid}`
          });
        }

        await streamChat(accessToken, userId, sid, promptText, thinkingLevel, selectedModel, (chunk: StreamChunk) => {
          if (!firstTokenTime && (chunk.text || chunk.thought || chunk.tool_call || chunk.tool_result)) {
            firstTokenTime = Date.now();
          }
          if (chunk.type === "error" && chunk.error) {
            setError(chunk.error);
            currentError = chunk.error;
            if (onTraceEvent) {
              onTraceEvent({
                type: "api_call",
                label: "SSE /api/chat Error",
                details: chunk.error
              });
            }
            return;
          }
          
          if (chunk && chunk.type !== "error") {
            responseReceived = true;
          }

          if (onTraceEvent) {
            if (chunk.thought) {
              onTraceEvent({
                type: "thought",
                label: "Gemini Thought Stream Segment",
                details: chunk.thought
              });
            }
            if (chunk.text) {
              onTraceEvent({
                type: "sse_chunk",
                label: "Text Chunk",
                details: `Stream block text size: ${chunk.text.length} chars`,
                data: chunk.text
              });
            }
            if (chunk.tool_call) {
              onTraceEvent({
                type: "api_call",
                label: `Tool Call Invoked: ${chunk.tool_call.name}`,
                details: `Invoking system grounding connector for '${chunk.tool_call.name}' with search parameters.`,
                data: chunk.tool_call.args
              });
            }
            if (chunk.tool_result) {
              onTraceEvent({
                type: "api_call",
                label: `Tool Response: ${chunk.tool_result.name}`,
                details: `Tool grounding data fetched successfully for '${chunk.tool_result.name}'`,
                data: {
                  preview: chunk.tool_result.preview,
                  response: chunk.tool_result.response,
                }
              });
            }
            if (chunk.usage_metadata) {
              onTraceEvent({
                type: "token_count",
                label: "Gemini Token Usage Flow Update",
                details: `Prompt: ${chunk.usage_metadata.prompt_token_count || 0} t | Output: ${chunk.usage_metadata.candidates_token_count || 0} t | Thoughts: ${chunk.usage_metadata.thoughts_token_count || 0} t`
              });
            }
          }

          setMessages((m) =>
            m.map((msg) => {
              if (msg.id !== assistantId || msg.role !== "assistant") return msg;
              const next = { ...msg };
              if (chunk.text) {
                next.text += chunk.text;
                next.groundingActive = false; // Turn off search state as soon as response streams
              }
              if (chunk.tool_call) {
                next.tools = [
                  ...next.tools,
                  { name: chunk.tool_call.name ?? "tool", args: chunk.tool_call.args },
                ];
              }
              if (chunk.tool_result) {
                const i = next.tools.findIndex(
                  (t) => t.name === chunk.tool_result?.name && t.preview === undefined,
                );
                if (i >= 0) next.tools[i] = { ...next.tools[i], preview: chunk.tool_result.preview };
                else next.tools.push({ name: chunk.tool_result.name ?? "tool", preview: chunk.tool_result.preview });
              }
              return next;
            }),
          );
        });

        if (onTraceEvent) {
          onTraceEvent({
            type: "sse_chunk",
            label: "SSE /api/chat Stream Closed",
            details: "Assistant response complete. Stream finished."
          });
        }
      } catch (e: unknown) {
        const err = e instanceof Error ? e.message : String(e);
        setError(err);
        currentError = err;
        if (onTraceEvent) {
          onTraceEvent({
            type: "api_call",
            label: "SSE /api/chat Failure",
            details: err
          });
        }
      } finally {
        if (!responseReceived) {
          sessionIdRef.current = null;
          if (!currentError) {
            setError("No response received from the agent. This usually happens if the active session expired or the server was redeployed. Retrying your request will now automatically start a fresh session.");
          }
          if (onTraceEvent) {
            onTraceEvent({
              type: "api_call",
              label: "Session Sync Restored",
              details: "Dead/expired session ID was automatically discarded and reset. A new session will be force-initialized on the next query."
            });
          }
        }
        const totalDuration = Date.now() - startTime;
        const firstTokenDuration = firstTokenTime ? (firstTokenTime - startTime) : undefined;

        setMessages((m) =>
          m.map((msg) =>
            msg.id === assistantId && msg.role === "assistant"
              ? { ...msg, streaming: false, groundingActive: false, latencyMs: totalDuration, firstTokenMs: firstTokenDuration }
              : msg
          )
        );
        setBusy(false);
      }
    },
    [accessToken, busy, ensureSession, userId, fusedMemories, onTraceEvent, thinkingLevel]
  );

  const disabled = !accessToken || busy;

  return (
    <div className="flex h-[55vh] md:h-full md:flex-1 min-h-0 flex-col rounded-2xl border border-slate-200/80 bg-white/70 shadow-md shadow-slate-100/40 backdrop-blur-md overflow-hidden">
      
      {/* Header bar of the ChatPanel */}
      <div className="px-5 py-3 border-b border-slate-100 bg-slate-50/50 flex items-center justify-between">
        <span className="text-[10px] font-black tracking-wider text-slate-400 uppercase flex items-center gap-1.5">
          <span className="h-2 w-2 rounded-full bg-indigo-500 animate-pulse"></span>
          3. Cognitive Synapse Mind
        </span>
        <span className="text-[9px] font-mono text-slate-400 bg-white px-2 py-0.5 rounded-md border border-slate-200/40 font-bold">
          {busy ? "PROCESSING" : "STANDBY"}
        </span>
      </div>

      <div ref={scrollRef} className="flex-1 space-y-5 overflow-y-auto p-5 custom-scrollbar">
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-center p-6 space-y-4">
            <div className="h-12 w-12 rounded-2xl bg-indigo-50 flex items-center justify-center text-indigo-500 border border-indigo-100/60 shadow-sm animate-bounce" style={{ animationDuration: "3s" }}>
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-5 h-5">
                <path strokeLinecap="round" strokeLinejoin="round" d="M8.625 12a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Zm0 0H8.25m4.125 0a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Zm0 0H12m4.125 0a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Zm0 0h-.375M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 0 1-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8Z" />
              </svg>
            </div>
            <div className="max-w-md">
              <h3 className="font-extrabold text-slate-800 text-sm tracking-tight uppercase">Conversational Search Mind</h3>
              <p className="mt-1.5 text-xs text-slate-500 leading-relaxed font-medium">
                {accessToken 
                  ? "Direct secure tunnel to Vertex AI Search & GSuite models. Send questions grounded in your selected datastores." 
                  : "Sync with Google Workspace above to launch the model-grounded workspace."}
              </p>
            </div>
            {accessToken && (
              <div className="flex flex-wrap gap-2 justify-center max-w-lg mt-2">
                {SAMPLE_PROMPTS.map((p) => (
                  <button
                    key={p}
                    className="rounded-xl border border-slate-200 bg-white px-3 py-2 text-[11px] text-slate-600 hover:border-cyan-400 hover:text-cyan-600 transition-all duration-200 font-bold cursor-pointer shadow-sm shadow-slate-100/40"
                    onClick={() => send(p)}
                  >
                    {p}
                  </button>
                ))}
              </div>
            )}
          </div>
        )}

        {messages.map((m) => (
          <MessageBubble key={m.id} msg={m} />
        ))}

        {error && (
          <div className="rounded-xl border border-rose-200 bg-rose-50/40 p-4 text-xs text-rose-700 backdrop-blur-sm shadow-inner flex items-center gap-2">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="w-4 h-4 text-rose-500 shrink-0">
              <path fillRule="evenodd" d="M18 10a8 8 0 1 1-16 0 8 8 0 0 1 16 0Zm-8-5a.75.75 0 0 1 .75.75v4.5a.75.75 0 0 1-1.5 0v-4.5A.75.75 0 0 1 10 5Zm0 10a1 1 0 1 0 0-2 1 1 0 0 0 0 2Z" clipRule="evenodd" />
            </svg>
            <span className="font-mono font-medium">{error}</span>
          </div>
        )}
      </div>

      <form
        onSubmit={(e) => {
          e.preventDefault();
          send(input);
        }}
        className="flex gap-2.5 border-t border-slate-100 p-4 bg-white/50 backdrop-blur-md"
      >
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={disabled}
          placeholder={accessToken ? "Query grounded workspace mind..." : "Awaiting secure credential linkage..."}
          className="flex-1 rounded-xl border border-slate-200/80 bg-white px-4 py-3 text-xs placeholder-slate-400 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500/10 focus:outline-none transition-all duration-200 shadow-sm disabled:bg-slate-50 disabled:text-slate-400 font-medium"
        />
        <button
          type="submit"
          disabled={disabled || !input.trim()}
          className="rounded-xl bg-gradient-to-r from-cyan-500 via-indigo-500 to-pink-500 hover:from-cyan-600 hover:to-pink-600 px-5 py-3 text-xs font-bold text-white shadow-md shadow-indigo-100/50 transition-all duration-300 disabled:from-slate-200 disabled:to-slate-200 disabled:shadow-none disabled:text-slate-400 flex items-center justify-center min-w-[75px] cursor-pointer glow-btn"
        >
          {busy ? (
            <svg className="animate-spin h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
          ) : (
            "SEND"
          )}
        </button>
      </form>
    </div>
  );
}

function parseInlineMarkdown(text: string): React.ReactNode[] {
  // Matches bold (**), italic (*), inline code (`) and markdown links [text](url)
  const regex = /(\*\*.*?\*\*|__.*?__|\*.*?\*|_.*?_|`.*?`|\[.*?\]\(.*?\))/g;
  const parts = text.split(regex);
  return parts.map((part, index) => {
    if ((part.startsWith("**") && part.endsWith("**")) || (part.startsWith("__") && part.endsWith("__"))) {
      return (
        <strong key={index} className="font-extrabold text-slate-900 dark:text-white">
          {part.slice(2, -2)}
        </strong>
      );
    }
    if ((part.startsWith("*") && part.endsWith("*")) || (part.startsWith("_") && part.endsWith("_"))) {
      return (
        <em key={index} className="italic text-slate-800 dark:text-slate-200">
          {part.slice(1, -1)}
        </em>
      );
    }
    if (part.startsWith("`") && part.endsWith("`")) {
      return (
        <code key={index} className="px-1.5 py-0.5 rounded bg-slate-100 border border-slate-200/60 font-mono text-[10px] text-indigo-600 font-bold dark:bg-slate-950 dark:border-slate-800 dark:text-indigo-400">
          {part.slice(1, -1)}
        </code>
      );
    }
    if (part.startsWith("[") && part.endsWith(")") && part.includes("](")) {
      const closingBracketIndex = part.indexOf("](");
      const linkText = part.slice(1, closingBracketIndex);
      const url = part.slice(closingBracketIndex + 2, -1);
      return (
        <a key={index} href={url} target="_blank" rel="noopener noreferrer" className="text-cyan-600 hover:text-cyan-700 hover:underline font-extrabold dark:text-cyan-400 transition-colors duration-200">
          {linkText}
        </a>
      );
    }
    return part;
  });
}

function renderMarkdown(text: string): React.ReactNode {
  if (!text) return null;
  const lines = text.split("\n");
  const renderedElements: React.ReactNode[] = [];
  
  let inCodeBlock = false;
  let codeBlockLines: string[] = [];
  let codeBlockLang = "";

  for (let idx = 0; idx < lines.length; idx++) {
    const line = lines[idx];
    const trimmed = line.trim();

    // Code block check
    if (trimmed.startsWith("```")) {
      if (inCodeBlock) {
        // End of code block
        const codeText = codeBlockLines.join("\n");
        renderedElements.push(
          <div key={`code-${idx}`} className="my-2.5 rounded-xl border border-slate-200 bg-slate-950 p-3.5 font-mono text-[10px] text-cyan-300 leading-normal overflow-x-auto dark:border-slate-800">
            {codeBlockLang && (
              <div className="text-[8px] font-black text-slate-500 uppercase tracking-widest border-b border-slate-800/60 pb-1.5 mb-2 select-none flex justify-between items-center">
                <span>💻 CODE: {codeBlockLang}</span>
                <span className="text-slate-600">UTF-8 SOURCE</span>
              </div>
            )}
            <pre className="whitespace-pre">{codeText}</pre>
          </div>
        );
        inCodeBlock = false;
        codeBlockLines = [];
        codeBlockLang = "";
      } else {
        // Start of code block
        inCodeBlock = true;
        codeBlockLang = trimmed.slice(3).trim().toUpperCase() || "SOURCE";
      }
      continue;
    }

    if (inCodeBlock) {
      codeBlockLines.push(line);
      continue;
    }

    if (!trimmed) {
      renderedElements.push(<div key={`empty-${idx}`} className="h-1.5" />);
      continue;
    }

    // Heading checks (H1 - H3)
    const h3Match = line.match(/^###\s+(.*)$/);
    if (h3Match) {
      renderedElements.push(
        <h4 key={`h3-${idx}`} className="text-xs font-black text-slate-900 uppercase tracking-wider mt-3 mb-1.5 flex items-center gap-1.5 dark:text-white">
          <span className="h-1.5 w-1.5 rounded-sm bg-cyan-500"></span>
          {parseInlineMarkdown(h3Match[1])}
        </h4>
      );
      continue;
    }

    const h2Match = line.match(/^##\s+(.*)$/);
    if (h2Match) {
      renderedElements.push(
        <h3 key={`h2-${idx}`} className="text-xs font-black text-slate-900 uppercase tracking-wide mt-4 mb-2 flex items-center gap-2 dark:text-white border-b border-slate-100 pb-1 dark:border-slate-800">
          <span className="h-2 w-2 rounded bg-indigo-500"></span>
          {parseInlineMarkdown(h2Match[1])}
        </h3>
      );
      continue;
    }

    const h1Match = line.match(/^#\s+(.*)$/);
    if (h1Match) {
      renderedElements.push(
        <h2 key={`h1-${idx}`} className="text-sm font-black text-slate-950 uppercase tracking-tight mt-5 mb-2.5 flex items-center gap-2 dark:text-white">
          <span className="h-2.5 w-2.5 rounded-full bg-gradient-to-tr from-cyan-500 to-indigo-500"></span>
          {parseInlineMarkdown(h1Match[1])}
        </h2>
      );
      continue;
    }

    // Numbered list item check
    const numMatch = line.match(/^\s*(\d+)\.\s+(.*)$/);
    if (numMatch) {
      const num = numMatch[1];
      const content = numMatch[2];
      renderedElements.push(
        <div key={`num-${idx}`} className="pl-6 relative my-1 text-slate-800 dark:text-slate-100 leading-relaxed font-semibold text-xs">
          <span className="absolute left-1.5 top-0.5 text-[10px] font-black text-indigo-500/80 font-mono">{num}.</span>
          {parseInlineMarkdown(content)}
        </div>
      );
      continue;
    }

    // Bullet list item check
    if (line.startsWith("* ") || line.startsWith("- ") || trimmed.startsWith("* ") || trimmed.startsWith("- ")) {
      const match = line.match(/^\s*[*+-]\s+(.*)$/);
      const content = match ? match[1] : line.replace(/^\s*[*+-]\s+/, "");
      renderedElements.push(
        <div key={`bullet-${idx}`} className="pl-5 relative my-1 text-slate-800 dark:text-slate-100 leading-relaxed font-semibold text-xs">
          <span className="absolute left-1.5 top-2 h-1.5 w-1.5 rounded-full bg-gradient-to-tr from-cyan-500 to-indigo-500"></span>
          {parseInlineMarkdown(content)}
        </div>
      );
      continue;
    }

    // Normal paragraph
    renderedElements.push(
      <p key={`p-${idx}`} className="leading-relaxed font-semibold text-slate-800 dark:text-slate-100 text-xs">
        {parseInlineMarkdown(line)}
      </p>
    );
  }

  // Handle unclosed code blocks gracefully
  if (inCodeBlock && codeBlockLines.length > 0) {
    renderedElements.push(
      <div key={`code-unclosed`} className="my-2.5 rounded-xl border border-slate-200 bg-slate-950 p-3.5 font-mono text-[10px] text-cyan-300 leading-normal overflow-x-auto dark:border-slate-800">
        <pre className="whitespace-pre">{codeBlockLines.join("\n")}</pre>
      </div>
    );
  }

  return (
    <div className="space-y-1.5">
      {renderedElements}
    </div>
  );
}

function LatencyTimer({
  streaming,
  latencyMs,
  firstTokenMs,
}: {
  streaming: boolean;
  latencyMs?: number;
  firstTokenMs?: number;
}) {
  const [seconds, setSeconds] = useState<number>(0);

  useEffect(() => {
    if (streaming) {
      const start = Date.now();
      const interval = setInterval(() => {
        setSeconds((Date.now() - start) / 1000);
      }, 50);
      return () => clearInterval(interval);
    }
  }, [streaming]);

  if (streaming) {
    return (
      <div className="text-[9px] font-mono text-cyan-500 pl-1.5 flex items-center gap-1.5 select-none animate-pulse bg-cyan-50/20 dark:bg-cyan-950/10 border border-cyan-500/10 px-2.5 py-0.5 rounded-full w-max">
        <span className="relative flex h-1.5 w-1.5">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
          <span className="relative inline-flex rounded-full h-1.5 w-1.5 bg-cyan-500"></span>
        </span>
        <span className="font-extrabold tracking-wide uppercase text-[8px]">STREAMING</span>
        <span className="text-cyan-600 dark:text-cyan-400 font-bold">{seconds.toFixed(2)}s</span>
      </div>
    );
  }

  if (latencyMs !== undefined) {
    return (
      <div className="text-[9px] font-mono text-slate-500 pl-1.5 flex items-center gap-2 select-none bg-slate-50/50 dark:bg-slate-900/40 border border-slate-200/40 dark:border-slate-800/40 px-2.5 py-0.5 rounded-full w-max">
        <div className="flex items-center gap-1">
          <span className="h-1.5 w-1.5 rounded-full bg-emerald-500"></span>
          <span className="font-extrabold tracking-wide uppercase text-[8px] text-slate-400">LATENCY</span>
          <span className="text-slate-700 dark:text-slate-300 font-bold">{(latencyMs / 1000).toFixed(2)}s</span>
        </div>
        {firstTokenMs !== undefined && (
          <div className="flex items-center gap-1 border-l border-slate-200/60 dark:border-slate-800/60 pl-2">
            <span className="font-extrabold tracking-wide uppercase text-[8px] text-slate-400">TTFT</span>
            <span className="text-slate-700 dark:text-slate-300 font-bold">{(firstTokenMs / 1000).toFixed(2)}s</span>
          </div>
        )}
      </div>
    );
  }

  return null;
}

function MessageBubble({ msg }: { msg: Msg }) {
  if (msg.role === "user") {
    return (
      <div className="flex justify-end">
        <div className="max-w-[80%] rounded-2xl rounded-tr-sm bg-gradient-to-br from-indigo-500 to-cyan-500 px-4 py-2.5 text-xs text-white shadow-sm shadow-indigo-100/40 whitespace-pre-wrap leading-relaxed font-medium">
          {msg.text}
        </div>
      </div>
    );
  }
  return (
    <div className="flex justify-start">
      <div className="max-w-[80%] space-y-2.5 w-full">
        {/* Tool Call Metadata details */}
        {msg.tools.map((t, i) => (
          <details key={i} className="group rounded-xl border border-slate-200 bg-slate-50/60 px-3.5 py-2 text-xs text-slate-600 transition-all dark:border-slate-850 dark:bg-slate-900/60 dark:text-slate-400">
            <summary className="cursor-pointer font-mono font-bold flex items-center justify-between select-none">
              <span className="flex items-center gap-1.5 text-[10px]">
                <span className="h-2 w-2 rounded-full bg-amber-400 animate-pulse"></span>
                SYS_TOOL: {t.name}
              </span>
              <span className="text-[9px] bg-slate-200/50 text-slate-500 px-2 py-0.5 rounded-md font-bold group-open:hidden">EXPAND</span>
            </summary>
            {t.args !== undefined && (
              <pre className="mt-2 overflow-x-auto whitespace-pre-wrap break-all text-[10px] bg-white p-2.5 rounded-lg border border-slate-150 font-mono text-slate-500 leading-normal dark:bg-slate-950 dark:border-slate-900 dark:text-slate-400">
                args: {JSON.stringify(t.args, null, 2)}
              </pre>
            )}
            {t.preview && (
              <pre className="mt-1.5 max-h-40 overflow-auto whitespace-pre-wrap break-all text-[10px] bg-white p-2.5 rounded-lg border border-slate-150 font-mono text-slate-500 leading-normal dark:bg-slate-950 dark:border-slate-900 dark:text-slate-400">
                {t.preview}
              </pre>
            )}
          </details>
        ))}

        {msg.groundingActive && (
          <div className="flex items-center gap-2 text-[10px] text-cyan-600 pulse-soft px-3.5 py-1.5 font-black bg-cyan-50/50 rounded-full w-max border border-cyan-100/40 tracking-wider dark:bg-cyan-950/20 dark:text-cyan-400 dark:border-cyan-900/30">
            <svg className="animate-spin h-3 w-3 text-cyan-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <span>RETRIEVING GROUNDED DATA STORES...</span>
          </div>
        )}

        {(msg.text || (msg.streaming && !msg.groundingActive)) && (
          <div className="space-y-1.5 w-full">
            <div className="rounded-2xl rounded-bl-sm bg-white border border-slate-200 px-4 py-3 text-xs text-slate-800 shadow-sm shadow-slate-100/40 leading-relaxed font-medium dark:bg-slate-900 dark:border-slate-800 dark:text-slate-100">
              {msg.text ? renderMarkdown(msg.text) : "…"}
            </div>
            <LatencyTimer streaming={msg.streaming} latencyMs={msg.latencyMs} firstTokenMs={msg.firstTokenMs} />
          </div>
        )}
      </div>
    </div>
  );
}
