import requests
import json
import base64

def decode_jwt(token: str):
    parts = token.split('.')
    if len(parts) >= 2:
        payload = parts[1]
        payload += '=' * (-len(payload) % 4)
        return json.loads(base64.urlsafe_b64decode(payload))
    return None

import builtins
