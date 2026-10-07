import subprocess
import json
import time
import os
import base64

NOTEBOOK_URL_KEY = "b14ca1e0-8e8f-424c-8b55-fc65a0b7f608"

def run_chrome_js(js_code, url_key=NOTEBOOK_URL_KEY):
    b64 = base64.b64encode(js_code.encode('utf-8')).decode('utf-8')
    osa_script = f'''
set b64 to "{b64}"
do shell script "echo " & quoted form of b64 & " | base64 --decode"
set decodedJS to result
tell application "Google Chrome"
    repeat with w in windows
        repeat with t in tabs of w
            if (URL of t) contains "{url_key}" or (URL of t) contains "gemini.google.com/corp/app" then
                return execute t javascript decodedJS
            end if
        end repeat
    end repeat
    error "Gemini tab not found for {url_key}"
end tell
'''
    res = subprocess.run(["osascript", "-e", osa_script], capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"AppleScript error: {res.stderr.strip()}")
    return res.stdout.strip()

def get_notebook_chats():
    js = """
    JSON.stringify(Array.from(document.querySelectorAll("button[data-test-id=navigate-to-recent-chat]")).map((b, i) => ({
        index: i,
        text: b.innerText.trim()
    })))
    """
    res = run_chrome_js(js)
    return json.loads(res)

def extract_chat_turns(chat_title):
    print(f"  Ensuring chat is fully loaded for '{chat_title}'...")
    scroll_js = """
    (() => {
        const scroller = document.querySelector("infinite-scroller.chat-history");
        if (scroller) {
            scroller.scrollTop = 0;
            scroller.dispatchEvent(new Event("scroll", { bubbles: true }));
            return JSON.stringify({ height: scroller.scrollHeight, top: scroller.scrollTop });
        }
        return JSON.stringify({ noScroller: true });
    })()
    """
    
    last_height = 0
    stable = 0
    for _ in range(15):
        r = json.loads(run_chrome_js(scroll_js))
        if r.get("noScroller"):
            break
        h = r.get("height", 0)
        if h == last_height:
            stable += 1
            if stable >= 3:
                break
        else:
            stable = 0
        last_height = h
        time.sleep(1)

    extract_js = """
    (() => {
        document.querySelectorAll(".turn-content-visibility").forEach(el => {
            el.style.contentVisibility = "visible";
        });
        
        const containers = Array.from(document.querySelectorAll(".conversation-container"));
        const turns = containers.map((c, i) => {
            const qEl = c.querySelector("user-query");
            const rEl = c.querySelector("model-response");
            
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
            url: window.location.href,
            title: document.title,
            turns: turns
        });
    })()
    """
    res = json.loads(run_chrome_js(extract_js))
    return res

def main():
    print("=== Harvesting All Saju Past Chats from Gemini Notebook ===")
    
    chats = get_notebook_chats()
    print(f"Found {len(chats)} chats in notebook:")
    for c in chats:
        print(f"  [{c['index']}] {c['text'].replace(chr(10), ' - ')}")

    all_harvested = []

    for i in range(1, len(chats)):
        item = chats[i]
        title_summary = item['text'].replace('\n', ' - ')
        print(f"\n--- Harvesting [{i}/{len(chats)-1}]: {title_summary} ---")
        
        click_js = f"""
        (() => {{
            const btns = document.querySelectorAll("button[data-test-id=navigate-to-recent-chat]");
            if (btns[{i}]) {{
                btns[{i}].click();
                return "CLICKED";
            }}
            return "NOT_FOUND";
        }})()
        """
        click_res = run_chrome_js(click_js)
        print(f"  Click result: {click_res}")
        time.sleep(3)

        data = extract_chat_turns(title_summary)
        print(f"  Navigated to: {data['url']}")
        print(f"  Harvested {len(data['turns'])} turns from this chat.")
        all_harvested.append({
            "index": i,
            "notebook_label": item['text'],
            "url": data['url'],
            "title": data['title'],
            "turns": data['turns']
        })

        print("  Navigating back to notebook...")
        run_chrome_js("window.history.back()")
        time.sleep(3)

    out_path = os.path.expanduser("~/IdeaProjects/vertex-ai-samples/semiautonomous-agents/companion-grounding-mcp/data/gemini_saju_notebook_all_chats.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(all_harvested, f, indent=2, ensure_ascii=False)
        
    print(f"\n=== Successfully harvested all {len(all_harvested)} Saju secondary chats! ===")
    print(f"Saved to: {out_path}")

if __name__ == "__main__":
    main()
