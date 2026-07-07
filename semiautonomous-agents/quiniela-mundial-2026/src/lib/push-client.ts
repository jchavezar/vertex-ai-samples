// Client helpers for Web Push: feature-detect, subscribe, unsubscribe, and
// keep the current PushSubscription in sync with the server. All functions
// no-op when push is unsupported so callers can call them blindly.

export function isPushSupported(): boolean {
  if (typeof window === "undefined") return false;
  return "serviceWorker" in navigator && "PushManager" in window && "Notification" in window;
}

export function currentPermission(): NotificationPermission | "unsupported" {
  if (!isPushSupported()) return "unsupported";
  return Notification.permission;
}

function urlBase64ToUint8Array(base64: string): Uint8Array {
  const padding = "=".repeat((4 - (base64.length % 4)) % 4);
  const b64 = (base64 + padding).replace(/-/g, "+").replace(/_/g, "/");
  const raw = atob(b64);
  const arr = new Uint8Array(raw.length);
  for (let i = 0; i < raw.length; i++) arr[i] = raw.charCodeAt(i);
  return arr;
}

async function getReg(): Promise<ServiceWorkerRegistration | null> {
  if (!("serviceWorker" in navigator)) return null;
  try {
    const reg = await navigator.serviceWorker.ready;
    return reg ?? null;
  } catch {
    return null;
  }
}

export async function getActiveSubscription(): Promise<PushSubscription | null> {
  const reg = await getReg();
  if (!reg) return null;
  try { return await reg.pushManager.getSubscription(); }
  catch { return null; }
}

export async function subscribeToPush(vapidPublicKey: string): Promise<{ ok: boolean; reason?: string }> {
  if (!isPushSupported()) return { ok: false, reason: "unsupported" };
  if (!vapidPublicKey) return { ok: false, reason: "no_vapid" };

  if (Notification.permission === "denied") return { ok: false, reason: "denied" };
  if (Notification.permission !== "granted") {
    const p = await Notification.requestPermission();
    if (p !== "granted") return { ok: false, reason: "denied" };
  }

  const reg = await getReg();
  if (!reg) return { ok: false, reason: "no_sw" };

  let sub: PushSubscription | null = null;
  try {
    sub = await reg.pushManager.getSubscription();
    if (!sub) {
      const keyBytes = urlBase64ToUint8Array(vapidPublicKey);
      sub = await reg.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: keyBytes.buffer.slice(keyBytes.byteOffset, keyBytes.byteOffset + keyBytes.byteLength) as ArrayBuffer,
      });
    }
  } catch (e) {
    console.error("[push] subscribe failed", e);
    return { ok: false, reason: "subscribe_failed" };
  }

  try {
    const r = await fetch("/api/push/subscribe", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ subscription: sub!.toJSON() }),
    });
    if (!r.ok) return { ok: false, reason: `server_${r.status}` };
    return { ok: true };
  } catch (e) {
    console.error("[push] subscribe POST failed", e);
    return { ok: false, reason: "server_unreachable" };
  }
}

export async function unsubscribeFromPush(): Promise<{ ok: boolean }> {
  const reg = await getReg();
  if (!reg) return { ok: true };
  const sub = await reg.pushManager.getSubscription().catch(() => null);
  if (!sub) return { ok: true };
  const endpoint = sub.endpoint;
  try { await sub.unsubscribe(); } catch {}
  try {
    await fetch("/api/push/unsubscribe", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ endpoint }),
    });
  } catch {}
  return { ok: true };
}
