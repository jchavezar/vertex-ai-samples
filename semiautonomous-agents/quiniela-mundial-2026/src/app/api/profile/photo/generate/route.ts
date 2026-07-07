// Generate a new AI photo for the logged-in player. Saved to history
// (Firestore subcollection + GCS) but NOT activated automatically — the
// user picks "Use this" from the UI to set it as their active profile photo.
//
// Rate limit: 30 generations per day per player.

import { NextRequest } from "next/server";
import { readAuth } from "@/lib/auth-server";
import { db } from "@/lib/firestore-server";
import {
  generateAvatarImage,
  loadActiveBasePhoto,
  uploadToGcs,
} from "@/lib/avatar-image";
import { getPreset } from "@/data/photo-presets";
import { PLAYERS } from "@/data/players";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const COLLECTION = "player_avatars";
const RATE_WINDOW_MS = 24 * 60 * 60 * 1000; // 24 hours
const RATE_MAX = 30;

function knownPlayer(id: string): boolean {
  return PLAYERS.some(p => p.id === id);
}

export async function POST(req: NextRequest) {
  const auth = await readAuth();
  if (!auth) return Response.json({ ok: false, error: "unauthorized" }, { status: 401 });
  if (auth.playerId === "ai") return Response.json({ ok: false, error: "forbidden" }, { status: 403 });
  if (!knownPlayer(auth.playerId)) return Response.json({ ok: false, error: "unknown_player" }, { status: 400 });

  type Body = { presetId?: string; prompt?: string };
  let body: Body = {};
  try { body = (await req.json()) as Body; } catch {}
  const promptText = (body.prompt ?? "").trim();
  const preset = getPreset(body.presetId ?? null);
  if (!preset && !promptText) {
    return Response.json({ ok: false, error: "need_preset_or_prompt" }, { status: 400 });
  }
  if (promptText.length > 500) {
    return Response.json({ ok: false, error: "prompt_too_long" }, { status: 400 });
  }

  const playerRef = db.collection(COLLECTION).doc(auth.playerId);
  const playerSnap = await playerRef.get();
  const playerData = playerSnap.exists ? (playerSnap.data() as { genCount?: number; genResetAt?: number }) : {};
  const now = Date.now();
  let genCount = playerData.genCount ?? 0;
  let genResetAt = playerData.genResetAt ?? 0;
  if (now > genResetAt) {
    genCount = 0;
    genResetAt = now + RATE_WINDOW_MS;
  }
  if (genCount >= RATE_MAX) {
    const retryInMs = Math.max(0, genResetAt - now);
    const hours = Math.ceil(retryInMs / (60 * 60 * 1000));
    return Response.json({
      ok: false, error: "rate_limited",
      retryInSeconds: Math.ceil(retryInMs / 1000),
      message: `Llegaste al límite de ${RATE_MAX} fotos por día. Vuelve en ${hours}h.`,
    }, { status: 429 });
  }

  const basePhoto = await loadActiveBasePhoto(auth.playerId);
  if (!basePhoto) {
    return Response.json({ ok: false, error: "no_base_photo" }, { status: 400 });
  }

  const stylePrompt = preset?.prompt ?? "Polished hero portrait of the person";
  const result = await generateAvatarImage({
    basePhoto,
    stylePrompt,
    extraNote: promptText || undefined,
  });
  if (!result) return Response.json({ ok: false, error: "generation_failed" }, { status: 502 });

  let url: string;
  try {
    const stamp = Date.now();
    url = await uploadToGcs({
      objectName: `profiles/${auth.playerId}/history/${stamp}.png`,
      dataUrl: result.dataUrl,
    });
  } catch (err) {
    console.error("[photo/generate] upload failed", err);
    return Response.json({ ok: false, error: "upload_failed" }, { status: 502 });
  }

  const historyRef = playerRef.collection("photo_history").doc();
  await historyRef.set({
    url,
    source: "generated",
    presetId: preset?.id ?? null,
    prompt: promptText || null,
    createdAt: Date.now(),
  });

  await playerRef.set({ genCount: genCount + 1, genResetAt }, { merge: true });

  return Response.json({
    ok: true,
    url,
    historyId: historyRef.id,
    presetId: preset?.id ?? null,
    remaining: RATE_MAX - (genCount + 1),
  });
}
