// Public read of all 10 player profile overrides (avatar/photo/name).
// No auth required — these are visible to anyone using the app.
import { listProfiles } from "@/lib/profiles-server";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET() {
  try {
    const all = await listProfiles();
    return Response.json({ ok: true, profiles: all });
  } catch (e) {
    console.error("[/api/profiles] error", e);
    return Response.json({ ok: false, profiles: {} }, { status: 500 });
  }
}
