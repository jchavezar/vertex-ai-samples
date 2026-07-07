// Owner-only AI evolution dashboard. The page itself is a thin server shell
// that gates on the auth cookie (playerId === "jesus") and renders the client
// dashboard which fetches /api/admin/ai-evolution. The same endpoint is also
// gated server-side, so even if someone landed here without auth the BFF
// would refuse them.

import { notFound } from "next/navigation";
import { readAuth } from "@/lib/auth-server";
import { AiEvolutionDashboard } from "@/components/AiEvolutionDashboard";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const OWNER_ID = "jesus";

export default async function AdminAiEvolutionPage() {
  const auth = await readAuth();
  if (!auth || auth.playerId !== OWNER_ID) notFound();
  return <AiEvolutionDashboard />;
}
