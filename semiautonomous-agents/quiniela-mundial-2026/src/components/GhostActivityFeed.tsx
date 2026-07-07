"use client";

// Ghost activity feed: social presence + micro-events from the OTHER charales.
// Renders right under the regular ActivityFeed. Polls /api/presence/live
// every 30s. Shows:
//   - online dots row (heartbeat within 90s)
//   - last 5 micro-events (from existing activity_feed collection)

import { useEffect, useMemo, useState } from "react";
import { Eye } from "lucide-react";
import { PLAYERS } from "@/data/players";
import { PlayerAvatar } from "@/components/PlayerAvatar";
import { usePlayer } from "@/lib/player-context";
import { useLocale } from "@/lib/i18n";
import type { PresenceLiveResponse } from "@/app/api/presence/live/route";

const PLAYERS_BY_ID = new Map(PLAYERS.map(p => [p.id, p]));

function relativeShort(ms: number, now: number): string {
  const dt = Math.max(0, now - ms);
  const s = Math.floor(dt / 1000);
  if (s < 60) return `${Math.max(1, s)}s`;
  const m = Math.floor(s / 60);
  if (m < 60) return `${m}m`;
  const h = Math.floor(m / 60);
  if (h < 24) return `${h}h`;
  const d = Math.floor(h / 24);
  return `${d}d`;
}

export function GhostActivityFeed() {
  const { currentPlayer, players } = usePlayer();
  const { t } = useLocale();
  const [data, setData] = useState<PresenceLiveResponse | null>(null);
  const [now, setNow] = useState<number>(() => Date.now());

  useEffect(() => {
    let alive = true;
    const fetchOnce = async () => {
      try {
        const r = await fetch("/api/presence/live", { cache: "no-store" });
        if (!r.ok) return;
        const j = (await r.json()) as PresenceLiveResponse;
        if (alive && j.ok) setData(j);
      } catch { /* ignore */ }
    };
    fetchOnce();
    const poll = setInterval(fetchOnce, 30_000);
    const tick = setInterval(() => setNow(Date.now()), 10_000);
    return () => { alive = false; clearInterval(poll); clearInterval(tick); };
  }, []);

  // Hide self from "online" row so the player doesn't see themself listed.
  const onlineOthers = useMemo(() => {
    if (!data?.online) return [];
    return data.online
      .filter(p => !currentPlayer || p.playerId !== currentPlayer.id)
      .map(p => ({ entry: p, player: players.find(pp => pp.id === p.playerId) ?? PLAYERS_BY_ID.get(p.playerId) }))
      .filter((x): x is { entry: typeof data.online[number]; player: NonNullable<typeof x.player> } => !!x.player);
  }, [data, currentPlayer, players]);

  const recent = useMemo(() => (data?.events ?? []).slice(0, 5), [data]);

  if (onlineOthers.length === 0 && recent.length === 0) return null;

  return (
    <section className="container-app pt-1 pb-6">
      <div className="glass rounded-3xl p-4 md:p-5">
        {onlineOthers.length > 0 && (
          <div className="flex items-center gap-3 mb-3">
            <div className="flex -space-x-2">
              {onlineOthers.slice(0, 6).map(({ player }) => (
                <div key={player.id} className="ring-2 ring-white rounded-full relative">
                  <PlayerAvatar player={player} size={24} rounded="rounded-full" textClass="text-[10px]" tint={0.2} />
                  <span
                    aria-hidden
                    className="absolute -bottom-0.5 -right-0.5 w-2 h-2 rounded-full ring-2 ring-white"
                    style={{ background: "#14F195" }}
                  />
                </div>
              ))}
            </div>
            <div className="text-xs text-[var(--ink-soft)] min-w-0 truncate">
              <span className="font-semibold text-[var(--ink)]">
                {onlineOthers.slice(0, 3).map(o => o.player.name).join(" · ")}
              </span>
              {onlineOthers.length > 3 ? ` +${onlineOthers.length - 3} · ` : " · "}
              <span className="text-[var(--ink-muted)]">{t("presence.online")}</span>
            </div>
          </div>
        )}

        {recent.length > 0 && (
          <ul className="space-y-1">
            {recent.map(ev => {
              const player = PLAYERS_BY_ID.get(ev.playerId);
              const verb =
                ev.type === "pick_made" ? `⌨️ ${t("presence.fillingPicks")}` :
                ev.type === "exact_score" ? `🔥 ${t("presence.justHit")}` :
                ev.type === "streak" ? `🔥 ${t("presence.justHit")}` :
                `👁️ ${t("presence.viewedCromo")}`;
              return (
                <li
                  key={ev.id}
                  className="flex items-center gap-2.5 px-2 py-1.5 rounded-xl hover:bg-[var(--bg-tint)] transition-colors"
                >
                  {player ? (
                    <PlayerAvatar player={player} size={20} rounded="rounded-full" textClass="text-[9px]" tint={0.2} />
                  ) : (
                    <Eye size={16} className="text-[var(--ink-muted)]" />
                  )}
                  <div className="min-w-0 flex-1 text-xs text-[var(--ink-soft)] truncate">
                    <span className="font-semibold text-[var(--ink)]">{player?.name ?? ev.playerId}</span>{" "}
                    {verb}
                  </div>
                  <span className="text-[10px] uppercase tracking-wider text-[var(--ink-muted)] tabular-nums shrink-0">
                    {relativeShort(ev.createdAt, now)}
                  </span>
                </li>
              );
            })}
          </ul>
        )}
      </div>
    </section>
  );
}
