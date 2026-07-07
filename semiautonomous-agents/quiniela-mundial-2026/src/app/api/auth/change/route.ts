import { NextRequest } from "next/server";
import { setPin, verifyPin } from "@/lib/pins";
import { readAuth, setAuthCookie } from "@/lib/auth-server";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function POST(req: NextRequest) {
  let body: { oldPin?: string; newPin?: string };
  try {
    body = await req.json();
  } catch {
    return Response.json({ ok: false, error: "invalid_json" }, { status: 400 });
  }

  const auth = await readAuth();
  if (!auth) return Response.json({ ok: false, error: "not_authed" }, { status: 401 });

  const oldPin = (body.oldPin || "").toString().trim();
  const newPin = (body.newPin || "").toString().trim();
  if (!/^\d{4}$/.test(newPin)) {
    return Response.json({ ok: false, error: "invalid_new_pin" }, { status: 400 });
  }

  try {
    const ok = await verifyPin(auth.playerId, oldPin);
    if (!ok) return Response.json({ ok: false, error: "wrong_old_pin" }, { status: 401 });
    await setPin(auth.playerId, newPin);
    await setAuthCookie(auth.playerId); // refresh
    return Response.json({ ok: true });
  } catch (e) {
    return Response.json({ ok: false, error: (e as Error).message }, { status: 500 });
  }
}
