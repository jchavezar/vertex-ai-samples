"use client";

// FUT-style cromo, Mexico edition. Portrait pops out of the card on a sacred
// altar stage (spotlight cone + pyramid podium + Piedra-del-Sol disk). The
// photo uses a gradient mask so the body fades into the scene instead of
// being clipped flat.

import Image from "next/image";
import { Fragment, useEffect } from "react";
import { TEAMS, flagUrl } from "@/data/teams";
import { tierMeta, type Cromo, type TierTheme } from "@/lib/cromos";
import type { Player } from "@/data/players";
import { useCromoPortrait } from "@/lib/cromo-portrait";
import { track } from "@/lib/track";

const CROMO_VIEW_KEY = "q26:track-cromo-views";
function shouldTrackCromoView(playerId: string): boolean {
  if (typeof window === "undefined") return false;
  try {
    const raw = sessionStorage.getItem(CROMO_VIEW_KEY);
    const seen: string[] = raw ? JSON.parse(raw) : [];
    if (seen.includes(playerId)) return false;
    seen.push(playerId);
    sessionStorage.setItem(CROMO_VIEW_KEY, JSON.stringify(seen));
    return true;
  } catch {
    return false;
  }
}

type Props = {
  cromo: Cromo;
  player: Pick<Player, "id" | "name" | "emoji" | "accent" | "photoDataUrl" | "defaultPhoto">;
  size?: "sm" | "md" | "lg";
  className?: string;
  // When set, the cromo becomes clickable. Receives the currently-loaded
  // portrait URL (or null if it hasn't arrived yet) so the parent can open a
  // zoom modal without re-fetching.
  onClick?: (info: { portraitSrc: string | null; playerId: string }) => void;
};

const SIZE_PX = { sm: 220, md: 280, lg: 340 } as const;

export function CromoCard({ cromo, player, size = "md", className = "", onClick }: Props) {
  const w = SIZE_PX[size];
  const meta = tierMeta(cromo.tier);
  const aiPortrait = useCromoPortrait(player.id);
  useEffect(() => {
    if (shouldTrackCromoView(player.id)) track("cromo_view", { playerId: player.id });
  }, [player.id]);
  // HARD RULE: the cromo NEVER shows the raw `/players/{id}.jpg`. If the AI
  // portrait hasn't arrived yet, the `else` branch below renders a tier-tinted
  // shimmer placeholder. Falling back to defaultPhoto caused the kitchen-
  // background flicker bug; do not re-introduce it.
  const portraitSrc = aiPortrait;
  const championTeam = cromo.championPick ? TEAMS.find(t => t.code === cromo.championPick) : undefined;
  const left = cromo.statRows.slice(0, 3);
  const right = cromo.statRows.slice(3);
  const ratio = 1.45;
  const h = Math.round(w * ratio);
  const uid = `cromo-${cromo.playerId}-${size}`;

  // Portrait geometry — sized to pop out of the stage.
  // Vertical: head sits high so the rating numbers feel like they're behind it.
  const portraitW = Math.round(w * 0.78);
  const portraitH = Math.round(portraitW * 1.05);
  const portraitTop = Math.round(h * 0.08);

  const Wrapper = onClick ? "button" : "div";
  const wrapperProps = onClick
    ? {
        type: "button" as const,
        onClick: () => onClick({ portraitSrc, playerId: player.id }),
        "aria-label": `Ver cromo de ${player.name}`,
        className: `relative shrink-0 select-none cursor-pointer transition-transform hover:-translate-y-0.5 active:scale-[0.98] ${className}`,
      }
    : { className: `relative shrink-0 select-none ${className}` };

  return (
    <Wrapper
      {...wrapperProps}
      style={{ width: w, height: h, maxWidth: "100%" }}
    >
      <div
        className="relative w-full h-full rounded-[26px] overflow-hidden"
        style={{
          background: meta.gradient,
          color: meta.textColor,
          boxShadow: meta.glow
            ? `0 32px 70px -22px rgba(0,0,0,0.55), 0 0 0 1px ${meta.accent}aa, inset 0 0 0 1px ${meta.accent}77, 0 0 32px 2px ${meta.glow}44`
            : `0 32px 70px -22px rgba(0,0,0,0.55), 0 0 0 1px ${meta.accent}66, inset 0 0 0 1px ${meta.accent}55`,
        }}
      >
        {/* Layer 1 — serigrafia: altar, calendar, greca, glyphs (+ tier-specific overlays) */}
        <SerigrafiaLayer uid={uid} accent={meta.accent} textColor={meta.textColor} theme={meta.theme} />

        {/* Layer 1b — ORO RARO · TENOCHTITLAN: barrido de foil obsidiana/oro
            sobre toda la carta. Más denso y lento que el shine estándar. */}
        {meta.theme === "obsidiana" && (
          <div
            aria-hidden
            className="absolute inset-0 pointer-events-none mix-blend-soft-light opacity-90 cromo-foil"
            style={{
              background: "linear-gradient(110deg, transparent 5%, rgba(0,0,0,0.45) 30%, rgba(255,213,79,0.85) 48%, rgba(255,143,0,0.55) 55%, rgba(0,0,0,0.4) 70%, transparent 95%)",
              backgroundSize: "220% 100%",
            }}
          />
        )}

        {/* Layer 2 — holographic shine. Para ESPECIAL le agregamos el ciclo
            iridiscente de matiz para que el rayo de luz mute jade->oro->magenta. */}
        {meta.shine && (
          <div
            aria-hidden
            className={`absolute inset-0 pointer-events-none mix-blend-overlay cromo-shine ${meta.iridescent ? "cromo-iridescent opacity-75" : "opacity-60"}`}
            style={{
              background: meta.iridescent
                ? "linear-gradient(115deg, transparent 22%, rgba(29,233,182,0.55) 42%, rgba(255,235,130,0.75) 50%, rgba(194,24,91,0.55) 58%, transparent 78%)"
                : "linear-gradient(115deg, transparent 30%, rgba(255,255,255,0.55) 50%, transparent 70%)",
              backgroundSize: "200% 100%",
            }}
          />
        )}

        {/* Layer 3 — inner border ornament. Para premium usamos el accent y un poco más de presencia. */}
        <div
          aria-hidden
          className="absolute inset-[6px] rounded-[20px] pointer-events-none"
          style={{
            border: meta.premium
              ? `1px solid ${meta.accent}66`
              : `1px solid ${meta.textColor}22`,
            boxShadow: meta.premium ? `inset 0 0 12px ${meta.accent}33` : undefined,
          }}
        />

        {/* Layer 3b — ESPECIAL: anillo jade interior que late suavemente. */}
        {meta.theme === "quetzal" && meta.glow && (
          <div
            aria-hidden
            className="absolute inset-[3px] rounded-[22px] pointer-events-none cromo-especial-pulse"
            style={{
              boxShadow: `inset 0 0 0 1px ${meta.glow}88, inset 0 0 24px ${meta.glow}55`,
              mixBlendMode: "screen",
            }}
          />
        )}

        {/* ESPECIAL — aura solar girando lento detrás del retrato. Vive en su propio
            layer (z-5) para quedar entre la serigrafía y el portrait. */}
        {meta.theme === "quetzal" && (
          <div
            aria-hidden
            className="cromo-sun-halo z-[5]"
            style={{
              width: portraitW * 1.4,
              height: portraitW * 1.4,
              top: portraitTop + portraitH * 0.4,
              background: `conic-gradient(from 0deg, ${meta.accent}44, transparent 18%, ${meta.glow}33 38%, transparent 55%, ${meta.accent}33 75%, transparent 92%, ${meta.accent}44 100%)`,
              opacity: 0.55,
              filter: "blur(4px)",
            }}
          />
        )}

        {/* PORTRAIT STAGE — sits BEHIND the badges so the head appears to break the plane */}
        <div
          className="absolute left-1/2 -translate-x-1/2 z-10 pointer-events-none"
          style={{
            top: portraitTop,
            width: portraitW,
            height: portraitH,
          }}
        >
          {/* Stage spotlight cone (warm light spilling from above) */}
          <div
            aria-hidden
            className="absolute left-1/2 -translate-x-1/2"
            style={{
              top: "-8%",
              width: "120%",
              height: "85%",
              background: `radial-gradient(ellipse 55% 80% at 50% 5%, ${meta.accent}55 0%, ${meta.accent}22 35%, transparent 70%)`,
              filter: "blur(2px)",
            }}
          />
          {/* Ground halo / spotlight pool */}
          <div
            aria-hidden
            className="absolute left-1/2 -translate-x-1/2"
            style={{
              bottom: "-4%",
              width: "92%",
              height: "22%",
              background: `radial-gradient(ellipse 50% 60% at 50% 50%, ${meta.accent}88 0%, ${meta.accent}33 45%, transparent 80%)`,
              filter: "blur(6px)",
            }}
          />
          {/* Portrait image — full bleed with all-edge fade + tint overlay for immersion */}
          {portraitSrc ? (
            <div
              className="absolute inset-0"
              style={{
                filter: `drop-shadow(0 12px 18px rgba(0,0,0,0.55)) drop-shadow(0 0 10px ${meta.accent}66)`,
              }}
            >
              <div
                className="relative w-full h-full"
                style={{
                  WebkitMaskImage:
                    "radial-gradient(ellipse 78% 70% at 50% 38%, black 0%, black 38%, rgba(0,0,0,0.85) 55%, rgba(0,0,0,0.45) 75%, transparent 100%)",
                  maskImage:
                    "radial-gradient(ellipse 78% 70% at 50% 38%, black 0%, black 38%, rgba(0,0,0,0.85) 55%, rgba(0,0,0,0.45) 75%, transparent 100%)",
                }}
              >
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src={portraitSrc}
                  alt={player.name}
                  className="w-full h-full object-cover object-top"
                  style={{
                    WebkitMaskImage:
                      "linear-gradient(180deg, black 0%, black 68%, rgba(0,0,0,0.55) 86%, transparent 100%)",
                    maskImage:
                      "linear-gradient(180deg, black 0%, black 68%, rgba(0,0,0,0.55) 86%, transparent 100%)",
                  }}
                />
                {/* Tier-color tint that picks up at the edges (multiplies into the photo so corners take the card color) */}
                <div
                  aria-hidden
                  className="absolute inset-0 pointer-events-none mix-blend-multiply"
                  style={{
                    background: `radial-gradient(ellipse 65% 60% at 50% 40%, transparent 0%, transparent 45%, ${meta.accent}55 75%, ${meta.accent}cc 100%)`,
                  }}
                />
                {/* Soft color wash that lifts toward the tier gradient */}
                <div
                  aria-hidden
                  className="absolute inset-0 pointer-events-none mix-blend-soft-light opacity-70"
                  style={{
                    background: `radial-gradient(ellipse 75% 70% at 50% 40%, transparent 0%, transparent 50%, ${meta.accent} 100%)`,
                  }}
                />
              </div>
            </div>
          ) : (
            <div
              className="absolute inset-0 grid place-items-center cromo-portrait-skeleton"
              aria-label={`Generando cromo de ${player.name}`}
              role="img"
              style={{
                background: `radial-gradient(ellipse 80% 70% at 50% 40%, ${meta.accent}40 0%, ${meta.accent}1c 55%, transparent 100%)`,
                filter: `drop-shadow(0 12px 18px rgba(0,0,0,0.55))`,
              }}
            >
              <div
                className="rounded-full grid place-items-center"
                style={{
                  width: Math.round(portraitW * 0.55),
                  height: Math.round(portraitW * 0.55),
                  background: `radial-gradient(circle at 30% 30%, ${meta.accent}88, ${meta.accent}33 70%, transparent 100%)`,
                  color: meta.textColor,
                  fontSize: Math.round(portraitW * 0.34),
                  lineHeight: 1,
                }}
              >
                <span aria-hidden="true">{player.emoji}</span>
              </div>
            </div>
          )}
        </div>

        {/* HEADER STRIP — rating + position (left) and champion flag (right). z-30 so it sits IN FRONT of the portrait. */}
        <div
          className="absolute left-0 right-0 px-4 z-30 flex items-start justify-between pointer-events-none"
          style={{ top: Math.round(h * 0.04), height: Math.round(h * 0.16) }}
        >
          <div className="flex flex-col items-center leading-none">
            <div
              className="font-display font-black tabular-nums"
              style={{
                fontSize: Math.round(w * 0.17),
                color: meta.textColor,
                textShadow: `0 2px 6px rgba(0,0,0,0.55), 0 1px 0 ${meta.accent}aa`,
              }}
            >
              {cromo.tier === "debutante" ? "—" : cromo.rating}
            </div>
            <div
              className="font-display font-bold tracking-[0.2em] mt-0.5"
              style={{
                fontSize: Math.round(w * 0.055),
                color: meta.textColor,
                opacity: 0.95,
                textShadow: "0 1px 3px rgba(0,0,0,0.45)",
              }}
            >
              {cromo.position}
            </div>
            <div
              className="mt-1 h-[2px] rounded-full"
              style={{ width: Math.round(w * 0.1), background: meta.textColor, opacity: 0.6 }}
            />
          </div>

          {championTeam && (
            <div className="flex flex-col items-center gap-1">
              <div
                className="rounded-md overflow-hidden"
                style={{
                  width: Math.round(w * 0.14),
                  height: Math.round(w * 0.1),
                  boxShadow: `0 0 0 1px ${meta.accent}cc, 0 4px 10px rgba(0,0,0,0.55)`,
                }}
              >
                <Image
                  src={flagUrl(championTeam.iso2, 64)}
                  alt={championTeam.name}
                  width={64}
                  height={48}
                  className="w-full h-full object-cover"
                  unoptimized
                />
              </div>
              <div
                className="font-display font-bold tracking-[0.15em]"
                style={{
                  fontSize: Math.round(w * 0.044),
                  color: meta.textColor,
                  opacity: 0.95,
                  textShadow: "0 1px 3px rgba(0,0,0,0.45)",
                }}
              >
                {championTeam.code}
              </div>
            </div>
          )}
        </div>

        {/* NAME BANNER — full-width skewed ribbon */}
        <div
          className="absolute left-0 right-0 z-20"
          style={{ top: Math.round(h * 0.62) }}
        >
          <div
            className="relative mx-3 py-1.5 flex items-center justify-center"
            style={{
              background: `linear-gradient(90deg, transparent 0%, ${meta.textColor}33 15%, ${meta.textColor}55 50%, ${meta.textColor}33 85%, transparent 100%)`,
              borderTop: `1px solid ${meta.textColor}77`,
              borderBottom: `1px solid ${meta.textColor}77`,
              boxShadow: `inset 0 0 12px ${meta.accent}33`,
            }}
          >
            <div
              className="font-display font-black uppercase tracking-[0.18em] truncate px-3"
              style={{
                fontSize: Math.round(w * 0.078),
                color: meta.textColor,
                maxWidth: "92%",
                textShadow: "0 1px 2px rgba(0,0,0,0.35)",
              }}
            >
              {player.name}
            </div>
          </div>
        </div>

        {/* STATS GRID 3+3 con separador central */}
        <div
          className="absolute left-0 right-0 px-5 z-20"
          style={{ top: Math.round(h * 0.72) }}
        >
          <div className="relative grid grid-cols-2 gap-x-5 gap-y-0.5">
            <div
              aria-hidden
              className="absolute top-1 bottom-1 left-1/2 -translate-x-1/2 w-px"
              style={{ background: `${meta.textColor}44` }}
            />
            {left.map((lrow, i) => {
              const rrow = right[i];
              return (
                <Fragment key={lrow.key}>
                  <StatRow label={lrow.label} value={lrow.value} color={meta.textColor} fontSize={Math.round(w * 0.057)} align="right" />
                  {rrow && <StatRow label={rrow.label} value={rrow.value} color={meta.textColor} fontSize={Math.round(w * 0.057)} align="left" />}
                </Fragment>
              );
            })}
          </div>
        </div>

        {/* TIER FOOTER con dashes laterales */}
        <div
          className="absolute left-0 right-0 z-20 flex items-center justify-center gap-2 px-6"
          style={{ bottom: Math.round(h * 0.025) }}
        >
          <span className="flex-1 h-px" style={{ background: `${meta.textColor}55` }} />
          <span
            className="font-display font-bold tracking-[0.32em]"
            style={{ fontSize: Math.round(w * 0.04), color: meta.textColor, opacity: 0.85 }}
          >
            {meta.label}
          </span>
          <span className="flex-1 h-px" style={{ background: `${meta.textColor}55` }} />
        </div>
      </div>
    </Wrapper>
  );
}

function StatRow({
  label, value, color, fontSize, align,
}: { label: string; value: number; color: string; fontSize: number; align: "left" | "right" }) {
  return (
    <div className={`flex items-baseline gap-1 ${align === "right" ? "justify-end" : "justify-start"}`}>
      <span
        className="font-display font-black tabular-nums"
        style={{ fontSize, color, textShadow: "0 1px 2px rgba(0,0,0,0.3)" }}
      >
        {value}
      </span>
      <span
        className="font-display font-semibold tracking-[0.15em]"
        style={{ fontSize: fontSize * 0.68, color, opacity: 0.75 }}
      >
        {label}
      </span>
    </div>
  );
}

// Dense ceremonial serigrafía — Aztec altar, calendar rings, glyph border,
// pyramid podium, greca azteca, halftone, side feathers, corner ziggurats.
//
// Premium themes (obsidiana / quetzal) inject extra layers: obsidian shadow
// band + dual sun + denser greca for oroRaro; full quetzal feather wrap +
// plumed-serpent ring + iridescent inner frame + star burst particles for
// especial. The bronce/plata/oro variants keep the original layout intact.
function SerigrafiaLayer({
  uid, accent, textColor, theme,
}: {
  uid: string;
  accent: string;
  textColor: string;
  theme: TierTheme;
}) {
  const isObsidiana = theme === "obsidiana";
  const isQuetzal = theme === "quetzal";
  // 60-glyph outer ring (cardinal stops).
  const glyphRing = Array.from({ length: 60 }).map((_, i) => {
    const a = (i / 60) * Math.PI * 2;
    const r = 44;
    return { x: Math.cos(a) * r, y: Math.sin(a) * r, rot: (a * 180) / Math.PI };
  });
  // 12-block month/day ring (Aztec calendar inspired).
  const monthRing = Array.from({ length: 12 }).map((_, i) => {
    const a = (i / 12) * Math.PI * 2 - Math.PI / 2;
    const r = 36;
    return { x: Math.cos(a) * r, y: Math.sin(a) * r, deg: (a * 180) / Math.PI + 90, idx: i };
  });

  const grecaPath = "M0,3 L1,3 L1,2 L2,2 L2,1 L3,1 L3,0 L4,0 L4,1 L5,1 L5,2 L6,2 L6,3 L7,3";
  const pyramidPath = "M0,12 L4,12 L4,9 L8,9 L8,6 L12,6 L12,3 L16,3 L20,3 L20,6 L24,6 L24,9 L28,9 L28,12 L32,12 Z";
  const stepDiamond = "M0,2 L2,0 L4,2 L2,4 Z";

  return (
    <svg
      aria-hidden
      className="absolute inset-0 w-full h-full pointer-events-none"
      viewBox="0 0 100 145"
      preserveAspectRatio="none"
    >
      <defs>
        {/* Halftone dots */}
        <pattern id={`${uid}-dots`} x="0" y="0" width="2.4" height="2.4" patternUnits="userSpaceOnUse">
          <circle cx="1.2" cy="1.2" r="0.32" fill={textColor} opacity="0.28" />
        </pattern>
        {/* Microdot grid for stat zone */}
        <pattern id={`${uid}-microdots`} x="0" y="0" width="1.4" height="1.4" patternUnits="userSpaceOnUse">
          <circle cx="0.7" cy="0.7" r="0.18" fill={textColor} opacity="0.22" />
        </pattern>
        {/* Greca azteca */}
        <pattern id={`${uid}-greca`} x="0" y="0" width="7" height="3" patternUnits="userSpaceOnUse">
          <path d={grecaPath} fill="none" stroke={accent} strokeWidth="0.4" opacity="0.95" />
        </pattern>
        {/* Vertical greca (sides) */}
        <pattern id={`${uid}-greca-v`} x="0" y="0" width="3" height="7" patternUnits="userSpaceOnUse">
          <path d="M0,0 L0,1 L1,1 L1,2 L2,2 L2,3 L3,3 L3,4 L2,4 L2,5 L1,5 L1,6 L0,6 L0,7" fill="none" stroke={accent} strokeWidth="0.35" opacity="0.7" />
        </pattern>
        {/* Step diamonds */}
        <pattern id={`${uid}-diamonds`} x="0" y="0" width="6" height="6" patternUnits="userSpaceOnUse">
          <path d={stepDiamond} fill={accent} opacity="0.35" transform="translate(1,1)" />
        </pattern>
        {/* Quetzal feather */}
        <pattern id={`${uid}-feather`} x="0" y="0" width="3" height="5" patternUnits="userSpaceOnUse">
          <path d="M1.5,0 L2.8,2 L1.5,4 L0.2,2 Z" fill={accent} opacity="0.45" />
        </pattern>
        {/* Radial vignette mask centered on portrait */}
        <radialGradient id={`${uid}-vignette`} cx="50%" cy="35%" r="65%">
          <stop offset="0%" stopColor="white" stopOpacity="1" />
          <stop offset="55%" stopColor="white" stopOpacity="0.55" />
          <stop offset="100%" stopColor="white" stopOpacity="0" />
        </radialGradient>
        <mask id={`${uid}-vmask`}>
          <rect x="0" y="0" width="100" height="100" fill={`url(#${uid}-vignette)`} />
        </mask>

        {/* PIEDRA DEL SOL — full ceremonial disk */}
        <symbol id={`${uid}-sun`} viewBox="-50 -50 100 100">
          {/* Outer ring of 32 sharp rays */}
          {Array.from({ length: 32 }).map((_, i) => {
            const a = (i / 32) * Math.PI * 2;
            const innerR = 38, outerR = 49;
            const half = (Math.PI * 2) / 96;
            const x1 = Math.cos(a - half) * innerR;
            const y1 = Math.sin(a - half) * innerR;
            const x2 = Math.cos(a) * outerR;
            const y2 = Math.sin(a) * outerR;
            const x3 = Math.cos(a + half) * innerR;
            const y3 = Math.sin(a + half) * innerR;
            return <polygon key={i} points={`${x1},${y1} ${x2},${y2} ${x3},${y3}`} fill={accent} opacity="0.7" />;
          })}
          {/* Outer ring marks (60 glyphs) */}
          {glyphRing.map((g, i) => (
            <g key={i} transform={`translate(${g.x},${g.y}) rotate(${g.rot})`}>
              <rect x="-0.5" y="-0.5" width="1" height="1" fill={textColor} opacity="0.55" />
            </g>
          ))}
          {/* Concentric rings */}
          <circle cx="0" cy="0" r="36" fill="none" stroke={textColor} strokeWidth="0.6" opacity="0.55" />
          <circle cx="0" cy="0" r="32" fill="none" stroke={accent} strokeWidth="0.5" opacity="0.7" />
          <circle cx="0" cy="0" r="26" fill="none" stroke={textColor} strokeWidth="0.5" opacity="0.55" />
          <circle cx="0" cy="0" r="22" fill="none" stroke={accent} strokeWidth="0.4" opacity="0.6" />
          {/* 12-block calendar */}
          {monthRing.map((m, i) => (
            <g key={i} transform={`translate(${m.x},${m.y}) rotate(${m.deg})`}>
              <rect x="-3" y="-2.4" width="6" height="4.8" fill={textColor} opacity="0.35" />
              <rect x="-2.2" y="-1.6" width="4.4" height="3.2" fill={accent} opacity="0.65" />
              <rect x="-1.2" y="-0.8" width="2.4" height="1.6" fill={textColor} opacity="0.75" />
            </g>
          ))}
          {/* Inner cardinal eagle/jaguar marks */}
          {[0, 90, 180, 270].map(deg => (
            <g key={deg} transform={`rotate(${deg})`}>
              <polygon points="-3,-18 0,-13 3,-18 0,-23" fill={textColor} opacity="0.7" />
              <polygon points="-1.5,-19 0,-16 1.5,-19" fill={accent} opacity="0.95" />
            </g>
          ))}
          {/* Diagonal cardinal small glyphs */}
          {[45, 135, 225, 315].map(deg => (
            <g key={deg} transform={`rotate(${deg})`}>
              <rect x="-1.6" y="-18" width="3.2" height="1.2" fill={accent} opacity="0.75" />
              <rect x="-1.2" y="-16.4" width="2.4" height="1" fill={textColor} opacity="0.65" />
            </g>
          ))}
          {/* Tonatiuh face center */}
          <circle cx="0" cy="0" r="9" fill={accent} opacity="0.55" />
          <circle cx="0" cy="0" r="7" fill="none" stroke={textColor} strokeWidth="0.4" opacity="0.7" />
          <polygon points="-3,4 0,-2 3,4 1.5,7 -1.5,7" fill={textColor} opacity="0.75" />
          <circle cx="0" cy="-1" r="1.4" fill={accent} opacity="0.95" />
          <circle cx="-2.6" cy="-1" r="0.7" fill={textColor} opacity="0.85" />
          <circle cx="2.6" cy="-1" r="0.7" fill={textColor} opacity="0.85" />
        </symbol>

        {/* Quetzal feather symbol */}
        <symbol id={`${uid}-quetzal-feather`} viewBox="-10 -30 20 60">
          <path d="M0,-28 C-4,-18 -6,-6 -3,0 C-2,6 -4,14 0,22 C4,14 2,6 3,0 C6,-6 4,-18 0,-28 Z"
                fill={accent} opacity="0.65" stroke={textColor} strokeWidth="0.3" />
          <line x1="0" y1="-24" x2="0" y2="18" stroke={textColor} strokeWidth="0.3" opacity="0.55" />
          {Array.from({ length: 8 }).map((_, i) => {
            const y = -22 + i * 5;
            return <line key={i} x1="-2" y1={y} x2="2" y2={y + 1.4} stroke={textColor} strokeWidth="0.2" opacity="0.55" />;
          })}
        </symbol>

        {/* Corner ziggurat */}
        <symbol id={`${uid}-zig`} viewBox="0 0 12 12">
          <path d="M0,0 L4,0 L4,2 L2,2 L2,4 L0,4 Z" fill={accent} opacity="0.9" />
          <path d="M5,0 L8,0 L8,2 L6,2 Z" fill={accent} opacity="0.7" />
          <path d="M0,5 L2,5 L2,7 L0,7 Z" fill={accent} opacity="0.7" />
          <path d="M9,0 L11,0 L11,1.5 L9,1.5 Z" fill={accent} opacity="0.55" />
          <path d="M0,9 L1.5,9 L1.5,11 L0,11 Z" fill={accent} opacity="0.55" />
        </symbol>

        {/* PREMIUM — obsidian shadow band gradient (oroRaro) */}
        {isObsidiana && (
          <linearGradient id={`${uid}-obsidian`} x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#000" stopOpacity="0" />
            <stop offset="55%" stopColor="#1A0E00" stopOpacity="0.42" />
            <stop offset="100%" stopColor="#000" stopOpacity="0.62" />
          </linearGradient>
        )}

        {/* PREMIUM — iridescent jade->oro->magenta->morado gradient (especial) */}
        {isQuetzal && (
          <>
            <linearGradient id={`${uid}-iri`} x1="0" y1="0" x2="1" y2="1">
              <stop offset="0%" stopColor="#1DE9B6" />
              <stop offset="32%" stopColor="#FFD54F" />
              <stop offset="62%" stopColor="#C2185B" />
              <stop offset="100%" stopColor="#4A148C" />
            </linearGradient>
            <radialGradient id={`${uid}-jadeglow`} cx="50%" cy="40%" r="65%">
              <stop offset="0%" stopColor="#1DE9B6" stopOpacity="0.55" />
              <stop offset="45%" stopColor="#1DE9B6" stopOpacity="0.18" />
              <stop offset="100%" stopColor="#1DE9B6" stopOpacity="0" />
            </radialGradient>
          </>
        )}
      </defs>

      {/* Halftone field — full card */}
      <g mask={`url(#${uid}-vmask)`}>
        <rect x="0" y="0" width="100" height="100" fill={`url(#${uid}-dots)`} />
      </g>

      {/* Side vertical greca columns */}
      <rect x="0.5" y="14" width="3" height="60" fill={`url(#${uid}-greca-v)`} opacity="0.7" />
      <rect x="96.5" y="14" width="3" height="60" fill={`url(#${uid}-greca-v)`} opacity="0.7" />

      {/* PIEDRA DEL SOL — bigger, centered behind portrait */}
      <g transform="translate(50,52) scale(1.05)">
        <use href={`#${uid}-sun`} width="100" height="100" x="-50" y="-50" style={{ opacity: 0.75 }} />
      </g>

      {/* Auxiliary smaller calendar disk lower (mostly hidden behind name) */}
      <g transform="translate(50,98) scale(0.42)" style={{ opacity: 0.35 }}>
        <use href={`#${uid}-sun`} width="100" height="100" x="-50" y="-50" />
      </g>

      {/* Quetzal feathers ascending sides of portrait area */}
      <use href={`#${uid}-quetzal-feather`} x="-1" y="20" width="14" height="55" style={{ opacity: 0.55 }} />
      <use href={`#${uid}-quetzal-feather`} x="87" y="20" width="14" height="55" style={{ opacity: 0.55 }} />
      <use href={`#${uid}-quetzal-feather`} x="6" y="38" width="10" height="40" style={{ opacity: 0.4 }} />
      <use href={`#${uid}-quetzal-feather`} x="84" y="38" width="10" height="40" style={{ opacity: 0.4 }} />

      {/* Pyramid stage podium (sits behind the portrait base, partially showing) */}
      <g transform="translate(34,82)" fill={accent} opacity="0.42">
        <path d={pyramidPath} />
      </g>
      <g transform="translate(38,86)" fill={textColor} opacity="0.32">
        <path d="M0,9 L4,9 L4,6 L8,6 L8,3 L16,3 L20,3 L20,6 L24,6 L24,9 Z" />
      </g>
      <g transform="translate(42,90)" fill={accent} opacity="0.55">
        <path d="M0,5 L4,5 L4,2 L12,2 L16,2 L16,5 Z" />
      </g>

      {/* Stat zone — microdot field beneath the numbers */}
      <rect x="6" y="103" width="88" height="32" fill={`url(#${uid}-microdots)`} opacity="0.6" />

      {/* Greca bands above stats + above tier footer */}
      <rect x="0" y="100" width="100" height="3" fill={`url(#${uid}-greca)`} />
      <rect x="0" y="135" width="100" height="3" fill={`url(#${uid}-greca)`} opacity="0.7" />

      {/* Diamond mosaic strip on band */}
      <rect x="6" y="139" width="88" height="3" fill={`url(#${uid}-diamonds)`} opacity="0.6" />

      {/* Corner ziggurats */}
      <use href={`#${uid}-zig`} x="2" y="2" width="9" height="9" />
      <use href={`#${uid}-zig`} x="89" y="2" width="9" height="9" transform="translate(98 2) scale(-1 1) translate(-89 -2)" />
      <use href={`#${uid}-zig`} x="2" y="134" width="9" height="9" transform="translate(2 145) scale(1 -1) translate(-2 -134)" />
      <use href={`#${uid}-zig`} x="89" y="134" width="9" height="9" transform="translate(98 145) scale(-1 -1) translate(-89 -134)" />

      {/* Lateral mid diamonds */}
      <g fill={accent} opacity="0.85">
        <polygon points="1,72 3,69 5,72 3,75" />
        <polygon points="95,72 97,69 99,72 97,75" />
        <polygon points="1,58 3,55 5,58 3,61" opacity="0.55" />
        <polygon points="95,58 97,55 99,58 97,61" opacity="0.55" />
        <polygon points="1,86 3,83 5,86 3,89" opacity="0.55" />
        <polygon points="95,86 97,83 99,86 97,89" opacity="0.55" />
      </g>

      {/* Tiny floating glyphs around portrait (sparkle accents) */}
      <g fill={textColor} opacity="0.75">
        <polygon points="18,28 19,30 21,31 19,32 18,34 17,32 15,31 17,30" transform="scale(0.7) translate(8 8)" />
        <polygon points="80,30 81,32 83,33 81,34 80,36 79,34 77,33 79,32" transform="scale(0.7) translate(28 8)" />
        <polygon points="14,60 15,62 17,63 15,64 14,66 13,64 11,63 13,62" transform="scale(0.8) translate(2 -4)" />
      </g>

      {/* ============================================================ */}
      {/* ORO RARO · TENOCHTITLAN — capa obsidiana                     */}
      {/* ============================================================ */}
      {isObsidiana && (
        <g>
          {/* Banda obsidiana en mitad inferior — da profundidad y peso */}
          <rect x="0" y="60" width="100" height="85" fill={`url(#${uid}-obsidian)`} />
          {/* Marco interno punteado oro sobre obsidiana */}
          <rect x="3" y="3" width="94" height="139" rx="3" ry="3" fill="none"
            stroke={accent} strokeWidth="0.5" strokeDasharray="2.4 1.4" opacity="0.85" />
          {/* Sol secundario superior izquierda */}
          <g transform="translate(13,15) scale(0.16)">
            <use href={`#${uid}-sun`} width="100" height="100" x="-50" y="-50" style={{ opacity: 0.7 }} />
          </g>
          {/* Sol secundario superior derecha */}
          <g transform="translate(87,15) scale(0.16)">
            <use href={`#${uid}-sun`} width="100" height="100" x="-50" y="-50" style={{ opacity: 0.7 }} />
          </g>
          {/* Greca azteca densa adicional en la banda media */}
          <rect x="0" y="56" width="100" height="2" fill={`url(#${uid}-greca)`} opacity="0.85" />
          {/* Chispas de oro extra alrededor del retrato */}
          <g fill={accent} opacity="0.95">
            {[[24, 18], [76, 18], [12, 44], [88, 44], [26, 90], [74, 90]].map(([x, y], i) => (
              <polygon key={i}
                points="0,-1.6 0.5,-0.5 1.6,0 0.5,0.5 0,1.6 -0.5,0.5 -1.6,0 -0.5,-0.5"
                transform={`translate(${x},${y})`} />
            ))}
          </g>
        </g>
      )}

      {/* ============================================================ */}
      {/* ESPECIAL · QUETZAL — capa quetzal iridiscente                */}
      {/* ============================================================ */}
      {isQuetzal && (
        <g>
          {/* Aura jade detrás del retrato (refuerzo del halo CSS) */}
          <rect x="0" y="0" width="100" height="100" fill={`url(#${uid}-jadeglow)`} opacity="0.85" />

          {/* Marco interno iridiscente — jade → oro → magenta → morado */}
          <rect x="2.5" y="2.5" width="95" height="140" rx="3.5" ry="3.5" fill="none"
            stroke={`url(#${uid}-iri)`} strokeWidth="0.75" opacity="0.95" />
          <rect x="4" y="4" width="92" height="137" rx="2.5" ry="2.5" fill="none"
            stroke={accent} strokeWidth="0.25" strokeDasharray="0.6 1.2" opacity="0.7" />

          {/* Banda de plumas de quetzal en el borde superior */}
          {Array.from({ length: 11 }).map((_, i) => (
            <g key={`top-${i}`} transform={`translate(${9 + i * 8.2},7) rotate(180)`}>
              <use href={`#${uid}-quetzal-feather`} x="-3" y="-6" width="6" height="12"
                style={{ opacity: 0.6 }} />
            </g>
          ))}
          {/* Banda de plumas en el borde inferior */}
          {Array.from({ length: 11 }).map((_, i) => (
            <g key={`bot-${i}`} transform={`translate(${9 + i * 8.2},138)`}>
              <use href={`#${uid}-quetzal-feather`} x="-3" y="-6" width="6" height="12"
                style={{ opacity: 0.6 }} />
            </g>
          ))}

          {/* Anillo plumed-serpent rodeando el sol central */}
          <g transform="translate(50,52)">
            <circle r="46" fill="none" stroke={accent} strokeWidth="0.45"
              strokeDasharray="0.7 2.2" opacity="0.85" />
            <circle r="42" fill="none" stroke="#1DE9B6" strokeWidth="0.4"
              strokeDasharray="2 1.4" opacity="0.6" />
            <circle r="38" fill="none" stroke="#C2185B" strokeWidth="0.3"
              strokeDasharray="0.4 1.6" opacity="0.55" />
          </g>

          {/* Estrellas mexicanas (8 puntas) dispersas — efecto super card */}
          <g fill={accent} opacity="0.95">
            {[
              [16, 22], [84, 22], [12, 48], [88, 48],
              [50, 14], [22, 88], [78, 88], [50, 102],
            ].map(([x, y], i) => (
              <g key={i} transform={`translate(${x},${y})`}>
                <polygon
                  points="0,-2.6 0.9,-0.9 2.6,0 0.9,0.9 0,2.6 -0.9,0.9 -2.6,0 -0.9,-0.9"
                  opacity={0.85 - (i % 3) * 0.12}
                />
                <polygon
                  points="0,-1.2 0.4,-0.4 1.2,0 0.4,0.4 0,1.2 -0.4,0.4 -1.2,0 -0.4,-0.4"
                  fill={textColor}
                  opacity="0.9"
                />
              </g>
            ))}
          </g>

          {/* Pluma central grande detrás del nombre — el quetzal preside la carta */}
          <g transform="translate(50,118) scale(1.1)">
            <use href={`#${uid}-quetzal-feather`} x="-5" y="-15" width="10" height="30"
              style={{ opacity: 0.35 }} />
          </g>
        </g>
      )}
    </svg>
  );
}
