// One-off admin endpoint to generate static site assets (background images,
// promo art, etc.) via Vertex and dump them to GCS under site-assets/.
// Use ADMIN_SECRET header. Returns the public URL.

import { NextRequest } from "next/server";
import { getStorage, getVertexClient, IMAGE_MODEL, CROMO_BUCKET } from "@/lib/avatar-image";

type Body = {
  prompt?: string;
  key?: string; // filename without extension
};

export async function POST(req: NextRequest) {
  const expected = process.env.ADMIN_SECRET;
  if (!expected) return Response.json({ ok: false, error: "admin_disabled" }, { status: 503 });
  if (req.headers.get("x-admin-secret") !== expected) {
    return Response.json({ ok: false, error: "forbidden" }, { status: 403 });
  }
  let body: Body = {};
  try { body = (await req.json()) as Body; } catch {}
  const prompt = (body.prompt ?? "").trim();
  const key = (body.key ?? "").trim().replace(/[^a-z0-9-_]/gi, "");
  if (!prompt || !key) {
    return Response.json({ ok: false, error: "prompt and key required" }, { status: 400 });
  }

  const ai = getVertexClient();
  const resp = await ai.models.generateContent({
    model: IMAGE_MODEL,
    contents: [{ role: "user", parts: [{ text: prompt }] }],
  });
  const out = resp.candidates?.[0]?.content?.parts ?? [];
  for (const p of out) {
    const inline = (p as { inlineData?: { mimeType?: string; data?: string } }).inlineData;
    if (inline?.data && inline?.mimeType?.startsWith("image/")) {
      const ext = inline.mimeType.split("/")[1].split("+")[0];
      const file = getStorage().bucket(CROMO_BUCKET).file(`site-assets/${key}.${ext}`);
      const buf = Buffer.from(inline.data, "base64");
      await file.save(buf, {
        contentType: inline.mimeType,
        resumable: false,
        metadata: { cacheControl: "public, max-age=86400" },
      });
      const url = `https://storage.googleapis.com/${CROMO_BUCKET}/site-assets/${key}.${ext}`;
      return Response.json({ ok: true, url, bytes: buf.length });
    }
  }
  return Response.json({ ok: false, error: "no_image_in_response" }, { status: 502 });
}
