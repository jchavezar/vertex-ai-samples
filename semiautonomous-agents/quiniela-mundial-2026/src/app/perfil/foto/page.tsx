"use client";

// Self-service photo studio. Each logged-in player can:
//   1. Generate AI portraits (10 presets + free-form natural language prompt)
//   2. Upload their own photo
//   3. Browse + reactivate / delete past entries from history
//   4. Restore the original baseline photo (public/players/{id}.jpg)
//
// Rate-limited to 5 generations per hour per player (server-enforced).
// Active photo persists across sessions in Firestore player_avatars/{id}.
// Daily cromo portraits are independent and unaffected.

import { useEffect, useMemo, useRef, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  ArrowLeft, Sparkles, Upload, Image as ImageIcon, Wand2, Loader2,
  RotateCcw, Trash2, Check, AlertCircle, X,
} from "lucide-react";
import { usePlayer } from "@/lib/player-context";
import { useProfileAvatar, notifyProfileAvatarUpdated } from "@/lib/profile-avatar";
import { PHOTO_PRESETS, getPreset } from "@/data/photo-presets";
import { track } from "@/lib/track";

type Tab = "ai" | "upload" | "history";
type HistoryItem = {
  id: string;
  url: string;
  source: "generated" | "uploaded";
  presetId: string | null;
  prompt: string | null;
  createdAt: number;
};

export default function PerfilFotoPage() {
  const router = useRouter();
  const { currentPlayer, ready } = usePlayer();
  const activeUrl = useProfileAvatar(currentPlayer?.id);

  useEffect(() => {
    if (ready && !currentPlayer) router.replace("/jugadores");
  }, [ready, currentPlayer, router]);

  if (!ready) return <div className="min-h-screen grid place-items-center text-[var(--ink-muted)]">…</div>;
  if (!currentPlayer) return null;

  return <Studio playerId={currentPlayer.id} playerName={currentPlayer.name} accent={currentPlayer.accent ?? "#7C3AED"} activeUrl={activeUrl} defaultPhoto={currentPlayer.defaultPhoto ?? `/players/${currentPlayer.id}.jpg`} />;
}

function Studio({
  playerId, playerName, accent, activeUrl, defaultPhoto,
}: {
  playerId: string;
  playerName: string;
  accent: string;
  activeUrl: string | null;
  defaultPhoto: string;
}) {
  const [tab, setTab] = useState<Tab>("ai");
  const [presetId, setPresetId] = useState<string>("mexico-stadium");
  const [prompt, setPrompt] = useState<string>("");
  const [generating, setGenerating] = useState(false);
  const [lastGenerated, setLastGenerated] = useState<{ url: string; historyId: string; presetId: string | null; prompt: string | null } | null>(null);
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [info, setInfo] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const [activating, setActivating] = useState<string | null>(null);
  const [confirmDelete, setConfirmDelete] = useState<HistoryItem | null>(null);
  const [recovering, setRecovering] = useState(false);
  const fileRef = useRef<HTMLInputElement>(null);

  const display = activeUrl || defaultPhoto;
  const isOriginalActive = !activeUrl;
  const activePreset = useMemo(() => getPreset(history.find(h => h.url === activeUrl)?.presetId ?? null), [history, activeUrl]);

  // Auto-clear info after 3s.
  useEffect(() => {
    if (!info) return;
    const t = setTimeout(() => setInfo(null), 3000);
    return () => clearTimeout(t);
  }, [info]);

  useEffect(() => {
    track("photo_studio_open");
  }, []);

  const loadHistory = async () => {
    setHistoryLoading(true);
    try {
      const r = await fetch("/api/profile/photo/history", { cache: "no-store" });
      const j = await r.json();
      if (j?.ok) setHistory(j.items ?? []);
    } catch {} finally {
      setHistoryLoading(false);
    }
  };
  useEffect(() => { void loadHistory(); }, [playerId]);

  const generate = async () => {
    setError(null);
    setGenerating(true);
    try {
      const r = await fetch("/api/profile/photo/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ presetId, prompt: prompt.trim() }),
      });
      const j = await r.json();
      if (!r.ok || !j?.ok) {
        setError(j?.message ?? j?.error ?? "No se pudo generar la foto.");
        return;
      }
      setLastGenerated({ url: j.url, historyId: j.historyId, presetId: j.presetId ?? presetId, prompt: prompt.trim() || null });
      track("photo_generated", { preset: j.presetId ?? presetId });
      await loadHistory();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Error de red");
    } finally {
      setGenerating(false);
    }
  };

  const upload = async (file: File) => {
    setError(null);
    setUploading(true);
    try {
      // iPhone/Android camera shots are routinely 5-10MB which used to
      // blow past our old 4MB server limit and "fail silently". Resize
      // client-side to longest-edge 2048px JPEG q=0.9 — this keeps faces
      // sharp for avatars and brings payloads to ~300-800kB.
      let toSend: Blob = file;
      let sendName = file.name || "photo.jpg";
      try {
        const resized = await resizeImage(file, 2048, 0.9);
        if (resized) {
          toSend = resized;
          sendName = (file.name || "photo").replace(/\.[^.]+$/, "") + ".jpg";
        }
      } catch (resizeErr) {
        console.warn("[photo/upload] resize failed, sending original", resizeErr);
      }
      const fd = new FormData();
      fd.append("file", toSend, sendName);
      const r = await fetch("/api/profile/photo/upload", { method: "POST", body: fd, credentials: "same-origin" });
      let j: { ok?: boolean; error?: string; url?: string; historyId?: string; maxMB?: number; activated?: boolean } = {};
      try { j = await r.json(); } catch {}
      if (!r.ok || !j?.ok) {
        const msg =
          j?.error === "too_large" ? `El archivo pesa más de ${j.maxMB ?? 12}MB. Intenta con una foto más chica.` :
          j?.error === "bad_mime" ? "Formato no soportado. Usa JPG, PNG o WEBP." :
          j?.error === "file_missing" ? "No se detectó el archivo. Vuelve a elegirlo." :
          j?.error === "invalid_multipart" ? "La foto no llegó completa. Revisa tu conexión y reintenta." :
          j?.error === "unauthorized" ? "Tu sesión caducó. Vuelve a iniciar sesión." :
          j?.error === "upload_failed" ? "El servidor no pudo guardar la foto. Intenta otra vez." :
          (j?.error ? `Error: ${j.error}` : `No se pudo subir (HTTP ${r.status}).`);
        setError(msg);
        return;
      }
      setLastGenerated({ url: j.url!, historyId: j.historyId!, presetId: null, prompt: null });
      track("photo_uploaded");
      await loadHistory();
      // Server auto-activates uploaded photos; refresh the top preview so
      // the user sees their new selfie immediately instead of the previous one.
      if (j.activated) {
        notifyProfileAvatarUpdated(playerId);
        setInfo("¡Foto subida y activada!");
      } else {
        setInfo("Foto subida. Toca «Usar esta» para activarla.");
      }
    } catch (e) {
      setError(e instanceof Error ? `Error de red: ${e.message}` : "Error de red");
    } finally {
      setUploading(false);
    }
  };

  const activate = async (url: string, source: "generated" | "uploaded" | "original") => {
    setActivating(url);
    setError(null);
    try {
      const r = await fetch("/api/profile/photo/set-active", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url, source }),
      });
      const j = await r.json();
      if (!r.ok || !j?.ok) {
        setError(j?.error ?? "No se pudo activar.");
        return;
      }
      notifyProfileAvatarUpdated(playerId);
      track("photo_activated", { source });
      setInfo(source === "original" ? "Foto original activada." : "¡Foto activada!");
      if (source === "original") setLastGenerated(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Error de red");
    } finally {
      setActivating(null);
    }
  };

  const deleteHistory = async (id: string) => {
    setError(null);
    try {
      const r = await fetch(`/api/profile/photo/history/${id}`, { method: "DELETE" });
      const j = await r.json();
      if (!r.ok || !j?.ok) {
        setError(j?.error ?? "No se pudo borrar.");
        return;
      }
      setHistory(h => h.filter(x => x.id !== id));
    } catch (e) {
      setError(e instanceof Error ? e.message : "Error de red");
    }
  };

  const recoverHistory = async () => {
    setError(null);
    setRecovering(true);
    try {
      const r = await fetch("/api/profile/photo/recover", { method: "POST" });
      const j = await r.json();
      if (!r.ok || !j?.ok) {
        setError(j?.error ?? "No se pudo recuperar.");
        return;
      }
      await loadHistory();
      setInfo(j.recovered > 0 ? `Recuperadas ${j.recovered} fotos.` : "Tu historial ya está completo.");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Error de red");
    } finally {
      setRecovering(false);
    }
  };

  return (
    <main className="min-h-screen bg-[var(--bg)] pb-24">
      {/* Header — non-sticky to avoid overlap with global Nav */}
      <div className="bg-white/80 backdrop-blur-md border-b border-[var(--line)]">
        <div className="max-w-3xl mx-auto px-4 py-3 flex items-center gap-3">
          <Link href="/jugadores" className="w-9 h-9 rounded-full grid place-items-center hover:bg-[var(--bg-tint)] transition-colors" aria-label="Volver">
            <ArrowLeft size={18} />
          </Link>
          <div className="flex-1 min-w-0">
            <div className="text-[10px] uppercase tracking-[0.15em] text-[var(--ink-muted)]">{playerName}</div>
            <div className="font-display text-lg font-bold text-[var(--ink)] truncate">Estudio de foto</div>
          </div>
          <Sparkles size={18} style={{ color: accent }} />
        </div>
      </div>

      <div className="max-w-3xl mx-auto px-4 pt-6 space-y-6">
        {/* Active preview */}
        <section
          className="rounded-3xl p-6 relative overflow-hidden"
          style={{ background: `linear-gradient(160deg, ${accent}16, ${accent}05 60%, transparent)` }}
        >
          <div className="flex flex-col sm:flex-row items-center gap-5">
            <div className="relative shrink-0">
              <div
                className="w-40 h-40 sm:w-48 sm:h-48 rounded-2xl overflow-hidden ring-4 ring-white shadow-xl"
                style={{ boxShadow: `0 16px 36px -12px ${accent}66` }}
              >
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img src={display} alt={playerName} className="w-full h-full object-cover" />
              </div>
              {isOriginalActive && (
                <span className="absolute -top-2 -right-2 text-[10px] font-bold uppercase tracking-wider bg-[var(--ink)] text-white px-2 py-1 rounded-full">
                  Original
                </span>
              )}
            </div>
            <div className="flex-1 min-w-0 text-center sm:text-left">
              <div className="text-[10px] uppercase tracking-[0.18em] text-[var(--ink-muted)]">Foto activa</div>
              <div className="font-display text-xl font-bold text-[var(--ink)] mt-1">
                {isOriginalActive ? "Foto original" : activePreset?.label ?? "Personalizada"}
              </div>
              <div className="text-xs text-[var(--ink-muted)] mt-1">
                {isOriginalActive ? "La que subimos al inicio del torneo." : "Aparece en el chatbot, leaderboard y avatares."}
              </div>
              {!isOriginalActive && (
                <button
                  type="button"
                  onClick={() => activate(`/players/${playerId}.jpg`, "original")}
                  disabled={activating !== null}
                  className="mt-3 inline-flex items-center gap-1.5 text-xs font-semibold text-[var(--ink-soft)] hover:text-[var(--ink)] underline underline-offset-2"
                >
                  <RotateCcw size={12} /> Restaurar original
                </button>
              )}
            </div>
          </div>
        </section>

        {/* Toasts */}
        {error && (
          <div className="rounded-2xl bg-red-50 border border-red-200 px-4 py-3 text-sm text-red-800 flex items-start gap-2">
            <AlertCircle size={16} className="mt-0.5 shrink-0" />
            <div className="flex-1">{error}</div>
            <button type="button" onClick={() => setError(null)} className="text-red-600 hover:text-red-900" aria-label="Cerrar"><X size={14} /></button>
          </div>
        )}
        {info && (
          <div className="rounded-2xl bg-emerald-50 border border-emerald-200 px-4 py-3 text-sm text-emerald-800 flex items-center gap-2">
            <Check size={16} /> {info}
          </div>
        )}

        {/* Tabs */}
        <div className="bg-white rounded-2xl border border-[var(--line)] overflow-hidden">
          <div role="tablist" className="grid grid-cols-3 border-b border-[var(--line)]">
            <TabButton active={tab === "ai"} onClick={() => setTab("ai")} icon={<Wand2 size={14} />} label="AI" />
            <TabButton active={tab === "upload"} onClick={() => setTab("upload")} icon={<Upload size={14} />} label="Subir" />
            <TabButton active={tab === "history"} onClick={() => setTab("history")} icon={<ImageIcon size={14} />} label={`Historial${history.length ? ` · ${history.length}` : ""}`} />
          </div>

          {/* AI tab */}
          {tab === "ai" && (
            <div className="p-5 space-y-5">
              <div>
                <label className="text-[10px] uppercase tracking-[0.15em] text-[var(--ink-muted)] font-semibold">Estilo</label>
                <select
                  value={presetId}
                  onChange={e => setPresetId(e.target.value)}
                  className="mt-1.5 w-full rounded-xl border border-[var(--line)] bg-white px-3 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-[var(--accent-violet)]"
                >
                  {PHOTO_PRESETS.map(p => (
                    <option key={p.id} value={p.id}>{p.icon} {p.label} — {p.blurb}</option>
                  ))}
                </select>
              </div>

              {/* Quick chips */}
              <div className="flex flex-wrap gap-1.5">
                {PHOTO_PRESETS.map(p => (
                  <button
                    key={p.id}
                    type="button"
                    onClick={() => setPresetId(p.id)}
                    className={`text-xs px-2.5 py-1.5 rounded-full border transition-all ${
                      presetId === p.id
                        ? "border-transparent text-white shadow-md"
                        : "border-[var(--line)] bg-white text-[var(--ink-soft)] hover:border-[var(--ink)]"
                    }`}
                    style={presetId === p.id ? { background: accent } : undefined}
                  >
                    {p.icon} {p.label}
                  </button>
                ))}
              </div>

              <div>
                <label className="text-[10px] uppercase tracking-[0.15em] text-[var(--ink-muted)] font-semibold">
                  Tu idea (opcional)
                </label>
                <textarea
                  value={prompt}
                  onChange={e => setPrompt(e.target.value)}
                  placeholder='Ej: "con peluca de Cristiano, sonriendo, en el Azteca"'
                  rows={3}
                  maxLength={500}
                  className="mt-1.5 w-full rounded-xl border border-[var(--line)] bg-white px-3 py-3 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-[var(--accent-violet)]"
                />
                <div className="text-[10px] text-[var(--ink-muted)] mt-1 text-right tabular-nums">{prompt.length}/500</div>
              </div>

              <button
                type="button"
                onClick={generate}
                disabled={generating}
                className="w-full rounded-2xl text-white font-display font-bold py-3.5 text-sm flex items-center justify-center gap-2 transition-all disabled:opacity-60 disabled:cursor-not-allowed shadow-lg"
                style={{ background: `linear-gradient(135deg, ${accent}, ${accent}dd)`, boxShadow: `0 10px 22px -8px ${accent}88` }}
              >
                {generating ? <><Loader2 size={16} className="animate-spin" /> Generando…</> : <><Sparkles size={14} /> Generar foto</>}
              </button>
              <div className="text-[10px] text-[var(--ink-muted)] text-center">
                Hasta 30 fotos por día · No se activa hasta que la elijas
              </div>

              {lastGenerated && (
                <div className="rounded-2xl border border-[var(--line)] p-3 flex items-center gap-3">
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img src={lastGenerated.url} alt="Última generada" className="w-20 h-20 rounded-xl object-cover ring-2 ring-white shadow-md" />
                  <div className="flex-1 min-w-0">
                    <div className="font-display font-bold text-sm text-[var(--ink)] truncate">
                      {lastGenerated.presetId ? getPreset(lastGenerated.presetId)?.label : "Subida"}
                    </div>
                    {lastGenerated.prompt && (
                      <div className="text-xs text-[var(--ink-muted)] truncate italic">«{lastGenerated.prompt}»</div>
                    )}
                  </div>
                  <button
                    type="button"
                    onClick={() => activate(lastGenerated.url, lastGenerated.presetId === null && !lastGenerated.prompt ? "uploaded" : "generated")}
                    disabled={activating === lastGenerated.url}
                    className="shrink-0 rounded-full px-3 py-2 text-xs font-bold text-white"
                    style={{ background: accent }}
                  >
                    {activating === lastGenerated.url ? "…" : "Usar esta"}
                  </button>
                </div>
              )}
            </div>
          )}

          {/* Upload tab */}
          {tab === "upload" && (
            <div className="p-5 space-y-4">
              <button
                type="button"
                onClick={() => fileRef.current?.click()}
                disabled={uploading}
                className="w-full rounded-2xl border-2 border-dashed border-[var(--line-strong)] bg-[var(--bg-tint)] py-10 px-5 flex flex-col items-center gap-2 hover:border-[var(--ink-soft)] transition-colors disabled:opacity-60"
              >
                {uploading ? <Loader2 size={28} className="animate-spin text-[var(--ink-soft)]" /> : <Upload size={28} className="text-[var(--ink-soft)]" />}
                <div className="font-display font-bold text-sm text-[var(--ink)]">
                  {uploading ? "Subiendo…" : "Toca para elegir una foto"}
                </div>
                <div className="text-xs text-[var(--ink-muted)]">JPG, PNG o WEBP · se redimensiona en tu teléfono</div>
              </button>
              <input
                ref={fileRef}
                type="file"
                accept="image/jpeg,image/png,image/webp"
                onChange={e => {
                  const f = e.target.files?.[0];
                  if (f) void upload(f);
                  e.target.value = "";
                }}
                className="hidden"
              />
              <div className="text-xs text-[var(--ink-muted)] leading-relaxed">
                La foto se guarda en tu historial. Después tócala para activarla y reemplazar tu avatar.
              </div>
            </div>
          )}

          {/* History tab */}
          {tab === "history" && (
            <div className="p-5 space-y-3">
              <div className="flex items-center justify-between gap-3 text-xs text-[var(--ink-muted)]">
                <div>Tócala para activar · Toca 🗑 para borrar (te pide confirmar).</div>
                <button
                  type="button"
                  onClick={recoverHistory}
                  disabled={recovering}
                  className="shrink-0 inline-flex items-center gap-1.5 text-[10px] font-bold uppercase tracking-wider text-[var(--ink-soft)] hover:text-[var(--ink)] border border-[var(--line)] rounded-full px-2.5 py-1 disabled:opacity-50"
                  title="Vuelve a leer tu carpeta en la nube y recupera fotos borradas por error"
                >
                  {recovering ? <Loader2 size={10} className="animate-spin" /> : <RotateCcw size={10} />}
                  Recuperar
                </button>
              </div>
              {historyLoading ? (
                <div className="py-12 text-center text-sm text-[var(--ink-muted)]">Cargando…</div>
              ) : history.length === 0 ? (
                <div className="py-12 text-center text-sm text-[var(--ink-muted)]">
                  Aún no has generado ni subido fotos. Empieza en el tab «AI».
                </div>
              ) : (
                <div className="grid grid-cols-3 sm:grid-cols-4 gap-2">
                  {history.map(item => {
                    const isActive = item.url === activeUrl;
                    const preset = getPreset(item.presetId);
                    const isActivating = activating === item.url;
                    return (
                      <div key={item.id} className="relative">
                        <button
                          type="button"
                          onClick={() => { if (!isActive && !isActivating) void activate(item.url, item.source); }}
                          disabled={isActive || isActivating}
                          aria-label={isActive ? "Foto activa" : "Activar esta foto"}
                          className={`block w-full aspect-square rounded-xl overflow-hidden ring-2 shadow-md transition-all ${
                            isActive
                              ? "ring-[var(--accent-violet)]"
                              : "ring-white active:scale-95 active:ring-[var(--accent-violet)]/60 hover:ring-[var(--ink-soft)]"
                          }`}
                        >
                          {/* eslint-disable-next-line @next/next/no-img-element */}
                          <img src={item.url} alt={preset?.label ?? item.source} className="w-full h-full object-cover pointer-events-none" />
                        </button>
                        {isActive && (
                          <span className="absolute top-1.5 left-1.5 text-[9px] font-bold uppercase tracking-wider bg-[var(--accent-violet)] text-white px-1.5 py-0.5 rounded pointer-events-none">
                            Activa
                          </span>
                        )}
                        {isActivating && (
                          <div className="absolute inset-0 rounded-xl bg-black/40 grid place-items-center pointer-events-none">
                            <Loader2 size={20} className="animate-spin text-white" />
                          </div>
                        )}
                        <button
                          type="button"
                          onClick={(e) => { e.stopPropagation(); setConfirmDelete(item); }}
                          aria-label="Borrar foto"
                          className="absolute top-1.5 right-1.5 w-7 h-7 grid place-items-center rounded-full bg-black/60 text-white hover:bg-red-600 transition-colors backdrop-blur-sm"
                        >
                          <Trash2 size={12} />
                        </button>
                        <div className="mt-1 text-[10px] text-[var(--ink-muted)] truncate text-center">
                          {preset?.label ?? (item.source === "uploaded" ? "Subida" : "Personalizada")}
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          )}
        </div>

        <div className="text-[10px] text-[var(--ink-muted)] text-center pt-2 leading-relaxed">
          Tus cromos diarios siguen rotando independientes. Esta foto sólo cambia el avatar.
        </div>
      </div>

      {confirmDelete && (
        <div
          className="fixed inset-0 z-50 grid place-items-center bg-black/60 backdrop-blur-sm p-4"
          onClick={() => setConfirmDelete(null)}
          role="dialog"
          aria-modal="true"
        >
          <div
            className="bg-white rounded-3xl max-w-sm w-full p-5 shadow-2xl"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-start gap-3">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img src={confirmDelete.url} alt="" className="w-20 h-20 rounded-xl object-cover ring-2 ring-[var(--line)] shrink-0" />
              <div className="flex-1 min-w-0">
                <div className="font-display font-bold text-base text-[var(--ink)]">¿Borrar esta foto?</div>
                <div className="text-xs text-[var(--ink-muted)] mt-1 leading-relaxed">
                  Se quita de tu historial. Si la borras por error, toca «Recuperar» arriba.
                </div>
              </div>
            </div>
            <div className="mt-4 grid grid-cols-2 gap-2">
              <button
                type="button"
                onClick={() => setConfirmDelete(null)}
                className="rounded-xl border border-[var(--line)] px-3 py-3 text-sm font-bold text-[var(--ink)] hover:bg-[var(--bg-tint)] transition-colors"
              >
                Cancelar
              </button>
              <button
                type="button"
                onClick={() => { const id = confirmDelete.id; setConfirmDelete(null); void deleteHistory(id); }}
                className="rounded-xl bg-red-600 text-white px-3 py-3 text-sm font-bold hover:bg-red-700 transition-colors inline-flex items-center justify-center gap-1.5"
              >
                <Trash2 size={14} /> Borrar
              </button>
            </div>
          </div>
        </div>
      )}
    </main>
  );
}

// Downscale an image File to longest-edge `maxEdge`px and re-encode as
// JPEG with the given quality. Returns null if the browser can't decode
// the file (e.g. HEIC on some platforms) — caller will fall back to the
// original. Pure vanilla canvas, no dependencies.
async function resizeImage(file: File, maxEdge: number, quality: number): Promise<Blob | null> {
  if (typeof window === "undefined") return null;
  if (!file.type.startsWith("image/")) return null;
  const url = URL.createObjectURL(file);
  try {
    const img = await new Promise<HTMLImageElement>((resolve, reject) => {
      const i = new Image();
      i.onload = () => resolve(i);
      i.onerror = () => reject(new Error("decode_failed"));
      i.src = url;
    });
    const longest = Math.max(img.naturalWidth, img.naturalHeight);
    const scale = longest > maxEdge ? maxEdge / longest : 1;
    const w = Math.round(img.naturalWidth * scale);
    const h = Math.round(img.naturalHeight * scale);
    const canvas = document.createElement("canvas");
    canvas.width = w;
    canvas.height = h;
    const ctx = canvas.getContext("2d");
    if (!ctx) return null;
    ctx.drawImage(img, 0, 0, w, h);
    const blob: Blob | null = await new Promise(res => canvas.toBlob(b => res(b), "image/jpeg", quality));
    return blob;
  } finally {
    URL.revokeObjectURL(url);
  }
}

function TabButton({ active, onClick, icon, label }: { active: boolean; onClick: () => void; icon: React.ReactNode; label: string }) {
  return (
    <button
      type="button"
      role="tab"
      aria-selected={active}
      onClick={onClick}
      className={`flex items-center justify-center gap-1.5 py-3 text-xs font-display font-bold transition-colors ${
        active ? "text-[var(--ink)] border-b-2 border-[var(--ink)]" : "text-[var(--ink-muted)] hover:text-[var(--ink-soft)]"
      }`}
    >
      {icon} {label}
    </button>
  );
}
