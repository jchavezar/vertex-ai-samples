// GET /api/envelope/today — returns today's envelope state for the logged-in
// user. Idempotent read; the doc is created by POST /api/envelope/open.
import { readAuth } from "@/lib/auth-server";
import { db } from "@/lib/firestore-server";
import { etTodayKey, msUntilNextEtMidnight, type EnvelopeOpenDoc } from "@/lib/envelope";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET() {
  const auth = await readAuth();
  if (!auth) {
    return Response.json({ ok: false, error: "unauthorized" }, { status: 401 });
  }
  const playerId = auth.playerId;
  const today = etTodayKey();

  const ref = db
    .collection("daily_envelopes")
    .doc(playerId)
    .collection("opens")
    .doc(today);

  const snap = await ref.get();
  const countdownUntil = msUntilNextEtMidnight();

  if (!snap.exists) {
    return Response.json({
      ok: true,
      opened: false,
      date: today,
      countdownUntilMs: countdownUntil,
    });
  }

  const data = snap.data() as EnvelopeOpenDoc;
  return Response.json({
    ok: true,
    opened: true,
    date: today,
    countdownUntilMs: countdownUntil,
    reward: data.reward,
    openedAt: data.openedAt,
  });
}
