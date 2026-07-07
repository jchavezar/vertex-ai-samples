export type ProfileOverride = {
  name?: string;
  emoji?: string;
  photoDataUrl?: string;
};

const KEY = "q26_profile_overrides";
const HYDRATED_KEY = "q26_profile_hydrated_at";
export const PROFILE_UPDATED_EVENT = "q26:profile-updated";

export function loadOverrides(): Record<string, ProfileOverride> {
  if (typeof window === "undefined") return {};
  try {
    const raw = localStorage.getItem(KEY);
    if (!raw) return {};
    const parsed = JSON.parse(raw);
    if (parsed && typeof parsed === "object") return parsed as Record<string, ProfileOverride>;
    return {};
  } catch {
    return {};
  }
}

function persist(all: Record<string, ProfileOverride>) {
  try {
    localStorage.setItem(KEY, JSON.stringify(all));
  } catch {}
  window.dispatchEvent(new CustomEvent(PROFILE_UPDATED_EVENT));
}

export function setOverride(playerId: string, patch: Partial<ProfileOverride>): void {
  if (typeof window === "undefined") return;
  const all = loadOverrides();
  const current = all[playerId] ?? {};
  const next: ProfileOverride = { ...current, ...patch };
  if (patch.photoDataUrl === "") delete next.photoDataUrl;
  if (patch.emoji === "") delete next.emoji;
  if (patch.name === "") delete next.name;
  all[playerId] = next;
  persist(all);
  // Push to server in background (best-effort). Requires PIN auth — server
  // will 401 if not logged in, which is fine (local cache still works).
  pushToServer(patch).catch(err => console.warn("[profile] server push failed:", err?.message ?? err));
}

export function clearOverride(playerId: string): void {
  if (typeof window === "undefined") return;
  const all = loadOverrides();
  if (!(playerId in all)) return;
  delete all[playerId];
  persist(all);
  // Server-side reset = send empty strings.
  pushToServer({ name: "", emoji: "", photoDataUrl: "" }).catch(() => {});
}

// === Server sync (Firestore) ===

async function pushToServer(patch: Partial<ProfileOverride>): Promise<void> {
  const res = await fetch("/api/profile", {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(patch),
  });
  if (!res.ok && res.status !== 401) {
    const text = await res.text().catch(() => "");
    throw new Error(`PUT /api/profile ${res.status}: ${text}`);
  }
}

// Hydrate localStorage from Firestore. Server is canonical for name/emoji/photo
// so a change on one device must appear on another quickly. Soft throttle to
// avoid spamming the server when callers fire repeatedly (mount, focus, etc).
export async function hydrateFromServer(force = false): Promise<void> {
  if (typeof window === "undefined") return;
  const last = Number(localStorage.getItem(HYDRATED_KEY) || "0");
  const MIN_INTERVAL = 5_000;
  if (!force && Date.now() - last < MIN_INTERVAL) return;
  try {
    const res = await fetch("/api/profiles", { cache: "no-store" });
    if (!res.ok) return;
    const body = await res.json();
    if (!body?.ok || !body.profiles) return;
    const local = loadOverrides();
    const remote = body.profiles as Record<string, { name?: string; emoji?: string; photoDataUrl?: string }>;
    let changed = false;
    for (const [pid, doc] of Object.entries(remote)) {
      const merged: ProfileOverride = {};
      if (doc.name)         merged.name = doc.name;
      if (doc.emoji)        merged.emoji = doc.emoji;
      if (doc.photoDataUrl) merged.photoDataUrl = doc.photoDataUrl;
      // Only overwrite if remote differs from local — avoids spurious events.
      if (JSON.stringify(local[pid] ?? {}) !== JSON.stringify(merged)) {
        local[pid] = merged;
        changed = true;
      }
    }
    localStorage.setItem(HYDRATED_KEY, String(Date.now()));
    if (changed) persist(local);
  } catch (e) {
    console.warn("[profile] hydrate failed:", (e as Error)?.message ?? e);
  }
}
