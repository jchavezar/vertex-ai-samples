"use client";

import { useEffect, useState } from "react";
import { Radio } from "lucide-react";
import { PLAYERS } from "@/data/players";
import { PlayerAvatar } from "@/components/PlayerAvatar";

type ActivityEvent = {
  id: string;
  type: "pick_made" | "leader_change" | "streak" | "exact_score";
  playerId: string;
  text: string;
  fixtureId?: string;
  createdAt: number;
};

const PLAYERS_BY_ID = new Map(PLAYERS.map(p => [p.id, p]));

function relativeTime(ms: number, now: number): string {
  const dt = Math.max(0, now - ms);
  const s = Math.floor(dt / 1000);
  if (s < 60) return "ahora";
  const m = Math.floor(s / 60);
  if (m < 60) return `hace ${m}m`;
  const h = Math.floor(m / 60);
  if (h < 24) return `hace ${h}h`;
  const d = Math.floor(h / 24);
  return `hace ${d}d`;
}

export function ActivityFeed() {
  const [events, setEvents] = useState<ActivityEvent[]>([]);
  const [now, setNow] = useState<number>(() => Date.now());

  useEffect(() => {
    let alive = true;
    const fetchOnce = async () => {
      try {
        const r = await fetch("/api/activity", { cache: "no-store" });
        if (!r.ok) return;
        const j = (await r.json()) as { ok: boolean; events?: ActivityEvent[] };
        if (alive && j.ok && Array.isArray(j.events)) setEvents(j.events);
      } catch {}
    };
    fetchOnce();
    const poll = setInterval(fetchOnce, 30_000);
    const tick = setInterval(() => setNow(Date.now()), 60_000);
    return () => {
      alive = false;
      clearInterval(poll);
      clearInterval(tick);
    };
  }, []);

  if (events.length === 0) return null;
  const visible = events.slice(0, 8);

  return (
    <section className="container-app pt-2 pb-6">
      <div className="glass rounded-3xl p-4 md:p-5">
        <div className="flex items-center justify-between mb-3">
          <span className="chip"><Radio size={11} /> Lo que está pasando</span>
          <span className="text-[10px] uppercase tracking-wider text-[var(--ink-muted)] tabular-nums">
            {events.length} {events.length === 1 ? "evento" : "eventos"}
          </span>
        </div>
        <ul className="space-y-1.5">
          {visible.map(ev => {
            const player = PLAYERS_BY_ID.get(ev.playerId);
            return (
              <li
                key={ev.id}
                className="flex items-center gap-2.5 px-2 py-1.5 rounded-xl hover:bg-[var(--bg-tint)] transition-colors"
              >
                {player ? (
                  <PlayerAvatar player={player} size={24} rounded="rounded-full" textClass="text-[10px]" tint={0.2} />
                ) : (
                  <div className="w-6 h-6 rounded-full bg-[var(--bg-tint)] shrink-0" />
                )}
                <div className="min-w-0 flex-1 text-sm text-[var(--ink-soft)] truncate">
                  {ev.text}
                </div>
                <span className="text-[10px] uppercase tracking-wider text-[var(--ink-muted)] tabular-nums shrink-0">
                  {relativeTime(ev.createdAt, now)}
                </span>
              </li>
            );
          })}
        </ul>
      </div>
    </section>
  );
}
