// Shared GCS-backed keeper store for the cromo workshop AND the live album
// pipeline. Workshop saves a ⭐ here; the album reads it as the canonical
// cromo for that {playerId, styleName} pair so the same PNG that survived
// HIL review is what users see on the album page — no re-generation, no
// drift, no re-paying the model.

import { Storage } from "@google-cloud/storage";

const BUCKET = process.env.CROMO_BUCKET || "q26-cromo-portraits";
export const KEEPER_PREFIX = "_keepers";
export const LAST_VARIANT_PREFIX = "_last_variants";

let _storage: Storage | null = null;
function getStorage(): Storage {
  if (!_storage) _storage = new Storage({ projectId: process.env.GOOGLE_CLOUD_PROJECT || "vtxdemos" });
  return _storage;
}

export function keeperObject(playerId: string, styleName: string): string {
  return `${KEEPER_PREFIX}/${playerId}/${styleName}.png`;
}

export function keeperBucket() {
  return getStorage().bucket(BUCKET);
}

export async function saveKeeper(playerId: string, styleName: string, buf: Buffer): Promise<void> {
  await keeperBucket().file(keeperObject(playerId, styleName)).save(buf, {
    contentType: "image/png",
    metadata: { cacheControl: "no-store" },
  });
}

export async function deleteKeeper(playerId: string, styleName: string): Promise<void> {
  await keeperBucket().file(keeperObject(playerId, styleName)).delete({ ignoreNotFound: true });
}

export async function readKeeper(playerId: string, styleName: string): Promise<Buffer | null> {
  try {
    const [buf] = await keeperBucket().file(keeperObject(playerId, styleName)).download();
    return buf;
  } catch {
    return null;
  }
}

// "Last variant" auto-cache: every workshop generation writes here so the
// admin never loses a render they liked but forgot to ⭐. Reloading the
// workshop serves the last variant (no model call) until a 🎲 reroll or
// 🎯 extra-direction explicitly replaces it.
function lastVariantObject(playerId: string, styleName: string): string {
  return `${LAST_VARIANT_PREFIX}/${playerId}/${styleName}.png`;
}

export async function saveLastVariant(playerId: string, styleName: string, buf: Buffer): Promise<void> {
  await keeperBucket().file(lastVariantObject(playerId, styleName)).save(buf, {
    contentType: "image/png",
    metadata: { cacheControl: "no-store" },
  });
}

export async function readLastVariant(playerId: string, styleName: string): Promise<Buffer | null> {
  try {
    const [buf] = await keeperBucket().file(lastVariantObject(playerId, styleName)).download();
    return buf;
  } catch {
    return null;
  }
}

export async function listKeepers(playerId: string): Promise<Set<string>> {
  try {
    const [files] = await keeperBucket().getFiles({ prefix: `${KEEPER_PREFIX}/${playerId}/` });
    const out = new Set<string>();
    const stripLen = `${KEEPER_PREFIX}/${playerId}/`.length;
    for (const f of files) {
      const name = f.name.slice(stripLen);
      if (name.endsWith(".png")) out.add(name.slice(0, -4));
    }
    return out;
  } catch {
    return new Set<string>();
  }
}
