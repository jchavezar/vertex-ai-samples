import { readAuth } from "@/lib/auth-server";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const BRIDGE_URL = process.env.Q26_MAINT_BRIDGE_URL;
const BRIDGE_TOKEN = process.env.Q26_MAINT_BRIDGE_TOKEN;
const ALLOWED_USER = "jesus";

export async function POST(req: Request) {
  if (!BRIDGE_URL || !BRIDGE_TOKEN) {
    return new Response("maintenance bridge not configured", { status: 503 });
  }
  const session = await readAuth();
  if (!session || session.playerId !== ALLOWED_USER) {
    return new Response("forbidden", { status: 403 });
  }
  const body = await req.text();
  const upstream = await fetch(`${BRIDGE_URL}/permission`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${BRIDGE_TOKEN}`,
    },
    body,
  });
  const txt = await upstream.text();
  return new Response(txt, { status: upstream.status, headers: { "Content-Type": "application/json" } });
}
