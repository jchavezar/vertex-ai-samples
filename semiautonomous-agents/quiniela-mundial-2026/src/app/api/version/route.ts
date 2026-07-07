import { NextResponse } from "next/server";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export function GET() {
  return NextResponse.json(
    { build: process.env.NEXT_PUBLIC_BUILD_HASH ?? "unknown" },
    { headers: { "Cache-Control": "no-store" } },
  );
}
