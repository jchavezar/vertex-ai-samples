import re

with open("generate_2076_readme.py", "r") as f:
    text = f.read()

# Using a robust regex to find and replace the entire mermaid block
pattern = re.compile(r"```mermaid.*?```", re.DOTALL)

new_mermaid = """```mermaid
%%{init: {
  "theme": "base",
  "themeVariables": {
    "background": "#020617",
    "primaryColor": "#0f172a",
    "primaryBorderColor": "#38bdf8",
    "primaryTextColor": "#e2e8f0",
    "secondaryColor": "#1e293b",
    "tertiaryColor": "#020617",
    "lineColor": "#22d3ee",
    "actorBkg": "#0f172a",
    "actorBorder": "#22d3ee",
    "actorTextColor": "#38bdf8",
    "actorLineColor": "#334155",
    "signalColor": "#4ade80",
    "signalTextColor": "#f8fafc",
    "noteBkg": "#064e3b",
    "noteBorder": "#10b981",
    "noteTextColor": "#a7f3d0",
    "labelBoxBkgColor": "#0f172a",
    "labelBoxBorderColor": "#f43f5e",
    "labelTextColor": "#fda4af",
    "edgeLabelBackground": "#020617",
    "fontFamily": "monospace"
  }
}}%%
sequenceDiagram
    participant User as 👤 [USR]_Operator
    participant Frontend as 💻 [SYS]_Sockcop_Client
    participant EntraID as 🗝️ [AUTH]_Entra_ID
    participant GoogleSTS as 🛡️ [SEC]_Google_STS
    participant VertexAI as 🧠 [AI]_Vertex_Search
    
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
```"""

text = pattern.sub(new_mermaid, text)

with open("generate_2076_readme.py", "w") as f:
    f.write(text)
