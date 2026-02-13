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

print("Getting details for Drive b!BHsWCCxPaUS03HCxu6-PIcmJPN90079KlSeyLCi5bjUIyP8ZqZLLS40PQVQ3p0dn...")

url = "https://graph.microsoft.com/v1.0/drives/b!BHsWCCxPaUS03HCxu6-PIcmJPN90079KlSeyLCi5bjUIyP8ZqZLLS40PQVQ3p0dn"
res = requests.get(url, headers=headers)
drive_data = res.json()
print("Drive Data:")
print(json.dumps(drive_data, indent=2))

if 'owner' in drive_data and 'group' in drive_data['owner']:
   group_id = drive_data['owner']['group']['id']
   print(f"\nFetching site for Group ID: {group_id}")
   site_res = requests.get(f"https://graph.microsoft.com/v1.0/groups/{group_id}/sites/root", headers=headers)
   site = site_res.json()
   print("Site Data:")
   print(json.dumps(site, indent=2))
   print(f"\n=> NEW SITE_ID: {site.get('id')}")

