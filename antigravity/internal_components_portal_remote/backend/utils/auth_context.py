import contextvars
import os

user_token_var = contextvars.ContextVar('user_token', default=None)
user_id_token_var = contextvars.ContextVar('user_id_token', default=None)

# File-based caching for isolated environments
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LOCAL_ONLY_DIR = os.path.join(PROJECT_ROOT, "local_only")
STS_TOKEN_FILE = os.path.join(LOCAL_ONLY_DIR, "sts_token.txt")
ID_TOKEN_FILE = os.path.join(LOCAL_ONLY_DIR, "id_token.txt")

# Ensure local_only exists
os.makedirs(LOCAL_ONLY_DIR, exist_ok=True)

def get_user_token():
    token = user_token_var.get()
    if not token:
        if os.path.exists(STS_TOKEN_FILE):
            try:
                with open(STS_TOKEN_FILE, "r") as f:
                    token = f.read().strip()
                    if token:
                        return token
            except:
                pass
        return os.environ.get("USER_TOKEN")
    return token

def set_user_token(token: str):
    user_token_var.set(token)
    if token:
        try:
            with open(STS_TOKEN_FILE, "w") as f:
                f.write(token)
        except:
            pass

def get_user_id_token():
    token = user_id_token_var.get()
    if not token:
        if os.path.exists(ID_TOKEN_FILE):
            try:
                with open(ID_TOKEN_FILE, "r") as f:
                    token = f.read().strip()
                    if token:
                        return token
            except:
                pass
        return os.environ.get("USER_ID_TOKEN")
    return token

def set_user_id_token(token: str):
    user_id_token_var.set(token)
    if token:
        try:
            with open(ID_TOKEN_FILE, "w") as f:
                f.write(token)
        except:
            pass
