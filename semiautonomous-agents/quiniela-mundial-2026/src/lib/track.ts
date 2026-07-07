// Fire-and-forget client telemetry. Queue events in memory and flush via
// sendBeacon so the live app never blocks on network for analytics.

type TrackEvent = {
  event: string;
  props?: Record<string, unknown>;
  ts: number;
  path?: string;
  sessionId?: string;
};

const ENDPOINT = "/api/track";
const FLUSH_INTERVAL_MS = 8000;
const MAX_BATCH = 30;
const SESSION_KEY = "q26:track-session";

let queue: TrackEvent[] = [];
let timer: ReturnType<typeof setInterval> | null = null;
let installed = false;
let sessionStartedFired = false;

function isBrowser(): boolean {
  return typeof window !== "undefined";
}

function getSessionId(): string {
  if (!isBrowser()) return "";
  try {
    let sid = sessionStorage.getItem(SESSION_KEY);
    if (!sid) {
      // Avoid crypto.randomUUID() reliance: present in evergreen browsers but
      // missing on some older webviews. Fall back to time+rand if needed.
      sid =
        typeof crypto !== "undefined" && typeof crypto.randomUUID === "function"
          ? crypto.randomUUID()
          : `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 12)}`;
      sessionStorage.setItem(SESSION_KEY, sid);
    }
    return sid;
  } catch {
    return "";
  }
}

function currentPath(): string | undefined {
  if (!isBrowser()) return undefined;
  try {
    return window.location.pathname + window.location.search;
  } catch {
    return undefined;
  }
}

function flush(): void {
  if (!isBrowser()) return;
  if (queue.length === 0) return;
  const batch = queue.slice(0, MAX_BATCH);
  queue = queue.slice(batch.length);
  const body = JSON.stringify({ events: batch });
  try {
    if (typeof navigator !== "undefined" && typeof navigator.sendBeacon === "function") {
      const blob = new Blob([body], { type: "application/json" });
      const ok = navigator.sendBeacon(ENDPOINT, blob);
      if (ok) return;
    }
  } catch {}
  try {
    void fetch(ENDPOINT, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body,
      keepalive: true,
    }).catch(() => {});
  } catch {}
}

function install(): void {
  if (installed || !isBrowser()) return;
  installed = true;

  if (!sessionStartedFired) {
    sessionStartedFired = true;
    queue.push({
      event: "session_start",
      ts: Date.now(),
      path: currentPath(),
      sessionId: getSessionId(),
    });
  }

  timer = setInterval(flush, FLUSH_INTERVAL_MS);

  const onHidden = () => {
    if (document.visibilityState === "hidden") flush();
  };
  document.addEventListener("visibilitychange", onHidden);

  const onPageHide = () => {
    queue.push({
      event: "session_end",
      ts: Date.now(),
      path: currentPath(),
      sessionId: getSessionId(),
    });
    flush();
  };
  window.addEventListener("pagehide", onPageHide);
  window.addEventListener("beforeunload", () => {
    flush();
  });
  window.addEventListener("unload", () => {
    if (timer) clearInterval(timer);
    timer = null;
  });
}

export function track(event: string, props?: Record<string, unknown>): void {
  if (!isBrowser()) return;
  if (typeof event !== "string" || event.length === 0) return;
  install();
  queue.push({
    event: event.slice(0, 64),
    props,
    ts: Date.now(),
    path: currentPath(),
    sessionId: getSessionId(),
  });
  if (queue.length >= MAX_BATCH) flush();
}

export function trackPageView(path: string): void {
  if (!isBrowser()) return;
  install();
  queue.push({
    event: "page_view",
    props: { path },
    ts: Date.now(),
    path,
    sessionId: getSessionId(),
  });
}
