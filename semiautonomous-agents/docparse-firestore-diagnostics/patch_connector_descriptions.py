import google.auth
import google.auth.transport.requests
import requests
import json

def main():
    creds, project = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    auth_req = google.auth.transport.requests.Request()
    creds.refresh(auth_req)
    
    proj_num = "254356041555"
    connector_id = "docparse-firestore-mcp-1780165632"
    
    headers = {
        "Authorization": f"Bearer {creds.token}",
        "Content-Type": "application/json",
        "X-Goog-User-Project": proj_num
    }
    
    # 1. Fetch current connector config
    url = f"https://discoveryengine.googleapis.com/v1alpha/projects/{proj_num}/locations/global/collections/{connector_id}/dataConnector"
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        print(f"Error fetching connector: {r.status_code} - {r.text}")
        return
        
    orig = r.json()
    action_config = orig["actionConfig"]
    dynamic_tools = orig.get("dynamicTools", [])
    
    # Aggressive server and tool descriptions
    aggressive_server_description = (
        "Firestore-backed RAG system for Docparse. This is the MANDATORY and EXCLUSIVE database for "
        "all user queries, general knowledge, definitions, and document questions. You MUST call this "
        "connector to retrieve the required internal groundings before answering any user question."
    )
    
    aggressive_tool_description = (
        "CRITICAL DIRECTIVE: Call this tool for EVERY single query, term, definition, or question without "
        "exception. Even for highly general questions like 'what is the metaverse?', 'what is the multiverse?', "
        "or definitions/explanations, you MUST call this tool first. Answering using pre-trained weights or general "
        "knowledge is STRICTLY FORBIDDEN. This tool searches the exclusive Firestore PDF database for Accenture "
        "Technology Vision 2022 and other documents.\n\n"
        "Args:\n"
        "    query: The exact user question or search term verbatim.\n"
        "    top_k: Number of chunks (default 5)."
    )
    
    action_config["actionParams"]["mcp_server_description"] = aggressive_server_description
    
    # Find and update search_docs tool description
    for tool in dynamic_tools:
        if tool.get("name") == "search_docs":
            tool["description"] = aggressive_tool_description
            print("Updated search_docs description in dynamicTools.")
            
    # Build patch body
    patch_body = {
        "name": orig["name"],
        "actionConfig": action_config,
        "dynamicTools": dynamic_tools
    }
    
    # Patch the DataConnector
    patch_url = f"{url}?updateMask=actionConfig,dynamicTools"
    print("Patching connector actionConfig and dynamicTools...")
    patch_r = requests.patch(patch_url, headers=headers, json=patch_body)
    print(f"Patch Response ({patch_r.status_code}):")
    try:
        print(json.dumps(patch_r.json(), indent=2))
    except:
        print(patch_r.text)

if __name__ == "__main__":
    main()
