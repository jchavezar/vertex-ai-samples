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

print("Listing files in Drive ID b!BHsWCCxPaUS03HCxu6-PIcmJPN90079KlSeyLCi5bjUIyP8ZqZLLS40PQVQ3p0dn ...")

url = "https://graph.microsoft.com/v1.0/drives/b!BHsWCCxPaUS03HCxu6-PIcmJPN90079KlSeyLCi5bjUIyP8ZqZLLS40PQVQ3p0dn/root/children"
res = requests.get(url, headers=headers)
files = res.json().get('value', [])
for f in files:
    print(f"- {f.get('name')} (ID: {f.get('id')})")


