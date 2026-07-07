// Shared Firestore read for the daily MVP doc. The route handler in ./route.ts
// wraps this for the public HTTP endpoint; the home snapshot endpoint imports
// it directly to skip the HTTP layer.

import { db } from "@/lib/firestore-server";

const COLLECTION = "daily_mvp";

export type MvpEntry = {
  date: string;
  playerId: string;
  name: string;
  points: number;
  pickedExact?: number;
  computedAt: number;
  detail?: string;
};

export async function fetchDailyMvpEntries(): Promise<MvpEntry[]> {
  const snap = await db.collection(COLLECTION).orderBy("date", "desc").limit(2).get();
  return snap.docs.map(d => {
    const data = d.data() as Partial<MvpEntry>;
    return {
      date: typeof data.date === "string" ? data.date : d.id,
      playerId: typeof data.playerId === "string" ? data.playerId : "",
      name: typeof data.name === "string" ? data.name : "",
      points: typeof data.points === "number" ? data.points : 0,
      pickedExact: typeof data.pickedExact === "number" ? data.pickedExact : 0,
      computedAt: typeof data.computedAt === "number" ? data.computedAt : 0,
      detail: typeof data.detail === "string" ? data.detail : undefined,
    };
  });
}
