import json
import os
import sys

TOKEN_FILE = "factset_tokens.json"

def update_token():
    print("Paste your FactSet REFRESH TOKEN below and press Enter:")
    new_refresh_token = input().strip()
    
    if not new_refresh_token:
        print("Error: No token entered.")
        return

    # Load existing or create new
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'r') as f:
            try:
                tokens = json.load(f)
            except:
                tokens = {}
    else:
        tokens = {}

    # Update all relevant sessions or just default? 
    # Let's update default_chat and benchmark_chat as they are key.
    # Actually, let's just make it valid for any new session by updating 'default_chat' which is often used as a template,
    # or ensuring main.py picks it up. `get_valid_factset_token` checks `factset_tokens.get(session_id)`.
    
    # We will update 'default_chat'
    ts = tokens.get("default_chat", {})
    ts["refresh_token"] = new_refresh_token
    # Force immediate refresh by setting expires_at to 0
    ts["expires_at"] = 0 
    tokens["default_chat"] = ts
    
    # Also update benchmark_chat just in case
    ts_bench = tokens.get("benchmark_chat", {})
    ts_bench["refresh_token"] = new_refresh_token
    ts_bench["expires_at"] = 0
    tokens["benchmark_chat"] = ts_bench

    with open(TOKEN_FILE, 'w') as f:
        json.dump(tokens, f, indent=2)

    print(f"\nSUCCESS: Token updated in {TOKEN_FILE}.")
    print("The system will automatically use this to generate a fresh access token on next run.")

if __name__ == "__main__":
    # Allow argument pass if user prefers: python3 update_token.py <token>
    if len(sys.argv) > 1:
        # manual mode not implemented to avoid cli history logging of secrets, standard input is safer
        pass
    
    update_token()
