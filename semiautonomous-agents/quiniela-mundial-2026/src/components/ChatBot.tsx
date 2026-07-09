"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Bot, X, Send, Loader2, Sparkles, ShieldCheck, KeyRound, LogOut, ChevronLeft, Wrench } from "lucide-react";
import { ChatMarkdown } from "@/components/ChatMarkdown";
import { MaintenanceChat } from "@/components/MaintenanceChat";

import { PLAYERS, type Player } from "@/data/players";
import { PlayerAvatar } from "@/components/PlayerAvatar";
import { track } from "@/lib/track";

type Msg = { role: "user" | "assistant"; text: string; streaming?: boolean };
type Screen = "pick-player" | "enter-pin" | "setup-pin" | "chat" | "change-pin";

const SUGGESTIONS = [
  "¿Cuándo arranca el Mundial?",
  "¿Quién es favorito a campeón?",
  "Reglas de la quiniela",
  "Próximos amistosos de México",
];

type HistoryEvent = { role: string | null; text: string | null };

async function fetchHistory(): Promise<Msg[]> {
  try {
    const r = await fetch("/api/chat/history", { cache: "no-store" });
    if (!r.ok) return [];
    const j = await r.json();
    if (!j?.ok || !Array.isArray(j.history?.messages)) return [];
    return (j.history.messages as HistoryEvent[])
      .filter(m => (m.text ?? "").trim().length > 0)
      .map<Msg>(m => ({
        role: m.role === "user" ? "user" : "assistant",
        text: m.text!,
      }));
  } catch {
    return [];
  }
}

export function ChatBot() {
  const [open, setOpen] = useState(false);
  const [screen, setScreen] = useState<Screen>("pick-player");
  const [pickedPlayer, setPickedPlayer] = useState<Player | null>(null);
  const [authedPlayer, setAuthedPlayer] = useState<Player | null>(null);
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<Msg[]>([]);
  const [busy, setBusy] = useState(false);
  const [authErr, setAuthErr] = useState<string | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const [historyLoaded, setHistoryLoaded] = useState(false);
  const [pendingSeed, setPendingSeed] = useState<string | null>(null);
  const [maintMode, setMaintMode] = useState(false);
  // RAF-based streaming: accumulate chunks in a ref, flush to state at 60fps
  const streamAccRef = useRef("");
  const streamRafRef = useRef<number | null>(null);
  // Conversación es permanente. Al abrir solo se renderiza la ventana visible
  // (los últimos PAGE_SIZE); más se cargan automáticamente al hacer scroll
  // hacia arriba — sin botón.
  const PAGE_SIZE = 12;
  const [visibleCount, setVisibleCount] = useState(PAGE_SIZE);
  // Cuando el usuario sube en la conversación, deja de "stickear" al fondo
  // para no arrastrarlo de vuelta cuando llega un nuevo token.
  const stickToBottomRef = useRef(true);

  // External opener: pages dispatch q26:open-chat to launch a guided flow.
  useEffect(() => {
    function handle(e: Event) {
      const detail = (e as CustomEvent).detail as { seedMessage?: string } | undefined;
      setOpen(true);
      if (detail?.seedMessage) setPendingSeed(detail.seedMessage);
    }
    window.addEventListener("q26:open-chat", handle as EventListener);
    return () => window.removeEventListener("q26:open-chat", handle as EventListener);
  }, []);

  useEffect(() => {
    if (open) track("chat_open");
  }, [open]);

  // Probe existing session on first open.
  useEffect(() => {
    if (!open) return;
    if (authedPlayer) return;
    (async () => {
      try {
        const r = await fetch("/api/auth/me", { cache: "no-store" });
        const j = await r.json();
        if (j.authed) {
          const p = PLAYERS.find(x => x.id === j.playerId);
          if (p) {
            setAuthedPlayer(p);
            setScreen("chat");
            return;
          }
        }
        setScreen("pick-player");
      } catch {
        setScreen("pick-player");
      }
    })();
  }, [open, authedPlayer]);

  // Hydrate chat history from Firestore once authenticated.
  useEffect(() => {
    if (!authedPlayer || historyLoaded) return;
    let cancelled = false;
    (async () => {
      const prior = await fetchHistory();
      if (cancelled) return;
      if (prior.length > 0) setMessages(prior);
      setHistoryLoaded(true);
    })();
    return () => { cancelled = true; };
  }, [authedPlayer, historyLoaded]);

  useEffect(() => {
    if (open && screen === "chat") setTimeout(() => inputRef.current?.focus(), 200);
  }, [open, screen]);

  // Fire pending seed message once chat is authenticated + history loaded.
  useEffect(() => {
    if (!open || !pendingSeed) return;
    if (screen !== "chat" || !authedPlayer || !historyLoaded || busy) return;
    const seed = pendingSeed;
    setPendingSeed(null);
    setTimeout(() => { void send(seed); }, 120);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open, pendingSeed, screen, authedPlayer, historyLoaded, busy]);

  // Mantener pegado al fondo SOLO si el usuario no se ha movido hacia arriba.
  // Sin animación: el smooth-scroll en cada token causaba "temblor" cuando el
  // streaming reescribe el último burbuja muchas veces por segundo.
  useEffect(() => {
    if (!stickToBottomRef.current) return;
    const el = scrollRef.current;
    if (!el) return;
    el.scrollTop = el.scrollHeight;
  }, [messages]);

  // Al abrir el panel, ir directamente al fondo (sin animación) y resetear el
  // "stick" para que el siguiente stream lo siga.
  useEffect(() => {
    if (!open) return;
    stickToBottomRef.current = true;
    const id = requestAnimationFrame(() => {
      const el = scrollRef.current;
      if (el) el.scrollTop = el.scrollHeight;
    });
    return () => cancelAnimationFrame(id);
  }, [open, historyLoaded]);

  // Auto-grow the composer textarea up to max-h-40 (160px).
  useEffect(() => {
    const el = inputRef.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = Math.min(el.scrollHeight, 160) + "px";
  }, [input]);

  async function send(textOverride?: string) {
    const text = (textOverride ?? input).trim();
    if (!text || busy) return;
    track("chat_message_sent");
    setInput("");
    setBusy(true);

    const next: Msg[] = [...messages, { role: "user", text }, { role: "assistant", text: "", streaming: true }];
    setMessages(next);

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          messages: next.filter(m => !m.streaming).map(({ role, text }) => ({ role, text })),
        }),
      });

      if (res.status === 401) {
        setAuthedPlayer(null);
        setScreen("pick-player");
        setMessages([]);
        setHistoryLoaded(false);
        return;
      }

      if (!res.ok || !res.body) {
        const err = await res.text().catch(() => "");
        setMessages(prev => {
          const copy = [...prev];
          const last = copy[copy.length - 1];
          if (last?.streaming) {
            last.text = `Tuve un problema (${res.status}). ${err.slice(0, 120)}`;
            last.streaming = false;
          }
          return copy;
        });
        return;
      }

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      streamAccRef.current = "";

      // Flush accumulated text to React state — called via RAF (max 60fps).
      const flush = () => {
        streamRafRef.current = null;
        const text = streamAccRef.current;
        setMessages(prev => {
          const copy = [...prev];
          const last = copy[copy.length - 1];
          if (last?.streaming) last.text = text;
          return copy;
        });
      };

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        streamAccRef.current += decoder.decode(value, { stream: true });
        // Schedule at most one RAF per frame instead of setState on every chunk.
        if (streamRafRef.current === null) {
          streamRafRef.current = requestAnimationFrame(flush);
        }
      }

      // Cancel any pending RAF and do a final synchronous flush.
      if (streamRafRef.current !== null) {
        cancelAnimationFrame(streamRafRef.current);
        streamRafRef.current = null;
      }
      setMessages(prev => {
        const copy = [...prev];
        const last = copy[copy.length - 1];
        if (last?.streaming) { last.text = streamAccRef.current; last.streaming = false; }
        return copy;
      });
    } catch (e) {
      setMessages(prev => {
        const copy = [...prev];
        const last = copy[copy.length - 1];
        if (last?.streaming) {
          last.text = `Error: ${(e as Error).message}`;
          last.streaming = false;
        }
        return copy;
      });
    } finally {
      setBusy(false);
    }
  }

  function onKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      send();
    }
  }

  async function onPickPlayer(p: Player) {
    setPickedPlayer(p);
    setAuthErr(null);
    try {
      const r = await fetch(`/api/auth/status?playerId=${encodeURIComponent(p.id)}`, { cache: "no-store" });
      const j = await r.json();
      if (j.ok && j.hasCustomPin) setScreen("enter-pin");
      else setScreen("setup-pin");
    } catch {
      setScreen("enter-pin");
    }
  }

  async function onLogout() {
    try { await fetch("/api/auth/logout", { method: "POST" }); } catch {}
    setAuthedPlayer(null);
    setMessages([]);
    setHistoryLoaded(false);
    setVisibleCount(PAGE_SIZE);
    setScreen("pick-player");
    setMaintMode(false);
  }

  const loadMore = useCallback(() => {
    const el = scrollRef.current;
    if (!el) return;
    const prevHeight = el.scrollHeight;
    const prevTop = el.scrollTop;
    setVisibleCount(c => c + PAGE_SIZE);
    // Tras el re-render, restituir la posición de lectura para que el nuevo
    // contenido entre por arriba sin patearle el ojo al usuario.
    requestAnimationFrame(() => {
      const cur = scrollRef.current;
      if (!cur) return;
      cur.scrollTop = cur.scrollHeight - prevHeight + prevTop;
    });
  }, []);

  // Listener de scroll: (a) si llega cerca del tope, auto-carga más; (b)
  // actualiza stickToBottomRef según qué tan cerca del fondo está.
  const onScroll = useCallback((e: React.UIEvent<HTMLDivElement>) => {
    const el = e.currentTarget;
    const distFromBottom = el.scrollHeight - el.scrollTop - el.clientHeight;
    stickToBottomRef.current = distFromBottom < 80;
    if (el.scrollTop < 64) {
      setVisibleCount(c => {
        if (c >= messages.length) return c;
        const prevHeight = el.scrollHeight;
        const prevTop = el.scrollTop;
        const next = c + PAGE_SIZE;
        requestAnimationFrame(() => {
          const cur = scrollRef.current;
          if (!cur) return;
          cur.scrollTop = cur.scrollHeight - prevHeight + prevTop;
        });
        return next;
      });
    }
  }, [messages.length]);

  return (
    <>
      {/* Floating button */}
      <button
        onClick={() => setOpen(true)}
        aria-label="Abrir Charal Bot"
        style={{
          right: "max(1rem, env(safe-area-inset-right))",
          touchAction: "manipulation",
        }}
        className="group fixed z-[70] bottom-24 md:bottom-5 h-14 pl-3 pr-4 rounded-full bg-[var(--ink)] text-white shadow-2xl flex items-center gap-2 md:hover:scale-105 md:active:scale-95 md:transition-transform select-none border border-[var(--accent-mint)]/30"
      >
        <span className="relative w-9 h-9 rounded-full bg-white/15 grid place-items-center">
          <Bot size={20} className="text-[var(--accent-mint)]" />
          <span className="absolute -top-0.5 -right-0.5 w-2.5 h-2.5 rounded-full bg-[var(--accent-mint)] ring-2 ring-[var(--ink)] animate-pulse" />
        </span>
        <span className="text-sm font-display font-semibold tracking-wide">Charal Bot</span>
      </button>

      <AnimatePresence>
        {open && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setOpen(false)}
              className="fixed inset-0 z-[95] bg-black/60 backdrop-blur-md"
            />

            <motion.div
              initial={{ y: 24, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              exit={{ y: 24, opacity: 0 }}
              transition={{ type: "spring", damping: 28, stiffness: 280 }}
              style={{
                top: "max(env(safe-area-inset-top), 0.75rem)",
                bottom: "max(env(safe-area-inset-bottom), 0.75rem)",
                left: "max(env(safe-area-inset-left), 0.75rem)",
                right: "max(env(safe-area-inset-right), 0.75rem)",
              }}
              className="fixed z-[100] bg-[var(--bg-elev)] text-[var(--ink)] shadow-2xl flex flex-col rounded-3xl overflow-hidden ring-1 ring-[var(--accent-mint)]/30
                         md:!inset-auto md:!bottom-5 md:!right-5 md:!left-auto md:!top-auto md:w-[420px] md:h-[640px]"
            >
              {/* Header */}
              <div className="flex items-center gap-3 px-4 py-3 border-b border-[var(--line)] bg-[var(--bg-elev)]">
                {(screen === "enter-pin" || screen === "setup-pin") && (
                  <button
                    onClick={() => { setScreen("pick-player"); setPickedPlayer(null); setAuthErr(null); }}
                    aria-label="Atrás"
                    className="w-9 h-9 rounded-full grid place-items-center hover:bg-[var(--bg-tint)] shrink-0"
                  >
                    <ChevronLeft size={18} />
                  </button>
                )}
                <div className="w-10 h-10 rounded-full bg-[var(--ink)] grid place-items-center text-[var(--accent-mint)] shrink-0 border border-[var(--accent-mint)]/40 shadow-[0_0_12px_rgba(0,245,155,0.2)]">
                  <Sparkles size={18} />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="font-display font-bold text-sm">Charal Bot</div>
                  <div className="text-[11px] text-[var(--ink-muted)] truncate">
                    {screen === "chat" && authedPlayer ? `Sesión de ${authedPlayer.name}` : "Powered by Gemini · Google Search"}
                  </div>
                </div>
                {screen === "chat" && authedPlayer?.id === "jesus" && !maintMode && (
                  <button
                    onClick={() => setMaintMode(true)}
                    aria-label="Entrar a modo mantenimiento"
                    title="Modo mantenimiento — hablar con Claude Code"
                    className="relative h-9 pl-2 pr-2.5 rounded-full flex items-center gap-1.5 shrink-0 transition-all border bg-gradient-to-r from-zinc-900 to-zinc-700 border-zinc-700 text-white"
                  >
                    <Wrench size={14} />
                    <span className="text-[10.5px] font-extrabold uppercase tracking-wider leading-none">
                      Mant.
                    </span>
                  </button>
                )}
                <button
                  onClick={() => setOpen(false)}
                  aria-label="Cerrar"
                  className="w-9 h-9 rounded-full grid place-items-center hover:bg-[var(--bg-tint)] shrink-0"
                >
                  <X size={18} />
                </button>
              </div>

              {/* Body */}
              <div className="flex-1 min-h-0 flex flex-col">
                {screen === "pick-player" && (
                  <PickPlayer onPick={onPickPlayer} />
                )}

                {screen === "enter-pin" && pickedPlayer && (
                  <EnterPin
                    player={pickedPlayer}
                    error={authErr}
                    onCancel={() => { setScreen("pick-player"); setPickedPlayer(null); setAuthErr(null); }}
                    onSubmit={async pin => {
                      setAuthErr(null);
                      const r = await fetch("/api/auth/verify", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ playerId: pickedPlayer.id, pin }),
                      });
                      const j = await r.json().catch(() => ({}));
                      if (j.ok) {
                        setAuthedPlayer(pickedPlayer);
                        setScreen("chat");
                        window.dispatchEvent(new CustomEvent("q26:reauthed", { detail: pickedPlayer.id }));
                        return;
                      }
                      if (j.error === "must_setup") {
                        setScreen("setup-pin");
                        return;
                      }
                      setAuthErr(j.error === "wrong_pin" ? "PIN incorrecto." : `Error: ${j.error || r.status}`);
                    }}
                  />
                )}

                {screen === "setup-pin" && pickedPlayer && (
                  <SetupPin
                    player={pickedPlayer}
                    error={authErr}
                    onSubmit={async (defaultPin, newPin, confirmPin) => {
                      setAuthErr(null);
                      const r = await fetch("/api/auth/setup", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ playerId: pickedPlayer.id, defaultPin, newPin, confirmPin }),
                      });
                      const j = await r.json().catch(() => ({}));
                      if (j.ok) {
                        setAuthedPlayer(pickedPlayer);
                        setScreen("chat");
                        window.dispatchEvent(new CustomEvent("q26:reauthed", { detail: pickedPlayer.id }));
                        return;
                      }
                      const map: Record<string, string> = {
                        wrong_default_pin: "PIN inicial incorrecto.",
                        pins_dont_match: "Los PINs no coinciden.",
                        pin_equals_default: "Elige un PIN distinto al inicial.",
                        invalid_new_pin: "El PIN nuevo debe ser de 4 dígitos.",
                        already_setup: "Este jugador ya tiene un PIN. Inicia sesión.",
                      };
                      setAuthErr(map[j.error] || `Error: ${j.error || r.status}`);
                      if (j.error === "already_setup") setTimeout(() => setScreen("enter-pin"), 1500);
                    }}
                  />
                )}

                {screen === "chat" && authedPlayer && !maintMode && (
                  <ChatView
                    scrollRef={scrollRef}
                    messages={messages}
                    visibleCount={visibleCount}
                    onScroll={onScroll}
                    onSuggestion={s => send(s)}
                  />
                )}

                {screen === "chat" && authedPlayer?.id === "jesus" && maintMode && (
                  <MaintenanceChat onExit={() => setMaintMode(false)} />
                )}

                {screen === "change-pin" && authedPlayer && (
                  <ChangePin
                    onBack={() => { setAuthErr(null); setScreen("chat"); }}
                    onLogout={onLogout}
                  />
                )}
              </div>

              {/* Composer (only on chat screen, hidden in maintenance mode) */}
              {screen === "chat" && !maintMode && (
                <div className="p-3 border-t border-[var(--hairline)] bg-white">
                  <div className="flex items-end gap-2 rounded-3xl px-3 py-2 bg-[var(--bg-tint)] transition-shadow">
                    <textarea
                      ref={inputRef}
                      value={input}
                      onChange={e => setInput(e.target.value)}
                      onKeyDown={onKeyDown}
                      rows={1}
                      placeholder="Escribe tu pregunta…"
                      style={{ WebkitTapHighlightColor: "transparent", outline: "none", boxShadow: "none" }}
                      className="flex-1 bg-transparent text-base md:text-sm resize-none outline-none focus:outline-none focus-visible:outline-none focus:ring-0 placeholder:text-[var(--ink-muted)] py-1.5 max-h-40 leading-snug"
                    />
                    <button
                      onClick={() => send()}
                      disabled={!input.trim() || busy}
                      aria-label="Enviar"
                      className="w-9 h-9 rounded-full bg-[var(--ink)] text-white grid place-items-center disabled:opacity-30 disabled:cursor-not-allowed transition-opacity shrink-0"
                    >
                      {busy ? <Loader2 size={16} className="animate-spin" /> : <Send size={16} />}
                    </button>
                  </div>
                </div>
              )}
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </>
  );
}

function PickPlayer({ onPick }: { onPick: (p: Player) => void }) {
  return (
    <div className="flex-1 overflow-y-auto p-4">
      <div className="text-center mb-4">
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-[var(--bg-tint)] text-[11px] font-semibold uppercase tracking-wider text-[var(--ink-soft)]">
          <ShieldCheck size={12} /> Acceso restringido
        </div>
        <p className="mt-3 text-sm text-[var(--ink-soft)] leading-relaxed">
          ¿Quién eres? Selecciona tu nombre para entrar al chat de la quiniela.
        </p>
      </div>
      <div className="grid grid-cols-3 gap-2">
        {PLAYERS.map(p => (
          <button
            key={p.id}
            onClick={() => onPick(p)}
            className="flex flex-col items-center gap-1.5 p-2.5 rounded-2xl hairline-strong bg-white hover:bg-[var(--bg-tint)] transition-colors active:scale-95"
          >
            <PlayerAvatar player={p} size={44} className="rounded-2xl" />
            <span className="text-[11px] font-semibold truncate w-full text-center">{p.name}</span>
          </button>
        ))}
      </div>
    </div>
  );
}

function PinPad({
  value,
  onChange,
  autoFocus,
}: {
  value: string;
  onChange: (v: string) => void;
  autoFocus?: boolean;
}) {
  const ref = useRef<HTMLInputElement>(null);
  useEffect(() => {
    if (autoFocus) setTimeout(() => ref.current?.focus(), 100);
  }, [autoFocus]);
  return (
    <div className="relative">
      <input
        ref={ref}
        inputMode="numeric"
        pattern="[0-9]*"
        autoComplete="one-time-code"
        maxLength={4}
        value={value}
        onChange={e => onChange(e.target.value.replace(/\D/g, "").slice(0, 4))}
        className="absolute inset-0 opacity-0 cursor-pointer"
        aria-label="PIN"
      />
      <div className="flex gap-2 justify-center" onClick={() => ref.current?.focus()}>
        {Array.from({ length: 4 }).map((_, i) => (
          <div
            key={i}
            className={`w-12 h-14 rounded-2xl border-2 grid place-items-center text-2xl font-display font-bold transition-all ${
              i < value.length
                ? "border-[var(--ink)] bg-[var(--ink)] text-white"
                : i === value.length
                ? "border-[var(--ink)] bg-white text-[var(--ink)] animate-pulse"
                : "border-[var(--hairline)] bg-white text-[var(--ink-muted)]"
            }`}
          >
            {i < value.length ? "•" : ""}
          </div>
        ))}
      </div>
    </div>
  );
}

function EnterPin({
  player,
  error,
  onSubmit,
  onCancel,
}: {
  player: Player;
  error: string | null;
  onSubmit: (pin: string) => Promise<void>;
  onCancel: () => void;
}) {
  const [pin, setPin] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (pin.length === 4 && !busy) {
      setBusy(true);
      onSubmit(pin).finally(() => {
        setBusy(false);
        setPin("");
      });
    }
  }, [pin, busy, onSubmit]);

  return (
    <div className="flex-1 overflow-y-auto p-6 flex flex-col items-center text-center">
      <PlayerAvatar player={player} size={64} className="rounded-3xl" />
      <div className="mt-3 font-display font-bold text-lg">Hola, {player.name}</div>
      <div className="mt-1 text-xs text-[var(--ink-muted)]">Ingresa tu PIN de 4 dígitos</div>

      <div className="mt-6">
        <PinPad value={pin} onChange={setPin} autoFocus />
      </div>

      <div className="mt-4 h-5 text-xs">
        {busy ? (
          <span className="text-[var(--ink-muted)] inline-flex items-center gap-1"><Loader2 size={12} className="animate-spin" /> Verificando…</span>
        ) : error ? (
          <span className="text-red-600">{error}</span>
        ) : null}
      </div>

      <button
        onClick={onCancel}
        className="mt-auto text-xs text-[var(--ink-muted)] underline-offset-2 hover:underline"
      >
        ¿No eres {player.name}?
      </button>
    </div>
  );
}

function SetupPin({
  player,
  error,
  onSubmit,
}: {
  player: Player;
  error: string | null;
  onSubmit: (defaultPin: string, newPin: string, confirmPin: string) => Promise<void>;
}) {
  const [step, setStep] = useState<"default" | "new" | "confirm">("default");
  const [defaultPin, setDefaultPin] = useState("");
  const [newPin, setNewPin] = useState("");
  const [confirmPin, setConfirmPin] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => { setDefaultPin(""); setNewPin(""); setConfirmPin(""); setStep("default"); }, [player.id]);

  useEffect(() => {
    if (step === "default" && defaultPin.length === 4) setStep("new");
  }, [defaultPin, step]);

  useEffect(() => {
    if (step === "new" && newPin.length === 4) setStep("confirm");
  }, [newPin, step]);

  useEffect(() => {
    if (step === "confirm" && confirmPin.length === 4 && !busy) {
      setBusy(true);
      onSubmit(defaultPin, newPin, confirmPin).finally(() => {
        setBusy(false);
        if (error) { setStep("default"); setDefaultPin(""); setNewPin(""); setConfirmPin(""); }
      });
    }
  }, [confirmPin, step, busy, defaultPin, newPin, onSubmit, error]);

  const headerText =
    step === "default" ? "Ingresa el PIN inicial (te lo dijo Jesús)"
    : step === "new" ? "Crea tu PIN personal de 4 dígitos"
    : "Confirma tu PIN nuevo";

  const value = step === "default" ? defaultPin : step === "new" ? newPin : confirmPin;
  const setter = step === "default" ? setDefaultPin : step === "new" ? setNewPin : setConfirmPin;

  return (
    <div className="flex-1 overflow-y-auto p-6 flex flex-col items-center text-center">
      <div className="flex items-center gap-3">
        <PlayerAvatar player={player} size={48} className="rounded-2xl" />
        <div className="text-left">
          <div className="font-display font-bold text-base">Bienvenido, {player.name}</div>
          <div className="text-[11px] text-[var(--ink-muted)] flex items-center gap-1">
            <KeyRound size={11} /> Primera vez — crea tu PIN
          </div>
        </div>
      </div>

      <div className="mt-5 text-xs text-[var(--ink-soft)] max-w-xs">{headerText}</div>

      <div className="mt-4 flex gap-1.5">
        <Dot active={step === "default"} done={defaultPin.length === 4} />
        <Dot active={step === "new"} done={newPin.length === 4} />
        <Dot active={step === "confirm"} done={confirmPin.length === 4} />
      </div>

      <div className="mt-5">
        <PinPad value={value} onChange={setter} autoFocus />
      </div>

      <div className="mt-4 h-5 text-xs">
        {busy ? (
          <span className="text-[var(--ink-muted)] inline-flex items-center gap-1"><Loader2 size={12} className="animate-spin" /> Guardando…</span>
        ) : error ? (
          <span className="text-red-600">{error}</span>
        ) : null}
      </div>
    </div>
  );
}

function Dot({ active, done }: { active: boolean; done: boolean }) {
  return (
    <div
      className={`h-1.5 rounded-full transition-all ${
        done ? "w-6 bg-[var(--accent-mint)]" : active ? "w-6 bg-[var(--ink)]" : "w-3 bg-[var(--hairline)]"
      }`}
    />
  );
}

function ChatView({
  scrollRef,
  messages,
  visibleCount,
  onScroll,
  onSuggestion,
}: {
  scrollRef: React.RefObject<HTMLDivElement | null>;
  messages: Msg[];
  visibleCount: number;
  onScroll: (e: React.UIEvent<HTMLDivElement>) => void;
  onSuggestion: (s: string) => void;
}) {
  const hiddenCount = Math.max(0, messages.length - visibleCount);
  const visible = hiddenCount > 0 ? messages.slice(-visibleCount) : messages;
  return (
    <div
      ref={scrollRef}
      onScroll={onScroll}
      style={{ overscrollBehavior: "contain", scrollbarGutter: "stable" }}
      className="flex-1 overflow-y-auto p-4 space-y-3"
    >
      {messages.length === 0 && (
        <div className="space-y-4">
          <div className="text-center pt-4">
            <div className="inline-block px-3 py-1 rounded-full bg-[var(--bg-tint)] text-[11px] font-semibold uppercase tracking-wider text-[var(--ink-soft)]">
              Pregúntale lo que sea
            </div>
            <p className="mt-3 text-sm text-[var(--ink-soft)] leading-relaxed">
              Reglas, calendario, fichajes, alineaciones, pronósticos...<br />
              Tu asistente del Mundial 2026.
            </p>
          </div>
          <div className="grid grid-cols-2 gap-2">
            {SUGGESTIONS.map(s => (
              <button
                key={s}
                onClick={() => onSuggestion(s)}
                className="text-left text-xs px-3 py-2.5 rounded-2xl hairline-strong bg-white hover:bg-[var(--bg-tint)] transition-colors"
              >
                {s}
              </button>
            ))}
          </div>
        </div>
      )}

      {hiddenCount > 0 && (
        <div className="flex justify-center pt-1 pb-2">
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-[var(--bg-tint)] text-[var(--ink-muted)] text-[10px] font-semibold uppercase tracking-wider">
            <Loader2 size={10} className="animate-spin" />
            {hiddenCount} mensaje{hiddenCount === 1 ? "" : "s"} más arriba
          </span>
        </div>
      )}

      {visible.map((m, i) => (
        <div key={messages.length - visible.length + i} className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}>
          <div
            className={`px-3.5 py-2.5 rounded-2xl text-sm leading-relaxed break-words min-w-0 ${
              m.role === "user"
                ? "max-w-[85%] whitespace-pre-wrap bg-[var(--ink)] text-white rounded-br-md"
                : "max-w-[92%] bg-[var(--bg-tint)] text-[var(--ink)] rounded-bl-md"
            }`}
          >
            {m.role === "user" ? (
              <>{m.text}</>
            ) : m.streaming && !m.text ? (
              <span className="inline-flex items-center gap-1 h-5">
                <span className="chat-dot" />
                <span className="chat-dot chat-dot--2" />
                <span className="chat-dot chat-dot--3" />
              </span>
            ) : m.streaming && m.text ? (
              <span className="whitespace-pre-wrap">{m.text}<span className="chat-cursor" /></span>
            ) : m.text ? (
              <ChatMarkdown text={m.text} />
            ) : null}
          </div>
        </div>
      ))}
    </div>
  );
}

function ChangePin({ onBack, onLogout }: { onBack: () => void; onLogout: () => void }) {
  const [oldPin, setOldPin] = useState("");
  const [newPin, setNewPin] = useState("");
  const [confirmPin, setConfirmPin] = useState("");
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<string | null>(null);
  const [ok, setOk] = useState(false);

  async function submit() {
    setErr(null);
    if (!/^\d{4}$/.test(oldPin) || !/^\d{4}$/.test(newPin)) { setErr("PIN de 4 dígitos."); return; }
    if (newPin !== confirmPin) { setErr("Los PIN nuevos no coinciden."); return; }
    setBusy(true);
    try {
      const r = await fetch("/api/auth/change", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ oldPin, newPin }),
      });
      const j = await r.json().catch(() => ({}));
      if (j.ok) { setOk(true); setTimeout(onBack, 800); return; }
      const map: Record<string, string> = {
        wrong_old_pin: "PIN actual incorrecto.",
        invalid_new_pin: "El PIN nuevo debe ser de 4 dígitos.",
        not_authed: "Sesión expirada.",
      };
      setErr(map[j.error] || `Error: ${j.error || r.status}`);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="flex-1 overflow-y-auto p-5 space-y-4">
      <div>
        <div className="font-display font-bold text-base flex items-center gap-2"><KeyRound size={16} /> Cambiar PIN</div>
        <div className="text-xs text-[var(--ink-muted)] mt-0.5">Solo tú decides.</div>
      </div>

      <Field label="PIN actual">
        <input
          inputMode="numeric" maxLength={4} value={oldPin}
          onChange={e => setOldPin(e.target.value.replace(/\D/g, "").slice(0, 4))}
          className="w-full px-3 py-2.5 rounded-2xl hairline-strong outline-none font-display tracking-widest text-center text-lg"
          placeholder="••••"
        />
      </Field>

      <Field label="PIN nuevo">
        <input
          inputMode="numeric" maxLength={4} value={newPin}
          onChange={e => setNewPin(e.target.value.replace(/\D/g, "").slice(0, 4))}
          className="w-full px-3 py-2.5 rounded-2xl hairline-strong outline-none font-display tracking-widest text-center text-lg"
          placeholder="••••"
        />
      </Field>

      <Field label="Confirma PIN nuevo">
        <input
          inputMode="numeric" maxLength={4} value={confirmPin}
          onChange={e => setConfirmPin(e.target.value.replace(/\D/g, "").slice(0, 4))}
          className="w-full px-3 py-2.5 rounded-2xl hairline-strong outline-none font-display tracking-widest text-center text-lg"
          placeholder="••••"
        />
      </Field>

      <div className="h-5 text-xs text-center">
        {ok ? <span className="text-green-700">Listo. PIN actualizado.</span>
          : err ? <span className="text-red-600">{err}</span>
          : null}
      </div>

      <div className="flex gap-2">
        <button
          onClick={onBack}
          className="flex-1 px-3 py-2.5 rounded-2xl hairline-strong text-sm font-semibold"
        >
          Cancelar
        </button>
        <button
          onClick={submit}
          disabled={busy || oldPin.length !== 4 || newPin.length !== 4 || confirmPin.length !== 4}
          className="flex-1 px-3 py-2.5 rounded-2xl bg-[var(--ink)] text-white text-sm font-semibold disabled:opacity-40 inline-flex items-center justify-center gap-1.5"
        >
          {busy ? <Loader2 size={14} className="animate-spin" /> : null}
          Guardar
        </button>
      </div>

      <button
        onClick={onLogout}
        className="w-full mt-2 text-xs text-[var(--ink-muted)] hover:text-[var(--ink)] inline-flex items-center justify-center gap-1.5"
      >
        <LogOut size={12} /> Cerrar sesión
      </button>
    </div>
  );
}


function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <label className="block">
      <span className="text-[11px] uppercase tracking-wider text-[var(--ink-muted)] font-semibold">{label}</span>
      <div className="mt-1.5">{children}</div>
    </label>
  );
}
