"use client";

import { useCallback, useRef, useState } from "react";

import { createSession, streamChat, type StreamChunk } from "@/lib/api";

type Msg =
  | { id: string; role: "user"; text: string }
  | {
      id: string;
      role: "assistant";
      text: string;
      tools: { name: string; args?: unknown; preview?: string }[];
      streaming: boolean;
    };

type Props = {
  accessToken: string | null;
  userId: string;
};

const SAMPLE_PROMPTS = [
  "Show 5 of my most recently modified files",
  "Search my Drive for documents about envato",
  "Whose Drive am I reading right now?",
];

export default function ChatPanel({ accessToken, userId }: Props) {
  const [messages, setMessages] = useState<Msg[]>([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const sessionIdRef = useRef<string | null>(null);

  const ensureSession = useCallback(async () => {
    if (!accessToken) throw new Error("Not signed in");
    if (sessionIdRef.current) return sessionIdRef.current;
    const sid = await createSession(accessToken, userId);
    sessionIdRef.current = sid;
    return sid;
  }, [accessToken, userId]);

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
      };
      setMessages((m) => [...m, userMsg, assistantMsg]);
      setInput("");

      try {
        const sid = await ensureSession();
        await streamChat(accessToken, userId, sid, text, (chunk: StreamChunk) => {
          if (chunk.type === "error" && chunk.error) {
            setError(chunk.error);
            return;
          }
          setMessages((m) =>
            m.map((msg) => {
              if (msg.id !== assistantId || msg.role !== "assistant") return msg;
              const next = { ...msg };
              if (chunk.text) next.text += chunk.text;
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
      } catch (e: unknown) {
        const err = e instanceof Error ? e.message : String(e);
        setError(err);
      } finally {
        setMessages((m) =>
          m.map((msg) => (msg.id === assistantId && msg.role === "assistant" ? { ...msg, streaming: false } : msg)),
        );
        setBusy(false);
      }
    },
    [accessToken, busy, ensureSession, userId],
  );

  const disabled = !accessToken || busy;

  return (
    <div className="flex h-[70vh] flex-col rounded-xl border border-zinc-200 bg-white shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
      <div className="flex-1 space-y-4 overflow-y-auto p-4">
        {messages.length === 0 && (
          <div className="space-y-3 text-sm text-zinc-500">
            <p>{accessToken ? "Try one of these:" : "Connect your Google Drive first."}</p>
            {accessToken && (
              <ul className="space-y-1">
                {SAMPLE_PROMPTS.map((p) => (
                  <li key={p}>
                    <button
                      className="rounded border border-zinc-200 bg-zinc-50 px-2 py-1 text-left text-zinc-700 hover:bg-zinc-100 dark:border-zinc-700 dark:bg-zinc-800 dark:text-zinc-200 dark:hover:bg-zinc-700"
                      onClick={() => send(p)}
                    >
                      {p}
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </div>
        )}

        {messages.map((m) => (
          <MessageBubble key={m.id} msg={m} />
        ))}

        {error && (
          <div className="rounded border border-red-300 bg-red-50 p-3 text-sm text-red-800 dark:border-red-800/40 dark:bg-red-950/30 dark:text-red-200">
            {error}
          </div>
        )}
      </div>

      <form
        onSubmit={(e) => {
          e.preventDefault();
          send(input);
        }}
        className="flex gap-2 border-t border-zinc-200 p-3 dark:border-zinc-800"
      >
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={disabled}
          placeholder={accessToken ? "Ask about your Drive…" : "Connect Drive first"}
          className="flex-1 rounded-md border border-zinc-300 bg-white px-3 py-2 text-sm shadow-sm focus:border-blue-500 focus:outline-none disabled:bg-zinc-100 dark:border-zinc-700 dark:bg-zinc-950 dark:disabled:bg-zinc-900"
        />
        <button
          type="submit"
          disabled={disabled || !input.trim()}
          className="rounded-md bg-blue-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-blue-700 disabled:bg-zinc-400"
        >
          {busy ? "…" : "Send"}
        </button>
      </form>
    </div>
  );
}

function MessageBubble({ msg }: { msg: Msg }) {
  if (msg.role === "user") {
    return (
      <div className="flex justify-end">
        <div className="max-w-[80%] rounded-2xl rounded-br-sm bg-blue-600 px-3 py-2 text-sm text-white whitespace-pre-wrap">
          {msg.text}
        </div>
      </div>
    );
  }
  return (
    <div className="flex justify-start">
      <div className="max-w-[80%] space-y-2">
        {msg.tools.map((t, i) => (
          <details key={i} className="rounded-md border border-zinc-200 bg-zinc-50 px-3 py-1 text-xs text-zinc-700 dark:border-zinc-700 dark:bg-zinc-800 dark:text-zinc-300">
            <summary className="cursor-pointer font-mono">
              tool: {t.name} {t.preview ? "✓" : "…"}
            </summary>
            {t.args !== undefined && (
              <pre className="mt-1 overflow-x-auto whitespace-pre-wrap break-all text-[11px] opacity-80">
                args: {JSON.stringify(t.args, null, 2)}
              </pre>
            )}
            {t.preview && (
              <pre className="mt-1 max-h-48 overflow-auto whitespace-pre-wrap break-all text-[11px] opacity-80">
                {t.preview}
              </pre>
            )}
          </details>
        ))}
        <div className="rounded-2xl rounded-bl-sm bg-zinc-100 px-3 py-2 text-sm text-zinc-900 whitespace-pre-wrap dark:bg-zinc-800 dark:text-zinc-100">
          {msg.text || (msg.streaming ? "…" : "")}
        </div>
      </div>
    </div>
  );
}
