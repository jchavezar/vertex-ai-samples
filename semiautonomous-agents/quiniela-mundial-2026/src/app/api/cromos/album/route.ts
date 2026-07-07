// Day-by-day album of all generated cromos. Normal flow returns only past +
// today (no spoilers). Admin (cookie playerId === "jesus") additionally gets
// every future day up to the World Cup final as empty placeholders so the
// admin can preview themes and trigger generation per cell.

import { db } from "@/lib/firestore-server";
import { readAuth } from "@/lib/auth-server";
import { styleForDay } from "@/app/api/cromos/portrait/route";
import { TOURNAMENT } from "@/data/tournament";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const COLLECTION = "cromo_portraits";
const OWNER_ID = "jesus";

function todayKey(): string {
  return new Intl.DateTimeFormat("en-CA", {
    timeZone: "America/New_York",
    year: "numeric", month: "2-digit", day: "2-digit",
  }).format(new Date());
}

function tournamentEndKey(): string {
  // TOURNAMENT.endDate is ISO with tz offset; reduce to YYYY-MM-DD in ET.
  return new Intl.DateTimeFormat("en-CA", {
    timeZone: "America/New_York",
    year: "numeric", month: "2-digit", day: "2-digit",
  }).format(new Date(TOURNAMENT.endDate));
}

function* eachDay(startISO: string, endISO: string): Generator<string> {
  // Iterate by adding 1 day to UTC noon to avoid DST edges.
  const [sy, sm, sd] = startISO.split("-").map(n => parseInt(n, 10));
  const [ey, em, ed] = endISO.split("-").map(n => parseInt(n, 10));
  const cursor = Date.UTC(sy, sm - 1, sd, 12);
  const stop = Date.UTC(ey, em - 1, ed, 12);
  for (let t = cursor; t <= stop; t += 86400000) {
    const d = new Date(t);
    const yy = d.getUTCFullYear();
    const mm = String(d.getUTCMonth() + 1).padStart(2, "0");
    const dd = String(d.getUTCDate()).padStart(2, "0");
    yield `${yy}-${mm}-${dd}`;
  }
}

type Doc = {
  playerId?: string;
  date?: string;
  style?: string;
  url?: string;
  createdAt?: number;
};

export async function GET() {
  const today = todayKey();
  const auth = await readAuth();
  const isAdmin = auth?.playerId === OWNER_ID;
  const cutoff = isAdmin ? tournamentEndKey() : today;

  const snap = await db.collection(COLLECTION).get();
  const byDate = new Map<string, {
    style: string | null;
    cromos: Array<{ playerId: string; url: string; createdAt: number }>;
  }>();

  for (const d of snap.docs) {
    const data = d.data() as Doc;
    if (!data.date || !data.playerId || !data.url) continue;
    if (data.date > cutoff) continue;
    const entry = byDate.get(data.date) ?? { style: null, cromos: [] };
    // Prefer human style for the spread header; AI bot rotates independently.
    const isAiStyle = data.style?.startsWith("ai-");
    if (data.style && (!entry.style || (entry.style.startsWith("ai-") && !isAiStyle))) {
      entry.style = data.style;
    }
    const v = data.createdAt ?? 0;
    const url = data.url.includes("?") ? data.url : `${data.url}?v=${v}`;
    entry.cromos.push({ playerId: data.playerId, url, createdAt: v });
    byDate.set(data.date, entry);
  }

  // Admin sees future days too. Fill in placeholders with the rotation's
  // computed theme so admin can plan ahead and generate per cell.
  if (isAdmin) {
    const tournamentStart = (() => {
      return new Intl.DateTimeFormat("en-CA", {
        timeZone: "America/New_York",
        year: "numeric", month: "2-digit", day: "2-digit",
      }).format(new Date(TOURNAMENT.startDate));
    })();
    for (const date of eachDay(tournamentStart, cutoff)) {
      if (byDate.has(date)) continue;
      byDate.set(date, { style: styleForDay(date).name, cromos: [] });
    }
    // Also fill in style preview for past/today entries that exist but with
    // only AI cromos (so the human-style header shows correctly).
    for (const [date, entry] of byDate) {
      if (!entry.style || entry.style.startsWith("ai-")) {
        entry.style = styleForDay(date).name;
      }
      byDate.set(date, entry);
    }
  }

  const days = Array.from(byDate.entries())
    .sort((a, b) => a[0].localeCompare(b[0]))
    .map(([date, entry]) => ({
      date,
      style: entry.style,
      cromos: entry.cromos.sort((a, b) => a.playerId.localeCompare(b.playerId)),
    }));

  return Response.json({ ok: true, today, days, admin: isAdmin });
}
