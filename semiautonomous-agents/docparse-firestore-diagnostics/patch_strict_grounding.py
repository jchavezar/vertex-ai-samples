import google.auth
import google.auth.transport.requests
import requests

def patch_connector(connector_id):
    creds, project = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    auth_req = google.auth.transport.requests.Request()
    creds.refresh(auth_req)
    
    proj_num = "254356041555"
    headers = {
        "Authorization": f"Bearer {creds.token}",
        "Content-Type": "application/json",
        "X-Goog-User-Project": proj_num
    }
    
    url = f"https://discoveryengine.googleapis.com/v1alpha/projects/{proj_num}/locations/global/collections/{connector_id}/dataConnector"
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        print(f"Error fetching connector {connector_id}: {r.status_code} - {r.text}")
        return
    
    orig = r.json()
    action_config = orig.get("actionConfig", {})
    if not action_config:
        print(f"Connector {connector_id} has no actionConfig!")
        return
        
    strict_instructions = (
        "CRITICAL SYSTEM DIRECTIVE: You are a strict document-grounded assistant. "
        "For every single user query without exception, you MUST first call the `search_docs` tool with the query verbatim. "
        "Formulate your response based SOLELY on the returned chunks, and provide precise page-level citations and "
        "HTTPS grounding URLs to refer back to the original PDF documents.\n\n"
        "STRICT NO-GROUNDING REFUSAL CLAUSE: If the `search_docs` tool returns empty results, or if the returned chunks "
        "do not contain the direct answer to the user's question, you MUST politely and clearly state: "
        "'I cannot find the answer to your question in the provided documents.' "
        "You are strictly and absolutely forbidden from answering using your pre-trained weights, general knowledge, "
        "or external reasoning. Under no circumstances should you generate an answer from general knowledge if the "
        "search results do not directly ground it."
    )
    
    # We update ONLY the nested actionConfig structure
    action_config["actionParams"]["mcp_agent_instructions"] = strict_instructions
    
    patch_body = {
        "name": orig["name"],
        "actionConfig": action_config
    }
    
    # Use nested camelCase update mask
    patch_url = f"{url}?updateMask=actionConfig.actionParams.mcp_agent_instructions"
    print(f"Patching connector {connector_id} with strict grounding instructions via nested mask...")
    patch_r = requests.patch(patch_url, headers=headers, json=patch_body)
    print(f"Patch Response for {connector_id} ({patch_r.status_code}):")
    try:
        print(patch_r.json())
    except:
        print(patch_r.text)

def main():
    connectors = ["docparse-firestore-mcp-1780165632", "docparse-firestore-mcp-1780162342"]
    for conn in connectors:
        patch_connector(conn)

if __name__ == "__main__":
    main()
