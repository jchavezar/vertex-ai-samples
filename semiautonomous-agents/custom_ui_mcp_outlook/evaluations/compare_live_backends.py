import json
import httpx
import time
import asyncio
import os

QUESTIONS = [
    "Do I have an unsent email drafted for the Falcon Project Team?",
    "Check if I have a draft email for 'Q3 Strategy Planning'.",
    "Find the email I sent to support@M365x214355.onmicrosoft.com and tell me its subject and content.",
    "What did I write in the email I sent to james.wu@contoso.com about the Q3 budget?",
    "I see an undeliverable notice for an email to james.wilson@sockcop.onmicrosoft.com. Cross-reference this with my sent items to find the subject of the original email that failed to deliver.",
    "What is my most recent unread email?",
    "Find emails with 'Project Phoenix' in the subject line and summarize the discussion.",
    "Did I get any emails from HR Operations?",
    "What are the action items from the 'Quarterly Review' email from Joni Sherman?",
    "Explain the error I'm getting in the undeliverable notices for emails to lidia.holloway@sockcop.onmicrosoft.com."
]

async def query_local_adk(client: httpx.AsyncClient, query: str) -> dict:
    url = "http://localhost:8005/api/chat"
    payload = {
        "message": query,
        "session_id": "test_comparison_session",
        "model": "gemini-3.6-flash"
    }
    t0 = time.time()
    try:
        resp = await client.post(url, json=payload, timeout=60.0)
        data = resp.json()
        return {
            "response": data.get("response", ""),
            "tools_called": [t.get("name") for t in data.get("tools_called", [])],
            "latency_s": round(time.time() - t0, 2)
        }
    except Exception as e:
        return {"error": str(e), "latency_s": round(time.time() - t0, 2)}

async def query_remote_adk(client: httpx.AsyncClient, query: str) -> dict:
    url = "http://localhost:8001/api/search"
    payload = {
        "query": query
    }
    t0 = time.time()
    response_text = ""
    tools_called = []
    try:
        async with client.stream("POST", url, json=payload, timeout=90.0) as response:
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data_str = line[6:].strip()
                    if not data_str:
                        continue
                    try:
                        evt = json.loads(data_str)
                        if evt.get("type") == "text":
                            response_text += evt.get("text", "")
                        elif evt.get("type") == "tool_call":
                            t_name = evt.get("tool", {}).get("name")
                            if t_name:
                                tools_called.append(t_name)
                    except Exception:
                        pass
        return {
            "response": response_text,
            "tools_called": tools_called,
            "latency_s": round(time.time() - t0, 2)
        }
    except Exception as e:
        return {"error": str(e), "latency_s": round(time.time() - t0, 2)}

async def main():
    async with httpx.AsyncClient() as client:
        comparison_results = []
        for idx, q in enumerate(QUESTIONS):
            q_id = f"Q{idx+1:03d}"
            print(f"[{q_id}] Querying: {q}")
            
            # Query local
            local_res = await query_local_adk(client, q)
            print(f"  Local latency: {local_res.get('latency_s')}s")
            
            # Query remote
            remote_res = await query_remote_adk(client, q)
            print(f"  Remote latency: {remote_res.get('latency_s')}s")
            
            comparison_results.append({
                "id": q_id,
                "query": q,
                "local": local_res,
                "remote": remote_res
            })
            # Brief cooldown to avoid rate limits
            await asyncio.sleep(2.0)
            
        # Write to report artifact
        artifact_dir = "/Users/jesusarguelles/.gemini/jetski/brain/0603c274-f3c2-4d01-b948-9cd747b6dba2"
        report_path = os.path.join(artifact_dir, "backend_comparison_report.md")
        
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("# Backends Parity Comparison Report\n\n")
            f.write(f"Generated at: {time.strftime('%Y-%m-%d %H:%M:%S UTC')}\n\n")
            f.write("This report compares the live execution of 10 golden questions on **Local ADK Agent** (port `8005`) and **Remote Production Agent** (port `8001`).\n\n")
            
            f.write("## Overview Metrics\n\n")
            f.write("| Metric | Local Agent (Port 8005) | Remote Agent (Port 8001) |\n")
            f.write("| :--- | :--- | :--- |\n")
            local_latencies = [r["local"].get("latency_s", 0) for r in comparison_results if "error" not in r["local"]]
            remote_latencies = [r["remote"].get("latency_s", 0) for r in comparison_results if "error" not in r["remote"]]
            avg_local = round(sum(local_latencies)/len(local_latencies), 2) if local_latencies else "N/A"
            avg_remote = round(sum(remote_latencies)/len(remote_latencies), 2) if remote_latencies else "N/A"
            f.write(f"| Average Latency | {avg_local}s | {avg_remote}s |\n")
            f.write(f"| Completed Runs | {len(local_latencies)}/10 | {len(remote_latencies)}/10 |\n\n")
            
            f.write("## Detailed Question Breakdown\n\n")
            for r in comparison_results:
                f.write(f"### {r['id']}: {r['query']}\n\n")
                f.write("#### 💻 Local Agent (Port 8005)\n")
                if "error" in r["local"]:
                    f.write(f"- **Error**: {r['local']['error']}\n")
                else:
                    f.write(f"- **Response**: {r['local']['response']}\n")
                    f.write(f"- **Tools Called**: `{r['local']['tools_called']}`\n")
                    f.write(f"- **Latency**: {r['local']['latency_s']}s\n")
                
                f.write("\n#### ☁️ Remote Agent (Port 8001)\n")
                if "error" in r["remote"]:
                    f.write(f"- **Error**: {r['remote']['error']}\n")
                else:
                    f.write(f"- **Response**: {r['remote']['response']}\n")
                    f.write(f"- **Tools Called**: `{r['remote']['tools_called']}`\n")
                    f.write(f"- **Latency**: {r['remote']['latency_s']}s\n")
                f.write("\n---\n\n")
                
        print(f"Parity report successfully written to {report_path}")

if __name__ == "__main__":
    asyncio.run(main())
