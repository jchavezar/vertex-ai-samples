// Per-player profile read (public) + write (auth required, own only).
import { readAuth } from "@/lib/auth-server";
import { getProfile, upsertProfile, validatePhoto } from "@/lib/profiles-server";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET(req: Request) {
  const url = new URL(req.url);
  const playerId = url.searchParams.get("playerId");
  if (!playerId) return Response.json({ ok: false, error: "playerId required" }, { status: 400 });
  try {
    const profile = await getProfile(playerId);
    return Response.json({ ok: true, profile });
  } catch (e) {
    console.error("[/api/profile GET] error", e);
    return Response.json({ ok: false, error: "internal" }, { status: 500 });
  }
}

export async function PUT(req: Request) {
  const auth = await readAuth();
  if (!auth) return Response.json({ ok: false, error: "unauthorized" }, { status: 401 });
  let body: { name?: string; emoji?: string; photoDataUrl?: string };
  try {
    body = await req.json();
  } catch {
    return Response.json({ ok: false, error: "invalid json" }, { status: 400 });
  }
  // Players can only edit their OWN profile.
  const photoErr = validatePhoto(body.photoDataUrl);
  if (photoErr) return Response.json({ ok: false, error: photoErr }, { status: 400 });
  try {
    const updated = await upsertProfile(auth.playerId, body);
    return Response.json({ ok: true, profile: updated });
  } catch (e) {
    console.error("[/api/profile PUT] error", e);
    return Response.json({ ok: false, error: "internal" }, { status: 500 });
  }
}
