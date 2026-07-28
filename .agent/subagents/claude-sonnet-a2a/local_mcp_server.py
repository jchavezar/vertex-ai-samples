import os
import sys
import subprocess
import logging
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("local_mcp_server")

mcp = FastMCP(
    "repo-manager-mcp",
    transport_security=TransportSecuritySettings(enable_dns_rebinding_protection=False)
)

REPO_ROOT = "/Users/jesusarguelles/IdeaProjects/vertex-ai-samples"

def _resolve_path(rel_path: str) -> str:
    # Ensure it stays inside the repo
    abs_path = os.path.abspath(os.path.join(REPO_ROOT, rel_path))
    if not abs_path.startswith(REPO_ROOT):
        raise ValueError("Access outside repository path is denied.")
    return abs_path

@mcp.tool()
def list_directory(relative_path: str = "") -> str:
    """Lists files and directories under the specified relative path in the repository."""
    try:
        path = _resolve_path(relative_path)
        items = os.listdir(path)
        return "\n".join(items)
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def read_file(relative_path: str) -> str:
    """Reads the full content of a file in the repository."""
    try:
        path = _resolve_path(relative_path)
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def write_file(relative_path: str, content: str) -> str:
    """Writes content to a file in the repository (creates or overwrites it)."""
    try:
        path = _resolve_path(relative_path)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Successfully wrote to {relative_path}"
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def execute_command(command: str) -> str:
    """Runs a shell command inside the repository root directory."""
    try:
        # Run command in repo root
        result = subprocess.run(
            command,
            shell=True,
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=60
        )
        output = []
        if result.stdout:
            output.append("STDOUT:\n" + result.stdout)
        if result.stderr:
            output.append("STDERR:\n" + result.stderr)
        return "\n".join(output) if output else "Command completed with no output."
    except Exception as e:
        return f"Error executing command: {str(e)}"

# Expose SSE ASGI application
app = mcp.sse_app()

if __name__ == "__main__":
    import uvicorn
    # Default to port 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)
