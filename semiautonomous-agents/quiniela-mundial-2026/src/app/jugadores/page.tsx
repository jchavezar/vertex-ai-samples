"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { useRouter } from "next/navigation";
import Image from "next/image";
import { Bot, Check, KeyRound, LogOut, Pencil, Sparkles, Target, Users } from "lucide-react";
import { POT_TOTAL_MXN, type Player } from "@/data/players";
import { TEAMS, flagUrl } from "@/data/teams";
import { usePlayer } from "@/lib/player-context";
import { loadPredictions, fillStats } from "@/lib/predictions";
import { useEffect, useState } from "react";
import { PlayerAvatar } from "@/components/PlayerAvatar";
import { ProfileEditor } from "@/components/ProfileEditor";
import { PinAuthModal } from "@/components/PinAuthModal";

type Row = { id: string; pct: number; champion?: string; filled: number; total: number };

export default function PlayersPage() {
  const router = useRouter();
  const { players, currentPlayer, setPlayer } = usePlayer();
  const [rows, setRows] = useState<Row[]>([]);
  const [editing, setEditing] = useState<Player | null>(null);
  const [authTarget, setAuthTarget] = useState<Player | null>(null);
  const [loggingOut, setLoggingOut] = useState(false);

  useEffect(() => {
    const refresh = () => {
      setRows(players.map(p => {
        const s = fillStats(loadPredictions(p.id));
        return { id: p.id, pct: s.percent, champion: s.champion, filled: s.groupFilled, total: s.groupTotal };
      }));
    };
    refresh();
    const onUpd = () => refresh();
    window.addEventListener("q26:predictions-updated", onUpd);
    return () => window.removeEventListener("q26:predictions-updated", onUpd);
  }, [players]);

  function choose(p: Player) {
    if (currentPlayer && p.id === currentPlayer.id) {
      router.push("/");
      return;
    }
    // Bot AI: no PIN, always read-only — it just shows what the algorithm picked.
    if (p.isBot) {
      router.push(`/quiniela?view=${p.id}`);
      return;
    }
    // Logged in & clicking another compa → read-only view of their picks.
    // Not logged in → PIN modal so they can identify first.
    if (currentPlayer) {
      router.push(`/quiniela?view=${p.id}`);
      return;
    }
    setAuthTarget(p);
  }

  async function onLogout() {
    setLoggingOut(true);
    try { await fetch("/api/auth/logout", { method: "POST" }); } catch {}
    setPlayer(null);
    setLoggingOut(false);
  }

  return (
    <div className="container-app py-10 md:py-14">
      <div className="max-w-2xl mx-auto text-center mb-10">
        <span className="chip mb-3"><Users size={12} /> Identifícate</span>
        <h1 className="font-display text-4xl md:text-6xl font-bold leading-tight">
          ¿Quién <span className="grad-text">eres tú</span>?
        </h1>
        <p className="mt-3 text-[var(--ink-soft)]">
          Cada compa entra con su PIN de 4 dígitos. Primera vez: PIN inicial <strong>2026</strong>, luego eliges el tuyo.
        </p>
        {currentPlayer && (
          <div className="mt-5 inline-flex items-center gap-3 glass rounded-full pl-2 pr-4 py-1.5">
            <PlayerAvatar player={currentPlayer} size={28} rounded="rounded-full" textClass="text-base" tint={0.2} enableLightbox />
            <span className="text-sm">Sesión actual: <strong>{currentPlayer.name}</strong></span>
            <button
              onClick={onLogout}
              disabled={loggingOut}
              className="text-xs text-[var(--ink-muted)] hover:text-[var(--accent-coral)] flex items-center gap-1 disabled:opacity-50"
            >
              <LogOut size={12} /> {loggingOut ? "saliendo…" : "cerrar sesión"}
            </button>
          </div>
        )}
      </div>

      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4 max-w-5xl mx-auto">
        {players.map((p, idx) => {
          const data = rows.find(r => r.id === p.id);
          const isMe = currentPlayer?.id === p.id;
          return (
            <motion.div
              key={p.id}
              initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: .35, delay: idx * 0.04 }}
              whileHover={{ y: -3 }}
              className="relative"
            >
              {p.isBot && (
                <>
                  <span
                    aria-hidden
                    className="pointer-events-none absolute inset-0 rounded-3xl z-10 ai-liquid-border ai-liquid-border--lg"
                  />
                  <span className="absolute -top-2 -right-2 z-20 text-[10px] font-extrabold tracking-wider px-2.5 py-1 rounded-full bg-gradient-to-r from-[#5E5BFF] to-[#14F195] text-white shadow-lg ring-2 ring-white">
                    NUEVO
                  </span>
                </>
              )}
              <div
                className={`relative overflow-hidden glass rounded-3xl p-5 transition-shadow ${isMe ? "ring-2 ring-[var(--ink)]" : "hover:shadow-lg"}`}
                style={{
                  background: `linear-gradient(135deg, ${p.accent}10, white 60%)`,
                }}
              >
              <div
                className="absolute -top-12 -right-12 w-32 h-32 rounded-full opacity-30 blur-2xl pointer-events-none"
                style={{ background: p.accent }}
              />

              {(() => {
                const champ = data?.champion ? TEAMS.find(t => t.code === data.champion) : null;
                return (
                  <div
                    className="absolute top-3 right-12 z-10 inline-flex items-center gap-1.5 pl-1 pr-2 py-1 rounded-full bg-white/95 shadow-sm hairline-strong transition-transform hover:scale-105"
                    style={{ boxShadow: `0 0 0 1px ${p.accent}33, 0 1px 2px rgba(0,0,0,0.04)` }}
                    title={champ ? `Apuesta de campeón: ${champ.name}` : "Aún sin pick de campeón"}
                  >
                    {champ ? (
                      <>
                        <span className="relative w-4 h-4 rounded-full overflow-hidden ring-1 ring-black/5 shrink-0">
                          <Image src={flagUrl(champ.iso2, 32)} alt={champ.name} fill sizes="16px" className="object-cover" unoptimized />
                        </span>
                        <span className="text-[10px] font-bold tracking-wider tabular-nums" style={{ color: p.accent }}>{champ.code}</span>
                      </>
                    ) : (
                      <>
                        <span className="text-[11px] leading-none">🔮</span>
                        <span className="text-[10px] font-bold tracking-wider text-[var(--ink-muted)]">?</span>
                      </>
                    )}
                  </div>
                );
              })()}

              <button
                type="button"
                onClick={(e) => { e.stopPropagation(); setEditing(p); }}
                className="absolute top-3 right-3 z-10 w-8 h-8 rounded-full bg-white/90 hover:bg-white grid place-items-center shadow-sm hairline-strong text-[var(--ink-soft)] hover:text-[var(--ink)] transition-colors"
                aria-label={`Editar perfil de ${p.name}`}
                title="Editar perfil"
              >
                <Pencil size={13} />
              </button>

              <button
                type="button"
                onClick={() => choose(p)}
                className="relative w-full text-left"
              >
                <div className="flex items-center gap-4">
                  {isMe ? (
                    <Link
                      href="/perfil/foto"
                      onClick={(e) => e.stopPropagation()}
                      className="shrink-0 relative group/ava"
                      aria-label="Editar mi foto"
                      title="Editar mi foto"
                    >
                      <PlayerAvatar player={p} size={64} rounded="rounded-2xl" textClass="text-3xl" tint={0.15} className="transition-transform group-hover:scale-105" />
                      <span className="absolute -bottom-1 -right-1 w-6 h-6 rounded-full bg-white grid place-items-center shadow-md ring-2 ring-white">
                        <Sparkles size={11} style={{ color: p.accent }} />
                      </span>
                    </Link>
                  ) : (
                    <PlayerAvatar player={p} size={64} rounded="rounded-2xl" textClass="text-3xl" tint={0.15} className="transition-transform group-hover:scale-105" enableLightbox />
                  )}
                  <div className="flex-1 min-w-0 pr-8">
                    <div className="font-display text-2xl font-bold leading-none truncate">{p.name}</div>
                    <div className="text-xs text-[var(--ink-muted)] mt-1.5">
                      {data?.pct ? `${data.pct}% de la quiniela lista` : "Aún no empieza"}
                    </div>
                  </div>
                  {isMe ? (
                    <div className="w-8 h-8 rounded-full bg-[var(--ink)] text-white grid place-items-center shrink-0" title="Tu sesión">
                      <Check size={14} />
                    </div>
                  ) : p.isBot ? (
                    <div className="w-8 h-8 rounded-full bg-[var(--ink)] text-white grid place-items-center shrink-0" title="Bot — sin PIN">
                      <Bot size={14} />
                    </div>
                  ) : (
                    <div className="w-8 h-8 rounded-full bg-[var(--bg-tint)] text-[var(--ink-soft)] grid place-items-center shrink-0" title="Requiere PIN">
                      <KeyRound size={13} />
                    </div>
                  )}
                </div>

                <div className="relative mt-4">
                  <div className="flex items-center justify-between text-[10px] uppercase tracking-wider text-[var(--ink-muted)] mb-1.5">
                    <span>Fase de grupos</span>
                    <span className="tabular-nums">{data?.filled ?? 0} / {data?.total ?? 72}</span>
                  </div>
                  <div className="h-2 rounded-full bg-[var(--bg-tint)] overflow-hidden">
                    <motion.div
                      className="h-full rounded-full"
                      initial={{ width: 0 }}
                      animate={{ width: `${data?.pct ?? 0}%` }}
                      transition={{ duration: 0.6, delay: 0.1 + idx * 0.03 }}
                      style={{ background: p.accent }}
                    />
                  </div>
                </div>

                <div className="relative mt-3 flex items-center justify-end">
                  <span className="text-sm font-semibold opacity-60 group-hover:opacity-100 transition-opacity flex items-center gap-1" style={{ color: p.accent }}>
                    {isMe ? "Entrar" : p.isBot ? "Ver picks AI" : currentPlayer ? "Ver quiniela" : "Iniciar sesión"} →
                  </span>
                </div>
              </button>
              </div>
            </motion.div>
          );
        })}
      </div>

      <div className="max-w-2xl mx-auto mt-12 glass rounded-3xl p-6 flex flex-col sm:flex-row items-center gap-4 sm:gap-6 text-center sm:text-left">
        <div className="w-12 h-12 rounded-2xl grid place-items-center shrink-0" style={{ background: "linear-gradient(135deg,#D4AF37,#FFE07A)" }}>
          <Sparkles size={20} className="text-white" />
        </div>
        <div className="flex-1">
          <div className="font-display text-lg font-semibold">Bolsa: ${POT_TOTAL_MXN} MXN</div>
          <div className="text-sm text-[var(--ink-soft)]">10 compas × $100 · al ganador, todo. Tu sesión vive 30 días en este dispositivo.</div>
        </div>
        <Link href="/quiniela" className="btn btn-primary w-full sm:w-auto justify-center">
          <Target size={14} /> Ir a quiniela
        </Link>
      </div>

      {editing && (
        <ProfileEditor
          player={editing}
          open={!!editing}
          onClose={() => setEditing(null)}
        />
      )}

      <PinAuthModal
        player={authTarget}
        open={!!authTarget}
        onClose={() => setAuthTarget(null)}
        onAuthed={(p) => {
          setPlayer(p.id);
          setAuthTarget(null);
          router.push("/");
        }}
      />
    </div>
  );
}
