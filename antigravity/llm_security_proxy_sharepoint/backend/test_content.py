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
headers = {"Authorization": f"Bearer {token}"}

item_id = "01XOLSUZSAWNVT5NNTTRHLDDERKOTRV2D2"
print(f"Testing direct /content fetch for {item_id}...")

url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drives/{drive_id}/items/{item_id}/content"
res = requests.get(url, headers=headers)
print(f"Status: {res.status_code}")
if res.ok:
    print(f"Downloaded bytes: {len(res.content)}")
else:
    print(res.text)

print("\nTesting Drives bypass /content fetch...")
url2 = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/items/{item_id}/content"
res2 = requests.get(url2, headers=headers)
print(f"Status2: {res2.status_code}")
if res2.ok:
    print(f"Downloaded bytes: {len(res2.content)}")
else:
    print(res2.text)

