import requests
import json
import os
from dotenv import load_dotenv
import msal

# Load env variables from the parent directory
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

if "access_token" in result:
    token = result["access_token"]
else:
    print("Authentication failed.")
    exit(1)

headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

print("Searching for Sites matching 'Financial'...")
sites_url = "https://graph.microsoft.com/v1.0/sites?search=Financial"
res = requests.get(sites_url, headers=headers)
sites = res.json().get('value', [])
for site in sites:
    print(f"\nSite: {site.get('displayName')} (ID: {site.get('id')})")
    
    # Get drives for this site
    drives_url = f"https://graph.microsoft.com/v1.0/sites/{site.get('id')}/drives"
    drives_res = requests.get(drives_url, headers=headers)
    drives = drives_res.json().get('value', [])
    for drive in drives:
         print(f"  -> Drive: {drive.get('name')} (ID: {drive.get('id')})")

print("\n\nSearching for Drives anywhere matching 'Financial'...")
all_drives_url = "https://graph.microsoft.com/v1.0/drives?$select=id,name,description,webUrl&$search=\"Financial\""
all_drives_res = requests.get(all_drives_url, headers=headers)
drives = all_drives_res.json().get('value', [])
for d in drives:
   print(f"Global Drive: {d.get('name')} (ID: {d.get('id')}) -- URL: {d.get('webUrl')}")


