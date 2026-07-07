// POST  body: { playerId, favorites, fillOnlyEmpty, manualScores? }
// Returns proposed picks (does NOT write to Firestore). Gated by x-q26-agent-secret.
import { getPicks } from "@/lib/predictions-server";
import { generateGroupProposals, type ManualScoreOverride } from "@/lib/ai-predictions";
import type { GroupPrediction } from "@/lib/predictions";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

type Body = {
  playerId?: string;
  favorites?: string[];
  fillOnlyEmpty?: boolean;
  manualScores?: ManualScoreOverride[];
};

export async function POST(req: Request) {
  const secret = process.env.Q26_AGENT_SECRET;
  if (!secret) return Response.json({ ok: false, error: "server misconfigured" }, { status: 500 });
  if (req.headers.get("x-q26-agent-secret") !== secret) {
    return Response.json({ ok: false, error: "forbidden" }, { status: 403 });
  }

  let body: Body;
  try {
    body = await req.json();
  } catch {
    return Response.json({ ok: false, error: "invalid json" }, { status: 400 });
  }

  const playerId = body.playerId;
  if (!playerId) return Response.json({ ok: false, error: "playerId required" }, { status: 400 });

  const favorites = Array.isArray(body.favorites) ? body.favorites.filter(x => typeof x === "string") : [];
  const fillOnlyEmpty = body.fillOnlyEmpty !== false;
  const manualScores = Array.isArray(body.manualScores) ? body.manualScores : [];

  try {
    const current = (await getPicks(playerId)) as { group?: Record<string, GroupPrediction> } | null;
    const existing = current?.group ?? {};
    const proposals = generateGroupProposals({
      favorites,
      existing,
      fillOnlyEmpty,
      manualScores,
    });
    return Response.json({
      ok: true,
      proposals,
      counts: {
        total: proposals.length,
        existing: Object.values(existing).filter(g => g?.pick).length,
        wouldOverwrite: fillOnlyEmpty ? 0 : Object.values(existing).filter(g => g?.pick).length,
      },
    });
  } catch (e) {
    console.error("[/api/ai-predictions/propose] error", e);
    return Response.json({ ok: false, error: "internal" }, { status: 500 });
  }
}
