// Admin one-shot: regenerate any player's active profile photo using all
// reference photos in public/players/refs/{playerId}/* plus a custom prompt
// (e.g. wardrobe / pose tweaks). Writes the result to player_avatars/{id} so
// every client picks it up via the existing avatar pipeline.
//
// Gated to cookie playerId === "jesus" or x-admin-secret header.

import { NextRequest } from "next/server";
import { promises as fs } from "node:fs";
import path from "node:path";
import { readAuth } from "@/lib/auth-server";
import { db } from "@/lib/firestore-server";
import {
  getVertexClient,
  IMAGE_MODEL,
  loadRefPhotos,
  uploadToGcs,
  type BasePhoto,
} from "@/lib/avatar-image";
import { PLAYERS } from "@/data/players";
import { PLAYER_IDENTITY } from "@/data/player-identity";
import { getIdentityOverride } from "@/lib/identity-override";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const COLLECTION = "player_avatars";
const CROMO_COLLECTION = "cromo_portraits";

function todayKey(): string {
  return new Intl.DateTimeFormat("en-CA", {
    timeZone: "America/New_York",
    year: "numeric", month: "2-digit", day: "2-digit",
  }).format(new Date());
}

async function authorize(req: NextRequest): Promise<boolean> {
  const secret = process.env.ADMIN_SECRET;
  if (secret && req.headers.get("x-admin-secret") === secret) return true;
  const auth = await readAuth();
  return auth?.playerId === "jesus";
}

export async function POST(req: NextRequest) {
  if (!(await authorize(req))) {
    return Response.json({ ok: false, error: "forbidden" }, { status: 403 });
  }

  type Body = { playerId?: string; prompt?: string };
  let body: Body = {};
  try { body = (await req.json()) as Body; } catch {}
  const playerId = (body.playerId ?? "").trim();
  if (!playerId || !PLAYERS.some(p => p.id === playerId)) {
    return Response.json({ ok: false, error: "unknown_player" }, { status: 400 });
  }
  if (playerId === "ai") {
    return Response.json({ ok: false, error: "ai_unsupported" }, { status: 400 });
  }
  const prompt = (body.prompt ?? "").trim();
  if (!prompt) {
    return Response.json({ ok: false, error: "prompt_required" }, { status: 400 });
  }

  const refs = await loadRefPhotos(playerId);
  // Also pull the high-res static /players/{id}.jpg if it exists — it's
  // typically the cleanest face shot we have and helps the model anchor on
  // the actual person rather than drifting into a generic look-alike.
  try {
    const mainPath = path.join(process.cwd(), "public", "players", `${playerId}.jpg`);
    const buf = await fs.readFile(mainPath);
    const mainRef: BasePhoto = { mime: "image/jpeg", base64: buf.toString("base64") };
    refs.unshift(mainRef);
  } catch { /* missing static photo — fine */ }
  if (refs.length === 0) {
    return Response.json({ ok: false, error: "no_refs" }, { status: 400 });
  }

  // Identity lock: PLAYER_IDENTITY map (compile-time) + Firestore override
  // (admin can tweak it from the workshop without redeploying). Without this
  // the model frequently drifts into a generic handsome-guy face — we already
  // see this happen for mvictor / jesus / charal in cromo generation.
  const fileIdentity = PLAYER_IDENTITY[playerId] ?? "";
  const dbOverride = await getIdentityOverride(playerId).catch(() => null);
  const identityClause = (dbOverride ?? fileIdentity).trim();

  const ai = getVertexClient();
  const parts: Array<{ inlineData?: { mimeType: string; data: string }; text?: string }> = [];
  parts.push({
    text: `You will receive ${refs.length} reference photo${refs.length > 1 ? "s" : ""} of the SAME real adult man. Study his face carefully — the references are GROUND TRUTH for his identity and override any stereotype, celebrity bias, or genre convention you might otherwise apply. If any photo contains other people, the subject is the central adult male face; ignore anyone else.`,
  });
  for (const r of refs) parts.push({ inlineData: { mimeType: r.mime, data: r.base64 } });
  const finalPrompt = identityClause
    ? `${prompt}\n\n=== IDENTITY LOCK (highest priority — overrides any other instruction) ===\n${identityClause}\nAFTER drafting the image, check: is this the SAME specific man as the reference photos? If you cannot match his nose, eye shape, jawline, and hairline 1:1, REDRAW the face from the references — never default to a generic Mexican leading-man face.`
    : prompt;
  parts.push({ text: finalPrompt });

  let dataUrl: string;
  try {
    const resp = await ai.models.generateContent({
      model: IMAGE_MODEL,
      contents: [{ role: "user", parts }],
    });
    const out = resp.candidates?.[0]?.content?.parts ?? [];
    let found: string | null = null;
    for (const p of out) {
      const inline = (p as { inlineData?: { mimeType?: string; data?: string } }).inlineData;
      if (inline?.data && inline?.mimeType?.startsWith("image/")) {
        found = `data:${inline.mimeType};base64,${inline.data}`;
        break;
      }
    }
    if (!found) {
      return Response.json({ ok: false, error: "no_image_returned" }, { status: 502 });
    }
    dataUrl = found;
  } catch (err) {
    console.error("[maint/regen-profile] generate failed", err);
    return Response.json({ ok: false, error: "generation_failed", detail: String((err as Error)?.message ?? err).slice(0, 300) }, { status: 502 });
  }

  let url: string;
  try {
    const stamp = Date.now();
    url = await uploadToGcs({
      objectName: `profiles/${playerId}/history/${stamp}_maint.png`,
      dataUrl,
    });
  } catch (err) {
    console.error("[maint/regen-profile] upload failed", err);
    return Response.json({ ok: false, error: "upload_failed" }, { status: 502 });
  }

  const playerRef = db.collection(COLLECTION).doc(playerId);
  const historyRef = playerRef.collection("photo_history").doc();
  const now = Date.now();
  await Promise.all([
    historyRef.set({
      url,
      source: "maint",
      presetId: null,
      prompt,
      createdAt: now,
    }),
    playerRef.set({ url, source: "maint", updatedAt: now }, { merge: true }),
    // Active photo changed → today's cromo is stale.
    db.collection(CROMO_COLLECTION).doc(`${playerId}_${todayKey()}`).delete().catch(() => {}),
  ]);

  return Response.json({ ok: true, playerId, url, historyId: historyRef.id });
}
