import os
import sys
import json
import time
import asyncio
import base64
import httpx
import inspect
import logging
from dotenv import load_dotenv

# Add current directory to sys.path so we can import src
sys.path.append(os.getcwd())

# Configure Logging
logging.basicConfig(level=logging.DEBUG)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)

from src import factset_core # Apply patches immediately
from src.smart_agent import create_smart_agent
from src.factset_core import check_factset_health

load_dotenv()

TOKEN_FILE = "factset_tokens.json"
FS_TOKEN_URL = "https://auth.factset.com/as/token.oauth2"
FS_CLIENT_ID = os.getenv("FS_CLIENT_ID")
FS_CLIENT_SECRET = os.getenv("FS_CLIENT_SECRET")

async def refresh_token(refresh_token_str):
    print("Refreshing token...")
    auth_str = f"{FS_CLIENT_ID}:{FS_CLIENT_SECRET}"
    b64_auth = base64.b64encode(auth_str.encode()).decode()
    
    headers = {
        "Authorization": f"Basic {b64_auth}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    payload = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token_str
    }
    
    async with httpx.AsyncClient() as client:
        resp = await client.post(FS_TOKEN_URL, data=payload, headers=headers)
        if resp.status_code == 200:
            return resp.json()
        else:
            print(f"Refresh failed: {resp.text}")
            return None

def get_function_schema(func):
    """Generates a JSON schema from a python function signature + docstring."""
    sig = inspect.signature(func)
    doc = (func.__doc__ or "").strip()
    
    parameters = {
        "type": "object",
        "properties": {},
        "required": []
    }
    
    for name, param in sig.parameters.items():
        param_type = "string" # Default
        if param.annotation == int: param_type = "integer"
        elif param.annotation == bool: param_type = "boolean"
        elif param.annotation == float: param_type = "number"
        elif param.annotation == dict: param_type = "object"
        elif param.annotation == list: param_type = "array"
        
        parameters["properties"][name] = {
            "type": param_type,
            "description": f"Parameter {name}" # Placeholder if not in docstring
        }
        
        if param.default == inspect.Parameter.empty:
            parameters["required"].append(name)
            
    return parameters

async def main():
    print("Starting MCP Tool Extraction...")
    
    # 1. Load Token
    token = None
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'r') as f:
            tokens = json.load(f)
            data = tokens.get("default_chat", {})
            token = data.get("token")
            refresh = data.get("refresh_token")
            expires_at = data.get("expires_at", 0)
            
            # Check Expiry
            if time.time() > (expires_at - 60):
                print("Token expired. Attempting refresh...")
                if refresh:
                    new_tokens = await refresh_token(refresh)
                    if new_tokens:
                        token = new_tokens.get("access_token")
                        # Update file
                        data["token"] = token
                        data["expires_at"] = time.time() + new_tokens.get("expires_in", 900)
                        if "refresh_token" in new_tokens:
                             data["refresh_token"] = new_tokens["refresh_token"]
                        tokens["default_chat"] = data
                        with open(TOKEN_FILE, 'w') as f_out:
                            json.dump(tokens, f_out, indent=2)
                        print("Token Refreshed and Saved.")
                    else:
                        print("Could not refresh token. Tools might be incomplete.")
                else:
                    print("No refresh token found. Tools might be incomplete.")

    if not token:
        print("WARNING: No valid token found. Using MOCK tools.")
    else:
        # Health Check (Skipping due to timeout issues, relying on agent internal retry)
        # print(f"Checking FactSet Health with token: {token[:10]}...")
        # is_healthy = await check_factset_health(token)
        # print(f"FactSet Health: {is_healthy}")
        pass

    # 2. Initialize Agent
    try:
        agent = await create_smart_agent(token, model_name="gemini-2.0-flash-exp")
    except Exception as e:
        print(f"Error creating agent: {e}")
        import traceback
        traceback.print_exc()
        return

    # 3. Extract Tools
    print(f"Found {len(agent.tools)} tools.")
    
    tool_schemas = []
    
    for tool in agent.tools:
        # Extract basic info
        t_info = {
            "name": tool.__name__,
            "description": (tool.__doc__ or "").strip(),
            "parameters": {}
        }
        
        # Try to get schema from ADK/MCP attributes
        schema = {}
        if hasattr(tool, "input_schema"):
            schema = tool.input_schema
        elif hasattr(tool, "func") and hasattr(tool.func, "input_schema"):
             schema = tool.func.input_schema
        elif hasattr(tool, "tool_def"): # Common ADK pattern
             schema = tool.tool_def.get("inputSchema", {})
        
        # Log available attributes for debugging if empty
        if not schema and "factset" in t_info["name"].lower():
            print(f"DEBUG: tool {t_info['name']} attributes: {dir(tool)}")
            if hasattr(tool, "__dict__"):
                print(f"DEBUG: tool dict: {tool.__dict__.keys()}")
        
        if schema:
            t_info["parameters"] = schema
        else:
            # Fallback for local
            t_info["parameters"] = get_function_schema(tool)
            
        tool_schemas.append(t_info)
        
    # 4. Save to JSON
    output_file = "mcp_tools_schema.json"
    with open(output_file, 'w') as f:
        json.dump(tool_schemas, f, indent=2)
        
    print(f"Successfully saved {len(tool_schemas)} tools to {output_file}")
    
    # Print names
    for t in tool_schemas:
        print(f"- {t['name']}")

if __name__ == "__main__":
    asyncio.run(main())
