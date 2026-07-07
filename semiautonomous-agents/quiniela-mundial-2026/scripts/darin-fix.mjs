import { Firestore } from "@google-cloud/firestore";
const db = new Firestore({ projectId: "vtxdemos", databaseId: "(default)" });
const ref = db.collection("quiniela_charales_picks").doc("darin");
const snap = await ref.get();
const cur = snap.exists ? snap.data() : { playerId: "darin", group: {}, bracket: {} };
const group = { ...(cur.group || {}) };
if (group["A-M1"]) {
  console.log("Already has A-M1:", group["A-M1"]);
  process.exit(0);
}
group["A-M1"] = { pick: "H", source: "manual-backfill" };
const next = { ...cur, playerId: "darin", group, updatedAt: Date.now() };
await ref.set(next, { merge: false });
console.log("Wrote A-M1=H for darin. group keys now:", Object.keys(next.group).sort());
