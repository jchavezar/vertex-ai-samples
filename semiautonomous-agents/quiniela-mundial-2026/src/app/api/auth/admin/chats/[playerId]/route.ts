// Admin: full chat history for a specific player.
import { NextRequest } from "next/server";
import { getChatHistory } from "@/lib/chat-history-server";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET(
  req: NextRequest,
  ctx: { params: Promise<{ playerId: string }> }
) {
  const expected = process.env.ADMIN_SECRET;
  if (!expected) return Response.json({ error: "admin_disabled" }, { status: 503 });
  const got = req.headers.get("x-admin-secret");
  if (got !== expected) return Response.json({ error: "forbidden" }, { status: 403 });
  const { playerId } = await ctx.params;
  try {
    const history = await getChatHistory(playerId, { limit: 1000 });
    return Response.json({ ok: true, history });
  } catch (e) {
    return Response.json({ error: (e as Error).message }, { status: 500 });
  }
}
