"use client";

import { useEffect, useRef, useState } from "react";

const SCOPE = "https://www.googleapis.com/auth/drive.readonly";

type Props = {
  clientId: string;
  onToken: (token: string) => void;
  signedIn: boolean;
  onSignOut: () => void;
};

export default function DriveAuthButton({ clientId, onToken, signedIn, onSignOut }: Props) {
  const tokenClientRef = useRef<ReturnType<NonNullable<Window["google"]>["accounts"]["oauth2"]["initTokenClient"]> | null>(null);
  const [ready, setReady] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Wait for the GIS script (loaded in app/layout.tsx) to attach window.google.
    let cancelled = false;
    const wait = setInterval(() => {
      if (cancelled) return;
      if (window.google?.accounts?.oauth2 && clientId) {
        tokenClientRef.current = window.google.accounts.oauth2.initTokenClient({
          client_id: clientId,
          scope: SCOPE,
          callback: (resp) => {
            if (resp.error || !resp.access_token) {
              setError(resp.error_description || resp.error || "OAuth failed");
              return;
            }
            setError(null);
            onToken(resp.access_token);
          },
        });
        setReady(true);
        clearInterval(wait);
      }
    }, 150);
    return () => {
      cancelled = true;
      clearInterval(wait);
    };
  }, [clientId, onToken]);

  if (!clientId) {
    return (
      <div className="rounded-md border border-amber-500/40 bg-amber-50 px-3 py-2 text-sm text-amber-900 dark:bg-amber-950/30 dark:text-amber-200">
        Set <code className="font-mono">NEXT_PUBLIC_GOOGLE_CLIENT_ID</code> in <code>frontend/.env.local</code>.
      </div>
    );
  }

  if (signedIn) {
    return (
      <button
        onClick={onSignOut}
        className="rounded-md border border-zinc-300 bg-white px-3 py-1.5 text-sm font-medium text-zinc-700 shadow-sm hover:bg-zinc-50 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-200 dark:hover:bg-zinc-800"
      >
        Disconnect Drive
      </button>
    );
  }

  return (
    <div className="flex flex-col items-end gap-1">
      <button
        disabled={!ready}
        onClick={() => tokenClientRef.current?.requestAccessToken({ prompt: "consent" })}
        className="inline-flex items-center gap-2 rounded-md bg-blue-600 px-3 py-1.5 text-sm font-semibold text-white shadow-sm hover:bg-blue-700 disabled:bg-zinc-400"
      >
        <svg viewBox="0 0 24 24" className="h-4 w-4" aria-hidden="true">
          <path fill="#fff" d="M12 11v3h7.6c-.3 1.7-2 5-7.6 5-4.6 0-8.3-3.8-8.3-8.5S7.4 2 12 2c2.6 0 4.4 1.1 5.4 2.1l3.7-3.6C18.7-1.6 15.6-3 12-3 5.4-3 0 2.4 0 9s5.4 12 12 12c6.9 0 11.5-4.9 11.5-11.7 0-.8-.1-1.4-.2-2H12z"/>
        </svg>
        {ready ? "Connect Google Drive" : "Loading…"}
      </button>
      {error && <p className="text-xs text-red-600">{error}</p>}
    </div>
  );
}
