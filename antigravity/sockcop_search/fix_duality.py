import re

with open("generate_2076_readme.py", "r") as f:
    text = f.read()

warning_block = """<br/>

> [!WARNING]  
> **CRITICAL ARCHITECTURE DISAMBIGUATION: THE DUAL-APP TOPOLOGY**  
> 
> Due to the complexity of these integrations, do not conflate the Entra ID application required for **Frontend SSO** with the application required for **Backend Indexing**. They are distinct entities with entirely different routing parameters:
> 
> * **1. App A (Frontend / WIF)**: Authenticates the end-user accessing the React frontend. Callback URL is typically `http://localhost:5173`. Grants Standard OIDC (`profile`, `email`, `openid`). Controls access to the GCP Workload Identity Federation.
> * **2. App B (Backend / Datastore Connector)**: Authorizes Vertex AI to crawl and index the corporate SharePoint repository in the background. Callback URL is the specific `https://vertexaisearch.cloud.google...` Google Cloud OAuth redirect. Requires Application permission `Sites.Read.All`.

> **ARCHITECTURE DUALITY:"""

text = text.replace("> **ARCHITECTURE DUALITY:", warning_block)

with open("generate_2076_readme.py", "w") as f:
    f.write(text)

