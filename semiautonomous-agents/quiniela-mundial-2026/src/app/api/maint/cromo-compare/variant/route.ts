// Generates ONE cromo variant on demand and returns it as image/png. Called by
// the compare page's <img> tags so the HTML loads instantly and the 4 variants
// stream in progressively instead of one 12MB monolithic response.

import { NextRequest } from "next/server";
import { PLAYERS } from "@/data/players";
import { generatePortrait, PORTRAIT_STYLES } from "@/app/api/cromos/portrait/route";
import { readKeeper } from "@/app/api/maint/cromo-compare/keeper/route";
import { readLastVariant, saveLastVariant } from "@/lib/cromo-keepers";
import { isAdminRequest } from "@/lib/admin-gate";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";
export const maxDuration = 300;

export async function GET(req: NextRequest) {
  if (!(await isAdminRequest(req))) {
    return new Response("forbidden", { status: 403 });
  }
  const { searchParams } = new URL(req.url);
  const playerId = (searchParams.get("playerId") ?? "").trim();
  const styleStr = searchParams.get("style");
  const force = searchParams.get("force") === "1";
  if (!playerId) return new Response("playerId required", { status: 400 });
  if (!PLAYERS.some(p => p.id === playerId)) return new Response("unknown player", { status: 400 });
  const idx = styleStr === null ? NaN : parseInt(styleStr, 10);
  if (!Number.isFinite(idx) || idx < 0 || idx >= PORTRAIT_STYLES.length) {
    return new Response("invalid style", { status: 400 });
  }

  const styleName = PORTRAIT_STYLES[idx].name;
  // Per-variant `extra` text: the workshop lets the admin type ad-hoc tweaks
  // (pose, expression, framing) per cromo. When present we bypass cached
  // images because the admin explicitly wants a fresh render with the new
  // direction.
  const extra = (searchParams.get("extra") ?? "").trim() || undefined;

  // Read priority (admin's mental model on reload):
  //   1. ⭐ keeper — canonical, the admin picked this
  //   2. _last_variants/ — most recent generation, "what I saw last time"
  //   3. fresh model call
  // 🎲 reroll (force=1) or ↻ extra-direction skip 1+2 and always regenerate.
  if (!force && !extra) {
    const keeper = await readKeeper(playerId, styleName);
    if (keeper) {
      return new Response(new Uint8Array(keeper), {
        status: 200,
        headers: {
          "content-type": "image/png",
          "cache-control": "no-store",
          "x-style-name": styleName,
          "x-source": "keeper",
        },
      });
    }
    const last = await readLastVariant(playerId, styleName);
    if (last) {
      return new Response(new Uint8Array(last), {
        status: 200,
        headers: {
          "content-type": "image/png",
          "cache-control": "no-store",
          "x-style-name": styleName,
          "x-source": "last",
        },
      });
    }
  }

  const today = new Intl.DateTimeFormat("en-CA", {
    timeZone: "America/New_York",
    year: "numeric", month: "2-digit", day: "2-digit",
  }).format(new Date());
  const res = await generatePortrait(playerId, today, idx, extra);
  if (!res) return new Response("generation failed", { status: 502 });

  const m = /^data:([^;]+);base64,(.+)$/.exec(res.dataUrl);
  if (!m) return new Response("invalid dataUrl from model", { status: 502 });
  const mime = m[1];
  const buf = Buffer.from(m[2], "base64");
  // Auto-save as the new "last variant" so the admin can come back later and
  // see the exact same render — they'll never lose a good one to a reload.
  void saveLastVariant(playerId, styleName, buf).catch(e =>
    console.warn("[variant] saveLastVariant failed (non-fatal)", e instanceof Error ? e.message : e),
  );
  return new Response(buf, {
    status: 200,
    headers: {
      "content-type": mime,
      "cache-control": "no-store",
      "x-style-name": res.style,
      "x-source": "fresh",
    },
  });
}
