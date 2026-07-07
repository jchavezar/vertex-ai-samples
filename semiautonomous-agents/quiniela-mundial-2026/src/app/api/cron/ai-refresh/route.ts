// POST /api/cron/ai-refresh
//
// Cloud Scheduler entry point (gated by `x-cron-secret`). Runs the full
// AI/probability refresh cycle:
//   1) Rebuild + snapshot fixture probabilities.
//   2) Re-simulate the bracket (10k iter Monte Carlo) + snapshot.
//   3) Run the AI bot sync (Gemini-reasoned picks for every non-locked match).
//
// Frequency: every 6 hours (see scheduler job q26-ai-refresh). The endpoint
// is idempotent and safe to call manually for forced refresh.
//
// Anti-cheat: every step honors the per-fixture kickoff lock. The bot picks
// are written through `upsertPicks`, which uses `mergeWithServerLocks` to
// enforce that locked fixtures keep whatever was stored before kickoff.

import { NextRequest } from "next/server";
import { POST as syncAi } from "@/app/api/ai/sync/route";
import { POST as recomputeProbs } from "@/app/api/probabilities/route";
import { POST as recomputeBracket } from "@/app/api/probabilities/bracket/route";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";
export const maxDuration = 600;

type StepResult = { step: string; ok: boolean; ms: number; detail?: unknown; error?: string };

async function runStep(name: string, fn: () => Promise<Response>): Promise<StepResult> {
  const t0 = Date.now();
  try {
    const r = await fn();
    const j = await r.json().catch(() => ({}));
    return { step: name, ok: !!j?.ok, ms: Date.now() - t0, detail: j };
  } catch (e) {
    return { step: name, ok: false, ms: Date.now() - t0, error: (e as Error).message };
  }
}

export async function POST(req: NextRequest) {
  const expected = process.env.CRON_SECRET;
  if (!expected) {
    return Response.json({ ok: false, error: "cron_disabled" }, { status: 503 });
  }
  if (req.headers.get("x-cron-secret") !== expected) {
    return Response.json({ ok: false, error: "forbidden" }, { status: 403 });
  }

  const results: StepResult[] = [];

  // 1) Per-fixture probabilities (also persists market odds + daily snapshot).
  results.push(await runStep("probabilities", () => recomputeProbs()));

  // 2) Bracket Monte Carlo (depends on step 1's snapshot).
  results.push(await runStep("bracket", () => recomputeBracket()));

  // 3) AI bot picks (uses the same blender + Gemini reasoning).
  results.push(await runStep("ai-sync", () => syncAi()));

  const ok = results.every(r => r.ok);
  return Response.json({ ok, runAt: Date.now(), results });
}
