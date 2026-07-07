// One-shot: generate a photorealistic FIFA World Cup trophy on light/cream
// background and save to public/trophy-bg.png for use as the homepage watermark.
// Run: node scripts/generate-trophy-bg.mjs

import { GoogleGenAI } from "@google/genai";
import { promises as fs } from "node:fs";
import path from "node:path";

const ai = new GoogleGenAI({
  vertexai: true,
  project: process.env.GOOGLE_CLOUD_PROJECT || "vtxdemos",
  location: process.env.VERTEX_LOCATION || "global",
});

const PROMPT = `Photorealistic studio still life of THE official FIFA World Cup Trophy: solid 18-karat gold sculpture of two stylized human figures with outstretched arms together holding up a globe, mounted on a dark malachite green base with two thin gold rings around it. Premium product photography, centered composition, vertical 3:4 portrait, soft directional rim light from upper left, very subtle warm gold reflections, ultra clean cream-to-white seamless paper backdrop, no people, no text, no logos, no badges, hyper-detailed gold surface with realistic reflections and contact shadow on the surface. Editorial magazine quality, looks like it could be on the cover of a luxury sports publication. Negative: cartoon, low-poly, painted, line art, words, dark background, dramatic shadow, sparkles.`;

const MODEL = process.env.CROMO_IMAGE_MODEL || "gemini-3-pro-image-preview";

console.log(`[trophy] generating with ${MODEL}...`);
const resp = await ai.models.generateContent({
  model: MODEL,
  contents: [{ role: "user", parts: [{ text: PROMPT }] }],
});

const out = resp.candidates?.[0]?.content?.parts ?? [];
let saved = false;
for (const p of out) {
  const inline = p.inlineData;
  if (inline?.data && inline?.mimeType?.startsWith("image/")) {
    const ext = inline.mimeType.split("/")[1].split("+")[0];
    const buf = Buffer.from(inline.data, "base64");
    const dest = path.join(process.cwd(), "public", `trophy-bg.${ext}`);
    await fs.writeFile(dest, buf);
    console.log(`[trophy] wrote ${dest} (${buf.length} bytes)`);
    saved = true;
    break;
  }
}

if (!saved) {
  console.error("[trophy] no image part in response", JSON.stringify(out, null, 2));
  process.exit(1);
}
