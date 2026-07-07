// Sprint-1 stub. Sprint 2 swaps the body for gemini-3-flash-image / Nano
// Banana Pro generation and caches the result in GCS + Firestore.
// For now: returns ok=false so the client falls back to PlayerAvatar.

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function POST(req: Request) {
  let body: { playerId?: string; tier?: string } = {};
  try { body = await req.json(); } catch {}
  if (!body.playerId) {
    return Response.json({ ok: false, error: "playerId required" }, { status: 400 });
  }
  return Response.json({
    ok: false,
    reason: "stub",
    message: "AI portrait generation lands in sprint 2 (nano-banana).",
    playerId: body.playerId,
    tier: body.tier ?? null,
  });
}
