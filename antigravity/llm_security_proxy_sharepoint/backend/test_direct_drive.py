import requests
import os
from dotenv import load_dotenv
import msal

load_dotenv(dotenv_path="../.env")

tenant_id = os.getenv("TENANT_ID")
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
drive_id = os.getenv("DRIVE_ID")

options = {"tenant_id": tenant_id, "client_id": client_id, "client_secret": client_secret}
authority = f"https://login.microsoftonline.com/{options['tenant_id']}"
app = msal.ConfidentialClientApplication(
    options["client_id"], authority=authority, client_credential=options["client_secret"])

result = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
token = result["access_token"]
headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

print(f"Testing direct drive fetch for {drive_id}...")
url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}"
res = requests.get(url, headers=headers)
print(f"Status: {res.status_code}")
if res.ok:
    print(res.json().get('webUrl'))
else:
    print(res.text)

