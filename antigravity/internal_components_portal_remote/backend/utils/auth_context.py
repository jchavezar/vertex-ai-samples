import contextvars
import os

user_token_var = contextvars.ContextVar('user_token', default=None)
user_id_token_var = contextvars.ContextVar('user_id_token', default=None)

def get_user_token():
    token = user_token_var.get()
    if not token:
        # Fallback for MCP server running in separate process
        return os.environ.get("USER_TOKEN")
    return token

def set_user_token(token: str):
    user_token_var.set(token)

def get_user_id_token():
    token = user_id_token_var.get()
    if not token:
        return os.environ.get("USER_ID_TOKEN")
    return token

def set_user_id_token(token: str):
    user_id_token_var.set(token)
