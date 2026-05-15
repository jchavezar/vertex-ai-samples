"use client";

import { useEffect, useRef, useState } from "react";
import { AccountInfo } from "@azure/msal-browser";
import { getMsal, loginRequest } from "@/lib/msal";
import { backendHealth, createSession, streamChat, AgentEvent } from "@/lib/api";
import { ToolEvent } from "@/components/ToolEvent";

type Bubble =
  | { kind: "user"; text: string }
  | { kind: "agent"; text: string; events: AgentEvent[] }
  | { kind: "system"; text: string };

export default function Page() {
  const [account, setAccount] = useState<AccountInfo | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [bubbles, setBubbles] = useState<Bubble[]>([]);
  const [input, setInput] = useState("find documents about agent gateway");
  const [busy, setBusy] = useState(false);
  const [health, setHealth] = useState<any>(null);
  const endRef = useRef<HTMLDivElement>(null);

  // Initialize MSAL once on mount; consume any redirect response from a
  // prior loginRedirect() so we land in a signed-in state without a popup.
  // CRITICAL: do NOT touch sessionStorage before handleRedirectPromise() —
  // MSAL stores the PKCE verifier there and clearing it makes the redirect
  // response un-consumable.
  useEffect(() => {
    (async () => {
      const m = getMsal();
      await m.initialize();
      try {
        const resp = await m.handleRedirectPromise();
        if (resp?.account) {
          m.setActiveAccount(resp.account);
          setAccount(resp.account);
          setToken(resp.accessToken);
          const s = await createSession(resp.accessToken, resp.account.username);
          setSessionId(s.session_id);
          pushSystem(`Signed in as ${resp.account.username}. Session: ${s.session_id}`);
        } else {
          const accs = m.getAllAccounts();
          if (accs.length) {
            m.setActiveAccount(accs[0]);
            setAccount(accs[0]);
            try {
              const t = await m.acquireTokenSilent({ ...loginRequest, account: accs[0] });
              setToken(t.accessToken);
              const s = await createSession(t.accessToken, accs[0].username);
              setSessionId(s.session_id);
              pushSystem(`Resumed session for ${accs[0].username}. Session: ${s.session_id}`);
            } catch {
              pushSystem(`Found cached account ${accs[0].username} but token expired — click Sign in.`);
            }
          }
        }
      } catch (e: any) {
        pushSystem(`MSAL init error: ${e?.message || e}`);
      }
      try { setHealth(await backendHealth()); } catch { /* backend not up yet */ }
    })();
  }, []);

  useEffect(() => { endRef.current?.scrollIntoView({ behavior: "smooth" }); }, [bubbles]);

  async function signIn() {
    const m = getMsal();
    try {
      // Full-page redirect flow — more reliable than popups inside embedded
      // browsers and avoids the BrowserAuthError: interaction_in_progress
      // that pops up when a popup gets closed prematurely.
      await m.loginRedirect(loginRequest);
    } catch (e: any) {
      pushSystem(`Sign-in failed: ${e?.message || e}`);
    }
  }

  async function refreshToken(): Promise<string> {
    const m = getMsal();
    const acc = account ?? m.getAllAccounts()[0];
    if (!acc) throw new Error("not signed in");
    const r = await m.acquireTokenSilent({ ...loginRequest, account: acc });
    setToken(r.accessToken);
    return r.accessToken;
  }

  function pushSystem(text: string) {
    setBubbles(b => [...b, { kind: "system", text }]);
  }

  async function send() {
    if (!input.trim()) return;
    if (!sessionId) {
      pushSystem("No session. Click 'Sign in with Microsoft' first.");
      return;
    }
    let tok = token;
    if (!tok) tok = await refreshToken();

    const userText = input;
    setInput("");
    setBubbles(b => [...b, { kind: "user", text: userText }, { kind: "agent", text: "", events: [] }]);
    setBusy(true);

    try {
      const stream = streamChat({ message: userText, sessionId, userId: account?.username });
      for await (const ev of stream) {
        if (ev.type === "done") break;
        setBubbles(b => {
          const copy = b.slice();
          const last = copy[copy.length - 1];
          if (last && last.kind === "agent") {
            const updated = { ...last };
            if (ev.type === "error") updated.text += `\n[error] ${ev.error}`;
            if (ev.type === "event") {
              if (ev.text) updated.text += ev.text;
              if (ev.tool_call || ev.tool_result) updated.events = [...updated.events, ev];
            }
            copy[copy.length - 1] = updated;
          }
          return copy;
        });
      }
    } catch (e: any) {
      pushSystem(`Stream failed: ${e.message || e}`);
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="mx-auto max-w-4xl px-4 py-6">
      <header className="mb-4 flex items-center gap-3">
        <div className="text-lg font-semibold">Agent Gateway demo</div>
        <div className="text-xs opacity-60">{health ? `backend OK · AE ${health.agent_engine_configured ? "wired" : "MISSING"}` : "backend ?"}</div>
        <div className="ml-auto flex items-center gap-2">
          {!account ? (
            <button onClick={signIn} className="rounded bg-blue-600 px-3 py-1 text-sm font-medium hover:bg-blue-500">Sign in with Microsoft</button>
          ) : (
            <div className="text-xs opacity-80">{account.username}</div>
          )}
        </div>
      </header>

      <section className="rounded border border-white/10 bg-black/40 p-3">
        <div className="space-y-3 max-h-[60vh] overflow-y-auto pr-1">
          {bubbles.length === 0 && (
            <div className="text-sm opacity-50">
              Sign in with Microsoft to start a session. Then ask: <code>find documents about agent gateway</code>.
              The pane below will show streamed text + every tool call + every tool result so you can verify
              the auth path end-to-end.
            </div>
          )}
          {bubbles.map((b, i) => (
            <div key={i} className={
              b.kind === "user" ? "text-right" :
              b.kind === "system" ? "text-xs opacity-60" : ""
            }>
              <div className={
                b.kind === "user" ? "inline-block max-w-[80%] rounded bg-blue-600/20 px-3 py-2 text-sm" :
                b.kind === "system" ? "" :
                "block max-w-[95%] rounded bg-white/5 px-3 py-2 text-sm"
              }>
                <div className="whitespace-pre-wrap">{b.text || (b.kind === "agent" && busy ? "…" : "")}</div>
                {b.kind === "agent" && b.events.map((ev, j) =>
                  ev.type === "event" && ev.tool_call ? (
                    <ToolEvent key={j} kind="call" name={ev.tool_call.name} body={ev.tool_call.args} />
                  ) : ev.type === "event" && ev.tool_result ? (
                    <ToolEvent key={j} kind="result" name={ev.tool_result.name} body={ev.tool_result.preview} />
                  ) : null
                )}
              </div>
            </div>
          ))}
          <div ref={endRef} />
        </div>
        <div className="mt-3 flex gap-2">
          <input
            className="flex-1 rounded border border-white/10 bg-black/40 px-3 py-2 text-sm outline-none focus:border-white/30"
            value={input} onChange={e => setInput(e.target.value)}
            onKeyDown={e => { if (e.key === "Enter" && !e.shiftKey && !busy) { e.preventDefault(); void send(); } }}
            placeholder={sessionId ? "Ask Doc Search…" : "Sign in first"}
            disabled={!sessionId || busy}
          />
          <button onClick={() => void send()} disabled={!sessionId || busy}
            className="rounded bg-emerald-600 px-3 py-2 text-sm font-medium hover:bg-emerald-500 disabled:opacity-40">
            {busy ? "…" : "Send"}
          </button>
        </div>
      </section>

      <footer className="mt-4 text-xs opacity-40">
        Token-pre-injection mode (state["{health?.session_token_key || "temp:sharepoint_3lo"}"]) ·
        backend = {process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8080"} ·
        engine = {health?.agent_engine_resource || "—"}
      </footer>
    </main>
  );
}
