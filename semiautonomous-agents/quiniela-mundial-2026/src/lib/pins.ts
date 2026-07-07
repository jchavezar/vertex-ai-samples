// PIN storage in Firestore. Plain text by design — owner needs to look them up.
import { db, PINS_COLLECTION } from "./firestore-server";
import { DEFAULT_PIN } from "./auth-server";
import { PLAYERS } from "@/data/players";

export type PinRecord = {
  playerId: string;
  name: string;
  pin: string;
  isDefault: boolean;
  createdAt: number;
  updatedAt: number;
};

function nameFor(playerId: string): string {
  return PLAYERS.find(p => p.id === playerId)?.name || playerId;
}

export async function getPin(playerId: string): Promise<PinRecord> {
  const ref = db.collection(PINS_COLLECTION).doc(playerId);
  const snap = await ref.get();
  if (snap.exists) {
    return snap.data() as PinRecord;
  }
  const now = Date.now();
  const rec: PinRecord = {
    playerId,
    name: nameFor(playerId),
    pin: DEFAULT_PIN,
    isDefault: true,
    createdAt: now,
    updatedAt: now,
  };
  await ref.set(rec);
  return rec;
}

export async function verifyPin(playerId: string, pin: string): Promise<boolean> {
  const rec = await getPin(playerId);
  return rec.pin === pin;
}

export async function setPin(playerId: string, newPin: string): Promise<PinRecord> {
  const ref = db.collection(PINS_COLLECTION).doc(playerId);
  const now = Date.now();
  const snap = await ref.get();
  const existing = (snap.exists ? snap.data() : null) as PinRecord | null;
  const rec: PinRecord = {
    playerId,
    name: nameFor(playerId),
    pin: newPin,
    isDefault: newPin === DEFAULT_PIN,
    createdAt: existing?.createdAt ?? now,
    updatedAt: now,
  };
  await ref.set(rec);
  return rec;
}

export async function listPins(): Promise<PinRecord[]> {
  const snap = await db.collection(PINS_COLLECTION).get();
  const map = new Map<string, PinRecord>();
  snap.forEach(d => map.set(d.id, d.data() as PinRecord));
  // Ensure every player appears, even if never logged in (returns default).
  return PLAYERS.map(p => {
    const r = map.get(p.id);
    if (r) return r;
    return {
      playerId: p.id,
      name: p.name,
      pin: DEFAULT_PIN,
      isDefault: true,
      createdAt: 0,
      updatedAt: 0,
    };
  });
}
