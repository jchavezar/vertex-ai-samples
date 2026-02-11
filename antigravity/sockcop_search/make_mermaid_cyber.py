import re

with open("generate_2076_readme.py", "r") as f:
    text = f.read()

old_mermaid = """```mermaid
sequenceDiagram
    participant User as End User
    participant Frontend as Sockcop Search (React)
    participant EntraID as Microsoft Entra ID (Azure AD)
    participant GoogleSTS as Google STS (Token Exchange)
    participant VertexAI as Vertex AI Search (Discovery Engine API)"""

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
    autonumber
    participant User as 👤 [USR]_Operator
    participant Frontend as 💻 [SYS]_Sockcop_Client
    participant EntraID as 🗝️ [AUTH]_Entra_ID
    participant GoogleSTS as 🛡️ [SEC]_Google_STS
    participant VertexAI as 🧠 [AI]_Vertex_Search"""

text = text.replace(old_mermaid, new_mermaid)

with open("generate_2076_readme.py", "w") as f:
    f.write(text)

