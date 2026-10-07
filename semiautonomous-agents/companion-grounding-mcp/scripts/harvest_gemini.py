import subprocess
import json
import time
import os
import base64

def run_chrome_js(js_code):
    b64 = base64.b64encode(js_code.encode('utf-8')).decode('utf-8')
    osa_script = f'''
set b64 to "{b64}"
do shell script "echo " & quoted form of b64 & " | base64 --decode"
set decodedJS to result
tell application "Google Chrome"
    repeat with w in windows
        repeat with t in tabs of w
            if (URL of t) contains "f6fe7adf1cc74569" or (URL of t) contains "gemini.google.com/corp/app" then
                return execute t javascript decodedJS
            end if
        end repeat
    end repeat
    error "Gemini tab not found"
end tell
'''
    res = subprocess.run(["osascript", "-e", osa_script], capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"AppleScript error: {res.stderr.strip()}")
    return res.stdout.strip()

def main():
    print("=== Step 1: Connecting to Gemini Tab in Google Chrome ===")
    check_js = "(() => JSON.stringify({ title: document.title, url: window.location.href }))()"
    initial_info = json.loads(run_chrome_js(check_js))
    print(f"Connected to: {initial_info['title']} ({initial_info['url']})")

    print("\n=== Step 2: Auto-Scrolling to the Very Beginning (Day 1 / June 1) ===")
    scroll_js = """
    (() => {
        const scroller = document.querySelector("infinite-scroller.chat-history");
        if (!scroller) return JSON.stringify({ error: "No scroller found" });
        
        scroller.scrollTop = 0;
        scroller.dispatchEvent(new Event("scroll", { bubbles: true }));
        
        const count = document.querySelectorAll(".conversation-container").length;
        const height = scroller.scrollHeight;
        const top = scroller.scrollTop;
        
        // Also check if the June 1 text is already loaded
        const bodyText = document.body.innerText;
        const hasOrigin = bodyText.includes("5pointzlic") || bodyText.includes("May 22") || bodyText.includes("kabbalah");
        
        return JSON.stringify({
            count: count,
            height: height,
            top: top,
            hasOrigin: hasOrigin
        });
    })()
    """

    last_height = 0
    stable_count = 0
    iteration = 0
    max_iterations = 80

    while iteration < max_iterations:
        iteration += 1
        res_str = run_chrome_js(scroll_js)
        data = json.loads(res_str)
        
        if "error" in data:
            print(f"Error during scroll: {data['error']}")
            break

        count = data["count"]
        height = data["height"]
        has_origin = data.get("hasOrigin", False)

        print(f"[{iteration:02d}] Loaded turns: {count} | Height: {height}px | Day 1 reached: {has_origin}")

        if has_origin and height == last_height:
            stable_count += 1
            if stable_count >= 3:
                print(">>> Reached Day 1 origin! Height stabilized.")
                break
        elif height == last_height:
            stable_count += 1
            if stable_count >= 6:
                print(">>> Scroller height stabilized across 6 checks. Assuming full history is loaded.")
                break
        else:
            stable_count = 0

        last_height = height
        time.sleep(1.8)

    print("\n=== Step 3: Extracting All Turns with Full Text & Formatting ===")
    extract_js = """
    (() => {
        // Force all turn-content-visibility elements to visible to render offscreen turns
        document.querySelectorAll(".turn-content-visibility").forEach(el => {
            el.style.contentVisibility = "visible";
        });
        
        const containers = Array.from(document.querySelectorAll(".conversation-container"));
        const turns = containers.map((c, i) => {
            const qEl = c.querySelector("user-query");
            const rEl = c.querySelector("model-response");
            
            // Clean 'You said' and 'Gemini said' headers
            let qText = qEl ? qEl.innerText.trim() : "";
            if (qText.startsWith("You said")) {
                qText = qText.replace(/^You said\\s*/i, "").trim();
            }
            
            let rText = rEl ? rEl.innerText.trim() : "";
            if (rText.startsWith("Gemini said")) {
                rText = rText.replace(/^Gemini said\\s*/i, "").trim();
            }
            
            return {
                turn_id: i + 1,
                user_query: qText,
                gemini_response: rText,
                user_char_count: qText.length,
                response_char_count: rText.length
            };
        }).filter(t => t.user_query.length > 0 || t.gemini_response.length > 0);
        
        return JSON.stringify({
            total_turns: turns.length,
            first_user_snippet: turns[0]?.user_query?.slice(0, 200),
            last_user_snippet: turns[turns.length - 1]?.user_query?.slice(0, 200),
            turns: turns
        });
    })()
    """

    extract_res_str = run_chrome_js(extract_js)
    extract_data = json.loads(extract_res_str)

    total_turns = extract_data["total_turns"]
    print(f"\nSuccessfully harvested {total_turns} total conversation turns!")
    print(f"Turn 1 Prompt: {extract_data.get('first_user_snippet')}")
    print(f"Latest Turn Prompt: {extract_data.get('last_user_snippet')}")

    out_dir = os.path.expanduser("~/IdeaProjects/vertex-ai-samples/semiautonomous-agents/companion-grounding-mcp/data")
    json_path = os.path.join(out_dir, "gemini_advisory_archive.json")
    md_path = os.path.join(out_dir, "gemini_advisory_archive.md")

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(extract_data, f, indent=2, ensure_ascii=False)
    print(f"\nSaved structured JSON to: {json_path}")

    # Also format clean Markdown for reading and ingestion
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(f"# Complete Gemini Strategic Advisory Archive\n\n")
        f.write(f"- **Total Turns Captured:** {total_turns}\n")
        f.write(f"- **First Turn Date:** June 1, 2026\n")
        f.write(f"- **Harvest Timestamp:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n---\n\n")
        
        for t in extract_data["turns"]:
            f.write(f"## Turn {t['turn_id']}\n\n")
            f.write(f"### 👤 User Query\n{t['user_query']}\n\n")
            f.write(f"### 🤖 Gemini Advice & Calibration\n{t['gemini_response']}\n\n")
            f.write(f"---\n\n")

    print(f"Saved readable Markdown to: {md_path}")
    print("=== Harvest Complete! ===")

if __name__ == "__main__":
    main()
