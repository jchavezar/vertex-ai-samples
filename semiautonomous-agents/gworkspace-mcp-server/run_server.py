import os
import subprocess

env = os.environ.copy()
env["GWORKSPACE_SECRET_ID"] = "gworkspace-mcp-tokens"
env["GOOGLE_CLOUD_PROJECT"] = "vtxdemos"
env["MCP_TRANSPORT"] = "sse"
env["PORT"] = "8085"

# Inject Client ID and Secret found from Cloud Run service
env["GOOGLE_CLIENT_ID"] = os.environ.get("GOOGLE_CLIENT_ID", "")
env["GOOGLE_CLIENT_SECRET"] = os.environ.get("GOOGLE_CLIENT_SECRET", "")

print("Starting server with Secret Manager integration...")
subprocess.run([".venv/bin/python", "server.py"], env=env)
