import { readAuth } from "@/lib/auth-server";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET() {
  const auth = await readAuth();
  if (!auth) return Response.json({ authed: false });
  return Response.json({ authed: true, playerId: auth.playerId });
}
