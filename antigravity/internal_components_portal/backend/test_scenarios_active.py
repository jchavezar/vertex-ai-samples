import requests
import json
import time

URL = "http://localhost:8008/chat"
TOKEN = "test_token_internal" # Placeholder, backend handles null/None for testing if needed

def run_scenario(name, router_mode, prompt):
    print(f"\n--- TESTING SCENARIO: {name} ---")
    print(f"Router Mode: {router_mode}")
    print(f"Prompt: {prompt}")
    
    headers = {
        "Content-Type": "application/json",
        "X-User-Token": TOKEN
    }
    
    payload = {
        "messages": [{"content": prompt, "role": "user"}],
        "model": "gemini-3-flash-preview",
        "routerMode": router_mode
    }
    
    try:
        start_time = time.time()
        response = requests.post(URL, headers=headers, json=payload, stream=True, timeout=60)
        response.raise_for_status()
        
        full_text = ""
        telemetry = {}
        
        for line in response.iter_lines():
            if line:
                chunk = line.decode('utf-8')
                if chunk.startswith("0:"):
                    # Text usually comes as 0:"content"
                    content = chunk[3:-1] if chunk.endswith('"') else chunk[3:]
                    # Unescape newlines
                    content = content.replace('\\n', '\n')
                    full_text += content
                elif chunk.startswith("2:"):
                    # Data comes as 2:[{"type":...}]
                    data_str = chunk[2:]
                    try:
                        data_list = json.loads(data_str)
                        for data in data_list:
                            if data.get("type") == "telemetry":
                                telemetry = data
                            elif data.get("type") == "status":
                                print(f"  [Status]: {data.get('message')}")
                    except json.JSONDecodeError:
                        pass
        
        duration = time.time() - start_time
        print(f"Result (Masked): {full_text[:200]}...")
        print(f"Latency Steps Breakdown:")
        if telemetry:
            for step in telemetry.get("data", []):
                print(f"  - {step['step']}: {step['duration_s']}s")
            
            print(f"Reasoning Trace Analysis:")
            for r in telemetry.get("reasoning", []):
                if "[Router]" in r or "[Discovery Engine]" in r or "[Redaction]" in r or "[Action]" in r:
                    print(f"    {r[:100]}...")
        
        print(f"Total Response Time: {round(duration, 2)}s")
        return full_text, telemetry
    except Exception as e:
        print(f"ERROR in {name}: {e}")
        return None, None

if __name__ == "__main__":
    # Scenario 1: All MCP (Direct) - Search query
    run_scenario("All MCP (Direct) - Search", "all_mcp", "What is the compensation for CFO Jennifer Anne Walsh?")
    
    # Scenario 2: GE + MCP (Router) - Search query (Routes to GE)
    run_scenario("GE + MCP (Router) - Search", "ge_mcp", "What are the latest SLA terms found in documents?")
    
    # Scenario 3: GE + MCP (Router) - Action query (Routes to MCP)
    run_scenario("GE + MCP (Router) - Action", "ge_mcp", "Please write a summary of the compliance docs and save it as a new file named compliance_summary.pdf")
