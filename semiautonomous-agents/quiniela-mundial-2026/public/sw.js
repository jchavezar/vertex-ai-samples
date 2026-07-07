const CACHE = "q26-v8";
const SNAPSHOT_CACHE = "q26-snapshot-v8";

// Endpoints we want to hot-cache: the BFF snapshot + scoreboard. Subsequent
// visits hit the SW cache first, then revalidate in the background. The
// snapshot endpoint already collapses 5 separate fetches into 1 — caching it
// here turns warm-tab reloads into instant paints.
const SNAPSHOT_URLS = ["/api/home/snapshot", "/api/scoreboard"];

self.addEventListener("install", (e) => {
  self.skipWaiting();
  e.waitUntil((async () => {
    const c = await caches.open(CACHE);
    await c.addAll(["/"]);
    // Pre-warm the BFF cache so the first paint of a fresh install has
    // something to serve before the network round-trip completes.
    try {
      const snap = await caches.open(SNAPSHOT_CACHE);
      await Promise.all(
        SNAPSHOT_URLS.map(async (u) => {
          try {
            const res = await fetch(u, { cache: "no-store" });
            if (res && res.ok) await snap.put(u, res.clone());
          } catch (_) { /* offline at install — fine */ }
        }),
      );
    } catch (_) {}
  })());
});

self.addEventListener("activate", (e) => {
  e.waitUntil((async () => {
    const keys = await caches.keys();
    await Promise.all(
      keys
        .filter((k) => k !== CACHE && k !== SNAPSHOT_CACHE)
        .map((k) => caches.delete(k)),
    );
    await self.clients.claim();
    // Tell every controlled tab to reload itself so users on stale HTML
    // immediately pick up the new bundle without manual refresh. Critical for
    // mobile, where the SW happily serves cached pages on weak networks.
    const all = await self.clients.matchAll({ type: "window", includeUncontrolled: true });
    for (const c of all) {
      try { c.postMessage({ type: "q26-sw-updated", cache: CACHE }); } catch (_) {}
    }
  })());
});

function isSnapshotRequest(url) {
  return SNAPSHOT_URLS.some((u) => url.pathname === u || url.pathname.startsWith(u + "?"));
}

self.addEventListener("fetch", (e) => {
  const { request } = e;
  if (request.method !== "GET") return;
  const url = new URL(request.url);
  if (url.origin !== self.location.origin) return;

  // Stale-while-revalidate for the snapshot endpoints — serve cached
  // immediately (sub-millisecond), then refresh in the background so the next
  // paint already has fresh data. This is what makes warm-tab reloads feel
  // instant even though the live cadence is still 8-15s on the network.
  if (isSnapshotRequest(url)) {
    e.respondWith((async () => {
      const snap = await caches.open(SNAPSHOT_CACHE);
      const cached = await snap.match(request, { ignoreSearch: false });
      const fetchPromise = fetch(request)
        .then((res) => {
          if (res && res.ok) snap.put(request, res.clone()).catch(() => {});
          return res;
        })
        .catch(() => cached || new Response("offline", { status: 503 }));
      return cached || fetchPromise;
    })());
    return;
  }

  if (url.pathname.startsWith("/api/") || url.pathname.startsWith("/_next/data")) return;

  e.respondWith(
    fetch(request)
      .then((res) => {
        const copy = res.clone();
        caches.open(CACHE).then((c) => c.put(request, copy)).catch(() => {});
        return res;
      })
      .catch(() => caches.match(request).then((r) => r || caches.match("/")))
  );
});

// Web Push: muestra una notificación nativa al recibir un payload de VAPID.
// Espera { title, body, url?, tag?, icon?, badge? } como JSON.
self.addEventListener("push", (e) => {
  let payload = {};
  try { payload = e.data ? e.data.json() : {}; } catch (_) {}
  const title = payload.title || "Charales 2026";
  const opts = {
    body: payload.body || "",
    icon: payload.icon || "/icon-192.png",
    badge: payload.badge || "/icon-192.png",
    tag: payload.tag || "q26",
    renotify: !!payload.tag,
    data: { url: payload.url || "/" },
  };
  e.waitUntil(self.registration.showNotification(title, opts));
});

// ── Background Sync: offline pick queue ──────────────────────────────────────
// When POST /api/picks fails due to no network, the client enqueues the pick
// in IndexedDB and registers a sync tag. The OS wakes us here once online.
// Feature-detected: no-ops on Safari/iOS which don't support Background Sync.

const _BG_STORE = "q26-bg-picks";

function _bgOpenDB() {
  return new Promise((resolve, reject) => {
    const req = indexedDB.open("q26-offline", 1);
    req.onupgradeneeded = (e) => {
      e.target.result.createObjectStore(_BG_STORE, { keyPath: "fixtureId" });
    };
    req.onsuccess = (e) => resolve(e.target.result);
    req.onerror = () => reject(req.error);
  });
}

async function _flushPickQueue() {
  let db;
  try { db = await _bgOpenDB(); } catch (_) { return; }
  const picks = await new Promise((resolve, reject) => {
    const tx = db.transaction(_BG_STORE, "readonly");
    const req = tx.objectStore(_BG_STORE).getAll();
    req.onsuccess = () => resolve(req.result);
    req.onerror = () => reject(req.error);
  });
  for (const item of picks) {
    try {
      const r = await fetch("/api/picks", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ fixtureId: item.fixtureId, pick: item.pick }),
        keepalive: true,
      });
      const j = await r.json();
      if (j.ok || j.error === "locked") {
        // Confirmed or too late — remove from queue either way
        const tx2 = db.transaction(_BG_STORE, "readwrite");
        tx2.objectStore(_BG_STORE).delete(item.fixtureId);
      }
      // 401 / 5xx: leave in queue, next sync will retry
    } catch (_) {
      // Still offline — leave in queue
    }
  }
}

self.addEventListener("sync", (e) => {
  if (e.tag === "q26-pick-queue") {
    e.waitUntil(_flushPickQueue());
  }
});

self.addEventListener("notificationclick", (e) => {
  e.notification.close();
  const target = (e.notification.data && e.notification.data.url) || "/";
  e.waitUntil((async () => {
    const all = await self.clients.matchAll({ type: "window", includeUncontrolled: true });
    for (const c of all) {
      try {
        const u = new URL(c.url);
        if (u.origin === self.location.origin) {
          c.focus();
          if (target && target !== "/") {
            c.navigate(target).catch(() => {});
          }
          return;
        }
      } catch (_) {}
    }
    if (self.clients.openWindow) await self.clients.openWindow(target);
  })());
});
