// AI-generated profile avatar per player. One-shot generation (not daily
// rotation): used as the default photo across the app. Stored in GCS with the
// canonical URL kept in Firestore so the chosen avatar persists.
//
// GET ?playerId=X -> returns current stored URL (or null if none approved yet).
// POST (admin)    -> regenerates with optional style/prompt overrides and
//                    stores the new URL as the canonical one.

import { NextRequest } from "next/server";
import { db } from "@/lib/firestore-server";
import {
  generateAvatarImage,
  loadBasePhoto,
  uploadToGcs,
} from "@/lib/avatar-image";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const COLLECTION = "player_avatars";

const CORS_HEADERS: Record<string, string> = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type, X-Admin-Secret",
  "Access-Control-Max-Age": "86400",
};

function withCors(res: Response): Response {
  const headers = new Headers(res.headers);
  for (const [k, v] of Object.entries(CORS_HEADERS)) headers.set(k, v);
  return new Response(res.body, { status: res.status, headers });
}

export async function OPTIONS() {
  return new Response(null, { status: 204, headers: CORS_HEADERS });
}

// Special prompt for the AI bot player — fully synthetic. Canonical face for
// the bot; cromo themes restyle the costume/scene around this same identity.
const AI_STYLE = {
  name: "ai-bot-portrait",
  prompt: "Photorealistic editorial portrait of Ava, the female humanoid robot from the 2014 film Ex Machina — recreated FAITHFULLY to the movie's exact design (Alicia Vikander reference). Female-presenting android. CRITICAL: she is BALD — there is ZERO hair anywhere on her head. NO bangs, NO fringe, NO sideburns, NO eyebrow-line hair tufts. The ENTIRE scalp, from forehead hairline down to the nape of the neck and around both ears, is one continuous sleek silver hexagonal honeycomb metal mesh cap that hugs the skull tightly — bare polished mesh, no glowing lights, no transparent dome — exactly like the film. The forehead skin meets the mesh cap with a clean seam where a human hairline would normally be. Face: gentle oval shape, delicate jawline, small straight nose, soft lips with a faint enigmatic closed-mouth smile, large pale-blue-grey eyes, very fine pale eyebrows. Pale porcelain synthetic skin with a noticeably cool grey-blue undertone and a subtle plastic sheen — clearly artificial, not human. Visible thin translucent panel seam running along the right cheekbone toward the jaw, revealing a hint of pale grey mechanical structure underneath (subtle, not glowing). A second small translucent rectangular panel at the temple above the ear. Slender pale neck shows a faint vertical seam and transitions into a thin woven grey mesh chest plate suggesting Ava's torso — only the very top edge is visible because she's wearing the green Mexico national football team jersey collar resting OVER the chest mesh. Three-quarter angle, head turned slightly, eyes looking softly toward camera. Studio lighting: cool soft key from front-left, neutral grey-blue rim from back-right, low contrast cinematic. Dark charcoal-to-black gradient background. Tight square 1:1 framing — face, neck, and upper shoulders only. Photoreal cinematic still from a sci-fi film, editorial magazine quality, NOT cartoon or 3D-rendered. Serene, intelligent, slightly mysterious expression — NEVER menacing, NEVER human. No text, no watermark, no logos.",
};

const STYLES = [
  {
    name: "mexico-stadium",
    prompt: "Wearing the official adidas Mexico national football team home jersey for FIFA World Cup 2026: deep vibrant verde (green) base with bold Aztec geometric patterns — sharply reimagined stepped greca motifs inspired by ancient Mesoamerican temple reliefs — rendered as intricate interlocking linework covering the chest and shoulders, adidas three-stripe sleeves in white, official FMF eagle crest embroidered on the left chest, subtle 'SOMOS MÉXICO' inscribed inside the collar. Dramatic Estadio Azteca night background, green-white-red bokeh confetti, golden rim light from the side, cinematic stadium hero portrait, head and shoulders, proud confident pose, crisp FIFA championship-photo finish",
  },
  {
    name: "mexico-papel-picado",
    prompt: "Wearing the green Mexico national football team jersey, vibrant Día de Muertos papel picado background in green-white-red, marigold petals floating, warm sunset light, head and shoulders portrait, joyful confident expression, glossy poster finish",
  },
  {
    name: "mexico-mural",
    prompt: "Wearing the Mexico national team green jersey, background is a bold Mexican muralist-style scene (Diego Rivera inspired) with aztec eagles and sun motifs, dramatic studio lighting, head and shoulders, dignified pose, painterly poster finish",
  },
  {
    name: "mexico-graffiti",
    prompt: "Wearing the green Mexico jersey, urban street-art graffiti background in green-white-red with stylized aztec glyphs, vibrant neon-meets-folk colors, smoke + lens flare, head and shoulders, swagger pose, magazine cover finish",
  },
  {
    name: "mexico-azteca",
    prompt: "Wearing the green Mexico national team jersey, background is the Estadio Azteca at golden hour packed with a sea of green tricolor flags, lens flares, head and shoulders portrait, intense gaze, championship-photo finish",
  },
];

function styleFor(override?: number) {
  if (typeof override === "number" && override >= 0 && override < STYLES.length) {
    return STYLES[override];
  }
  return STYLES[0];
}

async function regenerate(
  playerId: string,
  styleOverride: number | undefined,
  extra: string | undefined,
  approve: boolean,
): Promise<Response> {
  const isAi = playerId === "ai";
  const style = isAi ? AI_STYLE : styleFor(styleOverride);
  const basePhoto = isAi ? undefined : (await loadBasePhoto(playerId)) ?? undefined;
  if (!isAi && !basePhoto) {
    return Response.json({ ok: false, reason: "no_base_photo" }, { status: 400 });
  }

  const result = await generateAvatarImage({
    basePhoto,
    stylePrompt: style.prompt,
    extraNote: extra,
    synthetic: isAi,
  });
  if (!result) return Response.json({ ok: false, reason: "generation_failed" }, { status: 502 });

  let publicUrl: string;
  try {
    const stamp = Date.now();
    publicUrl = await uploadToGcs({
      objectName: `profiles/${playerId}-${stamp}.png`,
      dataUrl: result.dataUrl,
    });
  } catch (err) {
    console.error("[avatars/profile] gcs upload failed", err);
    return Response.json({ ok: false, reason: "upload_failed" }, { status: 502 });
  }
  if (approve) {
    const ref = db.collection(COLLECTION).doc(playerId);
    await ref.set({
      playerId,
      style: style.name,
      url: publicUrl,
      note: extra ?? null,
      updatedAt: Date.now(),
    }, { merge: true });
  }
  return Response.json({ ok: true, url: publicUrl, style: style.name, approved: approve });
}

export async function GET(req: NextRequest) {
  const { searchParams } = new URL(req.url);
  const playerId = searchParams.get("playerId");
  if (!playerId) return withCors(Response.json({ ok: false, error: "playerId required" }, { status: 400 }));

  const ref = db.collection(COLLECTION).doc(playerId);
  const snap = await ref.get();
  if (snap.exists) {
    const data = snap.data() as { url?: string; style?: string; updatedAt?: number };
    if (data?.url) {
      return withCors(Response.json({ ok: true, url: data.url, style: data.style ?? null, updatedAt: data.updatedAt ?? null }));
    }
  }
  return withCors(Response.json({ ok: true, url: null }));
}

export async function POST(req: NextRequest) {
  const expected = process.env.ADMIN_SECRET;
  if (!expected) return withCors(Response.json({ ok: false, error: "admin_disabled" }, { status: 503 }));
  if (req.headers.get("x-admin-secret") !== expected) {
    return withCors(Response.json({ ok: false, error: "forbidden" }, { status: 403 }));
  }
  type Body = { playerId?: string; style?: number; prompt?: string; approve?: boolean };
  let body: Body = {};
  try { body = (await req.json()) as Body; } catch {}
  if (!body.playerId) return withCors(Response.json({ ok: false, error: "playerId required" }, { status: 400 }));
  return withCors(await regenerate(body.playerId, body.style, body.prompt, body.approve === true));
}
