// One-shot: generate the canonical AI bot face (Ava-from-Ex-Machina inspired)
// and save to public/players/ai.jpg. Every daily cromo will reference this
// portrait so the AI keeps the same identity across themes.
// Run: node scripts/generate-ai-face.mjs

import { GoogleGenAI } from "@google/genai";
import { promises as fs } from "node:fs";
import path from "node:path";

const ai = new GoogleGenAI({
  vertexai: true,
  project: process.env.GOOGLE_CLOUD_PROJECT || "vtxdemos",
  location: process.env.VERTEX_LOCATION || "global",
});

const PROMPT = `Photorealistic hero portrait of a beautiful young female humanoid android, inspired by Ava from the film Ex Machina. Soft feminine facial features with delicate jawline, full lips with a subtle warm smile, large kind expressive hazel eyes with realistic catchlights and a faint holographic violet shimmer in the iris, fair porcelain skin with a translucent quality. The TOP of her head and forehead are partially transparent acrylic, revealing the intricate inner mechanism of her brain: glowing cyan and magenta circuit traces, fiber-optic strands, tiny LED nodes, and softly-pulsing hex-grid neural mesh visible beneath a polished glass dome — clean, elegant, sci-fi, not gore. Long platinum-silver hair pulled gently back at the temples revealing the transparent skull region; below the dome the rest of the face is smooth realistic synthetic skin. Slender neck shows faint glowing teal circuit lines tracing down toward the collarbone, where she wears the green Mexico national football team jersey (subtle, just the collar). Studio lighting: soft beauty dish from front-left, cool teal rim light from back-right, soft pinkish bounce from below. Pure neutral charcoal-to-graphite gradient background. Tight square 1:1 framing — only face, neck, and upper shoulders. Editorial sci-fi magazine quality, photoreal, NOT cartoon or 3D-rendered. Friendly, intelligent, warm — never menacing or uncanny. No text, no watermark, no logos.`;

const MODEL = process.env.CROMO_IMAGE_MODEL || "gemini-3-pro-image-preview";

console.log(`[ai-face] generating with ${MODEL}...`);
const resp = await ai.models.generateContent({
  model: MODEL,
  contents: [{ role: "user", parts: [{ text: PROMPT }] }],
});

const out = resp.candidates?.[0]?.content?.parts ?? [];
let saved = false;
for (const p of out) {
  const inline = p.inlineData;
  if (inline?.data && inline?.mimeType?.startsWith("image/")) {
    const buf = Buffer.from(inline.data, "base64");
    const dest = path.join(process.cwd(), "public", "players", "ai.jpg");
    await fs.writeFile(dest, buf);
    console.log(`[ai-face] wrote ${dest} (${buf.length} bytes, mime=${inline.mimeType})`);
    saved = true;
    break;
  }
}

if (!saved) {
  console.error("[ai-face] no image part in response", JSON.stringify(out, null, 2));
  process.exit(1);
}
