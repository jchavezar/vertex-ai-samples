/**
 * Rocket × Google Cloud Unified Single Source of Truth Portal
 * Apple iOS 26 / visionOS Liquid Glass + Black Mirror Spatial UI Controller (TypeScript)
 *
 * Implements:
 * 1. 4-Version Spatial Liquid Glass Material Switcher (V1 Daylight Prism, V2 Black Mirror Obsidian,
 *    V3 Spatial Titanium 3D, V4 Ryan Holiday Stillness Monolith)
 * 2. 3D Specular Refraction & Perspective Card Physics (--rx, --ry, --glare-x, --glare-y)
 * 3. Real Photorealistic Gemini 3.8 Live Video Avatar (`window.RocketLive` over `/ws/live-avatar`)
 *    + Omniscient Portal Screen Co-Pilot (`/api/portal-copilot` + `/ws/live-tts`)
 * 4. 4-Tier Homogenized Navigation (`studios`, `build`, `glossary`, `archive`)
 */

export type LiquidVersionId = 'v1' | 'v2' | 'v3' | 'v4';
export type PortalTabId = 'studios' | 'build' | 'glossary' | 'archive';

export interface AvatarProfile {
  key: string;
  name: string;
  role: string;
  voice: string;
  posterUrl: string;
  hasOfficialVideo: boolean;
}

export interface ScreenAction {
  name: 'navigate_portal_tab' | 'search_glossary_or_translator' | 'filter_reference_library';
  args: Record<string, string>;
}

export interface CopilotResponse {
  ok: boolean;
  model: string;
  avatar: string;
  latency_ms: number;
  answer: string;
  screen_action?: ScreenAction | null;
}

declare global {
  interface Window {
    RocketLive?: {
      start: (opts: Record<string, unknown>) => Promise<void>;
      stop: () => void;
      interrupt: () => void;
      sendText: (text: string) => Promise<void>;
      isActive: () => boolean;
      getState: () => string;
      getOutputLevel: () => number;
      on: (evt: string, fn: (detail: any) => void) => () => void;
    };
    PORTAL_AUTH_TOKEN?: string;
    switchPortalTab: (tabId: PortalTabId, highlightId?: string) => void;
    setLiquidVersion: (ver: LiquidVersionId) => void;
    cycleLiquidVersion: () => void;
    toggleVersionPopover: (ev?: MouseEvent) => void;
    closeVersionPopover: () => void;
    selectPortalAvatar: (key: string) => void;
    togglePortalLiveAvatar: () => void;
    interruptPortalAvatar: () => void;
    askPortalCopilot: (promptText?: string) => Promise<void>;
    speakPortalText: (text: string, btnEl?: HTMLElement | null) => void;
    filterGlossaryView: (query?: string, vendorTag?: string) => void;
    filterArchiveBlueprints: (deptOrQuery?: string) => void;
    openDiagramLightbox: (src: string, title: string) => void;
    closeDiagramLightbox: () => void;
    copyTextSnippet: (text: string, btnEl?: HTMLElement | null) => void;
  }
}

export const AVATAR_ROSTER: Record<string, AvatarProfile> = {
  Kira: {
    key: 'Kira',
    name: 'Kira',
    role: 'Principal AI Portal Concierge',
    voice: 'Aoede',
    posterUrl: '/static/official_kira_38_full.jpg',
    hasOfficialVideo: true,
  },
  Sam: {
    key: 'Sam',
    name: 'Sam',
    role: 'Cloud & GECX Solutions Architect',
    voice: 'Puck',
    posterUrl: '/static/official_sam_38_full.jpg',
    hasOfficialVideo: true,
  },
  Ben: {
    key: 'Ben',
    name: 'Ben',
    role: 'BigQuery TimesFM & Vector Lead',
    voice: 'Fenrir',
    posterUrl: '/static/official_ben_38_full.jpg',
    hasOfficialVideo: true,
  },
  Vera: {
    key: 'Vera',
    name: 'Vera',
    role: 'Redfin & Veo 3.1 Creative Director',
    voice: 'Kore',
    posterUrl: '/static/official_vera_38_full.jpg',
    hasOfficialVideo: true,
  },
  Leo: {
    key: 'Leo',
    name: 'Leo',
    role: 'Mr. Cooper Servicing & Security Lead',
    voice: 'Charon',
    posterUrl: '/static/official_leo_38_full.jpg',
    hasOfficialVideo: true,
  },
  Jesus: {
    key: 'Jesus',
    name: 'Jesus',
    role: 'Lead Architect (2D Portrait Audio)',
    voice: 'Puck',
    posterUrl: '/static/jesus_idle_closed.jpg',
    hasOfficialVideo: false,
  },
};
