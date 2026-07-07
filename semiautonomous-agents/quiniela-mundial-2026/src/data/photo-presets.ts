// Style presets for the self-service photo studio at /perfil/foto.
// Each preset is a complete style direction. The identity guardrail lives
// once in src/lib/avatar-image.ts (IDENTITY_GUARDRAIL) and is appended
// automatically — DO NOT repeat it here.

export type PhotoPreset = {
  id: string;
  label: string;
  icon: string;       // single emoji for chip
  blurb: string;      // 4-6 words shown under chip
  prompt: string;     // style direction (no identity guardrail)
};

export const PHOTO_PRESETS: PhotoPreset[] = [
  {
    id: "mexico-stadium",
    label: "México estadio",
    icon: "🇲🇽",
    blurb: "Jersey verde 2026, noche de gala",
    prompt: "Wearing the official adidas Mexico national football team home jersey for FIFA World Cup 2026: deep vibrant verde (green) base with bold Aztec geometric patterns — sharply reimagined stepped greca motifs inspired by ancient Mesoamerican temple reliefs — rendered as intricate interlocking linework covering the chest and shoulders, adidas three-stripe sleeves in white, official FMF eagle crest embroidered on the left chest, subtle 'SOMOS MÉXICO' inscribed inside the collar. Dramatic Estadio Azteca night background, green-white-red bokeh confetti, golden rim light from the side, cinematic stadium hero portrait, head and shoulders, proud confident pose, crisp FIFA championship-photo finish",
  },
  {
    id: "manga-shonen",
    label: "Manga shōnen",
    icon: "⚡",
    blurb: "Anime intenso 90s",
    prompt: "High-energy shōnen manga illustration of the person, dynamic anime line art, vibrant cel-shaded colors with crisp black ink linework, speed lines and motion energy radiating from behind, expressive determined eyes with sparkle, dramatic spiky-hair shading, Mexico-green jacket with subtle aztec patches, halftone screentone background in magenta-violet, head and shoulders 1:1 framing, looks like a tournament-arc cover panel",
  },
  {
    id: "pixar-3d",
    label: "Pixar 3D",
    icon: "🎬",
    blurb: "Personaje animado familiar",
    prompt: "Charming Pixar/DreamWorks style 3D animated character portrait of the person, soft cinematic studio lighting, warm friendly expression, slightly stylized large eyes with reflections, smooth subsurface-scattering skin, simplified but recognizable features, wearing a casual green Mexico fan jersey, blurred warm-toned playful background, head and shoulders 1:1 framing, movie poster finish",
  },
  {
    id: "lucha-libre",
    label: "Lucha libre",
    icon: "🤼",
    blurb: "Máscara, gloria mexicana",
    prompt: "Heroic mexican lucha libre portrait of the person wearing a vibrant intricate luchador mask (silver, gold and emerald-green with aztec patterns and red accents), shirtless or sleeveless showing championship belt strap, dramatic spotlight from above, smoke and confetti, arena ropes blurred in background, head and shoulders, hero pose, vintage wrestling-poster finish",
  },
  {
    id: "vaporwave",
    label: "Vaporwave",
    icon: "🌴",
    blurb: "Neón 80s, palmeras",
    prompt: "Synthwave/vaporwave aesthetic portrait of the person, magenta-cyan-purple neon gradient lighting on the face, retro 80s grid horizon and palm tree silhouettes behind, chrome and glassy reflections, light glitch artifacts, wearing a colorful pastel windbreaker with abstract aztec geometric patterns, head and shoulders, dreamlike retrofuturist finish",
  },
  {
    id: "renaissance",
    label: "Retrato clásico",
    icon: "🖼️",
    blurb: "Óleo renacentista",
    prompt: "Classical Renaissance oil-painting portrait of the person in the style of a 16th-century master (think Bronzino or Velázquez), warm chiaroscuro lighting from a single window, rich burgundy and forest-green velvet garments with delicate embroidery, ornate gold-trimmed collar, soft cracked-varnish texture, dark muted backdrop, head and shoulders, gallery-museum finish",
  },
  {
    id: "cyberpunk",
    label: "Cyberpunk",
    icon: "🤖",
    blurb: "Neón, lluvia, futuro",
    prompt: "Cinematic cyberpunk portrait of the person, neon-soaked rainy night city background with kanji and aztec-glyph holograms, magenta-cyan-violet rim lighting, sleek high-tech jacket with luminous green circuitry trim and a small Mexico flag patch, subtle wet-skin highlights, head and shoulders, Blade-Runner-poster finish",
  },
  {
    id: "comic-pop",
    label: "Cómic pop-art",
    icon: "💥",
    blurb: "Tinta, Ben-Day dots",
    prompt: "Bold pop-art comic-book panel of the person, thick black ink outlines, vibrant flat primary colors (red, yellow, green), classic Ben-Day halftone dots, dynamic action lines, a small speech bubble exclaiming 'GOOOL!' in stylized lettering, vintage Roy-Lichtenstein-meets-Marvel finish, head and shoulders 1:1 framing",
  },
  {
    id: "acuarela",
    label: "Acuarela",
    icon: "🎨",
    blurb: "Pintura suave hecha a mano",
    prompt: "Soft hand-painted watercolor portrait of the person, gentle washes of green-teal-ochre, visible brush strokes and paper texture, loose ink-line accents around the edges, a faint Mexican folk art floral motif in the background corner, head and shoulders, art-print finish",
  },
  {
    id: "studio-portrait",
    label: "Foto profesional",
    icon: "📸",
    blurb: "Estudio limpio, alta calidad",
    prompt: "Clean professional studio portrait of the person, soft three-point lighting with a slight warm fill, neutral charcoal-to-cream gradient backdrop, subtle catchlights in the eyes, sharp focus, wearing a smart casual outfit in muted earth tones, relaxed confident expression, head and shoulders 1:1 framing, magazine-cover finish",
  },
];

export function getPreset(id: string | null | undefined): PhotoPreset | null {
  if (!id) return null;
  return PHOTO_PRESETS.find(p => p.id === id) ?? null;
}
