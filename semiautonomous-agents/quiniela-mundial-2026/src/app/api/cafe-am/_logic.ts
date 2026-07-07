// Shared reader for today's cafe_am Firestore brief. Used by ./route.ts and
// by /api/home/snapshot to avoid an extra HTTP round-trip.

import { db } from "@/lib/firestore-server";

const COLLECTION = "cafe_am";

export type CafeBrief = {
  date: string;
  text: string;
  generatedAt: number;
  modelUsed?: string;
};

export type PublicCafeBrief = {
  date: string;
  text: string;
  generatedAt: number;
};

export function cdmxDate(): string {
  return new Intl.DateTimeFormat("en-CA", {
    timeZone: "America/Mexico_City",
    year: "numeric", month: "2-digit", day: "2-digit",
  }).format(new Date());
}

export async function fetchTodayCafeBrief(): Promise<PublicCafeBrief | null> {
  const date = cdmxDate();
  const snap = await db.collection(COLLECTION).doc(date).get();
  if (!snap.exists) return null;
  const data = snap.data() as CafeBrief;
  return { date: data.date, text: data.text, generatedAt: data.generatedAt };
}
