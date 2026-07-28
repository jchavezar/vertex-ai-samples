import os
import sys
import json

# Add the mcp_server directory to python path to import server
mcp_server_dir = "/Users/jesusarguelles/IdeaProjects/vertex-ai-samples/semiautonomous-agents/docparse-firestore-mcp/mcp_server"
sys.path.append(mcp_server_dir)

from server import mcp

def main():
    tools = mcp._tool_manager.list_tools()
    for tool in tools:
        if tool.name == "search_docs":
            print("--- search_docs Input Schema properties ---")
            print(json.dumps(tool.parameters, indent=2))

if __name__ == "__main__":
    main()
