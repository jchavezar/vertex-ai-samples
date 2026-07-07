// Test-only auth bypass for Playwright E2E. Gated by Q26_TEST_LOGIN_SECRET.
// Missing secret → 503 (prod-safe — never returns OK if the env var is unset).
import { setAuthCookie } from "@/lib/auth-server";
import { PLAYERS } from "@/data/players";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function POST(req: Request) {
  const expected = process.env.Q26_TEST_LOGIN_SECRET;
  if (!expected) {
    return Response.json({ ok: false, error: "test-login disabled" }, { status: 503 });
  }
  if (req.headers.get("x-admin-secret") !== expected) {
    return Response.json({ ok: false, error: "forbidden" }, { status: 403 });
  }
  let body: { playerId?: string };
  try { body = await req.json(); }
  catch { return Response.json({ ok: false, error: "invalid json" }, { status: 400 }); }
  const playerId = body.playerId;
  if (!playerId || !PLAYERS.some(p => p.id === playerId)) {
    return Response.json({ ok: false, error: "unknown playerId" }, { status: 400 });
  }
  await setAuthCookie(playerId);
  return Response.json({ ok: true, playerId });
}
