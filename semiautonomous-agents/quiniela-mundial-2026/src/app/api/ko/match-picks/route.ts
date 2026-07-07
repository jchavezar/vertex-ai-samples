// GET /api/ko/match-picks?slot=R16-1
// Returns each player's pick for a given KO slot.
// For R16, picks are stored as bracket.R16[idx] (0-based).
// For R32, picks are stored as bracket.R32[idx] (0-based).

import { NextRequest } from "next/server";
import { db } from "@/lib/firestore-server";
import { PICKS_COLLECTION } from "@/lib/predictions-server";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

// Official FIFA 2026 R16 pairings [R32-slotA, R32-slotB] — same as KnockoutSection.tsx
const R16_PAIRINGS: Array<[number, number]> = [
  [1, 3],    // R16-1
  [2, 5],    // R16-2
  [4, 6],    // R16-3
  [7, 8],    // R16-4
  [11, 12],  // R16-5
  [9, 10],   // R16-6
  [15, 16],  // R16-7
  [13, 14],  // R16-8
];

export async function GET(req: NextRequest) {
  const slot = req.nextUrl.searchParams.get("slot");
  if (!slot) return Response.json({ ok: false, error: "missing slot" }, { status: 400 });

  // Parse slot like "R16-1" or "R32-3"
  const match = slot.match(/^(R32|R16|QF|SF)-(\d+)$/);
  if (!match) return Response.json({ ok: false, error: "invalid slot format" }, { status: 400 });

  const round = match[1] as "R32" | "R16" | "QF" | "SF";
  const slotNum = parseInt(match[2], 10);
  const slotIdx = slotNum - 1;

  const roundSizes: Record<string, number> = { R32: 16, R16: 8, QF: 4, SF: 2 };
  const maxIdx = (roundSizes[round] ?? 1) - 1;
  if (slotIdx < 0 || slotIdx > maxIdx) {
    return Response.json({ ok: false, error: `slot index out of range for ${round}` }, { status: 400 });
  }

  try {
    const snapshot = await db.collection(PICKS_COLLECTION).get();
    const picks: Record<string, string | null> = {};

    for (const doc of snapshot.docs) {
      const data = doc.data() as Record<string, unknown>;
      const bracket = data.bracket as Record<string, unknown> | undefined;
      if (!bracket) {
        picks[doc.id] = null;
        continue;
      }
      const arr = bracket[round] as string[] | undefined;
      const pick = arr?.[slotIdx] ?? null;
      picks[doc.id] = pick || null;
    }

    // Also include R16_PAIRINGS info if it's an R16 slot
    const extra: Record<string, unknown> = {};
    if (round === "R16") {
      const pairing = R16_PAIRINGS[slotIdx];
      if (pairing) {
        extra.r32SlotA = pairing[0];
        extra.r32SlotB = pairing[1];
      }
    }

    return Response.json({ ok: true, slot, round, slotIdx, picks, ...extra });
  } catch (e) {
    return Response.json({ ok: false, error: (e as Error).message }, { status: 500 });
  }
}
