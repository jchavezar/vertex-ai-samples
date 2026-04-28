"use client";

import { useCallback, useMemo, useState } from "react";

import ChatPanel from "@/components/ChatPanel";
import DriveAuthButton from "@/components/DriveAuthButton";

export default function Home() {
  const clientId = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID ?? "";
  const [accessToken, setAccessToken] = useState<string | null>(null);

  const userId = useMemo(
    () => (typeof window === "undefined" ? "anon" : (window.localStorage.getItem("uid") ?? newUid())),
    [],
  );

  const onToken = useCallback((tok: string) => setAccessToken(tok), []);
  const onSignOut = useCallback(() => {
    if (accessToken && window.google?.accounts?.oauth2) {
      window.google.accounts.oauth2.revoke(accessToken);
    }
    setAccessToken(null);
  }, [accessToken]);

  return (
    <main className="mx-auto max-w-3xl p-6">
      <header className="mb-6 flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">ADK Drive Assistant</h1>
          <p className="mt-1 text-sm text-zinc-500">
            Custom OAuth UI · Google Identity Services in the browser · Vertex AI Agent Engine
          </p>
        </div>
        <DriveAuthButton
          clientId={clientId}
          onToken={onToken}
          signedIn={!!accessToken}
          onSignOut={onSignOut}
        />
      </header>

      <ChatPanel accessToken={accessToken} userId={userId} />

      <footer className="mt-6 text-xs text-zinc-500">
        Token stays in this browser tab. The backend forwards it once per session into the deployed
        agent's session state and the agent calls Drive API directly.
      </footer>
    </main>
  );
}

function newUid(): string {
  const id = `u-${Math.random().toString(36).slice(2, 10)}`;
  if (typeof window !== "undefined") window.localStorage.setItem("uid", id);
  return id;
}
