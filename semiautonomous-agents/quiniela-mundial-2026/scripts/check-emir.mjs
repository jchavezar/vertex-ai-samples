import { Firestore } from "@google-cloud/firestore";
const db = new Firestore({ projectId: "vtxdemos", databaseId: "(default)" });

const players = ["emir", "jesus", "xavi", "akyno", "charal", "aldo", "darin", "tilapia", "jochabe", "mvictor"];
const ref = db.collection("quiniela_charales_picks");

for (const id of players) {
  const snap = await ref.doc(id).get();
  if (!snap.exists) { console.log(`${id.padEnd(10)} → NO DOC`); continue; }
  const data = snap.data();
  const group = data.group || {};
  const bracket = data.bracket || {};
  const groupKeys = Object.keys(group);
  const sources = {};
  for (const v of Object.values(group)) {
    const s = v?.source || "unknown";
    sources[s] = (sources[s] || 0) + 1;
  }
  const updated = data.updatedAt ? new Date(data.updatedAt).toISOString() : "n/a";
  console.log(`${id.padEnd(10)} → group=${groupKeys.length}/72  bracket=${Object.keys(bracket).length}  updated=${updated}  src=${JSON.stringify(sources)}`);
}

console.log("\n--- Emir detail ---");
const emir = await ref.doc("emir").get();
if (emir.exists) {
  const d = emir.data();
  const group = d.group || {};
  const keys = Object.keys(group).sort();
  console.log("group keys:", keys);
  console.log("bracket:", d.bracket || {});
  if (keys.length) {
    console.log("sample entry:", keys[0], "=>", group[keys[0]]);
  }
} else {
  console.log("NO emir doc");
}
