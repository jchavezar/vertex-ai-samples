// Admin-secret-gated endpoint to seed the default Mexico-stadium AI portrait
// for a player who never touched /perfil/foto. Skips anyone who already chose
// something (uploaded, generated, or explicitly went back to original) — so
// it's safe to run on the whole roster.
//
// POST { playerId, dryRun?: boolean }
//   -> action: "regenerated" | "skipped_has_history" | "skipped_has_active"

import { NextRequest } from "next/server";
import { db } from "@/lib/firestore-server";
import { PLAYERS } from "@/data/players";
import { generateAvatarImage, loadBasePhoto, uploadToGcs } from "@/lib/avatar-image";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";
export const maxDuration = 120;

const COLLECTION = "player_avatars";

const MEXICO_STADIUM_PROMPT =
  "Wearing the official Mexico national football team home jersey (verde with subtle aztec sun patterns), dramatic stadium-night background, green-white-red bokeh lights, soft confetti in the air, golden rim light, cinematic studio portrait, head and shoulders, hero pose, crisp magazine-quality finish";

type Body = { playerId?: string; dryRun?: boolean };

export async function POST(req: NextRequest) {
  const expected = process.env.ADMIN_SECRET;
  if (!expected) return Response.json({ ok: false, error: "admin_disabled" }, { status: 503 });
  if (req.headers.get("x-admin-secret") !== expected) {
    return Response.json({ ok: false, error: "forbidden" }, { status: 403 });
  }

  let body: Body = {};
  try { body = (await req.json()) as Body; } catch {}
  const playerId = (body.playerId ?? "").trim();
  const dryRun = body.dryRun === true;
  if (!playerId) return Response.json({ ok: false, error: "playerId_required" }, { status: 400 });
  if (playerId === "ai") return Response.json({ ok: false, error: "ai_not_allowed" }, { status: 400 });
  if (!PLAYERS.some(p => p.id === playerId)) {
    return Response.json({ ok: false, error: "unknown_player" }, { status: 400 });
  }

  const activeRef = db.collection(COLLECTION).doc(playerId);
  const activeSnap = await activeRef.get();
  const active = activeSnap.exists ? (activeSnap.data() as { url?: string | null; source?: string | null }) : null;

  // Already has an active avatar URL → respect it, even if source is "original"
  // (means they explicitly chose to revert and we should not overwrite).
  if (active?.url) {
    return Response.json({
      ok: true,
      action: "skipped_has_active",
      playerId,
      activeUrl: active.url,
    });
  }

  const histSnap = await activeRef.collection("photo_history").limit(1).get();
  if (!histSnap.empty) {
    // They touched /perfil/foto at some point — even if their active is null
    // (back to original), that was a deliberate choice. Don't overwrite.
    const histCount = (await activeRef.collection("photo_history").count().get()).data().count;
    return Response.json({
      ok: true,
      action: "skipped_has_history",
      playerId,
      historyCount: histCount,
    });
  }

  if (dryRun) {
    return Response.json({ ok: true, action: "would_regenerate", playerId });
  }

  const basePhoto = await loadBasePhoto(playerId);
  if (!basePhoto) {
    return Response.json({ ok: false, error: "no_base_photo", playerId }, { status: 400 });
  }

  const result = await generateAvatarImage({
    basePhoto,
    stylePrompt: MEXICO_STADIUM_PROMPT,
  });
  if (!result) {
    return Response.json({ ok: false, error: "generation_failed", playerId }, { status: 502 });
  }

  let publicUrl: string;
  try {
    publicUrl = await uploadToGcs({
      objectName: `profiles/${playerId}-${Date.now()}.png`,
      dataUrl: result.dataUrl,
    });
  } catch (err) {
    console.error("[seed-portrait] upload failed", err);
    return Response.json({ ok: false, error: "upload_failed" }, { status: 502 });
  }

  await activeRef.set({
    playerId,
    style: "mexico-stadium",
    url: publicUrl,
    note: null,
    source: "generated",
    updatedAt: Date.now(),
  }, { merge: true });

  return Response.json({ ok: true, action: "regenerated", playerId, url: publicUrl });
}
