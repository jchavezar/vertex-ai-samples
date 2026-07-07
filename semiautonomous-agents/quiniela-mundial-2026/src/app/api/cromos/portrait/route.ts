// Daily AI portrait for a player's cromo. Uses Gemini image model with the
// player's photo as input and a style that rotates day-to-day. Caches the
// result in Firestore keyed by {playerId}_{YYYY-MM-DD} so each player only
// regenerates once per day.

import { NextRequest } from "next/server";
import { GoogleGenAI } from "@google/genai";
import { Storage } from "@google-cloud/storage";
import { db } from "@/lib/firestore-server";
import { loadActiveBasePhoto, loadRefPhotos, type BasePhoto } from "@/lib/avatar-image";
import { PLAYER_IDENTITY } from "@/data/player-identity";
import { teamForDay } from "@/data/players";
import { readKeeper } from "@/lib/cromo-keepers";
import { getIdentityOverride } from "@/lib/identity-override";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const COLLECTION = "cromo_portraits";
const BUCKET = process.env.CROMO_BUCKET || "q26-cromo-portraits";

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

let _storage: Storage | null = null;
function getStorage(): Storage {
  if (!_storage) _storage = new Storage({ projectId: process.env.GOOGLE_CLOUD_PROJECT || "vtxdemos" });
  return _storage;
}

async function uploadToGcs(playerId: string, dateStr: string, dataUrl: string): Promise<string> {
  const match = /^data:([^;]+);base64,(.+)$/.exec(dataUrl);
  if (!match) throw new Error("invalid_data_url");
  const mime = match[1];
  const buf = Buffer.from(match[2], "base64");
  const ext = mime.split("/")[1] || "png";
  const objectName = `${playerId}/${dateStr}.${ext}`;
  const file = getStorage().bucket(BUCKET).file(objectName);
  await file.save(buf, {
    contentType: mime,
    // Short edge cache + must-revalidate so a regen propagates to every
    // friend's browser within seconds. The dataUrl already includes
    // `?v={createdAt}`, so identical URLs serve from cache (no extra cost),
    // while a re-roll produces a different URL that's never cached anywhere.
    metadata: { cacheControl: "public, max-age=60, must-revalidate" },
  });
  return `https://storage.googleapis.com/${BUCKET}/${objectName}`;
}

const STYLES = [
  { name: "ultimate-team", prompt: "FIFA Ultimate Team trading-card LIGHTING and BACKGROUND only: dramatic stadium-night lighting with deep crowd bokeh, gold rim light from one side, slight low angle, glossy magazine finish, transparent background not required, 1:1 aspect. CRITICAL: the subject is the SAME ordinary man from the reference photos — NOT an idealized footballer's headshot. Do NOT slim the face, do NOT sharpen the jaw, do NOT add an intense camera-ready model gaze, do NOT make him look like a celebrity football star. Frame slightly wider than a tight headshot (head + shoulders + a sliver of upper chest) so the face does not dominate the entire card." },
  { name: "lucha-libre",   prompt: "Mexican Lucha Libre cinematic POSTER styling around him: bold rojo y oro palette, halftone print background, Día de Muertos confetti, golden rim light. He is wearing a translucent silver lucha libre máscara that frames his face — eyes, nose, mouth FULLY visible through the mask cutouts." },
  { name: "manga-shonen",  prompt: "Anime shōnen sports manga PANEL styling AROUND him: dynamic ink lines, screen-tone halftone shading, dramatic speed lines behind the head, vibrant magenta and cobalt accents." },
  { name: "renaissance",   prompt: "Renaissance oil-painting styling around him in the manner of a Florentine master: soft chiaroscuro, warm earth tones, ornate gilded background with subtle Aztec greca motifs. Wearing a regal painted collar." },
  { name: "vaporwave",     prompt: "Vaporwave 80s neon styling around him: magenta and cyan rim light, retro pink-grid backdrop with palm-tree silhouettes, holographic chrome highlights, soft VHS scanlines." },
  { name: "comic-pop",     prompt: "Pop-art comic book PANEL styling AROUND him: Ben-Day dots, bold black outline, primary red-yellow-blue background with Mexican green accents, half-tone shading, exclamation bubble accent." },
  { name: "studio-watercolor", prompt: "Studio Ghibli-inspired WATERCOLOR styling AROUND him: soft gouache washes, gentle painterly background of a sunlit pitch at dawn." },
  { name: "azteca-codex",  prompt: "Pre-Hispanic Aztec codex styling AROUND him: amate-paper background with hand-painted glyphs, feathered serpent motifs, turquoise and cinnabar pigments, gold-leaf accents framing the head." },
  { name: "dia-muertos",   prompt: "Día de los Muertos altar styling AROUND him: orange marigold cempasúchil petals, papel picado banners, copal smoke, candle glow, painted sugar-skull motifs in the background. He has SUBTLE delicate black-and-white catrina face-paint outlining the eyes and a small floral motif on the cheek (paint only — NO skull mask, NO white-painted skull jaw)." },
  { name: "mariachi-noche",prompt: "Traditional Mexican mariachi styling: he wears a black charro suit with silver botonadura down the lapels and a wide-brimmed sombrero charro tipped back so his face stays fully visible. Background: warm Plaza Garibaldi night lighting, soft bokeh of papel-picado strings, golden trumpet glow." },
  { name: "cyberpunk-cdmx",prompt: "Cyberpunk Mexico City night styling AROUND him: neon Spanish-language signage reflected in rain, magenta and teal rim light, holographic Aztec greca glyphs floating in the background, distant Torre Latino silhouette." },
  { name: "mural-rivera",  prompt: "Diego Rivera mural styling AROUND him: bold flat color planes, earthy ochres and terracotta reds, monumental composition with workers and milpas in the background, fresco texture, faint plaster cracks." },
  { name: "loteria-card",  prompt: "Mexican Lotería card styling: thick black border like an antique lotería card, a banner along the bottom with ornamental scrollwork (no readable text), flat saturated colors, naive folk-illustration background of a stylized stadium with stars and clouds." },
  { name: "ukiyo-e",       prompt: "Japanese ukiyo-e woodblock-print styling AROUND him: flat color blocks, visible woodgrain, Hokusai-style wave pattern background, indigo and vermilion palette, decorative cloud bands." },
  { name: "art-deco",      prompt: "1920s Art Deco poster styling AROUND him: black and gold geometric sunburst background, fine gold linework, symmetrical fan and chevron motifs, cream-and-onyx palette." },
  { name: "pixel-art-16bit",prompt:"Retro 16-bit pixel-art trading card frame AROUND him: pixelated dithered background of a SNES-era stadium, chunky pixel border, limited-palette UI elements (HP bar, star icon, no readable text)." },
  { name: "low-poly-3d",   prompt: "Low-poly 3D geometric styling AROUND him: faceted triangulated background in teal and coral, abstract polygon shards floating in the air, soft studio lighting." },
  { name: "talavera-mosaic",prompt:"Mexican Talavera tile mosaic styling AROUND him: cobalt-blue, mustard-yellow and terracotta hand-painted tile patterns covering the background, intricate floral and geometric motifs, visible grout lines." },
  { name: "stained-glass", prompt: "Cathedral stained-glass styling AROUND him: leaded black outlines, jewel-toned panes (cobalt, ruby, emerald, amber), divine backlighting glow, geometric tracery." },
  { name: "sumi-e",        prompt: "Japanese sumi-e ink-wash styling AROUND him: minimal calligraphic brush strokes, washi-paper texture, a single red hanko stamp accent, restrained monochrome with one touch of cinnabar." },
  { name: "holographic-prizm",prompt:"Holographic prism trading-card styling: iridescent rainbow refraction effect on the card border, subtle prism light leaks across the surface, deep black background." },
  { name: "polaroid",      prompt: "Vintage Polaroid instant-photo styling: thick white Polaroid frame, slight warm color cast, soft film-grain, subtle light leak in one corner, casual hand-held angle." },
  { name: "newspaper-vintage",prompt:"Vintage newspaper front-page styling AROUND him: aged sepia newsprint texture, halftone dot screen, faux column layout with blurred unreadable text, prominent black-ink masthead element." },
  { name: "crayon-kids",   prompt: "Childlike crayon-on-construction-paper styling AROUND him: scribbled crayon-drawn stadium with green grass, a yellow sun in the corner, stick figures cheering, visible paper grain." },
  { name: "graffiti-mural",prompt: "Urban street-art mural styling AROUND him: spray-painted concrete wall background with bold tags, drip lines, vivid magenta and lime accents, stencil arrows." },
  { name: "bauhaus",       prompt: "Bauhaus geometric styling AROUND him: flat primary-color circles, squares and triangles in red, yellow and blue, clean black grid lines, off-white paper background." },
  { name: "retro-arcade-8bit",prompt:"Retro 8-bit arcade-game styling AROUND him: pixelated arcade-cabinet HUD elements, scanline overlay, chunky pixel border, high-score numerals (no real readable text), neon arcade palette." },
  { name: "stencil-banksy",prompt: "Stencil street-art styling AROUND him: high-contrast spray-painted stencil on concrete wall, a single accent color (vivid red), drip marks." },
  { name: "velvet-painting",prompt:"Kitsch black-velvet painting styling AROUND him: deep matte-black velvet background with a soft glowing tropical sunset, heavy paint impasto in the surrounding scene." },
  { name: "tarot-major",   prompt: "Mystical major-arcana tarot-card styling: ornate gold scroll border, deep midnight blue background with constellations and a crescent moon, alchemical symbols floating, decorative banner at the bottom with no readable text." },
  { name: "wpa-travel",    prompt: "1930s WPA travel-poster styling AROUND him: stylized flat-color background of an idealized stadium under a setting sun, screen-printed look, vintage cream-and-teal palette." },
  { name: "cubism",        prompt: "Cubist fractured-plane styling AROUND him: angular geometric shards in muted ochre, slate and rust palette in the background, overlapping faceted planes." },
  { name: "saturday-cartoon-90s",prompt:"90s Saturday-morning cartoon opening-title styling AROUND him: bold zig-zag shapes, splatter accents, vibrant teal and hot-pink palette, comic 'POW' starburst background." },
  { name: "neon-tube",     prompt: "Neon-tube sign styling AROUND him: glowing magenta and cyan neon tubes forming an abstract sport-themed sign behind him, dark brick wall background, soft glow halation." },
  { name: "embroidery-cross-stitch",prompt:"Cross-stitch embroidery styling AROUND him: visible aida-cloth weave background, stitched ornamental floral border in red-green-blue threads, simulated thread texture." },
  { name: "rotulista-mexico",prompt:"Mexican rotulista hand-painted sign styling AROUND him: vivid hand-lettered banner shapes (no readable text), saturated red-yellow-green palette, brush-stroke shadows, loncheria-stall vibe." },
  { name: "blueprint",     prompt: "Technical blueprint styling AROUND him: deep cyan-blue background with fine white grid lines, simulated dimension callouts and orthographic projection sketches of a stadium, drafting compass marks." },
  { name: "alebrije",      prompt: "Oaxacan alebrije folk-art styling AROUND him: brilliantly painted polka-dotted spirit creatures in fuchsia, lime and turquoise floating in the background, fine white dot patterns, intricate folk-art ornamentation." },
  { name: "papel-picado",  prompt: "Festive Mexican papel picado styling AROUND him: cascading rows of intricately cut tissue-paper banners in pink, orange, lime and turquoise across the top, soft party lights, terracotta plaza wall behind." },
  { name: "art-nouveau",   prompt: "Art Nouveau Alphonse Mucha styling AROUND him: ornate curving floral border, halo-like circular mandorla behind the head, muted pastel palette with gold accents, decorative typography frame (no readable text)." },
];

// AI bot cromo themes. These describe ONLY the costume + scene around the
// bot. The face/identity itself stays the canonical Ava-inspired android
// portrait that lives in `player_avatars/ai` (active profile photo). Each
// prompt must preserve the same translucent porcelain face + transparent
// circuit-brain dome — only the styling around her changes.
const AI_STYLES = [
  { name: "ai-ultimate-team", prompt: "FIFA Ultimate Team trading-card portrait styling: dramatic stadium-night lighting with verde-blanco-rojo bokeh, gold rim light, slight low angle, glossy magazine finish. Wearing the green Mexico national football team home jersey." },
  { name: "ai-lucha-libre", prompt: "Mexican Lucha Libre cinematic poster styling: bold rojo y oro palette, halftone print background, Día de Muertos confetti, golden rim light. She is wearing a glowing translucent silver lucha libre máscara that frames her face — eyes and mouth FULLY visible through the mask cutouts — over a Mexico-green jersey." },
  { name: "ai-manga-shonen", prompt: "Anime shōnen sports manga panel styling around her: dynamic ink lines, screen-tone halftone shading, dramatic speed lines behind the head, vibrant magenta and cobalt accents. Wearing the green Mexico jersey. Keep the face PHOTOREAL even though the background is illustrated." },
  { name: "ai-renaissance", prompt: "Renaissance oil-painting styling around her, in the style of a Florentine master: soft chiaroscuro, warm earth tones, ornate gilded background with subtle Aztec greca motifs. Wearing a regal collar painted in Mexico-green over the jersey. Keep the face PHOTOREAL even though the background is painterly." },
  { name: "ai-vaporwave", prompt: "Vaporwave 80s neon styling: magenta and cyan rim light, retro pink-grid backdrop with palm-tree silhouettes, holographic chrome highlights, soft VHS scanlines. Wearing the green Mexico jersey. Dreamy, confident." },
  { name: "ai-comic-pop", prompt: "Pop-art comic book panel styling around her: Ben-Day dots, bold black outline, primary red-yellow-blue background with Mexican green accents, half-tone shading. Wearing the green Mexico jersey. Keep the face PHOTOREAL even though the background is illustrated." },
  { name: "ai-cosmic-circuit", prompt: "Cinematic cosmic studio styling: dark cosmic gradient background (deep indigo to magenta) with floating soft binary digits and hexagonal HUD elements, faint Aztec greca line motifs in neon, cinematic studio lighting, gold rim light. Wearing the green Mexico jersey with subtle neural-net embroidery." },
  { name: "ai-azteca-codex",   prompt: "Pre-Hispanic Aztec codex styling AROUND her: amate-paper background with hand-painted glyphs, feathered serpent motifs, turquoise and cinnabar pigments, gold-leaf accents framing the head. Wearing the green Mexico jersey. Keep her bald silver hex-mesh skull and porcelain face fully visible — the codex art is only the border and background." },
  { name: "ai-dia-muertos",    prompt: "Día de los Muertos altar styling AROUND her: orange marigold cempasúchil petals, papel picado banners, copal smoke, candle glow, painted sugar-skull motifs in the background. Subtle delicate black-and-white catrina face-paint outlining the eyes (paint only — NO skull mask, NO white-painted skull jaw, NO covering the porcelain). Wearing the green Mexico jersey. Her bald hex-mesh skull and porcelain face stay fully visible." },
  { name: "ai-mariachi-noche", prompt: "Traditional Mexican mariachi styling: she wears a black charro jacket with silver botonadura over the green Mexico jersey collar; a wide-brimmed sombrero charro HOVERS beside her or rests on her shoulder (NEVER on her head — her bald hex-mesh skull MUST stay fully visible). Background: warm Plaza Garibaldi night lighting, soft bokeh of papel-picado strings, golden trumpet glow." },
  { name: "ai-cyberpunk-cdmx", prompt: "Cyberpunk Mexico City night styling AROUND her: neon Spanish-language signage reflected in rain, magenta and teal rim light, holographic Aztec greca glyphs floating in the background, distant Torre Latino silhouette. Wearing the green Mexico jersey. The cyberpunk scene is only background and lighting — her porcelain face and hex-mesh skull are untouched." },
  { name: "ai-mural-rivera",   prompt: "Diego Rivera mural styling AROUND her: bold flat color planes, earthy ochres and terracotta reds, monumental composition with workers and milpas in the background, fresco texture, faint plaster cracks. Wearing the green Mexico jersey. Keep the face PHOTOREAL — the mural is the surrounding scene only, the face is not flattened into mural style." },
  { name: "ai-loteria-card",   prompt: "Mexican Lotería card styling: thick black border like an antique lotería card, a banner along the bottom with ornamental scrollwork (no readable text), flat saturated colors, naive folk-illustration background of a stylized stadium with stars and clouds. Wearing the green Mexico jersey. Keep her porcelain android face PHOTOREAL — only the card frame and background are illustrated." },
  { name: "ai-ukiyo-e",        prompt: "Japanese ukiyo-e woodblock-print styling AROUND her: flat color blocks, visible woodgrain, Hokusai-style wave pattern background, indigo and vermilion palette, decorative cloud bands. Wearing the green Mexico jersey. Keep the face PHOTOREAL — only the background is woodblock." },
  { name: "ai-art-deco",       prompt: "1920s Art Deco poster styling AROUND her: black and gold geometric sunburst background, fine gold linework, symmetrical fan and chevron motifs, cream-and-onyx palette. Wearing the green Mexico jersey." },
  { name: "ai-pixel-art-16bit",prompt: "Retro 16-bit pixel-art trading card frame AROUND her: pixelated dithered background of a SNES-era stadium, chunky pixel border, limited-palette UI elements (HP bar, star icon, no readable text). Wearing the green Mexico jersey. Keep her porcelain face PHOTOREAL — only the frame, background and UI are pixelated." },
  { name: "ai-low-poly-3d",    prompt: "Low-poly 3D geometric styling AROUND her: faceted triangulated background in teal and coral, abstract polygon shards floating in the air, soft studio lighting. Wearing the green Mexico jersey. Keep her face PHOTOREAL — only the background and scattered shards are low-poly." },
  { name: "ai-talavera-mosaic",prompt: "Mexican Talavera tile mosaic styling AROUND her: cobalt-blue, mustard-yellow and terracotta hand-painted tile patterns covering the background, intricate floral and geometric motifs, visible grout lines. Wearing the green Mexico jersey. Keep the face PHOTOREAL — the tiles fill only the border and background." },
  { name: "ai-stained-glass",  prompt: "Cathedral stained-glass styling AROUND her: leaded black outlines, jewel-toned panes (cobalt, ruby, emerald, amber), divine backlighting glow, geometric tracery. Wearing the green Mexico jersey. Keep the face PHOTOREAL — only the surrounding panels are stained glass." },
  { name: "ai-sumi-e",         prompt: "Japanese sumi-e ink-wash styling AROUND her: minimal calligraphic brush strokes, washi-paper texture, a single red hanko stamp accent, restrained monochrome with one touch of cinnabar. Wearing the green Mexico jersey. Keep the face PHOTOREAL — only the surroundings are ink-wash." },
  { name: "ai-holographic-prizm",prompt:"Holographic prism trading-card styling: iridescent rainbow refraction effect on the card border, subtle prism light leaks across the surface, deep black background. Wearing the green Mexico jersey. Keep the face PHOTOREAL — the hologram is only on the card framing." },
  { name: "ai-polaroid",       prompt: "Vintage Polaroid instant-photo styling: thick white Polaroid frame, slight warm color cast, soft film-grain, subtle light leak in one corner, casual hand-held angle. Wearing the green Mexico jersey." },
  { name: "ai-newspaper-vintage",prompt:"Vintage newspaper front-page styling AROUND her: aged sepia newsprint texture, halftone dot screen, faux column layout with blurred unreadable text, prominent black-ink masthead element. Wearing the green Mexico jersey. Keep the face PHOTOREAL and in full color — the newspaper styling is only on the surrounding layout." },
  { name: "ai-crayon-kids",    prompt: "Childlike crayon-on-construction-paper styling AROUND her: scribbled crayon-drawn stadium with green grass, a yellow sun in the corner, stick figures cheering, visible paper grain. Wearing the green Mexico jersey. Keep the face PHOTOREAL — only the surrounding crayon drawing is childlike, she stays a real photograph pasted into the kid's drawing." },
  { name: "ai-graffiti-mural", prompt: "Urban street-art mural styling AROUND her: spray-painted concrete wall background with bold tags, drip lines, vivid magenta and lime accents, stencil arrows. Wearing the green Mexico jersey. Keep the face PHOTOREAL — the graffiti is on the wall behind her." },
  { name: "ai-bauhaus",        prompt: "Bauhaus geometric styling AROUND her: flat primary-color circles, squares and triangles in red, yellow and blue, clean black grid lines, off-white paper background. Wearing the green Mexico jersey." },
  { name: "ai-retro-arcade-8bit",prompt:"Retro 8-bit arcade-game styling AROUND her: pixelated arcade-cabinet HUD elements, scanline overlay, chunky pixel border, high-score numerals (no real readable text), neon arcade palette. Wearing the green Mexico jersey. Keep the face PHOTOREAL — only the frame and HUD are pixelated." },
  { name: "ai-stencil-banksy", prompt: "Stencil street-art styling AROUND her: high-contrast spray-painted stencil on concrete wall, a single accent color (vivid red), drip marks. Wearing the green Mexico jersey. Keep the face PHOTOREAL and in full color — only the wall and stencil graphics around her are monochrome stencil." },
  { name: "ai-velvet-painting",prompt: "Kitsch black-velvet painting styling AROUND her: deep matte-black velvet background with a soft glowing tropical sunset, heavy paint impasto in the surrounding scene. Wearing the green Mexico jersey. Keep the face PHOTOREAL — only the velvet background is painterly." },
  { name: "ai-tarot-major",    prompt: "Mystical major-arcana tarot-card styling: ornate gold scroll border, deep midnight blue background with constellations and a crescent moon, alchemical symbols floating, decorative banner at the bottom with no readable text. Wearing the green Mexico jersey." },
  { name: "ai-wpa-travel",     prompt: "1930s WPA travel-poster styling AROUND her: stylized flat-color background of an idealized stadium under a setting sun, screen-printed look, vintage cream-and-teal palette. Wearing the green Mexico jersey. Keep the face PHOTOREAL — only the surrounding poster art is screen-printed." },
  { name: "ai-cubism",         prompt: "Cubist fractured-plane styling AROUND her: angular geometric shards in muted ochre, slate and rust palette in the background, overlapping faceted planes. Wearing the green Mexico jersey. Keep the face PHOTOREAL — only the surrounding planes are cubist." },
  { name: "ai-saturday-cartoon-90s",prompt:"90s Saturday-morning cartoon opening-title styling AROUND her: bold zig-zag shapes, splatter accents, vibrant teal and hot-pink palette, comic 'POW' starburst background. Wearing the green Mexico jersey. Keep the face PHOTOREAL — only the background is cartoon." },
  { name: "ai-neon-tube",      prompt: "Neon-tube sign styling AROUND her: glowing magenta and cyan neon tubes forming an abstract sport-themed sign behind her, dark brick wall background, soft glow halation. Wearing the green Mexico jersey." },
  { name: "ai-embroidery-cross-stitch",prompt:"Cross-stitch embroidery styling AROUND her: visible aida-cloth weave background, stitched ornamental floral border in red-green-blue threads, simulated thread texture. Wearing the green Mexico jersey. Keep the face PHOTOREAL — only the surrounding border is embroidery." },
  { name: "ai-rotulista-mexico",prompt:"Mexican rotulista hand-painted sign styling AROUND her: vivid hand-lettered banner shapes (no readable text), saturated red-yellow-green palette, brush-stroke shadows, loncheria-stall vibe. Wearing the green Mexico jersey. Keep the face PHOTOREAL — only the surrounding sign is hand-painted." },
  { name: "ai-blueprint",      prompt: "Technical blueprint styling AROUND her: deep cyan-blue background with fine white grid lines, simulated dimension callouts and orthographic projection sketches of a stadium, drafting compass marks. Wearing the green Mexico jersey. Keep the face PHOTOREAL in full color — only the surrounding blueprint is monochrome." },
  { name: "ai-alebrije",       prompt: "Oaxacan alebrije folk-art styling AROUND her: brilliantly painted polka-dotted spirit creatures in fuchsia, lime and turquoise floating in the background, fine white dot patterns, intricate folk-art ornamentation. Wearing the green Mexico jersey. Keep the face PHOTOREAL — only the alebrije creatures and background are folk-art." },
  { name: "ai-papel-picado",   prompt: "Festive Mexican papel picado styling AROUND her: cascading rows of intricately cut tissue-paper banners in pink, orange, lime and turquoise across the top, soft party lights, terracotta plaza wall behind. Wearing the green Mexico jersey." },
  { name: "ai-art-nouveau",    prompt: "Art Nouveau Alphonse Mucha styling AROUND her: ornate curving floral border, halo-like circular mandorla behind the head, muted pastel palette with gold accents, decorative typography frame (no readable text). Wearing the green Mexico jersey. Keep the face PHOTOREAL — only the border and background are Art Nouveau." },
];

function dayKey(d = new Date()): string {
  // Rotate at midnight America/New_York so the "day" changes at ET midnight.
  const fmt = new Intl.DateTimeFormat("en-CA", {
    timeZone: "America/New_York",
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  });
  return fmt.format(d);
}

// Per-date theme overrides (human pool only). Wins over both the day-of-epoch
// rotation AND any client-side request. Add a row when the host of the day
// wants to pin a specific style.
const HUMAN_DATE_OVERRIDES: Record<string, number> = {
  "2026-06-12": 2,  // manga-shonen
  "2026-06-13": 1,  // lucha-libre
  "2026-06-15": 19, // sumi-e — pinned: today everyone must match Xavi/Darin
};

export function styleForDay(dateStr: string, override?: number, isAi = false) {
  const pool = isAi ? AI_STYLES : STYLES;
  if (typeof override === "number" && override >= 0 && override < pool.length) {
    return pool[override];
  }
  const pinned = HUMAN_DATE_OVERRIDES[dateStr];
  if (typeof pinned === "number" && pinned >= 0 && pinned < pool.length) {
    return pool[pinned];
  }
  // Day-of-epoch hash → stable per calendar day, rotates through styles
  const d = new Date(dateStr + "T00:00:00Z").getTime();
  const idx = Math.floor(d / 86400000) % pool.length;
  return pool[idx];
}

let _ai: GoogleGenAI | null = null;
function getClient(): GoogleGenAI {
  if (!_ai) {
    _ai = new GoogleGenAI({
      vertexai: true,
      project: process.env.GOOGLE_CLOUD_PROJECT || "vtxdemos",
      location: process.env.VERTEX_LOCATION || "global",
    });
  }
  return _ai;
}

export const PORTRAIT_STYLES = STYLES;
export const PORTRAIT_AI_STYLES = AI_STYLES;

export async function generatePortrait(
  playerId: string,
  dateStr: string,
  override?: number,
  extra?: string,
): Promise<{ dataUrl: string; style: string } | null> {
  const isAi = playerId === "ai";
  const ai = getClient();
  const extraNote = extra && extra.trim().length > 0
    ? ` Additional user direction: ${extra.trim()}.`
    : "";

  const style = styleForDay(dateStr, override, isAi);

  // Keeper short-circuit: if an admin ⭐'d a cromo for this {playerId, style}
  // in the workshop, that PNG IS the canonical answer. Skip the model entirely
  // (saves cost + drift) unless the caller provided custom direction in `extra`,
  // in which case they explicitly want a fresh variation.
  if (!isAi && (!extra || extra.trim().length === 0)) {
    const keeperBuf = await readKeeper(playerId, style.name);
    if (keeperBuf) {
      return {
        dataUrl: `data:image/png;base64,${keeperBuf.toString("base64")}`,
        style: style.name,
      };
    }
  }

  const parts: Array<{ inlineData?: { mimeType: string; data: string }; text?: string }> = [];

  // AI bot: usa SOLO foto activa (que ya es el render Ava canónico) — refs no aplican.
  // Humanos: usa el BANCO de fotos de identidad (base + /players/refs/{id}/*) para
  // que el modelo tenga múltiples ángulos del mismo rostro y preserve mejor la
  // cara. La foto activa del perfil se ignora para humanos: el cromo siempre
  // viene de fotos reales, no de un render encadenado.
  let photos: BasePhoto[];
  if (isAi) {
    const active = await loadActiveBasePhoto(playerId);
    photos = active ? [active] : [];
  } else {
    photos = await loadRefPhotos(playerId);
  }
  if (photos.length === 0) return null;

  // Firestore override wins over the hardcoded file entry so the workshop can
  // tweak identity lock live without redeploying. Null override → file fallback.
  const dbOverride = !isAi ? await getIdentityOverride(playerId).catch(() => null) : null;
  const identityFromMap = !isAi ? (dbOverride ?? PLAYER_IDENTITY[playerId]) : null;
  const identityClause = isAi
    ? "CRITICAL identity lock: the subject is Ava, the female humanoid robot from the 2014 film Ex Machina (Alicia Vikander). She is a WOMAN, never a man. She is BALD — ZERO hair anywhere on her head. The ENTIRE scalp from forehead down to the nape and around both ears is one continuous silver hexagonal honeycomb metal mesh cap (exactly as in the reference photo). NEVER add hair, fringe, bangs, ponytail or sideburns. Preserve the EXACT face from the reference photo: same gentle oval female face, same pale-blue-grey eyes, same fine pale eyebrows, same cool pale porcelain synthetic skin with subtle plastic sheen, same translucent panel seam on the right cheek, same temple panel above the ear, same continuous silver hex-mesh covering the whole head. ONLY the costume, accessories, lighting and scene styling around her may change — the face, gender, baldness, skull mesh, skin tone and cheek/temple panels stay identical to the reference. She must look clearly artificial, never human."
    : identityFromMap
      ? `${identityFromMap}`
      : `The reference photos all show the SAME real person. Preserve their actual face, smile, jawline, hairline, skin tone, ethnicity and build EXACTLY — do NOT beautify, slim, sharpen, age, or change ethnicity. Recognizable identity is more important than stylistic flourish.`;

  // Sandwich pattern: text intro → reference images → text styling instruction.
  // Putting refs at the END (just before the model generates) gives identity
  // the strongest recency-bias slot in the attention window. The opening
  // text primes the model to treat refs as ground truth, and the closing
  // text re-anchors identity AFTER the style request so style cannot drown
  // it out.
  if (!isAi) {
    parts.push({
      text: `You will receive ${photos.length} reference photo${photos.length > 1 ? "s" : ""} of the SAME real adult man. Study his face carefully. If any photo contains multiple people, the SUBJECT is the central adult male face — ignore women, children, crowds, and other faces. His face in the references is the GROUND TRUTH and overrides any stereotype, celebrity bias, or genre convention you might otherwise apply.`,
    });
  }
  for (const p of photos) {
    parts.push({ inlineData: { mimeType: p.mime, data: p.base64 } });
  }
  const closingText = isAi
    ? `Generate a portrait of the subject above, restyled as: ${style.prompt}.${extraNote} ${identityClause} Tight square 1:1 framing — only face, neck, and upper shoulders. NEVER show hands, fingers, arms, or anything below the shoulders. Sports trading-card composition. No text, no watermark.`
    : `Now generate a stylized portrait of THE EXACT SAME MAN shown in the reference photos above. The STYLING (lighting, background, color palette, art treatment, AND the face itself) should be FULLY rendered in this theme: ${style.prompt}.${extraNote} The FACE must be DRAWN / PAINTED / ILLUSTRATED in the theme's medium — not pasted in as a photograph. If the theme is sumi-e the face is sumi-e brush-strokes; if manga it's manga line-art; if alebrije it's folk-art paint; if oil-painting it's oil paint. The whole cromo reads as ONE coherent artwork in the chosen style. WARDROBE — MUNDIAL 2026: he is wearing the ${teamForDay(playerId, dateStr)} national football team soccer jersey for FIFA World Cup 2026 (contemporary international fútbol kit, national colors and crest), also rendered in the theme's style. IGNORE any clothing from the reference photos (Warriors / Niners / Pumas / DHL / hoodie / polo / etc) — replace with the Mundial soccer jersey. ANTI-PASSTHROUGH: do NOT return a reference photo with only a filter or border added — render a FRESH composition from scratch in the theme. Tight square 1:1 framing — only face, neck, and upper shoulders. POSTURE: natural upright, head squared to camera (NOT tilted, NOT leaning), shoulders straight and facing forward, never slumped or hunched. NEVER show hands, arms, or anything below the shoulders. No text, no watermark. ===  IDENTITY LOCK (preserve facial features WHILE stylizing) === The portrait must be UNMISTAKABLY the same specific man from the reference photos — keep the same nose shape, eye shape and spacing, lip shape, jawline, hairline, ear shape, facial proportions, beard/mustache pattern, eyeglasses if present, and characteristic smile/expression. ${identityClause} Render those features in the theme's art style (painted/illustrated/stylized) — do NOT default to a generic anime/cartoon/footballer face. If you find yourself drifting toward a 'handsome generic Mexican guy', a generic footballer, or any celebrity, STOP and look at the reference photos again — extract HIS specific features then re-render them in the theme. The point of this cromo is: recognizable identity AND fully stylized art, never a photo with a filter.`;
  parts.push({ text: closingText });

  try {
    const resp = await ai.models.generateContent({
      model: process.env.CROMO_IMAGE_MODEL || "gemini-3-pro-image-preview",
      contents: [{ role: "user", parts }],
    });
    const out = resp.candidates?.[0]?.content?.parts ?? [];
    for (const p of out) {
      const inline = (p as { inlineData?: { mimeType?: string; data?: string } }).inlineData;
      if (inline?.data && inline?.mimeType?.startsWith("image/")) {
        return { dataUrl: `data:${inline.mimeType};base64,${inline.data}`, style: style.name };
      }
    }
    return null;
  } catch (err) {
    console.error("[cromos/portrait] generate failed", err);
    return null;
  }
}

async function regenerate(
  playerId: string,
  styleOverride: number | undefined,
  extra: string | undefined,
  dateOverride?: string,
): Promise<Response> {
  const date = dateOverride && /^\d{4}-\d{2}-\d{2}$/.test(dateOverride) ? dateOverride : dayKey();
  const out = await generatePortrait(playerId, date, styleOverride, extra);
  if (!out) {
    return Response.json({ ok: false, reason: "generation_failed", date }, { status: 502 });
  }
  let publicUrl: string;
  try {
    publicUrl = await uploadToGcs(playerId, date, out.dataUrl);
  } catch (err) {
    console.error("[cromos/portrait] gcs upload failed", err);
    return Response.json({ ok: false, reason: "upload_failed", date }, { status: 502 });
  }
  const ref = db.collection(COLLECTION).doc(`${playerId}_${date}`);
  const createdAt = Date.now();
  await ref.set({
    playerId,
    date,
    style: out.style,
    url: publicUrl,
    note: extra ?? null,
    createdAt,
  });
  return Response.json({ ok: true, dataUrl: `${publicUrl}?v=${createdAt}`, style: out.style, cached: false, date });
}

export async function GET(req: NextRequest) {
  const { searchParams } = new URL(req.url);
  const playerId = searchParams.get("playerId");
  if (!playerId) return withCors(Response.json({ ok: false, error: "playerId required" }, { status: 400 }));
  const force = searchParams.get("force") === "1";
  // No public `style` override: the daily theme is shared by all players so
  // the deck is coherent (if today is lucha-libre, EVERY cromo is lucha-libre).
  // Admin POST is still allowed to pass an override for one-off regenerations.
  const date = dayKey();
  const docId = `${playerId}_${date}`;
  const ref = db.collection(COLLECTION).doc(docId);
  const isAi = playerId === "ai";

  if (!force) {
    const snap = await ref.get();
    if (snap.exists) {
      const data = snap.data() as { url?: string; style?: string; createdAt?: number };
      // The docId is {player}_{date}, so a new calendar day always generates a
      // fresh doc with the rotated style. Within a day we always serve the
      // cached cromo — no stale-on-avatar-update check, because that caused
      // every refresh to trigger a full regen whenever the player happened to
      // upload a profile photo today. The admin can still force a re-roll via
      // the workshop or POST.
      if (data?.url) {
        const v = data.createdAt ?? 0;
        const versioned = data.url.includes("?") ? data.url : `${data.url}?v=${v}`;
        return withCors(Response.json({ ok: true, dataUrl: versioned, style: data.style ?? null, cached: true, date }));
      }
    }
  }
  return withCors(await regenerate(playerId, undefined, undefined));
}

export async function POST(req: NextRequest) {
  // Two auth paths: (1) admin secret header (server-to-server / curl) OR
  // (2) cookie session for playerId "jesus" so the in-app admin album can
  // trigger regenerations without leaking the secret to the browser.
  const expected = process.env.ADMIN_SECRET;
  const headerOk = !!expected && req.headers.get("x-admin-secret") === expected;
  let cookieOk = false;
  if (!headerOk) {
    try {
      const { readAuth } = await import("@/lib/auth-server");
      const auth = await readAuth();
      cookieOk = auth?.playerId === "jesus";
    } catch { /* no cookie → forbidden */ }
  }
  if (!headerOk && !cookieOk) {
    return withCors(Response.json({ ok: false, error: "forbidden" }, { status: 403 }));
  }
  type Body = { playerId?: string; style?: number; prompt?: string; date?: string };
  let body: Body = {};
  try { body = (await req.json()) as Body; } catch {}
  if (!body.playerId) return withCors(Response.json({ ok: false, error: "playerId required" }, { status: 400 }));
  return withCors(await regenerate(body.playerId, body.style, body.prompt, body.date));
}
