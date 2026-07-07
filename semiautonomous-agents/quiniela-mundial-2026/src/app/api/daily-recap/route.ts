// GET /api/daily-recap
//
// Public read endpoint for the home page's "Crónica de Ava" card. Picks the
// day whose recap has the freshest entry — that way an in-progress today
// (with one or more update entries) wins over yesterday, but yesterday's
// late-night wrap-up still shows in the early morning.

import { db } from "@/lib/firestore-server";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const COLLECTION = "daily_recaps";

type RecapEntry = {
  generatedAt: number;
  narration: string;
  fixtureIds: string[];
  scores: Record<string, string>;
  kind: "opening" | "update";
};

type RecapDoc = {
  date: string;
  narration: string;        // mirror of latest entry
  generatedAt: number;
  entries?: RecapEntry[];
  fixtureSummaries?: Array<{ fixtureId: string; home: string; away: string; score: string; winnerPlayers: string[] }>;
  modelUsed?: string;
};

function cdmxDate(d = new Date()): string {
  return new Intl.DateTimeFormat("en-CA", {
    timeZone: "America/Mexico_City",
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  }).format(d);
}

function shiftCdmx(dateStr: string, deltaDays: number): string {
  const anchor = new Date(`${dateStr}T12:00:00Z`).getTime();
  return cdmxDate(new Date(anchor + deltaDays * 24 * 60 * 60 * 1000));
}

async function readDoc(id: string): Promise<RecapDoc | null> {
  const snap = await db.collection(COLLECTION).doc(id).get();
  if (!snap.exists) return null;
  const raw = snap.data() as RecapDoc;
  // Back-fill entries[] for legacy docs that only stored `narration`.
  if (!raw.entries || raw.entries.length === 0) {
    raw.entries = raw.narration
      ? [{
          generatedAt: raw.generatedAt ?? 0,
          narration: raw.narration,
          fixtureIds: (raw.fixtureSummaries ?? []).map(s => s.fixtureId),
          scores: Object.fromEntries((raw.fixtureSummaries ?? []).map(s => [s.fixtureId, s.score])),
          kind: "opening",
        }]
      : [];
  }
  return raw;
}

export async function GET() {
  const today = cdmxDate();
  const yesterday = shiftCdmx(today, -1);
  const [todayDoc, yesterdayDoc] = await Promise.all([readDoc(today), readDoc(yesterday)]);

  // Pick the doc with the freshest entry. Ties or missing -> prefer today.
  let pick: { id: string; doc: RecapDoc } | null = null;
  for (const candidate of [todayDoc ? { id: today, doc: todayDoc } : null, yesterdayDoc ? { id: yesterday, doc: yesterdayDoc } : null]) {
    if (!candidate) continue;
    if (!pick) { pick = candidate; continue; }
    if ((candidate.doc.generatedAt ?? 0) > (pick.doc.generatedAt ?? 0)) pick = candidate;
  }
  if (!pick) return Response.json({ ok: true, recap: null });
  return Response.json({ ok: true, recap: pick.doc, label: pick.id === today ? "hoy" : "ayer" });
}
