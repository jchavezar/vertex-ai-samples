import { clearAuthCookie } from "@/lib/auth-server";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function POST() {
  await clearAuthCookie();
  return Response.json({ ok: true });
}
