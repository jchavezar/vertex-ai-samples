// Admin-only CRUD for cromo identity-lock text overrides. The workshop UI
// hits these so the admin can tweak a player's identity prompt live without
// editing src/data/player-identity.ts and redeploying.

import { NextRequest } from "next/server";
import { PLAYERS } from "@/data/players";
import { PLAYER_IDENTITY } from "@/data/player-identity";
import { isAdminRequest } from "@/lib/admin-gate";
import { getIdentityOverride, setIdentityOverride, deleteIdentityOverride } from "@/lib/identity-override";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const MAX_TEXT = 8000;

function getPlayerId(req: NextRequest): string | null {
  const { searchParams } = new URL(req.url);
  const playerId = (searchParams.get("playerId") ?? "").trim();
  if (!playerId) return null;
  if (!PLAYERS.some(p => p.id === playerId)) return null;
  return playerId;
}

export async function GET(req: NextRequest) {
  if (!(await isAdminRequest(req))) return Response.json({ ok: false, error: "forbidden" }, { status: 403 });
  const playerId = getPlayerId(req);
  if (!playerId) return Response.json({ ok: false, error: "bad_playerId" }, { status: 400 });
  const override = await getIdentityOverride(playerId);
  const fileText = PLAYER_IDENTITY[playerId] ?? null;
  return Response.json({
    ok: true,
    playerId,
    override,                // null if no Firestore override
    file: fileText,          // null if no entry in player-identity.ts
    effective: override ?? fileText,
  });
}

export async function PUT(req: NextRequest) {
  if (!(await isAdminRequest(req))) return Response.json({ ok: false, error: "forbidden" }, { status: 403 });
  const playerId = getPlayerId(req);
  if (!playerId) return Response.json({ ok: false, error: "bad_playerId" }, { status: 400 });
  let body: { text?: string } = {};
  try { body = await req.json(); } catch {}
  const text = (body.text ?? "").trim();
  if (!text) return Response.json({ ok: false, error: "text_required" }, { status: 400 });
  if (text.length > MAX_TEXT) return Response.json({ ok: false, error: "text_too_long" }, { status: 400 });
  await setIdentityOverride(playerId, text);
  return Response.json({ ok: true, playerId, text });
}

export async function DELETE(req: NextRequest) {
  if (!(await isAdminRequest(req))) return Response.json({ ok: false, error: "forbidden" }, { status: 403 });
  const playerId = getPlayerId(req);
  if (!playerId) return Response.json({ ok: false, error: "bad_playerId" }, { status: 400 });
  await deleteIdentityOverride(playerId);
  return Response.json({ ok: true, playerId, removed: true });
}
