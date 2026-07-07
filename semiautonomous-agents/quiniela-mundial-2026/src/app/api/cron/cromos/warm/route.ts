// Pre-generates today's cromo portraits for every player. Triggered by
// Cloud Scheduler at ET midnight so the daily style rotation is warm before
// the first user request.
//
// Calls the portrait GET handler in-process (not via HTTP) because the Cloud
// Run instance can't loop back to its own custom domain through Cloudflare.

import { NextRequest } from "next/server";
import { PLAYERS } from "@/data/players";
import { GET as portraitGet } from "@/app/api/cromos/portrait/route";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";
export const maxDuration = 300;

function todayKeyET(): string {
  const fmt = new Intl.DateTimeFormat("en-CA", {
    timeZone: "America/New_York",
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  });
  return fmt.format(new Date());
}

type Result = { id: string; ok: boolean; style?: string; error?: string };

export async function POST(req: NextRequest) {
  const expected = process.env.CRON_SECRET;
  if (!expected) {
    return Response.json({ ok: false, error: "cron_disabled" }, { status: 503 });
  }
  if (req.headers.get("x-cron-secret") !== expected) {
    return Response.json({ ok: false, error: "forbidden" }, { status: 403 });
  }

  const ids = PLAYERS.map((p) => p.id);
  const origin = req.nextUrl.origin;

  const settled = await Promise.allSettled(
    ids.map(async (id): Promise<Result> => {
      try {
        const url = `${origin}/api/cromos/portrait?playerId=${id}&force=1`;
        const inner = new NextRequest(url, { method: "GET" });
        const r = await portraitGet(inner);
        const j = (await r.json()) as { ok?: boolean; style?: string; reason?: string; error?: string };
        if (!r.ok || !j.ok) {
          return { id, ok: false, error: j.reason || j.error || `http_${r.status}` };
        }
        return { id, ok: true, style: j.style };
      } catch (err) {
        return { id, ok: false, error: (err as Error).message };
      }
    }),
  );

  const generated: Result[] = settled.map((s, i) =>
    s.status === "fulfilled" ? s.value : { id: ids[i], ok: false, error: String(s.reason) },
  );

  return Response.json({ ok: true, date: todayKeyET(), generated });
}
