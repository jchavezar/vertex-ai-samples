"use client";

// Offline pick queue backed by IndexedDB + Background Sync API.
// When a POST /api/picks fails due to no network, we enqueue it here.
// The SW will flush the queue the next time the device comes online,
// even if the app is closed. Falls back silently on browsers without support.

const DB_NAME = "q26-offline";
const STORE_NAME = "q26-bg-picks";
const SYNC_TAG = "q26-pick-queue";

function openDB(): Promise<IDBDatabase> {
  return new Promise((resolve, reject) => {
    const req = indexedDB.open(DB_NAME, 1);
    req.onupgradeneeded = (e) => {
      (e.target as IDBOpenDBRequest).result.createObjectStore(STORE_NAME, { keyPath: "fixtureId" });
    };
    req.onsuccess = (e) => resolve((e.target as IDBOpenDBRequest).result);
    req.onerror = () => reject(req.error);
  });
}

export async function enqueuePickForBgSync(fixtureId: string, pick: string): Promise<void> {
  if (typeof window === "undefined" || !("indexedDB" in window)) return;
  try {
    const db = await openDB();
    await new Promise<void>((resolve, reject) => {
      const tx = db.transaction(STORE_NAME, "readwrite");
      tx.objectStore(STORE_NAME).put({ fixtureId, pick, enqueuedAt: Date.now() });
      tx.oncomplete = () => resolve();
      tx.onerror = () => reject(tx.error);
    });
    if ("serviceWorker" in navigator) {
      const reg = await navigator.serviceWorker.ready;
      if ("sync" in reg) {
        await (reg as ServiceWorkerRegistration & { sync: { register(tag: string): Promise<void> } }).sync.register(SYNC_TAG);
      }
    }
  } catch {
    // SW not registered or Background Sync not supported — legacy retry handles it
  }
}

export async function removeFromBgSyncQueue(fixtureId: string): Promise<void> {
  if (typeof window === "undefined" || !("indexedDB" in window)) return;
  try {
    const db = await openDB();
    await new Promise<void>((resolve, reject) => {
      const tx = db.transaction(STORE_NAME, "readwrite");
      tx.objectStore(STORE_NAME).delete(fixtureId);
      tx.oncomplete = () => resolve();
      tx.onerror = () => reject(tx.error);
    });
  } catch { /* ignore */ }
}
