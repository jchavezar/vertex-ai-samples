import subprocess
import time
import json
import os

OUT_PATH = os.path.expanduser(
    "~/IdeaProjects/vertex-ai-samples/semiautonomous-agents/companion-grounding-mcp/data/instagram_from_msg1_verified.json"
)


def run_tiny_js(js_expr: str) -> str:
    # Write JS to a temporary file and read it via AppleScript `read POSIX file` so osascript NEVER hits -2742!
    tmp_js = "/tmp/ig_step_exec.js"
    with open(tmp_js, "w", encoding="utf-8") as f:
        f.write(js_expr)
    apple = '''
    set jsCode to read POSIX file "/tmp/ig_step_exec.js" as «class utf8»
    tell application "Google Chrome"
        repeat with w in windows
            repeat with t in tabs of w
                if URL of t contains "instagram.com/direct/t/119805939405917" then
                    return execute t javascript jsCode
                end if
            end repeat
        end repeat
    end tell
    '''
    res = subprocess.run(["osascript", "-e", apple], capture_output=True, text=True)
    return res.stdout.strip()


scan_js = """
(function() {
    const divs = Array.from(document.querySelectorAll('div'));
    const scroller = divs.find(d => {
        const s = getComputedStyle(d);
        return (s.overflowY === 'auto' || s.overflowY === 'scroll') && d.clientHeight > 300 && d.getBoundingClientRect().left > 350;
    });
    if (!scroller) return JSON.stringify({error: 'No scroller'});

    window.__ig_full_done = false;
    window.__ig_full_items = [];
    window.__ig_progress = 0;

    (async function() {
        const maxNeg = -(scroller.scrollHeight - scroller.clientHeight);
        const step = 520; // clientHeight is 882px -> 362px overlap on EVERY step! Zero gaps possible!
        const map = new Map();

        for (let pos = maxNeg; pos <= 0; pos += step) {
            scroller.scrollTop = pos;
            scroller.dispatchEvent(new Event('scroll', {bubbles: true}));
            await new Promise(r => setTimeout(r, 65));

            const scRect = scroller.getBoundingClientRect();
            const midX = scRect.left + scRect.width / 2;
            const curH = scroller.scrollHeight;
            const curTop = scroller.scrollTop;

            const els = scroller.querySelectorAll('div[dir="auto"], span[dir="auto"], img[alt]');
            for (const el of els) {
                if (el.tagName !== 'IMG') {
                    const inner = el.querySelector('div[dir="auto"]');
                    if (inner && inner.innerText.trim() === el.innerText.trim()) continue;
                }
                const r = el.getBoundingClientRect();
                if (r.width === 0 || r.height === 0) continue;
                if (el.tagName === 'IMG' && (r.width < 45 || (el.src && el.src.includes('profile')))) continue;

                const txt = el.tagName === 'IMG'
                    ? ('[Photo/Media: ' + (el.alt || 'image') + ']')
                    : (el.innerText || '').trim();
                if (!txt) continue;

                const distFromBottom = (curH - scRect.height) + curTop;
                const absY = Math.round(distFromBottom + (r.top - scRect.top));

                const center = (r.left + r.right) / 2;
                const isDate = /^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|\\d{1,2}\\/\\d{1,2}\\/\\d{2,4}|Mon|Tue|Wed|Thu|Fri|Sat|Sun|Yesterday|Today)/i.test(txt) && txt.length < 35;
                let role = 'Unknown';
                if (isDate || (Math.abs(center - midX) < 90 && r.left > scRect.left + 120 && r.right < scRect.right - 120 && txt.length < 45)) {
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

                const bY = Math.round(absY / 16);
                const k0 = bY + '::' + txt;
                const k1 = (bY - 1) + '::' + txt;
                const k2 = (bY + 1) + '::' + txt;
                if (!map.has(k0) && !map.has(k1) && !map.has(k2)) {
                    map.set(k0, {
                        absY: absY,
                        left_px: Math.round(r.left),
                        right_px: Math.round(r.right),
                        sender: role,
                        text: txt
                    });
                }
            }
            window.__ig_progress = map.size;
        }

        // Final stop at 0 (bottom of chat)
        scroller.scrollTop = 0;
        await new Promise(r => setTimeout(r, 120));
        const scRect = scroller.getBoundingClientRect();
        const midX = scRect.left + scRect.width / 2;
        const curH = scroller.scrollHeight;
        const els = scroller.querySelectorAll('div[dir="auto"], span[dir="auto"], img[alt]');
        for (const el of els) {
            if (el.tagName !== 'IMG') {
                const inner = el.querySelector('div[dir="auto"]');
                if (inner && inner.innerText.trim() === el.innerText.trim()) continue;
            }
            const r = el.getBoundingClientRect();
            if (r.width === 0 || r.height === 0) continue;
            if (el.tagName === 'IMG' && (r.width < 45 || (el.src && el.src.includes('profile')))) continue;
            const txt = el.tagName === 'IMG' ? ('[Photo/Media: ' + (el.alt || 'image') + ']') : (el.innerText || '').trim();
            if (!txt) continue;
            const distFromBottom = (curH - scRect.height) + scroller.scrollTop;
            const absY = Math.round(distFromBottom + (r.top - scRect.top));
            const center = (r.left + r.right) / 2;
            const isDate = /^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|\\d{1,2}\\/\\d{1,2}\\/\\d{2,4}|Mon|Tue|Wed|Thu|Fri|Sat|Sun|Yesterday|Today)/i.test(txt) && txt.length < 35;
            let role = isDate ? 'TIMESTAMP' : ((r.left - scRect.left < 140 && scRect.right - r.right > 140) ? 'Selene' : ((scRect.right - r.right < 140 && r.left - scRect.left > 140) ? 'Jesus' : (center < midX ? 'Selene' : 'Jesus')));
            const bY = Math.round(absY / 16);
            const k0 = bY + '::' + txt;
            if (!map.has(k0) && !map.has((bY-1)+'::'+txt) && !map.has((bY+1)+'::'+txt)) {
                map.set(k0, {absY, left_px: Math.round(r.left), right_px: Math.round(r.right), sender: role, text: txt});
            }
        }

        const arr = Array.from(map.values()).sort((a, b) => a.absY - b.absY || a.left_px - b.left_px);
        window.__ig_full_items = arr;
        window.__ig_full_done = true;
    })();
    return "Started 520px overlap scan";
})()
"""

print(run_tiny_js(scan_js))

for i in range(45):
    time.sleep(1.0)
    status_str = run_tiny_js("JSON.stringify({done: window.__ig_full_done, count: window.__ig_progress})")
    print(f"  [{i+1}s] {status_str}")
    if '"done":true' in status_str:
        break

raw_json = run_tiny_js("JSON.stringify(window.__ig_full_items)")
items = json.loads(raw_json)
for idx, it in enumerate(items, start=1):
    it["msg_number"] = idx
    it["platform"] = "Instagram"
    it["timestamp_section"] = "Instagram"

with open(OUT_PATH, "w", encoding="utf-8") as f:
    json.dump(items, f, indent=2, ensure_ascii=False)

print(f"Captured {len(items)} total nodes (zero-gap 520px step scan) -> {OUT_PATH}")
