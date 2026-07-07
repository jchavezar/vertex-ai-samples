"use client";
// Real-time picks sync via Server-Sent Events.
// Mount with usePicksStream(playerId) in PlayerProvider — applies every
// server-push directly into localStorage and fires q26:predictions-updated
// so all components re-render without polling.
import { useEffect, useRef } from "react";
import { applyServerPicks, type PlayerPredictions } from "./predictions";

type StreamMsg = { type: "picks"; picks: Partial<PlayerPredictions> & { group?: Record<string, unknown> } };

export function usePicksStream(playerId: string | null) {
  const esRef = useRef<EventSource | null>(null);
  const retryRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    if (!playerId || typeof EventSource === "undefined") return;

    let active = true;

    function connect() {
      if (!active || !playerId) return;

      const es = new EventSource("/api/picks/stream");
      esRef.current = es;

      es.onmessage = (e) => {
        try {
          const msg = JSON.parse(e.data) as StreamMsg;
          if (msg.type === "picks" && msg.picks) {
            applyServerPicks(playerId!, msg.picks as Parameters<typeof applyServerPicks>[1]);
          }
        } catch {}
      };

      // Server self-closes at 240s → onerror fires → reconnect after 1s.
      // EventSource also auto-retries natively, but we handle it explicitly
      // to guarantee reconnection and control the delay.
      es.onerror = () => {
        es.close();
        esRef.current = null;
        if (active) {
          retryRef.current = setTimeout(connect, 1_000);
        }
      };
    }

    connect();

    return () => {
      active = false;
      esRef.current?.close();
      esRef.current = null;
      if (retryRef.current) clearTimeout(retryRef.current);
    };
  }, [playerId]);
}
