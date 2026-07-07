// Shared helpers for player avatar generation (Vertex AI image model) + GCS
// upload. Used by `api/avatars/profile` (admin one-shot) and the self-service
// `api/profile/photo/*` endpoints.

import { GoogleGenAI } from "@google/genai";
import { Storage } from "@google-cloud/storage";
import { promises as fs } from "node:fs";
import path from "node:path";
import { db } from "@/lib/firestore-server";
import { listDeletedRefs } from "@/lib/deleted-refs";
import { listActiveGcsRefs } from "@/lib/active-gcs-refs";

export const CROMO_BUCKET = process.env.CROMO_BUCKET || "q26-cromo-portraits";
export const IMAGE_MODEL = process.env.CROMO_IMAGE_MODEL || "gemini-3-pro-image-preview";

let _storage: Storage | null = null;
export function getStorage(): Storage {
  if (!_storage) {
    _storage = new Storage({ projectId: process.env.GOOGLE_CLOUD_PROJECT || "vtxdemos" });
  }
  return _storage;
}

let _ai: GoogleGenAI | null = null;
export function getVertexClient(): GoogleGenAI {
  if (!_ai) {
    _ai = new GoogleGenAI({
      vertexai: true,
      project: process.env.GOOGLE_CLOUD_PROJECT || "vtxdemos",
      location: process.env.VERTEX_LOCATION || "global",
    });
  }
  return _ai;
}

export type BasePhoto = { base64: string; mime: string };

export async function loadBasePhoto(playerId: string): Promise<BasePhoto | null> {
  const file = path.join(process.cwd(), "public", "players", `${playerId}.jpg`);
  try {
    const buf = await fs.readFile(file);
    return { base64: buf.toString("base64"), mime: "image/jpeg" };
  } catch {
    return null;
  }
}

// Returns the player's currently ACTIVE profile photo (the one they chose in
// /perfil/foto) for use as the reference image for studio generations (where
// chaining onto a previously-generated AI photo is the intended behavior).
// Falls back to the static /players/{id}.jpg when no active photo is set, OR
// when the active photo URL is unreachable.
export async function loadActiveBasePhoto(playerId: string): Promise<BasePhoto | null> {
  try {
    const snap = await db.collection("player_avatars").doc(playerId).get();
    const url = snap.exists ? ((snap.data() as { url?: string | null })?.url ?? null) : null;
    if (url && /^https?:\/\//.test(url)) {
      const res = await fetch(url, { cache: "no-store" });
      if (res.ok) {
        const ab = await res.arrayBuffer();
        const mime = res.headers.get("content-type") || "image/jpeg";
        return { base64: Buffer.from(ab).toString("base64"), mime };
      }
    }
  } catch {
    // fall through to static fallback
  }
  return loadBasePhoto(playerId);
}

// Identity reference bank: returns ALL static reference photos for a player.
// Order: base /players/{id}.jpg first, then every file in /players/refs/{id}/.
// Used to feed gemini-3-pro-image-preview multiple inputs of the same person so
// the model preserves face/smile/build across diverse styles. Returns [] if the
// player has neither a base photo nor a refs/ folder.
export async function loadRefPhotos(playerId: string): Promise<BasePhoto[]> {
  const out: BasePhoto[] = [];
  // Soft-deleted refs (admin removed via workshop): skip even though file exists.
  const deleted = await listDeletedRefs(playerId);
  if (!deleted.has(`/players/${playerId}.jpg`)) {
    const base = await loadBasePhoto(playerId);
    if (base) out.push(base);
  }
  const refsDir = path.join(process.cwd(), "public", "players", "refs", playerId);
  try {
    const entries = await fs.readdir(refsDir);
    const allowed = new Set([".jpg", ".jpeg", ".png", ".webp"]);
    for (const name of entries.sort()) {
      const ext = path.extname(name).toLowerCase();
      if (!allowed.has(ext)) continue;
      const url = `/players/refs/${playerId}/${name}`;
      if (deleted.has(url)) continue;
      try {
        const buf = await fs.readFile(path.join(refsDir, name));
        const mime = ext === ".png" ? "image/png"
          : ext === ".webp" ? "image/webp"
          : "image/jpeg";
        out.push({ base64: buf.toString("base64"), mime });
      } catch { /* skip unreadable */ }
    }
  } catch { /* no refs folder is fine */ }
  // GCS-backed refs uploaded via the workshop drop-zone / clipboard paste.
  const gcsRefs = await listActiveGcsRefs(playerId);
  for (const url of gcsRefs) {
    if (deleted.has(url)) continue;
    try {
      const res = await fetch(url, { cache: "no-store" });
      if (!res.ok) continue;
      const ab = await res.arrayBuffer();
      const mime = res.headers.get("content-type") || "image/jpeg";
      out.push({ base64: Buffer.from(ab).toString("base64"), mime });
    } catch { /* skip unreachable */ }
  }
  return out;
}

// Returns the player's MOST RECENT uploaded selfie from photo_history, for use
// as the cromo reference image. We deliberately avoid the "active" photo here
// — if the player activated an AI portrait, restyling that into another AI
// portrait compounds artifacts and drifts the likeness. The cromo's identity
// source must always be a real photo. Falls back to /players/{id}.jpg.
export async function loadLatestUploadedBasePhoto(playerId: string): Promise<{ photo: BasePhoto | null; uploadedAt: number }> {
  try {
    const snap = await db.collection("player_avatars").doc(playerId)
      .collection("photo_history")
      .where("source", "==", "uploaded")
      .orderBy("createdAt", "desc")
      .limit(1)
      .get();
    if (!snap.empty) {
      const doc = snap.docs[0].data() as { url?: string; createdAt?: number };
      if (doc.url && /^https?:\/\//.test(doc.url)) {
        const res = await fetch(doc.url, { cache: "no-store" });
        if (res.ok) {
          const ab = await res.arrayBuffer();
          const mime = res.headers.get("content-type") || "image/jpeg";
          return {
            photo: { base64: Buffer.from(ab).toString("base64"), mime },
            uploadedAt: doc.createdAt ?? 0,
          };
        }
      }
    }
  } catch {
    // fall through to static fallback
  }
  return { photo: await loadBasePhoto(playerId), uploadedAt: 0 };
}

export type UploadOpts = {
  /** GCS object key (relative to bucket root). e.g. "profiles/jesus-1234.png" */
  objectName: string;
  /** Buffer + mime, OR a data URL string. */
  buffer?: Buffer;
  mime?: string;
  dataUrl?: string;
};

export async function uploadToGcs(opts: UploadOpts): Promise<string> {
  let buf: Buffer;
  let mime: string;
  if (opts.dataUrl) {
    const m = /^data:([^;]+);base64,(.+)$/.exec(opts.dataUrl);
    if (!m) throw new Error("invalid_data_url");
    mime = m[1];
    buf = Buffer.from(m[2], "base64");
  } else if (opts.buffer && opts.mime) {
    buf = opts.buffer;
    mime = opts.mime;
  } else {
    throw new Error("upload: need dataUrl OR buffer+mime");
  }
  const file = getStorage().bucket(CROMO_BUCKET).file(opts.objectName);
  await file.save(buf, {
    contentType: mime,
    metadata: { cacheControl: "public, max-age=31536000, immutable" },
  });
  return `https://storage.googleapis.com/${CROMO_BUCKET}/${opts.objectName}`;
}

// Identity-preservation guardrail. Same wording as the original avatar admin
// route — keep ONE source of truth so we don't drift.
export const IDENTITY_GUARDRAIL =
  "CRITICAL: keep the same person clearly recognizable — same face, same hair, same skin tone, same build. Preserve eyeglasses, facial hair, and body shape exactly as in the reference. Complete the face naturally if cropped in the reference. Tight square 1:1 framing — only face, neck, and upper shoulders. NEVER show hands, fingers, arms, or anything below the shoulders. No text, no watermark, no logos other than what the prompt requests.";

export type GenerateOpts = {
  /** If provided, used as reference image input. */
  basePhoto?: BasePhoto;
  /** Style prompt (preset + free-form, already concatenated). */
  stylePrompt: string;
  /** Optional free-form user direction appended after the style prompt. */
  extraNote?: string;
  /** Set true to skip identity guardrail (only for fully-synthetic e.g. AI bot). */
  synthetic?: boolean;
};

export async function generateAvatarImage(opts: GenerateOpts): Promise<{ dataUrl: string } | null> {
  const ai = getVertexClient();
  const extra = opts.extraNote && opts.extraNote.trim().length > 0
    ? ` Additional user direction: ${opts.extraNote.trim()}.`
    : "";
  const parts: Array<{ inlineData?: { mimeType: string; data: string }; text?: string }> = [];
  if (opts.synthetic || !opts.basePhoto) {
    parts.push({ text: `${opts.stylePrompt}${extra}` });
  } else {
    const fullPrompt = `Polished hero profile portrait of the person in the reference photo. ${opts.stylePrompt}.${extra} ${IDENTITY_GUARDRAIL}`;
    parts.push({ inlineData: { mimeType: opts.basePhoto.mime, data: opts.basePhoto.base64 } });
    parts.push({ text: fullPrompt });
  }
  try {
    const resp = await ai.models.generateContent({
      model: IMAGE_MODEL,
      contents: [{ role: "user", parts }],
    });
    const out = resp.candidates?.[0]?.content?.parts ?? [];
    for (const p of out) {
      const inline = (p as { inlineData?: { mimeType?: string; data?: string } }).inlineData;
      if (inline?.data && inline?.mimeType?.startsWith("image/")) {
        return { dataUrl: `data:${inline.mimeType};base64,${inline.data}` };
      }
    }
    return null;
  } catch (err) {
    console.error("[avatar-image] generate failed", err);
    return null;
  }
}
