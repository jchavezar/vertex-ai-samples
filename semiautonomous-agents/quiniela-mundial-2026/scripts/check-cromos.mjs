import { Firestore } from "@google-cloud/firestore";
const db = new Firestore({ projectId: "vtxdemos" });
const snap = await db.collection("cromo_portraits").orderBy("createdAt","desc").limit(50).get();
const byDate = {};
for (const d of snap.docs) {
  const v = d.data();
  const dt = v.date || "?";
  byDate[dt] = byDate[dt] || [];
  byDate[dt].push({ id: d.id, style: v.style, created: new Date(v.createdAt||0).toISOString() });
}
for (const dt of Object.keys(byDate).sort().reverse()) {
  console.log(`\n=== ${dt} (${byDate[dt].length} docs) ===`);
  for (const x of byDate[dt]) console.log(" ", x.id.padEnd(30), x.style?.padEnd(20), x.created);
}
