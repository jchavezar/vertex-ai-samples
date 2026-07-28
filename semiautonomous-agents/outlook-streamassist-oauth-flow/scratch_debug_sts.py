import os
import requests
import json
from dotenv import load_dotenv

load_dotenv(dotenv_path="backend/.env")

WIF_POOL_ID = os.environ.get("WIF_POOL_ID")
WIF_PROVIDER_ID = os.environ.get("WIF_PROVIDER_ID")

url = "https://sts.googleapis.com/v1/token"
body = {
    "audience": f"//iam.googleapis.com/locations/global/workforcePools/{WIF_POOL_ID}/providers/{WIF_PROVIDER_ID}",
    "grantType": "urn:ietf:params:oauth:grant-type:token-exchange",
    "requestedTokenType": "urn:ietf:params:oauth:token-type:access_token",
    "scope": "https://www.googleapis.com/auth/cloud-platform",
    "subjectToken": "dummy_token_header.dummy_token_payload.dummy_token_signature",
    "subjectTokenType": "urn:ietf:params:oauth:token-type:jwt",
}

print(f"Audience: {body['audience']}")
resp = requests.post(url, json=body)
print(f"Status Code: {resp.status_code}")
print(f"Response: {resp.text}")
