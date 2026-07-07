// Delete a photo_history entry (soft delete — leaves the GCS object alone).
// Only the owner can delete their own history entries.

import { NextRequest } from "next/server";
import { readAuth } from "@/lib/auth-server";
import { db } from "@/lib/firestore-server";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const COLLECTION = "player_avatars";

export async function DELETE(_req: NextRequest, { params }: { params: Promise<{ id: string }> }) {
  const auth = await readAuth();
  if (!auth) return Response.json({ ok: false, error: "unauthorized" }, { status: 401 });
  const { id } = await params;
  if (!id) return Response.json({ ok: false, error: "id_required" }, { status: 400 });

  const ref = db.collection(COLLECTION).doc(auth.playerId).collection("photo_history").doc(id);
  const snap = await ref.get();
  if (!snap.exists) return Response.json({ ok: false, error: "not_found" }, { status: 404 });
  await ref.delete();
  return Response.json({ ok: true });
}
