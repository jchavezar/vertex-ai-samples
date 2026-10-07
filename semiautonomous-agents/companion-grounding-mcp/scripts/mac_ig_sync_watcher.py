#!/usr/bin/env python3
"""
Background watcher that polls gs://vtxdemos-companion-memory/sync_trigger.json.
Whenever Claude on Pixel 11 Pro calls `sync_my_journal_backup`, this watcher:
1. Scrapes any new Instagram messages, emojis, reactions, and photos from Chrome `Default` profile.
2. Runs `gemini-3.8-flash` Multimodal Vision on any newly sent photos.
3. Updates `ground_truth.db` + rebuilds FTS & 3072-dim vector embeddings (`gemini-embedding-001`).
4. Uploads `ground_truth.db` to `gs://vtxdemos-companion-memory/ground_truth.db` for instant zero-redeploy Cloud Run hot-reload.
"""
import os, time, json, subprocess, sqlite3, urllib.request
from google.cloud import storage
from google import genai
from google.genai import types

os.environ.pop("GOOGLE_API_CERTIFICATE_CONFIG", None)
BUCKET_NAME = "vtxdemos-companion-memory"
PROJECT_ID = "vtxdemos"
BASE_DIR = "/Users/jesusarguelles/IdeaProjects/vertex-ai-samples/semiautonomous-agents/companion-grounding-mcp"
DB_PATH = os.path.join(BASE_DIR, "data/ground_truth.db")
CACHE_DIR = os.path.join(BASE_DIR, "data/media_cache/ig_live")
os.makedirs(CACHE_DIR, exist_ok=True)


def sync_instagram_and_vision():
    # Ensure Instagram DM tab is open in Default profile
    subprocess.run(
        [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "--profile-directory=Default",
            "https://www.instagram.com/direct/t/119805939405917/",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    time.sleep(3)

    js = """
    (function() {
        const divs = Array.from(document.querySelectorAll("div"));
        const scroller = divs.find(d => {
            const s = getComputedStyle(d);
            return (s.overflowY === "auto" || s.overflowY === "scroll") && d.clientHeight > 300 && d.getBoundingClientRect().left > 350;
        });
        if (!scroller) return "[]";
        scroller.scrollTop = 0;
        const scRect = scroller.getBoundingClientRect();
        const midX = scRect.left + scRect.width / 2;

        function getTextWithEmojis(el) {
            let out = "";
            for (const child of el.childNodes) {
                if (child.nodeType === Node.TEXT_NODE) out += child.nodeValue;
                else if (child.nodeType === Node.ELEMENT_NODE) {
                    if (child.tagName === "IMG") {
                        const alt = child.getAttribute("alt") || "";
                        if (alt && alt.length <= 8) out += alt;
                    } else if (child.tagName === "BR") out += "\\n";
                    else out += getTextWithEmojis(child);
                }
            }
            return out;
        }

        const out = [];
        const mediaEls = scroller.querySelectorAll("img, video");
        for (const m of mediaEls) {
            const r = m.getBoundingClientRect();
            if (r.width < 45 || r.height < 45) continue;
            const src = m.src || m.currentSrc || m.poster || "";
            const alt = m.alt || "";
            if (!src || src.includes("emoji.php") || alt.includes("profile-picture") || src.includes("playButton.png")) continue;
            const center = (r.left + r.right) / 2;
            out.push({type: "image", y: Math.round(r.top), sender: center < midX ? "Selene" : "Jesus", src: src, alt: alt});
        }

        const els = scroller.querySelectorAll("div[dir=\\"auto\\"], span[dir=\\"auto\\"]");
        for (const el of els) {
            const inner = el.querySelector("div[dir=\\"auto\\"], span[dir=\\"auto\\"]");
            if (inner && getTextWithEmojis(inner).trim() === getTextWithEmojis(el).trim()) continue;
            const r = el.getBoundingClientRect();
            if (r.width === 0 || r.height === 0) continue;
            const txt = getTextWithEmojis(el).trim();
            if (!txt || txt === "Edited" || txt === "Open photo") continue;
            const center = (r.left + r.right) / 2;
            out.push({type: "text", y: Math.round(r.top), sender: center < midX ? "Selene" : "Jesus", text: txt});
        }
        out.sort((a, b) => a.y - b.y);
        return JSON.stringify(out);
    })()
    """
    with open("/tmp/ig_watcher_step.js", "w", encoding="utf-8") as f:
        f.write(js)
    apple = '''
    set jsCode to read POSIX file "/tmp/ig_watcher_step.js" as «class utf8»
    tell application "Google Chrome"
        repeat with w in windows
            repeat with t in tabs of w
                if (URL of t contains "instagram.com/direct/t/119805939405917") and (URL of t does not contain "__coig_login") then
                    return execute t javascript jsCode
                end if
            end repeat
        end repeat
        return "[]"
    end tell
    '''
    raw = subprocess.run(["osascript", "-e", apple], capture_output=True, text=True).stdout.strip()
    try:
        items = json.loads(raw) if raw else []
    except Exception:
        items = []

    if not items:
        return 0

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    recent_rows = c.execute("SELECT text, raw_json FROM raw_messages WHERE platform='Instagram' ORDER BY id DESC LIMIT 120").fetchall()
    existing_texts = {r[0].strip() for r in recent_rows if r[0]}
    existing_srcs = set()
    for _, rj in recent_rows:
        if rj:
            try:
                d = json.loads(rj)
                if d.get("src"):
                    existing_srcs.add(d["src"][:90])
            except Exception:
                pass

    ai_client = genai.Client(vertexai=True, project=PROJECT_ID, location="global")
    added = 0
    now_str = time.strftime("%b %d, %Y, %I:%M %p")

    for it in items:
        if it["type"] == "image":
            src = it["src"]
            if src[:90] in existing_srcs:
                continue
            try:
                req = urllib.request.Request(src, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=15) as resp:
                    img_bytes = resp.read()
                res = ai_client.models.generate_content(
                    model="gemini-3.8-flash",
                    contents=[
                        types.Part.from_bytes(data=img_bytes, mime_type="image/jpeg"),
                        f"Photo sent by {it['sender']} in Instagram DM between Jesus and Selene. Describe in vivid detail (2-3 sentences): people, facial expressions, outfit, food, setting, and visible text.",
                    ],
                )
                vdesc = res.text.strip().replace("\n", " ")
            except Exception:
                vdesc = f"Photo sent by {it['sender']}"
            full_txt = f"[Photo sent by {it['sender']}: {vdesc}]"
            c.execute(
                """
                INSERT INTO raw_messages (
                    platform, channel_name, channel_id, account_type, thread_url,
                    sender, timestamp, text, media_desc, sentiment_label, models_net_rating, raw_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'Live Synced Multimodal', 'Live Synced', ?)
                """,
                (
                    "Instagram",
                    "Instagram Direct Message (@selenesng <-> @jchavezarg)",
                    "ig_dm_119805939405917",
                    "Personal Social Account (Instagram Live Watcher)",
                    "https://www.instagram.com/direct/t/119805939405917/",
                    it["sender"],
                    now_str,
                    full_txt,
                    f"Vision (gemini-3.8-flash): {vdesc}",
                    json.dumps(it, ensure_ascii=False),
                ),
            )
            existing_srcs.add(src[:90])
            added += 1
        else:
            txt = it["text"].strip()
            if txt in existing_texts or txt in ("You replied to selenesng", "selenesng replied to you"):
                continue
            c.execute(
                """
                INSERT INTO raw_messages (
                    platform, channel_name, channel_id, account_type, thread_url,
                    sender, timestamp, text, sentiment_label, models_net_rating, raw_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'Live Synced', 'Live Synced', ?)
                """,
                (
                    "Instagram",
                    "Instagram Direct Message (@selenesng <-> @jchavezarg)",
                    "ig_dm_119805939405917",
                    "Personal Social Account (Instagram Live Watcher)",
                    "https://www.instagram.com/direct/t/119805939405917/",
                    it["sender"],
                    now_str,
                    txt,
                    json.dumps(it, ensure_ascii=False),
                ),
            )
            existing_texts.add(txt)
            added += 1

    if added > 0:
        c.execute("INSERT INTO raw_messages_fts(raw_messages_fts) VALUES('rebuild')")
        conn.commit()
    conn.close()

    if added > 0:
        subprocess.run(["python3", os.path.join(BASE_DIR, "scripts/build_vector_index.py")], check=False)

    # Always upload latest ground_truth.db to GCS
    storage_client = storage.Client(project=PROJECT_ID)
    bucket = storage_client.bucket(BUCKET_NAME)
    bucket.blob("ground_truth.db").upload_from_filename(DB_PATH)
    return added


def main():
    storage_client = storage.Client(project=PROJECT_ID)
    bucket = storage_client.bucket(BUCKET_NAME)
    print("[mac_ig_sync_watcher] Listening for gs://vtxdemos-companion-memory/sync_trigger.json every 20s...")
    while True:
        try:
            blob = bucket.blob("sync_trigger.json")
            if blob.exists():
                data = json.loads(blob.download_as_text())
                if data.get("status") == "requested":
                    print("[mac_ig_sync_watcher] Trigger detected! Running Instagram + Vision sync...")
                    added = sync_instagram_and_vision()
                    blob.upload_from_string(
                        json.dumps({
                            "status": "completed",
                            "completed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                            "new_items_added": added,
                            "source": "mac_chrome_instagram_vision_watcher",
                        }),
                        content_type="application/json",
                    )
                    print(f"[mac_ig_sync_watcher] Completed sync (added={added}) and uploaded ground_truth.db to GCS!")
        except Exception as e:
            print(f"[mac_ig_sync_watcher] Poll error: {e}")
        time.sleep(20)


if __name__ == "__main__":
    main()
