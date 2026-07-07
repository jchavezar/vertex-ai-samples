// Owner-only cromo-compare workshop. Wraps /api/maint/cromo-compare in an
// in-app shell so the admin can validate the identity pipeline (refs + prompt)
// across all 40 styles without leaving the app or pasting ADMIN_SECRET into
// the URL. Cookie auth (playerId === "jesus") gates both this page and the
// underlying endpoints — same gate, no secret in browser-visible URLs.

import { notFound } from "next/navigation";
import Link from "next/link";
import { readAuth } from "@/lib/auth-server";
import { PLAYERS } from "@/data/players";
import { OWNER_ID } from "@/lib/admin-gate";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

type SP = { playerId?: string | string[]; mode?: string | string[] };

export default async function AdminCromosPage({ searchParams }: { searchParams: Promise<SP> }) {
  const auth = await readAuth();
  if (!auth || auth.playerId !== OWNER_ID) notFound();

  const sp = await searchParams;
  const raw = Array.isArray(sp.playerId) ? sp.playerId[0] : sp.playerId;
  const rawMode = Array.isArray(sp.mode) ? sp.mode[0] : sp.mode;
  const mode: "probe" | "full" = rawMode === "full" ? "full" : "probe";
  const humans = PLAYERS.filter(p => !p.isBot);
  const selected = humans.find(p => p.id === raw)?.id ?? humans[0]?.id ?? "";
  const probeQS = mode === "probe" ? "&probe=1" : "";
  const iframeSrc = `/api/maint/cromo-compare?playerId=${encodeURIComponent(selected)}${probeQS}`;
  const linkFor = (pid: string) => `/admin/cromos?playerId=${encodeURIComponent(pid)}&mode=${mode}`;
  const modeLinkFor = (m: "probe" | "full") => `/admin/cromos?playerId=${encodeURIComponent(selected)}&mode=${m}`;

  return (
    <main className="min-h-screen bg-[var(--bg)] pb-10">
      <section className="max-w-6xl mx-auto px-4 pt-6">
        <div className="flex items-baseline justify-between gap-3 flex-wrap">
          <div>
            <div className="text-[10px] uppercase tracking-[0.25em] text-[var(--ink-muted)] font-bold">Admin · estudio de cromos</div>
            <h1 className="font-display text-2xl sm:text-3xl font-black text-[var(--ink)]">Cromo Workshop</h1>
            <div className="text-sm text-[var(--ink-soft)] mt-1">
              {mode === "probe"
                ? "Probe · 6 estilos diagnósticos. Si la cara aguanta aquí, los 40 también."
                : "Full · los 40 estilos. Sólo cuando el probe ya pasó."}
            </div>
          </div>
          <div className="flex items-center gap-3">
            <div className="inline-flex rounded-full hairline-strong bg-white p-0.5 text-xs font-bold">
              <Link
                href={modeLinkFor("probe")}
                className={`px-3 py-1.5 rounded-full transition-colors ${mode === "probe" ? "bg-[var(--ink)] text-white" : "text-[var(--ink-soft)] hover:text-[var(--ink)]"}`}
              >
                Probe (6)
              </Link>
              <Link
                href={modeLinkFor("full")}
                className={`px-3 py-1.5 rounded-full transition-colors ${mode === "full" ? "bg-[var(--ink)] text-white" : "text-[var(--ink-soft)] hover:text-[var(--ink)]"}`}
              >
                Full (40)
              </Link>
            </div>
            <Link href="/album" className="text-xs font-semibold text-[var(--ink-soft)] hover:text-[var(--ink)] underline underline-offset-2">
              ← Álbum
            </Link>
          </div>
        </div>

        <div className="mt-5 flex flex-wrap gap-2">
          {humans.map(p => {
            const active = p.id === selected;
            return (
              <Link
                key={p.id}
                href={linkFor(p.id)}
                className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-bold transition-colors ${
                  active
                    ? "bg-[var(--ink)] text-white"
                    : "bg-white hairline-strong text-[var(--ink-soft)] hover:text-[var(--ink)]"
                }`}
                style={active ? { background: p.accent } : undefined}
              >
                <span>{p.emoji}</span>
                <span>{p.name}</span>
              </Link>
            );
          })}
        </div>
      </section>

      <section className="max-w-6xl mx-auto px-4 mt-4">
        <div className="rounded-2xl overflow-hidden border border-[var(--line)] bg-[#0b0d12] shadow-lg">
          <iframe
            key={selected}
            src={iframeSrc}
            title={`cromo-compare ${selected}`}
            className="w-full block"
            style={{ height: "calc(100vh - 220px)", minHeight: 640 }}
          />
        </div>
      </section>
    </main>
  );
}
