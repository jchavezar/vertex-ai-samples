import requests
import jwt
import base64
import json

token_path = "scratch/real_token.txt"
with open(token_path, "r") as f:
    token = f.read().replace(" ", "").replace("\n", "").replace("\r", "").strip()

# 1. Get header to find kid
parts = token.split(".")
header_p = parts[0]
padded_header = header_p + '=' * (-len(header_p) % 4)
header = json.loads(base64.urlsafe_b64decode(padded_header))
kid = header.get("kid")
print(f"Header kid: {kid}")

# 2. Fetch MS keys
# For common endpoint or tenant specific
payload_p = parts[1]
padded_payload = payload_p + '=' * (-len(payload_p) % 4)
payload = json.loads(base64.urlsafe_b64decode(padded_payload))
tid = payload.get("tid")
print(f"Tenant ID: {tid}")

keys_url = f"https://login.microsoftonline.com/{tid}/discovery/keys"
res = requests.get(keys_url)
keys = res.json().get("keys", [])
if not keys:
    # Try common
    res = requests.get("https://login.microsoftonline.com/common/discovery/keys")
    keys = res.json().get("keys", [])


# 3. Find matching key
matching_key = None
for k in keys:
    if k.get("kid") == kid:
        matching_key = k
        break

if not matching_key:
    print("❌ No matching key found for kid!")
    exit(1)

print("✅ Found matching key.")

# 4. Verify Signature using PyJWT
# Needs cryptography installed for RSA
try:
    public_key = jwt.algorithms.RSAAlgorithm.from_jwk(matching_key)
    # Use aud=Microsoft Graph if specified
    payload_decoded = jwt.decode(
        token,
        public_key,
        algorithms=["RS256"],
        audience="00000003-0000-0000-c000-000000000000"
    )
    print("✅ Local Signature Verification SUCCEEDED!")
    print(f"Verified Scope: {payload_decoded.get('scp')}")
except Exception as e:
    print(f"❌ Local Signature Verification FAILED: {e}")
