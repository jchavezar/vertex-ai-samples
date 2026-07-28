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
    
    # Updated prompt instructions with specific page and pdf_name usage guidelines
    new_instructions = (
        "CRITICAL SYSTEM DIRECTIVE: You are a strictly document-grounded assistant. For every single user query "
        "without exception, you MUST first call the `search_docs` tool. Even for highly generic questions (like "
        "'what is the metaverse?', 'what is the multiverse?'), you MUST call `search_docs` to check our database. "
        "Formulate your response based SOLELY on the returned chunks.\n\n"
        "PARAMETER USAGE INSTRUCTIONS:\n"
        "1. For exact page queries or lookups (e.g., 'Who is quoted on page 9 of the Accenture report?', 'What is on page 4?'), "
        "you MUST pass the target page number verbatim in the `page` parameter (e.g., '9' or 'ix') and, if known, the document "
        "name in the `pdf_name` parameter (e.g., 'accenture'). This bypasses vector search and executes a direct, highly "
        "accurate lookup.\n"
        "2. For general semantic questions, pass the user query verbatim to the `query` parameter and leave `page` empty.\n\n"
        "CITATION DISCIPLINE AND MARKDOWN GROUNDING REQUIREMENTS:\n"
        "1. For every claim, fact, or definition you provide, you MUST include a page-level citation formatted EXACTLY as a clickable Markdown link using the 'pdf_name', 'page' number, and 'https_pdf_url' fields from the tool's search results.\n"
        "2. The clickable citation format MUST be: `[pdf_name - Page X](https_pdf_url)` (e.g., [Accenture-Metaverse-Evolution-Before-Revolution.pdf - Page 4](https://storage.googleapis.com/vtxdemos-docparse-in/Accenture-Metaverse-Evolution-Before-Revolution.pdf#page=4)).\n"
        "3. NEVER use general citation labels like [1] or plain text. Every citation must be a fully clickable Markdown link with the exact URL provided in 'https_pdf_url'.\n"
        "4. NEVER invent or hallucinate document names, page numbers, or URLs. If a source or page is not returned in the tool results, you MUST NOT cite it or mention it.\n"
        "5. If no chunks are found or search returns empty, respond EXACTLY with: 'I cannot find the answer to your question in the provided documents.'"
    )
    
    action_config["actionParams"]["mcp_agent_instructions"] = new_instructions
    
    # Build clean patch body preserving OAuth and connector settings
    # Build clean patch body with ONLY the changed instruction path to bypass OAuth validations
    patch_body = {
        "name": orig["name"],
        "actionConfig": {
            "actionParams": {
                "mcp_agent_instructions": new_instructions
            }
        }
    }
    
    # Patch the DataConnector back to trigger dynamic sync
    patch_url = f"{url}?updateMask=actionConfig.actionParams.mcp_agent_instructions"
    print("Patching active connector actionConfig to trigger dynamic tool sync...")
    patch_r = requests.patch(patch_url, headers=headers, json=patch_body)
    print(f"Patch Response ({patch_r.status_code}):")
    try:
        res = patch_r.json()
        if patch_r.status_code == 200:
            print("Sync and patch complete! Current dynamic tools list:")
            print(json.dumps(res.get("dynamicTools"), indent=2))
        else:
            print("Error Response Body:")
            print(json.dumps(res, indent=2))
    except:
        print(patch_r.text)

if __name__ == "__main__":
    main()
