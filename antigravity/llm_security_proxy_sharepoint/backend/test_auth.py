import requests
import json
import os
from dotenv import load_dotenv
import msal

load_dotenv(dotenv_path="../.env")

tenant_id = os.getenv("TENANT_ID")
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
# Strip quotes if they were pasted into .env
if client_secret and client_secret.startswith('"') and client_secret.endswith('"'):
    client_secret = client_secret[1:-1]

options = {"tenant_id": tenant_id, "client_id": client_id, "client_secret": client_secret}
authority = f"https://login.microsoftonline.com/{options['tenant_id']}"
app = msal.ConfidentialClientApplication(
    options["client_id"], authority=authority, client_credential=options["client_secret"])

result = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])

if "access_token" in result:
    print("Token Acquired.")
    token = result["access_token"]
else:
    print("Failed to acquire token:")
    print(json.dumps(result, indent=2))
    exit(1)

headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

print("\nTesting user access...")
res = requests.get("https://graph.microsoft.com/v1.0/users", headers=headers)
print(f"Users Status: {res.status_code}")
if "error" in res.json():
    print(res.json()["error"])
