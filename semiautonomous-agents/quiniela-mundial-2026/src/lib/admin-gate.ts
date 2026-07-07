// Shared gate for /admin and /api/maint endpoints. True iff caller has the
// ADMIN_SECRET (header or query) OR is signed in via cookie as the owner.
//
// Same-origin browser requests carry the auth cookie automatically, so the
// in-app admin pages (e.g. /admin/cromos) can talk to these endpoints without
// ever exposing ADMIN_SECRET to the client.

import type { NextRequest } from "next/server";
import { readAuth } from "@/lib/auth-server";

export const OWNER_ID = "jesus";

export async function isAdminRequest(req: NextRequest): Promise<boolean> {
  const expected = process.env.ADMIN_SECRET;
  if (expected) {
    if (req.headers.get("x-admin-secret") === expected) return true;
    const url = new URL(req.url);
    if (url.searchParams.get("secret") === expected) return true;
  }
  try {
    const auth = await readAuth();
    if (auth?.playerId === OWNER_ID) return true;
  } catch { /* no cookie */ }
  return false;
}
