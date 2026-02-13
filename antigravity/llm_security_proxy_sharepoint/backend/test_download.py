import requests
import json
import os
from dotenv import load_dotenv
import msal

load_dotenv(dotenv_path="../.env")

tenant_id = os.getenv("TENANT_ID")
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
drive_id = os.getenv("DRIVE_ID")
site_id = os.getenv("SITE_ID")

options = {"tenant_id": tenant_id, "client_id": client_id, "client_secret": client_secret}
authority = f"https://login.microsoftonline.com/{options['tenant_id']}"
app = msal.ConfidentialClientApplication(
    options["client_id"], authority=authority, client_credential=options["client_secret"])

result = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
token = result["access_token"]
headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

# 05_MA_Due_Diligence_Project_Starlight.pdf 
item_id = "01XOLSUZSAWNVT5NNTTRHLDDERKOTRV2D2"
print(f"Testing direct download info for item {item_id}...")

url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drives/{drive_id}/items/{item_id}?$expand=listItem"
res = requests.get(url, headers=headers)
print(f"Status: {res.status_code}")
if res.ok:
    print(res.json().get('@microsoft.graph.downloadUrl'))
else:
    print(res.text)

print("\nTesting Drives endpoint bypass...")
url2 = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/items/{item_id}?$expand=listItem"
res2 = requests.get(url2, headers=headers)
print(f"Status2: {res2.status_code}")
if res2.ok:
    print(res2.json().get('@microsoft.graph.downloadUrl'))
else:
    print(res2.text)
