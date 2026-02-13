import os
import json
import base64
from dotenv import load_dotenv
import msal

load_dotenv(dotenv_path="../.env")

tenant_id = os.getenv("TENANT_ID")
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

app = msal.ConfidentialClientApplication(
    client_id, authority=f"https://login.microsoftonline.com/{tenant_id}", client_credential=client_secret)

result = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
if "access_token" in result:
    token = result["access_token"]
    print("Token Acquired. Decoding...")
    parts = token.split(".")
    if len(parts) >= 2:
        payload = parts[1]
        # pad to multiple of 4
        payload += "=" * ((4 - len(payload) % 4) % 4)
        print(json.dumps(json.loads(base64.urlsafe_b64decode(payload)), indent=2))
else:
    print("No token")
    print(result)
