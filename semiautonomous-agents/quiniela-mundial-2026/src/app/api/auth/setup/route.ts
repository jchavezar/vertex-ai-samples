// First-time PIN setup. Only allowed if the player still has the default PIN.
import { NextRequest } from "next/server";
import { getPin, setPin } from "@/lib/pins";
import { setAuthCookie, DEFAULT_PIN } from "@/lib/auth-server";
import { PLAYERS } from "@/data/players";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function POST(req: NextRequest) {
  let body: { playerId?: string; defaultPin?: string; newPin?: string; confirmPin?: string };
  try {
    body = await req.json();
  } catch {
    return Response.json({ ok: false, error: "invalid_json" }, { status: 400 });
  }

  const playerId = (body.playerId || "").toString().trim();
  const defaultPin = (body.defaultPin || "").toString().trim();
  const newPin = (body.newPin || "").toString().trim();
  const confirmPin = (body.confirmPin || "").toString().trim();

  if (!PLAYERS.find(p => p.id === playerId)) {
    return Response.json({ ok: false, error: "unknown_player" }, { status: 400 });
  }
  if (!/^\d{4}$/.test(newPin)) {
    return Response.json({ ok: false, error: "invalid_new_pin" }, { status: 400 });
  }
  if (newPin !== confirmPin) {
    return Response.json({ ok: false, error: "pins_dont_match" }, { status: 400 });
  }
  if (newPin === DEFAULT_PIN) {
    return Response.json({ ok: false, error: "pin_equals_default" }, { status: 400 });
  }

  try {
    const current = await getPin(playerId);
    if (!current.isDefault) {
      return Response.json({ ok: false, error: "already_setup" }, { status: 409 });
    }
    if (defaultPin !== DEFAULT_PIN) {
      return Response.json({ ok: false, error: "wrong_default_pin" }, { status: 401 });
    }
    await setPin(playerId, newPin);
    await setAuthCookie(playerId);
    return Response.json({ ok: true, playerId });
  } catch (e) {
    return Response.json({ ok: false, error: (e as Error).message }, { status: 500 });
  }
}
