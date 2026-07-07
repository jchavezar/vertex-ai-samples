// Admin: list per-player chat summaries.
import { NextRequest } from "next/server";
import { listPlayerChats } from "@/lib/chat-history-server";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET(req: NextRequest) {
  const expected = process.env.ADMIN_SECRET;
  if (!expected) return Response.json({ error: "admin_disabled" }, { status: 503 });
  const got = req.headers.get("x-admin-secret");
  if (got !== expected) return Response.json({ error: "forbidden" }, { status: 403 });
  try {
    const rows = await listPlayerChats();
    return Response.json({ count: rows.length, chats: rows });
  } catch (e) {
    return Response.json({ error: (e as Error).message }, { status: 500 });
  }
}
