import requests
import os
import base64
import json

token_path = "scratch/real_token.txt"
with open(token_path, "r") as f:
    # Aggressively strip multiple spacing or carriage returns
    token = f.read().replace(" ", "").replace("\n", "").replace("\r", "").strip()


parts = token.split(".")
print(f"Token Parts Count: {len(parts)}")
for i, p in enumerate(parts):
    print(f"Part {i} Length: {len(p)}")
    try:
        # Add padding back if missing
        padded = p + '=' * (-len(p) % 4)
        decoded = base64.urlsafe_b64decode(padded)
        print(f"Part {i} Base64: Valid")
        if i == 1:
            try:
                 payload_json = json.loads(decoded)
                 print(f"Part 1 Payload JSON Keys: {list(payload_json.keys())}")
                 print(f"Part 1 Subject/User: {payload_json.get('unique_name') or payload_json.get('sub')}")
            except Exception as e:
                 print(f"Part 1 JSON Parse Fail: {e}")
    except Exception as e:
        print(f"Part {i} Base64: Invalid ({e})")


headers = {"Authorization": f"Bearer {token}"}


# 1. Test me/drive (Baseline)
res_me = requests.get("https://graph.microsoft.com/v1.0/me/drive", headers=headers)
print(f"✅ me/drive Status: {res_me.status_code}")
if res_me.status_code != 200:
    print(f"Response: {res_me.text[:300]}")

# 2. Test Target Site with Hardcoded IDs into .env
site_id = "sockcop.sharepoint.com,33f4308c-c3f0-45d4-ac95-af66117261f8,692b0064-e281-41ee-9d24-d6af43f45058"
drive_id = "b!jDD0M_DD1EWsla9mEXJh-GQAK2mB4u5BnSTWr0P0UFhbq3cLMkLaRq4g5YaJ3Wvw"

url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drives/{drive_id}/items/root/children"
res_site = requests.get(url, headers=headers)
print(f"\n✅ Target Drive Status: {res_site.status_code}")
if res_site.status_code != 200:
    print(f"Response: {res_site.text[:300]}")
