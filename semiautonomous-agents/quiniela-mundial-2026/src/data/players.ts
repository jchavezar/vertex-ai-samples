// 10 charales humanos + 1 bot ("AI"). Bolsa: 10 × $100 MXN = $1000 MXN al ganador.
// AI no entra al pozo — compite como benchmark con picks dinámicos basados en
// resultados reales (ver src/lib/elo-dynamic.ts).
export type Player = {
  id: string;
  name: string;
  emoji: string;
  accent: string;
  photoDataUrl?: string;
  defaultPhoto?: string;
  isBot?: boolean;
  // World Cup 2026 national teams this player roots for, in priority order.
  // The cromo generator rotates through this list day-by-day to pick the SOCCER
  // jersey shown in each cromo — keeps wardrobe always Mundial 2026 instead of
  // bleeding the NBA/NFL/polo from the reference photos. Default = ["Mexico"].
  favoriteTeams?: string[];
  // Cosmetic frame tier shown on the cromo card. Decoupled from rating on
  // purpose: with 10 friends in the same skill band every rating-derived tier
  // would be ORO · MAYAB. Per-player static "house" gives visual variety
  // between charales while rating still shows numerically. Players without
  // any picks at all get overridden to "debutante" at compute time.
  cromoTier?: import("@/lib/cromos").CromoTier;
};

export const AI_PLAYER_ID = "ai";

// Default favorites until the user tells me each player's real picks. Mexico
// home for everyone — anchors the wardrobe to Mundial 2026 from day one.
const MX = ["Mexico"];

export const PLAYERS: Player[] = [
  // cromoTier distribution: 1 especial (jesus, admin), 1 oroRaro (jochabe, "king" vibe),
  // 2 oro, 3 plata, 3 bronce — spreads the 10 charales across all 5 cosmetic
  // palettes so the album never looks monochrome.
  { id: "jesus",    name: "Jesús",    emoji: "🦅", accent: "#7C3AED", defaultPhoto: "/players/jesus.jpg",   favoriteTeams: ["France"], cromoTier: "especial" },
  { id: "jochabe",  name: "Jochabe",  emoji: "👑", accent: "#E11D48", defaultPhoto: "/players/jochabe.jpg", favoriteTeams: MX, cromoTier: "oroRaro"  },
  { id: "charal",   name: "Charal",   emoji: "🐺", accent: "#22C55E", defaultPhoto: "/players/charal.jpg",  favoriteTeams: MX, cromoTier: "oro"      },
  { id: "aldo",     name: "Aldo",     emoji: "🦁", accent: "#EAB308", defaultPhoto: "/players/aldo.jpg",    favoriteTeams: MX, cromoTier: "oro"      },
  { id: "tilapia",  name: "Tilapia",  emoji: "🐟", accent: "#14B8A6", defaultPhoto: "/players/tilapia.jpg", favoriteTeams: MX, cromoTier: "plata"    },
  { id: "mvictor",  name: "MVictor",  emoji: "🐂", accent: "#8B5CF6", defaultPhoto: "/players/mvictor.jpg", favoriteTeams: MX, cromoTier: "plata"    },
  { id: "xavi",     name: "Xavi",     emoji: "⚡", accent: "#0EA5E9", defaultPhoto: "/players/xavi.jpg",    favoriteTeams: MX, cromoTier: "plata"    },
  { id: "akyno",    name: "Akyno",    emoji: "🔥", accent: "#F97316", defaultPhoto: "/players/akyno.jpg",   favoriteTeams: MX, cromoTier: "bronce"   },
  { id: "darin",    name: "Darin",    emoji: "🌊", accent: "#06B6D4", defaultPhoto: "/players/darin.jpg",   favoriteTeams: MX, cromoTier: "bronce"   },
  { id: "emir",     name: "Emir",     emoji: "🦊", accent: "#D946EF", defaultPhoto: "/players/emir.jpg",    favoriteTeams: MX, cromoTier: "bronce"   },
  { id: AI_PLAYER_ID, name: "AI",     emoji: "🤖", accent: "#0F172A", isBot: true },
];

// Pick the team the player wears in their cromo for a given date. Deterministic
// rotation across favoriteTeams so the same date always produces the same kit
// (keeper cache stays valid). dateStr format: "YYYY-MM-DD".
export function teamForDay(playerId: string, dateStr: string): string {
  const p = PLAYERS.find(x => x.id === playerId);
  const list = (p?.favoriteTeams && p.favoriteTeams.length > 0) ? p.favoriteTeams : ["Mexico"];
  // Days-since-epoch index — stable, monotonic, no Date.now().
  const [y, m, d] = dateStr.split("-").map(n => parseInt(n, 10));
  const idx = Math.floor(Date.UTC(y, m - 1, d) / 86400000);
  return list[((idx % list.length) + list.length) % list.length];
}

export function isBot(playerId: string): boolean {
  return PLAYERS.find(p => p.id === playerId)?.isBot === true;
}

export const POT_TOTAL_MXN = 1000;
export const PER_PLAYER_MXN = 100;
