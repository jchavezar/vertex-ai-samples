import { NextRequest } from "next/server";
import { getPin, verifyPin } from "@/lib/pins";
import { setAuthCookie } from "@/lib/auth-server";
import { PLAYERS } from "@/data/players";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function POST(req: NextRequest) {
  let body: { playerId?: string; pin?: string };
  try {
    body = await req.json();
  } catch {
    return Response.json({ ok: false, error: "invalid_json" }, { status: 400 });
  }

  const playerId = (body.playerId || "").toString().trim();
  const pin = (body.pin || "").toString().trim();

  if (!PLAYERS.find(p => p.id === playerId)) {
    return Response.json({ ok: false, error: "unknown_player" }, { status: 400 });
  }
  if (!/^\d{4}$/.test(pin)) {
    return Response.json({ ok: false, error: "invalid_pin_format" }, { status: 400 });
  }

  try {
    const rec = await getPin(playerId);
    if (rec.isDefault) {
      return Response.json({ ok: false, error: "must_setup" }, { status: 403 });
    }
    const ok = await verifyPin(playerId, pin);
    if (!ok) return Response.json({ ok: false, error: "wrong_pin" }, { status: 401 });
    await setAuthCookie(playerId);
    return Response.json({ ok: true, playerId });
  } catch (e) {
    return Response.json({ ok: false, error: (e as Error).message }, { status: 500 });
  }
}
