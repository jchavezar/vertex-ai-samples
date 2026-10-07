import subprocess
import time
import json
import base64
import os

OUT_FILE = os.path.expanduser(
    "~/IdeaProjects/vertex-ai-samples/semiautonomous-agents/companion-grounding-mcp/data/instagram_from_msg1_verified.json"
)

activate_cmd = """osascript -e '
tell application "Google Chrome"
    activate
    repeat with w in windows
        set tIdx to 1
        repeat with t in tabs of w
            if URL of t contains "instagram.com/direct/t/119805939405917" then
                set active tab index of w to tIdx
                set index of w to 1
                return "Activated Selene Instagram DM tab"
            end if
            set tIdx to tIdx + 1
        end repeat
    end repeat
    return "Not found"
end tell
'"""

print(subprocess.run(activate_cmd, shell=True, capture_output=True, text=True).stdout.strip())
time.sleep(1.0)

init_crawler_js = """
(function() {
    window.__ig_snapshots = [];
    return "Initialized __ig_snapshots";
})()
"""

step_scroll_and_capture_js = """
(function() {
    const divs = Array.from(document.querySelectorAll('div'));
    const scroller = divs.find(d => {
        const s = getComputedStyle(d);
        return (s.overflowY === 'auto' || s.overflowY === 'scroll') && d.clientHeight > 300 && d.getBoundingClientRect().left > 350;
    });
    if (!scroller) return JSON.stringify({error: 'No scroller'});

    const scRect = scroller.getBoundingClientRect();
    const midX = scRect.left + scRect.width / 2;

    // Extract all currently rendered bubbles in top-to-bottom visual order
    const candidates = Array.from(scroller.querySelectorAll('div[dir="auto"], span[dir="auto"], img[alt]'));
    const items = [];
    for (const el of candidates) {
        if (el.tagName !== 'IMG') {
            const inner = el.querySelector('div[dir="auto"]');
            if (inner && inner.innerText.trim() === el.innerText.trim()) continue;
        }
        const r = el.getBoundingClientRect();
        if (r.width === 0 || r.height === 0) continue;
        // Skip small avatars
        if (el.tagName === 'IMG' && (r.width < 45 || (el.src && el.src.includes('profile')))) continue;

        let txt = el.tagName === 'IMG'
            ? ('[Photo/Media: ' + (el.alt || 'image') + ']')
            : (el.innerText || '').trim();
        if (!txt) continue;

        // Classify by exact horizontal geometry inside scroller
        let role = 'Unknown';
        const center = (r.left + r.right) / 2;
        if (Math.abs(center - midX) < 90 && r.left > scRect.left + 120 && r.right < scRect.right - 120 && txt.length < 45) {
            role = 'TIMESTAMP';
        } else if (r.left - scRect.left < 140 && scRect.right - r.right > 140) {
            role = 'Selene';
        } else if (scRect.right - r.right < 140 && r.left - scRect.left > 140) {
            role = 'Jesus';
        } else if (center < midX) {
            role = 'Selene';
        } else {
            role = 'Jesus';
        }

        items.push({
            visualY: Math.round(r.top),
            left: Math.round(r.left),
            right: Math.round(r.right),
            role: role,
            text: txt
        });
    }
    items.sort((a, b) => a.visualY - b.visualY || a.left - b.left);

    // Deduplicate overlapping identical nodes at same visualY
    const deduped = [];
    for (const it of items) {
        if (deduped.length > 0) {
            const prev = deduped[deduped.length - 1];
            if (Math.abs(prev.visualY - it.visualY) <= 6 && prev.text === it.text) continue;
        }
        deduped.push(it);
    }

    if (!window.__ig_snapshots) window.__ig_snapshots = [];
    window.__ig_snapshots.push({
        scrollTop: scroller.scrollTop,
        scrollHeight: scroller.scrollHeight,
        items: deduped
    });

    // Now scroll UP to trigger loading older messages
    // Because flex-direction is column-reverse, top of history is scrollTop = -(scrollHeight - clientHeight)
    const maxNeg = -(scroller.scrollHeight - scroller.clientHeight);
    scroller.scrollTop = Math.max(maxNeg, scroller.scrollTop - 650);

    // Also if near top, touch the topmost element and dispatch wheel + scroll events
    if (Math.abs(scroller.scrollTop - maxNeg) < 150) {
        scroller.scrollTop = maxNeg;
        const firstChild = scroller.lastElementChild || scroller.firstElementChild;
        if (firstChild && firstChild.scrollIntoView) {
            firstChild.scrollIntoView({block: 'start'});
        }
    }
    for (let i = 0; i < 4; i++) {
        scroller.dispatchEvent(new WheelEvent('wheel', {deltaY: -900, bubbles: true, cancelable: true}));
    }
    scroller.dispatchEvent(new Event('scroll', {bubbles: true}));

    return JSON.stringify({
        scrollTop: Math.round(scroller.scrollTop),
        maxNeg: Math.round(maxNeg),
        scrollHeight: scroller.scrollHeight,
        capturedInView: deduped.length,
        topItem: deduped.length > 0 ? (deduped[0].role + ': ' + deduped[0].text.slice(0, 60)) : ''
    });
})()
"""

def run_js(code):
    b64 = base64.b64encode(code.encode("utf-8")).decode("utf-8")
    cmd = f"""osascript -e '
    tell application "Google Chrome"
        repeat with w in windows
            repeat with t in tabs of w
                if URL of t contains "instagram.com/direct/t/119805939405917" then
                    return (execute t javascript "eval(atob(\\"{b64}\\"))")
                end if
            end repeat
        end repeat
    end tell
    '"""
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return res.stdout.strip()

run_js(init_crawler_js)

same_top_streak = 0
last_top_item = None
last_scroll_height = 0

for step in range(90):
    out = run_js(step_scroll_and_capture_js)
    try:
        info = json.loads(out)
    except Exception:
        print(f"Step {step}: raw={out[:100]}")
        continue

    top_item = info.get("topItem", "")
    sh = info.get("scrollHeight", 0)
    st = info.get("scrollTop", 0)
    mn = info.get("maxNeg", 0)
    if step % 5 == 0 or sh != last_scroll_height:
        print(f"[Step {step:02d}] scrollTop={st} (maxNeg={mn}) | scrollHeight={sh} | top='{top_item}'")

    if top_item == last_top_item and sh == last_scroll_height and abs(st - mn) < 30:
        same_top_streak += 1
        if same_top_streak >= 8:
            print(f"Reached absolute top of thread after {step+1} steps! Top item: {top_item}")
            break
    else:
        same_top_streak = 0

    last_top_item = top_item
    last_scroll_height = sh
    time.sleep(0.85)

# Fetch all snapshots and stitch them in exact chronological order from Message #1 to final message
fetch_snapshots_js = "JSON.stringify(window.__ig_snapshots || [])"
raw_snaps = run_js(fetch_snapshots_js)
snaps = json.loads(raw_snaps)
print(f"Retrieved {len(snaps)} scroll snapshots from browser.")

# Since snapshots[0] is bottom (newest) and snapshots[-1] is top (oldest, Message #1),
# we reverse snapshots so we walk from the oldest view (Message #1) down to the newest view!
snaps.reverse()

merged = []
for snap in snaps:
    items = snap.get("items", [])
    if not items:
        continue
    if not merged:
        merged.extend(items)
        continue
    # Find overlap between tail of merged and head of items
    overlap_found = False
    max_k = min(len(merged), len(items), 25)
    for k in range(max_k, 1, -1):
        tail_sigs = [(m["role"], m["text"]) for m in merged[-k:]]
        head_sigs = [(m["role"], m["text"]) for m in items[:k]]
        if tail_sigs == head_sigs:
            merged.extend(items[k:])
            overlap_found = True
            break
    if not overlap_found:
        # Try single anchor match in last 15 items of merged
        for idx_in_items in range(min(10, len(items))):
            sig = (items[idx_in_items]["role"], items[idx_in_items]["text"])
            for back in range(1, min(20, len(merged)) + 1):
                if (merged[-back]["role"], merged[-back]["text"]) == sig:
                    # Replace from -back with items[idx_in_items:] if items extends further
                    if len(items) - idx_in_items > back:
                        merged = merged[:-back] + items[idx_in_items:]
                    overlap_found = True
                    break
            if overlap_found:
                break
    if not overlap_found:
        # Append any items not recently seen in last 30 of merged
        recent_set = {(m["role"], m["text"]) for m in merged[-30:]}
        for it in items:
            if (it["role"], it["text"]) not in recent_set:
                merged.append(it)
                recent_set.add((it["role"], it["text"]))

# Propagate TIMESTAMP headers onto subsequent messages
current_ts = "Beginning of Thread"
structured_messages = []
msg_num = 1
for m in merged:
    if m["role"] == "TIMESTAMP":
        current_ts = m["text"]
    else:
        structured_messages.append({
            "msg_number": msg_num,
            "platform": "Instagram",
            "sender": m["role"],
            "timestamp_section": current_ts,
            "text": m["text"],
            "left_px": m["left"],
            "right_px": m["right"]
        })
        msg_num += 1

with open(OUT_FILE, "w", encoding="utf-8") as f:
    json.dump(structured_messages, f, indent=2, ensure_ascii=False)

print(f"Saved {len(structured_messages)} verified Instagram messages to {OUT_FILE}")
if structured_messages:
    print("First 5 messages (from Message #1):")
    for x in structured_messages[:5]:
        print(" ", x)
    print("Last 5 messages:")
    for x in structured_messages[-5:]:
        print(" ", x)
