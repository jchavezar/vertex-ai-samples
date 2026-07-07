// Admin-only: list all PINs. Protected by X-Admin-Secret header.
import { NextRequest } from "next/server";
import { listPins } from "@/lib/pins";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET(req: NextRequest) {
  const expected = process.env.ADMIN_SECRET;
  if (!expected) return Response.json({ error: "admin_disabled" }, { status: 503 });
  const got = req.headers.get("x-admin-secret");
  if (got !== expected) return Response.json({ error: "forbidden" }, { status: 403 });
  try {
    const rows = await listPins();
    return Response.json({
      count: rows.length,
      pins: rows.map(r => ({
        playerId: r.playerId,
        name: r.name,
        pin: r.pin,
        isDefault: r.isDefault,
        updatedAt: r.updatedAt ? new Date(r.updatedAt).toISOString() : null,
      })),
    });
  } catch (e) {
    return Response.json({ error: (e as Error).message }, { status: 500 });
  }
}
