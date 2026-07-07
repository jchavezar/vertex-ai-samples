// Tells the UI whether a player still has the default PIN
// (and therefore needs to set one before logging in).
import { NextRequest } from "next/server";
import { getPin } from "@/lib/pins";
import { PLAYERS } from "@/data/players";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET(req: NextRequest) {
  const playerId = req.nextUrl.searchParams.get("playerId") || "";
  if (!PLAYERS.find(p => p.id === playerId)) {
    return Response.json({ ok: false, error: "unknown_player" }, { status: 400 });
  }
  try {
    const rec = await getPin(playerId);
    return Response.json({ ok: true, hasCustomPin: !rec.isDefault });
  } catch (e) {
    return Response.json({ ok: false, error: (e as Error).message }, { status: 500 });
  }
}
