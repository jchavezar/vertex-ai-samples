// Live Mundial 2026 top scorers — see ./_logic.ts for the full aggregator.
// This file is a thin HTTP wrapper so /api/home/snapshot can call the
// computation directly without an HTTP round-trip.

import { NextResponse } from "next/server";
import { computeTopScorers, type ScorersResponse, type ScorerEntry } from "./_logic";

export const dynamic = "force-dynamic";
export const revalidate = 0;

// Re-export so existing client imports `import type { ScorerEntry, ScorersResponse } from "@/app/api/scorers/route"`
// keep working without modification.
export type { ScorerEntry, ScorersResponse };

export async function GET() {
  const result = await computeTopScorers();
  if (!result.ok) {
    return NextResponse.json(result satisfies ScorersResponse, { status: 502 });
  }
  return NextResponse.json(
    result satisfies ScorersResponse,
    { headers: { "Cache-Control": "public, max-age=20, stale-while-revalidate=120" } },
  );
}
