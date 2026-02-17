import requests
import sys
import base64
import json

def decode_jwt(token: str):
    parts = token.split('.')
    if len(parts) >= 2:
        payload = parts[1]
        payload += '=' * (-len(payload) % 4)
        return json.loads(base64.urlsafe_b64decode(payload))
    return None

import logging
logging.basicConfig(filename='backend.log', level=logging.INFO)
# I will modify main.py to insert decode logic
