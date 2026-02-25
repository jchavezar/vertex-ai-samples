import json
import time

TOKEN_FILE = "factset_tokens.json"
SESSION_ID = "repro_hang"

try:
    with open(TOKEN_FILE, 'r') as f:
        tokens = json.load(f)
except FileNotFoundError:
    tokens = {}

tokens[SESSION_ID] = {
    "token": "mock_token_for_testing",
    "refresh_token": "mock_refresh",
    "expires_at": time.time() + 3600,
    "created_at": time.time()
}

with open(TOKEN_FILE, 'w') as f:
    json.dump(tokens, f, indent=2)

print(f"Injected mock token for {SESSION_ID}")
