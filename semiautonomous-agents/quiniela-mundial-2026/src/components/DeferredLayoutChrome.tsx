"use client";

// Wraps the layout-level chrome components that don't need to render on the
// critical path so their bundles are split out of the initial download.
// Lives in a Client Component because `next/dynamic({ ssr: false })` is not
// allowed in Server Components (layout.tsx is a Server Component).

import dynamic from "next/dynamic";

const LiveEventOverlay = dynamic(
  () => import("@/components/LiveEventOverlay").then(m => ({ default: m.LiveEventOverlay })),
  { ssr: false },
);

const SyncStatusBanner = dynamic(
  () => import("@/components/SyncStatusBanner").then(m => ({ default: m.SyncStatusBanner })),
  { ssr: false },
);

export function DeferredLayoutChrome() {
  return (
    <>
      <SyncStatusBanner />
      <LiveEventOverlay />
    </>
  );
}
