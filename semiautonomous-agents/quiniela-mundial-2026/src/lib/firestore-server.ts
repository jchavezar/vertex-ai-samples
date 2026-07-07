// Server-only Firestore client. Uses ADC from Cloud Run compute SA.
import { Firestore } from "@google-cloud/firestore";

declare global {
  // eslint-disable-next-line no-var
  var __q26_firestore: Firestore | undefined;
}

export const db: Firestore =
  global.__q26_firestore ??
  (global.__q26_firestore = new Firestore({
    projectId: process.env.GOOGLE_CLOUD_PROJECT || "vtxdemos",
    databaseId: process.env.FIRESTORE_DATABASE_ID || "(default)",
  }));

export const PINS_COLLECTION = "quiniela_charales_pins";
