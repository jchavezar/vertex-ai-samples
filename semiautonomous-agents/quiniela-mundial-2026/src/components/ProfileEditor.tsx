"use client";

import { motion, AnimatePresence } from "framer-motion";
import { Camera, Check, RotateCcw, User, X, KeyRound, Loader2, ChevronDown, Sparkles } from "lucide-react";
import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import type { Player } from "@/data/players";
import { clearOverride, setOverride } from "@/lib/profile-overrides";
import { PlayerAvatar } from "@/components/PlayerAvatar";
import { usePlayer } from "@/lib/player-context";

const EMOJI_OPTIONS = ["🦅","⚡","🔥","🐺","🦁","🌊","🐟","👑","🐂","🦊","🐉","🦖","⚽","🥇","🏆","🎯"];

const MAX_PHOTO_BYTES = 200 * 1024;

type Props = {
  player: Player;
  open: boolean;
  onClose: () => void;
};

export function ProfileEditor({ player, open, onClose }: Props) {
  const { currentPlayer } = usePlayer();
  const isMe = currentPlayer?.id === player.id;
  const [name, setName] = useState(player.name);
  const [emoji, setEmoji] = useState<string>(player.emoji);
  const [photo, setPhoto] = useState<string | undefined>(player.photoDataUrl);
  const [error, setError] = useState<string | null>(null);
  const fileRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (!open) return;
    setName(player.name);
    setEmoji(player.emoji);
    setPhoto(player.photoDataUrl);
    setError(null);
  }, [open, player]);

  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    document.addEventListener("keydown", onKey);
    document.body.style.overflow = "hidden";
    return () => {
      document.removeEventListener("keydown", onKey);
      document.body.style.overflow = "";
    };
  }, [open, onClose]);

  async function handleFile(file: File) {
    setError(null);
    if (!file.type.startsWith("image/")) {
      setError("Solo imágenes (JPG, PNG, WebP).");
      return;
    }
    try {
      const dataUrl = await compressImage(file, MAX_PHOTO_BYTES);
      if (dataUrl.length * 0.75 > MAX_PHOTO_BYTES * 1.4) {
        setError("La foto es muy pesada. Intenta una más chica.");
        return;
      }
      setPhoto(dataUrl);
    } catch {
      setError("No se pudo leer la imagen.");
    }
  }

  function handleSave() {
    const trimmedName = name.trim();
    const next: { name?: string; emoji?: string; photoDataUrl?: string } = {};
    if (trimmedName) next.name = trimmedName;
    if (emoji) next.emoji = emoji;
    if (photo) next.photoDataUrl = photo;
    clearOverride(player.id);
    if (Object.keys(next).length > 0) setOverride(player.id, next);
    onClose();
  }

  function handleReset() {
    clearOverride(player.id);
    onClose();
  }

  return (
    <AnimatePresence>
      {open && (
        <>
          <motion.div
            initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            transition={{ duration: 0.18 }}
            className="fixed inset-0 z-[60] bg-black/40 backdrop-blur-sm"
            onClick={onClose}
          />
          <motion.div
            role="dialog"
            aria-modal="true"
            aria-label="Editar perfil"
            initial={{ opacity: 0, y: 40, scale: 0.98 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 30, scale: 0.98 }}
            transition={{ type: "spring", damping: 28, stiffness: 280 }}
            className="fixed z-[61] left-0 right-0 bottom-0 md:left-1/2 md:right-auto md:top-1/2 md:bottom-auto md:-translate-x-1/2 md:-translate-y-1/2 md:w-[440px]"
          >
            <div className="bg-white rounded-t-3xl md:rounded-3xl shadow-2xl max-h-[92vh] overflow-y-auto">
              <div className="sticky top-0 bg-white/95 backdrop-blur px-5 pt-4 pb-3 border-b border-[var(--line)] flex items-center gap-3">
                <div className="w-9 h-9 rounded-full grid place-items-center bg-[var(--bg-tint)]">
                  <User size={16} />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="font-display font-bold leading-none">Editar perfil</div>
                  <div className="text-xs text-[var(--ink-muted)] mt-1">Personaliza tu nombre y avatar</div>
                </div>
                <button onClick={onClose} aria-label="Cerrar" className="w-9 h-9 rounded-full grid place-items-center hover:bg-[var(--bg-tint)]">
                  <X size={16} />
                </button>
              </div>

              <div className="px-5 py-5 space-y-5">
                <div className="flex items-center gap-4">
                  <PlayerAvatar player={{ id: player.id, name, emoji, accent: player.accent, photoDataUrl: photo }} size={72} rounded="rounded-3xl" textClass="text-4xl" />
                  <div className="flex-1 min-w-0">
                    <label className="text-[11px] uppercase tracking-wider text-[var(--ink-muted)] font-semibold">Nombre</label>
                    <input
                      type="text"
                      value={name}
                      onChange={e => setName(e.target.value.slice(0, 24))}
                      placeholder={player.name}
                      className="mt-1 w-full px-3 py-2 rounded-xl border border-[var(--line)] bg-white focus:outline-none focus:ring-2 focus:ring-[var(--ink)] text-base"
                    />
                  </div>
                </div>

                <div>
                  <div className="text-[11px] uppercase tracking-wider text-[var(--ink-muted)] font-semibold mb-2">Elige avatar</div>
                  <div className="grid grid-cols-8 gap-1.5">
                    {EMOJI_OPTIONS.map(e => {
                      const active = emoji === e && !photo;
                      return (
                        <button
                          key={e}
                          type="button"
                          onClick={() => { setEmoji(e); setPhoto(undefined); }}
                          className={`aspect-square rounded-xl grid place-items-center text-xl transition-all ${active ? "ring-2 ring-[var(--ink)] bg-[var(--bg-tint)]" : "hover:bg-[var(--bg-tint)]"}`}
                          style={active ? { background: player.accent + "22" } : undefined}
                          aria-label={`Avatar ${e}`}
                        >
                          {e}
                        </button>
                      );
                    })}
                  </div>
                </div>

                <div>
                  <div className="text-[11px] uppercase tracking-wider text-[var(--ink-muted)] font-semibold mb-2">O sube tu foto</div>
                  <input
                    ref={fileRef}
                    type="file"
                    accept="image/*"
                    className="hidden"
                    onChange={e => {
                      const f = e.target.files?.[0];
                      if (f) handleFile(f);
                      e.target.value = "";
                    }}
                  />
                  <div className="flex items-center gap-2">
                    <button type="button" onClick={() => fileRef.current?.click()} className="btn btn-ghost flex-1 justify-center">
                      <Camera size={14} /> Subir foto
                    </button>
                    {photo && (
                      <button type="button" onClick={() => setPhoto(undefined)} className="btn btn-ghost">
                        <X size={14} /> Quitar
                      </button>
                    )}
                  </div>
                  <p className="mt-1.5 text-[11px] text-[var(--ink-muted)]">Se guarda solo en tu dispositivo. Máx ~200KB.</p>
                  {error && <p className="mt-1.5 text-[11px] text-[var(--accent-coral,#E11D48)]">{error}</p>}
                </div>

                {isMe && (
                  <Link
                    href="/perfil/foto"
                    onClick={onClose}
                    className="block rounded-2xl p-4 text-white font-display font-bold text-sm shadow-lg transition-transform active:scale-[0.98]"
                    style={{
                      background: `linear-gradient(135deg, ${player.accent}, ${player.accent}cc)`,
                      boxShadow: `0 12px 24px -10px ${player.accent}99`,
                    }}
                  >
                    <div className="flex items-center gap-3">
                      <div className="w-9 h-9 rounded-full bg-white/20 grid place-items-center backdrop-blur-sm">
                        <Sparkles size={16} />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="leading-tight">Estudio de foto AI</div>
                        <div className="text-[11px] font-medium opacity-90 mt-0.5">Genera o sube tu propia foto · 10 estilos</div>
                      </div>
                      <span className="text-lg">→</span>
                    </div>
                  </Link>
                )}

                {isMe && <PinChangePanel />}
              </div>

              <div className="sticky bottom-0 bg-white border-t border-[var(--line)] px-5 py-3 flex items-center gap-2">
                <button type="button" onClick={handleReset} className="btn btn-ghost" title="Restablecer">
                  <RotateCcw size={14} /> <span className="hidden sm:inline">Restablecer</span>
                </button>
                <div className="ml-auto flex items-center gap-2">
                  <button type="button" onClick={onClose} className="btn btn-ghost">Cancelar</button>
                  <button type="button" onClick={handleSave} className="btn btn-primary">
                    <Check size={14} /> Guardar
                  </button>
                </div>
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}

function PinChangePanel() {
  const [openPanel, setOpenPanel] = useState(false);
  const [oldPin, setOldPin] = useState("");
  const [newPin, setNewPin] = useState("");
  const [confirmPin, setConfirmPin] = useState("");
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<string | null>(null);
  const [ok, setOk] = useState(false);

  async function submit() {
    setErr(null); setOk(false);
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
      if (j.ok) {
        setOk(true); setOldPin(""); setNewPin(""); setConfirmPin("");
        setTimeout(() => { setOk(false); setOpenPanel(false); }, 1200);
        return;
      }
      const map: Record<string, string> = {
        wrong_old_pin: "PIN actual incorrecto.",
        invalid_new_pin: "El PIN nuevo debe ser de 4 dígitos.",
        not_authed: "Sesión expirada. Vuelve a iniciar sesión.",
      };
      setErr(map[j.error] || `Error: ${j.error || r.status}`);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="rounded-2xl border border-[var(--line)]">
      <button
        type="button"
        onClick={() => setOpenPanel(o => !o)}
        className="w-full flex items-center gap-3 px-4 py-3 text-left"
      >
        <div className="w-8 h-8 rounded-full bg-[var(--bg-tint)] grid place-items-center">
          <KeyRound size={14} />
        </div>
        <div className="flex-1 min-w-0">
          <div className="text-sm font-display font-semibold">Cambiar PIN</div>
          <div className="text-[11px] text-[var(--ink-muted)]">Tu llave para entrar al chat y autoría</div>
        </div>
        <ChevronDown size={16} className={`transition-transform ${openPanel ? "rotate-180" : ""}`} />
      </button>

      <AnimatePresence initial={false}>
        {openPanel && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.18 }}
            className="overflow-hidden"
          >
            <div className="px-4 pb-4 pt-1 space-y-2.5">
              <PinField label="PIN actual" value={oldPin} onChange={setOldPin} />
              <PinField label="PIN nuevo" value={newPin} onChange={setNewPin} />
              <PinField label="Confirma PIN nuevo" value={confirmPin} onChange={setConfirmPin} />

              <div className="h-4 text-[11px]">
                {ok ? <span className="text-green-700">Listo. PIN actualizado.</span>
                  : err ? <span className="text-red-600">{err}</span>
                  : null}
              </div>

              <button
                type="button"
                onClick={submit}
                disabled={busy || oldPin.length !== 4 || newPin.length !== 4 || confirmPin.length !== 4}
                className="w-full px-3 py-2 rounded-xl bg-[var(--ink)] text-white text-sm font-semibold disabled:opacity-40 inline-flex items-center justify-center gap-1.5"
              >
                {busy ? <Loader2 size={14} className="animate-spin" /> : <Check size={14} />} Guardar PIN
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

function PinField({ label, value, onChange }: { label: string; value: string; onChange: (v: string) => void }) {
  return (
    <label className="block">
      <span className="text-[10.5px] uppercase tracking-wider text-[var(--ink-muted)] font-semibold">{label}</span>
      <input
        inputMode="numeric"
        maxLength={4}
        value={value}
        onChange={e => onChange(e.target.value.replace(/\D/g, "").slice(0, 4))}
        className="mt-1 w-full px-3 py-2 rounded-xl border border-[var(--line)] bg-white outline-none font-display tracking-widest text-center text-lg focus:ring-2 focus:ring-[var(--ink)]"
        placeholder="••••"
      />
    </label>
  );
}

async function compressImage(file: File, targetBytes: number): Promise<string> {
  const dataUrl = await readAsDataUrl(file);
  if (dataUrl.length * 0.75 <= targetBytes) return dataUrl;
  const img = await loadImage(dataUrl);
  const maxDim = 384;
  let { width, height } = img;
  if (width > height && width > maxDim) {
    height = Math.round((maxDim / width) * height);
    width = maxDim;
  } else if (height >= width && height > maxDim) {
    width = Math.round((maxDim / height) * width);
    height = maxDim;
  }
  const canvas = document.createElement("canvas");
  canvas.width = width;
  canvas.height = height;
  const ctx = canvas.getContext("2d");
  if (!ctx) return dataUrl;
  ctx.drawImage(img, 0, 0, width, height);
  let quality = 0.85;
  let out = canvas.toDataURL("image/jpeg", quality);
  while (out.length * 0.75 > targetBytes && quality > 0.4) {
    quality -= 0.1;
    out = canvas.toDataURL("image/jpeg", quality);
  }
  return out;
}

function readAsDataUrl(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const r = new FileReader();
    r.onload = () => resolve(String(r.result));
    r.onerror = () => reject(r.error);
    r.readAsDataURL(file);
  });
}

function loadImage(src: string): Promise<HTMLImageElement> {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.onload = () => resolve(img);
    img.onerror = reject;
    img.src = src;
  });
}
