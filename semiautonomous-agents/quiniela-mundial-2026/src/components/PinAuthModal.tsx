"use client";

import { useEffect, useRef, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { KeyRound, Loader2, X, ChevronLeft } from "lucide-react";
import { PlayerAvatar } from "@/components/PlayerAvatar";
import type { Player } from "@/data/players";

type Screen = "loading" | "enter" | "setup";

export function PinAuthModal({
  player,
  open,
  onClose,
  onAuthed,
}: {
  player: Player | null;
  open: boolean;
  onClose: () => void;
  onAuthed: (p: Player) => void;
}) {
  const [screen, setScreen] = useState<Screen>("loading");
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    if (!open || !player) return;
    setErr(null);
    setScreen("loading");
    let cancelled = false;
    (async () => {
      try {
        const r = await fetch(`/api/auth/status?playerId=${encodeURIComponent(player.id)}`, { cache: "no-store" });
        const j = await r.json();
        if (cancelled) return;
        if (j.ok && j.hasCustomPin) setScreen("enter");
        else setScreen("setup");
      } catch {
        if (!cancelled) setScreen("enter");
      }
    })();
    return () => { cancelled = true; };
  }, [open, player]);

  return (
    <AnimatePresence>
      {open && player && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm"
          />
          <motion.div
            initial={{ y: 24, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            exit={{ y: 24, opacity: 0 }}
            transition={{ type: "spring", damping: 28, stiffness: 280 }}
            className="fixed z-50 bg-white shadow-2xl rounded-3xl overflow-hidden ring-1 ring-black/5
                       left-3 right-3 bottom-3 top-auto max-h-[92vh]
                       md:left-1/2 md:right-auto md:-translate-x-1/2 md:bottom-auto md:top-1/2 md:-translate-y-1/2 md:w-[400px]"
          >
            <div className="flex items-center gap-3 px-4 py-3 border-b border-[var(--hairline)] bg-white">
              <div className="w-10 h-10 rounded-full bg-[var(--ink)] grid place-items-center text-white shrink-0">
                <KeyRound size={18} />
              </div>
              <div className="flex-1 min-w-0">
                <div className="font-display font-bold text-sm">Cambiar de jugador</div>
                <div className="text-[11px] text-[var(--ink-muted)] truncate">
                  {screen === "setup" ? "Primera vez · crea tu PIN" : "Ingresa tu PIN"}
                </div>
              </div>
              <button
                onClick={onClose}
                aria-label="Cerrar"
                className="w-9 h-9 rounded-full grid place-items-center hover:bg-[var(--bg-tint)] shrink-0"
              >
                <X size={18} />
              </button>
            </div>

            <div className="min-h-[300px] flex flex-col">
              {screen === "loading" && (
                <div className="flex-1 grid place-items-center p-8 text-[var(--ink-muted)]">
                  <Loader2 size={20} className="animate-spin" />
                </div>
              )}

              {screen === "enter" && (
                <EnterPin
                  player={player}
                  error={err}
                  onCancel={onClose}
                  onSubmit={async pin => {
                    setErr(null);
                    const r = await fetch("/api/auth/verify", {
                      method: "POST",
                      headers: { "Content-Type": "application/json" },
                      body: JSON.stringify({ playerId: player.id, pin }),
                    });
                    const j = await r.json().catch(() => ({}));
                    if (j.ok) { onAuthed(player); return; }
                    if (j.error === "must_setup") { setScreen("setup"); return; }
                    setErr(j.error === "wrong_pin" ? "PIN incorrecto." : `Error: ${j.error || r.status}`);
                  }}
                />
              )}

              {screen === "setup" && (
                <SetupPin
                  player={player}
                  error={err}
                  onBack={() => setScreen("enter")}
                  onSubmit={async (defaultPin, newPin, confirmPin) => {
                    setErr(null);
                    const r = await fetch("/api/auth/setup", {
                      method: "POST",
                      headers: { "Content-Type": "application/json" },
                      body: JSON.stringify({ playerId: player.id, defaultPin, newPin, confirmPin }),
                    });
                    const j = await r.json().catch(() => ({}));
                    if (j.ok) { onAuthed(player); return; }
                    const map: Record<string, string> = {
                      wrong_default_pin: "PIN inicial incorrecto.",
                      pins_dont_match: "Los PINs no coinciden.",
                      pin_equals_default: "Elige un PIN distinto al inicial.",
                      invalid_new_pin: "El PIN nuevo debe ser de 4 dígitos.",
                      already_setup: "Este jugador ya tiene un PIN. Inicia sesión.",
                    };
                    setErr(map[j.error] || `Error: ${j.error || r.status}`);
                    if (j.error === "already_setup") setTimeout(() => setScreen("enter"), 1200);
                  }}
                />
              )}
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
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

  useEffect(() => { setPin(""); }, [player.id]);

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
      <PlayerAvatar player={player} size={64} rounded="rounded-3xl" />
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
        className="mt-6 text-xs text-[var(--ink-muted)] underline-offset-2 hover:underline"
      >
        Cancelar
      </button>
    </div>
  );
}

function SetupPin({
  player,
  error,
  onBack,
  onSubmit,
}: {
  player: Player;
  error: string | null;
  onBack: () => void;
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
        <PlayerAvatar player={player} size={48} rounded="rounded-2xl" />
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

      <button
        onClick={onBack}
        className="mt-6 text-xs text-[var(--ink-muted)] inline-flex items-center gap-1 underline-offset-2 hover:underline"
      >
        <ChevronLeft size={12} /> Ya tengo PIN
      </button>
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
