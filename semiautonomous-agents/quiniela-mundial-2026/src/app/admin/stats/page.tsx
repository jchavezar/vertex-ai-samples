// Owner-only stats dashboard. Server-rendered gate: anyone not signed in as
// "jesus" gets a 404. Heavy lifting happens client-side in StatsDashboard so
// the page can refresh without a full reload.

import { notFound } from "next/navigation";
import { readAuth } from "@/lib/auth-server";
import { StatsDashboard } from "@/components/StatsDashboard";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const OWNER_ID = "jesus";

export default async function AdminStatsPage() {
  const auth = await readAuth();
  if (!auth || auth.playerId !== OWNER_ID) notFound();
  return <StatsDashboard />;
}
