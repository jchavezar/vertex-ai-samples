import sys
import json
import jwt

def decode_token_info():
    with open('/usr/local/google/home/jesusarguelles/IdeaProjects/vertex-ai-samples/antigravity/internal_components_portal/backend/nohup.out', 'r') as f:
        # just print a few latest lines from the server log
        lines = f.readlines()
        for line in lines[-100:]:
            pass # we'll look at logs by patching the backend instead

