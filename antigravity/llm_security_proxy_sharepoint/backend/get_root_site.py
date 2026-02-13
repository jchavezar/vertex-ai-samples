import requests
import json
import os
from dotenv import load_dotenv
import msal

load_dotenv(dotenv_path="../.env")

tenant_id = os.getenv("TENANT_ID")
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

options = {"tenant_id": tenant_id, "client_id": client_id, "client_secret": client_secret}
authority = f"https://login.microsoftonline.com/{options['tenant_id']}"
app = msal.ConfidentialClientApplication(
    options["client_id"],
    authority=authority,
    client_credential=options["client_secret"]
)

result = app.acquire_token_silent(["https://graph.microsoft.com/.default"], account=None)
if not result:
    result = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])

token = result["access_token"]
headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

print("Getting Root Site ID for the tenant...")

url = "https://graph.microsoft.com/v1.0/sites/root"
res = requests.get(url, headers=headers)
site_data = res.json()
print("Root Site Data:")
print(json.dumps(site_data, indent=2))
print(f"\n=> ROOT SITE_ID: {site_data.get('id')}")

