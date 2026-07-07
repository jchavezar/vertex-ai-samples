"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { Swords, ChevronRight } from "lucide-react";
import { usePlayer } from "@/lib/player-context";
import { loadAllPredictionsFromServer } from "@/lib/predictions";
import { PLAYERS, AI_PLAYER_ID } from "@/data/players";
import { PlayerAvatar } from "@/components/PlayerAvatar";
import { CharalProfileTrigger } from "@/components/CharalProfileModal";
import { SCORING } from "@/data/tournament";

interface BracketRow {
  id: string;
  name: string;
  emoji: string;
  accent: string;
  photoDataUrl?: string;
  bracketPts: number;
  koHits: number;
  isMe: boolean;
}

export function BracketMiniLeaderboard() {
  const { currentPlayer } = usePlayer();
  const [rows, setRows] = useState<BracketRow[]>([]);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      try {
        const [preds, koRes] = await Promise.all([
          loadAllPredictionsFromServer(),
          fetch("/api/bracket/ko-results", { cache: "no-store" }).then(r => r.json()).catch(() => ({})),
        ]);
        if (cancelled) return;
        const koSlots: Record<string, string> = koRes?.slotResults ?? {};

        const computed: BracketRow[] = preds
          .filter(p => p.playerId !== AI_PLAYER_ID)
          .map(p => {
            const player = PLAYERS.find(pl => pl.id === p.playerId);
            if (!player) return null;
            let bracketPts = 0;
            let koHits = 0;

            const b = p.bracket;
            if (b?.R32) {
              for (let i = 0; i < b.R32.length; i++) {
                const pick = b.R32[i];
                const actual = koSlots[`R32-${i + 1}`];
                if (pick && actual && pick === actual) { bracketPts += SCORING.knockoutWinner.R32; koHits++; }
              }
            }
            if (b?.R16) {
              for (let i = 0; i < b.R16.length; i++) {
                const pick = b.R16[i];
                const actual = koSlots[`R16-${i + 1}`];
                if (pick && actual && pick === actual) { bracketPts += SCORING.knockoutWinner.R16; koHits++; }
              }
            }
            if (b?.QF) {
              for (let i = 0; i < b.QF.length; i++) {
                const pick = b.QF[i];
                const actual = koSlots[`QF-${i + 1}`];
                if (pick && actual && pick === actual) { bracketPts += SCORING.knockoutWinner.QF; koHits++; }
              }
            }
            if (b?.SF) {
              for (let i = 0; i < b.SF.length; i++) {
                const pick = b.SF[i];
                const actual = koSlots[`SF-${i + 1}`];
                if (pick && actual && pick === actual) { bracketPts += SCORING.knockoutWinner.SF; koHits++; }
              }
            }
            if (b?.THIRD && koSlots["THIRD"] && b.THIRD === koSlots["THIRD"]) {
              bracketPts += SCORING.knockoutWinner.THIRD; koHits++;
            }
            if (b?.FINAL && koSlots["FINAL"] && b.FINAL === koSlots["FINAL"]) {
              bracketPts += SCORING.knockoutWinner.FINAL; koHits++;
            }

            return {
              id: player.id,
              name: player.name,
              emoji: player.emoji,
              accent: player.accent,
              photoDataUrl: player.photoDataUrl ?? undefined,
              bracketPts,
              koHits,
              isMe: currentPlayer?.id === player.id,
            } as BracketRow;
          })
          .filter((r): r is NonNullable<typeof r> => r !== null)
          .sort((a, b) => b.bracketPts - a.bracketPts || b.koHits - a.koHits) as BracketRow[];

        setRows(computed);
        setLoaded(true);
      } catch {}
    }
    load();
    return () => { cancelled = true; };
  }, [currentPlayer]);

  if (!loaded) return null;
  const hasAnyPts = rows.some(r => r.bracketPts > 0);
  if (!hasAnyPts) return null;

  return (
    <section className="container-app pb-4">
      <div className="glass rounded-2xl overflow-hidden">
        <div className="px-4 py-3 flex items-center justify-between border-b border-[var(--line)]">
          <div className="flex items-center gap-2">
            <Swords size={14} className="text-[var(--accent-purple)]" />
            <span className="font-display font-bold text-sm">Bracket Eliminatorio</span>
            <span className="chip text-[10px] py-0.5 px-2">en vivo</span>
          </div>
          <Link
            href="/leaderboard"
            className="flex items-center gap-0.5 text-xs text-[var(--ink-muted)] hover:text-[var(--ink)] transition-colors"
          >
            Ver tabla completa <ChevronRight size={12} />
          </Link>
        </div>
        <ul>
          {rows.slice(0, 5).map((r, idx) => {
            const medal = idx === 0 ? "🥇" : idx === 1 ? "🥈" : idx === 2 ? "🥉" : null;
            return (
              <li
                key={r.id}
                className={`flex items-center gap-3 px-4 py-2.5 border-b border-[var(--line)] last:border-b-0 ${r.isMe ? "bg-[var(--bg-tint)]" : ""}`}
              >
                <span className="w-5 text-center text-sm">
                  {medal ?? <span className="font-display font-bold text-[var(--ink-muted)]">{idx + 1}</span>}
                </span>
                <CharalProfileTrigger player={r}>
                  <PlayerAvatar player={r} size={28} rounded="rounded-lg" textClass="text-sm" tint={0.15} />
                </CharalProfileTrigger>
                <span className="flex-1 font-semibold text-sm truncate">
                  {r.name}
                  {r.isMe && (
                    <span className="ml-1.5 text-[9px] font-bold px-1 py-0.5 rounded-full bg-[var(--ink)] text-white">tú</span>
                  )}
                </span>
                <span className="text-xs text-[var(--ink-muted)] tabular-nums">
                  {r.koHits} {r.koHits === 1 ? "acierto" : "aciertos"}
                </span>
                <span
                  className="font-display font-bold text-sm tabular-nums min-w-[40px] text-right"
                  style={{ color: r.bracketPts > 0 ? r.accent : "var(--ink-muted)" }}
                >
                  +{r.bracketPts}
                </span>
              </li>
            );
          })}
        </ul>
        <div className="px-4 py-2 text-[10px] text-[var(--ink-muted)] border-t border-[var(--line)] flex items-center gap-1.5">
          <span>R32 = {SCORING.knockoutWinner.R32}pts</span>
          <span>·</span>
          <span>R16 = {SCORING.knockoutWinner.R16}pts</span>
          <span>·</span>
          <span>QF = {SCORING.knockoutWinner.QF}pts</span>
          <span>·</span>
          <span>SF = {SCORING.knockoutWinner.SF}pts</span>
          <span>·</span>
          <span>Final = {SCORING.knockoutWinner.FINAL}pts</span>
        </div>
      </div>
    </section>
  );
}
