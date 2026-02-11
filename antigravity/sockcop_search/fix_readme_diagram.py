with open("generate_2076_readme.py", "r") as f:
    text = f.read()

diagram_payload = """
<br/>

## 🔐 Authentication Duality & Identity Mapping

> **REFERENCE ARCHITECTURE:** Ensure you review the official Google Cloud documentation before modifying the baseline security protocol.
> - [Configure Workload Identity Federation (WIF) with Entra ID](https://cloud.google.com/iam/docs/workload-identity-federation-with-deployment-pipelines)
> - [Vertex AI Search: Microsoft SharePoint connector](https://cloud.google.com/generative-ai-app-builder/docs/sharepoint-connector)

The following diagram illustrates the zero-trust authentication flow across Entra ID and Google Cloud via WIF, critical for **TOPOLOGY B**:

```mermaid
sequenceDiagram
    participant User as End User
    participant Frontend as Sockcop Search (React)
    participant EntraID as Microsoft Entra ID (Azure AD)
    participant GoogleSTS as Google STS (Token Exchange)
    participant VertexAI as Vertex AI Search (Discovery Engine API)
    
    User->>Frontend: Clicks "Sign in with Entra ID"
    Frontend->>EntraID: Redirects (auth URL + MS_APP_ID)
    EntraID-->>Frontend: Redirects back with `id_token` in hash
    Frontend->>Frontend: Extracts `id_token`
    
    Note over Frontend,GoogleSTS: Workload Identity Federation (WIF) Exchange
    Frontend->>GoogleSTS: POST /v1/token (audience, subject_token)
    GoogleSTS-->>Frontend: Returns short-lived `access_token`
    Frontend->>Frontend: Stores Google Token locally
    
    User->>Frontend: Enters query ("IT Support")
    Frontend->>VertexAI: POST .../servingConfigs/default_search:search
    Note over Frontend,VertexAI: Header: Authorization: Bearer <Google Token>
    VertexAI-->>Frontend: JSON payload (Results, Summaries, Extractive Snippets)
    
    Frontend->>Frontend: Parses structData & Sanitizes Snippets
    Frontend-->>User: Renders rich Grounded Search & AI Summary UI
```

"""

# Insert right before the TOPOLOGIES block
anchor = "<blockquote>\n  <p><b>ARCHITECTURE DUALITY:</b>"
if anchor in text:
    text = text.replace(anchor, diagram_payload + anchor)
    with open("generate_2076_readme.py", "w") as f:
        f.write(text)
    print("Successfully injected sequence diagram and WIF/SharePoint URLs.")
else:
    print("Anchor not found.")

