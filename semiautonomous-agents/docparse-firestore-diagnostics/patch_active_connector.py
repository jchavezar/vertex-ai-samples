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
    
    # 1. Fetch current connector
    url = f"https://discoveryengine.googleapis.com/v1alpha/projects/{proj_num}/locations/global/collections/{connector_id}/dataConnector"
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        print(f"Error fetching connector: {r.status_code} - {r.text}")
        return
        
    orig = r.json()
    action_config = orig["actionConfig"]
    
    # Aggressive descriptions
    aggressive_server_description = (
        "CRITICAL SYSTEM DIRECTIVE: Call search_docs for EVERY user question or search. General knowledge is FORBIDDEN."
    )
    
    aggressive_agent_instructions = (
        "CRITICAL SYSTEM DIRECTIVE: You are a strictly document-grounded assistant. For every single user query "
        "without exception, you MUST first call the `search_docs` tool with the query verbatim. Even for highly generic "
        "questions (like 'what is the metaverse?', 'what is the multiverse?'), you MUST call `search_docs` to check "
        "our database. Formulate your response based SOLELY on the returned chunks.\n\n"
        "CITATION DISCIPLINE AND MARKDOWN GROUNDING REQUIREMENTS:\n"
        "1. For every claim, fact, or definition you provide, you MUST include a page-level citation formatted EXACTLY as a clickable Markdown link using the 'pdf_name', 'page' number, and 'https_pdf_url' fields from the tool's search results.\n"
        "2. The clickable citation format MUST be: `[pdf_name - Page X](https_pdf_url)` (e.g., [Accenture-Metaverse-Evolution-Before-Revolution.pdf - Page 4](https://storage.googleapis.com/vtxdemos-docparse-in/Accenture-Metaverse-Evolution-Before-Revolution.pdf#page=4)).\n"
        "3. NEVER use general citation labels like [1] or plain text. Every citation must be a fully clickable Markdown link with the exact URL provided in 'https_pdf_url'.\n"
        "4. NEVER invent or hallucinate document names, page numbers, or URLs. If a source or page is not returned in the tool results, you MUST NOT cite it or mention it.\n"
        "5. If no chunks are found or search returns empty, respond EXACTLY with: 'I cannot find the answer to your question in the provided documents.'"
    )
    
    action_config["actionParams"]["mcp_server_description"] = aggressive_server_description
    action_config["actionParams"]["mcp_agent_instructions"] = aggressive_agent_instructions
    action_config["actionParams"]["auth_type"] = "NONE"
    action_config["actionParams"].pop("auth_uri", None)
    action_config["actionParams"].pop("token_uri", None)
    action_config["actionParams"].pop("scopes", None)
    action_config["actionParams"].pop("client_id", None)
    action_config["actionParams"].pop("client_secret", None)
    
    patch_body = {
        "name": orig["name"],
        "actionConfig": action_config
    }
    
    # Patch the DataConnector
    patch_url = f"{url}?updateMask=actionConfig"
    print("Patching active connector actionConfig...")
    patch_r = requests.patch(patch_url, headers=headers, json=patch_body)
    print(f"Patch Response ({patch_r.status_code}):")
    try:
        print(json.dumps(patch_r.json(), indent=2))
    except:
        print(patch_r.text)

if __name__ == "__main__":
    main()
