import contextvars

user_token_var = contextvars.ContextVar('user_token', default=None)

def get_user_token():
    return user_token_var.get()

def set_user_token(token: str):
    user_token_var.set(token)
